"""
===========================================================================
 AetherCompass — Local Gemma Worker
 "The Offline Intelligence Engine"
===========================================================================

 Architecture:
   1. Reads raw scraped data (Reddit, GitHub, web) from a local JSON source.
   2. Runs three local AI passes using Gemma 4 E4B via Ollama:
        a) Noise Gate   — filters garbage / off-topic content
        b) Tagger       — assigns Aether category taxonomy
        c) Sentiment    — scores Positive / Neutral / Negative + confidence
   3. Outputs a clean `clean_verified_batch.json` ready for upload to Render.

 Requirements:
   - Ollama installed and running locally (https://ollama.com)
   - Model pulled:  `ollama pull gemma4:e4b`
   - Python lib:    `pip install ollama`

 Usage:
   python local_aether_worker.py
   python local_aether_worker.py --input raw_scraped.json
   python local_aether_worker.py --dry-run   (skip LLM, use mock outputs)
===========================================================================
"""

import json
import os
import sys
import argparse
from datetime import datetime, timezone
from typing import List, Dict, Optional

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OLLAMA_MODEL = "gemma4:e4b"
OLLAMA_HOST = "http://localhost:11434"
OUTPUT_FILE = "clean_verified_batch.json"
SENTIMENT_ESCALATION_THRESHOLD = 0.8  # Below this confidence → escalate to Cloud

# Aether's canonical category taxonomy
VALID_CATEGORIES = [
    "Text & Productivity",
    "Design & Images",
    "Dev & Code",
    "Video & Audio",
    "Automation",
    "Data & Analytics",
    "Marketing & SEO",
    "Education & Research",
    "Customer Support",
    "Other",
]

# ---------------------------------------------------------------------------
# Mock Input Data — 3 raw Reddit-style review objects
# ---------------------------------------------------------------------------

MOCK_RAW_DATA: List[Dict] = [
    {
        "id": "raw_001",
        "tool_name": "CursorAI",
        "source": "Reddit - r/programming",
        "text": (
            "lmao bro just use notepad 😂😂😂 who even needs AI for coding "
            "anyway my cat could write better code. also did anyone see the "
            "game last night? absolute banger 🔥🔥🔥"
        ),
        "url": "https://reddit.com/r/programming/comments/abc123",
        "scraped_at": "2026-04-11T10:30:00Z",
    },
    {
        "id": "raw_002",
        "tool_name": "Midjourney",
        "source": "Reddit - r/midjourney",
        "text": (
            "I've been using Midjourney v7 for client work for 3 months now. "
            "The photorealism is insane — I replaced 80% of my stock photo "
            "budget. Prompt adherence is way better than DALL-E. Only real "
            "downside is the $30/mo pro plan adds up if you're a freelancer. "
            "Rendering speed is about 15 seconds per image on fast mode."
        ),
        "url": "https://reddit.com/r/midjourney/comments/def456",
        "scraped_at": "2026-04-11T11:00:00Z",
    },
    {
        "id": "raw_003",
        "tool_name": "Jasper AI",
        "source": "Reddit - r/copywriting",
        "text": (
            "Tried Jasper for a week on the free trial. Some outputs were "
            "genuinely impressive for blog intros, but then it hallucinated "
            "statistics in a product description which almost went live. "
            "The templates are decent but I'm not sure if it's worth $49/mo "
            "when ChatGPT Plus is $20. Still undecided."
        ),
        "url": "https://reddit.com/r/copywriting/comments/ghi789",
        "scraped_at": "2026-04-11T12:15:00Z",
    },
]


# ---------------------------------------------------------------------------
# Ollama Client Wrapper
# ---------------------------------------------------------------------------

def _query_gemma(system_prompt: str, user_prompt: str, expect_json: bool = True) -> Optional[Dict | str]:
    """
    Sends a prompt to the local Gemma 4 E4B model via Ollama.
    Returns parsed JSON dict if expect_json=True, raw string otherwise.
    """
    try:
        from ollama import chat
    except ImportError:
        print("[FATAL] 'ollama' Python package not installed. Run: pip install ollama")
        sys.exit(1)

    try:
        response = chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            options={"temperature": 0.1},  # Near-deterministic for classification
        )
        raw_text = response.message.content.strip()

        if not expect_json:
            return raw_text

        # Attempt to extract JSON from the response (handle markdown fences)
        json_text = raw_text
        if "```json" in json_text:
            json_text = json_text.split("```json")[1].split("```")[0].strip()
        elif "```" in json_text:
            json_text = json_text.split("```")[1].split("```")[0].strip()

        return json.loads(json_text)

    except json.JSONDecodeError as e:
        print(f"  [WARN] Gemma returned invalid JSON: {e}")
        print(f"  [WARN] Raw output: {raw_text[:200]}...")
        return None
    except Exception as e:
        print(f"  [ERROR] Ollama query failed: {e}")
        return None


