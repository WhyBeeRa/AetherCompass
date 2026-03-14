import asyncio
import time
from search_engine import AetherSearchEngine

async def run_test():
    print("Initializing Aether Search Engine...")
    engine = AetherSearchEngine()
    
    query = "כלי ליצירת מצגות"
    print(f"\n[Test] Running Query: '{query}'")
    
    start = time.time()
    results = await engine.semantic_search(query)
    end = time.time()
    
    print(f"Results found in {((end-start)*1000):.2f} ms:")
    if not results:
        print("No results returned.")
        return
        
    for idx, r in enumerate(results):
        print(f"{idx+1}. {r.get('tool_name')} - Score: {r.get('relevance_score')}")
        print(f"   Reason: {r.get('match_reason')}")

if __name__ == "__main__":
    asyncio.run(run_test())
