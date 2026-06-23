"""
===========================================================================
 AetherCompass — Local AI Processor
 "The Zero-Cost Intelligence Extractor"
===========================================================================

 Extracts structured LabAnalysis-compatible data from raw tool info using
 a local LLM (Ollama). Zero API costs, no rate limits.

 Model: llama3.2:3b (recommended for reliable JSON extraction)
 Fallback: gemma4:e4b, qwen2.5

 Usage:
   from local_ai_processor import LocalAIProcessor
   processor = LocalAIProcessor()
   result = processor.process_tool("Cursor", "AI code editor built on VS Code...")
   # result = {"tool_name": "Cursor", "analysis": {...}, "trust_score": 82.0, ...}
===========================================================================
"""

import json
import sys
from typing import Dict, Optional, List

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OLLAMA_MODEL = "llama3.2:3b"
OLLAMA_FALLBACK_MODELS = ["gemma4:e4b", "qwen2.5:3b"]
OLLAMA_HOST = "http://localhost:11434"

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
# Prompts
# ---------------------------------------------------------------------------

EXTRACTION_SYSTEM_PROMPT = """You are a strict data extraction engine for an AI tool directory.
Given a tool name and any available description, extract structured information about the tool.
You MUST return ONLY valid JSON with NO markdown fences, no commentary, no explanation.

Required JSON structure:
{
  "tool_name": "Exact name of the tool",
  "executive_summary": "Sentence 1: What the tool does best. Sentence 2: The main trade-off.",
  "category": "One of: Text & Productivity, Design & Images, Dev & Code, Video & Audio, Automation, Data & Analytics, Marketing & SEO, Education & Research, Customer Support, Other",
  "job_to_be_done": ["Primary use case", "Secondary use case"],
  "pros": ["Pro 1: Brief explanation", "Pro 2: Brief explanation"],
  "cons": ["Con 1: Brief explanation", "Con 2: Brief explanation"],
  "use_cases": ["Use case 1", "Use case 2", "Use case 3"],
  "pricing": "Free / Freemium / Paid ($X/mo) / API-based",
  "learning_curve": "Very Easy / Medium / Hard / For Developers",
  "integration": "Web / API / Desktop / Mobile / Plugin",
  "metrics": {
    "accuracy": 4,
    "speed": 4,
    "value": 4,
    "ease_of_use": 4
  }
}

Rules:
- All metric scores are integers from 1 to 5.
- Be objective and factual. Do NOT invent features or capabilities.
- If you don't have enough information about a field, use reasonable defaults.
- Category MUST be exactly one from the list provided.
- Return ONLY the JSON object. No other text."""

QUALITY_CHECK_PROMPT = """You are a data quality assessor. Given a JSON object representing an AI tool analysis, rate the quality of the data on a scale of 0-100.

Consider:
- Is the executive summary informative and non-generic?
- Are the pros/cons specific and not just generic filler?
- Is the category correctly assigned?
- Are use cases realistic?

Return ONLY a JSON object:
{"quality_score": 85, "issues": ["Issue 1 if any"]}"""


# ---------------------------------------------------------------------------
# Ollama Client
# ---------------------------------------------------------------------------

def _query_ollama(system_prompt: str, user_prompt: str, model: str = None) -> Optional[Dict]:
    """
    Sends a prompt to a local LLM via Ollama.
    Returns parsed JSON dict, or None on failure.
    Tries fallback models if primary fails.
    """
    models_to_try = [model or OLLAMA_MODEL] + OLLAMA_FALLBACK_MODELS

    for current_model in models_to_try:
        try:
            from ollama import chat
        except ImportError:
            print("[FATAL] 'ollama' Python package not installed. Run: pip install ollama")
            return None

        try:
            response = chat(
                model=current_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                options={"temperature": 0.1},
            )
            raw_text = response.message.content.strip()

            # Extract JSON from response (handle markdown fences)
            json_text = raw_text
            if "```json" in json_text:
                json_text = json_text.split("```json")[1].split("```")[0].strip()
            elif "```" in json_text:
                parts = json_text.split("```")
                if len(parts) >= 3:
                    json_text = parts[1].strip()

            # Try to find JSON object boundaries
            if not json_text.startswith("{"):
                start = json_text.find("{")
                if start != -1:
                    # Find matching closing brace
                    depth = 0
                    for i in range(start, len(json_text)):
                        if json_text[i] == "{":
                            depth += 1
                        elif json_text[i] == "}":
                            depth -= 1
                        if depth == 0:
                            json_text = json_text[start:i+1]
                            break

            return json.loads(json_text)

        except json.JSONDecodeError as e:
            print(f"  [WARN] {current_model} returned invalid JSON: {e}")
            print(f"  [WARN] Raw output (first 300 chars): {raw_text[:300]}")
            continue  # Try next model
        except Exception as e:
            error_str = str(e).lower()
            if "not found" in error_str or "model" in error_str:
                print(f"  [WARN] Model '{current_model}' not available. Trying fallback...")
                continue
            print(f"  [ERROR] Ollama query failed with '{current_model}': {e}")
            continue

    return None


