import asyncio
import os
from admin_auditor import run_lean_audit
from dotenv import load_dotenv

load_dotenv()

async def test():
    url = "https://www.perplexity.ai"
    print(f"Testing auditor for: {url}")
    res = await run_lean_audit(url)
    print("Result:")
    print(res)

if __name__ == "__main__":
    asyncio.run(test())
