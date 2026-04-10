import asyncio
import sys
import os
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.models import ToolMetrics
from backend.agents.auditor import AuditorAgent

async def verify_auditor():
    print("--- Starting Auditor Verification ---")
    auditor = AuditorAgent()
    
    # Mock Metrics
    standard_metrics = ToolMetrics(accuracy=5, speed=5, value=5, ease_of_use=5)
    
    # SCENARIO A: Fraud / Textual Twins
    print("\n[Test A] Fraud Detection (Textual Twins)")
    fake_reviews = [
        "This tool changed my life! It is the best.",
        "This tool changed my life! It is the best.", # Twin
        "This tool changed my life! It is the best.", # Twin
        "Good tool."
    ]
    
    log_a = await auditor.audit_tool("FakeAI", standard_metrics, fake_reviews)
    
    if log_a.new_trust_score == 0.0 and "Flagged" in log_a.action:
        print(f"  [PASS] Fraud detected. Score dropped to 0.")
        print(f"  Reason: {log_a.reason}")
    else:
        print(f"  [FAIL] Fraud NOT detected. Score: {log_a.new_trust_score}")

    # SCENARIO B: Performance Drift (Simulated by low speed)
    print("\n[Test B] Performance Drift")
    drift_metrics = ToolMetrics(accuracy=5, speed=1, value=5, ease_of_use=5) # Speed 1 triggers drift logic in mock
    
    log_b = await auditor.audit_tool("SlowAI", drift_metrics, ["Great tool but slow."])
    
    if "Instability" in log_b.reason:
        print(f"  [PASS] Drift warning triggered.")
        print(f"  Reason: {log_b.reason}")
    else:
        print(f"  [FAIL] Drift warning missed.")

if __name__ == "__main__":
    asyncio.run(verify_auditor())
