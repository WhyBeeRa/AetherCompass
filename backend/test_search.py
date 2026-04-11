import asyncio
import time
import os
from dotenv import load_dotenv

# Load environment variables before importing the engine
load_dotenv()

from search_engine import AetherSearchEngine

async def run_test():
    print("Initializing Aether Search Engine...")
    engine = AetherSearchEngine()
    
    # Force query to be treated as UTF-8
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
        name = r.get('tool_name', 'Unknown')
        score = r.get('relevance_score', 0)
        reason = r.get('match_reason', 'No reason provided')
        print(f"{idx+1}. {name} - Score: {score}")
        print(f"   Reason: {reason}")

if __name__ == "__main__":
    asyncio.run(run_test())
