import sqlite3
import json

db_path = "vault.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT tool_name, trust_score, is_active FROM verified_tools LIMIT 10")
rows = cursor.fetchall()

print("--- Top 10 Tools ---")
for row in rows:
    print(dict(row))

cursor.execute("SELECT count(*) FROM verified_tools WHERE is_active = 1")
active_count = cursor.fetchone()[0]
print(f"\nActive Tools: {active_count}")

cursor.execute("SELECT count(*) FROM verified_tools WHERE is_active = 0")
inactive_count = cursor.fetchone()[0]
print(f"Inactive Tools: {inactive_count}")

conn.close()
