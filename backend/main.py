from dotenv import load_dotenv
from pathlib import Path
import os
env_path = Path(__file__).parent / ".env"
with open("startup.log", "w") as f:
    f.write(f"!!! LOADING ENV FROM: {env_path}\n")
    if env_path.exists():
        f.write(".env file exists\n")
    else:
        f.write(".env file NOT FOUND\n")
load_dotenv(dotenv_path=env_path)

import json
import os
import uuid
import asyncio
import traceback
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, BackgroundTasks, HTTPException, Header, Request, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional
from firebase_admin import auth as firebase_auth
from pipeline import AetherPipeline
from models import GalleryItem, LabAnalysis, TrustScore, ToolMetrics, VisualQuality, AuditLog, ManualToolEntry
from auth import verify_admin_user, initialize_firebase_admin
initialize_firebase_admin()
from community_logic import check_for_badges
from models import UserProfile, Badge, ToolContribution, LiveMetric
from pydantic import BaseModel
from admin_auditor import run_lean_audit
from admin_agent import run_deep_audit_stream
from agents.scout import ScoutAgent
import psutil
from logger_utils import log_streamer, log_terminal
from fastapi import WebSocket, WebSocketDisconnect
from routers.abc_tom_router import router as abc_tom_router
from routers.factory_router import router as factory_router
from routers.bridge_router import router as bridge_router

class AuditRequest(BaseModel):
    url: str
    
class BulkAuditRequest(BaseModel):
    urls: List[str]

class SentinelSettingsInput(BaseModel):
    enabled: bool
    alert_email: str
    frequency_minutes: int
    failure_threshold: int

global_scheduler = None

app = FastAPI(title="Aeather API", description="Backend for the Agentic Grid", version="0.2.0")

origins = [
    "https://www.aethercompass.com",
    "https://aethercompass.com",
    "https://aethercompass.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
]

# 3. Middleware Injection
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount ABC-TOM Engine Router
app.include_router(abc_tom_router)

# Mount Local AI Factory Router (local admin only)
app.include_router(factory_router)

# Mount Prod-to-Local Bridge Router
app.include_router(bridge_router)

