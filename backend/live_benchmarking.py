import time
import asyncio
import httpx
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from models import LiveMetric
from persistence import AetherVault
try:
    from logger_utils import log_terminal
except ImportError:
    async def log_terminal(m): print(m)

class LiveMonitor:
    """
    The Live Benchmarking Engine.
    Dynamically assesses tools from the Vault with strict architecture rules.
    """
    def __init__(self, vault: AetherVault):
        self.vault = vault
        # Rule: Limit concurrency to 5 to prevent IP blocking
        self.semaphore = asyncio.Semaphore(5)
        
        # Major LLM providers and their identifiers
        self.llm_identifiers = ["chat", "gpt", "claude", "gemini", "llama", "mistral", "perplexity"]

    async def is_benchmarkable(self, tool: Dict) -> bool:
        """
        Determines if a tool is 'Live Benchmarkable'.
        Only tools with a predefined website_url are processed.
        """
        name = tool.get("tool_name", "").lower()
        analysis = tool.get("analysis", {})
        website = tool.get("website_url") or analysis.get("website_url")
        
        # Rule: No URL guessing (.ai logic removed). If no URL, skip.
        if not website:
            return False
            
        # Rule: Skip creative/media tools that don't have relevant latency metrics
        non_benchmarkable_keywords = ["suno", "music", "video", "generator", "udio", "runway", "pika"]
        if any(kw in name for kw in non_benchmarkable_keywords):
            return False
            
        return True

    async def measure_gemini_real(self, client: httpx.AsyncClient) -> Optional[float]:
        """
        Attempts a real ping to Gemini using a dynamic model from environment variables.
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return None
            
        # Rule: Dynamic Gemini Model (e.g. gemini-2.5-flash)
        gemini_model = os.getenv("BENCHMARK_GEMINI_MODEL", "gemini-2.5-flash")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{gemini_model}:generateContent?key={api_key}"
        payload = {"contents": [{"parts": [{"text": "ping"}]}]}
        
        try:
            start_time = time.time()
            response = await client.post(url, json=payload, timeout=10.0)
            latency = (time.time() - start_time) * 1000
            if response.status_code == 200:
                return round(latency, 2)
        except Exception as e:
            print(f"[LiveMonitor] Gemini Real Ping failed: {e}")
        return None

    async def measure_tool(self, tool: Dict, client: httpx.AsyncClient) -> Optional[LiveMetric]:
        """
        Measures a single tool's performance. 
        Uses a semaphore to strictly limit parallel requests.
        """
        async with self.semaphore:
            name = tool.get("tool_name", "")
            analysis = tool.get("analysis", {})
            website = tool.get("website_url") or analysis.get("website_url")
            
            # 1. LATENCY & RELIABILITY CHECK
            latency = None
            status = "offline"
            reliability_score = 0.0 # Standardized to 0-100
            
            # specialized Real Pings for Gemini
            if "gemini" in name.lower():
                 latency = await self.measure_gemini_real(client)
                 
            if not latency:
                try:
                    start_time = time.time()
                    # Rule: Deterministic request without random noise
                    resp = await client.get(website, timeout=10.0, follow_redirects=True)
                    latency = (time.time() - start_time) * 1000
                    
                    # Rule: Handle 403 and 429 as protected (Cloudflare/WAF)
                    if resp.status_code in [403, 429]:
                        status = "protected"
                        latency = 0
                        reliability_score = 100.0
                    elif resp.status_code >= 400:
                        status = "slow" if latency > 1500 else "online"
                        reliability_score = 0.0 # Error codes count as 0 reliability
                    else:
                        status = "online" if latency < 1200 else "slow"
                        # Deterministic Reliability: Based on success and latency penalty
                        reliability_score = max(0.0, 100.0 - (latency / 100.0))
                except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPError):
                    status = "offline"
                    latency = 0
                    reliability_score = 0.0
                except Exception as e:
                    print(f"[LiveMonitor] Unexpected error measuring {name}: {e}")
                    status = "offline"
                    reliability_score = 0.0
            else:
                # Gemini Real Ping success
                status = "online" if latency < 1500 else "slow"
                reliability_score = max(0.0, 100.0 - (latency / 100.0))

            provider = "AI Provider"
            name_lower = name.lower()
            if any(kw in name_lower for kw in ["gpt", "openai"]): provider = "OpenAI"
            elif "claude" in name_lower: provider = "Anthropic"
            elif "gemini" in name_lower: provider = "Google"
            elif "perplexity" in name_lower: provider = "Perplexity"
            elif "llama" in name_lower: provider = "Meta"
            elif "mistral" in name_lower: provider = "Mistral"

            return LiveMetric(
                tool_name=name,
                provider=provider,
                latency_ms=round(latency or 0, 2),
                hallucination_score=round(reliability_score, 2), # Standardized to float 0-100
                timestamp=datetime.now(),
                status=status
            )

    async def run_benchmark_cycle(self):
        """
        Runs one cycle of benchmarks with local client management and IP block prevention.
        """
        await log_terminal(f"Starting Live Benchmark Cycle (Strict Architecture Mode)...")
        
        # 1. Fetch tools from Vault
        all_tools = self.vault.search_tools("", include_inactive=True)
        
        # 2. Filter for benchmarkable (Strict: No URL guessing)
        targets = [t for t in all_tools if await self.is_benchmarkable(t)]
        print(f"  - Identified {len(targets)} valid benchmarkable targets.")
        
        if not targets:
            await log_terminal("  - No valid targets found. Skipping cycle.")
            return

        # 3. Lifecycle Management: Local AsyncClient
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            tasks = [self.measure_tool(t, client) for t in targets]
            results = await asyncio.gather(*tasks)
            
            metrics = [m for m in results if m is not None]
            
            if not metrics:
                await log_terminal("  - No metrics captured.")
                return

            # 4. Calculate comparisons and save
            active_metrics = [m for m in metrics if m.status not in ["offline", "Connection_Error", "protected"]]
            if active_metrics:
                avg_latency = sum(m.latency_ms for m in active_metrics) / len(active_metrics)
            else:
                avg_latency = 0
            
            for m in metrics:
                if m.status not in ["offline", "Connection_Error", "protected"] and avg_latency > 0:
                    m.comparison_vs_avg = round(((m.latency_ms - avg_latency) / avg_latency) * 100, 2)
                else:
                    m.comparison_vs_avg = 0
                    
                self.vault.save_live_metric(m)
                await log_terminal(f"  [{m.status}] {m.tool_name}: {m.latency_ms}ms | Reliability: {m.hallucination_score}%")

        # 5. Database Pruning: Remove records older than 24h to prevent bloat
        self.vault.prune_live_metrics(hours=24)

        await log_terminal(f"Benchmark Cycle Complete. {len(metrics)} metrics updated.")

if __name__ == "__main__":
    vault = AetherVault()
    monitor = LiveMonitor(vault)
    asyncio.run(monitor.run_benchmark_cycle())
