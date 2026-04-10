import os
import sqlite3
import json
import asyncio
from datetime import datetime

from models import LabAnalysis, ToolMetrics, VisualQuality, IntentMapping, AuditLog
from persistence import AetherVault

async def inject_mocks():
    print(f"--- Starting Aether Direct Mock Injection ---")
    vault = AetherVault()
    
    mock_data = [
        {
            "tool_name": "Claude 3.5 Sonnet",
            "job_to_be_done": ["Coding", "Writing"],
            "limitations": ["Limited internet access", "Rate limits"],
            "privacy_policy": "No training on API data",
            "social_proof": "The best coding assistant currently available.",
            "executive_summary": "Extremely fast and capable reasoning model. Lacks multimodal generation.",
            "pros": ["Top-tier coding ability", "Fast response", "Large context window"],
            "cons": ["Cannot generate images", "Stricter safety filters"],
            "use_cases": ["Software Development", "Content Creation", "Data Analysis"],
            "metrics": {"accuracy": 5, "speed": 5, "value": 4, "ease_of_use": 4, "learning_curve": "קל מאוד", "pricing": "Freemium", "integration": "Web / API"},
            "intents_mapped": [
                {"intent_description": "Writing code", "success_score": 98, "trade_off": "Can hallucinate complex architecture"},
                {"intent_description": "Summarizing docs", "success_score": 95, "trade_off": "None"}
            ]
        },
        {
            "tool_name": "Perplexity AI",
            "job_to_be_done": ["Research", "Search"],
            "limitations": ["Relies on web scraping", "Sometimes synthesizes incorrectly"],
            "privacy_policy": "Opt-out available for training",
            "social_proof": "It replaced Google for me.",
            "executive_summary": "Incredible conversational search engine. Can be unstable on niche topics.",
            "pros": ["Real-time web access", "Citations provided", "Multiple LLM options"],
            "cons": ["Paywall for advanced models", "UI can be cluttered"],
            "use_cases": ["Academic Research", "News Aggregation"],
            "metrics": {"accuracy": 4, "speed": 5, "value": 5, "ease_of_use": 5, "learning_curve": "קל מאוד", "pricing": "Freemium", "integration": "Web / App"},
            "intents_mapped": [
                {"intent_description": "Fact checking", "success_score": 90, "trade_off": "Depends on source quality"}
            ]
        },
        {
            "tool_name": "ChatGPT",
            "job_to_be_done": ["General Utility", "Conversation"],
            "limitations": ["Generic writing style", "High rate of hallucination on math"],
            "privacy_policy": "Opt-out available",
            "social_proof": "The industry standard AI.",
            "executive_summary": "The most versatile omni-model. Writing style is often recognizable.",
            "pros": ["Voice mode", "DALL-E integration", "Custom GPTs"],
            "cons": ["Writing requires heavy editing", "Occasional lazy coding"],
            "use_cases": ["Brainstorming", "Everyday tasks", "Translation"],
            "metrics": {"accuracy": 4, "speed": 5, "value": 5, "ease_of_use": 5, "learning_curve": "קל מאוד", "pricing": "Freemium", "integration": "Web / App / API"},
            "intents_mapped": [
                {"intent_description": "Drafting emails", "success_score": 92, "trade_off": "Needs tone adjustments"}
            ]
        },
        {
            "tool_name": "Midjourney v6",
            "job_to_be_done": ["Image Generation"],
            "limitations": ["Discord only UI", "Hard to control specific text"],
            "privacy_policy": "Trains on user generations",
            "social_proof": "Unmatched aesthetic quality.",
            "executive_summary": "Produces the most beautiful AI images. UI is non-existent outside Discord.",
            "pros": ["Photorealism", "Artistic styles", "High resolution"],
            "cons": ["Discord interface", "Steep prompting curve"],
            "use_cases": ["Concept Art", "Marketing Assets"],
            "metrics": {"accuracy": 4, "speed": 3, "value": 4, "ease_of_use": 2, "learning_curve": "בינוני", "pricing": "תשלום חודשי", "integration": "Discord"},
            "intents_mapped": [
                {"intent_description": "Generating realistic photos", "success_score": 95, "trade_off": "Takes multiple iterations"}
            ]
        },
        {
            "tool_name": "ElevenLabs",
            "job_to_be_done": ["Voice Generation", "Text-to-Speech"],
            "limitations": ["Expensive at scale", "Some languages sound robotic"],
            "privacy_policy": "Does not claim ownership of generated audio",
            "social_proof": "The voices sound entirely human.",
            "executive_summary": "The best TTS engine available. Pricing scales quickly.",
            "pros": ["Emotional range", "Voice cloning", "Low latency API"],
            "cons": ["Cost", "Interface is simple"],
            "use_cases": ["Audiobooks", "Video Voiceovers", "Game Assets"],
            "metrics": {"accuracy": 5, "speed": 4, "value": 4, "ease_of_use": 5, "learning_curve": "קל מאוד", "pricing": "Freemium", "integration": "API / Web"},
            "intents_mapped": [
                {"intent_description": "Voice cloning", "success_score": 98, "trade_off": "Requires clean audio sample"}
            ]
        },
        {
            "tool_name": "Runway Gen-3 Alpha",
            "job_to_be_done": ["Video Generation"],
            "limitations": ["High compute cost", "Generates only short clips"],
            "privacy_policy": "Trains on public models",
            "social_proof": "Incredible temporal consistency and physics.",
            "executive_summary": "Pushes the boundary of AI video. Control is still limited.",
            "pros": ["Cinematic quality", "Text-to-video", "Temporal consistency"],
            "cons": ["expensive", "Character morphing issues"],
            "use_cases": ["B-Roll", "Music Videos", "Ads"],
            "metrics": {"accuracy": 3, "speed": 3, "value": 4, "ease_of_use": 4, "learning_curve": "בינוני", "pricing": "תשלום חודשי", "integration": "Web"},
            "intents_mapped": [
                {"intent_description": "Cinematic B-Roll", "success_score": 85, "trade_off": "Hard to control exact camera moves"}
            ]
        },
        {
            "tool_name": "GitHub Copilot",
            "job_to_be_done": ["Coding Assistant", "Code Completion"],
            "limitations": ["Can suggest insecure code", "Requires context management"],
            "privacy_policy": "Enterprise versions do not train",
            "social_proof": "Saves me hours every week.",
            "executive_summary": "The default AI pair programmer. Sometimes lacks full-repo understanding.",
            "pros": ["IDE native", "Fast autocomplete", "Inline chat"],
            "cons": ["Not as smart as Claude 3.5 Sonnet", "Subscription required"],
            "use_cases": ["Boilerplate coding", "Refactoring", "Writing tests"],
            "metrics": {"accuracy": 4, "speed": 5, "value": 5, "ease_of_use": 5, "learning_curve": "קל מאוד", "pricing": "תשלום חודשי", "integration": "VS Code"},
            "intents_mapped": [
                {"intent_description": "Autocompleting functions", "success_score": 90, "trade_off": "Requires manual review"}
            ]
        },
        {
            "tool_name": "Notion AI",
            "job_to_be_done": ["Writing", "Organization"],
            "limitations": ["Confined to Notion", "Basic generation quality"],
            "privacy_policy": "Does not use your data to train public models",
            "social_proof": "Perfectly integrated into my workspace.",
            "executive_summary": "Convenient workspace assistant. Output quality is standard.",
            "pros": ["Native integration", "Summarizes databases", "Frictionless UI"],
            "cons": ["Uses older models", "Limited outside Notion"],
            "use_cases": ["Meeting notes", "Drafting docs", "Task extraction"],
            "metrics": {"accuracy": 3, "speed": 4, "value": 4, "ease_of_use": 5, "learning_curve": "קל מאוד", "pricing": "תשלום חודשי", "integration": "App"},
            "intents_mapped": [
                {"intent_description": "Summarizing notes", "success_score": 85, "trade_off": "Can miss nuance"}
            ]
        },
        {
            "tool_name": "Canva Magic Studio",
            "job_to_be_done": ["Graphic Design", "Presentations"],
            "limitations": ["Less profound control than Photoshop", "Template reliant"],
            "privacy_policy": "User opt-in for training",
            "social_proof": "Made design accessible to fully everyone.",
            "executive_summary": "The easiest all-in-one AI design suite. Lacks professional-grade manual control.",
            "pros": ["Massive template library", "Magic Eraser", "One-click resize"],
            "cons": ["Repetitive styles", "Sometimes cheesy output"],
            "use_cases": ["Social Media posts", "Pitch decks", "Flyers"],
            "metrics": {"accuracy": 4, "speed": 5, "value": 5, "ease_of_use": 5, "learning_curve": "קל מאוד", "pricing": "Freemium", "integration": "Web / App"},
            "intents_mapped": [
                {"intent_description": "Removing backgrounds", "success_score": 95, "trade_off": "Struggles with messy hair"}
            ]
        },
        {
            "tool_name": "Synthesia",
            "job_to_be_done": ["Avatar Video", "Presentations"],
            "limitations": ["Avatars can look stiff", "Limited emotion"],
            "privacy_policy": "Strict consent rules for custom avatars",
            "social_proof": "Saved thousands on video production.",
            "executive_summary": "Professional AI presenter videos. Loses authenticity compared to real humans.",
            "pros": ["Multi-language support", "Enterprise security", "Easy to update"],
            "cons": ["Uncanny valley effect", "Requires subscription"],
            "use_cases": ["Training videos", "Corporate comms", "Sales outreach"],
            "metrics": {"accuracy": 4, "speed": 4, "value": 4, "ease_of_use": 5, "learning_curve": "קל מאוד", "pricing": "תשלום חודשי", "integration": "Web"},
            "intents_mapped": [
                {"intent_description": "Creating training videos", "success_score": 90, "trade_off": "Lacks human warmth"}
            ]
        }
    ]

    for result in mock_data:
        tool_name = result.get("tool_name", "Unknown")
        
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
        
        intents_mapped = []
        for item in result.get("intents_mapped", []):
            intents_mapped.append(IntentMapping(
                intent_description=item.get("intent_description", ""),
                success_score=item.get("success_score", 0),
                trade_off=item.get("trade_off")
            ))

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
            source_findings_id="mock_data_crawler"
        )
        
        if intents_mapped:
            trust_score = sum(i.success_score for i in intents_mapped) / len(intents_mapped)
        else:
            trust_score = 70.0
            
        audit = AuditLog(
            tool_name=tool_name,
            action="Mock Ingestion",
            reason="Rate limit fallback",
            new_trust_score=trust_score
        )
        
        vault.save_tool(
            tool_name=tool_name,
            analysis=analysis,
            trust_score=trust_score,
            gallery=[],
            audit_log=audit
        )
        print(f"Successfully injected: {tool_name}")
            
    print("--- Injection Complete ---")

if __name__ == "__main__":
    asyncio.run(inject_mocks())
