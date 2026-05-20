import os
import json
import asyncio
from typing import List, Optional
from bs4 import BeautifulSoup
import httpx
from ddgs import DDGS
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

class VaultAuditorResult(BaseModel):
    name: str = Field(description="The formal name of the AI tool.")
    category: str = Field(description="Broad category (e.g. dev, design, text, video, marketing).")
    pricing_model: str = Field(description="Pricing model (e.g. Free, Freemium, Subscription).")
    community_consensus: str = Field(description="1 sentence summary of Reddit sentiment.")
    trust_score: int = Field(ge=1, le=100, description="Trust score from 1-100 based on community feedback.")
    audit_notes: str = Field(description="Red flags or critical warnings about the tool.")

async def run_lean_audit(url: str):
    """
    Runs a lean audit on a URL using BeautifulSoup, DDGS, and Gemini Flash.
    """
    print(f"[Vault Auditor] Starting lean audit for: {url}")
    
    # 1. Scrape Title and Meta Description
    meta_data = {"title": "", "description": ""}
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        async with httpx.AsyncClient(headers=headers, timeout=10.0, follow_redirects=True) as client:
            response = await client.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                meta_data["title"] = soup.title.string.strip() if soup.title else ""
                desc = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
                if desc:
                    meta_data["description"] = desc.get("content", "").strip()
    except Exception as e:
        print(f"[Vault Auditor] Scrape failed: {e}")

    extracted_name = meta_data["title"].split("|")[0].split("-")[0].strip() or url
    
    # 2. Fetch Reddit Sentiment via DDGS
    reddit_results = []
    try:
        with DDGS() as ddgs:
            query = f'site:reddit.com "{extracted_name}" (review OR scam)'
            results = ddgs.text(query, max_results=10)
            for r in results:
                reddit_results.append(r.get('body', ''))
    except Exception as e:
        print(f"[Vault Auditor] DDGS search failed: {e}")

    reddit_text = "\n---\n".join(reddit_results)

    # 3. Analyze with Gemini 1.5 Flash
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"status": "error", "reason": "GEMINI_API_KEY not found"}

    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    You are a 'Cynical Tech Auditor'. Your mission is to evaluate AI tools based on limited scraped data and community chatter.
    Be skeptical. Look for hype vs reality.
    
    Tool URL: {url}
    Scraped Title: {meta_data['title']}
    Scraped Description: {meta_data['description']}
    
    Reddit Community Chatter:
    {reddit_text if reddit_text else "No Reddit results found. Be extremely cautious."}
    
    Evaluate this tool and return the audit results in a structured format.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=VaultAuditorResult,
            ),
        )
        
        audit_result = response.parsed
        return {
            "status": "success",
            "audit_data": audit_result.model_dump()
        }
    except Exception as e:
        print(f"[Vault Auditor] Gemini analysis failed: {e}")
        return {"status": "error", "reason": str(e)}
