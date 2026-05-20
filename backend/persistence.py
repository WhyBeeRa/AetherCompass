import sqlite3
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any, Tuple
from models import AuditLog, LabAnalysis, GalleryItem, TrustScore, UserProfile, Badge, LiveMetric

from pathlib import Path

# Database File Path
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "vault.db"


class AetherVault:
    """
    The Memory Layer.
    Manages persistence for the Aether ecosystem.
    """
    def __init__(self):
        self._init_db()

    def _get_conn(self):
        """
        Returns a thread-safe connection to the SQLite database.
        check_same_thread=False is essential for FastAPI's async/threading model.
        """
        return sqlite3.connect(DB_PATH, check_same_thread=False)

    def _init_db(self):
        """
        Initialize the SQLite database schema.
        """
        conn = self._get_conn()
        c = conn.cursor()
        
        # 1. Verified Tools (The Core Truth)
        c.execute('''CREATE TABLE IF NOT EXISTS verified_tools (
                        tool_name TEXT PRIMARY KEY,
                        last_updated TIMESTAMP,
                        trust_score REAL,
                        intent_category TEXT,
                        analysis_json TEXT,  -- Storing complex objects as JSON for MVP flexibility
                        gallery_json TEXT,
                        embedding_json TEXT,  -- Storing numpy vectors as JSON array
                        is_active INTEGER DEFAULT 1 -- 1 for active, 0 for hidden
                    )''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS scout_tasks (
                task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_name TEXT,
                url TEXT,
                submitter_email TEXT,
                status TEXT DEFAULT 'pending', -- pending, scanning, completed, failed
                error_message TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )''')
                    
        # Apply schema migration for is_active column
        try:
             c.execute("ALTER TABLE verified_tools ADD COLUMN is_active INTEGER DEFAULT 1")
        except sqlite3.OperationalError:
             pass # Column already exists
             
        # Apply schema migration if embedding_json is missing
        try:
             c.execute("ALTER TABLE verified_tools ADD COLUMN embedding_json TEXT")
        except sqlite3.OperationalError:
             pass # Column already exists

        # Migration: Add embedding_blob column for FastEmbed binary vectors
        try:
             c.execute("ALTER TABLE verified_tools ADD COLUMN embedding_blob BLOB")
        except sqlite3.OperationalError:
             pass # Column already exists

        # Migration: Add audit_pending column for Local Factory polling bridge
        try:
             c.execute("ALTER TABLE verified_tools ADD COLUMN audit_pending INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
             pass # Column already exists

        # 2. Audit History (The Trail)
        c.execute('''CREATE TABLE IF NOT EXISTS audit_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tool_name TEXT,
                        timestamp TIMESTAMP,
                        action TEXT,
                        reason TEXT,
                        score_snapshot REAL
                    )''')
        
        # 3. Search Index (Simplified for MVP - in prod use vector DB)
        c.execute('''CREATE TABLE IF NOT EXISTS search_index (
                        tool_name TEXT,
                        keyword TEXT,
                        PRIMARY KEY (tool_name, keyword)
                    )''')

        # 4. Search Analytics (New for Phase 5)
        c.execute('''CREATE TABLE IF NOT EXISTS search_queries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        query_text TEXT,
                        timestamp TIMESTAMP,
                        has_match INTEGER -- 1 for match (results found), 0 for miss
                    )''')

        # 5. User Profiles (Community)
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                        uid TEXT PRIMARY KEY,
                        email TEXT,
                        display_name TEXT,
                        points INTEGER DEFAULT 0,
                        elo INTEGER DEFAULT 1200,
                        badges_json TEXT DEFAULT '[]',
                        contributions_count INTEGER DEFAULT 0,
                        votes_count INTEGER DEFAULT 0,
                        last_active TIMESTAMP
                    )''')


        # 6. Elo Battles History
        c.execute('''CREATE TABLE IF NOT EXISTS elo_battles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tool_a TEXT,
                        tool_b TEXT,
                        winner TEXT,
                        category TEXT,
                        reason TEXT,
                        timestamp TIMESTAMP,
                        voter_uid TEXT
                    )''')
        
        # 7. Live Benchmarks (Phase 8)
        c.execute('''CREATE TABLE IF NOT EXISTS live_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tool_name TEXT,
                        provider TEXT,
                        latency_ms REAL,
                        hallucination_score REAL,
                        timestamp TIMESTAMP,
                        status TEXT,
                        comparison_vs_avg REAL
                    )''')

        # Migration: Add reason column to elo_battles if it doesn't exist
        try:
             c.execute("ALTER TABLE elo_battles ADD COLUMN reason TEXT")
        except sqlite3.OperationalError:
             pass # Column already exists

        conn.commit()
        conn.close()

    def save_tool(self, tool_name: str, analysis: LabAnalysis, trust_score: float, gallery: List[GalleryItem], audit_log: AuditLog, embedding: Optional[bytes] = None, is_active: int = 1):
        """
        Saves a fully verified tool to the Vault.
        `embedding` should be raw bytes from numpy ndarray.tobytes() (float32, 384 dims).
        """
        conn = self._get_conn()
        c = conn.cursor()
        
        timestamp = datetime.now()
        
        # Serialize complex objects
        analysis_json = analysis.json()
        
        # Protect existing gallery data if update sends an empty list
        if not gallery:
            c.execute("SELECT gallery_json FROM verified_tools WHERE tool_name = ?", (tool_name.lower(),))
            row = c.fetchone()
            if row and row[0]:
                gallery_json = row[0]
            else:
                gallery_json = "[]"
        else:
            gallery_json = json.dumps([item.dict() for item in gallery], default=str)
        
        # Handle binary embedding: keep old if new is not provided
        embedding_blob = None
        if embedding is not None:
             embedding_blob = embedding  # Already raw bytes
        else:
             c.execute("SELECT embedding_blob FROM verified_tools WHERE tool_name = ?", (tool_name.lower(),))
             row = c.fetchone()
             if row and row[0]:
                  embedding_blob = row[0]
                  
        # Upsert into Verified Tools
        c.execute('''INSERT OR REPLACE INTO verified_tools 
                     (tool_name, last_updated, trust_score, intent_category, analysis_json, gallery_json, embedding_json, embedding_blob, is_active)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (tool_name.lower(), timestamp, trust_score, str(analysis.job_to_be_done), analysis_json, gallery_json, None, embedding_blob, is_active))
        
        # Log Audit
        c.execute('''INSERT INTO audit_history (tool_name, timestamp, action, reason, score_snapshot)
                     VALUES (?, ?, ?, ?, ?)''',
                  (tool_name.lower(), timestamp, audit_log.action, audit_log.reason, audit_log.new_trust_score))
        
        # Update Search Index (Basic Keyword Mapping)
        # Clear old keywords first
        c.execute("DELETE FROM search_index WHERE tool_name = ?", (tool_name.lower(),))
        
        keywords = set(analysis.job_to_be_done + [tool_name.lower()] + analysis.tool_name.lower().split())
        for kw in keywords:
            c.execute("INSERT OR IGNORE INTO search_index (tool_name, keyword) VALUES (?, ?)", (tool_name.lower(), kw.lower()))

        conn.commit()
        conn.close()
        print(f"[Vault] Tool '{tool_name}' secured in the Vault.")
        
    def delete_tool(self, tool_name: str):
        """
        Deletes a tool and all related data from the Vault.
        """
        conn = self._get_conn()
        c = conn.cursor()
        
        tool_name_lower = tool_name.lower()
        
        # 1. Delete from search index
        c.execute("DELETE FROM search_index WHERE tool_name = ?", (tool_name_lower,))
        
        # 2. Delete from audit history
        c.execute("DELETE FROM audit_history WHERE tool_name = ?", (tool_name_lower,))
        
        # 3. Delete from verified tools
        c.execute("DELETE FROM verified_tools WHERE tool_name = ?", (tool_name_lower,))
        
        conn.commit()
        conn.close()
        print(f"[Vault] Tool '{tool_name}' and all related data purged from the Vault.")

    def update_tool_embedding(self, tool_name: str, embedding_bytes: bytes):
        """
        Updates only the binary embedding for a specific tool.
        `embedding_bytes` should be raw bytes from numpy ndarray.tobytes().
        """
        conn = self._get_conn()
        c = conn.cursor()
        
        c.execute("UPDATE verified_tools SET embedding_blob = ? WHERE tool_name = ?", (embedding_bytes, tool_name.lower()))
        
        conn.commit()
        conn.close()
        print(f"[Vault] Binary embedding saved for '{tool_name}'.")

    def get_all_embeddings(self) -> List[Tuple[str, float, np.ndarray, dict, int]]:
        """
        Bulk-loads all active tool embeddings for the search engine.
        Returns list of (tool_name, trust_score, embedding_vector, analysis_dict, is_active).
        Reconstructs numpy arrays from binary BLOB using np.frombuffer.
        """
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute("SELECT tool_name, trust_score, embedding_blob, analysis_json, is_active FROM verified_tools WHERE is_active = 1")
        rows = c.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            row_dict = dict(row)
            blob = row_dict['embedding_blob']
            if not blob:
                continue  # Skip tools without embeddings
            
            # CRITICAL: Reconstruct numpy array from raw bytes
            vector = np.frombuffer(blob, dtype=np.float32)
            analysis_json = row_dict['analysis_json']
            analysis = json.loads(analysis_json) if analysis_json else {}
            
            results.append((
                row_dict['tool_name'],
                row_dict['trust_score'],
                vector,
                analysis,
                row_dict['is_active']
            ))
        
        return results

    def get_tool(self, tool_identifier: str, include_expired: bool = False) -> Optional[Dict]:
        """
        Retrieves a tool from the Vault.
        Can query by exact tool_name or slugified id.
        """
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        # Try exact match first (Explicit columns to avoid binary blob leakage)
        c.execute("""SELECT tool_name, last_updated, trust_score, intent_category, 
                            analysis_json, gallery_json, is_active 
                     FROM verified_tools WHERE tool_name = ?""", (tool_identifier.lower(),))
        row = c.fetchone()
        
        # Try slug match if not found
        if not row:
            c.execute("""SELECT tool_name, last_updated, trust_score, intent_category, 
                                analysis_json, gallery_json, is_active 
                         FROM verified_tools WHERE replace(lower(tool_name), ' ', '-') = ?""", (tool_identifier.lower(),))
            row = c.fetchone()
            
        # Try a relaxed LIKE match if still not found
        if not row:
            search_pattern = f"%{tool_identifier.lower()}%"
            c.execute("""SELECT tool_name, last_updated, trust_score, intent_category, 
                                analysis_json, gallery_json, is_active 
                         FROM verified_tools WHERE lower(tool_name) LIKE ? LIMIT 1""", (search_pattern,))
            row = c.fetchone()
            
        conn.close()
        
        if not row:
            return None
            
        row_dict = dict(row)
            
        # Expiration Logic (90 Days - Extended for better UX / development)
        last_updated = datetime.fromisoformat(str(row_dict['last_updated']))
        if datetime.now() - last_updated > timedelta(days=90):
            if include_expired:
                print(f"[Vault] Tool '{row_dict['tool_name']}' is EXPIRED but returning anyway due to override.")
            else:
                print(f"[Vault] Tool '{row_dict['tool_name']}' found but EXPIRED. Triggering Pulse Check.")
                return None # Treat as not found to trigger re-verification
            
        # Reconstruct Data
        tool_name = row_dict['tool_name']
        slug_id = tool_name.strip().lower().replace(' ', '-')
        return {
            "id": slug_id,
            "tool_name": tool_name,
            "last_updated": row_dict['last_updated'],
            "trust_score": row_dict['trust_score'],
            "analysis": json.loads(row_dict['analysis_json']) if row_dict['analysis_json'] else {},
            "is_active": bool(row_dict['is_active']),
            "status": "success" # Implicitly success if in DB
        }

    def search_tools(self, query: str, include_inactive: bool = False) -> List[Dict]:
        """
        Searches the Vault for tools matching the query (Intent or Name).
        """
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        where_clause = " WHERE is_active = 1 " if not include_inactive else " WHERE 1=1 "
        
        if not query.strip():
            # If query is empty, return ALL tools
            c.execute(f"""SELECT tool_name, trust_score, analysis_json, gallery_json, is_active 
                         FROM verified_tools {where_clause}""")
        else:
            # Simple LIKE search on the index
            c.execute(f'''SELECT DISTINCT vt.tool_name, vt.trust_score, vt.analysis_json, vt.gallery_json, vt.is_active 
                         FROM verified_tools vt
                         JOIN search_index si ON vt.tool_name = si.tool_name
                         {where_clause.replace("WHERE", "AND")}
                         AND si.keyword LIKE ?''', (f"%{query.lower()}%",))
        
        rows = c.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            row_dict = dict(row)
            tool_name = row_dict['tool_name']
            slug_id = tool_name.strip().lower().replace(' ', '-')
            results.append({
                "id": slug_id,
                "tool_name": tool_name,
                "trust_score": row_dict['trust_score'],
                "analysis": json.loads(row_dict['analysis_json']) if row_dict['analysis_json'] else {},
                "gallery": json.loads(row_dict['gallery_json']) if row_dict['gallery_json'] else [],
                "is_active": bool(row_dict['is_active']),
            })
            
        return results

    def get_stats(self) -> Dict:
         conn = self._get_conn()
         c = conn.cursor()
         
         # count
         c.execute("SELECT COUNT(*) FROM verified_tools")
         count = c.fetchone()[0] or 0
         
         # average trust score
         c.execute("SELECT AVG(trust_score) FROM verified_tools")
         avg_score = c.fetchone()[0] or 0.0
         
         # last scan date
         c.execute("SELECT MAX(last_updated) FROM verified_tools")
         last_scan = c.fetchone()[0]
         
         # For unique intents mapped
         c.execute("SELECT analysis_json FROM verified_tools")
         rows = c.fetchall()
         
         unique_intents = set()
         for row in rows:
             if row[0]:
                 try:
                     analysis = json.loads(row[0])
                     intents = analysis.get("intents_mapped", [])
                     for intent in intents:
                         desc = intent.get("intent_description")
                         if desc:
                             unique_intents.add(desc.lower().strip())
                 except Exception:
                     pass
                     
         conn.close()
         return {
             "verified_tools_count": count,
             "total_intents_mapped": len(unique_intents),
             "last_scan_date": last_scan
         }

    # --- Phase 5: Analytics & Admin Controls ---

    def log_search(self, query_text: str, has_match: bool):
        """Logs a search query to the database."""
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("INSERT INTO search_queries (query_text, timestamp, has_match) VALUES (?, ?, ?)",
                  (query_text, datetime.now(), 1 if has_match else 0))
        conn.commit()
        conn.close()

    def get_search_analytics(self, limit: int = 50) -> List[Dict]:
        """Fetches the latest search queries for the admin dashboard."""
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM search_queries ORDER BY timestamp DESC LIMIT ?", (limit,))
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def update_tool_status(self, tool_name: str, status: int):
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("UPDATE verified_tools SET is_active = ? WHERE tool_name = ?", (status, tool_name.lower()))
        conn.commit()
        conn.close()

    def toggle_tool_status(self, tool_name: str, active: bool):
        """Toggle tool active/inactive status. Alias used by admin endpoints."""
        self.update_tool_status(tool_name, 1 if active else 0)

    def create_scout_task(self, tool_name: str, url: str, email: str) -> int:
        conn = self._get_conn()
        c = conn.cursor()
        now = datetime.now()
        c.execute("INSERT INTO scout_tasks (tool_name, url, submitter_email, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                  (tool_name, url, email, now, now))
        task_id = c.lastrowid
        conn.commit()
        conn.close()
        return task_id

    def update_scout_task(self, task_id: int, status: str, error_message: str = None, final_tool_name: str = None):
        conn = self._get_conn()
        c = conn.cursor()
        if final_tool_name:
            c.execute("UPDATE scout_tasks SET status = ?, error_message = ?, updated_at = ?, tool_name = ? WHERE task_id = ?",
                      (status, error_message, datetime.now(), final_tool_name, task_id))
        else:
            c.execute("UPDATE scout_tasks SET status = ?, error_message = ?, updated_at = ? WHERE task_id = ?",
                      (status, error_message, datetime.now(), task_id))
        conn.commit()
        conn.close()

    def get_live_scans(self) -> List[Dict]:
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        # Keep only recent tasks or non-completed ones
        c.execute("SELECT * FROM scout_tasks WHERE status IN ('pending', 'scanning', 'failed') OR (status = 'completed' AND updated_at > datetime('now', '-1 hour')) ORDER BY updated_at DESC")
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_pending_tools(self) -> List[Dict]:
        """
        Fetches all tools that are currently hidden (is_active = 0) for admin review.
        """
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""SELECT tool_name, last_updated, trust_score, analysis_json, is_active 
                     FROM verified_tools 
                     WHERE is_active = 0 
                     ORDER BY last_updated DESC""")
        rows = c.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            row_dict = dict(row)
            tool_name = row_dict['tool_name']
            slug_id = tool_name.strip().lower().replace(' ', '-')
            results.append({
                "id": slug_id,
                "tool_name": tool_name,
                "trust_score": row_dict['trust_score'],
                "analysis": json.loads(row_dict['analysis_json']) if row_dict['analysis_json'] else {},
                "last_updated": row_dict['last_updated']
            })
        return results

    def quick_update_pricing(self, tool_name: str, new_pricing: str):
        """Quickly updates the pricing model of a tool."""
        conn = self._get_conn()
        c = conn.cursor()
        
        # We need to update analysis_json to persist the pricing change
        c.execute("SELECT analysis_json FROM verified_tools WHERE tool_name = ?", (tool_name.lower(),))
        row = c.fetchone()
        if row and row[0]:
            analysis_dict = json.loads(row[0])
            analysis_dict["metrics"]["pricing"] = new_pricing
            c.execute("UPDATE verified_tools SET analysis_json = ? WHERE tool_name = ?", (json.dumps(analysis_dict), tool_name.lower()))
            conn.commit()
        
        conn.close()

    # --- Phase 6: Community & Elo Implementation ---

    def get_or_create_user(self, uid: str, email: str, display_name: Optional[str] = None) -> UserProfile:
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute("SELECT * FROM users WHERE uid = ?", (uid,))
        row = c.fetchone()
        
        if row:
            user = UserProfile(
                uid=row['uid'],
                email=row['email'],
                display_name=row['display_name'],
                points=row['points'],
                elo=row['elo'],
                badges=json.loads(row['badges_json']),
                contributions_count=row['contributions_count'],
                votes_count=row['votes_count'],
                last_active=datetime.fromisoformat(row['last_active']) if row['last_active'] else datetime.now(),
            )
            # Update last active
            c.execute("UPDATE users SET last_active = ? WHERE uid = ?", (datetime.now(), uid))
            conn.commit()
        else:
            user = UserProfile(uid=uid, email=email, display_name=display_name)
            c.execute('''INSERT INTO users (uid, email, display_name, points, elo, badges_json, last_active)
                         VALUES (?, ?, ?, ?, ?, ?, ?)''',
                      (uid, email, display_name, user.points, user.elo, json.dumps(user.badges), user.last_active))
            conn.commit()
            
        conn.close()
        return user

    def update_user(self, user: UserProfile):
        conn = self._get_conn()
        c = conn.cursor()
        c.execute('''UPDATE users SET 
                     display_name = ?, points = ?, elo = ?, badges_json = ?, 
                     contributions_count = ?, votes_count = ?, last_active = ?
                     WHERE uid = ?''',
                  (user.display_name, user.points, user.elo, json.dumps(user.badges), 
                   user.contributions_count, user.votes_count, datetime.now(), user.uid))
        conn.commit()
        conn.close()



    def get_user_rankings(self, limit: int = 10) -> List[Dict]:
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT display_name, email, points, elo, badges_json FROM users ORDER BY points DESC LIMIT ?", (limit,))
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]





    def get_vendor_insights(self, tool_name: str) -> Dict:
        """
        Gathers intelligence for a specific tool vendor.
        """
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        name_lower = tool_name.lower()
        
        # 3. Missed Searches (Market Demand)
        # We look for queries that have NO match and might be relevant to this tool's category
        c.execute("SELECT intent_category FROM verified_tools WHERE tool_name = ?", (name_lower,))
        cat_row = c.fetchone()
        tool_category = cat_row[0] if cat_row else ""
        
        c.execute('''SELECT query_text, COUNT(*) as count FROM search_queries 
                     WHERE has_match = 0 
                     GROUP BY query_text 
                     ORDER BY count DESC LIMIT 10''')
        missed_searches = [dict(r) for r in c.fetchall()]
        
        conn.close()
        
        return {
            "tool_name": tool_name,
            "missed_searches": missed_searches
        }

    # --- Phase 8: Live Benchmarking ---

    def save_live_metric(self, metric: LiveMetric):
        """
        Saves a live performance metric.
        """
        conn = self._get_conn()
        c = conn.cursor()
        c.execute('''INSERT INTO live_metrics 
                     (tool_name, provider, latency_ms, hallucination_score, timestamp, status, comparison_vs_avg)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (metric.tool_name, metric.provider, metric.latency_ms, metric.hallucination_score, 
                   metric.timestamp, metric.status, metric.comparison_vs_avg))
        conn.commit()
        conn.close()

    def get_latest_benchmarks(self, limit: int = 10) -> List[Dict]:
        """
        Fetches the latest live benchmarks for each major provider.
        """
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        # Get the latest entry for each tool_name
        c.execute('''SELECT * FROM live_metrics 
                     WHERE id IN (SELECT MAX(id) FROM live_metrics GROUP BY tool_name)
                     ORDER BY timestamp DESC LIMIT ?''', (limit,))
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def prune_live_metrics(self, hours: int = 24):
        """
        Removes metrics older than X hours to prevent database bloat.
        """
        conn = self._get_conn()
        c = conn.cursor()
        cutoff = datetime.now() - timedelta(hours=hours)
        c.execute("DELETE FROM live_metrics WHERE timestamp < ?", (cutoff,))
        conn.commit()
        conn.close()
        print(f"[Vault] Pruned metrics older than {hours} hours.")

    # --- Phase 3: Bridge Architecture ---
    
    def get_audit_pending_tools(self) -> List[Dict]:
        """Fetches all tools with audit_pending = 1 for the Local AI Factory to process."""
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""SELECT tool_name, trust_score, analysis_json 
                     FROM verified_tools 
                     WHERE audit_pending = 1""")
        rows = c.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            row_dict = dict(row)
            tool_name = row_dict['tool_name']
            slug_id = tool_name.strip().lower().replace(' ', '-')
            results.append({
                "id": slug_id,
                "tool_name": tool_name,
                "trust_score": row_dict['trust_score'],
                "analysis": json.loads(row_dict['analysis_json']) if row_dict['analysis_json'] else {}
            })
        return results

    def set_audit_pending(self, tool_id: str, pending: bool) -> bool:
        """Sets the audit_pending flag for a specific tool."""
        conn = self._get_conn()
        c = conn.cursor()
        
        # We need to find the exact tool name based on the slug tool_id or tool_name
        search_pattern = f"%{tool_id.lower()}%"
        c.execute("SELECT tool_name FROM verified_tools WHERE lower(tool_name) = ? OR replace(lower(tool_name), ' ', '-') = ?", 
                  (tool_id.lower(), tool_id.lower()))
        row = c.fetchone()
        
        if not row:
            conn.close()
            return False
            
        actual_name = row[0]
        c.execute("UPDATE verified_tools SET audit_pending = ? WHERE tool_name = ?", (1 if pending else 0, actual_name))
        conn.commit()
        conn.close()
        return True

    def apply_bridge_audit_update(self, tool_id: str, trust_score: float, executive_summary: str, 
                                  time_to_value: str, privacy_grade: str, skill_multiplier: str) -> bool:
        """Applies the structured data from the Local Factory and unsets audit_pending."""
        import re
        conn = self._get_conn()
        c = conn.cursor()
        
        c.execute("SELECT tool_name, analysis_json, gallery_json FROM verified_tools WHERE replace(lower(tool_name), ' ', '-') = ? OR lower(tool_name) = ?", 
                  (tool_id.lower(), tool_id.lower()))
        row = c.fetchone()
        
        if not row:
            conn.close()
            return False
            
        actual_name = row[0]
        analysis_json = row[1]
        gallery_json = row[2]
        
        # Update Analysis JSON
        analysis = json.loads(analysis_json) if analysis_json else {}
        analysis['executive_summary'] = executive_summary
        analysis['time_to_value'] = time_to_value
        analysis['privacy_grade'] = privacy_grade
        analysis['skill_multiplier_text'] = skill_multiplier
        
        # Purge Unsplash placeholder images from gallery
        UNSPLASH_PATTERN = re.compile(r"https?://images\.unsplash\.com/", re.IGNORECASE)
        gallery = json.loads(gallery_json) if gallery_json else []
        clean_gallery = [g for g in gallery if not UNSPLASH_PATTERN.search(g.get('media_url', ''))]
        
        c.execute("""UPDATE verified_tools 
                     SET trust_score = ?, 
                         analysis_json = ?, 
                         gallery_json = ?, 
                         audit_pending = 0,
                         last_updated = ?
                     WHERE tool_name = ?""",
                  (trust_score, json.dumps(analysis), json.dumps(clean_gallery), datetime.now(), actual_name))
                  
        # Add to audit history
        c.execute("""INSERT INTO audit_history (tool_name, timestamp, action, reason, score_snapshot)
                     VALUES (?, ?, ?, ?, ?)""",
                  (actual_name, datetime.now(), "Factory Audit - Phase 3 (Bridge)", "Automated re-audit via Worker Polling", trust_score))
        
        conn.commit()
        conn.close()
        return True
