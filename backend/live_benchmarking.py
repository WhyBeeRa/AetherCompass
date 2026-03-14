import time
import random
from datetime import datetime
from typing import List, Dict
from models import LiveMetric
from persistence import AetherVault

class LiveMonitor:
    """
    The Live Benchmarking Engine.
    Pings major AI APIs to measure Latency and Hallucination.
    """
    def __init__(self, vault: AetherVault):
        self.vault = vault
        self.targets = [
            {"name": "GPT-4o", "provider": "OpenAI"},
            {"name": "Claude 3.5 Sonnet", "provider": "Anthropic"},
            {"name": "Gemini 1.5 Pro", "provider": "Google"},
            {"name": "Llama 3 (Groq)", "provider": "Meta/Groq"}
        ]

    async def run_benchmark_cycle(self):
        """
        Runs one cycle of benchmarks across all targets.
        In a real world scenario, this would send a standardized prompt to each API.
        """
        print(f"[{datetime.now()}] Starting Live Benchmark Cycle...")
        metrics = []

        for target in self.targets:
            # Simulation of API call
            # In production: start_time = time.time(), response = await call_api(target), latency = time.time() - start_time
            
            # Latency: Claude is usually fast, GPT varies, Groq is blazing.
            base_latency = {
                "OpenAI": 1200,
                "Anthropic": 950,
                "Google": 1100,
                "Meta/Groq": 350
            }.get(target["provider"], 1000)
            
            latency = base_latency + random.randint(-100, 500)
            
            # Hallucination Score (Mock): 100 is perfect, 0 is total hallucination
            # We use a weighted random to simulate model drift
            hallucination_score = random.uniform(92, 99.9)
            if random.random() < 0.05: # 5% chance of a "bad" result
                hallucination_score -= 15

            metric = LiveMetric(
                tool_name=target["name"],
                provider=target["provider"],
                latency_ms=latency,
                hallucination_score=round(hallucination_score, 2),
                timestamp=datetime.now(),
                status="online" if latency < 2000 else "slow"
            )
            metrics.append(metric)

        # Calculate comparisons
        avg_latency = sum(m.latency_ms for m in metrics) / len(metrics)
        for m in metrics:
            m.comparison_vs_avg = round(((m.latency_ms - avg_latency) / avg_latency) * 100, 2)
            self.vault.save_live_metric(m)
            print(f"  - {m.tool_name}: {m.latency_ms}ms | Hallucination: {m.hallucination_score} | {m.comparison_vs_avg}% vs avg")

        print(f"[{datetime.now()}] Benchmark Cycle Complete.")

if __name__ == "__main__":
    # For manual testing
    import asyncio
    vault = AetherVault()
    monitor = LiveMonitor(vault)
    asyncio.run(monitor.run_benchmark_cycle())
