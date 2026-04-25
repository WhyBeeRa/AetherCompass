import os
import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime

# Add backend directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent))

from models import (
    LabAnalysis, ToolMetrics, VisualQuality, GalleryItem, AuditLog, IntentMapping, MeasurementProof
)
from persistence import AetherVault

def clear_database():
    print("Purging existing data to ensure 100% English environment...")
    db_path = Path(__file__).resolve().parent / "vault.db"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("DELETE FROM verified_tools")
    c.execute("DELETE FROM search_index")
    c.execute("DELETE FROM audit_history")
    conn.commit()
    conn.close()

def run_seed():
    clear_database()
    print("Initiating Global English Seeding...")
    vault = AetherVault()
    
    tools_data = [
        {
            "name": "ChatGPT",
            "metrics": ToolMetrics(
                accuracy=5, speed=5, value=5, ease_of_use=5, skill_multiplier=4, hallucination_score=4,
                learning_curve="Very Easy", pricing="Freemium ($20 Plus)", integration="API / Web / Mobile",
                latency_label="~1s", cost_label="Free / $20 mo", privacy_grade="Enterprise Option"
            ),
            "visual_quality": VisualQuality.MID,
            "jobs": ["Text Generation", "Productivity", "Analysis"],
            "intents": [
                IntentMapping(intent_description="Writing professional emails", success_score=98.0, trade_off=None),
                IntentMapping(intent_description="Analyzing complex spreadsheets", success_score=92.0, trade_off="Requires clear headers")
            ],
            "summary": "The gold standard for conversational AI. Versatile, fast, and highly capable across writing, coding, and reasoning tasks.",
            "pros": ["Versatility: Handles almost any text-based task", "Speed: Instant responses with GPT-4o"],
            "cons": ["Accuracy: Can still hallucinate facts", "Privacy: Free tier trains on user data"],
            "cases": ["Content Creation", "Data Analysis", "Coding Help"],
            "score": 98.0
        },
        {
            "name": "Claude 3.5 Sonnet",
            "metrics": ToolMetrics(
                accuracy=5, speed=4, value=5, ease_of_use=5, skill_multiplier=5, hallucination_score=5,
                learning_curve="Very Easy", pricing="Freemium ($20 Pro)", integration="API / Web",
                latency_label="~2s", cost_label="Free / $20 mo", privacy_grade="Strong Privacy"
            ),
            "visual_quality": VisualQuality.HIGH,
            "jobs": ["Coding", "Nuanced Writing", "Logic"],
            "intents": [
                IntentMapping(intent_description="Complex software refactoring", success_score=99.0, trade_off=None),
                IntentMapping(intent_description="Creative writing with specific tone", success_score=96.0, trade_off=None)
            ],
            "summary": "Highly intelligent model with a focus on natural language and advanced coding. Often preferred for its 'human-like' writing style.",
            "pros": ["Intelligence: Superior reasoning and coding", "Artifacts: Live preview for code and docs"],
            "cons": ["Rate Limits: Pro tier has strict message caps", "Speed: Slightly slower than GPT-4o"],
            "cases": ["App Development", "Technical Writing", "Strategic Planning"],
            "score": 97.5
        },
        {
            "name": "Midjourney",
            "metrics": ToolMetrics(
                accuracy=4, speed=3, value=4, ease_of_use=2, skill_multiplier=4, hallucination_score=5,
                learning_curve="Hard", pricing="Paid ($10-$120)", integration="Discord / Web",
                latency_label="~60s", cost_label="$0.05 / image", privacy_grade="Public by default"
            ),
            "visual_quality": VisualQuality.HIGH,
            "jobs": ["Image Generation", "Art", "Design"],
            "intents": [
                IntentMapping(intent_description="Photorealistic product photography", success_score=98.0, trade_off="Hard to control text"),
                IntentMapping(intent_description="Concept art for movies", success_score=99.0, trade_off=None)
            ],
            "summary": "The industry leader in artistic AI image generation. Produces studio-quality visuals but requires Discord for the full experience.",
            "pros": ["Quality: Unmatched aesthetic and detail", "Community: Access to millions of public prompts"],
            "cons": ["UX: Discord interface can be confusing", "Control: Difficult to get exact text/layout"],
            "cases": ["Advertising", "Concept Art", "Web Design Assets"],
            "score": 96.0
        },
        {
            "name": "Cursor",
            "metrics": ToolMetrics(
                accuracy=5, speed=5, value=5, ease_of_use=3, skill_multiplier=5, hallucination_score=5,
                learning_curve="For Developers", pricing="Freemium ($20 Pro)", integration="VS Code",
                latency_label="Instant", cost_label="$0.02 / task", privacy_grade="Enterprise Ready"
            ),
            "visual_quality": VisualQuality.HIGH,
            "jobs": ["Software Development", "Debugging"],
            "intents": [
                IntentMapping(intent_description="Building a full-stack app from scratch", success_score=95.0, trade_off=None),
                IntentMapping(intent_description="Fixing bugs in large codebases", success_score=98.0, trade_off=None)
            ],
            "summary": "An AI-native code editor that understands your entire project. The best tool for modern software engineers.",
            "pros": ["Context: Understands all your files", "Integration: Built directly into the editor"],
            "cons": ["Audience: Not for non-coders", "Cost: Requires subscription for best models"],
            "cases": ["Web Dev", "Systems Engineering", "Rapid Prototyping"],
            "score": 98.5
        },
        {
            "name": "Perplexity",
            "metrics": ToolMetrics(
                accuracy=5, speed=5, value=5, ease_of_use=5, skill_multiplier=4, hallucination_score=5,
                learning_curve="Very Easy", pricing="Freemium ($20 Pro)", integration="Web / Mobile / API",
                latency_label="~2s", cost_label="Free", privacy_grade="Standard"
            ),
            "visual_quality": VisualQuality.MID,
            "jobs": ["Search", "Research", "Fact Checking"],
            "intents": [
                IntentMapping(intent_description="Real-time news research", success_score=99.0, trade_off=None),
                IntentMapping(intent_description="Finding specific academic citations", success_score=94.0, trade_off=None)
            ],
            "summary": "An AI search engine that provides cited answers to any question. Replaces traditional search with direct, verified information.",
            "pros": ["Citations: Every claim is linked to a source", "Speed: Faster than manual googling"],
            "cons": ["Depth: Sometimes misses very niche results", "UI: Can get cluttered with many sources"],
            "cases": ["Market Research", "Academic Study", "Daily News"],
            "score": 97.0
        },
        {
            "name": "Gamma AI",
            "metrics": ToolMetrics(
                accuracy=4, speed=5, value=5, ease_of_use=5, skill_multiplier=5, hallucination_score=4,
                learning_curve="Very Easy", pricing="Freemium", integration="Web / Export",
                latency_label="~10s", cost_label="Credits", privacy_grade="Standard"
            ),
            "visual_quality": VisualQuality.HIGH,
            "jobs": ["Presentations", "Webpages", "Docs"],
            "intents": [
                IntentMapping(intent_description="Creating a pitch deck from a PDF", success_score=96.0, trade_off=None),
                IntentMapping(intent_description="Building a landing page in minutes", success_score=90.0, trade_off="Generic templates")
            ],
            "summary": "A new way to create beautiful presentations and websites. Just type a prompt and watch the design come to life.",
            "pros": ["Effortless: No design skills needed", "Modern: Sleek, responsive layouts"],
            "cons": ["Control: Hard to move specific elements", "Customization: Limited font and color options"],
            "cases": ["Sales Decks", "Portfolio Sites", "Internal Reports"],
            "score": 94.0
        }
    ]

    for tool in tools_data:
        analysis = LabAnalysis(
            tool_name=tool["name"],
            metrics=tool["metrics"],
            visual_quality=tool["visual_quality"],
            job_to_be_done=tool["jobs"],
            intents_mapped=tool["intents"],
            executive_summary=tool["summary"],
            pros=tool["pros"],
            cons=tool["cons"],
            use_cases=tool["cases"]
        )
        
        audit = AuditLog(
            tool_name=tool["name"],
            action="Verified",
            reason="Manual English Audit",
            new_trust_score=tool["score"]
        )
        
        vault.save_tool(
            tool_name=tool["name"],
            analysis=analysis,
            trust_score=tool["score"],
            gallery=[],
            audit_log=audit
        )
        
    print(f"English seeding completed. {len(tools_data)} tools secured.")

if __name__ == "__main__":
    run_seed()
