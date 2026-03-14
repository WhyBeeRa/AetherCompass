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
            learning_curve="קל מאוד",
            pricing="Freemium (קרדיטים)",
            integration="ייצוא ל-PDF / Web",
            latency_label="5-10s",
            cost_label="Free tier / $15 mo",
            privacy_grade="B+"
        ),
        visual_quality=VisualQuality.HIGH,
        job_to_be_done=["מצגות", "בניית מצגות משקיעים"],
        intents_mapped=[
            IntentMapping(intent_description="בניית מצגת משקיעים מתוך טקסט", success_score=98.5, trade_off="העיצוב גנרי מעט"),
            IntentMapping(intent_description="סיכום פגישה ויזואלי", success_score=95.0, trade_off=None),
            IntentMapping(intent_description="הכנת מערך שיעור אינטראקטיבי", success_score=88.0, trade_off="קשה לשלוט בפריסות מורכבות")
        ],
        executive_summary="התאמה מושלמת לכוונת המשתמש: מייצר מצגות משקיעים מטקסט בתוך שניות עם עיצוב מובנה. מיועד למי שרוצה לדלג על עיצוב ידני ולהתמקד בתוכן.",
        pros=["מהירות: יצירת דראפט ראשוני בשניות", "עיצוב טבעי: פלטפורמה הדואגת לחוויה ויזואלית מצוינת"],
        cons=["התאמה אישית: קשה לעצב פיקסל-פרפקט פריטים מסוימים", "תבניות מוגבלות: יכול לחזור על עצמו למשתמשים מתקדמים"],
        use_cases=["מצגות משקיעים (Pitch Decks)", "הדרכות מוצר", "סיכומי פגישות ויזואליים"],
        measurement_proofs=[
            MeasurementProof(
                scenario="בניית מצגת למותג קפה אורגני",
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
            style_tags=["מצגת", "Data Visualization"],
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
            learning_curve="מיועד למפתחים",
            pricing="תשלום חודשי ($20)",
            integration="VS Code / GitHub Projects",
            latency_label="Instant (Streaming)",
            cost_label="$0.02 / task",
            privacy_grade="Enterprise Ready"
        ),
        visual_quality=VisualQuality.HIGH,
        job_to_be_done=["פיתוח קוד", "כתיבת אפליקציות"],
        intents_mapped=[
            IntentMapping(intent_description="בניית אפליקציה מבוססת React ו-Tailwind", success_score=99.0, trade_off=None),
            IntentMapping(intent_description="כתיבת דף נחיתה מקוד ללא ניסיון קודם", success_score=75.0, trade_off="עדיין דורש הבנה טכנית בסיסית של הפקודות"),
            IntentMapping(intent_description="דיבוג שגיאות עמוקות בשרת (Backend)", success_score=92.5, trade_off="תלוי בגישה פתוחה לקבצים")
        ],
        executive_summary="הכלי שכבש את קהילת המפתחים. עורך קוד מבוסס בינה מלאכותית מלאה, שנבנה על התשתית של VS Code אבל מבין את התיקייה כולה.",
        pros=["הקשר רחב: מבין את כל מאגר הקוד (Codebase)", "חוויה חלקה: UI טבעי בתוך סביבת עבודה מוכרת"],
        cons=["קהל יעד: לא מתאים להדיוטות / No-code", "פרטיות: רגישות לחברות שדורשות on-prem"],
        use_cases=["פיתוח Full Stack", "דיבוג באגים (Debugging)", "תיעוד אלקטרוני ושיפור מאגרי קוד"],
        measurement_proofs=[
            MeasurementProof(
                scenario="כתיבת שירות API ב-FastAPI",
                prompt="Write a complete FastAPI endpoint that handles user registration with Pydantic validation and password hashing using passlib.",
                output="[Code generated: import FastAPI, User model with EmailStr, registration endpoint with @app.post, bcrypt hashing implementation. Zero syntax errors.]",
                metrics_captured={"latency": "1.2s", "hallucination_detected": "Zero", "compilation": "Success"}
            ),
            MeasurementProof(
                scenario="תיקון באג ב-React useEffect",
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
            learning_curve="קשה",
            pricing="תשלום חודשי ($10-$30)",
            integration="Discord / Web Alpha",
            latency_label="~60s",
            cost_label="$0.05 / GPU hr",
            privacy_grade="Public / Stealth mode"
        ),
        visual_quality=VisualQuality.HIGH,
        job_to_be_done=["יצירת תמונות", "אמנות AI", "עיצוב ויזואלי"],
        intents_mapped=[
            IntentMapping(intent_description="יצירת תמונות מציאותיות וריאליסטיות", success_score=98.0, trade_off="דורש שליטה בפרמטרים של מצלמה"),
            IntentMapping(intent_description="המרת טקסט ללוגו (Typography)", success_score=50.0, trade_off="מתקשה המון עם טקסטים עקביים"),
            IntentMapping(intent_description="קונספט ארט לפיתוח משחק", success_score=99.5, trade_off=None)
        ],
        executive_summary="פלטפורמת יצירת התמונות המתקדמת בעולם מבחינה אמנותית. מניבה אסתטיקה ברמת אולפן אבל מצריכה שליטה בפרמטרים והבנה כיצד לכתוב רצפט מדויק.",
        pros=["איכות צילום: הפלטפורמה המובילה לפוטו-ריאליזם", "סגנון אמנותי: מגוון אדיר של השפעות מציירים, במאים ורזולוציות"],
        cons=["ממשק: דורש שימוש בדיסקורד או באתר אלפא לחלק מהמשתמשים", "עקומת למידה: שימוש בפרמטרים מורכבים (--v 6.0, --ar)"],
        use_cases=["קונספט ארט לסדרות ומשחקים", "צילום מוצר לחנויות E-commerce", "תמונות אווירה לשיווק בלוגים"],
        measurement_proofs=[
            MeasurementProof(
                scenario="צילום אופנה עתידני",
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
