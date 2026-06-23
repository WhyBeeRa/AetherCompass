"""
===========================================================================
 AetherCompass — Bulk Ingester
 "The Mass Seeder"
===========================================================================

 CLI tool for loading hundreds of AI tools into the staging pipeline.
 Reads from JSON, CSV, or plain text files and inserts into staging_tools.

 Usage:
   python bulk_ingester.py --source data/ai_tools_dataset.json
   python bulk_ingester.py --source tools.csv
   python bulk_ingester.py --source tool_names.txt
   python bulk_ingester.py --source data/ai_tools_dataset.json --dry-run

 Supports:
   - JSON: Array of {"name", "url", "description", "category"}
   - CSV:  Columns: name, url, description, category
   - TXT:  One tool name per line (minimal mode)
===========================================================================
"""

import os
import sys
import json
import csv
import argparse
from pathlib import Path
from datetime import datetime

# Ensure backend is importable
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))


def load_json_source(filepath: str) -> list:
    """Loads tools from a JSON array file."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        print(f"[ERROR] JSON file must contain an array. Got: {type(data).__name__}")
        return []
    return data


def load_csv_source(filepath: str) -> list:
    """Loads tools from a CSV file with columns: name, url, description, category."""
    tools = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tools.append({
                "name": row.get("name", "").strip(),
                "url": row.get("url", "").strip(),
                "description": row.get("description", "").strip(),
                "category": row.get("category", "").strip(),
            })
    return tools


def load_txt_source(filepath: str) -> list:
    """Loads tool names from a plain text file (one per line)."""
    tools = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            name = line.strip()
            if name and not name.startswith("#"):
                tools.append({"name": name, "url": "", "description": "", "category": ""})
    return tools


def load_source(filepath: str) -> list:
    """Auto-detects file format and loads tools."""
    ext = Path(filepath).suffix.lower()
    if ext == ".json":
        return load_json_source(filepath)
    elif ext == ".csv":
        return load_csv_source(filepath)
    elif ext in (".txt", ".text"):
        return load_txt_source(filepath)
    else:
        print(f"[ERROR] Unsupported file format: {ext}")
        print("  Supported: .json, .csv, .txt")
        return []


def run_ingestion(source_path: str, dry_run: bool = False, source_label: str = "bulk_seed"):
    """
    Main ingestion flow:
    1. Read input source
    2. Deduplicate against existing DB
    3. Insert new tools into staging_tools
    """
    print("=" * 60)
    print(" AetherCompass — Bulk Ingester")
    print(f" Source: {source_path}")
    print(f" Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print(f" Started: {datetime.now().isoformat()}")
    print("=" * 60)

    # 1. Load source data
    if not os.path.exists(source_path):
        print(f"[FATAL] Source file not found: {source_path}")
        return

    tools = load_source(source_path)
    if not tools:
        print("[WARN] No tools found in source file.")
        return

    # Filter out entries with no name
    tools = [t for t in tools if t.get("name", "").strip()]
    print(f"\n  Loaded {len(tools)} tools from source file.")

    if dry_run:
        print("\n  [DRY RUN] Would insert the following tools:")
        for i, tool in enumerate(tools, 1):
            print(f"    {i:3d}. {tool['name']:<30s} | {tool.get('category', 'Unknown'):<25s} | {tool.get('url', 'N/A')}")
        print(f"\n  Total: {len(tools)} tools (dry run, nothing saved)")
        return

    # 2. Connect to DB and insert
    from persistence import AetherVault
    vault = AetherVault()

    stats = {"total": len(tools), "new": 0, "duplicate_vault": 0, "duplicate_staging": 0, "errors": 0}

    for i, tool in enumerate(tools, 1):
        name = tool["name"].strip()
        raw_data = json.dumps(tool, ensure_ascii=False)
        category = tool.get("category", "")

        result = vault.save_staging_tool(
            tool_name=name,
            source=source_label,
            raw_data=raw_data,
            category=category
        )

        if result == -1:
            stats["duplicate_vault"] += 1
            status_icon = "SKIP"
        elif result > 0:
            stats["new"] += 1
            status_icon = " NEW"
        else:
            stats["errors"] += 1
            status_icon = "ERR!"

        print(f"  [{status_icon}] {i:3d}/{len(tools)} {name}")

    # 3. Summary
    print(f"\n{'=' * 60}")
    print(" INGESTION COMPLETE")
    print("=" * 60)
    print(f"  Total in source:     {stats['total']}")
    print(f"  New (staged):        {stats['new']}")
    print(f"  Duplicates (skipped): {stats['duplicate_vault']}")
    print(f"  Errors:              {stats['errors']}")
    print("=" * 60)

    # Show staging stats
    staging_stats = vault.get_staging_stats()
    print(f"\n  Staging Pipeline Status:")
    print(f"    Pending processing: {staging_stats.get('pending', 0)}")
    print(f"    Processed (ready):  {staging_stats.get('processed', 0)}")
    print(f"    Approved (live):    {staging_stats.get('approved', 0)}")
    print(f"    Rejected:           {staging_stats.get('rejected', 0)}")
    print(f"    Total staged:       {staging_stats.get('total', 0)}")

    print(f"\n  Next step: Run 'python batch_processor.py' to process pending tools.")


# ---------------------------------------------------------------------------
# Main Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="AetherCompass Bulk Ingester — Load AI tools into the staging pipeline"
    )
    parser.add_argument(
        "--source", "-s",
        type=str,
        required=True,
        help="Path to source file (JSON, CSV, or TXT)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be ingested without saving to DB"
    )
    parser.add_argument(
        "--label",
        type=str,
        default="bulk_seed",
        help="Source label for tracking (default: bulk_seed)"
    )
    args = parser.parse_args()

    run_ingestion(args.source, dry_run=args.dry_run, source_label=args.label)
