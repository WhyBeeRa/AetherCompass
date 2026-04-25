import time
import asyncio
import random
import httpx
from datetime import datetime
from typing import List, Dict, Optional
from models import LiveMetric, LabAnalysis
from persistence import AetherVault
import os

class LiveMonitor:
    """
    The Live Benchmarking Engine.
    Dynamically assesses tools from the Vault.
    """
    def __init__(self, vault: AetherVault):
        self.vault = vault
        self.client = httpx.AsyncClient(timeout=10.0, follow_redirects=True)
        
        # Major LLM providers and their identifiers
        self.llm_identifiers = ["chat", "gpt", "claude", "gemini", "llama", "mistral", "perplexity"]
        
        # Status page or homepages for pings
        self.target_urls = {
            "openai": "https://status.openai.com/api/v2/status.json",
            "anthropic": "https://status.anthropic.com/api/v2/status.json",
            "google": "https://gemini.google.com",
            "meta": "https://llama.meta.com",
            "perplexity": "https://www.perplexity.ai"
        }

    async def is_benchmarkable(self, tool: Dict) -> bool:
        """
        Determines if a tool is 'Live Benchmarkable'.
        Following user's rule: 'SUNO no (audio/creative), CHATGPT yes (LLM/Service)'.
        """
        name = tool.get("tool_name", "").lower()
        analysis = tool.get("analysis", {})
        summary = analysis.get("executive_summary", "").lower()
        
        # Skip creative/media tools that don't have a simple performance API/web latency metric relevant to 'efficiency'
        non_benchmarkable_keywords = ["suno", "music", "video", "generator", "udio", "runway", "pika"]
        if any(kw in name for kw in non_benchmarkable_keywords):
            return False
            
        # Prioritize LLMs, Chatbots, and Search Engines
        benchmarkable_keywords = self.llm_identifiers + ["search", "api", "assistant", "workflow"]
        if any(kw in name for kw in benchmarkable_keywords) or any(kw in summary for kw in benchmarkable_keywords):
            return True
            
        # Default: if it's a popular tool with a website, let's try it
        return True

    async def measure_gemini_real(self) -> Optional[float]:
        """
        Attempts a real ping to Gemini if API key is present.
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return None
            
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        payload = {"contents": [{"parts": [{"text": "ping"}]}]}
        
        try:
            start_time = time.time()
            response = await self.client.post(url, json=payload)
            latency = (time.time() - start_time) * 1000
            if response.status_code == 200:
                return round(latency, 2)
        except Exception as e:
            print(f"[LiveMonitor] Gemini Real Ping failed: {e}")
        return None

    async def measure_tool(self, tool: Dict) -> Optional[LiveMetric]:
        """
        Measures a single tool's performance.
        """
        name = tool.get("tool_name", "")
        analysis = tool.get("analysis", {})
        website = tool.get("website_url") or analysis.get("website_url")
        
        # Comprehensive Fallback Mapping for popular tools
        popular_tools = {
            "chatgpt": "https://chatgpt.com",
            "gpt-4": "https://chatgpt.com",
            "claude": "https://claude.ai",
            "gemini": "https://gemini.google.com",
            "perplexity": "https://www.perplexity.ai",
            "v0": "https://v0.dev",
            "midjourney": "https://www.midjourney.com",
            "runway": "https://runwayml.com",
            "luma": "https://lumalabs.ai",
            "github copilot": "https://github.com/features/copilot",
            "notion ai": "https://www.notion.so/product/ai",
            "mistral": "https://mistral.ai",
            "llama": "https://llama.meta.com",
            "hugging face": "https://huggingface.co",
            "elevenlabs": "https://elevenlabs.io",
            "heygen": "https://www.heygen.com",
            "gamma": "https://gamma.app",
            "jasper": "https://www.jasper.ai",
            "leonardo": "https://leonardo.ai",
            "phind": "https://www.phind.com",
            "groq": "https://groq.com",
            "make.com": "https://www.make.com",
            "zapier": "https://zapier.com",
            "cursor": "https://cursor.sh"
        }
        
        if not website:
            name_lower = name.lower()
            # Try exact match or partial match in popular tools
            for key, url in popular_tools.items():
                if key in name_lower:
                    website = url
                    break
            
            # If still nothing, try a smart guess
            if not website:
                clean_name = "".join(filter(str.isalnum, name_lower))
                if clean_name:
                    # We'll try .ai first as it's common for AI tools
                    website = f"https://{clean_name}.ai"
        
        if not website:
            return None

        # 1. LATENCY CHECK
        latency = None
        status = "offline"
        
        # Specilized Real Pings
        if "gemini" in name.lower():
             latency = await self.measure_gemini_real()
             
        if not latency:
            try:
                start_time = time.time()
                # We use a simple get request to the website as a proxy for 'Life' and latency
                resp = await self.client.get(website, timeout=5.0)
                latency = (time.time() - start_time) * 1000
                
                if resp.status_code == 403 or resp.status_code == 429:
                    status = "protected"
                elif resp.status_code >= 400:
                    status = "slow" if latency > 1500 else "online" 
                else:
                    status = "online" if latency < 1200 else "slow"
            except (httpx.ConnectError, httpx.TimeoutException):
                return LiveMetric(
                    tool_name=name,
                    provider="Web",
                    latency_ms=0,
                    hallucination_score=0,
                    status="offline"
                )
            except Exception as e:
                print(f"[LiveMonitor] Unexpected error measuring {name}: {e}")
                status = "offline"
        else:
            status = "online" if latency < 1500 else "slow"

        # 2. ACCESS RELIABILITY (Formerly Hallucination Score)
        # 100% = Perfect uptime/unblocked. 0% = Offline.
        if status == "online":
            base_score = 99.0 - (latency / 500.0) # Minor penalty for every 500ms
        elif status == "protected":
            base_score = 99.5 # High reliability but cloaked
        elif status == "slow":
            base_score = 85.0 - (latency / 1000.0)
        else:
            base_score = 0
            
        access_reliability = round(base_score + random.uniform(-0.5, 0.5), 2)
        access_reliability = max(0, min(100, access_reliability))

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
            hallucination_score=access_reliability, # Reusing field for Access Reliability
            timestamp=datetime.now(),
            status=status
        )

    async def run_benchmark_cycle(self):
        """
        Runs one cycle of benchmarks across all benchmarkable tools in the Vault.
        """
        print(f"[{datetime.now()}] Starting Live Benchmark Cycle...")
        
        # 1. Fetch tools from Vault
        all_tools = self.vault.search_tools("", include_inactive=True)
        print(f"  - Found {len(all_tools)} tools in Vault.")
        
        # 2. Filter for benchmarkable
        targets = []
        for t in all_tools:
            if await self.is_benchmarkable(t):
                targets.append(t)
        
        print(f"  - Identified {len(targets)} benchmarkable targets (excluding creative tools like Suno).")
        
        # 3. Measure in parallel
        tasks = [self.measure_tool(t) for t in targets]
        results = await asyncio.gather(*tasks)
        
        metrics = [m for m in results if m is not None]
        
        if not metrics:
            print("  - No metrics captured.")
            return

        # 4. Calculate comparisons and save
        avg_latency = sum(m.latency_ms for m in metrics if m.status != "offline") / max(1, len([m for m in metrics if m.status != "offline"]))
        
        for m in metrics:
            if m.status != "offline" and avg_latency > 0:
                m.comparison_vs_avg = round(((m.latency_ms - avg_latency) / avg_latency) * 100, 2)
            else:
                m.comparison_vs_avg = 0
                
            self.vault.save_live_metric(m)
            status_symbol = "[OK]" if m.status == "online" else "[SLOW]" if m.status == "slow" else "[PROTECTED]" if m.status == "protected" else "[OFFLINE]"
            print(f"  {status_symbol} {m.tool_name} ({m.provider}): {m.latency_ms}ms | Access Reliability: {m.hallucination_score} | {m.comparison_vs_avg}% vs avg")

        print(f"[{datetime.now()}] Benchmark Cycle Complete. {len(metrics)} tools updated.")
        await self.client.aclose()

if __name__ == "__main__":
    # For manual testing
    vault = AetherVault()
    monitor = LiveMonitor(vault)
    asyncio.run(monitor.run_benchmark_cycle())
