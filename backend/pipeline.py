import asyncio
from typing import Dict, List, Optional
from models import ScoutFindings, LabAnalysis, AuditLog, GalleryItem, TrustScore, ToolMetrics, VisualProof
from agents.scout import ScoutAgent
from agents.classifier import ClassifierAgent
from agents.auditor import AuditorAgent
from agents.curator import CuratorAgent

class AetherPipeline:
    """
    The Orchestrator.
    Manages the flow of data from Discovery to Gallery.
    Enforces the Integrity Gate.
    """
    def __init__(self):
        self.scout = ScoutAgent()
        self.lab = ClassifierAgent()
        self.auditor = AuditorAgent()
        self.curator = CuratorAgent()

    async def run_pipeline(self, intent: str) -> Dict:
        """
        Executes the full chain: Scout -> Lab -> Auditor -> Curator.
        Includes Logic Gate (Vault Check).
        """
        print(f"\n[Pipeline] [START] Initiating Sequence for intent: {intent}")
        
        # ---------------------------------------------------------
        # PHASE 0: LOGIC GATE (The Vault)
        # ---------------------------------------------------------
        from persistence import AetherVault
        vault = AetherVault()
        
        # Check if the vault already has tools answering this exact intent
        cached_results = vault.search_tools(intent)
        if cached_results:
             print(f"[Pipeline] [VAULT] Identity Found for intent '{intent}'. Retrieving from secured memory (Zero Latency).")
             # Return the first match for the pipeline result formatting
             # Frontend already hits /vault/search so this is mostly for completeness if polled
             return {
                 "status": "success", 
                 "tool_name": cached_results[0]["tool_name"],
                 "analysis": cached_results[0]["analysis"],
                 "trust_score": cached_results[0]["trust_score"],
                 "gallery": cached_results[0]["gallery"],
                 "cached": True
             }

        # ---------------------------------------------------------
        # PHASE 1: DISCOVERY (The Scout)
        # ---------------------------------------------------------
        # Ask the scout to find tools for this specific intent
        all_findings = await self.scout.run_discovery_cycle(intent)
        
        # Pick the top recommended finding by Scout
        if not all_findings:
             return {"status": "rejected", "reason": "Scout found zero evidence for this intent"}
             
        target_finding = all_findings[0] # The Scout ranks them
        
        print(f"[Pipeline] [SCOUT] Evidence Secured: {len(target_finding.visual_proofs)} proofs found.")

        # ---------------------------------------------------------
        # PHASE 2: ANALYSIS (The Lab)
        # ---------------------------------------------------------
        analysis = await self.lab.analyze(target_finding)
        print(f"[Pipeline] [LAB] Analysis Complete: {analysis.executive_summary}")

        # ---------------------------------------------------------
        # PHASE 3: VERIFICATION (The Auditor)
        # ---------------------------------------------------------
        # We simulate extraction of reviews from the 'raw_sentiment'
        reviews = [target_finding.raw_sentiment] 
        audit_log = await self.auditor.audit_tool(
            target_finding.tool_name, 
            analysis.metrics, 
            reviews,
            hype_factor=target_finding.hype_factor
        )
        
        # INTEGRITY GATE
        if audit_log.new_trust_score < 50 or "Revoked" in audit_log.action:
            print(f"[Pipeline] [STOP] INTEGRITY LOCKDOWN. Trust Score {audit_log.new_trust_score} is too low.")
            # Even rejected tools might be worth logging in Audit History (not verified_tools)
            # For now, we return rejection.
            return {
                "status": "rejected",
                "reason": f"Integrity Check Failed: {audit_log.reason}",
                "audit_log": audit_log
            }
            
        print(f"[Pipeline] [AUDITOR] Integrity Verified. Trust Score: {audit_log.new_trust_score}")

        # ---------------------------------------------------------
        # PHASE 4: CURATION (The Curator)
        # ---------------------------------------------------------
        gallery_items = self.curator.curate_gallery(target_finding, audit_log)
        
        if not gallery_items:
             print("[Pipeline] [WARN] Curator found no high-quality visuals to showcase.")
             return {"status": "empty_gallery", "reason": "Low Visual Quality"}
             
        print(f"[Pipeline] [CURATOR] Gallery Curation Complete. {len(gallery_items)} items ready.")
        
        # ---------------------------------------------------------
        # PHASE 5: PERSISTENCE (The Vault)
        # ---------------------------------------------------------
        vault.save_tool(
            tool_name=target_finding.tool_name,
            analysis=analysis,
            trust_score=audit_log.new_trust_score,
            gallery=gallery_items,
            audit_log=audit_log
        )

        # ---------------------------------------------------------
        # FINAL PAYLOAD
        # ---------------------------------------------------------
        return {
            "status": "success",
            "tool_name": target_finding.tool_name,
            "analysis": analysis,
            "trust_score": audit_log.new_trust_score,
            "gallery": gallery_items
        }
