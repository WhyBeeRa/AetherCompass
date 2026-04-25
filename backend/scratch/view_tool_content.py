import sqlite3
import json
import re

def view_hebrew_content():
    conn = sqlite3.connect('c:/Users/Yuval/Documents/GitHub/AetherCompass/backend/vault.db')
    c = conn.cursor()
    c.execute('SELECT tool_name, analysis_json FROM verified_tools WHERE tool_name = "chatgpt"')
    
    row = c.fetchone()
    if row:
        print(f"Tool: {row[0]}")
        print(f"Analysis: {row[1]}")
            
    conn.close()

if __name__ == "__main__":
    view_hebrew_content()
