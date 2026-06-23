"""
Backfill Embeddings Script (PostgreSQL + pgvector)
=================================================
Re-embeds all tools in the vault using Google's text-embedding-004.
"""
import sys
import os

# Ensure backend/ is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import numpy as np
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

# Load env variables from backend/.env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

from persistence import AetherVault
from local_embedder import LocalEmbeddingEngine


def build_search_text(tool_name: str, analysis: dict) -> str:
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
    print("  AetherCompass PostgreSQL pgvector Backfill")
    print("  Model: text-embedding-004 (768 dims)")
    print("=" * 60)

    # 1. Load the model
    print("\n[1/3] Loading embedding engine...")
    engine = LocalEmbeddingEngine.get_instance()
    vault = AetherVault()
    print("  [OK] Engine ready.\n")

    # 2. Read all tools
    print("[2/3] Reading tools from PostgreSQL...")
    conn = vault._get_conn()
    c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    c.execute("SELECT tool_name, analysis_json, embedding FROM verified_tools")
    rows = c.fetchall()
    print(f"  [OK] Found {len(rows)} tools.\n")

    # 3. Embed each tool
    print("[3/3] Generating embeddings...")
    processed = 0
    skipped = 0
    failed = 0

    for row in rows:
        tool_name = row["tool_name"]

        # Skip if already has a valid 768-dim embedding (and is not all zeros)
        if row["embedding"] is not None:
            existing = np.array(row["embedding"])
            if len(existing) == 768 and not np.all(existing == 0):
                print(f"  [SKIP] '{tool_name}' — already has 768-dim embedding.")
                skipped += 1
                continue

        try:
            analysis = json.loads(row["analysis_json"]) if row["analysis_json"] else {}
            search_text = build_search_text(tool_name, analysis)

            # Embed
            vector = engine.embed(search_text)
            blob = vector.tobytes()
            vector_list = vector.tolist()

            # Save to DB
            c_update = conn.cursor()
            c_update.execute(
                "UPDATE verified_tools SET embedding_blob = %s, embedding = %s WHERE tool_name = %s",
                (psycopg2.Binary(blob), vector_list, tool_name)
            )
            conn.commit()

            processed += 1
            print(f"  [OK] '{tool_name}' — embedded (768 dims)")

        except Exception as e:
            failed += 1
            print(f"  [FAILED] '{tool_name}' — FAILED: {e}")

    conn.close()

    print("\n" + "=" * 60)
    print(f"  DONE: {processed} embedded, {skipped} skipped, {failed} failed")
    print("=" * 60)


if __name__ == "__main__":
    run_backfill()
