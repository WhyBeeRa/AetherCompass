import sqlite3
import os

db_path = "backend/vault.db"
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
else:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM search_queries ORDER BY timestamp DESC LIMIT 20")
        rows = c.fetchall()
        print("Latest 20 searches:")
        for row in rows:
            print(row)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