# ---------------------------------------------------------------------------
# Stage 1: The Noise Gate
# ---------------------------------------------------------------------------

NOISE_GATE_SYSTEM = """You are a strict content quality filter for an AI tool review platform.
Your job: determine if a piece of text is a GENUINE, USEFUL review of an AI tool,
or if it is NOISE (off-topic, memes, spam, too short, no actionable information).

Respond ONLY with valid JSON:
{
  "verdict": "pass" or "reject",
  "reason": "One-sentence explanation"
}

Rules:
- "pass" = text contains a real opinion, experience, or technical detail about the tool.
- "reject" = text is off-topic, a joke, spam, contains no tool-specific information, or is too vague to extract insights from.
- Be strict. Marketing copy with zero user experience is also "reject".
"""


def apply_noise_gate(item: Dict, dry_run: bool = False) -> Dict:
    """
    Runs the Noise Gate on a single raw item.
    Returns the item dict enriched with `noise_gate` results.
    """
    print(f"  [Noise Gate] Evaluating: {item['id']} ({item['tool_name']})...")

    if dry_run:
        # Heuristic mock: reject if text is under 80 chars or has 3+ emojis
        emoji_count = sum(1 for c in item["text"] if ord(c) > 0x1F600)
        is_noise = len(item["text"]) < 80 or emoji_count >= 3
        result = {
            "verdict": "reject" if is_noise else "pass",
            "reason": "Dry-run heuristic filter",
        }
    else:
        prompt = f"Tool Name: {item['tool_name']}\nSource: {item['source']}\n\nReview Text:\n\"{item['text']}\""
        result = _query_gemma(NOISE_GATE_SYSTEM, prompt)

    if result is None:
        result = {"verdict": "pass", "reason": "LLM error -- defaulting to pass"}

    item["noise_gate"] = result
    verdict_icon = "[PASS]" if result["verdict"] == "pass" else "[REJECT]"
    print(f"    {verdict_icon} Verdict: {result['verdict']} -- {result['reason']}")
    return item


# ---------------------------------------------------------------------------
# Stage 2: The Category Tagger
# ---------------------------------------------------------------------------

TAGGER_SYSTEM = f"""You are a classification engine for an AI tool directory.
Given a tool name and a review, assign the tool to ONE primary category from this fixed list:

{chr(10).join(f'- {cat}' for cat in VALID_CATEGORIES)}

Also extract the tool's tech_stack if mentioned (e.g., "LLM", "Diffusion Model", "API Wrapper").

Respond ONLY with valid JSON:
{{
  "category": "One of the categories above",
  "tech_stack": "Detected tech stack or 'Unknown'",
  "confidence": 0.95
}}

If the review does not contain enough info to determine the category, use your knowledge of the tool name.
"confidence" is a float from 0.0 to 1.0 representing how certain you are.
"""


def tag_category(item: Dict, dry_run: bool = False) -> Dict:
    """
    Tags a single item with an Aether category and tech stack.
    Only runs on items that passed the Noise Gate.
    """
    print(f"  [Tagger] Classifying: {item['id']} ({item['tool_name']})...")

    if dry_run:
        # Simple keyword-based mock
        text_lower = item["text"].lower()
        if any(kw in text_lower for kw in ["code", "programming", "cursor", "copilot"]):
            cat = "Dev & Code"
        elif any(kw in text_lower for kw in ["image", "photo", "design", "midjourney", "dall-e"]):
            cat = "Design & Images"
        elif any(kw in text_lower for kw in ["video", "audio", "voice"]):
            cat = "Video & Audio"
        elif any(kw in text_lower for kw in ["write", "copy", "blog", "content", "jasper"]):
            cat = "Text & Productivity"
        else:
            cat = "Other"
        result = {"category": cat, "tech_stack": "Unknown", "confidence": 0.7}
    else:
        prompt = f"Tool Name: {item['tool_name']}\n\nReview Text:\n\"{item['text']}\""
        result = _query_gemma(TAGGER_SYSTEM, prompt)

    if result is None:
        result = {"category": "Other", "tech_stack": "Unknown", "confidence": 0.0}

    # Validate category is in our taxonomy
    if result.get("category") not in VALID_CATEGORIES:
        print(f"    [WARN] Unknown category '{result.get('category')}', defaulting to 'Other'")
        result["category"] = "Other"

    item["classification"] = result
    print(f"    [TAG] Category: {result['category']} (confidence: {result['confidence']})")
    return item


