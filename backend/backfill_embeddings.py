import os
import sqlite3
import json
import asyncio
from typing import List
from dotenv import load_dotenv

import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found in environment.")
    exit(1)

genai.configure(api_key=api_key)

DB_PATH = "vault.db"

def get_db_connection():
    return sqlite3.connect(DB_PATH)

def generate_embedding(text: str) -> List[float]:
    """Generate a vector embedding for the given text using Gemini."""
    try:
        result = genai.embed_content(
            model="models/gemini-embedding-001",
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return []

def run_backfill():
    print("Starting embedding backfill...")
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Apply schema migration if needed just in case it hasn't run via the app yet
    try:
        c.execute("ALTER TABLE verified_tools ADD COLUMN embedding_json TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass # Column already exists

    c.execute("SELECT tool_name, analysis_json FROM verified_tools")
    rows = c.fetchall()
    
    tools_processed = 0
    tools_skipped = 0
    tools_failed = 0

    for row in rows:
        tool_name = row['tool_name']
        
        # Check if it already has an embedding
        c.execute("SELECT embedding_json FROM verified_tools WHERE tool_name = ?", (tool_name,))
        existing = c.fetchone()
        
        if existing and existing['embedding_json']:
            print(f"Skipping '{tool_name}' - embedding already exists.")
            tools_skipped += 1
            continue

        print(f"Generating embedding for '{tool_name}'...")
        try:
            analysis = json.loads(row['analysis_json'])
            
            # Construct a rich text representation of the tool
            text_parts = [
                f"Tool Name: {tool_name}",
                f"Summary: {analysis.get('executive_summary', '')}",
                "Jobs to be done: " + ", ".join(analysis.get('job_to_be_done', [])),
                "Category: " + analysis.get('intent_category', ''),
            ]
            
            intents = analysis.get('intents_mapped', [])
            if intents:
                intent_texts = [i.get('intent_description', '') for i in intents]
                text_parts.append("Specific intents: " + ", ".join(intent_texts))
                
            full_text = "\n".join(text_parts)
            
            # Get the embedding
            embedding = generate_embedding(full_text)
            
            if embedding:
                # Save back to DB
                embedding_json = json.dumps(embedding)
                c_update = conn.cursor()
                c_update.execute("UPDATE verified_tools SET embedding_json = ? WHERE tool_name = ?", (embedding_json, tool_name))
                conn.commit()
                tools_processed += 1
                import time
                time.sleep(1) # Small delay to respect rate limits
            else:
                tools_failed += 1
                
        except Exception as e:
            print(f"Failed to process '{tool_name}': {e}")
            tools_failed += 1

    conn.close()
    print("--------------------------------------------------")
    print(f"Backfill Complete. Processed: {tools_processed}, Skipped: {tools_skipped}, Failed: {tools_failed}")

if __name__ == "__main__":
    run_backfill()
