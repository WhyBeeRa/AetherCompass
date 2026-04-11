import asyncio
from admin_auditor import run_vault_audit

async def test():
    print("Testing Midjourney lookup...")
    res = await run_vault_audit("https://midjourney.com")
    print(res)

if __name__ == "__main__":
    asyncio.run(test())
