import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
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

    def _init_db(self):
        """
        Initialize the SQLite database schema.
        """
        conn = sqlite3.connect(DB_PATH)
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
                        last_active TIMESTAMP,
                        is_pro INTEGER DEFAULT 0
                    )''')

        # Migration: Add is_pro column to users if it doesn't exist
        try:
             c.execute("ALTER TABLE users ADD COLUMN is_pro INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
             pass # Column already exists

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

    def save_tool(self, tool_name: str, analysis: LabAnalysis, trust_score: float, gallery: List[GalleryItem], audit_log: AuditLog, embedding: Optional[List[float]] = None):
        """
        Saves a fully verified tool to the Vault.

        """
        conn = sqlite3.connect(DB_PATH)
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
        
        # Handle embeddings: keep old if new is not provided
        embedding_json = None
        if embedding is not None:
             embedding_json = json.dumps(embedding)
        else:
             c.execute("SELECT embedding_json FROM verified_tools WHERE tool_name = ?", (tool_name.lower(),))
             row = c.fetchone()
             if row and row[0]:
                  embedding_json = row[0]
                  
        # Upsert into Verified Tools
        c.execute('''INSERT OR REPLACE INTO verified_tools 
                     (tool_name, last_updated, trust_score, intent_category, analysis_json, gallery_json, embedding_json)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (tool_name.lower(), timestamp, trust_score, str(analysis.job_to_be_done), analysis_json, gallery_json, embedding_json))
        
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
        conn = sqlite3.connect(DB_PATH)
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

    def update_tool_embedding(self, tool_name: str, embedding: List[float]):
        """
        Updates only the embedding for a specific tool.
        """
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        embedding_json = json.dumps(embedding)
        c.execute("UPDATE verified_tools SET embedding_json = ? WHERE tool_name = ?", (embedding_json, tool_name.lower()))
        
        conn.commit()
        conn.close()
        print(f"[Vault] Embedded vector saved for '{tool_name}'.")

    def get_tool(self, tool_identifier: str, include_expired: bool = False) -> Optional[Dict]:
        """
        Retrieves a tool from the Vault.
        Can query by exact tool_name or slugified id.
        """
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        # Try exact match first
        c.execute("SELECT * FROM verified_tools WHERE tool_name = ?", (tool_identifier.lower(),))
        row = c.fetchone()
        
        # Try slug match if not found
        if not row:
            c.execute("SELECT * FROM verified_tools WHERE replace(lower(tool_name), ' ', '-') = ?", (tool_identifier.lower(),))
            row = c.fetchone()
            
        # Try a relaxed LIKE match if still not found (e.g. "claude" -> "claude 3")
        if not row:
            search_pattern = f"%{tool_identifier.lower()}%"
            c.execute("SELECT * FROM verified_tools WHERE lower(tool_name) LIKE ? LIMIT 1", (search_pattern,))
            row = c.fetchone()
            
        conn.close()
        
        if not row:
            return None
            
        # Expiration Logic (7 Days)
        last_updated = datetime.fromisoformat(str(row['last_updated']))
        if datetime.now() - last_updated > timedelta(days=7):
            if include_expired:
                print(f"[Vault] Tool '{row['tool_name']}' is EXPIRED but returning anyway due to override.")
            else:
                print(f"[Vault] Tool '{row['tool_name']}' found but EXPIRED. Triggering Pulse Check.")
                return None # Treat as not found to trigger re-verification
            
        # Reconstruct Data
        slug_id = row['tool_name'].strip().lower().replace(' ', '-')
        return {
            "id": slug_id,
            "tool_name": row['tool_name'],
            "last_updated": row['last_updated'],
            "trust_score": row['trust_score'],
            "analysis": json.loads(row['analysis_json']),
            "embedding": json.loads(row['embedding_json']) if 'embedding_json' in row.keys() and row['embedding_json'] else None,
            "is_active": bool(row['is_active']),
            "status": "success" # Implicitly success if in DB
        }

    def search_tools(self, query: str, include_inactive: bool = False) -> List[Dict]:
        """
        Searches the Vault for tools matching the query (Intent or Name).
        """
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        where_clause = " WHERE is_active = 1 " if not include_inactive else " WHERE 1=1 "
        
        if not query.strip():
            # If query is empty, return ALL tools
            c.execute(f'SELECT * FROM verified_tools {where_clause}')
        else:
            # Simple LIKE search on the index
            c.execute(f'''SELECT DISTINCT vt.* FROM verified_tools vt
                         JOIN search_index si ON vt.tool_name = si.tool_name
                         {where_clause.replace("WHERE", "AND")}
                         AND si.keyword LIKE ?''', (f"%{query.lower()}%",))
        
        rows = c.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            slug_id = row['tool_name'].strip().lower().replace(' ', '-')
            results.append({
                "id": slug_id,
                "tool_name": row['tool_name'],
                "trust_score": row['trust_score'],
                "analysis": json.loads(row['analysis_json']),
                "gallery": json.loads(row['gallery_json']),
                "embedding": json.loads(row['embedding_json']) if 'embedding_json' in row.keys() and row['embedding_json'] else None,
                "is_active": bool(row['is_active']),
            })
            
        return results

    def get_stats(self) -> Dict:
         conn = sqlite3.connect(DB_PATH)
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
             "total_intents_mapped": len(unique_intents),
             "last_scan_date": last_scan
         }

    # --- Phase 5: Analytics & Admin Controls ---

    def log_search(self, query_text: str, has_match: bool):
        """Logs a search query to the database."""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO search_queries (query_text, timestamp, has_match) VALUES (?, ?, ?)",
                  (query_text, datetime.now(), 1 if has_match else 0))
        conn.commit()
        conn.close()

    def get_search_analytics(self, limit: int = 50) -> List[Dict]:
        """Fetches the latest search queries for the admin dashboard."""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM search_queries ORDER BY timestamp DESC LIMIT ?", (limit,))
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def toggle_tool_status(self, tool_name: str, is_active: bool):
        """Enables or disables a tool (Kill Switch)."""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE verified_tools SET is_active = ? WHERE tool_name = ?", (1 if is_active else 0, tool_name.lower()))
        conn.commit()
        conn.close()
        print(f"[Vault] Tool '{tool_name}' set to active={is_active}")

    def quick_update_pricing(self, tool_name: str, new_pricing: str):
        """Quickly updates the pricing model of a tool."""
        conn = sqlite3.connect(DB_PATH)
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
        print(f"[Vault] Tool '{tool_name}' pricing updated to: {new_pricing}")

    # --- Phase 6: Community & Elo Implementation ---

    def get_or_create_user(self, uid: str, email: str, display_name: Optional[str] = None) -> UserProfile:
        conn = sqlite3.connect(DB_PATH)
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
                is_pro=bool(row['is_pro']) if 'is_pro' in row.keys() else False
            )
            # Update last active
            c.execute("UPDATE users SET last_active = ? WHERE uid = ?", (datetime.now(), uid))
            conn.commit()
        else:
            user = UserProfile(uid=uid, email=email, display_name=display_name)
            c.execute('''INSERT INTO users (uid, email, display_name, points, elo, badges_json, last_active, is_pro)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                      (uid, email, display_name, user.points, user.elo, json.dumps(user.badges), user.last_active, 1 if user.is_pro else 0))
            conn.commit()
            
        conn.close()
        return user

    def update_user(self, user: UserProfile):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''UPDATE users SET 
                     display_name = ?, points = ?, elo = ?, badges_json = ?, 
                     contributions_count = ?, votes_count = ?, last_active = ?, is_pro = ?
                     WHERE uid = ?''',
                  (user.display_name, user.points, user.elo, json.dumps(user.badges), 
                   user.contributions_count, user.votes_count, datetime.now(), 1 if user.is_pro else 0, user.uid))
        conn.commit()
        conn.close()

    def record_vote(self, voter_uid: str, tool_a: str, tool_b: str, winner: str, category: str, reason: Optional[str] = None):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''INSERT INTO elo_battles (tool_a, tool_b, winner, category, reason, timestamp, voter_uid)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (tool_a.lower(), tool_b.lower(), winner.lower(), category, reason, datetime.now(), voter_uid))
        
        # Also increment user vote count
        c.execute("UPDATE users SET votes_count = votes_count + 1, points = points + 10 WHERE uid = ?", (voter_uid,))
        
        conn.commit()
        conn.close()

    def get_user_rankings(self, limit: int = 10) -> List[Dict]:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT display_name, email, points, elo, badges_json FROM users ORDER BY points DESC LIMIT ?", (limit,))
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_random_tool_pair(self, category: Optional[str] = None) -> List[Dict]:
        """Gets two random tools for a battle."""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        if category:
            c.execute("SELECT * FROM verified_tools WHERE is_active = 1 AND intent_category LIKE ? ORDER BY RANDOM() LIMIT 2", (f"%{category}%",))
        else:
            c.execute("SELECT * FROM verified_tools WHERE is_active = 1 ORDER BY RANDOM() LIMIT 2")
            
        rows = c.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                "tool_name": row['tool_name'],
                "analysis": json.loads(row['analysis_json']),
                "trust_score": row['trust_score']
            })
        return results

    def update_tool_trust_score(self, tool_name: str, new_trust_score: float, reason: str = "Elo Battle Update"):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE verified_tools SET trust_score = ?, last_updated = ? WHERE tool_name = ?", 
                  (new_trust_score, datetime.now(), tool_name.lower()))
        
        # Log to audit history
        c.execute('''INSERT INTO audit_history (tool_name, timestamp, action, reason, score_snapshot)
                     VALUES (?, ?, ?, ?, ?)''',
                  (tool_name.lower(), datetime.now(), "Score Updated", reason, new_trust_score))
        
        conn.commit()
        conn.close()
        print(f"[Vault] Tool '{tool_name}' Trust Score updated to {new_trust_score} due to {reason}.")

    def get_vendor_insights(self, tool_name: str) -> Dict:
        """
        Gathers intelligence for a specific tool vendor.
        """
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        name_lower = tool_name.lower()
        
        # 1. Battle Stats
        c.execute("SELECT COUNT(*) FROM elo_battles WHERE tool_a = ? OR tool_b = ?", (name_lower, name_lower))
        total_battles = c.fetchone()[0] or 0
        
        c.execute("SELECT COUNT(*) FROM elo_battles WHERE winner = ?", (name_lower,))
        wins = c.fetchone()[0] or 0
        
        win_rate = (wins / total_battles * 100) if total_battles > 0 else 0
        
        # 2. Loss Reasons (Intelligence)
        c.execute('''SELECT reason, winner, timestamp FROM elo_battles 
                     WHERE (tool_a = ? OR tool_b = ?) AND winner != ? AND winner != 'draw' AND reason IS NOT NULL
                     ORDER BY timestamp DESC LIMIT 20''', (name_lower, name_lower, name_lower))
        loss_reasons = [dict(r) for r in c.fetchall()]

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
        
        # 4. Competitor Comparison
        # Find tools that often win against this tool
        c.execute('''SELECT winner as competitor, COUNT(*) as win_count FROM elo_battles 
                     WHERE (tool_a = ? OR tool_b = ?) AND winner != ? AND winner != 'draw'
                     GROUP BY winner 
                     ORDER BY win_count DESC LIMIT 5''', (name_lower, name_lower, name_lower))
        competitors = [dict(r) for r in c.fetchall()]
        
        conn.close()
        
        return {
            "tool_name": tool_name,
            "total_battles": total_battles,
            "win_rate": round(win_rate, 2),
            "loss_reasons": loss_reasons,
            "missed_searches": missed_searches,
            "competitor_comparison": competitors
        }

    # --- Phase 8: Live Benchmarking ---

    def save_live_metric(self, metric: LiveMetric):
        """
        Saves a live performance metric.
        """
        conn = sqlite3.connect(DB_PATH)
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
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        # Get the latest entry for each tool_name
        c.execute('''SELECT * FROM live_metrics 
                     WHERE id IN (SELECT MAX(id) FROM live_metrics GROUP BY tool_name)
                     ORDER BY timestamp DESC LIMIT ?''', (limit,))
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]
