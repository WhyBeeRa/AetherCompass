import sqlite3
import json

conn = sqlite3.connect('vault.db')
c = conn.cursor()
c.execute('SELECT tool_name FROM verified_tools')
tools = [r[0] for r in c.fetchall()]

print("Total tools:", len(tools))
print("Tools in DB:")
for t in tools:
    print(f" - {t}")
    
conn.close()
