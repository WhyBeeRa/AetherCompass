"""
Backfill Gemini Embeddings
==========================
This script iterates through all verified tools in vault.db, 
re-generates their embeddings using the new Gemini Remote Engine, 
and updates the database.

Run this after switching to the Remote Embedder to ensure vector dimension consistency.
"""
import os
import sys
import numpy as np
from persistence import AetherVault
from local_embedder import LocalEmbeddingEngine
from models import LabAnalysis

def backfill():
    print("--- Starting Gemini Embedding Backfill ---")
    
    # 1. Initialize components
    vault = AetherVault()
    embedder = LocalEmbeddingEngine.get_instance()
    
    if not embedder.is_ready():
        print("Error: Gemini API Key not found. Set GEMINI_API_KEY environment variable.")
        return

    # 2. Get all tools (including inactive ones if we want a full backfill)
    # We use search_tools with empty query to get everything
    tools = vault.search_tools(query="", include_inactive=True)
    total = len(tools)
    
    print(f"Found {total} tools to re-embed.")

    for i, tool in enumerate(tools):
        name = tool['tool_name']
        analysis = tool.get('analysis', {})
        
        # We need a string to embed. Usually we embed the job_to_be_done or a summary.
        # Following the pattern in etl.py (if exists) or common sense:
        # We'll combine the tool name and the executive summary/intents.
        
        summary = analysis.get("executive_summary", "")
        intents = analysis.get("job_to_be_done", [])
        
        content_to_embed = f"{name}: {summary} {' '.join(intents)}"
        
        print(f"[{i+1}/{total}] Embedding '{name}' ...", end="\r")
        
        try:
            # Generate new 768-dim vector
            new_vector_bytes = embedder.embed_to_bytes(content_to_embed)
            
            # Update DB
            vault.update_tool_embedding(name, new_vector_bytes)
        except Exception as e:
            print(f"\nFailed to embed {name}: {e}")

    print(f"\n--- Backfill Completed! {total} tools updated. ---")

if __name__ == "__main__":
    backfill()
