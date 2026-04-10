import asyncio
import sys
import os

# Ensure backend can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.agents.scout import ScoutAgent
from backend.models import ScoutFindings

async def verify_scout():
    print("--- Starting Scout Verification ---")
    scout = ScoutAgent()
    
    # Test 1: Hype Filtering Logic
    print("\n[Test 1] Hype Logic Check:")
    hype_text = "This is a revolutionary game changer best AI ever!"
    clean_text = "Python library for data analysis with benchmarks."
    
    score_hype = scout.calculate_reliability(hype_text, False)
    score_clean = scout.calculate_reliability(clean_text, True)
    
    print(f"  Hype Text Score: {score_hype} (Expected Low)")
    print(f"  Clean Text Score: {score_clean} (Expected High)")
    
    if score_hype < score_clean:
        print("  [PASS] Hype penalty functional.")
    else:
        print("  [FAIL] Hype penalty failed.")

    # Test 2: Full Discovery Cycle
    print("\n[Test 2] Full Discovery Cycle:")
    findings = await scout.run_discovery_cycle()
    
    if len(findings) > 0:
        print(f"  [PASS] Cycle returned {len(findings)} findings.")
        for f in findings:
            if isinstance(f, ScoutFindings):
                print(f"  [PASS] Verified finding type for {f.tool_name}")
                if f.hype_factor and f.reliability_score < 40:
                     print(f"  [PASS] Successfully identified hype in {f.tool_name}")
            else:
                print(f"  [FAIL] Invalid finding type: {type(f)}")
    else:
        print("  [FAIL] No findings returned.")

if __name__ == "__main__":
    asyncio.run(verify_scout())
