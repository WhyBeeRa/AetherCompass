"""
Backfill Embeddings Script (FastEmbed Local)
=============================================
Re-embeds all tools in the vault using the local FastEmbed model.
NO API calls. NO rate limits. Runs in ~5 seconds for 31 tools.

Usage:
    cd backend
    python scripts/backfill_embeddings.py
"""
import sys
import os

# Ensure backend/ is on the path so we can import persistence, local_embedder, etc.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import sqlite3
import json
import numpy as np
from pathlib import Path

from local_embedder import LocalEmbeddingEngine

DB_PATH = Path(__file__).resolve().parent.parent / "vault.db"


def build_search_text(tool_name: str, analysis: dict) -> str:
    """
    Build a rich text corpus for embedding from the tool's stored analysis.
    Combines name, summary, jobs, intents, pros, and use cases.
    """
    parts = [f"Tool Name: {tool_name}"]

    summary = analysis.get("executive_summary", "")
    if summary:
        parts.append(f"Summary: {summary}")

    jobs = analysis.get("job_to_be_done", [])
    if jobs:
        parts.append("Jobs to be done: " + ", ".join(str(j) for j in jobs))

    intents = analysis.get("intents_mapped", [])
    if intents:
        intent_texts = [i.get("intent_description", "") for i in intents if isinstance(i, dict)]
        if intent_texts:
            parts.append("Specific intents: " + ", ".join(intent_texts))

    pros = analysis.get("pros", [])
    if pros:
        parts.append("Pros: " + ", ".join(str(p) for p in pros))

    use_cases = analysis.get("use_cases", [])
    if use_cases:
        parts.append("Use cases: " + ", ".join(str(u) for u in use_cases))

    return "\n".join(parts)


def run_backfill():
    print("=" * 60)
    print("  AetherCompass FastEmbed Backfill")
    print("  Model: BAAI/bge-small-en-v1.5 (384 dims)")
    print("=" * 60)

    # 1. Load the model (singleton)
    print("\n[1/3] Loading FastEmbed model...")
    engine = LocalEmbeddingEngine.get_instance()
    print("  [OK] Model loaded.\n")

    # 2. Read all tools from DB
    print(f"[2/3] Reading tools from {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Ensure embedding_blob column exists
    try:
        c.execute("ALTER TABLE verified_tools ADD COLUMN embedding_blob BLOB")
        conn.commit()
        print("  [OK] Created embedding_blob column.")
    except sqlite3.OperationalError:
        pass  # Already exists

    c.execute("SELECT tool_name, analysis_json, embedding_blob FROM verified_tools")
    rows = c.fetchall()
    print(f"  [OK] Found {len(rows)} tools.\n")

    # 3. Embed each tool
    print("[3/3] Generating embeddings...")
    processed = 0
    skipped = 0
    failed = 0

    for row in rows:
        tool_name = row["tool_name"]

        # Skip if already has a valid embedding_blob
        if row["embedding_blob"]:
            existing = np.frombuffer(row["embedding_blob"], dtype=np.float32)
            if len(existing) == 384:
                print(f"  [SKIP] '{tool_name}' — already has 384-dim embedding, skipping.")
                skipped += 1
                continue

        try:
            analysis = json.loads(row["analysis_json"]) if row["analysis_json"] else {}
            search_text = build_search_text(tool_name, analysis)

            # Embed locally
            vector = engine.embed(search_text)
            blob = vector.tobytes()

            # Save to DB
            c.execute("UPDATE verified_tools SET embedding_blob = ? WHERE tool_name = ?",
                       (blob, tool_name))
            conn.commit()

            processed += 1
            print(f"  [OK] '{tool_name}' — embedded ({len(vector)} dims, {len(blob)} bytes)")

        except Exception as e:
            failed += 1
            print(f"  [FAILED] '{tool_name}' — FAILED: {e}")

    conn.close()

    print("\n" + "=" * 60)
    print(f"  DONE: {processed} embedded, {skipped} skipped, {failed} failed")
    print("=" * 60)


if __name__ == "__main__":
    run_backfill()
