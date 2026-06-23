"""
===========================================================================
 AetherCompass — Batch Processor
 "The Autonomous Assembly Line"
===========================================================================

 Pulls pending tools from staging, processes them through the local AI
 processor (Ollama) and local embedder, then marks them ready for review.

 Zero API cost. Runs entirely on local hardware.

 Usage:
   python batch_processor.py                          # Process all pending (live)
   python batch_processor.py --batch-size 50          # Process 50 at a time
   python batch_processor.py --dry-run                # Heuristic mode, no Ollama
   python batch_processor.py --dry-run --skip-embed   # Fastest test mode
   python batch_processor.py --model qwen2.5:3b       # Use specific model

 Pipeline:
   staging_tools (pending) → LocalAIProcessor → OfflineEmbedder → staging_tools (processed)
===========================================================================
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime

# Ensure backend is importable
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))


def run_batch_processing(batch_size: int = 100, dry_run: bool = False,
                          model: str = None, skip_embed: bool = False):
    """
    Main batch processing loop:
    1. Pull pending tools from staging
    2. Process each with LocalAIProcessor (Ollama or heuristic)
    3. Generate embeddings with OfflineEmbeddingEngine
    4. Update staging with processed data
    """
    from persistence import AetherVault
    from local_ai_processor import LocalAIProcessor

    vault = AetherVault()
    processor = LocalAIProcessor(model=model, dry_run=dry_run)

    # Initialize embedder (skip if requested)
    embedder = None
    if not skip_embed:
        try:
            from local_embedder_offline import OfflineEmbeddingEngine
            embedder = OfflineEmbeddingEngine.get_instance()
            if not embedder.is_ready():
                print("[WARN] Offline embedder not ready. Embeddings will be skipped.")
                embedder = None
        except Exception as e:
            print(f"[WARN] Could not load offline embedder: {e}")
            print("  Embeddings will be skipped. Install: pip install sentence-transformers")
            embedder = None

    # Pull pending tools
    pending = vault.get_staging_queue(status='pending', limit=batch_size)

    if not pending:
        print("\n  No pending tools in staging. Nothing to process.")
        print("  Run 'python bulk_ingester.py --source data/ai_tools_dataset.json' first.")
        return

    total = len(pending)
    start_time = time.time()

    model_name = model or "llama3.2:3b"
    mode_str = 'DRY RUN (heuristic)' if dry_run else f'LIVE (Ollama -> {model_name})'
    
    print("=" * 70)
    print(" AetherCompass — Batch Processor")
    print(f" Mode: {mode_str}")
    print(f" Embedder: {'SKIP' if skip_embed else ('READY' if embedder else 'UNAVAILABLE')}")
    print(f" Batch: {total} tools to process")
    print(f" Started: {datetime.now().isoformat()}")
    print("=" * 70)

    processed = 0
    errors = 0
    embedded = 0

    for i, tool in enumerate(pending, 1):
        tool_name = tool['tool_name']
        elapsed = time.time() - start_time
        avg_time = elapsed / i if i > 1 else 0
        eta = avg_time * (total - i)

        print(f"\n  [{i}/{total}] Processing: {tool_name}" +
              (f"  (ETA: {eta:.0f}s)" if i > 1 else ""))

        # Parse raw data
        raw_data = {}
        if tool.get('raw_data'):
            try:
                raw_data = json.loads(tool['raw_data'])
            except Exception:
                pass

        description = raw_data.get('description', '')
        url = raw_data.get('url', '')
        category = tool.get('category', raw_data.get('category', ''))

        # --- Stage 1: AI Processing ---
        try:
            result = processor.process_tool(
                tool_name=tool_name,
                description=description,
                url=url,
                category=category
            )

            analysis = result['analysis']
            trust_score = result['trust_score']
            final_category = result['category']
            processing_log = result['processing_log']
            processed += 1

        except Exception as e:
            print(f"    [ERROR] Processing failed: {e}")
            errors += 1
            continue

        # --- Stage 2: Embedding ---
        embedding_bytes = None
        if embedder and not skip_embed:
            try:
                # Build rich search text for embedding
                search_parts = [tool_name]
                if analysis.get('executive_summary'):
                    search_parts.append(analysis['executive_summary'])
                for job in analysis.get('job_to_be_done', []):
                    search_parts.append(job)
                for uc in analysis.get('use_cases', []):
                    search_parts.append(uc)

                search_text = ". ".join(search_parts)
                embedding_bytes = embedder.embed_to_bytes(search_text)
                embedded += 1
                print(f"    [EMBED] OK - Vector generated ({len(embedding_bytes)} bytes)")
            except Exception as e:
                print(f"    [EMBED] FAIL: {e}")

        # --- Stage 3: Save to staging ---
        try:
            processed_data = json.dumps(analysis, ensure_ascii=False)
            vault.update_staging_processed(
                tool_name=tool_name,
                processed_data=processed_data,
                trust_score=trust_score,
                category=final_category,
                embedding_bytes=embedding_bytes,
                processing_log=processing_log
            )
            print(f"    [SAVE] OK - Ready for review (score: {trust_score:.0f}, cat: {final_category})")
        except Exception as e:
            print(f"    [SAVE] FAIL to save: {e}")
            errors += 1

    # --- Summary ---
    elapsed = time.time() - start_time

    print(f"\n{'=' * 70}")
    print(" BATCH PROCESSING COMPLETE")
    print("=" * 70)
    print(f"  Total processed:   {processed}/{total}")
    print(f"  Embedded:          {embedded}")
    print(f"  Errors:            {errors}")
    print(f"  Time elapsed:      {elapsed:.1f}s ({elapsed/total:.1f}s per tool)")
    print("=" * 70)

    # Show updated staging stats
    stats = vault.get_staging_stats()
    print(f"\n  Staging Pipeline Status:")
    print(f"    Pending:           {stats.get('pending', 0)}")
    print(f"    Ready for Review:  {stats.get('processed', 0)}")
    print(f"    Approved:          {stats.get('approved', 0)}")
    print(f"    Rejected:          {stats.get('rejected', 0)}")
    print(f"    Total:             {stats.get('total', 0)}")

    if stats.get('processed', 0) > 0:
        print(f"\n  [SUCCESS] {stats['processed']} tools ready for review in the Admin Review Queue!")


# ---------------------------------------------------------------------------
# Main Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="AetherCompass Batch Processor — Process staged tools with local AI"
    )
    parser.add_argument(
        "--batch-size", "-b",
        type=int,
        default=100,
        help="Number of tools to process in this batch (default: 100)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Use heuristic processing instead of Ollama (no LLM needed)"
    )
    parser.add_argument(
        "--model", "-m",
        type=str,
        default=None,
        help="Ollama model to use (default: llama3.2:3b)"
    )
    parser.add_argument(
        "--skip-embed",
        action="store_true",
        help="Skip embedding generation (useful for testing)"
    )
    args = parser.parse_args()

    run_batch_processing(
        batch_size=args.batch_size,
        dry_run=args.dry_run,
        model=args.model,
        skip_embed=args.skip_embed
    )
