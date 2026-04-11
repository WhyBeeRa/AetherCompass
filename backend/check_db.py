import sqlite3
import os

db_path = "backend/vault.db"
if not os.path.exists(db_path):
    print(f"DB not found at {db_path}")
else:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        c.execute("SELECT count(*) FROM search_queries")
        count = c.fetchone()[0]
        print(f"Total search_queries: {count}")
    except Exception as e:
        print(f"Error: {e}")
    conn.close()
