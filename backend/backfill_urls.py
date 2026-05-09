import sqlite3
import json

conn = sqlite3.connect('vault.db')
c = conn.cursor()
c.execute('SELECT tool_name, analysis_json FROM verified_tools')
rows = c.fetchall()

urls = {
    'chatgpt': 'https://chatgpt.com',
    'claude 3.5 sonnet': 'https://claude.ai',
    'cursor': 'https://cursor.com',
    'perplexity': 'https://perplexity.ai'
}

count = 0
for t_name, a_json in rows:
    if a_json:
        try:
            data = json.loads(a_json)
            if t_name.lower() in urls:
                data['website_url'] = urls[t_name.lower()]
                c.execute('UPDATE verified_tools SET analysis_json = ? WHERE tool_name = ?', (json.dumps(data), t_name))
                count += 1
        except Exception as e:
            print(f"Error updating {t_name}: {e}")

conn.commit()
print(f"Updated {count} tools.")
conn.close()
