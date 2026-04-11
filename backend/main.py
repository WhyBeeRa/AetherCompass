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

from fastapi import FastAPI, BackgroundTasks, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional
import uuid

import json
import os
from pathlib import Path
from pipeline import AetherPipeline
from models import GalleryItem, LabAnalysis, TrustScore, ToolMetrics, VisualQuality, AuditLog, ManualToolEntry
from auth import verify_admin_user, initialize_firebase_admin
initialize_firebase_admin()
from fastapi import Request, Depends
from firebase_admin import auth as firebase_auth
from community_logic import calculate_elo_change, check_for_badges
from models import UserProfile, EloBattleVote, Badge, ToolContribution, LiveMetric
from pydantic import BaseModel
from admin_auditor import run_vault_audit

class AuditRequest(BaseModel):
    url: str
    
class BulkAuditRequest(BaseModel):
    urls: List[str]

app = FastAPI(title="Aeather API", description="Backend for the Agentic Grid", version="0.2.0")

origins = [
    "https://www.aethercompass.com",
    "https://aethercompass.com",
    "https://api.aethercompass.com",
    "http://www.aethercompass.com",
    "http://aethercompass.com",
    "http://localhost:5173",
    "http://localhost",
    "http://localhost:80",
]

# 3. הזרקת ה-Middleware
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

# Initialize Semantic Search Engine
from search_engine import AetherSearchEngine
search_engine = AetherSearchEngine()

