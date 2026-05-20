"""
AI Factory Router
=================
Local-only Admin API for managing the file-based AI Factory (ABC-TOM structure).
Strictly separated from production endpoints. All endpoints require local admin auth.

Exposes:
  - /admin/factory/tree      - Full directory tree
  - /admin/factory/file      - Read/write any .md file
  - /admin/factory/core      - List C-core files
  - /admin/factory/core/{f}  - Read specific C-core file
  - /admin/factory/memory/*  - Read M-memory logs (system-log, decisions)
  - /admin/factory/status    - Engine status
"""

import os
from pathlib import Path
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from auth import verify_admin_user


router = APIRouter(
    prefix="/admin/factory",
    tags=["AI Factory (Local)"],
    dependencies=[Depends(verify_admin_user)],
)

# Root of the local AI Factory
FACTORY_ROOT = Path(__file__).resolve().parent.parent / "local_ai_factory"

# Allowed top-level directories (safety boundary)
ALLOWED_DIRS = {"A-agents", "B-brain", "C-core", "M-memory", "O-output", "T-tools"}


# ---- Helpers ----------------------------------------------------------------

def _safe_path(relative_path: str) -> Path:
    """Resolve a relative path inside FACTORY_ROOT. Prevents traversal."""
    resolved = (FACTORY_ROOT / relative_path).resolve()
    if not str(resolved).startswith(str(FACTORY_ROOT.resolve())):
        raise HTTPException(status_code=403, detail="Path traversal not allowed")
    return resolved


def _build_tree(directory: Path) -> list:
    """Recursively build a file tree for the frontend."""
    items = []
    if not directory.exists():
        return items

    for entry in sorted(directory.iterdir()):
        if entry.name.startswith(".") or entry.name in ("__pycache__", "__MACOSX"):
            continue

        rel = entry.relative_to(FACTORY_ROOT).as_posix()

        if entry.is_dir():
            items.append({
                "name": entry.name,
                "path": rel,
                "type": "directory",
                "children": _build_tree(entry),
            })
        elif entry.suffix in (".md", ".txt", ".yaml", ".yml"):
            items.append({
                "name": entry.name,
                "path": rel,
                "type": "file",
                "size": entry.stat().st_size,
            })

    return items


# ---- Models -----------------------------------------------------------------

class FileUpdateBody(BaseModel):
    content: str


class FilePayload(BaseModel):
    path: str
    name: str
    content: str
    size: int
    last_modified: str


# ---- Endpoints --------------------------------------------------------------

@router.get("/tree")
async def get_factory_tree(admin_email: str = Depends(verify_admin_user)):
    """Returns the full directory tree of the local_ai_factory folder."""
    tree = []
    for dir_name in sorted(ALLOWED_DIRS):
        dir_path = FACTORY_ROOT / dir_name
        tree.append({
            "name": dir_name,
            "path": dir_name,
            "type": "directory",
            "children": _build_tree(dir_path) if dir_path.exists() else [],
        })
    return {"tree": tree, "root": str(FACTORY_ROOT)}


@router.get("/file")
async def read_factory_file(
    path: str = Query(..., description="Relative path inside local_ai_factory"),
    admin_email: str = Depends(verify_admin_user),
):
    """Read a file from the AI Factory."""
    target = _safe_path(path)
    if not target.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {path}")
    if target.is_dir():
        raise HTTPException(status_code=400, detail="Cannot read a directory")

    try:
        content = target.read_text(encoding="utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Read failed: {e}")

    stat = target.stat()
    return FilePayload(
        path=path,
        name=target.name,
        content=content,
        size=stat.st_size,
        last_modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
    )


@router.put("/file")
async def update_factory_file(
    path: str = Query(..., description="Relative path inside local_ai_factory"),
    body: FileUpdateBody = ...,
    admin_email: str = Depends(verify_admin_user),
):
    """Write (overwrite) a .md file in the AI Factory."""
    target = _safe_path(path)

    if target.suffix.lower() not in (".md", ".txt"):
        raise HTTPException(status_code=400, detail="Only .md and .txt files are writable")

    target.parent.mkdir(parents=True, exist_ok=True)

    try:
        target.write_text(body.content, encoding="utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Write failed: {e}")

    stat = target.stat()
    return {
        "status": "success",
        "path": path,
        "size": stat.st_size,
        "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "message": f"File '{target.name}' updated by {admin_email}",
    }