# ---------------------------------------------------------------------------
# Heuristic Processor (Dry-run fallback, no LLM needed)
# ---------------------------------------------------------------------------

CATEGORY_KEYWORDS = {
    "Dev & Code": ["code", "coding", "developer", "ide", "programming", "github", "git",
                    "debug", "compiler", "api", "sdk", "devops", "testing", "deploy"],
    "Design & Images": ["image", "design", "photo", "art", "visual", "graphic", "draw",
                         "illustration", "ui", "ux", "logo", "brand", "creative"],
    "Text & Productivity": ["text", "write", "writing", "document", "note", "productivity",
                             "chat", "assistant", "search", "knowledge", "summarize"],
    "Video & Audio": ["video", "audio", "music", "voice", "speech", "sound", "podcast",
                       "film", "edit", "subtitle", "transcri", "dubbing"],
    "Automation": ["automat", "workflow", "integration", "zapier", "trigger", "bot",
                    "agent", "orchestrat", "pipeline", "schedule", "task"],
    "Data & Analytics": ["data", "analytics", "dashboard", "report", "insight", "metric",
                          "bi", "visualization", "chart", "database", "ml", "model"],
    "Marketing & SEO": ["marketing", "seo", "ads", "campaign", "email", "social",
                         "content", "brand", "influencer", "conversion", "copy"],
    "Education & Research": ["education", "learn", "course", "tutor", "research",
                              "academic", "study", "quiz", "training", "teach"],
    "Customer Support": ["support", "customer", "helpdesk", "ticket", "chatbot",
                          "service", "crm", "feedback", "onboarding"],
}


def _heuristic_categorize(tool_name: str, description: str) -> str:
    """Categorizes a tool based on keyword matching (no LLM needed)."""
    text = f"{tool_name} {description}".lower()
    best_cat = "Other"
    best_score = 0

    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > best_score:
            best_score = score
            best_cat = category

    return best_cat


def _heuristic_process(tool_name: str, description: str, url: str = "",
                        category: str = "") -> Dict:
    """
    Generates a basic LabAnalysis-compatible dict using heuristics only.
    Used in dry-run mode when Ollama is not available.
    """
    if not category:
        category = _heuristic_categorize(tool_name, description)

    summary = description[:200] if description else f"{tool_name} is an AI-powered tool."
    if not summary.endswith("."):
        summary += "."

    return {
        "tool_name": tool_name,
        "executive_summary": summary,
        "category": category,
        "job_to_be_done": [category],
        "pros": [f"AI-powered: Leverages advanced AI for {category.lower()} tasks"],
        "cons": ["Limited information: Further evaluation needed for detailed assessment"],
        "use_cases": [category],
        "pricing": "Unknown",
        "learning_curve": "Medium",
        "integration": "Web",
        "metrics": {
            "accuracy": 3,
            "speed": 3,
            "value": 3,
            "ease_of_use": 3,
        },
        "website_url": url,
    }


# ---------------------------------------------------------------------------
# Main Processor Class
# ---------------------------------------------------------------------------