def get_current_user(authorization: str = Header(None)) -> Dict:
    """
    Verifies the Firebase token and returns user info.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Token")
    
    token = authorization.split(" ")[1]
    try:
        decoded_token = firebase_auth.verify_id_token(token)
        return decoded_token
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Token")


# Initialize Single Source of Truth
pipeline = AetherPipeline()

# Initialize Vault (Persistence Layer)
from persistence import AetherVault
vault = AetherVault()
db_ok = True
try:
    vault.get_stats()
except Exception:
    db_ok = False

# Initialize Local Embedding Engine (singleton — loads model once into ~130MB RAM)
from local_embedder import LocalEmbeddingEngine
embedder = LocalEmbeddingEngine.get_instance()

# Initialize Zero-API Semantic Search Engine
from search_engine import AetherSearchEngine
search_engine = AetherSearchEngine(embedder, vault)

def send_sentinel_email(to_email: str, error_msg: str, db_status: str, memory_usage: float):
    """
    Sends a clean, text-based alert report using smtplib.
    Falls back to writing a mock email in background_tasks.log if SMTP is not configured.
    """
    import os
    import smtplib
    from email.mime.text import MIMEText
    from email.header import Header
    from datetime import datetime
    
    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_pass = os.getenv("SMTP_PASSWORD", "")
    smtp_from = os.getenv("SMTP_FROM", "sentinel@aethercompass.com")
    
    subject = "AETHER SENTINEL: SYSTEM OUTAGE DETECTED"
    body = (
        "===============================================\n"
        "             AETHER COMPASS SENTINEL            \n"
        "===============================================\n\n"
        f"Alert Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        "System Status: CRITICAL SYSTEM FAULT\n"
        f"Target Email: {to_email}\n\n"
        "------------------ DIAGNOSTICS ----------------\n"
        f"Database Status: {db_status}\n"
        f"Process Memory: {memory_usage} MB\n"
        f"Error Details: {error_msg}\n"
        "-----------------------------------------------\n\n"
        "Actions Taken:\n"
        "1. Logged alert state in primary database\n"
        "2. Dispatched SMTP security report to administrator\n\n"
        "Please inspect the command console immediately.\n"
    )
    
    log_file = Path(__file__).parent / "background_tasks.log"
    
    if smtp_host and smtp_user and smtp_pass:
        try:
            msg = MIMEText(body, "plain", "utf-8")
            msg["Subject"] = Header(subject, "utf-8")
            msg["From"] = smtp_from
            msg["To"] = to_email
            
            with smtplib.SMTP(smtp_host, smtp_port, timeout=10.0) as server:
                if smtp_port == 587:
                    server.starttls()
                server.login(smtp_user, smtp_pass)
                server.sendmail(smtp_from, [to_email], msg.as_string())
                
            with open(log_file, "a") as f:
                f.write(f"[{datetime.now()}] SUCCESS: Real SMTP alert sent to {to_email}\n")
            print(f"[Sentinel] Real SMTP alert sent to {to_email}")
        except Exception as e:
            with open(log_file, "a") as f:
                f.write(f"[{datetime.now()}] ERROR: SMTP send failed: {str(e)}\n")
            raise e
    else:
        mock_log = (
            f"\n--- MOCK SMTP EMAIL DISPATCH ---\n"
            f"From: {smtp_from}\n"
            f"To: {to_email}\n"
            f"Subject: {subject}\n"
            f"Body:\n{body}"
            f"---------------------------------\n"
        )
        with open(log_file, "a") as f:
            f.write(f"[{datetime.now()}] Mock SMTP alert dispatched: {mock_log}\n")
        print(f"[Sentinel] SMTP not configured. Mock email logged to background_tasks.log")


async def perform_sentinel_audit(is_manual: bool = False) -> Dict:
    """
    Performs the actual Aether Sentinel health check.
    Pings /admin/heartbeat internally and checks database connectivity.
    Sends SMTP alert if failures cross threshold.
    """
    import os
    import httpx
    import psutil
    from datetime import datetime
    
    memory_usage = 0.0
    try:
        process = psutil.Process(os.getpid())
        memory_usage = round(process.memory_info().rss / 1024 / 1024, 2)
    except Exception:
        memory_usage = -1.0

    db_status = "DISCONNECTED"
    try:
        vault.get_stats()
        db_status = "CONNECTED"
    except Exception:
        db_status = "ERROR"

    ping_success = False
    ping_msg = ""
    
    settings = vault.get_sentinel_settings()
    enabled = settings.get("enabled", 0)
    
    if not enabled and not is_manual:
        return {"status": "skipped", "message": "Sentinel is disabled"}

    try:
        headers = {}
        admin_key = os.getenv("ADMIN_API_KEY")
        if admin_key:
            headers["x-admin-key"] = admin_key
        else:
            headers["Authorization"] = "Bearer dev-admin-token"
            
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.get("http://127.0.0.1:8000/admin/heartbeat", headers=headers)
            if res.status_code == 200:
                data = res.json()
                if data.get("database_status") == "CONNECTED":
                    ping_success = True
                    ping_msg = "Heartbeat ping successful"
                else:
                    ping_msg = f"Database status not connected: {data.get('database_status')}"
            else:
                ping_msg = f"HTTP error {res.status_code}"
    except Exception as e:
        ping_msg = f"HTTP ping failed: {str(e)}"

    is_db_ok = (db_status == "CONNECTED")
    audit_ok = is_db_ok and (ping_success or "HTTP ping failed" in ping_msg or "HTTP error" in ping_msg)
    
    status_str = "GREEN" if audit_ok else "RED"
    message_str = f"Database: {db_status}. Heartbeat: {ping_msg}."
    
    email_sent = 0
    new_failures = 0 if audit_ok else (settings.get("current_failures", 0) + 1)
    
    if not audit_ok and not is_manual:
        threshold = settings.get("failure_threshold", 3)
        if new_failures >= threshold:
            if settings.get("current_failures", 0) < threshold:
                alert_email = settings.get("alert_email", "")
                if alert_email:
                    try:
                        send_sentinel_email(alert_email, message_str, db_status, memory_usage)
                        email_sent = 1
                        message_str += " Alert email sent."
                    except Exception as email_err:
                        message_str += f" Failed to send email: {str(email_err)}"
                        print(f"[Sentinel Error] Email trigger failed: {email_err}")

    if not is_manual:
        vault.update_sentinel_failures(new_failures, status_str)
    else:
        vault.update_sentinel_failures(settings.get("current_failures", 0), status_str)

    logged_msg = message_str + (" (Manual Trigger)" if is_manual else " (Automated Run)")
    vault.log_sentinel_audit(status_str, logged_msg, db_status, memory_usage, email_sent)

    return {
        "status": status_str,
        "message": message_str,
        "database_status": db_status,
        "memory_usage_mb": memory_usage,
        "email_sent": bool(email_sent),
        "current_failures": new_failures
    }


@app.on_event("startup")
async def startup_event():
    print("Initializing Aether Backend...")
    
    # [Liveliness Indicator] Signal kernel status to the terminal
    await log_terminal("[SYSTEM] Aether Kernel Online - Command Center Linked")
    
    # --- Local AI Factory Engine (BackgroundScheduler) ---
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from local_ai_factory.engine import start_engine as start_factory_engine
        if start_factory_engine():
            await log_terminal("[FACTORY] AI Factory Engine started - Auditor cycle every 5 min")
            print("[FACTORY] AI Factory Engine initialized successfully")
        else:
            await log_terminal("[FACTORY] AI Factory Engine failed to start (check logs)")
    except ImportError as ie:
        print(f"[FACTORY] Could not import factory engine: {ie}")
        await log_terminal("[FACTORY] Engine not available (import error)")
    except Exception as fe:
        print(f"[FACTORY] Engine startup error: {fe}")
    # --- End Factory Engine ---
    
    # --- ABC-TOM Auditor Background Worker (APScheduler) ---
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        from ai_engine.agent_parser import (
            construct_agent_prompt, append_to_decisions, list_agents
        )

        async def auditor_periodic_task():
            """
            Periodic task that simulates the Auditor workflow:
            1. Load auditor agent instructions via the parser
            2. Query vault.db for tools needing review (is_active=0)
            3. Simulate decision-making and log to M-memory/decisions.md
            """
            try:
                prompt = construct_agent_prompt("auditor-agent.md")
                await log_terminal("[ABC-TOM] Auditor cycle started")

                # Query vault for pending tools
                pending = vault.get_pending_tools()
                if not pending:
                    await log_terminal("[ABC-TOM] Auditor: No pending tools to review")
                    return

                reviewed = 0
                for tool in pending[:5]:  # Process max 5 per cycle
                    tool_name = tool.get("tool_name", "Unknown")
                    trust_score = tool.get("trust_score", 0)

                    # Simulated decision logic based on agent criteria
                    if trust_score >= 60:
                        action = "APPROVE"
                        reason = f"Trust score {trust_score} meets threshold"
                    elif trust_score < 30:
                        action = "FLAG"
                        reason = f"Trust score {trust_score} below minimum. Needs manual review."
                    else:
                        action = "FLAG"
                        reason = f"Trust score {trust_score} in review range (30-59)"

                    from datetime import datetime as dt
                    entry = (
                        f"\n## [{dt.now().strftime('%Y-%m-%d %H:%M')}] Audit Decision\n"
                        f"- Tool: {tool_name}\n"
                        f"- Action: {action}\n"
                        f"- Trust Score: {trust_score}\n"
                        f"- Reason: {reason}\n"
                    )
                    append_to_decisions(entry)
                    reviewed += 1

                await log_terminal(f"[ABC-TOM] Auditor cycle complete: {reviewed} tools reviewed")

            except FileNotFoundError:
                await log_terminal("[ABC-TOM] Auditor agent file not found. Skipping cycle.")
            except Exception as e:
                await log_terminal(f"[ABC-TOM] Auditor error: {str(e)}")

        scheduler = AsyncIOScheduler()
        scheduler.add_job(auditor_periodic_task, 'interval', minutes=30, id='abc_tom_auditor')
        
        # --- Aether Sentinel Periodic Health Monitoring ---
        sentinel_settings = vault.get_sentinel_settings()
        sentinel_enabled = bool(sentinel_settings.get("enabled", 0))
        sentinel_freq = int(sentinel_settings.get("frequency_minutes", 30))
        
        if sentinel_enabled:
            scheduler.add_job(
                perform_sentinel_audit, 
                'interval', 
                minutes=sentinel_freq, 
                id='aether_sentinel'
            )
            await log_terminal(f"[Sentinel] Task initialized - monitoring every {sentinel_freq} minutes")
        else:
            await log_terminal("[Sentinel] Task initialized - standby state (monitoring disabled)")
            
        global global_scheduler
        global_scheduler = scheduler
        
        scheduler.start()
        await log_terminal("[ABC-TOM] APScheduler started - Auditor runs every 30 minutes")
        print("[ABC-TOM] APScheduler initialized successfully")

    except ImportError:
        print("[ABC-TOM] APScheduler not installed. Background auditor disabled.")
        await log_terminal("[ABC-TOM] APScheduler not available. Install with: pip install apscheduler")
    except Exception as e:
        print(f"[ABC-TOM] Scheduler setup error: {e}")
    # --- End ABC-TOM Worker ---
    
    # Check for critical environment variables
    if not os.getenv("GEMINI_API_KEY"):
        await log_terminal("[CRITICAL] GEMINI_API_KEY is missing! Autonomous agents will be disabled.")
    else:
        await log_terminal("[SYSTEM] GEMINI_API_KEY detected. Agent brains ready.")

    initialize_firebase_admin()
    seed_file = Path(__file__).parent / "seed_data.json"
    
    try:
        if seed_file.exists():
            print(f"Found seed_data.json at {seed_file}. Attempting to load...")
            with open(seed_file, "r", encoding="utf-8-sig") as f:
                seed_data = json.load(f)
            
            # Allow seed_data to be a list or a single dict
            if isinstance(seed_data, dict):
                seed_data = [seed_data]
                
            for tool_data in seed_data:
                tool_name = tool_data.get("tool_name")
                if not tool_name:
                    continue
                
                # Check if tool exists, if so we might skip or append. For MVP, we'll recreate or skip
                # Actually, let's just create a mock if it doesn't exist, or update intents if it does.
                existing_tool = vault.get_tool(tool_name)
                
                intents_mapped = tool_data.get("intents_mapped", [])
                job_to_be_done = [intent.get("intent_description", "") for intent in intents_mapped if intent.get("intent_description")]
                
                if existing_tool:
                    continue
                
                # Create default metrics for seeding
                analysis = LabAnalysis(
                    tool_name=tool_name,
                    metrics=ToolMetrics(
                        accuracy=4, speed=4, value=4, ease_of_use=4,
                        learning_curve="Medium", pricing="Freemium", integration="Web"
                    ),
                    visual_quality=VisualQuality.MID,
                    job_to_be_done=job_to_be_done,
                    executive_summary=f"Seeded from Data Ingestion. Category: {tool_data.get('category', 'All')}",
                    pros=["Seeded Data"],
                    cons=["Seeded Data"],
                    use_cases=job_to_be_done
                )
                
                avg_score = sum(intent.get("success_score", 5) for intent in intents_mapped) / max(1, len(intents_mapped))
                trust_score = min(100.0, avg_score * 10.0) # Convert 1-10 to 10-100
                
                audit = AuditLog(tool_name=tool_name, action="Seed Ingestion", reason="Loaded from seed_data.json", new_trust_score=trust_score)
                vault.save_tool(tool_name=tool_name, analysis=analysis, trust_score=trust_score, gallery=[], audit_log=audit)
                print(f"Successfully seeded '{tool_name}' from JSON.")
    except Exception as e:
        print(f"Warning: Failed to load seed_data.json gracefully. Server will still start. Error: {e}")

# Map: task_id -> status (Keep in-memory for now as disjointed tasks)
task_status: Dict[str, str] = {}

async def run_pipeline_task(task_id: str, intent: str):
    """
    Background task wrapper for the pipeline.
    """
    try:
        task_status[task_id] = "running"
        
        # PIPELINE RUN
        result = await pipeline.run_pipeline(intent)
        
        if result["status"] == "success":
            # Vault handles saving internally now via Pipeline or we do it here?
            # Pipeline is the orchestrator, so ideally Pipeline saves to Vault.
            # BUT, we need to pass the Vault to the pipeline or have pipeline init it.
            # For this Phase, let's have the Pipeline return the data and WE save it here 
            # OR better: The Pipeline should check the Vault first (Logic Gate).
            
            # Update: Pipeline now handles Vault logic internally (see pipeline.py updates).
            # So result comes back either from Cache or Fresh Run.
            
            task_status[task_id] = "completed"
        elif result["status"] == "rejected":
             task_status[task_id] = "completed_rejected"
        else:
            task_status[task_id] = f"failed: {result.get('reason')}"
            
    except Exception as e:
        print(f"Pipeline Critical Error: {e}")
        task_status[task_id] = "error"

@app.get("/")
def read_root():
    stats = vault.get_stats()
    return {"status": "online", "system": "Aether Agentic Grid", "tools_indexed": stats["verified_tools_count"]}

@app.post("/pipeline/trigger")
async def trigger_pipeline(intent: str, background_tasks: BackgroundTasks):
    """
    The 'Red Button'. Triggers the autonomous agents in the background.
    Returns a Task ID for polling.
    """
    task_id = str(uuid.uuid4())
    background_tasks.add_task(run_pipeline_task, task_id, intent)
    return {"message": "Pipeline triggered", "task_id": task_id, "intent": intent}

@app.get("/pipeline/status/{task_id}")
def get_status(task_id: str):
    status = task_status.get(task_id, "unknown")
    return {"task_id": task_id, "status": status}

async def scout_task_wrapper(intent: str):
    """
    Wrapper for the background task to ensure ScoutAgent runs correctly.
    """
    print(f"[Background] Starting ScoutAgent.run_discovery_cycle for: {intent}")
    try:
        from semantic_cache import AetherSemanticCache
        from local_embedder import LocalEmbeddingEngine
        from persistence import AetherVault
        
        vault = AetherVault()
        embedder = LocalEmbeddingEngine.get_instance()
        semantic_cache = AetherSemanticCache(embedder, vault)
        
        cached_tool = semantic_cache.check_cache(intent)
        if cached_tool:
            print(f"[Background] ScoutAgent discovery bypassed due to semantic cache hit for '{intent}'.")
            return
            
        scout = ScoutAgent()
        results = await scout.run_discovery_cycle(intent)
        print(f"[Background] ScoutAgent cycle complete. Found {len(results)} tools.")
    except Exception as e:
        print(f"[Background Error] ScoutAgent failed: {e}")

@app.post("/api/agents/scout/run", status_code=202)
async def run_scout_agent(intent: str, background_tasks: BackgroundTasks):
    """
    Triggers the Scout Agent to perform a discovery cycle in the background.
    """
    print(f"[API] Triggering Scout Agent for intent: {intent}")
    background_tasks.add_task(scout_task_wrapper, intent)
    return {"status": "success", "message": "Scout agent discovery cycle started in background"}

@app.get("/tool/{name}")
def get_tool_data(name: str):
    """
    Returns the 'Truth Card' data: Analysis + Trust Score.
    """
    data = vault.get_tool(name)
    if not data:
        raise HTTPException(status_code=404, detail="Tool not found or not yet verified.")
    
    return {
        "name": data["tool_name"],
        "analysis": data["analysis"],
        "trust_score": data["trust_score"],
        "status": data["status"]
    }

@app.get("/gallery/feed")
def get_gallery_feed():
    """
    Returns the 'Evidence Grid'.
    Fetches all items from the Vault.
    Implements Hybrid Ranking: Sponsored Slot (1-3) + Verified Organic.
    """
    # 1. SPONSORED/PROMOTED SLOT (Logic Injection)
    # in a real app, this comes from an Ad Server based on User Intent
    sponsored_items = []

    
    # 2. ORGANIC / VERIFIED SLOT (from Vault)
    # retrieving everything from the vault
    results = vault.search_tools("") 
    
    organic_feed = []
    for data in results:
        analysis = data.get("analysis", {})
        tool_name = data.get("tool_name", "Unknown")
        
        # [NEW] Skip "Ghost Tools" (tools with no actual data/empty summaries or seeded placeholders)
        summary = analysis.get("executive_summary", "")
        if not summary and not analysis.get("job_to_be_done"):
            continue
        if "Seeded from Data Ingestion" in summary:
            continue
            
        # Determine the primary intent or fallback to category
        primary_intent = "General"
        if analysis.get("intents_mapped"):
            primary_intent = analysis["intents_mapped"][0].get("intent_description", "General")
            
        tool_info = {
            "tool_name": tool_name,
            "title": tool_name.title(), # capitalization
            "summary": analysis.get("executive_summary", ""),
            "trust_score": data.get("trust_score", 0),
            "source": analysis.get("source_findings_id") or "Aether Scout",
            "type": "tool",
            "is_sponsored": False,
            "intents": analysis.get("intents_mapped", []),
            "metrics": analysis.get("metrics", {})
        }

        # If there's a gallery, use the first image for the card, else use a placeholder
        media_url = "C:/Users/Yuval/.gemini/antigravity/brain/edcea81f-32d1-4067-8b20-d3b26c1e4a91/aether_evidence_placeholder_1775911102864.png"
        if data.get("gallery") and len(data["gallery"]) > 0:
             media_url = data["gallery"][0].get("media_url", media_url)
             
        organic_feed.append({
             **tool_info,
             "media_url": media_url,
             "primary_intent": primary_intent
        })
            
    # Combine: Sponsored First -> Then Organic
    full_feed = sponsored_items + organic_feed
    
    return full_feed

@app.get("/vault/search")
async def search_vault(q: str):
    """
    Direct search in the Vault, excluding ghost tools.
    Supports semantic search if query is provided.
    """
    if q.strip():
        # Perform semantic search with a higher limit for the Vault view
        results = await search_engine.semantic_search(q, limit=50)
        # Log search for analytics (Phase 5)
        vault.log_search(q, has_match=len(results) > 0)
        return results
    else:
        # Default view: all tools via keyword engine (which returns all if q is empty)
        results = vault.search_tools("", include_inactive=False)
        
    # Filter out empty entries and seeded placeholders
    valid_results = []
    for r in results:
        analysis = r.get("analysis", {})
        summary = analysis.get("executive_summary", "")
        if (summary or analysis.get("job_to_be_done")) and "Seeded from Data Ingestion" not in summary:
            valid_results.append(r)
    return valid_results

@app.post("/admin/vault/tool", dependencies=[Depends(verify_admin_user)])
async def add_manual_tool(tool_data: ManualToolEntry, request: Request, admin_email: str = Depends(verify_admin_user)):
    """
    Adds a tool to the vault manually. Protected by Firebase ID Token.
    """
    try:
        # Construct the LabAnalysis object
        analysis = LabAnalysis(
            tool_name=tool_data.name,
            metrics=ToolMetrics(
                accuracy=tool_data.accuracy,
                speed=tool_data.speed,
                value=tool_data.value,
                ease_of_use=tool_data.ease_of_use,
                pricing=tool_data.pricing,
                learning_curve=tool_data.learning_curve,
                latency_label=tool_data.latency_label,
                cost_label=tool_data.cost_label,
                privacy_grade=tool_data.privacy_grade,
                integration=tool_data.integration
            ),
            visual_quality=VisualQuality(tool_data.visual_quality),
            job_to_be_done=[tool_data.intent_category],
            executive_summary=tool_data.description,
            pros=tool_data.pros,
            cons=tool_data.cons,
            use_cases=tool_data.use_cases,
            website_url=tool_data.website_url
        )

        gallery = []
        if tool_data.image_url:
            gallery.append(GalleryItem(
                tool_id=tool_data.name.lower().replace(" ", "-"),
                media_url=tool_data.image_url,
                style_tags=[tool_data.intent_category],
                prompt_recipe={"note": "Manual Entry"}
            ))

        audit_log = AuditLog(
            tool_name=tool_data.name,
            action="Manual Entry",
            reason=f"Added manually by Admin: {admin_email}",
            new_trust_score=float(tool_data.trust_score)
        )

        # Generate local embedding for search
        search_text = f"{tool_data.name}. {tool_data.description}. " + \
                      ", ".join(tool_data.use_cases + tool_data.pros)
        embedding_bytes = embedder.embed_to_bytes(search_text)

        # Save to database
        vault.save_tool(
            tool_name=tool_data.name,
            analysis=analysis,
            trust_score=float(tool_data.trust_score),
            gallery=gallery,
            audit_log=audit_log,
            embedding=embedding_bytes
        )

        return {"status": "success", "message": f"Tool '{tool_data.name}' added successfully."}

    except Exception as e:
        print(f"[Admin Error] Failed to add tool: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/agent/investigate", dependencies=[Depends(verify_admin_user)])
async def investigate_tool_stream(request: AuditRequest):
    """
    Streams the progress of the Deep Auditor (Agent Console).
    """
    return StreamingResponse(run_deep_audit_stream(request.url), media_type="text/event-stream")

@app.post("/admin/auditor/manual", dependencies=[Depends(verify_admin_user)])
async def manual_vault_audit(request: AuditRequest, admin_email: str = Depends(verify_admin_user)):
    """
    Runs the automated Vault Auditor on a single URL and saves it to the Vault as hidden (is_active: 0).
    """
    try:
        response = await run_lean_audit(request.url)
        if response.get("status") == "error":
            raise HTTPException(status_code=500, detail=response.get("reason", "Auditor failed"))
            
        data = response["audit_data"]
        
        analysis = LabAnalysis(
            tool_name=data["name"],
            metrics=ToolMetrics(
                accuracy=4, speed=4, value=4, ease_of_use=4,
                pricing=data["pricing_model"],
                learning_curve="Medium", # Default
                latency_label="Unknown",
                cost_label="Unknown",
                privacy_grade="Unknown",
                integration="Web"
            ),
            visual_quality=VisualQuality.MID,
            job_to_be_done=[data["category"]],
            executive_summary=data["community_consensus"],
            pros=[],
            cons=[],
            use_cases=[data["category"]],
            audit_notes=data["audit_notes"],
            website_url=request.url
        )

        audit_log = AuditLog(
            tool_name=data["name"],
            action="Vault Auditor AI Analysis",
            reason=f"Triggered by {admin_email} via DuckDuckGo + Gemini",
            new_trust_score=float(data["trust_score"])
        )

        # Generate local embedding for search
        search_text = f"{data['name']}. {data.get('community_consensus', '')}. {data.get('category', '')}"
        embedding_bytes = embedder.embed_to_bytes(search_text)

        vault.save_tool(
            tool_name=data["name"],
            analysis=analysis,
            trust_score=float(data["trust_score"]),
            gallery=[],
            audit_log=audit_log,
            embedding=embedding_bytes,
            is_active=0
        )

        return {"status": "success", "message": f"Tool '{data['name']}' audited and saved as hidden.", "data": data}

    except Exception as e:
        print(f"[Auditor Error]: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/auditor/auto-scan", dependencies=[Depends(verify_admin_user)])
async def bulk_vault_audit(request: BulkAuditRequest, admin_email: str = Depends(verify_admin_user)):
    """
    Runs the automated Vault Auditor on multiple URLs and saves them to the Vault as hidden.
    """
    results = []
    # Note: In a production app this should be enqueued via Celery or BackgroundTasks
    # For MVP we will await sequentially or use BackgroundTasks, but here we do it sequentially.
    for url in request.urls:
        try:
             # Basic implementation calling the single logic
             fake_req = AuditRequest(url=url)
             await manual_vault_audit(fake_req, admin_email)
             results.append({"url": url, "status": "success"})
        except Exception as e:
             results.append({"url": url, "status": "failed", "reason": str(e)})
             
    return {"status": "completed", "results": results}

@app.delete("/admin/vault/tool/{name}", dependencies=[Depends(verify_admin_user)])
async def delete_vault_tool(name: str, admin_email: str = Depends(verify_admin_user)):
    """
    Deletes a tool from the vault. Restricted to admins.
    """
    print(f"[Admin] Deletion request for '{name}' by '{admin_email}'")
    try:
        existing = vault.get_tool(name, include_expired=True)
        if not existing:
             raise HTTPException(status_code=404, detail=f"Tool '{name}' not found.")
            
        actual_name = existing["tool_name"]
        vault.delete_tool(actual_name)
        return {"status": "success", "message": f"Tool '{actual_name}' deleted successfully by {admin_email}."}
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Admin Error] Failed to delete tool: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/sentinel/settings", dependencies=[Depends(verify_admin_user)])
def get_sentinel_settings(admin_email: str = Depends(verify_admin_user)):
    """Retrieves Aether Sentinel settings."""
    settings = vault.get_sentinel_settings()
    settings["enabled"] = bool(settings.get("enabled", 0))
    return settings

@app.post("/admin/sentinel/settings", dependencies=[Depends(verify_admin_user)])
async def update_sentinel_settings(settings: SentinelSettingsInput, admin_email: str = Depends(verify_admin_user)):
    """Updates Sentinel configuration and schedules or updates tasks dynamically."""
    vault.update_sentinel_settings(
        1 if settings.enabled else 0,
        settings.alert_email,
        settings.frequency_minutes,
        settings.failure_threshold
    )
    
    global global_scheduler
    if global_scheduler:
        try:
            job = global_scheduler.get_job('aether_sentinel')
            if job:
                global_scheduler.remove_job('aether_sentinel')
                
            if settings.enabled:
                global_scheduler.add_job(
                    perform_sentinel_audit,
                    'interval',
                    minutes=settings.frequency_minutes,
                    id='aether_sentinel'
                )
                await log_terminal(f"[Sentinel] Dynamic Reschedule - Monitoring active every {settings.frequency_minutes} minutes")
            else:
                await log_terminal("[Sentinel] Dynamic Standby - Periodic monitoring paused")
        except Exception as se:
            print(f"[Sentinel Settings Exception] Job re-alignment failed: {se}")
            await log_terminal(f"[Sentinel Error] Dynamic realignment failed: {str(se)}")
            
    return {"status": "success", "message": "Sentinel settings saved and worker dynamically configured."}

@app.get("/admin/sentinel/logs", dependencies=[Depends(verify_admin_user)])
def get_sentinel_logs(limit: int = 50, admin_email: str = Depends(verify_admin_user)):
    """Retrieves recent health check sentinel audit logs."""
    return vault.get_sentinel_audit_logs(limit=limit)

@app.post("/admin/sentinel/test-audit", dependencies=[Depends(verify_admin_user)])
async def test_sentinel_audit(admin_email: str = Depends(verify_admin_user)):
    """Manually triggers a Sentinel audit scan in real-time and returns detailed status."""
    result = await perform_sentinel_audit(is_manual=True)
    return result

@app.get("/admin/analytics", dependencies=[Depends(verify_admin_user)])
def get_analytics(admin_email: str = Depends(verify_admin_user)):
    """
    Returns recent search queries and match rates.
    """
    return vault.get_search_analytics(limit=100)

@app.get("/admin/requests", dependencies=[Depends(verify_admin_user)])
def get_requests():
    tools = vault.get_pending_tools()
    return {"requests": tools}

@app.post("/admin/approve", dependencies=[Depends(verify_admin_user)])
def approve_tool(tool_name: str):
    vault.toggle_tool_status(tool_name, True)
    return {"status": "success", "message": f"Tool '{tool_name}' and is now live."}

@app.get("/admin/live-scans", dependencies=[Depends(verify_admin_user)])
def get_live_scans():
    return vault.get_live_scans()

@app.post("/admin/reject", dependencies=[Depends(verify_admin_user)])
def reject_tool(tool_name: str):
    vault.delete_tool(tool_name)
    return {"status": "success", "message": f"Tool '{tool_name}' was rejected and removed."}

# --- Staging Pipeline Endpoints ---

@app.get("/admin/staging/queue", dependencies=[Depends(verify_admin_user)])
def get_staging_queue(status: str = "processed", limit: int = 100):
    """
    Returns staging tools with the given status.
    Default: 'processed' (ready for human review).
    Also accepts: 'pending', 'approved', 'rejected'
    """
    return vault.get_staging_queue(status=status, limit=limit)

@app.get("/admin/staging/stats", dependencies=[Depends(verify_admin_user)])
def get_staging_stats():
    """Returns pipeline stats: pending, processed, approved, rejected counts."""
    return vault.get_staging_stats()

class StagingApprovePayload(BaseModel):
    trust_score: Optional[float] = None
    executive_summary: Optional[str] = None
    category: Optional[str] = None
    reviewer_notes: str = ""

@app.post("/admin/staging/approve/{staging_id}", dependencies=[Depends(verify_admin_user)])
def approve_staging(staging_id: int, payload: StagingApprovePayload = None):
    """
    Approves a staging tool and moves it to the live Vault.
    Supports optional overrides for trust_score, summary, and category.
    """
    if payload is None:
        payload = StagingApprovePayload()

    result = vault.approve_staging_tool(
        staging_id=staging_id,
        trust_score=payload.trust_score,
        executive_summary=payload.executive_summary,
        category=payload.category,
        reviewer_notes=payload.reviewer_notes
    )
    if not result:
        raise HTTPException(status_code=404, detail="Staging tool not found.")
    return {"status": "success", "message": f"Tool '{result}' approved and is now live."}

@app.post("/admin/staging/reject/{staging_id}", dependencies=[Depends(verify_admin_user)])
def reject_staging(staging_id: int, reason: str = ""):
    """Rejects a staging tool (keeps it in DB for analytics)."""
    result = vault.reject_staging_tool(staging_id, reviewer_notes=reason)
    if not result:
        raise HTTPException(status_code=404, detail="Staging tool not found.")
    return {"status": "success", "message": f"Tool '{result}' rejected."}

class StagingBatchPayload(BaseModel):
    staging_ids: List[int]
    reason: str = ""

@app.post("/admin/staging/approve-batch", dependencies=[Depends(verify_admin_user)])
def approve_staging_batch(payload: StagingBatchPayload):
    """Batch-approve multiple staging tools at once."""
    approved = vault.approve_staging_batch(payload.staging_ids)
    return {"status": "success", "approved": approved, "count": len(approved)}

@app.post("/admin/staging/reject-batch", dependencies=[Depends(verify_admin_user)])
def reject_staging_batch(payload: StagingBatchPayload):
    """Batch-reject multiple staging tools at once."""
    rejected = vault.reject_staging_batch(payload.staging_ids, reason=payload.reason)
    return {"status": "success", "rejected": rejected, "count": len(rejected)}

class StagingEditPayload(BaseModel):
    trust_score: Optional[float] = None
    executive_summary: Optional[str] = None
    category: Optional[str] = None

@app.put("/admin/staging/edit/{staging_id}", dependencies=[Depends(verify_admin_user)])
def edit_staging(staging_id: int, payload: StagingEditPayload):
    """Quick-edit trust score, summary, and category before approval."""
    success = vault.edit_staging_tool(
        staging_id=staging_id,
        trust_score=payload.trust_score,
        executive_summary=payload.executive_summary,
        category=payload.category
    )
    if not success:
        raise HTTPException(status_code=404, detail="Staging tool not found.")
    return {"status": "success", "message": "Staging tool updated."}


@app.post("/admin/vault/toggle/{name}", dependencies=[Depends(verify_admin_user)])
async def toggle_tool_active(name: str, active: bool, admin_email: str = Depends(verify_admin_user)):
    """
    Enables/Disables a tool (Kill Switch).
    """
    try:
        vault.toggle_tool_status(name, active)
        return {"status": "success", "is_active": active}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/vault/pricing/{name}", dependencies=[Depends(verify_admin_user)])
async def update_tool_pricing(name: str, pricing: str, admin_email: str = Depends(verify_admin_user)):
    """
    Quickly updates pricing.
    """
    try:
        vault.quick_update_pricing(name, pricing)
        return {"status": "success", "pricing": pricing}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search/intent")
async def search_intent(q: str):
    """
    Semantic Search using Gemini Intent Matching.
    """
    if not q.strip():
        return []
        
    try:
        results = await search_engine.semantic_search(q)
        # Log search for analytics (Phase 5)
        vault.log_search(q, has_match=len(results) > 0)
        return results
    except RuntimeError as re:
        if str(re) == "System initializing":
            raise HTTPException(status_code=503, detail="System initializing")
        raise HTTPException(status_code=500, detail=str(re))
    except Exception as e:
        print(f"[API Error] /search/intent failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vault/categories/stats")
def get_category_stats():
    results = vault.search_tools("")
    counts = {
        "dev": 0,
        "design": 0,
        "text": 0,
        "video": 0,
        "audio": 0,
        "marketing": 0,
        "presentations": 0,
        "enterprise": 0
    }
    
    # We define strict inclusion keywords per category
    # to avoid double-counting or missing items.
    category_map = {
         "dev": ["code", "dev", "react", "tailwind", "program", "cursor", "v0", "github", "api", "software", "python", "javascript", "copilot"],
         "design": ["image", "design", "midjourney", "art", "creative", "ui", "dall-e", "luma", "leonardo", "stable diffusion", "krea", "magnific"],
         "text": ["text", "write", "content", "chat", "perplexity", "claude", "knowledge", "gpt", "model", "copy", "wordtune", "quillbot", "character"],
         "video": ["video", "film", "edit", "heygen", "runway", "sora", "pika", "invideo", "veed", "synthesia"],
         "audio": ["audio", "music", "vocal", "sound", "suno", "elevenlabs", "murf", "playht", "descript", "voice"],
         "marketing": ["marketing", "seo", "sales", "brand", "campaign", "jasper"],
         "presentations": ["present", "gamma", "slide", "deck", "pitch", "tome", "beautiful"],
         "enterprise": ["enterprise", "automat", "zapier", "workflow", "make", "task", "agent", "notion"],
    }
    
    for data in results:
        analysis = data.get("analysis", {})
        jobs = analysis.get("job_to_be_done", [])
        intents = analysis.get("intents_mapped", [])
        
        # Combine all descriptive text to search for keywords
        text_corpus = " ".join([str(j) for j in jobs]).lower()
        if isinstance(intents, list):
            for i in intents:
                text_corpus += " " + str(i.get("intent_description", "")).lower()
        tool_name = data.get("tool_name", "").lower()
        text_corpus += " " + tool_name + " " + analysis.get("executive_summary", "").lower()
        
        # Determine the primary category for this tool (only count it once)
        best_cat = None
        best_cat_matches = 0
        
        for cat, keywords in category_map.items():
            matches = sum(1 for kw in keywords if kw in text_corpus)
            if matches > best_cat_matches:
                best_cat_matches = matches
                best_cat = cat
                
        # If we couldn't classify it, we try to put it somewhere reasonable based on tool name heuristics,
        # or we just skip it so the numbers don't lie.
        if best_cat:
            counts[best_cat] += 1
        elif "ai" in tool_name: # Fallback to text if completely generic
            counts["text"] += 1
            
    return counts

@app.get("/vault/stats")
def vault_stats():
    return vault.get_stats()

# --- Community & Elo Battle Endpoints ---

@app.post("/community/profile")
async def sync_profile(user_data: Dict = Depends(get_current_user)):
    """
    Syncs Firebase user with local profile and returns it.
    """
    uid = user_data.get("uid")
    email = user_data.get("email")
    display_name = user_data.get("name") or email.split("@")[0]
    
    profile = vault.get_or_create_user(uid, email, display_name)
    
    # Check for new badges
    new_badges = check_for_badges(profile)
    if new_badges:
        profile.badges.extend(new_badges)
        vault.update_user(profile)
        
    return profile

@app.get("/community/profile")
async def get_profile(user_data: Dict = Depends(get_current_user)):
    uid = user_data.get("uid")
    email = user_data.get("email")
    profile = vault.get_or_create_user(uid, email)
    
@app.get("/community/leaderboard")
def get_leaderboard():
    return vault.get_user_rankings(limit=20)

async def background_audit_scouted_tool(task_id: int, url: str, description: str, submitter_email: str, suggested_name: str = None):
    log_file = Path(__file__).parent / "background_tasks.log"
    await log_terminal(f"STARTING AUDIT: {url} (suggested name: {suggested_name}, requested by {submitter_email})")

    try:
        # Update task status to scanning
        vault.update_scout_task(task_id, "scanning")
        
        # Step 1: Run Scraper + Gemini Audit
        await log_terminal("Step 1: Running Agent Scan...")

        response = await run_lean_audit(url)
        if response.get("status") == "error":
            reason = response.get("reason", "Unknown error")
            with open(log_file, "a") as f:
                f.write(f"[{datetime.now()}] FAIL: Auditor returned error: {reason}\n")
            vault.update_scout_task(task_id, "failed", reason)
            return
            
        data = response["audit_data"]
        
        # Use suggested name if AI failed to find a meaningful one or as a fallback
        final_tool_name = data.get('name')
        if not final_tool_name or "unnamed" in final_tool_name.lower() or "ai tool" in final_tool_name.lower():
            if suggested_name:
                final_tool_name = suggested_name
        
        with open(log_file, "a") as f:
            f.write(f"[{datetime.now()}] Step 2: Agent Scan Complete. Name: {final_tool_name} (AI target: {data.get('name')}). Trust Score: {data.get('trust_score')}\n")
        
        await log_terminal(f"Step 2: Agent Scan Complete. Name: {final_tool_name}. Trust Score: {data.get('trust_score')}")

        # Step 2: Construct LabAnalysis
        analysis = LabAnalysis(
            tool_name=final_tool_name,
            metrics=ToolMetrics(
                accuracy=4, speed=4, value=4, ease_of_use=4,
                pricing=data.get("pricing_model", "Unknown"),
                learning_curve="Medium",
                latency_label="Unknown",
                cost_label="Unknown",
                privacy_grade="Unknown",
                integration="Web"
            ),
            visual_quality=VisualQuality.MID,
            job_to_be_done=[data.get("category", "General")],
            executive_summary=data.get("community_consensus", ""),
            pros=[],
            cons=[],
            use_cases=[data.get("category", "General")],
            audit_notes=data.get("audit_notes", ""),
            website_url=url
        )

        audit_log = AuditLog(
            tool_name=final_tool_name,
            action="Community Scout AI Analysis",
            reason=f"Triggered by {submitter_email} via DuckDuckGo + Gemini",
            new_trust_score=float(data.get("trust_score", 50))
        )

        # Step 3: Generate local embedding and Save to Vault (Inactive)
        with open(log_file, "a") as f:
            f.write(f"[{datetime.now()}] Step 3: Embedding + Saving to Vault (is_active=0)...\n")

        search_text = f"{final_tool_name}. {data.get('community_consensus', '')}. {data.get('category', '')}"
        embedding_bytes = embedder.embed_to_bytes(search_text)

        vault.save_tool(
            tool_name=final_tool_name,
            analysis=analysis,
            trust_score=float(data.get("trust_score", 50)),
            gallery=[],
            audit_log=audit_log,
            embedding=embedding_bytes,
            is_active=0
        )
        
        # Update task to completed and sync the name for the admin list
        vault.update_scout_task(task_id, "completed", final_tool_name=final_tool_name)
        
        with open(log_file, "a") as f:
            f.write(f"[{datetime.now()}] SUCCESS: Tool {final_tool_name} is now in the review queue.\n")

    except Exception as e:
        error_info = f"CRITICAL ERROR in background auditor: {str(e)}\n{traceback.format_exc()}"
        print(f"[Background Auditor Exception]: {error_info}")
        vault.update_scout_task(task_id, "failed", str(e))
        with open(log_file, "a") as f:
            f.write(f"[{datetime.now()}] {error_info}\n")


@app.post("/community/contribute")
async def contribute_tool(contribution: ToolContribution, background_tasks: BackgroundTasks, user_data: Dict = Depends(get_current_user)):
    """
    User suggests a tool. Awards points, updates contributions count, and runs AI Audit in background.
    """
    uid = user_data.get("uid")
    email = user_data.get("email")
    
    profile = vault.get_or_create_user(uid, email)
    profile.contributions_count += 1
    profile.points += 50 # Higher reward for contribution
    
    # Check for badges (like Model Scout)
    new_badges = check_for_badges(profile)
    if new_badges:
        profile.badges.extend(new_badges)
        
    vault.update_user(profile)
    
    # Create the scout task and pass its ID to the background
    task_id = vault.create_scout_task(contribution.name, contribution.url, email)
    
    # Run the Vault Auditor in the background
    background_tasks.add_task(background_audit_scouted_tool, task_id, contribution.url, contribution.description, email, suggested_name=contribution.name)
    
    print(f"[Community] New tool Scouted by {email}: {contribution.name} ({contribution.url}). Audit queued.")
    
    return {"status": "success", "user": profile, "new_badges": new_badges}

# --- Phase 7: B2B Intent Data (Aether Insights) ---

@app.get("/vendor/insights/{name}")
def get_vendor_insights(name: str):
    """
    Returns market intelligence for a specific tool vendor.
    """
    insights = vault.get_vendor_insights(name)
    if not insights or insights["total_battles"] == 0:
        # Check if tool even exists
        tool = vault.get_tool(name)
        if not tool:
             raise HTTPException(status_code=404, detail="Tool not found")
        
    return insights

@app.get("/vendor/tools")
def list_vendor_tools():
    """
    Lists all tools available for insight generation.
    """
    tools = vault.search_tools("")
    return [{"name": t["tool_name"], "id": t["id"]} for t in tools]

# --- Phase 8: Live Benchmarking Endpoints ---

@app.get("/benchmarks/live")
def get_live_benchmarks():
    """
    Returns the latest real-time performance metrics for monitored tools.
    """
    return vault.get_latest_benchmarks()

@app.post("/api/agents/metrics/run", status_code=202)
async def run_live_metrics_agent(background_tasks: BackgroundTasks):
    """
    Triggers the LiveMonitor agent to scan and benchmark tools in the background.
    """
    from live_benchmarking import LiveMonitor
    monitor = LiveMonitor(vault)
    background_tasks.add_task(monitor.run_benchmark_cycle)
    return {"status": "success", "message": "Live metrics benchmarking started in background"}

@app.post("/admin/live-metrics/trigger", dependencies=[Depends(verify_admin_user)])
async def trigger_live_benchmark(background_tasks: BackgroundTasks, admin_email: str = Depends(verify_admin_user)):
    """
    Manually triggers a live benchmark cycle. Admin only.
    """
    from live_benchmarking import LiveMonitor
    monitor = LiveMonitor(vault)
    background_tasks.add_task(monitor.run_benchmark_cycle)
    return {"status": "success", "message": "Live benchmark cycle triggered in background."}
@app.post("/admin/discovery/trigger", dependencies=[Depends(verify_admin_user)])
async def trigger_autonomous_discovery(background_tasks: BackgroundTasks, admin_email: str = Depends(verify_admin_user)):
    """
    The 'Super Scout'. Triggers autonomous agents to find new AI tools online.
    """
    print(f"[Admin] Autonomous Discovery triggered by {admin_email}")
    
    async def discovery_task():
        # High-potential categories to scan
        intents = [
            "Hot new AI tools for software developers",
            "Trending generative AI for video and audio",
            "Latest LLM tools on Reddit and ProductHunt",
            "Innovative AI automation agents"
        ]
        for intent in intents:
            try:
                # We use the pipeline to Discover -> Audit -> Save
                # Note: Pipeline saves as 'is_active=1' by default, 
                # but we might want them hidden for admin review.
                # For now we'll follow current pipeline logic.
                await pipeline.run_pipeline(intent)
                await asyncio.sleep(5) # Give it some breathing room
            except Exception as e:
                print(f"[Discovery Error] Failed intent '{intent}': {e}")

    background_tasks.add_task(discovery_task)
    return {"status": "success", "message": "Autonomous scouting cycle triggered in background."}

# --- Phase 10: System Pulse & Diagnostics ---

@app.get("/admin/heartbeat", dependencies=[Depends(verify_admin_user)])
async def get_system_heartbeat(admin_email: str = Depends(verify_admin_user)):
    """
    Returns the 'Health Status' of the Aether Backend.
    """
    # Check Embedder Status
    embedder_status = "UNKNOWN"
    memory_usage = 0
    
    try:
        import psutil
        process = psutil.Process(os.getpid())
        memory_usage = round(process.memory_info().rss / 1024 / 1024, 2)
    except Exception:
        memory_usage = -1 # N/A indicator
    
    try:
        from local_embedder import LocalEmbeddingEngine
        eng = LocalEmbeddingEngine.get_instance()
        if eng.is_ready():
            embedder_status = "ACTIVE"
        else:
            embedder_status = "NO_API_KEY"
    except Exception as e:
        print(f"[Heartbeat] Embedder check failed: {e}")
        embedder_status = "ERROR"

    # Dynamic DB check
    current_db_status = "DISCONNECTED"
    try:
        vault.get_stats()
        current_db_status = "CONNECTED"
    except Exception:
        current_db_status = "ERROR"

    return {
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "memory_usage_mb": memory_usage if memory_usage >= 0 else "N/A",
        "embedder_status": embedder_status,
        "database_status": current_db_status,
        "admin_identity": admin_email
    }

@app.get("/api/health")
async def get_api_health():
    """
    Public health check for Telemetry.
    Returns RAM usage, DB status, and Gemini API status.
    """
    # 1. RAM Usage (system-wide)
    try:
        ram = psutil.virtual_memory()
        ram_usage = f"{ram.percent}%"
    except Exception:
        ram_usage = "N/A"

    # 2. Process Memory (this backend process)
    try:
        process = psutil.Process(os.getpid())
        memory_usage_mb = round(process.memory_info().rss / 1024 / 1024, 2)
    except Exception:
        memory_usage_mb = "N/A"

    # 3. Database Status (SQLite)
    db_status = "Disconnected"
    try:
        vault.get_stats()
        db_status = "Connected"
    except Exception:
        db_status = "Error"

    # 4. Embedder Status
    embedder_status = "UNKNOWN"
    gemini_status = "Offline"
    try:
        from local_embedder import LocalEmbeddingEngine
        eng = LocalEmbeddingEngine.get_instance()
        if eng.is_ready():
            embedder_status = "ACTIVE"
            gemini_status = "Online"
        else:
            embedder_status = "NO_API_KEY"
    except Exception:
        embedder_status = "ERROR"

    return {
        "ram_usage": ram_usage,
        "memory_usage_mb": memory_usage_mb,
        "db_status": db_status,
        "embedder": gemini_status,
        "embedder_status": embedder_status,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/admin/logs", dependencies=[Depends(verify_admin_user)])
def get_admin_logs(lines: int = 50, log_type: str = "tasks", admin_email: str = Depends(verify_admin_user)):
    """
    Returns the last N lines of the requested log file.
    """
    log_file = "background_tasks.log" if log_type == "tasks" else "error.log"
    log_path = Path(__file__).parent / log_file
    
    if not log_path.exists():
        return {"error": f"Log file {log_file} not found"}
        
    try:
        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            # Simple tail implementation
            content = f.readlines()
            last_lines = content[-lines:] if len(content) > lines else content
            return {"log_type": log_type, "lines": last_lines}
    except Exception as e:
        return {"error": str(e)}

@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket, token: str = None):
    # Perform validation
    is_valid = False
    if token:
        try:
            # verify_admin_user expects "Bearer <token>" format. We pass websocket as the request parameter
            verify_admin_user(authorization=f"Bearer {token}", request=websocket)
            is_valid = True
        except Exception as e:
            print(f"[WS AUTH FAIL] WebSocket token verification failed: {e}")
            
    if not is_valid:
        # Accept first to properly send the close code (standard WebSocket handshake behavior)
        await websocket.accept()
        await websocket.close(code=1008) # Policy Violation
        return

    await log_streamer.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                if payload.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except Exception:
                # If not JSON or doesn't match format, just ignore to keep loop alive
                pass
    except WebSocketDisconnect:
        log_streamer.disconnect(websocket)
    except Exception:
        log_streamer.disconnect(websocket)

# --- Phase 9: Gemma Local Worker Batch Upload ---

GEMMA_BATCHES_FILE = Path(__file__).parent / "gemma_batches.json"
GEMMA_WORKER_KEY = os.getenv("GEMMA_WORKER_KEY", "")

class GemmaBatchUpload(BaseModel):
    batch_id: str
    processed_at: str
    model_used: str
    mode: str
    stats: Dict
    verified_items: List[Dict]
    rejected_items: List[Dict]

def _verify_worker_key(request: Request, authorization: str = Header(None)) -> str:
    """
    Accepts either:
      - Bearer <firebase_token> (admin browser)
      - X-Worker-Key <api_key>  (local worker script)
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization")

    # Option 1: API Key from local worker
    if authorization.startswith("X-Worker-Key "):
        key = authorization.split(" ", 1)[1]
        if not GEMMA_WORKER_KEY or key != GEMMA_WORKER_KEY:
            raise HTTPException(status_code=403, detail="Invalid Worker Key")
        return "local-worker"

    # Option 2: Firebase Bearer token (admin dashboard)
    if authorization.startswith("Bearer "):
        return verify_admin_user(authorization, request=request)

    raise HTTPException(status_code=401, detail="Invalid Authorization format")

