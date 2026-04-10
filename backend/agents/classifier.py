import asyncio
import os
import json
from datetime import datetime
from typing import List, Dict
from ..models import ScoutFindings, LabAnalysis, ToolMetrics, VisualQuality, IntentMapping
import google.genai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

LAB_SYSTEM_PROMPT = """
Role: You are the Senior Intelligence Analyst (The Classifier) for Aether. Your task is to transform raw technical data and social evidence into structured, intent-based insights.

Objective: Analyze the output from the Scout Agent and categorize it into the "Single Source of Truth" framework.

You must output ONLY valid JSON matching this schema:
{
  "metrics": {
    "accuracy": 4, // 1-5 integer
    "speed": 4, // 1-5 integer
    "value": 4, // 1-5 integer
    "ease_of_use": 4, // 1-5 integer
    "learning_curve": "string description (e.g. קל מאוד, בינוני, קשה)",
    "pricing": "string description (e.g. Freemium)",
    "integration": "string description (e.g. Web / API)"
  },
  "visual_quality": "High", // High, Mid, or Low
  "job_to_be_done": ["Broad Goal 1", "Broad Goal 2"],
  "intents_mapped": [
    {
        "intent_description": "Specific intent (e.g. Automating lead gen)",
        "success_score": 95.0, // 0-100 float
        "trade_off": "Trade off description or null"
    }
  ],
  "executive_summary": "Two sentences. First peak, second trade-off. Use Hebrew if appropriate or English.",
  "pros": ["Pro 1", "Pro 2"],
  "cons": ["Con 1", "Con 2"],
  "use_cases": ["Use Case 1", "Use Case 2"]
}
"""

class ClassifierAgent:
    """
    The Lab: Officer of Analysis.
    Transforming raw evidence into The Truth.
    """
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})

    async def _query_llm(self, prompt: str, findings: ScoutFindings) -> Dict:
        full_prompt = f"{prompt}\n\nScout Findings:\n{findings.model_dump_json()}"
        try:
            response = await asyncio.to_thread(self.model.generate_content, full_prompt)
            data = json.loads(response.text)
            return data
        except Exception as e:
            print(f"Classifier error: {e}")
            # Fallback
            return {
                "metrics": {"accuracy": 3, "speed": 3, "value": 3, "ease_of_use": 3, "learning_curve": "בינוני", "pricing": "Unknown", "integration": "Web"},
                "visual_quality": "Mid",
                "job_to_be_done": [findings.user_intent],
                "intents_mapped": [{"intent_description": findings.user_intent, "success_score": 50.0, "trade_off": "Unknown"}],
                "executive_summary": f"{findings.tool_name} is an AI tool. Trade-offs unknown.",
                "pros": ["Unknown"],
                "cons": ["Unknown"],
                "use_cases": [findings.user_intent]
            }

    async def analyze(self, findings: ScoutFindings) -> LabAnalysis:
        print(f"Lab: Analyzing findings for {findings.tool_name}...")
        
        llm_output = await self._query_llm(LAB_SYSTEM_PROMPT, findings)
        
        metrics_data = llm_output.get("metrics", {})
        metrics = ToolMetrics(
            accuracy=metrics_data.get("accuracy", 3),
            speed=metrics_data.get("speed", 3),
            value=metrics_data.get("value", 3),
            ease_of_use=metrics_data.get("ease_of_use", 3),
            learning_curve=metrics_data.get("learning_curve", "בינוני"),
            pricing=metrics_data.get("pricing", "Freemium"),
            integration=metrics_data.get("integration", "Web / API"),
            last_verified=datetime.now()
        )
        
        mapped_intents = []
        for im in llm_output.get("intents_mapped", []):
            mapped_intents.append(IntentMapping(
                intent_description=im.get("intent_description", ""),
                success_score=im.get("success_score", 50.0),
                trade_off=im.get("trade_off")
            ))
            
        jobs = llm_output.get("job_to_be_done", [])
        if findings.user_intent not in jobs:
            jobs.append(findings.user_intent)
            
        analysis = LabAnalysis(
            tool_name=findings.tool_name,
            metrics=metrics,
            visual_quality=VisualQuality(llm_output.get("visual_quality", "Mid")),
            job_to_be_done=jobs,
            intents_mapped=mapped_intents,
            executive_summary=llm_output.get("executive_summary", ""),
            pros=llm_output.get("pros", []),
            cons=llm_output.get("cons", []),
            use_cases=llm_output.get("use_cases", []),
            source_findings_id=None
        )
        
        print(f"Lab: Analysis Complete. Verified: {analysis.executive_summary}")
        return analysis
