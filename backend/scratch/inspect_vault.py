import sqlite3, json
conn = sqlite3.connect('vault.db')
c = conn.cursor()
c.execute("SELECT tool_name, trust_score, analysis_json FROM verified_tools LIMIT 5")
rows = c.fetchall()
for r in rows:
    analysis = json.loads(r[2]) if r[2] else {}
    print(r[0], '|', r[1], '|', analysis.get('executive_summary','')[:80])
print('---')
c.execute("SELECT COUNT(*) FROM verified_tools WHERE analysis_json LIKE '%Seeded from Data Ingestion%'")
print('Seeded placeholders:', c.fetchone()[0])
c.execute("SELECT COUNT(*) FROM verified_tools")
print('Total tools:', c.fetchone()[0])
c.execute("SELECT tool_name, analysis_json FROM verified_tools WHERE analysis_json LIKE '%Seeded from Data Ingestion%' LIMIT 5")
rows = c.fetchall()
for r in rows:
    a = json.loads(r[1]) if r[1] else {}
    print(' -', r[0], '| website_url:', a.get('website_url','N/A'))
conn.close()
