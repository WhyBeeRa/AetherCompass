import asyncio
from datetime import datetime
from typing import List, Dict
from ..models import TrustScore, AuditLog, ToolMetrics

AUDITOR_SYSTEM_PROMPT = """
Role: You are the Chief Auditor of Aether. Your sole purpose is to doubt, verify, and validate every piece of data entering the "Single Source of Truth."

Objective: Protect the platform from marketing manipulation, fake reviews, and outdated performance data. Give precise, objective numerical ratings based on fixed parameters.

1. Fraud & Bias Detection:
Analyze text and metadata for "Artificial Positivity." If a tool's description uses excessive superlatives (e.g. "revolutionary", "game-changing") without concrete technical specifics, penalize its score immediately.
Check for "Review Bombing" or inorganic sentiment patterns.

2. Objective Scoring (The Rating):
You must evaluate the tool across fixed parameters: True Capability, Speed/Performance, Price-to-Value, and Output Quality.
Do not accept generalized statements. If a tool claims to be "fast", demand context. If it is slow, deduct points harshly. Your final verdict drives an objective 0-100 trust score.

3. The "Cons" Mandate:
You MUST find real, technical, or practical limitations for EVERY tool. Even the best tools have architectural trade-offs, pricing issues, or steep learning curves. If you cannot find a flaw, you are not looking hard enough. Describe these flaws brutally but professionally.

Constraints:
You are skeptical by nature. Zero marketing fluff allowed.
Do not allow personal bias to influence the score, only data-driven evidence.
"""

class AuditorAgent:
    """
    The Auditor: Officer of Integrity.
    Verifies authenticity, stability, and quality.
    """
    def __init__(self):
        pass

    def _detect_textual_twins(self, reviews: List[str]) -> bool:
        """
        Detects if multiple reviews share identical structures (sign of bots).
        """
        # MVP Logic: Check for duplicate substrings of significant length or exact matches
        # In production, use cosine similarity
        if not reviews:
            return False
            
        seen_structures = set()
        duplicates = 0
        for r in reviews:
            # Simplified structure check: First 15 chars
            struct = r[:15].lower()
            if struct in seen_structures:
                duplicates += 1
            seen_structures.add(struct)
        
        # If more than 30% are twins, flag it
        return (duplicates / len(reviews)) > 0.3 if len(reviews) > 2 else False

    def _calculate_score(self, authenticity: float, stability: float, quality: float, penalty: float) -> float:
        """
        Weighted Formula: (Auth * 0.4) + (Stab * 0.3) + (Qual * 0.3) - Penalty
        """
        if authenticity <= 0:
            return 0.0
            
        base_score = (authenticity * 0.4) + (stability * 0.3) + (quality * 0.3)
        final_score = base_score - penalty
        return max(0.0, min(100.0, final_score))

    async def audit_tool(self, tool_name: str, current_metrics: ToolMetrics, reviews: List[str] = [], hype_factor: bool = False, raw_limitations: List[str] = []) -> AuditLog:
        """
        Main audit entry point.
        """
        print(f"Auditor: Initiating investigation on {tool_name}...")
        
        # 1. Identity & Fraud Check
        is_bot_attack = self._detect_textual_twins(reviews)
        authenticity_score = 0.0 if is_bot_attack else 90.0
        
        penalty = 0.0
        audit_reason = "Routine Check Passed."
        action = "Verified"
        
        if is_bot_attack:
            penalty += 40.0
            audit_reason = "Flagged: Detected pattern of inorganic sentiment."
            action = "Flagged"
            authenticity_score = 0.0
            
        # 1.5 Hype Penalty
        if hype_factor:
            penalty += 20.0
            audit_reason += " [Warning: High Marketing Hype]"
            
        # 2. Objective Metric Evaluation (Speed, Value, Accuracy)
        # Using 1-5 scale metrics to derive a baseline score. 5 = 100%, 1 = 20%
        # Weighting: Accuracy (40%), Value (30%), Speed (30%)
        # Note: ease_of_use doesn't penalize capability directly, usually.
        accuracy_norm = (current_metrics.accuracy / 5.0) * 100.0
        value_norm = (current_metrics.value / 5.0) * 100.0
        speed_norm = (current_metrics.speed / 5.0) * 100.0
        
        base_objective_score = (accuracy_norm * 0.4) + (value_norm * 0.3) + (speed_norm * 0.3)
        
        # Penalize if metrics are critically low
        if current_metrics.speed <= 2:
             audit_reason += " [Critique: Extremely slow processing speed observed.]"
             penalty += 15.0
        if current_metrics.value <= 2:
             audit_reason += " [Critique: Price-to-Value ratio implies it is overpriced.]"
             penalty += 15.0

        # Penalize based on severe limitations from crawler
        for limit in raw_limitations:
            if "not allow" in limit.lower() or "enterprise only" in limit.lower() or "struggles" in limit.lower():
                penalty += 5.0 

        # 3. Evidence Quality (Derived from Scout/Lab findings generally)
        evidence_quality = base_objective_score

        # Calculate Final Trust Score
        total_trust = self._calculate_score(authenticity_score, base_objective_score, evidence_quality, penalty)
        
        # Enforce Real Limitations output logic
        if len(raw_limitations) == 0:
             penalty += 10.0 # Silent penalty for finding absolutely zero flaws, very suspicious.
             total_trust = max(0.0, total_trust - 10.0)
             audit_reason += " [Warning: Suspiciously flawless, applying skeptical deduction.]"

        # Logic for Revocation
        if total_trust < 55:
             action = "Badge Revoked" if action != "Flagged" else action
        
        trust_model = TrustScore(
            authenticity_score=authenticity_score,
            evidence_quality_score=evidence_quality,
            performance_stability=base_objective_score,
            marketing_noise_penalty=penalty,
            total_trust_score=total_trust
        )
        
        print(f"Auditor: Verdict for {tool_name} -> {total_trust:.1f}/100. Action: {action}")
        
        return AuditLog(
            tool_name=tool_name,
            action=action,
            reason=audit_reason,
            new_trust_score=total_trust
        )