# ---------------------------------------------------------------------------
# Stage 3: The Sentiment Engine (with Escalation Flag)
# ---------------------------------------------------------------------------

SENTIMENT_SYSTEM = """You are a sentiment analysis engine for AI tool reviews.
Analyze the review and determine:
1. The overall sentiment: "Positive", "Neutral", or "Negative".
2. A confidence score (0.0 to 1.0) representing how clear the sentiment is.
3. Key "signal phrases" — the exact quotes from the text that drove your decision.

Respond ONLY with valid JSON:
{
  "sentiment": "Positive" or "Neutral" or "Negative",
  "confidence": 0.92,
  "signal_phrases": ["phrase 1", "phrase 2"],
  "summary": "One sentence summarizing the user's actual experience"
}

Important:
- "Neutral" means mixed feelings, undecided, or balanced pros and cons.
- If confidence is below 0.8, this review will be ESCALATED to a senior analyst.
- Focus on the USER'S EXPERIENCE, not the tool's marketing claims.
"""


def calculate_local_sentiment(item: Dict, dry_run: bool = False) -> Dict:
    """
    Scores sentiment for a single item using local Gemma.
    Flags items with low confidence for Cloud escalation.
    """
    print(f"  [Sentiment] Scoring: {item['id']} ({item['tool_name']})...")

    if dry_run:
        text_lower = item["text"].lower()
        pos_words = sum(1 for w in ["great", "insane", "impressive", "love", "replaced", "better"] if w in text_lower)
        neg_words = sum(1 for w in ["downside", "hallucinated", "expensive", "slow", "struggle", "undecided"] if w in text_lower)
        total = pos_words + neg_words or 1

        if pos_words > neg_words * 2:
            sent, conf = "Positive", round(0.7 + (pos_words / total) * 0.3, 2)
        elif neg_words > pos_words * 2:
            sent, conf = "Negative", round(0.7 + (neg_words / total) * 0.3, 2)
        else:
            sent, conf = "Neutral", round(0.5 + abs(pos_words - neg_words) / total * 0.2, 2)

        result = {
            "sentiment": sent,
            "confidence": min(conf, 0.99),
            "signal_phrases": [],
            "summary": "Dry-run heuristic sentiment analysis",
        }
    else:
        prompt = f"Tool Name: {item['tool_name']}\n\nReview Text:\n\"{item['text']}\""
        result = _query_gemma(SENTIMENT_SYSTEM, prompt)

    if result is None:
        result = {
            "sentiment": "Neutral",
            "confidence": 0.0,
            "signal_phrases": [],
            "summary": "LLM error -- defaulting to Neutral",
        }

    # Flag for Cloud escalation if confidence is too low
    needs_escalation = result["confidence"] < SENTIMENT_ESCALATION_THRESHOLD
    result["escalate_to_cloud"] = needs_escalation

    item["sentiment"] = result

    icon = {"Positive": "[+]", "Negative": "[-]", "Neutral": "[~]"}.get(result["sentiment"], "[?]")
    esc_tag = " >> ESCALATE TO CLOUD" if needs_escalation else ""
    print(f"    {icon} {result['sentiment']} (confidence: {result['confidence']}){esc_tag}")
    return item


# ---------------------------------------------------------------------------
# Pipeline Orchestrator
# ---------------------------------------------------------------------------

