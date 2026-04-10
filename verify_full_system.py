import asyncio
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.pipeline import AetherPipeline

async def verify_full_system():
    print("=== AETHER SYSTEM INITIALIZATION ===")
    pipeline = AetherPipeline()
    
    # CASE 1: The Happy Path (OpenDevin)
    # Expected: Scout finds it -> Lab analyzes -> Auditor passes -> Curator builds gallery.
    result_1 = await pipeline.run_pipeline("OpenDevin")
    
    if result_1["status"] == "success":
        print("\n[PASS] Case 1 (OpenDevin): Pipeline execution successful.")
        print(f"  Summary: {result_1['analysis'].executive_summary}")
        print(f"  Gallery Items: {len(result_1['gallery'])}")
    else:
        print(f"\n[FAIL] Case 1 (OpenDevin): Failed. Status: {result_1['status']}")

    # CASE 2: The Rejection Path (MagicBookWriter)
    # Expected: Scout finds it (with Hype) -> Lab analyzes -> Auditor flags Hype/Low Speed -> Trust Score drops -> REJECTED.
    result_2 = await pipeline.run_pipeline("MagicBookWriter")
    
    if result_2["status"] == "rejected":
        print("\n[PASS] Case 2 (MagicBookWriter): Pipeline correctly rejected the tool.")
        print(f"  Reason: {result_2['reason']}")
    else:
        print(f"\n[FAIL] Case 2 (MagicBookWriter): Should have been rejected. Got: {result_2['status']}")

if __name__ == "__main__":
    asyncio.run(verify_full_system())
