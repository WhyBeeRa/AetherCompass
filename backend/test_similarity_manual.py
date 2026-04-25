import sqlite3
import os
import numpy as np
import sys

# Add backend to path to import LocalEmbeddingEngine
sys.path.append(os.path.join(os.getcwd(), "backend"))

from local_embedder import LocalEmbeddingEngine

db_path = os.path.join("backend", "vault.db")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

embedder = LocalEmbeddingEngine.get_instance()

queries = ["Build a React app", "image generation", "audio music", "unknown query bla bla"]

for query in queries:
    print(f"\nTesting query: '{query}'")
    query_vector = embedder.embed(query)
    q_norm = np.linalg.norm(query_vector)
    print(f"Query norm: {q_norm}")

    cursor.execute("SELECT tool_name, trust_score, embedding_blob FROM verified_tools WHERE is_active = 1")
    rows = cursor.fetchall()

    scored = []
    for row in rows:
        blob = row['embedding_blob']
        if not blob:
            continue
        
        tool_vector = np.frombuffer(blob, dtype=np.float32)
        t_norm = np.linalg.norm(tool_vector)
        
        similarity = float(np.dot(query_vector, tool_vector) / (q_norm * t_norm))
        scored.append((similarity, row['tool_name']))

    scored.sort(key=lambda x: x[0], reverse=True)
    print("Top 5 results:")
    for sim, name in scored[:5]:
        status = "PASSED" if sim >= 0.20 else "FAILED (<0.20)"
        print(f"  {sim:.4f} - {name} [{status}]")

conn.close()
