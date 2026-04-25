import sqlite3
import os

db_path = os.path.join("backend", "vault.db")
if not os.path.exists(db_path):
    print(f"Error: {db_path} not found")
    exit(1)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

try:
    cursor.execute("SELECT COUNT(*) FROM verified_tools")
    total_tools = cursor.fetchone()[0]
    print(f"Total tools: {total_tools}")

    cursor.execute("SELECT COUNT(*) FROM verified_tools WHERE is_active = 1")
    active_tools = cursor.fetchone()[0]
    print(f"Active tools: {active_tools}")

    cursor.execute("SELECT COUNT(*) FROM verified_tools WHERE embedding_blob IS NOT NULL")
    tools_with_embeddings = cursor.fetchone()[0]
    print(f"Tools with embeddings: {tools_with_embeddings}")

    if total_tools > 0:
        print("\n--- Sample Tools ---")
        cursor.execute("SELECT tool_name, trust_score, (embedding_blob IS NOT NULL) as has_embedding FROM verified_tools LIMIT 5")
        for row in cursor.fetchall():
            print(dict(row))

except sqlite3.Error as e:
    print(f"SQLite error: {e}")

conn.close()
