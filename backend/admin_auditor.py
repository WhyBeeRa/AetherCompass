import sys
import os
import json
import asyncio
from typing import Dict, Any, List
from bs4 import BeautifulSoup
import httpx
from duckduckgo_search import DDGS
from pydantic import BaseModel, Field

# Ensure Google GenAI is correctly imported
try:
    from google import genai
    from google.genai import types
except ImportError:
    import google.generativeai as genai

# Models
class VaultAuditorResult(BaseModel):
    name: str = Field(description="The formal name of the AI tool extracted from the page or search.")
    category: str = Field(description="Broad category of the tool (e.g. dev, design, text, video, audio, marketing, presentations, enterprise).")
    pricing_model: str = Field(description="Pricing model commonly mentioned (e.g. Free, Freemium, $20/month, Subscription). If unknown, say 'Unknown'.")
    community_consensus: str = Field(description="A single insightful sentence summarizing the community's honest opinion (Reddit/HackerNews/Builders), highlighting real-world utility vs marketing hype.")
    trust_score: float = Field(ge=0, le=100, description="A score from 0-100 indicating community trust. High if reviews show it actually works well, low if it's considered a scam, buggy, or overly hyped.")
    pros: List[str] = Field(default_factory=list, description="Top 3 pros mentioned by users.")
    cons: List[str] = Field(default_factory=list, description="Top 3 cons or limitations commonly complained about.")

async def scrape_tool_meta(url: str) -> Dict[str, str]:
    """Fetches rudimentary meta tags from the URL."""
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            
        soup = BeautifulSoup(resp.text, 'html.parser')
        title = soup.title.string if soup.title else ""
        meta_desc = ""
        meta_node = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
        if meta_node:
           meta_desc = meta_node.get('content', '')
           
        return {
            "title": title.strip()[:200],
            "description": meta_desc.strip()[:500]
        }
    except Exception as e:
         print(f"[Auditor] Meta scrape failed for {url}: {e}")
         return {"title": "Unknown", "description": ""}

def search_community_consensus(tool_name: str) -> str:
    """Uses DDGS to find what the community actually says."""
    if not tool_name or tool_name.lower() == "unknown":
         return ""
         
    query = f"site:reddit.com \"{tool_name}\" (review OR scam OR worth it OR alternative)"
    try:
        results = DDGS().text(query, max_results=5)
        texts = [res.get("body", "") for res in results if res.get("body")]
        return "\n--- DDGS RESULT ---\n".join(texts)
    except Exception as e:
        print(f"[Auditor] DDGS failed for {tool_name}: {e}")
        return ""

async def run_vault_audit(url: str) -> Dict[str, Any]:
    """Main function to audit a tool visually and socially."""
    # 1. Scrape Site Metadata
    meta_info = await scrape_tool_meta(url)
    inferred_name = meta_info.get("title", url).split("-")[0].split("|")[0].strip()
    
    # 2. Search Community Consensus
    community_text = search_community_consensus(inferred_name)
    
    # 3. Analyze with Gemini Pydantic Output
    prompt = f"""
You are the Lead Auditor for Aether Compass. Your job is to analyze AI tools not by their marketing, but by what builders and users actually say.

Target Tool URL: {url}
Meta Title: {meta_info.get('title')}
Meta Description: {meta_info.get('description')}

Raw Community Chatter (Reddit/Forums):
{community_text if community_text else '(No significant community chatter found. You may have to infer strictly from the meta info, but penalize trust score due to lack of social proof.)'}

Please provide a structured honest assessment returning exactly the JSON matching the requested schema. Ensure `community_consensus` is brutally honest.
"""

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
         raise ValueError("GEMINI_API_KEY not set")

    try:
        # Use new Google GenAI SDK if available, else fallback
        if 'google.genai.types' in sys.modules or 'google.genai' in sys.modules:
             client = genai.Client(api_key=api_key)
             response = client.models.generate_content(
                 model='gemini-2.5-flash',
                 contents=prompt,
                 config=types.GenerateContentConfig(
                     response_mime_type="application/json",
                     response_schema=VaultAuditorResult,
                 ),
             )
             structured_data = json.loads(response.text)
        else:
            # Fallback to old SDK
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            # Without strong schema enforcement we just ask for JSON manually or using old typed dicts.
            import pydantic
            response = model.generate_content(
                  prompt + "\nIMPORTANT: Return ONLY raw JSON strictly adhering to this Pydantic Schema: " + json.dumps(VaultAuditorResult.model_json_schema()),
                  generation_config=genai.types.GenerationConfig(response_mime_type="application/json")
            )
            structured_data = json.loads(response.text)

        # Ensure values
        result = VaultAuditorResult(**structured_data)
        
        return {
             "status": "success",
             "url": url,
             "audit_data": result.model_dump()
        }

    except Exception as e:
         print(f"[Auditor] Gemini analysis failed for {url}: {e}")
         return {
              "status": "error",
              "url": url,
              "reason": str(e)
         }