# ---- C-core Endpoints -------------------------------------------------------

@router.get("/core")
async def list_core_files(admin_email: str = Depends(verify_admin_user)):
    """List all files in C-core."""
    core_dir = FACTORY_ROOT / "C-core"
    if not core_dir.exists():
        return {"files": []}

    files = []
    for entry in sorted(core_dir.iterdir()):
        if entry.is_file() and not entry.name.startswith("."):
            stat = entry.stat()
            files.append({
                "name": entry.name,
                "path": f"C-core/{entry.name}",
                "size": stat.st_size,
                "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            })
    return {"files": files}


@router.get("/core/{filename}")
async def read_core_file(filename: str, admin_email: str = Depends(verify_admin_user)):
    """Read a specific C-core file."""
    target = _safe_path(f"C-core/{filename}")
    if not target.exists():
        raise HTTPException(status_code=404, detail=f"Core file not found: {filename}")

    content = target.read_text(encoding="utf-8")
    stat = target.stat()
    return FilePayload(
        path=f"C-core/{filename}",
        name=filename,
        content=content,
        size=stat.st_size,
        last_modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
    )


# ---- M-memory Endpoints -----------------------------------------------------

@router.get("/memory/system-log")
async def read_system_log(admin_email: str = Depends(verify_admin_user)):
    """Read the M-memory/system-log.md (factory engine output)."""
    log_path = FACTORY_ROOT / "M-memory" / "system-log.md"
    if not log_path.exists():
        return FilePayload(
            path="M-memory/system-log.md",
            name="system-log.md",
            content="# System Log\n\nNo activity yet.\n",
            size=0,
            last_modified=datetime.now().isoformat(),
        )

    content = log_path.read_text(encoding="utf-8")
    stat = log_path.stat()
    return FilePayload(
        path="M-memory/system-log.md",
        name="system-log.md",
        content=content,
        size=stat.st_size,
        last_modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
    )


@router.get("/memory/decisions")
async def read_decisions(admin_email: str = Depends(verify_admin_user)):
    """Read the M-memory/decisions.md log."""
    dec_path = FACTORY_ROOT / "M-memory" / "decisions.md"
    if not dec_path.exists():
        return FilePayload(
            path="M-memory/decisions.md",
            name="decisions.md",
            content="# Decisions Log\n\nNo decisions recorded yet.\n",
            size=0,
            last_modified=datetime.now().isoformat(),
        )

    content = dec_path.read_text(encoding="utf-8")
    stat = dec_path.stat()
    return FilePayload(
        path="M-memory/decisions.md",
        name="decisions.md",
        content=content,
        size=stat.st_size,
        last_modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
    )


# ---- Engine Status -----------------------------------------------------------

@router.get("/status")
async def get_factory_status(admin_email: str = Depends(verify_admin_user)):
    """
    Returns the current status of the local AI Factory engine.
    Checks if the engine module is loaded and the scheduler is running.
    """
    engine_status = "UNKNOWN"
    last_cycle = None

    # Check system log for last entry timestamp
    log_path = FACTORY_ROOT / "M-memory" / "system-log.md"
    if log_path.exists():
        content = log_path.read_text(encoding="utf-8")
        lines = [l for l in content.strip().split("\n") if l.startswith("- ")]
        if lines:
            last_cycle = lines[-1].strip("- ").strip()

    try:
        from local_ai_factory.engine import get_engine_status
        engine_status = get_engine_status()
    except ImportError:
        engine_status = "MODULE_NOT_LOADED"
    except Exception as e:
        engine_status = f"ERROR: {e}"

    dirs_present = [d for d in ALLOWED_DIRS if (FACTORY_ROOT / d).exists()]

    return {
        "engine_status": engine_status,
        "last_cycle": last_cycle,
        "factory_root": str(FACTORY_ROOT),
        "directories_active": dirs_present,
        "directory_count": len(dirs_present),
        "timestamp": datetime.now().isoformat(),
    }


@router.post("/audit/trigger")
async def trigger_audit_cycle(
    batch_size: int = Query(5, description="Number of tools to process"),
    admin_email: str = Depends(verify_admin_user)
):
    """
    Manually trigger the Auditor Agent to run a batch cycle.
    """
    try:
        from local_ai_factory.engine import trigger_manual_audit
        result = trigger_manual_audit(batch_size=batch_size)
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("reason"))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