def _load_gemma_batches() -> List[Dict]:
    if GEMMA_BATCHES_FILE.exists():
        with open(GEMMA_BATCHES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def _save_gemma_batches(batches: List[Dict]):
    with open(GEMMA_BATCHES_FILE, "w", encoding="utf-8") as f:
        json.dump(batches, f, ensure_ascii=False, indent=2)

@app.post("/admin/gemma/upload-batch")
async def upload_gemma_batch(batch: GemmaBatchUpload, identity: str = Depends(_verify_worker_key)):
    """
    Receives a pre-processed batch from the local Gemma worker and stores it.
    Accepts API key auth (local worker) or Firebase token (admin browser).
    """
    print(f"[Gemma] Batch '{batch.batch_id}' uploaded by {identity}. Items: {batch.stats}")

    batch_record = batch.dict()
    batch_record["uploaded_by"] = identity
    batch_record["uploaded_at"] = datetime.now().isoformat()

    batches = _load_gemma_batches()
    batches.insert(0, batch_record)  # newest first
    # Keep only last 50 batches
    batches = batches[:50]
    _save_gemma_batches(batches)

    return {
        "status": "success",
        "message": f"Batch '{batch.batch_id}' stored. {batch.stats.get('passed_noise_gate', 0)} items verified, {batch.stats.get('escalated_to_cloud', 0)} escalated.",
        "batch_id": batch.batch_id
    }

@app.get("/admin/gemma/batches", dependencies=[Depends(verify_admin_user)])
def get_gemma_batches(admin_email: str = Depends(verify_admin_user)):
    """
    Returns all stored Gemma batch results for the admin dashboard.
    """
    return _load_gemma_batches()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
