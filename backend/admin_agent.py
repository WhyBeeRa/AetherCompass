import os
import json
import asyncio
from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup
import httpx
from ddgs import DDGS
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

class DeepAuditorResult(BaseModel):
    name: str = Field(description="The formal name of the AI tool.")
    category: str = Field(description="Broad category (e.g. dev, design, text, video, marketing, enterprise).")
    pricing_model: str = Field(description="Pricing model (e.g. Free, Freemium, Subscription, Unknown).")
    pricing_details: str = Field(description="Specific pricing details if found (e.g. $20/mo).")
    web_consensus: str = Field(description="Summary of what the web says about it (reviews, trust, alternatives).")
    trust_score: float = Field(ge=1.0, le=100.0, description="Trust score from 1-100 based on all findings.")
    pros: List[str] = Field(description="Top 3 pros.")
    cons: List[str] = Field(description="Top 3 cons or red flags.")
    use_cases: List[str] = Field(description="Top 3 use cases.")
    audit_notes: str = Field(description="Final verdict or critical warnings.")
    
    # New metrics for direct vault integration
    accuracy: int = Field(default=4, ge=1, le=5, description="1-5 rating of output reliability.")
    speed: int = Field(default=4, ge=1, le=5, description="1-5 rating of response time.")
    value: int = Field(default=4, ge=1, le=5, description="1-5 rating of cost-effectiveness.")
    ease_of_use: int = Field(default=4, ge=1, le=5, description="1-5 rating of user experience.")
    learning_curve: str = Field(default="Medium", description="Very Easy, Medium, Hard, or Developers Only.")
    visual_quality: str = Field(default="Mid", description="High, Mid, or Low.")
    executive_summary: str = Field(description="2-3 sentences. Objective, cold, and focusing on actual utility and flaws.")
    time_to_value: str = Field(description="Short string (e.g., 'Hours', 'Days', 'Requires heavy onboarding').")
    privacy_grade: str = Field(description="A, B, C, D, or F based on enterprise safety.")
    skill_multiplier: str = Field(description="Short string detailing the actual efficiency gain.")

async def fetch_page(client: httpx.AsyncClient, url: str) -> str:
    try:
        response = await client.get(url, follow_redirects=True, timeout=10.0)
        text = response.text
        # Check if we hit Cloudflare anti-bot challenge
        if response.status_code == 200 and "Just a moment..." not in text and "cf-browser-verification" not in text:
            return text
    except Exception:
        pass
        
    # Fallback to Jina Reader API (Bypasses bot protection and renders JS for LLMs)
    try:
        jina_url = f"https://r.jina.ai/{url}"
        response = await client.get(jina_url, follow_redirects=True, timeout=15.0)
        if response.status_code == 200:
            return response.text # Returns Markdown, which is perfect for the prompt
    except Exception:
        pass
        
    return ""

