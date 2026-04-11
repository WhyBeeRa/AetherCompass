import asyncio
import os
import json
from typing import List, Dict
from datetime import datetime
from models import ScoutFindings, VisualProof
import google.genai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

SCOUT_SYSTEM_PROMPT = """
Role: You are the Commander of the "Scout" Agent for Aether - the Single Source of Truth for the AI world. 
Your mission is to bypass marketing hype and retrieve raw, verified evidence of AI tool capabilities.

Objective: Scan the digital landscape to identify new AI tools from HIGH-QUALITY sources (e.g., GitHub, HackerNews, specialized subreddits like r/LocalLLaMA, top technical blogs, and trusted directories like 'There is an AI for that').
The user wants to scan for an AI tool matching a specific intent or query. Focus on delivering factual, evidence-based results.

You must output ONLY valid JSON matching this exact schema. You MUST provide real source URLs instead of simulated ones.
{
  "tool_name": "Name of the tool",
  "source": "Name of the concrete high-quality source (e.g., HackerNews, Reddit, Official Docs)",
  "user_intent": "The user's intent",
  "raw_sentiment": "A summary of general sentiment found in reviews",
  "tech_stack": "e.g., LLM, Generative AI, or API only",
  "reliability_score": 90.0,
  "hype_factor": false,
  "visual_proofs": [
    {
      "url": "A realistic image URL representing the tool interface or output",
      "source_url": "The EXACT real URL where this evidence or tool was found (e.g. project URL or official site)"
    }
  ]
}
Ensure the image URL is a real unsplash URL or highly plausible placeholder if real isn't known. The `source_url` MUST be a real, verifiable web link to the tool or its community discussion.
"""

class ScoutAgent:
    """
    The Scout: Officer of Discovery.
    Scans sources to find new AI tools, filtering out hype and focusing on evidence.
    """
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})

    def calculate_reliability(self, content: str, has_visuals: bool) -> float:
        return 90.0 # Handled by LLM now

    def _is_hype(self, content: str) -> bool:
        return False

    async def run_discovery_cycle(self, intent: str) -> List[ScoutFindings]:
        print(f"Scout: Initiating Operation for intent '{intent}' using Gemini API...")
        
        prompt = f"{SCOUT_SYSTEM_PROMPT}\n\nUser Intent to scan for: {intent}"
        
        try:
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            data = json.loads(response.text)
            
            proofs = []
            for vp in data.get("visual_proofs", []):
                proofs.append(VisualProof(
                    url=vp.get("url"),
                    source_url=vp.get("source_url")
                ))
                
            finding = ScoutFindings(
                tool_name=data.get("tool_name", "Unknown Tool"),
                source=data.get("source", "Simulated Web Scan"),
                user_intent=data.get("user_intent", intent),
                raw_sentiment=data.get("raw_sentiment", "Positive"),
                tech_stack=data.get("tech_stack", "AI"),
                reliability_score=data.get("reliability_score", 90.0),
                hype_factor=data.get("hype_factor", False),
                visual_proofs=proofs
            )
            
            print(f"Scout: Mission Report. 1 candidate extracted: {finding.tool_name}")
            return [finding]
            
        except Exception as e:
            print(f"Scout: Error during discovery: {e}")
            return []
