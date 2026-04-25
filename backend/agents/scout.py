import asyncio
import os
import json
import aiohttp
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from models import ScoutFindings, VisualProof
from google import genai
from google.genai import types
from dotenv import load_dotenv
try:
    from logger_utils import log_terminal
except ImportError:
    # Fallback for standalone testing
    async def log_terminal(m): print(m)

load_dotenv()

class ScoutResponseSchema(BaseModel):
    """
    Structured response schema for the Scout Agent.
    """
    tool_name: str = Field(..., description="Name of the AI tool discovered")
    source: str = Field(..., description="The specific source where this tool was found (e.g. Reddit r/LocalLLaMA)")
    user_intent: str = Field(..., description="The specific problem or intent this tool solves")
    raw_sentiment: str = Field(..., description="A summary of community sentiment or developer feedback")
    tech_stack: str = Field(..., description="Technical stack (e.g. Transformers, Python, API-only)")
    reliability_score: int = Field(..., ge=0, le=100, description="Calculated reliability score from 0-100 based on evidence")
    hype_factor: bool = Field(..., description="True if the tool is surrounded by marketing hype vs real substance")
    visual_proofs: List[dict] = Field(..., description="List of visual proofs with 'url' and 'source_url'. Use null for url if no image.")

SCOUT_SYSTEM_PROMPT = """
Role: You are the Commander of the "Scout" Agent for Aether - the Single Source of Truth for the AI world. 
Your mission is to bypass marketing hype and retrieve raw, verified evidence of AI tool capabilities.

Objective: Analyze the provided Reddit discussion data to identify a specific AI tool matching the user's intent. 
Focus on delivering factual, evidence-based results.

Instructions:
- If no specific tool is found in the data, try to identify the most relevant tool being discussed.
- Calculate a reliability_score (0-100) based on the depth of technical discussion and absence of "hype" words.
- For visual_proofs, if a real image URL is present in the discussion, use it. Otherwise, set the 'url' to null. 
- DO NOT use Unsplash or any other placeholder image service.
- The 'source_url' must be the link to the Reddit post or tool website.
"""

class ScoutAgent:
    def __init__(self):
        """
        The Scout: Officer of Discovery.
        Scans Reddit via public JSON endpoints and uses GenAI to find and verify new AI tools.
        """
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("WARNING: GEMINI_API_KEY is missing. ScoutAgent is disabled.")
            self.client = None
        else:
            self.client = genai.Client(api_key=api_key)

        # Unique User-Agent to avoid Reddit 429 errors
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AetherScout/1.0"
        }

    async def fetch_reddit_context(self, query: str, limit: int = 10) -> str:
        """
        Fetches data from public Reddit JSON endpoints using aiohttp.
        """
        subreddits = ["LocalLLaMA", "MachineLearning", "ArtificialInteligence", "ChatGPTCoders"]
        all_context = []
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            for sub in subreddits:
                # Using search endpoint to find relevant tools for the intent
                url = f"https://www.reddit.com/r/{sub}/search.json?q={query}&limit={limit}&restrict_sr=1&sort=relevance"
                try:
                    async with session.get(url, timeout=10) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            children = data.get("data", {}).get("children", [])
                            for child in children:
                                post = child.get("data", {})
                                title = post.get("title", "")
                                selftext = post.get("selftext", "")[:800] # Limit text per post
                                all_context.append(f"Subreddit: r/{sub}\nTitle: {title}\nContent: {selftext}\nURL: https://reddit.com{post.get('permalink', '')}")
                        elif resp.status == 429:
                            print(f"Scout: Reddit rate limited (429) for r/{sub}")
                        else:
                            print(f"Scout: Reddit error {resp.status} for r/{sub}")
                except Exception as e:
                    print(f"Scout: Error fetching from r/{sub}: {e}")
        
        return "\n---\n".join(all_context) if all_context else "No Reddit data found for this intent."

    async def run_discovery_cycle(self, intent: str) -> List[ScoutFindings]:
        if not self.client:
            await log_terminal(f"Scout: Discovery skipped for '{intent}' (Gemini disabled).")
            return []

        await log_terminal(f"Scout: Initiating Operation for intent '{intent}' using Public Reddit API...")
        
        # 1. Fetch Reddit Context
        reddit_data = await self.fetch_reddit_context(intent)
        
        prompt = f"{SCOUT_SYSTEM_PROMPT}\n\nUser Intent: {intent}\n\nReddit Data Found:\n{reddit_data}"
        
        try:
            # 2. Call Gemini using native async client
            response = await self.client.aio.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ScoutResponseSchema
                )
            )
            
            data = response.parsed
            
            proofs = []
            for vp in data.visual_proofs:
                proofs.append(VisualProof(
                    url=vp.get("url"), 
                    source_url=vp.get("source_url") or "https://reddit.com"
                ))
                
            finding = ScoutFindings(
                tool_name=data.tool_name,
                source=data.source,
                user_intent=data.user_intent,
                raw_sentiment=data.raw_sentiment,
                tech_stack=data.tech_stack,
                reliability_score=float(data.reliability_score),
                hype_factor=data.hype_factor,
                visual_proofs=proofs
            )
            
            await log_terminal(f"Scout: Mission Report. Candidate identified: {finding.tool_name} (Reliability: {finding.reliability_score})")
            return [finding]
            
        except Exception as e:
            print(f"Scout: Error during discovery cycle: {e}")
            return []