async def run_deep_audit_stream(url: str):
    """
    Yields JSON strings. First it yields status updates, then the final result.
    """
    yield json.dumps({"type": "log", "message": f"Initializing Deep Audit Protocol for {url}..."}) + "\n"
    await asyncio.sleep(0.5)

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    
    meta_data = {"title": "", "description": "", "text": ""}
    pricing_text = ""
    
    yield json.dumps({"type": "log", "message": "Navigating to target URL..."}) + "\n"
    
    async with httpx.AsyncClient(headers=headers) as client:
        html = await fetch_page(client, url)
        if html:
            yield json.dumps({"type": "log", "message": "Page downloaded successfully. Parsing DOM content..."}) + "\n"
            soup = BeautifulSoup(html, 'html.parser')
            meta_data["title"] = soup.title.string.strip() if soup.title else ""
            desc = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
            if desc:
                meta_data["description"] = desc.get("content", "").strip()
            
            # Extract basic text (first 2000 chars)
            text_content = soup.get_text(separator=' ', strip=True)
            meta_data["text"] = text_content[:2000]

            # Look for pricing page
            yield json.dumps({"type": "log", "message": "Scanning site architecture for Pricing/Terms..."}) + "\n"
            pricing_url = None
            for link in soup.find_all('a', href=True):
                href = link['href'].lower()
                if 'pricing' in href or 'plans' in href:
                    if link['href'].startswith('http'):
                        pricing_url = link['href']
                    else:
                        base_url = url.rstrip('/')
                        pricing_url = f"{base_url}/{link['href'].lstrip('/')}"
                    break
            
            if pricing_url:
                yield json.dumps({"type": "log", "message": f"Identified pricing endpoint at {pricing_url}. Fetching..."}) + "\n"
                p_html = await fetch_page(client, pricing_url)
                if p_html:
                    p_soup = BeautifulSoup(p_html, 'html.parser')
                    pricing_text = p_soup.get_text(separator=' ', strip=True)[:2000]
                    yield json.dumps({"type": "log", "message": "Pricing structure extracted successfully."}) + "\n"
                else:
                    yield json.dumps({"type": "log", "message": "Failed to bypass security on pricing page."}) + "\n"
        else:
            yield json.dumps({"type": "log", "message": "Failed to fetch homepage. Target might be blocking bots. Proceeding with limited intel."}) + "\n"

    # Guess name from URL or title
    fallback_name = url.split("//")[-1].split("/")[0].replace("www.", "").split(".")[0].capitalize()
    extracted_name = meta_data["title"].split("|")[0].split("-")[0].strip() or fallback_name

    yield json.dumps({"type": "log", "message": f"Subject identified as: '{extracted_name}'. Deploying external web scouts..."}) + "\n"
    
    web_results = []
    try:
        with DDGS() as ddgs:
            query = f'"{extracted_name}" AI tool site:reddit.com OR site:hackernews.com review OR pricing complaints'
            results = ddgs.text(query, max_results=5)
            for r in results:
                web_results.append(f"Source: {r.get('href')}\nSnippet: {r.get('body')}")
        yield json.dumps({"type": "log", "message": f"Intercepted {len(web_results)} external intelligence reports."}) + "\n"
    except Exception as e:
        yield json.dumps({"type": "log", "message": f"External scout deployment failed: {e}"}) + "\n"

    web_text = "\n---\n".join(web_results)

    yield json.dumps({"type": "log", "message": "Injecting gathered intelligence into Gemini Core for analysis..."}) + "\n"
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        yield json.dumps({"type": "error", "message": "GEMINI_API_KEY not found in environment."}) + "\n"
        return

    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    Role: You are Aether's Lead Auditor, a highly cynical, objective, and deeply technical AI strategist. Your goal is to protect enterprise clients from marketing fluff.

    The 80/20 Rule: You MUST assign 80% of your evaluation weight to the external scout data (community sentiment, Reddit complaints, hidden costs, bugs) and only 20% to the official website's claims.

    Banned Words: Never use marketing fluff. Banned words include: "empowering", "revolutionize", "magic", "seamless", "cutting-edge", "game-changer".

    Trust Score Logic: The `trust_score` (1-100) must start at 50. Deduct points heavily for hidden pricing, forced enterprise demos, or strong community complaints. Add points ONLY for verifiable open-source code, transparent pricing, and overwhelming positive developer/user sentiment. 90+ scores should be exceptionally rare.

    Formatting constraints: Do not use semicolons or the em-dash character in your output. Use standard hyphens instead.

    Target URL: {url}
    Extracted Subject Name: {extracted_name}
    Scraped Title: {meta_data['title']}
    Scraped Description: {meta_data['description']}
    Homepage Snippet: {meta_data['text']}
    
    Pricing Page Snippet: {pricing_text if pricing_text else "Not found"}
    
    External Web Intelligence (Reviews, Mentions, Alternatives):
    {web_text if web_text else "No external data found. Be highly skeptical and lower trust score significantly."}
    
    Evaluate this tool thoroughly based on the strict directives above. Return the audit results in the exact requested JSON structure.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=DeepAuditorResult,
            ),
        )
        
        audit_result = response.parsed
        yield json.dumps({"type": "log", "message": "Analysis complete. Generating final intelligence report..."}) + "\n"
        yield json.dumps({
            "type": "result",
            "data": audit_result.model_dump()
        }) + "\n"
    except Exception as e:
        yield json.dumps({"type": "error", "message": f"Gemini synthesis failed: {e}"}) + "\n"
