import sqlite3
import json
import re

def check_hebrew():
    conn = sqlite3.connect('c:/Users/Yuval/Documents/GitHub/AetherCompass/backend/vault.db')
    c = conn.cursor()
    c.execute('SELECT tool_name, analysis_json FROM verified_tools')
    
    hebrew_regex = re.compile(r'[\u0590-\u05FF]')
    
    hebrew_tools = []
    for name, analysis_json in c.fetchall():
        if analysis_json and hebrew_regex.search(analysis_json):
            hebrew_tools.append(name)
            
    print(f"Total tools with Hebrew: {len(hebrew_tools)}")
    if hebrew_tools:
        print("Tools with Hebrew content:")
        for tool in hebrew_tools:
            print(f" - {tool}")
            
    conn.close()

if __name__ == "__main__":
    check_hebrew()
