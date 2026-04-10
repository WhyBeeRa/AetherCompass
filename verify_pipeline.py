import asyncio
import sys
import os
from datetime import datetime

# Ensure backend can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.models import ScoutFindings, VisualProof
from backend.agents.classifier import ClassifierAgent

async def verify_pipeline():
    print("--- Starting Scout -> Lab Pipeline Verification ---")
    lab = ClassifierAgent()
    
    # 1. Create a "Midjourney" Mock Finding (as if coming from Scout)
    # Scenario: High Visuals, Low Ease of Use (Discord)
    mj_findings = ScoutFindings(
        tool_name="Midjourney v6",
        source="Discord",
        user_intent="Generating hyper-realistic images via Discord bot",
        raw_sentiment="Amazing quality but I hate using Discord slash commands.",
        tech_stack="Discord Interface",
        reliability_score=95.0, # High reliability
        hype_factor=False,
        visual_proofs=[
            VisualProof(url="https://mj.com/img.png", source_url="https://discord.com/channels/mj")
        ]
    )
    
    # 2. Run the Lab
    analysis = await lab.analyze(mj_findings)
    
    # 3. Validation Logic (The "Cross-Check")
    print("\n[Validation Report]")
    print(f"Tool: {analysis.tool_name}")
    print(f"Summary: {analysis.executive_summary}")
    print(f"Metrics: Accuracy={analysis.metrics.accuracy}, Ease={analysis.metrics.ease_of_use}")
    
    # Check 1: Ease of Use should be LOW (1 or 2)
    if analysis.metrics.ease_of_use <= 2:
        print("  [PASS] Ease of Use correctly identified as Low (Discord barrier).")
    else:
        print(f"  [FAIL] Ease of Use too high: {analysis.metrics.ease_of_use}")
        
    # Check 2: Accuracy/Quality should be HIGH (5)
    if analysis.metrics.accuracy >= 4 and analysis.visual_quality == "High":
        print("  [PASS] Quality/Accuracy correctly identified as High.")
    else:
        print(f"  [FAIL] Quality mismatch: Acc={analysis.metrics.accuracy}, Visual={analysis.visual_quality}")

    # Check 3: Summary Structure
    if "(Peak)" in analysis.executive_summary and "(Trade-off)" in analysis.executive_summary:
        print("  [PASS] Executive Summary follows 'Peak/Trade-off' structure.")
    else:
        print("  [FAIL] Executive Summary formatting incorrect.")

if __name__ == "__main__":
    asyncio.run(verify_pipeline())
