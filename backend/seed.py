import os
import sys
from pathlib import Path

# Add backend directory to sys.path so we can import from models and persistence
sys.path.append(str(Path(__file__).resolve().parent))

from models import (
    LabAnalysis, ToolMetrics, VisualQuality, GalleryItem, AuditLog, IntentMapping, MeasurementProof
)
from persistence import AetherVault

def run_seed():
    print("Initiating Default Data Seeding for Phase 4 (Intent Engine Enabled)...")
    vault = AetherVault()
    
    # Tool 1: Gamma AI
    gamma_analysis = LabAnalysis(
        tool_name="Gamma AI",
        metrics=ToolMetrics(
            accuracy=4, speed=5, value=5, ease_of_use=5,
            skill_multiplier=5, hallucination_score=4,
            learning_curve="Very Easy",
            pricing="Freemium (Credits)",
            integration="Export to PDF / Web",
            latency_label="5-10s",
            cost_label="Free tier / $15 mo",
            privacy_grade="B+"
        ),
        visual_quality=VisualQuality.HIGH,
        job_to_be_done=["Presentations", "Pitch Deck Creation"],
        intents_mapped=[
            IntentMapping(intent_description="Build a pitch deck from text", success_score=98.5, trade_off="Design is slightly generic"),
            IntentMapping(intent_description="Visual meeting summary", success_score=95.0, trade_off=None),
            IntentMapping(intent_description="Interactive lesson planning", success_score=88.0, trade_off="Hard to control complex layouts")
        ],
        executive_summary="Perfect fit for user intent: Generates pitch decks from text in seconds with built-in design. Aimed at those who want to skip manual design and focus on content.",
        pros=["Speed: Initial draft in seconds", "Natural Design: Platform ensures excellent visual experience"],
        cons=["Customization: Difficult to pixel-perfect certain items", "Limited Templates: Can be repetitive for advanced users"],
        use_cases=["Pitch Decks", "Product Training", "Visual Meeting Summaries"],
        measurement_proofs=[
            MeasurementProof(
                scenario="Building a deck for an organic coffee brand",
                prompt="Create a 10-slide deck for 'EarthBrew', a sustainable organic coffee brand focusing on direct-trade and carbon-neutral shipping.",
                output="[Generated 10 slides with professional layouts, specific sections for 'Our Mission', 'Direct Trade Impact', and financial projections. Visuals included coffee farm backgrounds.]",
                metrics_captured={"latency": "8.4s", "slides_count": 10, "design_coherence": "High"}
            )
        ]
    )
    
    gamma_gallery = [
        GalleryItem(
            tool_id="gamma-ai",
            media_url="https://images.unsplash.com/photo-1551288049-bebda4e38f71?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
            style_tags=["Presentation", "Data Visualization"],
            prompt_recipe={"prompt": "Startup pitch deck for an organic coffee brand"},
            is_featured=True,
            trust_badge_visible=True
        )
    ]
    
    # Tool 2: Cursor
    cursor_analysis = LabAnalysis(
        tool_name="Cursor",
        metrics=ToolMetrics(
            accuracy=5, speed=5, value=5, ease_of_use=3,
            skill_multiplier=5, hallucination_score=5,
            learning_curve="For Developers",
            pricing="Monthly Payment ($20)",
            integration="VS Code / GitHub Projects",
            latency_label="Instant (Streaming)",
            cost_label="$0.02 / task",
            privacy_grade="Enterprise Ready"
        ),
        visual_quality=VisualQuality.HIGH,
        job_to_be_done=["Code Development", "App Creation"],
        intents_mapped=[
            IntentMapping(intent_description="Build React & Tailwind applications", success_score=99.0, trade_off=None),
            IntentMapping(intent_description="Build landing pages without prior coding experience", success_score=75.0, trade_off="Still requires basic technical understanding of commands"),
            IntentMapping(intent_description="Advanced Backend debugging", success_score=92.5, trade_off="Depends on open file access")
        ],
        executive_summary="The tool that conquered the developer community. An AI-powered code editor built on VS Code foundation that understands the entire codebase.",
        pros=["Wide Context: Understands the entire codebase", "Seamless Experience: Native UI within a familiar workspace"],
        cons=["Target Audience: Not for non-technical/No-code users", "Privacy: Sensitive for companies requiring on-prem"],
        use_cases=["Full Stack Development", "Debugging", "Codebase improvement & documentation"],
        measurement_proofs=[
            MeasurementProof(
                scenario="Writing a FastAPI service",
                prompt="Write a complete FastAPI endpoint that handles user registration with Pydantic validation and password hashing using passlib.",
                output="[Code generated: import FastAPI, User model with EmailStr, registration endpoint with @app.post, bcrypt hashing implementation. Zero syntax errors.]",
                metrics_captured={"latency": "1.2s", "hallucination_detected": "Zero", "compilation": "Success"}
            ),
            MeasurementProof(
                scenario="Fixing a React useEffect bug",
                prompt="Find and fix the infinite loop in this component: [provided code with missing dependency array]",
                output="[Identified missing dependency array. Added [data] to dependency list. Explained why the loop was happening.]",
                metrics_captured={"latency": "0.8s", "reasoning_accuracy": "100%"}
            )
        ]
    )
    
    cursor_gallery = [
        GalleryItem(
            tool_id="cursor-ide",
            media_url="https://images.unsplash.com/photo-1542831371-29b0f74f9713?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
            style_tags=["Code", "IDE"],
            prompt_recipe={"prompt": "Generate a full React authentication flow"},
            is_featured=True,
            trust_badge_visible=True
        )
    ]
    
    # Tool 3: Midjourney
    mj_analysis = LabAnalysis(
        tool_name="Midjourney",
        metrics=ToolMetrics(
            accuracy=4, speed=3, value=4, ease_of_use=2,
            skill_multiplier=4, hallucination_score=5,
            learning_curve="Hard",
            pricing="Monthly Payment ($10-$30)",
            integration="Discord / Web Alpha",
            latency_label="~60s",
            cost_label="$0.05 / GPU hr",
            privacy_grade="Public / Stealth mode"
        ),
        visual_quality=VisualQuality.HIGH,
        job_to_be_done=["Image Generation", "AI Art", "Visual Design"],
        intents_mapped=[
            IntentMapping(intent_description="Photorealistic image generation", success_score=98.0, trade_off="Requires mastery of camera parameters"),
            IntentMapping(intent_description="Text to Logo (Typography)", success_score=50.0, trade_off="Struggles with consistent text"),
            IntentMapping(intent_description="Concept art for game development", success_score=99.5, trade_off=None)
        ],
        executive_summary="The world's most advanced artistic image generation platform. Yields studio-level aesthetics but requires parameter control and understanding of precise prompt recipes.",
        pros=["Photographic Quality: Leading platform for photorealism", "Artistic Style: Huge variety of influences from painters, directors, and resolutions"],
        cons=["Interface: Requires Discord or Alpha site for some users", "Learning Curve: Use of complex parameters (--v 6.0, --ar)"],
        use_cases=["Concept art for series and games", "Product photography for E-commerce", "Atmospheric images for blog marketing"],
        measurement_proofs=[
            MeasurementProof(
                scenario="Futuristic fashion photography",
                prompt="Cyberpunk fashion editorial, model in neon Tokyo, shot on Sony A7R IV, 85mm f/1.4, cinematic lighting --style raw --v 6.0",
                output="[Generated 4 high-resolution images. Exceptional skin texture and light scattering. Consistent cyberpunk aesthetic.]",
                metrics_captured={"generation_time": "52s", "aesthetic_score": "9.8/10", "prompt_adherence": "Extreme"}
            )
        ]
    )
    
    mj_gallery = [
        GalleryItem(
            tool_id="midjourney-v6",
            media_url="https://images.unsplash.com/photo-1681412330368-24ccdf8ded02?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
            style_tags=["Generative Art", "Fashion Photography"],
            prompt_recipe={"prompt": "Editorial fashion photography of a cybernetic model in Tokyo, shot on 35mm --ar 16:9 --style raw"},
            is_featured=True,
            trust_badge_visible=True
        )
    ]

    # Save to Vault
    for tool_name, analysis, score, gallery in [
        ("Gamma AI", gamma_analysis, 94.5, gamma_gallery),
        ("Cursor", cursor_analysis, 98.2, cursor_gallery),
        ("Midjourney", mj_analysis, 96.0, mj_gallery)
    ]:
        audit = AuditLog(tool_name=tool_name, action="Seed Verification", reason="Initial Phase 4 DB Setup", new_trust_score=score)
        vault.save_tool(tool_name=tool_name, analysis=analysis, trust_score=score, gallery=gallery, audit_log=audit)
        
    print("Database seeding successfully completed.")

if __name__ == "__main__":
    run_seed()
