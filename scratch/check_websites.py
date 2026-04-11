import sqlite3
import json

conn = sqlite3.connect('backend/vault.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT tool_name, analysis_json FROM verified_tools")
rows = c.fetchall()

print(f"Total tools: {len(rows)}")
with_website = 0
for row in rows:
    analysis = json.loads(row['analysis_json'])
    # Try multiple places where website might be
    website = analysis.get('website_url') or analysis.get('metrics', {}).get('website')
    if website:
        with_website += 1
    else:
        print(f"Missing website: {row['tool_name']}")

print(f"Tools with website: {with_website}")
conn.close()