def run_pipeline(raw_data: List[Dict], dry_run: bool = False) -> List[Dict]:
    """
    Runs the full local Gemma pipeline:
      Noise Gate -> Tagger -> Sentiment -> Output
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    total = len(raw_data)

    print("=" * 70)
    print(" AetherCompass Local Worker -- Gemma 4 E4B Batch Pipeline")
    print(f" Mode: {'DRY RUN (no LLM)' if dry_run else 'LIVE (Ollama -> ' + OLLAMA_MODEL + ')'}")
    print(" Items to process: " + str(total))
    print(" Started: " + timestamp)
    print("=" * 70)

    # -- Stage 1: Noise Gate
    print("\n" + "-" * 40)
    print("STAGE 1 / 3 -- NOISE GATE")
    print("-" * 40)
    for item in raw_data:
        apply_noise_gate(item, dry_run=dry_run)

    passed = [item for item in raw_data if item["noise_gate"]["verdict"] == "pass"]
    rejected = [item for item in raw_data if item["noise_gate"]["verdict"] == "reject"]
    print(f"\n  Results: {len(passed)} passed, {len(rejected)} rejected out of {total}")

    # -- Stage 2: Category Tagger (only on passed items)
    print("\n" + "-" * 40)
    print("STAGE 2 / 3 -- CATEGORY TAGGER")
    print("-" * 40)
    for item in passed:
        tag_category(item, dry_run=dry_run)

    # -- Stage 3: Sentiment Engine (only on passed items)
    print("\n" + "-" * 40)
    print("STAGE 3 / 3 -- SENTIMENT ENGINE")
    print("-" * 40)
    for item in passed:
        calculate_local_sentiment(item, dry_run=dry_run)

    escalated = [item for item in passed if item.get("sentiment", {}).get("escalate_to_cloud")]

    # -- Build Output
    output = {
        "batch_id": "local_" + datetime.now().strftime('%Y%m%d_%H%M%S'),
        "processed_at": timestamp,
        "model_used": OLLAMA_MODEL,
        "mode": "dry_run" if dry_run else "live",
        "stats": {
            "total_raw": total,
            "passed_noise_gate": len(passed),
            "rejected_noise_gate": len(rejected),
            "escalated_to_cloud": len(escalated),
        },
        "verified_items": passed,
        "rejected_items": [
            {"id": item["id"], "tool_name": item["tool_name"], "reason": item["noise_gate"]["reason"]}
            for item in rejected
        ],
    }

    # -- Summary
    print("\n" + "=" * 70)
    print(" PIPELINE COMPLETE")
    print("=" * 70)
    print("  Total processed:        " + str(total))
    print("  Passed Noise Gate:      " + str(len(passed)))
    print("  Rejected (garbage):     " + str(len(rejected)))
    print("  Need Cloud Escalation:  " + str(len(escalated)))
    print("=" * 70)

    return output


# ---------------------------------------------------------------------------
# Auto-Upload to Render API
# ---------------------------------------------------------------------------

# Load .env from the same directory as this script
from dotenv import load_dotenv
_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(_env_path):
    load_dotenv(_env_path)

RENDER_API_URL = os.getenv("RENDER_API_URL", "https://api.aethercompass.com")
GEMMA_WORKER_KEY = os.getenv("GEMMA_WORKER_KEY", "")


def upload_to_render(output: dict) -> bool:
    """
    POSTs the processed batch to the Render FastAPI server.
    Authenticates with the GEMMA_WORKER_KEY.
    """
    if not GEMMA_WORKER_KEY:
        print("\n  [SKIP] GEMMA_WORKER_KEY not set in .env -- skipping auto-upload.")
        print("         Set it in backend/.env to enable auto-upload.")
        return False

    upload_url = f"{RENDER_API_URL.rstrip('/')}/admin/gemma/upload-batch"
    print(f"\n  [UPLOAD] Sending batch to {upload_url}...")

    try:
        import httpx
        response = httpx.post(
            upload_url,
            json=output,
            headers={
                "Authorization": f"X-Worker-Key {GEMMA_WORKER_KEY}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

        if response.status_code == 200:
            data = response.json()
            print(f"  [OK] Server response: {data.get('message', 'Success')}")
            return True
        else:
            print(f"  [FAIL] Server returned {response.status_code}: {response.text[:200]}")
            return False

    except ImportError:
        print("  [SKIP] 'httpx' not installed. Run: pip install httpx")
        print("         Batch saved locally but NOT uploaded.")
        return False
    except Exception as e:
        print(f"  [FAIL] Upload error: {e}")
        print("         Batch saved locally. You can retry manually.")
        return False


# ---------------------------------------------------------------------------
# Main Entry Point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="AetherCompass Local Gemma Worker -- Offline Batch AI Pipeline"
    )
    parser.add_argument(
        "--input", "-i",
        type=str,
        default=None,
        help="Path to a JSON file with raw scraped data. Uses mock data if omitted.",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=OUTPUT_FILE,
        help=f"Output file path (default: {OUTPUT_FILE})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run pipeline with heuristic mocks instead of calling Ollama.",
    )
    parser.add_argument(
        "--no-upload",
        action="store_true",
        help="Skip auto-upload to Render API (local save only).",
    )
    args = parser.parse_args()

    # Load input data
    if args.input:
        if not os.path.exists(args.input):
            print(f"[FATAL] Input file not found: {args.input}")
            sys.exit(1)
        with open(args.input, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        print(f"[INFO] Loaded {len(raw_data)} items from {args.input}")
    else:
        raw_data = MOCK_RAW_DATA
        print(f"[INFO] No input file specified -- using {len(raw_data)} mock items")

    # Run the pipeline
    output = run_pipeline(raw_data, dry_run=args.dry_run)

    # Save output locally
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.output)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n  [SAVED] Output saved to: {output_path}")

    # Auto-upload to Render
    if args.no_upload:
        print("  [SKIP] --no-upload flag set. Skipping auto-upload.")
    else:
        upload_to_render(output)


if __name__ == "__main__":
    main()

