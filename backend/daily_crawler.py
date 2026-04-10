import os
import sqlite3
import json
import asyncio
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai

from models import LabAnalysis, ToolMetrics, VisualQuality, IntentMapping, AuditLog
from persistence import AetherVault

load_dotenv()

SYSTEM_PROMPT = """You are Aether's Daily AI Crawler.
Your job is to analyze raw information about a new AI tool and extract deep intelligence.
You MUST extract the data in a STRICT JSON format that matches the following schema perfectly.

Required JSON Structure:
{
    "tool_name": "Name of the tool",
    "source_url": "The true original URL where the tool was found or its official website",
    "job_to_be_done": ["Category 1", "Category 2"],
    "limitations": ["Limitation 1", "Limitation 2"],
    "privacy_policy": "Summary of privacy policy (e.g., trains on data, enterprise only, no training)",
    "social_proof": "A short, summarized quote from a user or developer validating it",
    "executive_summary": "1st sentence is peak capability. 2nd sentence is the trade-off.",
    "pros": ["Pro 1", "Pro 2"],
    "cons": ["Con 1", "Con 2"],
    "use_cases": ["Use Case 1", "Use Case 2"],
    "metrics": {
        "accuracy": 4, # 1-5
        "speed": 4, # 1-5
        "value": 4, # 1-5
        "ease_of_use": 3, # 1-5
        "learning_curve": "קל מאוד / בינוני / מיועד למפתחים",
        "pricing": "Freemium / תשלום חודשי / API",
        "integration": "Web / API / VS Code"
    },
    "intents_mapped": [
        {
            "intent_description": "Specific intent (e.g., Writing marketing copy)",
            "success_score": 95,
            "trade_off": "Can be repetitive"
        }
    ]
}

DO NOT wrap the response in markdown blocks (e.g., ```json). Return ONLY the raw JSON string.
"""

from google import genai
from google.genai import types

async def analyze_tool_with_gemini(tool_info: str):
    print(f"Analyzing: {tool_info[:50]}...")
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Missing GOOGLE_API_KEY or GEMINI_API_KEY")

    client = genai.Client(api_key=api_key)
    
    prompt = f"Analyze the following AI tool information:\n\n{tool_info}"
    
    attempt = 1
    base_wait = 5
    max_wait = 60
    while attempt <= 7:
        try:
            print(f"Attempting to call Gemini API (attempt {attempt})...")
            # Using synchronous call in a thread for the new SDK just in case async client is tricky
            response = await asyncio.to_thread(
                client.models.generate_content,
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.1,
                    response_mime_type="application/json"
                )
            )
            print("Successfully received Gemini response.")
            break
        except Exception as e:
            if "429" in str(e) or "Quota" in str(e) or "ResourceExhausted" in type(e).__name__:
                wait_time = min(base_wait * (2 ** (attempt - 1)), max_wait)
                print(f"Rate limit hit (429). Exponential Backoff: Waiting {wait_time} seconds before retry {attempt}...")
                await asyncio.sleep(wait_time)
                attempt += 1
            else:
                print(f"Failed Gemini call with non-rate-limit error: {e}")
                return None
    
    if attempt > 7:
        print("Max retries reached for Gemini call.")
        return None
    
    try:
        data = json.loads(response.text)
        return data
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON from Gemini: {e}\nResponse: {response.text}")
        return None

