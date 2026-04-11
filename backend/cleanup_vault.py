import os
import sys
from pathlib import Path
import json

# Add backend directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent))

from persistence import AetherVault

def cleanup_vault():
    vault = AetherVault()
    print("Cleaning up Vault from generic seed data...")
    
    # Get all tools
    tools = vault.search_tools("", include_inactive=True)
    count = 0
    for tool in tools:
        analysis = tool.get("analysis", {})
        summary = analysis.get("executive_summary", "")
        
        # Kill anything that smells like seed data
        if "Seeded from Data Ingestion" in summary or "Seeded Data" in str(analysis.get("pros", [])):
            print(f"Purging generic tool: {tool['tool_name']}")
            vault.delete_tool(tool['tool_name'])
            count += 1
            
    print(f"Purged {count} generic tools.")

if __name__ == "__main__":
    cleanup_vault()