class LocalAIProcessor:
    """
    Processes raw AI tool data into structured LabAnalysis-compatible dicts
    using a local Ollama LLM. Falls back to heuristics in dry-run mode.
    """

    def __init__(self, model: str = None, dry_run: bool = False):
        self.model = model or OLLAMA_MODEL
        self.dry_run = dry_run
        self.processed_count = 0
        self.error_count = 0

    def process_tool(self, tool_name: str, description: str = "",
                     url: str = "", category: str = "") -> Dict:
        """
        Processes a single tool and returns structured data.

        Returns dict with keys:
          - tool_name, analysis (dict), trust_score, category, processing_log
        """
        log_entries = []
        log_entries.append(f"Processing: {tool_name}")

        if self.dry_run:
            log_entries.append("Mode: DRY RUN (heuristic)")
            analysis = _heuristic_process(tool_name, description, url, category)
            trust_score = 65.0  # Default for heuristic
        else:
            log_entries.append(f"Mode: LIVE (Ollama → {self.model})")

            # Build prompt
            user_prompt = f"Tool Name: {tool_name}\n"
            if description:
                user_prompt += f"Description: {description}\n"
            if url:
                user_prompt += f"Website: {url}\n"
            if category:
                user_prompt += f"Suggested Category: {category}\n"

            analysis = _query_ollama(EXTRACTION_SYSTEM_PROMPT, user_prompt, self.model)

            if analysis is None:
                log_entries.append("ERROR: LLM extraction failed. Falling back to heuristics.")
                analysis = _heuristic_process(tool_name, description, url, category)
                trust_score = 50.0
                self.error_count += 1
            else:
                log_entries.append("LLM extraction successful.")
                trust_score = self._calculate_trust_score(analysis)

        # Validate and fix category
        extracted_category = analysis.get("category", category or "Other")
        if extracted_category not in VALID_CATEGORIES:
            extracted_category = _heuristic_categorize(
                tool_name, analysis.get("executive_summary", description))
            log_entries.append(f"Category corrected to: {extracted_category}")

        analysis["category"] = extracted_category
        if url:
            analysis["website_url"] = url

        # Ensure required fields exist
        analysis.setdefault("tool_name", tool_name)
        analysis.setdefault("executive_summary", f"{tool_name} is an AI tool.")
        analysis.setdefault("job_to_be_done", [extracted_category])
        analysis.setdefault("pros", [])
        analysis.setdefault("cons", [])
        analysis.setdefault("use_cases", [])
        analysis.setdefault("metrics", {"accuracy": 3, "speed": 3, "value": 3, "ease_of_use": 3})

        self.processed_count += 1
        log_entries.append(f"Trust Score: {trust_score:.1f}")
        log_entries.append(f"Category: {extracted_category}")

        return {
            "tool_name": tool_name,
            "analysis": analysis,
            "trust_score": trust_score,
            "category": extracted_category,
            "processing_log": " | ".join(log_entries),
        }

    def _calculate_trust_score(self, analysis: Dict) -> float:
        """
        Calculates an initial trust score based on data completeness and quality.
        This is a preliminary score — the human reviewer can override it.
        """
        score = 50.0  # Base score

        # +5 for each substantive field
        if analysis.get("executive_summary") and len(analysis["executive_summary"]) > 30:
            score += 10
        if analysis.get("pros") and len(analysis["pros"]) >= 2:
            score += 5
        if analysis.get("cons") and len(analysis["cons"]) >= 1:
            score += 5
        if analysis.get("use_cases") and len(analysis["use_cases"]) >= 2:
            score += 5
        if analysis.get("pricing") and analysis["pricing"] != "Unknown":
            score += 5
        if analysis.get("job_to_be_done") and len(analysis["job_to_be_done"]) >= 1:
            score += 5

        # Metrics quality
        metrics = analysis.get("metrics", {})
        if all(k in metrics for k in ("accuracy", "speed", "value", "ease_of_use")):
            score += 5
            # Penalize all-max or all-min ratings (likely not thoughtful)
            values = [metrics.get("accuracy", 3), metrics.get("speed", 3),
                      metrics.get("value", 3), metrics.get("ease_of_use", 3)]
            if len(set(values)) == 1:
                score -= 5  # All same value is suspicious

        # Cap at 90 — only human review can push to 100
        return min(score, 90.0)

    def process_batch(self, tools: List[Dict], progress_callback=None) -> List[Dict]:
        """
        Processes a batch of tools.
        Each tool dict should have: name, description (optional), url (optional), category (optional)
        """
        results = []
        total = len(tools)

        for i, tool in enumerate(tools, 1):
            result = self.process_tool(
                tool_name=tool.get("name", tool.get("tool_name", "Unknown")),
                description=tool.get("description", ""),
                url=tool.get("url", ""),
                category=tool.get("category", ""),
            )
            results.append(result)

            if progress_callback:
                progress_callback(i, total, result["tool_name"])
            else:
                print(f"  [{i}/{total}] {result['tool_name']} -> "
                      f"{result['category']} (score: {result['trust_score']:.0f})")

        return results


# ---------------------------------------------------------------------------
# Self-Test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AetherCompass Local AI Processor")
    parser.add_argument("--dry-run", action="store_true", help="Use heuristics instead of Ollama")
    parser.add_argument("--model", type=str, default=None, help=f"Ollama model (default: {OLLAMA_MODEL})")
    args = parser.parse_args()

    processor = LocalAIProcessor(model=args.model, dry_run=args.dry_run)

    test_tools = [
        {"name": "Cursor", "description": "AI-powered code editor built on VS Code that understands your entire codebase", "url": "https://cursor.com"},
        {"name": "Midjourney", "description": "AI image generation platform producing photorealistic art from text prompts", "url": "https://midjourney.com"},
        {"name": "Notion AI", "description": "AI writing and summarization built into the Notion workspace", "url": "https://notion.so"},
    ]

    print("=" * 60)
    print(f" Local AI Processor Test ({'DRY RUN' if args.dry_run else 'LIVE'})")
    print("=" * 60)

    results = processor.process_batch(test_tools)

    print(f"\n{'=' * 60}")
    print(f" Processed: {processor.processed_count}, Errors: {processor.error_count}")
    print("=" * 60)

    for r in results:
        print(f"\n--- {r['tool_name']} ---")
        print(f"  Category: {r['category']}")
        print(f"  Trust Score: {r['trust_score']}")
        print(f"  Summary: {r['analysis'].get('executive_summary', 'N/A')[:100]}...")
        print(f"  Log: {r['processing_log']}")
