import os
import sqlite3
import psycopg2
import psycopg2.extras
import numpy as np
from datetime import datetime
from pgvector.psycopg2 import register_vector

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "vault.db")
DATABASE_URL = os.environ.get(
    "DATABASE_URL", 
    "postgresql://aether_user:aether_password@localhost:5432/aether_db"
)

def migrate():
    print("=" * 60)
    print("  AetherCompass SQLite -> PostgreSQL Migration Utility")
    print("=" * 60)

    if not os.path.exists(DB_PATH):
        print(f"Error: Local SQLite file '{DB_PATH}' not found.")
        print("Please make sure you run this script from the backend directory.")
        return

    # 1. Connect to SQLite
    print("[1/4] Connecting to SQLite...")
    lite_conn = sqlite3.connect(DB_PATH)
    lite_conn.row_factory = sqlite3.Row
    lite_cur = lite_conn.cursor()

    # 2. Connect to PostgreSQL
    print("[2/4] Connecting to PostgreSQL...")
    try:
        pg_conn = psycopg2.connect(DATABASE_URL)
        # Register pgvector
        try:
            pg_cur = pg_conn.cursor()
            pg_cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            pg_conn.commit()
            register_vector(pg_conn)
            print("  [OK] Connected to Postgres and registered pgvector.")
        except Exception as e:
            print(f"  [WARNING] Failed to enable pgvector extension: {e}")
        pg_cur = pg_conn.cursor()
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        print("Please verify PostgreSQL is running and DATABASE_URL is correct.")
        lite_conn.close()
        return

    # 3. Create tables in PostgreSQL
    print("[3/4] Initializing PostgreSQL schema...")
    # 1. Verified Tools (The Core Truth)
    pg_cur.execute('''CREATE TABLE IF NOT EXISTS verified_tools (
                    tool_name TEXT PRIMARY KEY,
                    last_updated TIMESTAMP,
                    trust_score REAL,
                    intent_category TEXT,
                    analysis_json TEXT,
                    gallery_json TEXT,
                    embedding_json TEXT,
                    embedding_blob BYTEA,
                    is_active INTEGER DEFAULT 1,
                    audit_pending INTEGER DEFAULT 0,
                    embedding vector(768)
                )''')
    
    pg_cur.execute('''CREATE TABLE IF NOT EXISTS scout_tasks (
                    task_id SERIAL PRIMARY KEY,
                    tool_name TEXT,
                    url TEXT,
                    submitter_email TEXT,
                    status TEXT DEFAULT 'pending',
                    error_message TEXT,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                )''')

    pg_cur.execute('''CREATE TABLE IF NOT EXISTS audit_history (
                    id SERIAL PRIMARY KEY,
                    tool_name TEXT,
                    timestamp TIMESTAMP,
                    action TEXT,
                    reason TEXT,
                    score_snapshot REAL
                )''')
    
    pg_cur.execute('''CREATE TABLE IF NOT EXISTS search_index (
                    tool_name TEXT,
                    keyword TEXT,
                    PRIMARY KEY (tool_name, keyword)
                )''')

    pg_cur.execute('''CREATE TABLE IF NOT EXISTS search_queries (
                    id SERIAL PRIMARY KEY,
                    query_text TEXT,
                    timestamp TIMESTAMP,
                    has_match INTEGER
                )''')

    pg_cur.execute('''CREATE TABLE IF NOT EXISTS users (
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

    pg_cur.execute('''CREATE TABLE IF NOT EXISTS elo_battles (
                    id SERIAL PRIMARY KEY,
                    tool_a TEXT,
                    tool_b TEXT,
                    winner TEXT,
                    category TEXT,
                    reason TEXT,
                    timestamp TIMESTAMP,
                    voter_uid TEXT
                )''')
    
    pg_cur.execute('''CREATE TABLE IF NOT EXISTS live_metrics (
                    id SERIAL PRIMARY KEY,
                    tool_name TEXT,
                    provider TEXT,
                    latency_ms REAL,
                    hallucination_score REAL,
                    timestamp TIMESTAMP,
                    status TEXT,
                    comparison_vs_avg REAL
                )''')

    pg_cur.execute('''CREATE TABLE IF NOT EXISTS sentinel_settings (
                    id INTEGER PRIMARY KEY DEFAULT 1,
                    enabled INTEGER DEFAULT 0,
                    alert_email TEXT DEFAULT '',
                    frequency_minutes INTEGER DEFAULT 30,
                    failure_threshold INTEGER DEFAULT 3,
                    current_failures INTEGER DEFAULT 0,
                    last_run_timestamp TIMESTAMP,
                    last_status TEXT DEFAULT 'PENDING'
                )''')

    pg_cur.execute('''CREATE TABLE IF NOT EXISTS sentinel_audit_logs (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP,
                    status TEXT,
                    message TEXT,
                    database_status TEXT,
                    memory_usage_mb REAL,
                    email_sent INTEGER DEFAULT 0
                )''')

    pg_cur.execute('''CREATE TABLE IF NOT EXISTS semantic_cache (
                    id SERIAL PRIMARY KEY,
                    query_text TEXT UNIQUE,
                    embedding_blob BYTEA,
                    tool_name TEXT,
                    timestamp TIMESTAMP
                )''')

    pg_cur.execute('''CREATE INDEX IF NOT EXISTS verified_tools_embedding_hnsw_idx 
                 ON verified_tools USING hnsw (embedding vector_cosine_ops);''')
    
    pg_conn.commit()
    print("  [OK] PostgreSQL schema verified.")

    # 4. Migrate Data
    print("[4/4] Starting data transfer...")

    # Verified Tools
    print("  Migrating 'verified_tools'...")
    try:
        lite_cur.execute("SELECT * FROM verified_tools")
        rows = lite_cur.fetchall()
        for row in rows:
            # Handle embedding
            blob = row['embedding_blob']
            embedding_vector = None
            if blob:
                try:
                    embedding_vector = np.frombuffer(blob, dtype=np.float32).tolist()
                    if len(embedding_vector) != 768:
                        print(f"    [WARNING] Outdated {len(embedding_vector)}-dim embedding found for '{row['tool_name']}'. Resetting to NULL (requires 768-dim backfill).")
                        embedding_vector = None
                except Exception as e:
                    print(f"    [WARNING] Failed to parse embedding for {row['tool_name']}: {e}")

            # Upsert
            pg_cur.execute("""
                INSERT INTO verified_tools 
                (tool_name, last_updated, trust_score, intent_category, analysis_json, gallery_json, embedding_json, embedding_blob, is_active, audit_pending, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (tool_name) DO UPDATE SET
                    last_updated = EXCLUDED.last_updated,
                    trust_score = EXCLUDED.trust_score,
                    intent_category = EXCLUDED.intent_category,
                    analysis_json = EXCLUDED.analysis_json,
                    gallery_json = EXCLUDED.gallery_json,
                    embedding_json = EXCLUDED.embedding_json,
                    embedding_blob = EXCLUDED.embedding_blob,
                    is_active = EXCLUDED.is_active,
                    audit_pending = EXCLUDED.audit_pending,
                    embedding = EXCLUDED.embedding
            """, (
                row['tool_name'], 
                row['last_updated'], 
                row['trust_score'], 
                row['intent_category'], 
                row['analysis_json'], 
                row['gallery_json'], 
                row['embedding_json'], 
                psycopg2.Binary(blob) if blob else None, 
                row['is_active'], 
                row['audit_pending'] if 'audit_pending' in row.keys() else 0,
                embedding_vector
            ))
        pg_conn.commit()
        print(f"    [OK] Migrated {len(rows)} tools.")
    except Exception as e:
        print(f"    [ERROR] verified_tools migration failed: {e}")
        pg_conn.rollback()

    # Scout Tasks
    print("  Migrating 'scout_tasks'...")
    try:
        lite_cur.execute("SELECT * FROM scout_tasks")
        rows = lite_cur.fetchall()
        for row in rows:
            pg_cur.execute("""
                INSERT INTO scout_tasks 
                (task_id, tool_name, url, submitter_email, status, error_message, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (task_id) DO NOTHING
            """, (row['task_id'], row['tool_name'], row['url'], row['submitter_email'], row['status'], row['error_message'], row['created_at'], row['updated_at']))
        pg_conn.commit()
        # Reset serial sequence
        pg_cur.execute("SELECT setval('scout_tasks_task_id_seq', COALESCE((SELECT MAX(task_id)+1 FROM scout_tasks), 1), false)")
        pg_conn.commit()
        print(f"    [OK] Migrated {len(rows)} tasks.")
    except Exception as e:
        print(f"    [ERROR] scout_tasks migration failed: {e}")
        pg_conn.rollback()

    # Audit History
    print("  Migrating 'audit_history'...")
    try:
        lite_cur.execute("SELECT * FROM audit_history")
        rows = lite_cur.fetchall()
        for row in rows:
            pg_cur.execute("""
                INSERT INTO audit_history 
                (id, tool_name, timestamp, action, reason, score_snapshot)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (row['id'], row['tool_name'], row['timestamp'], row['action'], row['reason'], row['score_snapshot']))
        pg_conn.commit()
        pg_cur.execute("SELECT setval('audit_history_id_seq', COALESCE((SELECT MAX(id)+1 FROM audit_history), 1), false)")
        pg_conn.commit()
        print(f"    [OK] Migrated {len(rows)} audit entries.")
    except Exception as e:
        print(f"    [ERROR] audit_history migration failed: {e}")
        pg_conn.rollback()

    # Search Index
    print("  Migrating 'search_index'...")
    try:
        lite_cur.execute("SELECT * FROM search_index")
        rows = lite_cur.fetchall()
        for row in rows:
            pg_cur.execute("""
                INSERT INTO search_index (tool_name, keyword)
                VALUES (%s, %s)
                ON CONFLICT (tool_name, keyword) DO NOTHING
            """, (row['tool_name'], row['keyword']))
        pg_conn.commit()
        print(f"    [OK] Migrated {len(rows)} search index keywords.")
    except Exception as e:
        print(f"    [ERROR] search_index migration failed: {e}")
        pg_conn.rollback()

    # Search Queries
    print("  Migrating 'search_queries'...")
    try:
        lite_cur.execute("SELECT * FROM search_queries")
        rows = lite_cur.fetchall()
        for row in rows:
            pg_cur.execute("""
                INSERT INTO search_queries (id, query_text, timestamp, has_match)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (row['id'], row['query_text'], row['timestamp'], row['has_match']))
        pg_conn.commit()
        pg_cur.execute("SELECT setval('search_queries_id_seq', COALESCE((SELECT MAX(id)+1 FROM search_queries), 1), false)")
        pg_conn.commit()
        print(f"    [OK] Migrated {len(rows)} search queries.")
    except Exception as e:
        print(f"    [ERROR] search_queries migration failed: {e}")
        pg_conn.rollback()

    # Users
    print("  Migrating 'users'...")
    try:
        lite_cur.execute("SELECT * FROM users")
        rows = lite_cur.fetchall()
        for row in rows:
            pg_cur.execute("""
                INSERT INTO users (uid, email, display_name, points, elo, badges_json, contributions_count, votes_count, last_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (uid) DO UPDATE SET
                    email = EXCLUDED.email,
                    display_name = EXCLUDED.display_name,
                    points = EXCLUDED.points,
                    elo = EXCLUDED.elo,
                    badges_json = EXCLUDED.badges_json,
                    contributions_count = EXCLUDED.contributions_count,
                    votes_count = EXCLUDED.votes_count,
                    last_active = EXCLUDED.last_active
            """, (row['uid'], row['email'], row['display_name'], row['points'], row['elo'], row['badges_json'], row['contributions_count'], row['votes_count'], row['last_active']))
        pg_conn.commit()
        print(f"    [OK] Migrated {len(rows)} users.")
    except Exception as e:
        print(f"    [ERROR] users migration failed: {e}")
        pg_conn.rollback()

    # Elo Battles
    print("  Migrating 'elo_battles'...")
    try:
        lite_cur.execute("SELECT * FROM elo_battles")
        rows = lite_cur.fetchall()
        for row in rows:
            pg_cur.execute("""
                INSERT INTO elo_battles (id, tool_a, tool_b, winner, category, reason, timestamp, voter_uid)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (row['id'], row['tool_a'], row['tool_b'], row['winner'], row['category'], row['reason'] if 'reason' in row.keys() else None, row['timestamp'], row['voter_uid']))
        pg_conn.commit()
        pg_cur.execute("SELECT setval('elo_battles_id_seq', COALESCE((SELECT MAX(id)+1 FROM elo_battles), 1), false)")
        pg_conn.commit()
        print(f"    [OK] Migrated {len(rows)} ELO battles.")
    except Exception as e:
        print(f"    [ERROR] elo_battles migration failed: {e}")
        pg_conn.rollback()

    # Live Metrics
    print("  Migrating 'live_metrics'...")
    try:
        lite_cur.execute("SELECT * FROM live_metrics")
        rows = lite_cur.fetchall()
        for row in rows:
            pg_cur.execute("""
                INSERT INTO live_metrics (id, tool_name, provider, latency_ms, hallucination_score, timestamp, status, comparison_vs_avg)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (row['id'], row['tool_name'], row['provider'], row['latency_ms'], row['hallucination_score'], row['timestamp'], row['status'], row['comparison_vs_avg']))
        pg_conn.commit()
        pg_cur.execute("SELECT setval('live_metrics_id_seq', COALESCE((SELECT MAX(id)+1 FROM live_metrics), 1), false)")
        pg_conn.commit()
        print(f"    [OK] Migrated {len(rows)} live metrics.")
    except Exception as e:
        print(f"    [ERROR] live_metrics migration failed: {e}")
        pg_conn.rollback()

    # Sentinel Settings
    print("  Migrating 'sentinel_settings'...")
    try:
        lite_cur.execute("SELECT * FROM sentinel_settings")
        rows = lite_cur.fetchall()
        for row in rows:
            pg_cur.execute("""
                INSERT INTO sentinel_settings (id, enabled, alert_email, frequency_minutes, failure_threshold, current_failures, last_run_timestamp, last_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    enabled = EXCLUDED.enabled,
                    alert_email = EXCLUDED.alert_email,
                    frequency_minutes = EXCLUDED.frequency_minutes,
                    failure_threshold = EXCLUDED.failure_threshold,
                    current_failures = EXCLUDED.current_failures,
                    last_run_timestamp = EXCLUDED.last_run_timestamp,
                    last_status = EXCLUDED.last_status
            """, (row['id'], row['enabled'], row['alert_email'], row['frequency_minutes'], row['failure_threshold'], row['current_failures'], row['last_run_timestamp'], row['last_status']))
        pg_conn.commit()
        print(f"    [OK] Migrated sentinel settings.")
    except Exception as e:
        print(f"    [ERROR] sentinel_settings migration failed: {e}")
        pg_conn.rollback()

    # Sentinel Audit Logs
    print("  Migrating 'sentinel_audit_logs'...")
    try:
        lite_cur.execute("SELECT * FROM sentinel_audit_logs")
        rows = lite_cur.fetchall()
        for row in rows:
            pg_cur.execute("""
                INSERT INTO sentinel_audit_logs (id, timestamp, status, message, database_status, memory_usage_mb, email_sent)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (row['id'], row['timestamp'], row['status'], row['message'], row['database_status'], row['memory_usage_mb'], row['email_sent']))
        pg_conn.commit()
        pg_cur.execute("SELECT setval('sentinel_audit_logs_id_seq', COALESCE((SELECT MAX(id)+1 FROM sentinel_audit_logs), 1), false)")
        pg_conn.commit()
        print(f"    [OK] Migrated {len(rows)} sentinel audit logs.")
    except Exception as e:
        print(f"    [ERROR] sentinel_audit_logs migration failed: {e}")
        pg_conn.rollback()

    # Semantic Cache (if exists in SQLite)
    print("  Migrating 'semantic_cache'...")
    try:
        # Check if table exists in SQLite first
        lite_cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='semantic_cache'")
        if lite_cur.fetchone():
            lite_cur.execute("SELECT * FROM semantic_cache")
            rows = lite_cur.fetchall()
            for row in rows:
                pg_cur.execute("""
                    INSERT INTO semantic_cache (id, query_text, embedding_blob, tool_name, timestamp)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (query_text) DO UPDATE SET
                        embedding_blob = EXCLUDED.embedding_blob,
                        tool_name = EXCLUDED.tool_name,
                        timestamp = EXCLUDED.timestamp
                """, (row['id'], row['query_text'], psycopg2.Binary(row['embedding_blob']) if row['embedding_blob'] else None, row['tool_name'], row['timestamp']))
            pg_conn.commit()
            pg_cur.execute("SELECT setval('semantic_cache_id_seq', COALESCE((SELECT MAX(id)+1 FROM semantic_cache), 1), false)")
            pg_conn.commit()
            print(f"    [OK] Migrated {len(rows)} semantic cache entries.")
        else:
            print("    [INFO] 'semantic_cache' table does not exist in SQLite source. Skipping.")
    except Exception as e:
        print(f"    [ERROR] semantic_cache migration failed: {e}")
        pg_conn.rollback()

    # Clean up
    lite_conn.close()
    pg_conn.close()
    print("=" * 60)
    print("  Migration process complete!")
    print("=" * 60)

if __name__ == "__main__":
    migrate()
