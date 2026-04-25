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
from agents.scout import ScoutAgent
import psutil
from logger_utils import log_streamer, log_terminal
from fastapi import WebSocket, WebSocketDisconnect

class AuditRequest(BaseModel):
    url: str
    
class BulkAuditRequest(BaseModel):
    urls: List[str]

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

@app.on_event("startup")
async def startup_event():
    print("Initializing Aether Backend...")
    
    # [Liveliness Indicator] Signal kernel status to the terminal
    await log_terminal("[SYSTEM] Aether Kernel Online - Command Center Linked")
    
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
            use_cases=tool_data.use_cases
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
            audit_notes=data["audit_notes"]
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
            audit_notes=data.get("audit_notes", "")
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
            # Check if model files exist in cache
            cache_dir = Path(eng.CACHE_DIR)
            model_exists = (cache_dir / "models--BAAI--bge-small-en-v1.5").exists()
            embedder_status = "LOADING" if model_exists else "MISSING_MODEL"
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
    # 1. RAM Usage
    try:
        ram = psutil.virtual_memory()
        ram_usage = f"{ram.percent}%"
    except Exception:
        ram_usage = "N/A"

    # 2. Database Status (SQLAlchemy/SQLite)
    db_status = "Disconnected"
    try:
        vault.get_stats()
        db_status = "Connected"
    except Exception:
        db_status = "Error"

    # 3. Gemini API Status
    gemini_status = "Offline"
    if os.getenv("GEMINI_API_KEY"):
        gemini_status = "Online"

    return {
        "ram_usage": ram_usage,
        "db_status": db_status,
        "embedder": gemini_status,
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
async def websocket_logs(websocket: WebSocket):
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

def _verify_worker_key(authorization: str = Header(None)) -> str:
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
        return verify_admin_user(authorization)

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
