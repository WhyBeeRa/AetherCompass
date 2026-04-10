import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

backend_dir = Path(__file__).resolve().parent
sys.path.append(str(backend_dir))
load_dotenv(backend_dir / ".env")

from pipeline import AetherPipeline

async def run_scan():
    print("Initiating Initial Aether Real LLM Scan...")
    
    # Target MVP List
    mvp_tools = [
        "ChatGPT (Text/Productivity)",
        "Claude 3.5 Sonnet (Text/Productivity)",
        "Perplexity (Text/Productivity)",
        "Midjourney v6 (Design/Images)",
        "DALL-E 3 (Design/Images)",
        "GitHub Copilot (Code)",
        "Cursor AI (Code)",
        "ElevenLabs (Audio/Voice)",
        "Zapier (Automation)"
    ]
    
    # Ensure API Key exists
    if not os.environ.get("GEMINI_API_KEY"):
        print("ERROR: GEMINI_API_KEY is not set in your .env file!")
        print("Please add it before running the scan.")
        return
        
    pipeline = AetherPipeline()
    
    for intent in mvp_tools:
        print(f"\n[{intent}] --- Starting Pipeline ---")
        try:
            result = await pipeline.run_pipeline(intent)
            if result.get("status") == "success":
                print(f"✅ Successfully scanned, analyzed, and saved: {result.get('tool_name')}")
            else:
                print(f"❌ Failed or Rejected for {intent}: {result.get('reason')}")
        except Exception as e:
            print(f"⚠️ Critical Error during pipeline execution for {intent}: {e}")
            
    print("\nInitial Scan Cycle Complete.")

if __name__ == "__main__":
    # Ensure asyncio event loop runs properly on Windows
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_scan())
