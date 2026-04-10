import asyncio
import sys
import os
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.models import ScoutFindings, VisualProof, AuditLog
from backend.agents.curator import CuratorAgent

def verify_curator():
    print("--- Starting Curator Verification ---")
    curator = CuratorAgent()
    
    # Input Data
    proof = VisualProof(url="https://mj.com/art.png", source_url="https://discord.com", media_type="image")
    findings = ScoutFindings(
        tool_name="Midjourney",
        source="Discord",
        user_intent="Art",
        raw_sentiment="Good",
        tech_stack="Bot",
        reliability_score=90,
        visual_proofs=[proof]
    )
    
    # Scenario A: High Trust (Badge Visible)
    audit_log_high = AuditLog(tool_name="Midjourney", action="Verified", reason="OK", new_trust_score=95.0)
    
    gallery_high = curator.curate_gallery(findings, audit_log_high)
    
    if gallery_high and gallery_high[0].trust_badge_visible:
        print("  [PASS] High Trust: Badge is visible.")
        print(f"  Tags: {gallery_high[0].style_tags}")
    else:
        print("  [FAIL] High Trust: Badge missing or empty gallery.")

    # Scenario B: Low Trust (Badge Hidden)
    audit_log_low = AuditLog(tool_name="Midjourney", action="Flagged", reason="Drift", new_trust_score=40.0)
    
    gallery_low = curator.curate_gallery(findings, audit_log_low)
    
    if gallery_low and not gallery_low[0].trust_badge_visible:
         print("  [PASS] Low Trust: Badge is hidden.")
    else:
         print(f"  [FAIL] Low Trust logic failed. Badge Visible: {gallery_low[0].trust_badge_visible}")

if __name__ == "__main__":
    verify_curator()
