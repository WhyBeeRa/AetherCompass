import psycopg2
import psycopg2.extras
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any, Tuple
from models import AuditLog, LabAnalysis, GalleryItem, TrustScore, UserProfile, Badge, LiveMetric
import os
from pgvector.psycopg2 import register_vector

# Database Connection URI
DATABASE_URL = os.environ.get(
    "DATABASE_URL", 
    "postgresql://aether_user:aether_password@localhost:5432/aether_db"
)


class AetherVault:
    """
    The Memory Layer.
    Manages persistence for the Aether ecosystem using PostgreSQL + pgvector.
    """
    def __init__(self):
        self._init_db()

    def _get_conn(self):
        """
        Returns a connection to the PostgreSQL database.
        Registers pgvector support on it.
        """
        conn = psycopg2.connect(DATABASE_URL)
        register_vector(conn)
        return conn

    def _init_db(self):
        """
        Initialize the PostgreSQL database schema.
        Creates pgvector extension first.
        """
        # First connection to ensure extension exists
        conn = psycopg2.connect(DATABASE_URL)
        c = conn.cursor()
        try:
            c.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"[Vault] Failed to create vector extension: {e}")
        finally:
            conn.close()

        # Reconnect to build tables (now vector extension is loaded, we can use _get_conn)
        conn = self._get_conn()
        c = conn.cursor()
        
        # 1. Verified Tools (The Core Truth)
        c.execute('''CREATE TABLE IF NOT EXISTS verified_tools (
                        tool_name TEXT PRIMARY KEY,
                        last_updated TIMESTAMP,
                        trust_score REAL,
                        intent_category TEXT,
                        analysis_json TEXT,  -- JSON string
                        gallery_json TEXT,
                        embedding_json TEXT,  -- JSON string array (unused)
                        embedding_blob BYTEA,  -- float32 bytes representation
                        is_active INTEGER DEFAULT 1, -- 1 for active, 0 for hidden
                        audit_pending INTEGER DEFAULT 0,
                        embedding vector(768)  -- pgvector column
                    )''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS scout_tasks (
                        task_id SERIAL PRIMARY KEY,
                        tool_name TEXT,
                        url TEXT,
                        submitter_email TEXT,
                        status TEXT DEFAULT 'pending', -- pending, scanning, completed, failed
                        error_message TEXT,
                        created_at TIMESTAMP,
                        updated_at TIMESTAMP
                    )''')

        # 2. Audit History (The Trail)
        c.execute('''CREATE TABLE IF NOT EXISTS audit_history (
                        id SERIAL PRIMARY KEY,
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

        # 4. Search Analytics
        c.execute('''CREATE TABLE IF NOT EXISTS search_queries (
                        id SERIAL PRIMARY KEY,
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
                        id SERIAL PRIMARY KEY,
                        tool_a TEXT,
                        tool_b TEXT,
                        winner TEXT,
                        category TEXT,
                        reason TEXT,
                        timestamp TIMESTAMP,
                        voter_uid TEXT
                    )''')
        
        # 7. Live Benchmarks
        c.execute('''CREATE TABLE IF NOT EXISTS live_metrics (
                        id SERIAL PRIMARY KEY,
                        tool_name TEXT,
                        provider TEXT,
                        latency_ms REAL,
                        hallucination_score REAL,
                        timestamp TIMESTAMP,
                        status TEXT,
                        comparison_vs_avg REAL
                    )''')

        # 8. Sentinel Settings
        c.execute('''CREATE TABLE IF NOT EXISTS sentinel_settings (
                        id INTEGER PRIMARY KEY DEFAULT 1,
                        enabled INTEGER DEFAULT 0,
                        alert_email TEXT DEFAULT '',
                        frequency_minutes INTEGER DEFAULT 30,
                        failure_threshold INTEGER DEFAULT 3,
                        current_failures INTEGER DEFAULT 0,
                        last_run_timestamp TIMESTAMP,
                        last_status TEXT DEFAULT 'PENDING'
                    )''')
        
        # Seed default settings row if missing
        c.execute("""INSERT INTO sentinel_settings (id, enabled, alert_email, frequency_minutes, failure_threshold, current_failures) 
                     VALUES (1, 0, '', 30, 3, 0)
                     ON CONFLICT (id) DO NOTHING""")

        # 9. Sentinel Audit Logs
        c.execute('''CREATE TABLE IF NOT EXISTS sentinel_audit_logs (
                        id SERIAL PRIMARY KEY,
                        timestamp TIMESTAMP,
                        status TEXT,
                        message TEXT,
                        database_status TEXT,
                        memory_usage_mb REAL,
                        email_sent INTEGER DEFAULT 0
                    )''')

        # 10. Semantic Cache Table
        c.execute('''CREATE TABLE IF NOT EXISTS semantic_cache (
                        id SERIAL PRIMARY KEY,
                        query_text TEXT UNIQUE,
                        embedding_blob BYTEA,
                        tool_name TEXT,
                        timestamp TIMESTAMP
                    )''')

        # 11. Vector HNSW Index for pgvector
        c.execute('''CREATE INDEX IF NOT EXISTS verified_tools_embedding_hnsw_idx 
                     ON verified_tools USING hnsw (embedding vector_cosine_ops);''')

        # 12. Staging Tools (Ingestion Pipeline)
        c.execute('''CREATE TABLE IF NOT EXISTS staging_tools (
                        id SERIAL PRIMARY KEY,
                        tool_name TEXT UNIQUE,
                        source TEXT DEFAULT 'bulk_seed',
                        raw_data TEXT,
                        processed_data TEXT,
                        trust_score REAL DEFAULT 0,
                        category TEXT,
                        embedding vector(768),
                        embedding_blob BYTEA,
                        processing_status TEXT DEFAULT 'pending',
                        processing_log TEXT DEFAULT '',
                        ingested_at TIMESTAMP,
                        processed_at TIMESTAMP,
                        reviewed_at TIMESTAMP,
                        reviewer_notes TEXT
                    )''')

        conn.commit()
        conn.close()

    def save_tool(self, tool_name: str, analysis: LabAnalysis, trust_score: float, gallery: List[GalleryItem], audit_log: AuditLog, embedding: Optional[bytes] = None, is_active: int = 1):
        """
        Saves a fully verified tool to the Vault.
        `embedding` should be raw bytes from numpy ndarray.tobytes() (float32, 768 dims).
        """
        conn = self._get_conn()
        c = conn.cursor()
        
        timestamp = datetime.now()
        
        # Serialize complex objects
        analysis_json = analysis.json()
        
        # Protect existing gallery data if update sends an empty list
        if not gallery:
            c.execute("SELECT gallery_json FROM verified_tools WHERE tool_name = %s", (tool_name.lower(),))
            row = c.fetchone()
            if row and row[0]:
                gallery_json = row[0]
            else:
                gallery_json = "[]"
        else:
            gallery_json = json.dumps([item.dict() for item in gallery], default=str)
        
        # Handle binary embedding & pgvector: keep old if new is not provided
        embedding_blob = None
        embedding_vector = None
        if embedding is not None:
             embedding_blob = embedding  # Already raw bytes
             embedding_vector = np.frombuffer(embedding, dtype=np.float32).tolist()
        else:
             c.execute("SELECT embedding_blob FROM verified_tools WHERE tool_name = %s", (tool_name.lower(),))
             row = c.fetchone()
             if row and row[0]:
                  embedding_blob = bytes(row[0])
                  embedding_vector = np.frombuffer(embedding_blob, dtype=np.float32).tolist()
                   
        # Upsert into Verified Tools using ON CONFLICT for PostgreSQL
        c.execute('''INSERT INTO verified_tools 
                     (tool_name, last_updated, trust_score, intent_category, analysis_json, gallery_json, embedding_json, embedding_blob, is_active, embedding)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                     ON CONFLICT (tool_name) DO UPDATE SET
                         last_updated = EXCLUDED.last_updated,
                         trust_score = EXCLUDED.trust_score,
                         intent_category = EXCLUDED.intent_category,
                         analysis_json = EXCLUDED.analysis_json,
                         gallery_json = EXCLUDED.gallery_json,
                         embedding_json = EXCLUDED.embedding_json,
                         embedding_blob = EXCLUDED.embedding_blob,
                         is_active = EXCLUDED.is_active,
                         embedding = EXCLUDED.embedding''',
                  (tool_name.lower(), timestamp, trust_score, str(analysis.job_to_be_done), analysis_json, gallery_json, None, psycopg2.Binary(embedding_blob) if embedding_blob else None, is_active, embedding_vector))
        
        # Log Audit
        c.execute('''INSERT INTO audit_history (tool_name, timestamp, action, reason, score_snapshot)
                     VALUES (%s, %s, %s, %s, %s)''',
                  (tool_name.lower(), timestamp, audit_log.action, audit_log.reason, audit_log.new_trust_score))
        
        # Update Search Index (Basic Keyword Mapping)
        # Clear old keywords first
        c.execute("DELETE FROM search_index WHERE tool_name = %s", (tool_name.lower(),))
        
        keywords = set(analysis.job_to_be_done + [tool_name.lower()] + analysis.tool_name.lower().split())
        for kw in keywords:
            c.execute("""INSERT INTO search_index (tool_name, keyword) VALUES (%s, %s) 
                         ON CONFLICT (tool_name, keyword) DO NOTHING""", (tool_name.lower(), kw.lower()))

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
        c.execute("DELETE FROM search_index WHERE tool_name = %s", (tool_name_lower,))
        
        # 2. Delete from audit history
        c.execute("DELETE FROM audit_history WHERE tool_name = %s", (tool_name_lower,))
        
        # 3. Delete from semantic cache
        c.execute("DELETE FROM semantic_cache WHERE tool_name = %s", (tool_name_lower,))
        
        # 4. Delete from verified tools
        c.execute("DELETE FROM verified_tools WHERE tool_name = %s", (tool_name_lower,))
        
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
        
        vector = np.frombuffer(embedding_bytes, dtype=np.float32).tolist()
        c.execute("UPDATE verified_tools SET embedding_blob = %s, embedding = %s WHERE tool_name = %s", 
                  (psycopg2.Binary(embedding_bytes), vector, tool_name.lower()))
        
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
        c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        c.execute("SELECT tool_name, trust_score, embedding_blob, analysis_json, is_active FROM verified_tools WHERE is_active = 1")
        rows = c.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            blob = row['embedding_blob']
            if not blob:
                continue  # Skip tools without embeddings
            
            # CRITICAL: Reconstruct numpy array from bytes
            vector = np.frombuffer(bytes(blob), dtype=np.float32)
            analysis_json = row['analysis_json']
            analysis = json.loads(analysis_json) if analysis_json else {}
            
            results.append((
                row['tool_name'],
                row['trust_score'],
                vector,
                analysis,
                row['is_active']
            ))
        
        return results

    def save_semantic_cache(self, query_text: str, embedding_bytes: bytes, tool_name: str):
        """
        Saves a query and its embedding to the semantic cache.
        """
        conn = self._get_conn()
        c = conn.cursor()
        timestamp = datetime.now()
        try:
            c.execute('''INSERT INTO semantic_cache 
                         (query_text, embedding_blob, tool_name, timestamp)
                         VALUES (%s, %s, %s, %s)
                         ON CONFLICT (query_text) DO UPDATE SET 
                         embedding_blob = EXCLUDED.embedding_blob,
                         tool_name = EXCLUDED.tool_name,
                         timestamp = EXCLUDED.timestamp''',
                      (query_text.strip().lower(), psycopg2.Binary(embedding_bytes), tool_name.lower(), timestamp))
            conn.commit()
            print(f"[Vault] Semantic cache saved for query '{query_text}' -> tool '{tool_name}'.")
        except Exception as e:
            print(f"[Vault Error] Failed to save semantic cache: {e}")
        finally:
            conn.close()

    def get_all_semantic_cache(self) -> List[Tuple[str, np.ndarray, str]]:
        """
        Loads all semantic cache entries.
        Returns list of (query_text, embedding_vector, tool_name).
        """
        conn = self._get_conn()
        c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        c.execute("SELECT query_text, embedding_blob, tool_name FROM semantic_cache")
        rows = c.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            blob = row['embedding_blob']
            if not blob:
                continue
            vector = np.frombuffer(bytes(blob), dtype=np.float32)
            results.append((
                row['query_text'],
                vector,
                row['tool_name']
            ))
        return results

    def get_tool(self, tool_identifier: str, include_expired: bool = False) -> Optional[Dict]:
        """
        Retrieves a tool from the Vault.
        Can query by exact tool_name or slugified id.
        """
        conn = self._get_conn()
        c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Try exact match first (Explicit columns to avoid binary blob leakage)
        c.execute("""SELECT tool_name, last_updated, trust_score, intent_category, 
                            analysis_json, gallery_json, is_active 
                     FROM verified_tools WHERE tool_name = %s""", (tool_identifier.lower(),))
        row = c.fetchone()
        
        # Try slug match if not found
        if not row:
            c.execute("""SELECT tool_name, last_updated, trust_score, intent_category, 
                                analysis_json, gallery_json, is_active 
                         FROM verified_tools WHERE replace(lower(tool_name), ' ', '-') = %s""", (tool_identifier.lower(),))
            row = c.fetchone()
            
        # Try a relaxed LIKE match if still not found
        if not row:
            search_pattern = f"%{tool_identifier.lower()}%"
            c.execute("""SELECT tool_name, last_updated, trust_score, intent_category, 
                                analysis_json, gallery_json, is_active 
                         FROM verified_tools WHERE lower(tool_name) LIKE %s LIMIT 1""", (search_pattern,))
            row = c.fetchone()
            
        conn.close()
        
        if not row:
            return None
            
        # Expiration Logic (90 Days)
        last_updated = row['last_updated']
        if datetime.now() - last_updated > timedelta(days=90):
            if include_expired:
                print(f"[Vault] Tool '{row['tool_name']}' is EXPIRED but returning anyway due to override.")
            else:
                print(f"[Vault] Tool '{row['tool_name']}' found but EXPIRED. Triggering Pulse Check.")
                return None # Treat as not found to trigger re-verification
            
        # Reconstruct Data
        tool_name = row['tool_name']
        slug_id = tool_name.strip().lower().replace(' ', '-')
        return {
            "id": slug_id,
            "tool_name": tool_name,
            "last_updated": row['last_updated'].isoformat(),
            "trust_score": row['trust_score'],
            "analysis": json.loads(row['analysis_json']) if row['analysis_json'] else {},
            "gallery": json.loads(row['gallery_json']) if row['gallery_json'] else [],
            "is_active": bool(row['is_active']),
            "status": "success" # Implicitly success if in DB
        }

    def search_tools(self, query: str, include_inactive: bool = False) -> List[Dict]:
        """
        Searches the Vault for tools matching the query (Intent or Name).
        """
        conn = self._get_conn()
        c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        where_clause = " WHERE is_active = 1 " if not include_inactive else " WHERE 1=1 "
        
        if not query.strip():
            # If query is empty, return ALL tools
            c.execute(f"""SELECT tool_name, trust_score, analysis_json, gallery_json, is_active 
                         FROM verified_tools {where_clause}""")
        else:
            # Simple LIKE search on the index
            and_clause = " AND is_active = 1 " if not include_inactive else ""
            c.execute(f'''SELECT DISTINCT vt.tool_name, vt.trust_score, vt.analysis_json, vt.gallery_json, vt.is_active 
                         FROM verified_tools vt
                         JOIN search_index si ON vt.tool_name = si.tool_name
                         WHERE si.keyword LIKE %s {and_clause}''', (f"%{query.lower()}%",))
        
        rows = c.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            tool_name = row['tool_name']
            slug_id = tool_name.strip().lower().replace(' ', '-')
            results.append({
                "id": slug_id,
                "tool_name": tool_name,
                "trust_score": row['trust_score'],
                "analysis": json.loads(row['analysis_json']) if row['analysis_json'] else {},
                "gallery": json.loads(row['gallery_json']) if row['gallery_json'] else [],
                "is_active": bool(row['is_active']),
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
             "last_scan_date": last_scan.isoformat() if last_scan else None
         }

    # --- Phase 5: Analytics & Admin Controls ---

    def log_search(self, query_text: str, has_match: bool):
        """Logs a search query to the database."""
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("INSERT INTO search_queries (query_text, timestamp, has_match) VALUES (%s, %s, %s)",
                  (query_text, datetime.now(), 1 if has_match else 0))
        conn.commit()
        conn.close()

    def get_search_analytics(self, limit: int = 50) -> List[Dict]:
        """Fetches the latest search queries for the admin dashboard."""
        conn = self._get_conn()
        c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        c.execute("SELECT id, query_text, timestamp, has_match FROM search_queries ORDER BY timestamp DESC LIMIT %s", (limit,))
        rows = c.fetchall()
        conn.close()
        
        results = []
        for r in rows:
            d = dict(r)
            if d.get('timestamp'):
                d['timestamp'] = d['timestamp'].isoformat()
            results.append(d)
        return results

    def update_tool_status(self, tool_name: str, status: int):
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("UPDATE verified_tools SET is_active = %s WHERE tool_name = %s", (status, tool_name.lower()))
        conn.commit()
        conn.close()

    def toggle_tool_status(self, tool_name: str, active: bool):
        """Toggle tool active/inactive status. Alias used by admin endpoints."""
        self.update_tool_status(tool_name, 1 if active else 0)

    def create_scout_task(self, tool_name: str, url: str, email: str) -> int:
        conn = self._get_conn()
        c = conn.cursor()
        now = datetime.now()
        c.execute("INSERT INTO scout_tasks (tool_name, url, submitter_email, created_at, updated_at) VALUES (%s, %s, %s, %s, %s) RETURNING task_id",
                  (tool_name, url, email, now, now))
        task_id = c.fetchone()[0]
        conn.commit()
        conn.close()
        return task_id

    def update_scout_task(self, task_id: int, status: str, error_message: str = None, final_tool_name: str = None):
        conn = self._get_conn()
        c = conn.cursor()
        if final_tool_name:
            c.execute("UPDATE scout_tasks SET status = %s, error_message = %s, updated_at = %s, tool_name = %s WHERE task_id = %s",
                      (status, error_message, datetime.now(), final_tool_name, task_id))
        else:
            c.execute("UPDATE scout_tasks SET status = %s, error_message = %s, updated_at = %s WHERE task_id = %s",
                      (status, error_message, datetime.now(), task_id))
        conn.commit()
        conn.close()

    def get_live_scans(self) -> List[Dict]:
        conn = self._get_conn()
        c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        c.execute("SELECT * FROM scout_tasks WHERE status IN ('pending', 'scanning', 'failed') OR (status = 'completed' AND updated_at > NOW() - INTERVAL '1 hour') ORDER BY updated_at DESC")
        rows = c.fetchall()
        conn.close()
        
        results = []
        for r in rows:
            d = dict(r)
            if d.get('created_at'):
                d['created_at'] = d['created_at'].isoformat()
            if d.get('updated_at'):
                d['updated_at'] = d['updated_at'].isoformat()
            results.append(d)
        return results

    def get_pending_tools(self) -> List[Dict]:
        """
        Fetches all tools that are currently hidden (is_active = 0) for admin review.
        """
        conn = self._get_conn()
        c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        c.execute("""SELECT tool_name, last_updated, trust_score, analysis_json, is_active 
                     FROM verified_tools 
                     WHERE is_active = 0 
                     ORDER BY last_updated DESC""")
        rows = c.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            tool_name = row['tool_name']
            slug_id = tool_name.strip().lower().replace(' ', '-')
            results.append({
                "id": slug_id,
                "tool_name": tool_name,
                "trust_score": row['trust_score'],
                "analysis": json.loads(row['analysis_json']) if row['analysis_json'] else {},
                "last_updated": row['last_updated'].isoformat() if row['last_updated'] else None
            })
        return results

    def quick_update_pricing(self, tool_name: str, new_pricing: str):
        """Quickly updates the pricing model of a tool."""
        conn = self._get_conn()
        c = conn.cursor()
        
        c.execute("SELECT analysis_json FROM verified_tools WHERE tool_name = %s", (tool_name.lower(),))
        row = c.fetchone()
        if row and row[0]:
            analysis_dict = json.loads(row[0])
            analysis_dict["metrics"]["pricing"] = new_pricing
            c.execute("UPDATE verified_tools SET analysis_json = %s WHERE tool_name = %s", (json.dumps(analysis_dict), tool_name.lower()))
            conn.commit()
        
        conn.close()

    # --- Phase 6: Community & Elo Implementation ---

    def get_or_create_user(self, uid: str, email: str, display_name: Optional[str] = None) -> UserProfile:
        conn = self._get_conn()
        c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        c.execute("SELECT * FROM users WHERE uid = %s", (uid,))
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
                last_active=row['last_active'] if row['last_active'] else datetime.now(),
            )
            # Update last active
            c.execute("UPDATE users SET last_active = %s WHERE uid = %s", (datetime.now(), uid))
            conn.commit()
        else:
            user = UserProfile(uid=uid, email=email, display_name=display_name)
            c.execute('''INSERT INTO users (uid, email, display_name, points, elo, badges_json, last_active)
                         VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                      (uid, email, display_name, user.points, user.elo, json.dumps(user.badges), user.last_active))
            conn.commit()
            
        conn.close()
        return user

    def update_user(self, user: UserProfile):
        conn = self._get_conn()
        c = conn.cursor()
        c.execute('''UPDATE users SET 
                     display_name = %s, points = %s, elo = %s, badges_json = %s, 
                     contributions_count = %s, votes_count = %s, last_active = %s
                     WHERE uid = %s''',
                  (user.display_name, user.points, user.elo, json.dumps(user.badges), 
                   user.contributions_count, user.votes_count, datetime.now(), user.uid))
        conn.commit()
        conn.close()

    def get_user_rankings(self, limit: int = 10) -> List[Dict]:
        conn = self._get_conn()
        c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        c.execute("SELECT display_name, email, points, elo, badges_json FROM users ORDER BY points DESC LIMIT %s", (limit,))
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_vendor_insights(self, tool_name: str) -> Dict:
        """
        Gathers intelligence for a specific tool vendor.
        """
        conn = self._get_conn()
        c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        name_lower = tool_name.lower()
        
        c.execute("SELECT intent_category FROM verified_tools WHERE tool_name = %s", (name_lower,))
        cat_row = c.fetchone()
        
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
                     VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                  (metric.tool_name, metric.provider, metric.latency_ms, metric.hallucination_score, 
                   metric.timestamp, metric.status, metric.comparison_vs_avg))
        conn.commit()
        conn.close()

    def get_latest_benchmarks(self, limit: int = 10) -> List[Dict]:
        """
        Fetches the latest live benchmarks for each major provider.
        """
        conn = self._get_conn()
        c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        # Get the latest entry for each tool_name
        c.execute('''SELECT * FROM live_metrics 
                     WHERE id IN (SELECT MAX(id) FROM live_metrics GROUP BY tool_name)
                     ORDER BY timestamp DESC LIMIT %s''', (limit,))
        rows = c.fetchall()
        conn.close()
        
        results = []
        for r in rows:
            d = dict(r)
            if d.get('timestamp'):
                d['timestamp'] = d['timestamp'].isoformat()
            results.append(d)
        return results

    def prune_live_metrics(self, hours: int = 24):
        """
        Removes metrics older than X hours to prevent database bloat.
        """
        conn = self._get_conn()
        c = conn.cursor()
        cutoff = datetime.now() - timedelta(hours=hours)
        c.execute("DELETE FROM live_metrics WHERE timestamp < %s", (cutoff,))
        conn.commit()
        conn.close()
        print(f"[Vault] Pruned metrics older than {hours} hours.")

    # --- Phase 3: Bridge Architecture ---
    
    def get_audit_pending_tools(self) -> List[Dict]:
        """Fetches all tools with audit_pending = 1 for the Local AI Factory to process."""
        conn = self._get_conn()
        c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        c.execute("""SELECT tool_name, trust_score, analysis_json 
                     FROM verified_tools 
                     WHERE audit_pending = 1""")
        rows = c.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            tool_name = row['tool_name']
            slug_id = tool_name.strip().lower().replace(' ', '-')
            results.append({
                "id": slug_id,
                "tool_name": tool_name,
                "trust_score": row['trust_score'],
                "analysis": json.loads(row['analysis_json']) if row['analysis_json'] else {}
            })
        return results

    def set_audit_pending(self, tool_id: str, pending: bool) -> bool:
        """Sets the audit_pending flag for a specific tool."""
        conn = self._get_conn()
        c = conn.cursor()
        
        c.execute("SELECT tool_name FROM verified_tools WHERE lower(tool_name) = %s OR replace(lower(tool_name), ' ', '-') = %s", 
                  (tool_id.lower(), tool_id.lower()))
        row = c.fetchone()
        
        if not row:
            conn.close()
            return False
            
        actual_name = row[0]
        c.execute("UPDATE verified_tools SET audit_pending = %s WHERE tool_name = %s", (1 if pending else 0, actual_name))
        conn.commit()
        conn.close()
        return True

    def apply_bridge_audit_update(self, tool_id: str, trust_score: float, executive_summary: str, 
                                  time_to_value: str, privacy_grade: str, skill_multiplier: str) -> bool:
        """Applies the structured data from the Local Factory and unsets audit_pending."""
        import re
        conn = self._get_conn()
        c = conn.cursor()
        
        c.execute("SELECT tool_name, analysis_json, gallery_json FROM verified_tools WHERE replace(lower(tool_name), ' ', '-') = %s OR lower(tool_name) = %s", 
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
                     SET trust_score = %s, 
                         analysis_json = %s, 
                         gallery_json = %s, 
                         audit_pending = 0,
                         last_updated = %s
                     WHERE tool_name = %s""",
                  (trust_score, json.dumps(analysis), json.dumps(clean_gallery), datetime.now(), actual_name))
                  
        # Add to audit history
        c.execute("""INSERT INTO audit_history (tool_name, timestamp, action, reason, score_snapshot)
                     VALUES (%s, %s, %s, %s, %s)""",
                  (actual_name, datetime.now(), "Factory Audit - Phase 3 (Bridge)", "Automated re-audit via Worker Polling", trust_score))
        
        conn.commit()
        conn.close()
        return True

    def get_sentinel_settings(self) -> Dict[str, Any]:
        """Retrieves the Aether Sentinel settings."""
        conn = self._get_conn()
        c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        c.execute("SELECT * FROM sentinel_settings WHERE id = 1")
        row = c.fetchone()
        conn.close()
        if row:
            d = dict(row)
            if d.get('last_run_timestamp'):
                d['last_run_timestamp'] = d['last_run_timestamp'].isoformat()
            return d
        return {
            "id": 1,
            "enabled": 0,
            "alert_email": "",
            "frequency_minutes": 30,
            "failure_threshold": 3,
            "current_failures": 0,
            "last_run_timestamp": None,
            "last_status": "PENDING"
        }

    def update_sentinel_settings(self, enabled: int, alert_email: str, frequency_minutes: int, failure_threshold: int) -> bool:
        """Updates Aether Sentinel settings and resets dynamic counters if needed."""
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("""UPDATE sentinel_settings 
                     SET enabled = %s, 
                         alert_email = %s, 
                         frequency_minutes = %s, 
                         failure_threshold = %s,
                         current_failures = 0
                     WHERE id = 1""", 
                  (enabled, alert_email, frequency_minutes, failure_threshold))
        conn.commit()
        conn.close()
        return True

    def update_sentinel_failures(self, current_failures: int, last_status: str) -> bool:
        """Updates the failures count and last run timestamp."""
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("""UPDATE sentinel_settings 
                     SET current_failures = %s, 
                         last_status = %s, 
                         last_run_timestamp = %s 
                     WHERE id = 1""", 
                  (current_failures, last_status, datetime.now()))
        conn.commit()
        conn.close()
        return True

    def log_sentinel_audit(self, status: str, message: str, database_status: str, memory_usage_mb: float, email_sent: int):
        """Creates an audit log entry for the Sentinel run."""
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("""INSERT INTO sentinel_audit_logs 
                     (timestamp, status, message, database_status, memory_usage_mb, email_sent) 
                     VALUES (%s, %s, %s, %s, %s, %s)""", 
                  (datetime.now(), status, message, database_status, memory_usage_mb, email_sent))
        conn.commit()
        conn.close()

    def get_sentinel_audit_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves historical health checks of Aether Sentinel."""
        conn = self._get_conn()
        c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        c.execute("SELECT * FROM sentinel_audit_logs ORDER BY timestamp DESC LIMIT %s", (limit,))
        rows = c.fetchall()
        conn.close()
        
        results = []
        for r in rows:
            d = dict(r)
            if d.get('timestamp'):
                d['timestamp'] = d['timestamp'].isoformat()
            results.append(d)
        return results

    # --- Staging Pipeline ---

    def save_staging_tool(self, tool_name: str, source: str = 'bulk_seed',
                          raw_data: str = '', category: str = '') -> int:
        """
        Inserts a new tool into the staging table.
        Skips duplicates (both staging and verified).
        Returns the staging ID, or -1 if duplicate.
        """
        conn = self._get_conn()
        c = conn.cursor()
        
        # Check duplicates in verified_tools
        c.execute("SELECT 1 FROM verified_tools WHERE lower(tool_name) = %s", (tool_name.lower(),))
        if c.fetchone():
            conn.close()
            return -1  # Already in live vault
        
        # Check duplicates in staging
        c.execute("SELECT id FROM staging_tools WHERE lower(tool_name) = %s", (tool_name.lower(),))
        existing = c.fetchone()
        if existing:
            conn.close()
            return -1  # Already staged
        
        try:
            c.execute("""INSERT INTO staging_tools 
                         (tool_name, source, raw_data, category, processing_status, ingested_at)
                         VALUES (%s, %s, %s, %s, 'pending', %s)
                         RETURNING id""",
                      (tool_name.strip(), source, raw_data, category, datetime.now()))
            staging_id = c.fetchone()[0]
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"[Vault] Error saving staging tool '{tool_name}': {e}")
            staging_id = -1
        finally:
            conn.close()
        return staging_id

    def update_staging_processed(self, tool_name: str, processed_data: str,
                                  trust_score: float, category: str,
                                  embedding_bytes: Optional[bytes] = None,
                                  processing_log: str = ''):
        """
        Updates a staging tool with processed data from the local AI processor.
        Sets status to 'processed' (ready for review).
        """
        conn = self._get_conn()
        c = conn.cursor()
        
        embedding_vector = None
        if embedding_bytes:
            embedding_vector = np.frombuffer(embedding_bytes, dtype=np.float32).tolist()
        
        c.execute("""UPDATE staging_tools SET
                        processed_data = %s,
                        trust_score = %s,
                        category = %s,
                        embedding = %s,
                        embedding_blob = %s,
                        processing_status = 'processed',
                        processing_log = %s,
                        processed_at = %s
                     WHERE lower(tool_name) = %s""",
                  (processed_data, trust_score, category, embedding_vector,
                   psycopg2.Binary(embedding_bytes) if embedding_bytes else None,
                   processing_log, datetime.now(), tool_name.lower()))
        conn.commit()
        conn.close()
        print(f"[Vault] Staging tool '{tool_name}' processed and ready for review.")

    def get_staging_queue(self, status: str = 'processed', limit: int = 100) -> List[Dict]:
        """
        Returns staging tools with the given processing status.
        Default: 'processed' (ready for human review).
        """
        conn = self._get_conn()
        c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        c.execute("""SELECT id, tool_name, source, raw_data, processed_data, trust_score,
                            category, processing_status, processing_log,
                            ingested_at, processed_at, reviewed_at, reviewer_notes
                     FROM staging_tools
                     WHERE processing_status = %s
                     ORDER BY processed_at DESC NULLS LAST, ingested_at DESC
                     LIMIT %s""", (status, limit))
        rows = c.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            d = dict(row)
            for ts_field in ('ingested_at', 'processed_at', 'reviewed_at'):
                if d.get(ts_field):
                    d[ts_field] = d[ts_field].isoformat()
            # Parse processed_data JSON if exists
            if d.get('processed_data'):
                try:
                    d['analysis'] = json.loads(d['processed_data'])
                except Exception:
                    d['analysis'] = {}
            else:
                d['analysis'] = {}
            results.append(d)
        return results

    def approve_staging_tool(self, staging_id: int, trust_score: float = None,
                              executive_summary: str = None, category: str = None,
                              reviewer_notes: str = '') -> Optional[str]:
        """
        Moves a tool from staging to verified_tools (live).
        Allows optional overrides for trust_score, summary, and category.
        Returns the tool_name if successful, None otherwise.
        """
        conn = self._get_conn()
        c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Get the staging tool
        c.execute("SELECT * FROM staging_tools WHERE id = %s", (staging_id,))
        row = c.fetchone()
        if not row:
            conn.close()
            return None
        
        tool_name = row['tool_name']
        final_score = trust_score if trust_score is not None else (row['trust_score'] or 70.0)
        
        # Parse processed data
        analysis_dict = {}
        if row['processed_data']:
            try:
                analysis_dict = json.loads(row['processed_data'])
            except Exception:
                pass
        
        # Apply overrides
        if executive_summary is not None:
            analysis_dict['executive_summary'] = executive_summary
        if category is not None:
            if 'job_to_be_done' not in analysis_dict:
                analysis_dict['job_to_be_done'] = []
            analysis_dict['job_to_be_done'] = [category] + [
                j for j in analysis_dict.get('job_to_be_done', []) if j != category
            ]
        
        analysis_json = json.dumps(analysis_dict, ensure_ascii=False)
        
        # Build embedding data
        embedding_blob = bytes(row['embedding_blob']) if row.get('embedding_blob') else None
        embedding_vector = None
        if embedding_blob:
            embedding_vector = np.frombuffer(embedding_blob, dtype=np.float32).tolist()
        
        timestamp = datetime.now()
        intent_category = category or row.get('category', 'General')
        
        # Upsert into verified_tools
        c2 = conn.cursor()
        c2.execute('''INSERT INTO verified_tools 
                     (tool_name, last_updated, trust_score, intent_category, analysis_json, 
                      gallery_json, embedding_json, embedding_blob, is_active, embedding)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                     ON CONFLICT (tool_name) DO UPDATE SET
                         last_updated = EXCLUDED.last_updated,
                         trust_score = EXCLUDED.trust_score,
                         intent_category = EXCLUDED.intent_category,
                         analysis_json = EXCLUDED.analysis_json,
                         embedding_blob = EXCLUDED.embedding_blob,
                         is_active = EXCLUDED.is_active,
                         embedding = EXCLUDED.embedding''',
                  (tool_name.lower(), timestamp, final_score, intent_category, analysis_json,
                   '[]', None, 
                   psycopg2.Binary(embedding_blob) if embedding_blob else None,
                   1, embedding_vector))
        
        # Audit log
        c2.execute('''INSERT INTO audit_history (tool_name, timestamp, action, reason, score_snapshot)
                     VALUES (%s, %s, %s, %s, %s)''',
                  (tool_name.lower(), timestamp, "Staging Pipeline Approval",
                   f"Approved from staging pipeline. {reviewer_notes}", final_score))
        
        # Update search index
        c2.execute("DELETE FROM search_index WHERE tool_name = %s", (tool_name.lower(),))
        keywords = set()
        keywords.add(tool_name.lower())
        keywords.update(w.lower() for w in tool_name.split())
        for job in analysis_dict.get('job_to_be_done', []):
            keywords.update(w.lower() for w in job.split())
        for kw in keywords:
            c2.execute("""INSERT INTO search_index (tool_name, keyword) VALUES (%s, %s)
                         ON CONFLICT (tool_name, keyword) DO NOTHING""", 
                      (tool_name.lower(), kw.strip().lower()))
        
        # Mark staging as approved
        c2.execute("""UPDATE staging_tools SET 
                        processing_status = 'approved', 
                        reviewed_at = %s, 
                        reviewer_notes = %s,
                        trust_score = %s
                     WHERE id = %s""",
                  (timestamp, reviewer_notes, final_score, staging_id))
        
        conn.commit()
        conn.close()
        print(f"[Vault] Staging tool '{tool_name}' approved and published to live Vault.")
        return tool_name

    def reject_staging_tool(self, staging_id: int, reviewer_notes: str = '') -> Optional[str]:
        """
        Marks a staging tool as rejected.
        Does NOT delete it — keeps for analytics.
        Returns tool_name if found, None otherwise.
        """
        conn = self._get_conn()
        c = conn.cursor()
        
        c.execute("SELECT tool_name FROM staging_tools WHERE id = %s", (staging_id,))
        row = c.fetchone()
        if not row:
            conn.close()
            return None
        
        tool_name = row[0]
        c.execute("""UPDATE staging_tools SET 
                        processing_status = 'rejected',
                        reviewed_at = %s,
                        reviewer_notes = %s
                     WHERE id = %s""",
                  (datetime.now(), reviewer_notes, staging_id))
        conn.commit()
        conn.close()
        print(f"[Vault] Staging tool '{tool_name}' rejected.")
        return tool_name

    def approve_staging_batch(self, staging_ids: List[int]) -> List[str]:
        """
        Batch-approve multiple staging tools at once.
        Returns list of approved tool names.
        """
        approved = []
        for sid in staging_ids:
            result = self.approve_staging_tool(sid)
            if result:
                approved.append(result)
        return approved

    def reject_staging_batch(self, staging_ids: List[int], reason: str = '') -> List[str]:
        """
        Batch-reject multiple staging tools at once.
        Returns list of rejected tool names.
        """
        rejected = []
        for sid in staging_ids:
            result = self.reject_staging_tool(sid, reviewer_notes=reason)
            if result:
                rejected.append(result)
        return rejected

    def edit_staging_tool(self, staging_id: int, trust_score: float = None,
                           executive_summary: str = None, category: str = None) -> bool:
        """
        Quick-edit a staging tool's key fields before approval.
        Only modifies the processed_data JSON and trust_score.
        """
        conn = self._get_conn()
        c = conn.cursor()
        
        c.execute("SELECT processed_data FROM staging_tools WHERE id = %s", (staging_id,))
        row = c.fetchone()
        if not row:
            conn.close()
            return False
        
        analysis = {}
        if row[0]:
            try:
                analysis = json.loads(row[0])
            except Exception:
                pass
        
        if executive_summary is not None:
            analysis['executive_summary'] = executive_summary
        if category is not None:
            analysis['job_to_be_done'] = [category] + [
                j for j in analysis.get('job_to_be_done', []) if j != category
            ]
        
        updates = ["processed_data = %s"]
        values = [json.dumps(analysis, ensure_ascii=False)]
        
        if trust_score is not None:
            updates.append("trust_score = %s")
            values.append(trust_score)
        if category is not None:
            updates.append("category = %s")
            values.append(category)
        
        values.append(staging_id)
        c.execute(f"UPDATE staging_tools SET {', '.join(updates)} WHERE id = %s", values)
        conn.commit()
        conn.close()
        return True

    def get_staging_stats(self) -> Dict:
        """Returns counts for each staging status."""
        conn = self._get_conn()
        c = conn.cursor()
        
        stats = {}
        for status in ('pending', 'processed', 'approved', 'rejected'):
            c.execute("SELECT COUNT(*) FROM staging_tools WHERE processing_status = %s", (status,))
            stats[status] = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM staging_tools")
        stats['total'] = c.fetchone()[0]
        
        # Today's activity
        c.execute("""SELECT COUNT(*) FROM staging_tools 
                     WHERE processing_status = 'approved' 
                     AND reviewed_at >= CURRENT_DATE""")
        stats['approved_today'] = c.fetchone()[0]
        
        conn.close()
        return stats