@app.on_event("startup")
async def startup_event():
    print("Initializing Aether Backend...")
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
                    print(f"Tool {tool_name} already in Vault. Skipping seed overwrite to preserve original data.")
                    continue
                
                # Create default metrics for seeding
                analysis = LabAnalysis(
                    tool_name=tool_name,
                    metrics=ToolMetrics(
                        accuracy=4, speed=4, value=4, ease_of_use=4,
                        learning_curve="בינוני", pricing="Freemium", integration="Web"
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
    sponsored_items = [
        {
            "tool_name": "Jasper Enterprise",
            "title": "Jasper Enterprise",
            "summary": "AI marketing platform built for enterprise scale. Brand voice consistency and SOC2 compliance.",
            "trust_score": 98.0, # High trust even for ads
            "source": "Aether Promoted",
            "type": "tool",
            "is_sponsored": True,
            "media_url": "https://images.unsplash.com/photo-1661956602116-aa6865609028?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
            "prompt_recipe": {"prompt": "Enterprise marketing campaign"},
            "style_tags": ["Enterprise", "Marketing"],
            "trust_badge_visible": True
        }
        # Add more if needed, typically 1-3 slots
    ]
    
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
        primary_intent = "כללי"
        if analysis.get("intents_mapped"):
            primary_intent = analysis["intents_mapped"][0].get("intent_description", "כללי")
            
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
        media_url = "https://images.unsplash.com/photo-1620712948343-0008cc890752?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"
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
def search_vault(q: str):
    """
    Direct search in the Vault, excluding ghost tools.
    """
    results = vault.search_tools(q, include_inactive=False)
    # Log search for analytics (Phase 5)
    if q.strip():
        vault.log_search(q, has_match=len(results) > 0)
        
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

        # Save to database
        vault.save_tool(
            tool_name=tool_data.name,
            analysis=analysis,
            trust_score=float(tool_data.trust_score),
            gallery=gallery,
            audit_log=audit_log,
            embedding=None # We skip embedding for purely manual tools for now
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
        response = await run_vault_audit(request.url)
        if response.get("status") == "error":
            raise HTTPException(status_code=500, detail=response.get("reason", "Auditor failed"))
            
        data = response["audit_data"]
        
        analysis = LabAnalysis(
            tool_name=data["name"],
            metrics=ToolMetrics(
                accuracy=4, speed=4, value=4, ease_of_use=4,
                pricing=data["pricing_model"],
                learning_curve="בינוני", # Default
                latency_label="Unknown",
                cost_label="Unknown",
                privacy_grade="Unknown",
                integration="Web"
            ),
            visual_quality=VisualQuality.MID,
            job_to_be_done=[data["category"]],
            executive_summary=data["community_consensus"],
            pros=data["pros"],
            cons=data["cons"],
            use_cases=[data["category"]]
        )

        audit_log = AuditLog(
            tool_name=data["name"],
            action="Vault Auditor AI Analysis",
            reason=f"Triggered by {admin_email} via DuckDuckGo + Gemini",
            new_trust_score=float(data["trust_score"])
        )

        vault.save_tool(
            tool_name=data["name"],
            analysis=analysis,
            trust_score=float(data["trust_score"]),
            gallery=[],
            audit_log=audit_log,
            embedding=None
        )
        
        # Hide by default as requested
        vault.toggle_tool_status(data["name"], False)

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
    return profile

@app.get("/community/battle/pair")
def get_battle_pair(category: Optional[str] = None):
    """
    Returns two tools for an Elo battle.
    """
    pair = vault.get_random_tool_pair(category)
    if len(pair) < 2:
        # Fallback to any tools if category is empty
        pair = vault.get_random_tool_pair(None)
        
    if len(pair) < 2:
        raise HTTPException(status_code=404, detail="Not enough tools for a battle.")
        
    return pair

@app.post("/community/battle/vote")
async def submit_vote(vote: EloBattleVote, user_data: Dict = Depends(get_current_user)):
    """
    Records a vote and updates tool ELO scores.
    """
    uid = user_data.get("uid")
    
    # 1. Record the vote
    vault.record_vote(uid, vote.tool_a, vote.tool_b, vote.winner, vote.category, vote.reason)
    
    # 2. Update Tool ELO in Trust Score
    tool_a_data = vault.get_tool(vote.tool_a)
    tool_b_data = vault.get_tool(vote.tool_b)
    
    if tool_a_data and tool_b_data:
        elo_a = tool_a_data["trust_score"]
        elo_b = tool_b_data["trust_score"]
        
        if vote.winner == vote.tool_a:
            new_a, new_b = calculate_elo_change(elo_a, elo_b)
        elif vote.winner == vote.tool_b:
            new_b, new_a = calculate_elo_change(elo_b, elo_a)
        else: # Draw or other
             # In a draw, we don't change or change slightly? Let's skip for now or use 0.5
             return {"status": "success", "message": "Vote recorded (draw)"}

        # Cap scores between 1-100
        new_a = max(1.0, min(100.0, new_a))
        new_b = max(1.0, min(100.0, new_b))
        
        vault.update_tool_trust_score(vote.tool_a, new_a, f"Elo Battle Win against {vote.tool_b}")
        vault.update_tool_trust_score(vote.tool_b, new_b, f"Elo Battle Loss against {vote.tool_a}")

    # 3. Update User Badges/Points
    profile = vault.get_or_create_user(uid, user_data.get("email"))
    profile.votes_count += 1
    profile.points += 10
    new_badges = check_for_badges(profile)
    if new_badges:
        profile.badges.extend(new_badges)
    
    vault.update_user(profile)
    
    return {"status": "success", "user": profile, "new_badges": new_badges}

@app.get("/community/leaderboard")
def get_leaderboard():
    return vault.get_user_rankings(limit=20)

@app.post("/community/contribute")
async def contribute_tool(contribution: ToolContribution, user_data: Dict = Depends(get_current_user)):
    """
    User suggests a tool. Awards points and updates contributions count.
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
    
    # In a real app, we'd log this contribution for admin review
    print(f"[Community] New tool Scouted by {email}: {contribution.name} ({contribution.url})")
    
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

@app.post("/admin/benchmarks/trigger", dependencies=[Depends(verify_admin_user)])
async def trigger_live_benchmark(background_tasks: BackgroundTasks, admin_email: str = Depends(verify_admin_user)):
    """
    Manually triggers a live benchmark cycle.
    """
    from live_benchmarking import LiveMonitor
    monitor = LiveMonitor(vault)
    background_tasks.add_task(monitor.run_benchmark_cycle)
    return {"status": "success", "message": "Live benchmark cycle triggered in background."}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