async def process_single_tool(tool_raw_info: str, vault: AetherVault, semaphore: asyncio.Semaphore):
    async with semaphore:
        result = await analyze_tool_with_gemini(tool_raw_info)
        
        if result:
            tool_name = result.get("tool_name", "Unknown")
            source_url = result.get("source_url")
            
            # Map metrics
            m_data = result.get("metrics", {})
            metrics = ToolMetrics(
                accuracy=m_data.get("accuracy", 3),
                speed=m_data.get("speed", 3),
                value=m_data.get("value", 3),
                ease_of_use=m_data.get("ease_of_use", 3),
                learning_curve=m_data.get("learning_curve", "בינוני"),
                pricing=m_data.get("pricing", "Freemium"),
                integration=m_data.get("integration", "Web / API")
            )
            
            # Map intents
            intents_mapped = []
            for item in result.get("intents_mapped", []):
                intents_mapped.append(IntentMapping(
                    intent_description=item.get("intent_description", ""),
                    success_score=item.get("success_score", 0),
                    trade_off=item.get("trade_off")
                ))

            # Build Analysis
            analysis = LabAnalysis(
                tool_name=tool_name,
                metrics=metrics,
                visual_quality=VisualQuality.MID,
                job_to_be_done=result.get("job_to_be_done", []),
                intents_mapped=intents_mapped,
                executive_summary=result.get("executive_summary", ""),
                pros=result.get("pros", []),
                cons=result.get("cons", []),
                use_cases=result.get("use_cases", []),
                limitations=result.get("limitations", []),
                privacy_policy=result.get("privacy_policy", "Unknown"),
                social_proof=result.get("social_proof"),
                source_findings_id="daily_crawler"
            )
            
            # Provide an external reference inside the pipeline if source exists
            if source_url and tool_name != "Unknown":
                analysis.executive_summary += f" [Source: {source_url}]"

            # Calculate an aggregate trust score based on intents
            if intents_mapped:
                trust_score = sum(i.success_score for i in intents_mapped) / len(intents_mapped)
            else:
                trust_score = 70.0 # Default if empty
                
            audit = AuditLog(
                tool_name=tool_name,
                action="Daily Crawl Ingestion",
                reason="Automatic deep analysis via Gemini Crawler",
                new_trust_score=trust_score
            )
            
            # Save to persistent Vault DB
            vault.save_tool(
                tool_name=tool_name,
                analysis=analysis,
                trust_score=trust_score,
                gallery=[], # Gallery fetching would be a separate image ingestion step (persistence.py protects existing)
                audit_log=audit
            )
            print(f"Successfully ingested & deep-mapped: {tool_name}")
            
        # Respect rate limits even with concurrency
        await asyncio.sleep(2)

async def run_daily_crawl(target_tools: list[str]):
    print(f"--- Starting Aether Daily Crawl: {datetime.now()} ---")
    vault = AetherVault()
    
    # Process up to 5 tools concurrently
    semaphore = asyncio.Semaphore(5)
    
    tasks = [process_single_tool(info, vault, semaphore) for info in target_tools]
    await asyncio.gather(*tasks)
            
    print("--- Daily Crawl Complete ---")

if __name__ == "__main__":
    # Top 50 AI Tools List
    target_tools_list = [
        "ChatGPT", "Claude 3", "Midjourney", "Jasper", "Runway",
        "Perplexity", "GitHub Copilot", "Cursor", "ElevenLabs", "Zapier",
        "Synthesia", "Notion AI", "DALL-E 3", "Sora", "Gemini",
        "Mistral", "Llama 3", "Hugging Face", "Leonardo AI", "Copy.ai",
        "Writesonic", "Descript", "Canva Magic Studio", "Fireflies.ai", "Otter.ai",
        "Gamma", "Tome", "Beautiful.ai", "Veed", "InVideo",
        "Murf AI", "PlayHT", "Tabnine", "Amazon Q", "Devin",
        "AutoGPT", "AgentGPT", "Character.ai", "Pi", "Harvey",
        "Grammarly", "QuillBot", "Wordtune", "Stable Diffusion", "Krea",
        "Magnific", "Pika", "Suno", "Udio", "Phind"
    ]
    
    simulated_scraping_feed = [
        f"Analyze the AI tool '{tool}'. Extract its category, real limitations, objective pros and cons, pricing model, speed, ease of use, accuracy, and user intents it solves. Find the true project or company URL and place it in the source_url field. Provide a highly objective evaluation."
        for tool in target_tools_list
    ]
    
    asyncio.run(run_daily_crawl(simulated_scraping_feed))
