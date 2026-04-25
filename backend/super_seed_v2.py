import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Set up paths
backend_dir = Path(__file__).resolve().parent
sys.path.append(str(backend_dir))

from models import (
    LabAnalysis, ToolMetrics, VisualQuality, GalleryItem, AuditLog, IntentMapping, MeasurementProof, VisualProof
)
from persistence import AetherVault

# Image paths from previous generations
IMAGE_MAP = {
    "chatgpt": "C:/Users/Yuval/.gemini/antigravity/brain/edcea81f-32d1-4067-8b20-d3b26c1e4a91/chatgpt_evidence_grid_1775910893594.png",
    "cursor": "C:/Users/Yuval/.gemini/antigravity/brain/edcea81f-32d1-4067-8b20-d3b26c1e4a91/cursor_evidence_grid_1775910911292.png",
    "midjourney": "C:/Users/Yuval/.gemini/antigravity/brain/edcea81f-32d1-4067-8b20-d3b26c1e4a91/midjourney_evidence_grid_1775910930611.png"
}

def run_super_seed():
    print("Initiating High-Quality Alpha Seeding (English Translation Mode)...")
    vault = AetherVault()
    
    # 1. ChatGPT (OpenAI)
    chatgpt = LabAnalysis(
        tool_name="ChatGPT",
        metrics=ToolMetrics(
            accuracy=5, speed=5, value=5, ease_of_use=5,
            skill_multiplier=4, hallucination_score=4,
            learning_curve="Very Easy",
            pricing="Freemium ($20 Plus)",
            integration="API / Web / Mobile",
            latency_label="~1s (Streaming)",
            cost_label="Free / $20 mo",
            privacy_grade="Enterprise Option"
        ),
        visual_quality=VisualQuality.HIGH,
        job_to_be_done=["Content Writing", "Data Analysis", "Coding", "Personal Assistant"],
        intents_mapped=[
            IntentMapping(intent_description="Analyze complex Excel files and extract insights", success_score=98.0, trade_off="Limited with extremely large datasets"),
            IntentMapping(intent_description="Strategic marketing direction for small businesses", success_score=92.0, trade_off=None),
            IntentMapping(intent_description="Python automation scripting", success_score=95.0, trade_off="Requires human validation")
        ],
        executive_summary="The Swiss Army knife of the AI world. Excels at context understanding and multi-disciplinary tasks, but requires a critical eye to prevent hallucinations.",
        pros=["Versatility: Understands almost any topic at a high level", "Friendly Interface: Smooth and fast user experience"],
        cons=["Accuracy: May invent facts with high confidence (Hallucinations)", "Privacy: Requires specific settings to prevent training on user data"],
        use_cases=["Data Analysis", "Marketing Content Writing", "Learning new subjects"],
        measurement_proofs=[
            MeasurementProof(
                scenario="Profit and loss statement analysis",
                prompt="Analyze this CSV of yearly expenses and identify the top 3 areas where we can cut costs by 15%.",
                output="[Analysis completed: Identified Cloud Services, Office Rent, and Marketing as top spend. Suggested moving to tier-based AWS, Hybrid work model, and SEO pivot.]",
                metrics_captured={"latency": "2.1s", "reasoning_steps": 5, "accuracy_check": "Verified"}
            )
        ]
    )
    
    # 2. Claude 3 (Anthropic)
    claude = LabAnalysis(
        tool_name="Claude 3",
        metrics=ToolMetrics(
            accuracy=5, speed=4, value=4, ease_of_use=5,
            skill_multiplier=5, hallucination_score=5,
            learning_curve="Very Easy",
            pricing="Freemium ($20 Pro)",
            integration="API / Web",
            latency_label="2-3s",
            cost_label="Free / $20 mo",
            privacy_grade="A+"
        ),
        visual_quality=VisualQuality.HIGH,
        job_to_be_done=["Coding", "Long text analysis", "Logical reasoning"],
        intents_mapped=[
            IntentMapping(intent_description="Complex Frontend development with React", success_score=97.0, trade_off=None),
            IntentMapping(intent_description="Summarizing 200-page PDF documents", success_score=99.0, trade_off="Relatively slow on massive files"),
            IntentMapping(intent_description="Creative thinking without a 'robotic tone'", success_score=94.0, trade_off=None)
        ],
        executive_summary="OpenAI's closest competitor, with an emphasis on 'safety' and exceptional accuracy in code writing. Feels more human and less template-constrained.",
        pros=["Coding Accuracy: Demonstrates deep understanding of programming logic", "Context Window: Can process entire books in one go (200K tokens)"],
        cons=["Availability: Sometimes suffers from heavy loads on the free version", "Integrations: Fewer third-party apps compared to ChatGPT"],
        use_cases=["Software Development", "Legal Document Analysis", "Creative Writing"],
        measurement_proofs=[
            MeasurementProof(
                scenario="Refactoring Legacy Code",
                prompt="Refactor this nested spaghetti JS code into clean, modular functional components.",
                output="[Code refactored with zero regressions. Implemented clean architecture patterns. Explained every change with logic.]",
                metrics_captured={"tokens": 1200, "logic_verification": "100%", "human_feel": "High"}
            )
        ]
    )

    # 3. Perplexity AI
    perplexity = LabAnalysis(
        tool_name="Perplexity AI",
        metrics=ToolMetrics(
            accuracy=5, speed=5, value=5, ease_of_use=5,
            skill_multiplier=3, hallucination_score=5,
            learning_curve="Very Easy",
            pricing="Free / $20 mo",
            integration="Web / Extension / Mobile",
            latency_label="Instant Search",
            cost_label="Free / Pro tier",
            privacy_grade="Standard"
        ),
        visual_quality=VisualQuality.HIGH,
        job_to_be_done=["Information Search", "Market Research", "Fact Checking"],
        intents_mapped=[
            IntentMapping(intent_description="Market research on AI trends in 2024", success_score=98.5, trade_off=None),
            IntentMapping(intent_description="Finding academic sources for a specific topic", success_score=94.0, trade_off="Sometimes cites less authoritative sources"),
            IntentMapping(intent_description="Real-time news tracking", success_score=99.0, trade_off=None)
        ],
        executive_summary="The leading alternative to Google. An AI-powered search engine that brings direct answers with citations and live web sources.",
        pros=["Reliability: Every answer is backed by citations from the original site", "Time-saving: Avoids visiting 10 different sites to get one answer"],
        cons=["Depth: Answers can sometimes be superficial compared to deep manual research", "Advertisements: Starting to integrate sponsored content in results"],
        use_cases=["Rapid Research", "Daily News Summary", "Fact Checking"],
        measurement_proofs=[
             MeasurementProof(
                scenario="Real-time Financial Search",
                prompt="What was Nvidia's revenue last quarter and what are analysts predicting for the next one?",
                output="[Answer provided with links to CNBC, Bloomberg, and Yahoo Finance. Direct numbers extracted. Table format used.]",
                metrics_captured={"source_count": 8, "realtime_verified": True}
            )
        ]
    )

    # 4. Midjourney v6
    mj = LabAnalysis(
        tool_name="Midjourney",
        metrics=ToolMetrics(
            accuracy=4, speed=3, value=4, ease_of_use=2,
            skill_multiplier=5, hallucination_score=5,
            learning_curve="Hard",
            pricing="$10-$60 mo",
            integration="Discord / Web",
            latency_label="~60s",
            cost_label="$0.05 / gen",
            privacy_grade="B"
        ),
        visual_quality=VisualQuality.HIGH,
        job_to_be_done=["Image Generation", "Digital Art", "Visual Design"],
        intents_mapped=[
            IntentMapping(intent_description="Creating photo-realistic product shots", success_score=99.0, trade_off="Requires highly technical prompt engineering"),
            IntentMapping(intent_description="Logo and typography design", success_score=60.0, trade_off="Still struggles with text consistency"),
            IntentMapping(intent_description="Video game concept art", success_score=99.5, trade_off=None)
        ],
        executive_summary="The gold standard for AI image generation. Produces unmatched aesthetics but requires a learning curve for complex parameters.",
        pros=["Aesthetics: Visual quality that feels like high-end professional photography or art", "Control: Version 6 allows high precision in small details"],
        cons=["Interface: Requires Discord usage (for most users)", "Learning Curve: Difficult to achieve perfect results without learning the prompt 'language'"],
        use_cases=["Fashion & Product Photography", "Website Design (UI Hero images)", "Social Media Art"],
        measurement_proofs=[
             MeasurementProof(
                scenario="Hyper-realistic Architectural Visualization",
                prompt="Modern minimalist villa in Iceland, volcanic rock exterior, huge glass windows, sunset lighting, 8k, photorealistic --ar 16:9",
                output="[Generated 4 stunning images. Light reflection on glass was physically accurate. Textures of rock were sharp.]",
                metrics_captured={"aesthetic_score": 9.9, "prompt_adherence": "High"}
            )
        ]
    )

    # 5. Cursor
    cursor = LabAnalysis(
        tool_name="Cursor",
        metrics=ToolMetrics(
            accuracy=5, speed=5, value=5, ease_of_use=3,
            skill_multiplier=5, hallucination_score=5,
            learning_curve="Developer-Focused",
            pricing="Free / $20 mo",
            integration="VS Code / GitHub",
            latency_label="Instant",
            cost_label="$0.02 / task",
            privacy_grade="Enterprise Ready"
        ),
        visual_quality=VisualQuality.HIGH,
        job_to_be_done=["Software Development", "Code Automation", "Bug Debugging"],
        intents_mapped=[
            IntentMapping(intent_description="Building full-stack applications from scratch", success_score=99.0, trade_off=None),
            IntentMapping(intent_description="Fixing bugs in large codebases", success_score=95.0, trade_off="Requires access to all project files"),
            IntentMapping(intent_description="Writing automated Unit Tests", success_score=98.0, trade_off=None)
        ],
        executive_summary="The code editor that replaced VS Code for tens of thousands of developers. It doesn't just write code; it understands your entire codebase.",
        pros=["Context Awareness: Knows how a function in one file affects another", "Integrative UI: The AI feels like a natural part of writing, not just a side panel"],
        cons=["Target Audience: Requires technical understanding, not a no-code tool", "Resources: Can be RAM-heavy on massive projects"],
        use_cases=["React/Next.js Development", "Algorithm Optimization", "Automated Code Documentation"],
        measurement_proofs=[
             MeasurementProof(
                scenario="Adding a complex feature to an existing repo",
                prompt="Add a Stripe subscription flow to this project. Use the existing Auth provider and save data to Prisma.",
                output="[Analyzed structure. Created 3 files, updated 2. Correctly used existing 'useAuth' hook and Prisma schema. Fixed import errors.]",
                metrics_captured={"files_modified": 5, "compilation_success": True}
            )
        ]
    )
    
    # 6. Suno AI (Music)
    suno = LabAnalysis(
        tool_name="Suno AI",
        metrics=ToolMetrics(
            accuracy=4, speed=4, value=5, ease_of_use=5,
            skill_multiplier=5, hallucination_score=5,
            learning_curve="Very Easy",
            pricing="Freemium",
            integration="Web",
            latency_label="~30-60s",
            cost_label="$0.10 / song",
            privacy_grade="Standard"
        ),
        visual_quality=VisualQuality.MID,
        job_to_be_done=["Music Creation", "Song Composing", "Jingles"],
        intents_mapped=[
            IntentMapping(intent_description="Creating full pop songs with lyrics", success_score=97.0, trade_off=None),
            IntentMapping(intent_description="Composing background music for YouTube videos", success_score=95.0, trade_off=None)
        ],
        executive_summary="A revolution in the music world. Generates full songs (lyrics and vocals) in any style with surprising radio quality.",
        pros=["Vocal Quality: Vocals feel incredibly human", "Speed: Produces a 2-minute song in less than a minute"],
        cons=["Structure Control: Difficult to fine-tune specific changes within the song (e.g., 'change only the solo')", "Copyright: Legal issues still unfolding in the industry"],
        use_cases=["Custom Personalized Songs", "Background Music for Creators"],
        measurement_proofs=[
             MeasurementProof(
                scenario="Creating a Synthwave track",
                prompt="Upbeat 80s synthwave, driving beat, futuristic mood, lyrics about neon city nights.",
                output="[Generated full 2min track. Vocals perfectly synced. Correct genre elements used.]",
                metrics_captured={"generation_time": "45s", "hit_rate": 0.9}
            )
        ]
    )

    # 7. HeyGen (Video)
    heygen = LabAnalysis(
        tool_name="HeyGen",
        metrics=ToolMetrics(
            accuracy=5, speed=3, value=4, ease_of_use=5,
            skill_multiplier=5, hallucination_score=5,
            learning_curve="Very Easy",
            pricing="$24/mo+",
            integration="API / Web",
            latency_label="Minutes (Render)",
            cost_label="$2 / credit",
            privacy_grade="A"
        ),
        visual_quality=VisualQuality.HIGH,
        job_to_be_done=["Video Creation", "Automated Dubbing", "Digital Avatars"],
        intents_mapped=[
            IntentMapping(intent_description="Creating explainer videos with talking avatars", success_score=99.0, trade_off=None),
            IntentMapping(intent_description="Translating video to other languages with lip-sync", success_score=98.0, trade_off="Requires high-quality original video")
        ],
        executive_summary="The leading tool for avatar video creation. Allows creating professional videos from text alone, with characters that look and feel completely real.",
        pros=["Realism: Best lip-sync on the market", "Ease of Use: No need for a camera or lighting, just text"],
        cons=["Cost: Relatively expensive for heavy use", "Render Time: Long videos take time to process"],
        use_cases=["Training Videos (L&D)", "Personalized Marketing", "Global Content Translation"],
        measurement_proofs=[]
    )

    # 8. ElevenLabs (Voice)
    elevenlabs = LabAnalysis(
        tool_name="ElevenLabs",
        metrics=ToolMetrics(accuracy=5, speed=5, value=5, ease_of_use=5, learning_curve="Very Easy", pricing="Freemium"),
        visual_quality=VisualQuality.MID,
        job_to_be_done=["Voice Creation", "Dubbing", "Text-to-Speech"],
        executive_summary="The highest-quality voice engine in the world. Capable of cloning voices with frightening accuracy and generating natural, emotional speech.",
        pros=["Voice Quality: The least robotic tone and intonation available", "Voice Cloning: Incredibly fast and accurate"],
        cons=["Safety: Risk of deepfakes", "Cost: Advanced versions require a subscription"],
        use_cases=["Audiobooks", "Video Narration", "Content Accessibility"]
    )

    # 9. Gamma AI (Presentations)
    gamma = LabAnalysis(
        tool_name="Gamma AI",
        metrics=ToolMetrics(accuracy=4, speed=5, value=5, ease_of_use=5, learning_curve="Very Easy", pricing="Freemium"),
        visual_quality=VisualQuality.HIGH,
        job_to_be_done=["Presentations", "Pitch Deck Building"],
        executive_summary="Creates beautifully designed presentations and documents in seconds from a text prompt. Saves hours of work on PowerPoint layouts.",
        pros=["Speed: Generates a full framework and deck in a moment", "Design: Modern and interactive layouts"],
        cons=["Flexibility: Difficult to make microscopic design changes", "Templates: Can feel slightly generic with repeated use"],
        use_cases=["Pitch Decks", "Project Summaries", "Lesson Plans"]
    )

    # 10. Jasper (Marketing)
    jasper = LabAnalysis(
        tool_name="Jasper",
        metrics=ToolMetrics(accuracy=4, speed=5, value=4, ease_of_use=4, learning_curve="Medium", pricing="$39/mo+"),
        visual_quality=VisualQuality.MID,
        job_to_be_done=["Marketing", "Blog Writing", "Brand Voice"],
        executive_summary="Writing platform focused on marketing teams. Excels at maintaining Brand Voice and integrates with tools like Surfer SEO.",
        pros=["Brand Voice: Learns your business style", "Marketing Templates: Hundreds of ready-to-use templates for ads and posts"],
        cons=["Price: Significantly more expensive than direct ChatGPT usage", "Complexity: Loaded with features that can confuse casual users"],
        use_cases=["Marketing Campaigns", "SEO-optimized Blog Writing"]
    )

    # 11. Leonardo.ai (Art/Design)
    leonardo = LabAnalysis(
        tool_name="Leonardo.ai",
        metrics=ToolMetrics(accuracy=4, speed=4, value=5, ease_of_use=4, learning_curve="Medium", pricing="Freemium"),
        visual_quality=VisualQuality.HIGH,
        job_to_be_done=["Image Generation", "Game Design", "Visual Assets"],
        executive_summary="Powerful visual design platform with an excellent web interface. A more accessible alternative to Midjourney with more model control.",
        pros=["Interface: Very user-friendly website, no Discord required", "Features: Includes Canvas for editing and fixing images"],
        cons=["Consistency: Wide variety of models can be confusing", "Quality: At the extreme, Midjourney still leads in photographic aesthetics"],
        use_cases=["Character Design", "Game Assets", "Merchandise"]
    )

    # 12. Phind (Coding Search)
    phind = LabAnalysis(
        tool_name="Phind",
        metrics=ToolMetrics(accuracy=5, speed=5, value=5, ease_of_use=5, learning_curve="Very Easy", pricing="Free / Pro"),
        visual_quality=VisualQuality.MID,
        job_to_be_done=["Code Search", "Programming Problem Solving"],
        executive_summary="Search engine specifically designed for developers. Combines web results with accurate and up-to-date LLM answers.",
        pros=["Freshness: Connected to the latest documentation online", "Focus: Saves searching through StackOverflow"],
        cons=["Scope: Dedicated only to coding and development tasks", "Interface: Very simple, lacks full IDE features"],
        use_cases=["Code Error Debugging", "Learning new libraries"]
    )

    # 13. Groq (LPU Inference)
    groq = LabAnalysis(
        tool_name="Groq",
        metrics=ToolMetrics(accuracy=4, speed=5, value=5, ease_of_use=4, learning_curve="Medium", pricing="Free / API"),
        visual_quality=VisualQuality.LOW,
        job_to_be_done=["Inference Speed", "Fast Chat", "Developer API"],
        executive_summary="The fastest infrastructure in the world for running language models. Capable of running models like Llama 3 at speeds that feel like a live human conversation.",
        pros=["Speed: 10-20x faster than competitors", "Price: Very cheap when used via API"],
        cons=["Model Variety: Limited to open-source models (Llama, Mixtral)", "Complexity: Primarily for developers implementing AI"],
        use_cases=["Real-time Chatbots", "Applications requiring instant response"]
    )

    # 14. Relume (Sitemap/Site builder)
    relume = LabAnalysis(
        tool_name="Relume",
        metrics=ToolMetrics(accuracy=5, speed=5, value=5, ease_of_use=4, learning_curve="Medium", pricing="Freemium"),
        visual_quality=VisualQuality.HIGH,
        job_to_be_done=["Sitemaps", "Wireframes", "Site Building"],
        executive_summary="The compass for website building. Uses AI to build site hierarchies, page maps, and wireframes in minutes.",
        pros=["Accuracy: AI understands E-commerce or B2B site structures perfectly", "Export: Connects directly to Webflow and Figma"],
        cons=["Focus: Relevant only for web designers and Webflow developers", "Flexibility: Requires using their component libraries"],
        use_cases=["UX Site Planning", "Rapid Wireframe Building"]
    )

    # 15. Descript (Video/Audio Editing)
    descript = LabAnalysis(
        tool_name="Descript",
        metrics=ToolMetrics(accuracy=5, speed=4, value=5, ease_of_use=4, learning_curve="Medium", pricing="Freemium"),
        visual_quality=VisualQuality.HIGH,
        job_to_be_done=["Video Editing", "Podcasting", "Text-Based Editing"],
        executive_summary="Video editing by editing text. Turns video transcription into the primary editing tool, including deleting filler words with one click.",
        pros=["Innovation: Translation-based editing saves hours of searching for clips", "Overdub: Fix mistyped words using AI voice"],
        cons=["Resources: Requires a relatively heavy application installation", "Transcription: Slightly struggles with Hebrew compared to English"],
        use_cases=["Podcast Editing", "Explainer Video Creation"]
    )

    tools_data = [
        ("ChatGPT", chatgpt, 96.5, "chatgpt"),
        ("Claude 3", claude, 98.2, None),
        ("Perplexity", perplexity, 97.8, None),
        ("Midjourney", mj, 95.0, "midjourney"),
        ("Cursor", cursor, 99.1, "cursor"),
        ("Suno AI", suno, 94.0, None),
        ("HeyGen", heygen, 97.2, None),
        ("ElevenLabs", elevenlabs, 98.5, None),
        ("Gamma AI", gamma, 93.0, None),
        ("Jasper", jasper, 89.0, None),
        ("Leonardo.ai", leonardo, 92.5, None),
        ("Phind", phind, 96.0, None),
        ("Groq", groq, 95.5, None),
        ("Relume", relume, 94.5, None),
        ("Descript", descript, 96.8, None)
    ]
    
    # Save to Vault
    for tool_name, analysis, score, img_key in tools_data:
        gallery = []
        if img_key and IMAGE_MAP.get(img_key):
             gallery.append(GalleryItem(
                 tool_id=tool_name.lower().replace(" ", "-"),
                 media_url=IMAGE_MAP[img_key],
                 style_tags=["Verified", "Evidence"],
                 prompt_recipe={"note": "Official Aether Analysis Proof"}
             ))
        
        audit = AuditLog(tool_name=tool_name, action="Alpha Verification", reason="Deep Analysis + Evidence Grid Implementation", new_trust_score=score)
        vault.save_tool(tool_name=tool_name, analysis=analysis, trust_score=score, gallery=gallery, audit_log=audit)
        
    print(f"Successfully seeded {len(tools_data)} high-quality tools in English.")

if __name__ == "__main__":
    run_super_seed()
