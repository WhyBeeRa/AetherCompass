"""
Agent Parser & Prompt Constructor
==================================
Reads ABC-TOM Markdown agent files with YAML frontmatter, extracts metadata
and prompt body, and constructs final prompts by combining core context
(voice-dna, project-brief) with agent-specific instructions.

Dependencies: pyyaml (already in requirements or installed separately)
"""

import re
from pathlib import Path
from typing import Dict, Optional, Tuple


# Root of the ABC-TOM file-based engine
ABC_TOM_ROOT = Path(__file__).resolve().parent.parent / "abc_tom_engine"


def parse_agent_file(file_path: str | Path) -> Dict:
    """
    Parse a Markdown agent file that uses YAML frontmatter.

    Expected format:
    ```
    ---
    name: agent-name
    description: What this agent does
    ...
    ---

    # Agent Title

    Body text with instructions...
    ```

    Returns:
        dict with keys:
            - metadata: dict (parsed YAML frontmatter)
            - body: str (the markdown body after frontmatter)
            - raw: str (the full file content)
            - file_path: str (original file path)
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Agent file not found: {file_path}")

    content = path.read_text(encoding="utf-8")
    metadata, body = _extract_frontmatter(content)

    return {
        "metadata": metadata,
        "body": body.strip(),
        "raw": content,
        "file_path": str(path),
    }


def _extract_frontmatter(content: str) -> Tuple[Dict, str]:
    """
    Extract YAML frontmatter from a markdown string.

    Uses a simple regex-based approach to avoid requiring pyyaml
    for basic key-value parsing, with a pyyaml fallback for complex structures.
    """
    # Match YAML frontmatter delimited by ---
    pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
    match = re.match(pattern, content, re.DOTALL)

    if not match:
        # No frontmatter found, return empty metadata and full content as body
        return {}, content

    frontmatter_raw = match.group(1)
    body = match.group(2)

    # Try pyyaml first (handles lists, nested objects, etc.)
    try:
        import yaml
        metadata = yaml.safe_load(frontmatter_raw)
        if not isinstance(metadata, dict):
            metadata = {}
    except ImportError:
        # Fallback: simple key-value parser
        metadata = _simple_yaml_parse(frontmatter_raw)
    except Exception:
        metadata = _simple_yaml_parse(frontmatter_raw)

    return metadata, body


def _simple_yaml_parse(raw: str) -> Dict:
    """
    Minimal YAML-like parser for simple key: value pairs.
    Handles basic strings and lists (lines starting with -).
    """
    result = {}
    current_key = None
    current_list = None

    for line in raw.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Check for list item
        if stripped.startswith("- ") and current_key:
            if current_list is None:
                current_list = []
            current_list.append(stripped[2:].strip())
            result[current_key] = current_list
            continue

        # Check for key: value
        if ":" in stripped:
            if current_list is not None:
                current_list = None

            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip()
            current_key = key

            if value:
                result[key] = value
            else:
                # Value might be a list on next lines
                result[key] = ""
                current_list = []

    return result


def load_core_context() -> str:
    """
    Load and concatenate all C-core files into a single context string.
    This provides the foundational voice and project context for any agent.
    """
    core_dir = ABC_TOM_ROOT / "C-core"
    if not core_dir.exists():
        return ""

    parts = []
    for f in sorted(core_dir.iterdir()):
        if f.is_file() and f.suffix == ".md" and not f.name.startswith("."):
            content = f.read_text(encoding="utf-8").strip()
            if content:
                parts.append(f"<!-- SOURCE: {f.name} -->\n{content}")

    return "\n\n---\n\n".join(parts)


def load_voice_dna() -> str:
    """
    Load specifically the voice-dna.md file from C-core.
    """
    voice_path = ABC_TOM_ROOT / "C-core" / "voice-dna.md"
    if not voice_path.exists():
        return ""
    return voice_path.read_text(encoding="utf-8").strip()


def load_decisions_log() -> str:
    """
    Load the M-memory/decisions.md file.
    """
    decisions_path = ABC_TOM_ROOT / "M-memory" / "decisions.md"
    if not decisions_path.exists():
        return "# Decisions Log\n\nNo decisions recorded yet.\n"
    return decisions_path.read_text(encoding="utf-8").strip()


def append_to_decisions(entry: str) -> None:
    """
    Append a new decision entry to M-memory/decisions.md.
    """
    decisions_path = ABC_TOM_ROOT / "M-memory" / "decisions.md"
    decisions_path.parent.mkdir(parents=True, exist_ok=True)

    with open(decisions_path, "a", encoding="utf-8") as f:
        f.write(f"\n{entry}\n")


def construct_agent_prompt(agent_filename: str) -> str:
    """
    Construct a complete prompt by combining:
    1. Core context (voice-dna.md + project-brief.md)
    2. Agent-specific instructions (from A-agents/{agent_filename})

    This is the main entry point for the background worker and any
    future LLM-based agent execution.

    Args:
        agent_filename: Name of the agent file in A-agents/ (e.g., "auditor-agent.md")

    Returns:
        A fully constructed prompt string ready for LLM consumption.
    """
    # Load core context
    voice_dna = load_voice_dna()
    core_context = load_core_context()

    # Load agent-specific instructions
    agent_path = ABC_TOM_ROOT / "A-agents" / agent_filename
    agent_data = parse_agent_file(agent_path)

    # Load recent decisions for context (if the agent needs them)
    required_reading = agent_data["metadata"].get("required_reading", [])
    extra_context = ""
    if isinstance(required_reading, list):
        for req_file in required_reading:
            req_path = ABC_TOM_ROOT / req_file
            if req_path.exists() and req_path.is_file():
                content = req_path.read_text(encoding="utf-8").strip()
                if content:
                    extra_context += f"\n\n<!-- REQUIRED READING: {req_file} -->\n{content}"

    # Construct final prompt
    prompt_parts = []

    if core_context:
        prompt_parts.append(
            "## SYSTEM CONTEXT (Core DNA)\n\n" + core_context
        )

    if extra_context:
        prompt_parts.append(
            "## REQUIRED READING\n" + extra_context
        )

    prompt_parts.append(
        f"## AGENT INSTRUCTIONS ({agent_data['metadata'].get('name', agent_filename)})\n\n"
        + agent_data["body"]
    )

    return "\n\n" + "=" * 60 + "\n\n".join(prompt_parts)


def list_agents() -> list:
    """
    List all available agent files in A-agents/.
    Returns list of dicts with metadata for each agent.
    """
    agents_dir = ABC_TOM_ROOT / "A-agents"
    if not agents_dir.exists():
        return []

    agents = []
    for f in sorted(agents_dir.iterdir()):
        if f.is_file() and f.suffix == ".md" and not f.name.startswith("."):
            try:
                data = parse_agent_file(f)
                agents.append({
                    "filename": f.name,
                    "name": data["metadata"].get("name", f.stem),
                    "description": data["metadata"].get("description", ""),
                    "role": data["metadata"].get("role", ""),
                    "schedule": data["metadata"].get("schedule", "manual"),
                })
            except Exception:
                agents.append({
                    "filename": f.name,
                    "name": f.stem,
                    "description": "Error parsing agent file",
                    "role": "unknown",
                    "schedule": "manual",
                })

    return agents
