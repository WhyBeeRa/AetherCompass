import asyncio
import traceback
from search_engine import AetherSearchEngine

async def run_test():
    try:
        engine = AetherSearchEngine()
        await engine.semantic_search('test')
    except Exception as e:
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_test())
