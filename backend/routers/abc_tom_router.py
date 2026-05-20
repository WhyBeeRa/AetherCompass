"""
ABC-TOM Engine API Router
=========================
Local Admin API for managing the file-based ABC-TOM prompt/context/memory system.
All endpoints are secured behind verify_admin_user (Firebase or dev-admin-token bypass).

This router exposes:
  - File tree listing for the entire abc_tom_engine directory
  - Read/update endpoints for any markdown file in the engine
  - Dedicated endpoints for C-core files and M-memory/decisions.md
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from auth import verify_admin_user


router = APIRouter(
    prefix="/admin/abc-tom",
    tags=["ABC-TOM Engine"],
    dependencies=[Depends(verify_admin_user)],
)

# Root of the ABC-TOM file-based engine
ABC_TOM_ROOT = Path(__file__).resolve().parent.parent / "abc_tom_engine"

# Allowed top-level directories (safety boundary)
ALLOWED_DIRS = {"A-agents", "B-brain", "C-core", "M-memory", "O-output", "T-tools"}


# ─── Helpers ───────────────────────────────────────────────────────────────────

def _safe_path(relative_path: str) -> Path:
    """
    Resolve a relative path inside ABC_TOM_ROOT.
    Prevents directory traversal attacks.
    """
    resolved = (ABC_TOM_ROOT / relative_path).resolve()
    if not str(resolved).startswith(str(ABC_TOM_ROOT.resolve())):
        raise HTTPException(status_code=403, detail="Path traversal not allowed")
    return resolved


def _build_tree(directory: Path, prefix: str = "") -> list:
    """
    Recursively build a file tree structure for the frontend.
    Returns a list of dicts with {name, path, type, children?}.
    """
    items = []
    if not directory.exists():
        return items

    for entry in sorted(directory.iterdir()):
        # Skip hidden files / system files
        if entry.name.startswith(".") or entry.name == "__pycache__" or entry.name == "__MACOSX":
            continue

        rel = entry.relative_to(ABC_TOM_ROOT).as_posix()

        if entry.is_dir():
            children = _build_tree(entry, prefix=rel)
            items.append({
                "name": entry.name,
                "path": rel,
                "type": "directory",
                "children": children,
            })
        else:
            items.append({
                "name": entry.name,
                "path": rel,
                "type": "file",
                "size": entry.stat().st_size,
            })

    return items


# ─── Models ────────────────────────────────────────────────────────────────────

class FileUpdateRequest(BaseModel):
    content: str


class FileResponse(BaseModel):
    path: str
    name: str
    content: str
    size: int
    last_modified: str


# ─── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/tree")
async def get_file_tree(admin_email: str = Depends(verify_admin_user)):
    """
    Returns the full directory tree of the abc_tom_engine folder.
    Used by the frontend file browser pane.
    """
    tree = []
    for dir_name in sorted(ALLOWED_DIRS):
        dir_path = ABC_TOM_ROOT / dir_name
        if dir_path.exists():
            children = _build_tree(dir_path)
            tree.append({
                "name": dir_name,
                "path": dir_name,
                "type": "directory",
                "children": children,
            })
        else:
            tree.append({
                "name": dir_name,
                "path": dir_name,
                "type": "directory",
                "children": [],
            })

    return {"tree": tree, "root": str(ABC_TOM_ROOT)}


@router.get("/file")
async def read_file(
    path: str = Query(..., description="Relative path to file inside abc_tom_engine"),
    admin_email: str = Depends(verify_admin_user),
):
    """
    Read the content of a markdown file from the ABC-TOM engine.
    """
    target = _safe_path(path)
    if not target.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {path}")
    if target.is_dir():
        raise HTTPException(status_code=400, detail="Cannot read a directory")

    try:
        content = target.read_text(encoding="utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file: {e}")

    stat = target.stat()
    return FileResponse(
        path=path,
        name=target.name,
        content=content,
        size=stat.st_size,
        last_modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
    )


@router.put("/file")
async def update_file(
    path: str = Query(..., description="Relative path to file inside abc_tom_engine"),
    body: FileUpdateRequest = ...,
    admin_email: str = Depends(verify_admin_user),
):
    """
    Update (overwrite) the content of a markdown file in the ABC-TOM engine.
    Only .md files are writable for safety.
    """
    target = _safe_path(path)

    if not target.suffix.lower() == ".md":
        raise HTTPException(status_code=400, detail="Only .md files can be updated")

    # Create parent dirs if needed (e.g., new file in existing structure)
    target.parent.mkdir(parents=True, exist_ok=True)

    try:
        target.write_text(body.content, encoding="utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write file: {e}")

    stat = target.stat()
    return {
        "status": "success",
        "path": path,
        "size": stat.st_size,
        "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "message": f"File '{target.name}' updated successfully by {admin_email}",
    }


# ─── C-core Dedicated Endpoints ───────────────────────────────────────────────

@router.get("/core")
async def list_core_files(admin_email: str = Depends(verify_admin_user)):
    """
    List all files in the C-core directory.
    """
    core_dir = ABC_TOM_ROOT / "C-core"
    if not core_dir.exists():
        return {"files": []}

    files = []
    for entry in sorted(core_dir.iterdir()):
        if entry.is_file() and not entry.name.startswith("."):
            files.append({
                "name": entry.name,
                "path": f"C-core/{entry.name}",
                "size": entry.stat().st_size,
                "last_modified": datetime.fromtimestamp(entry.stat().st_mtime).isoformat(),
            })

    return {"files": files}


@router.get("/core/{filename}")
async def read_core_file(filename: str, admin_email: str = Depends(verify_admin_user)):
    """
    Read a specific C-core configuration file.
    """
    target = _safe_path(f"C-core/{filename}")
    if not target.exists():
        raise HTTPException(status_code=404, detail=f"Core file not found: {filename}")

    content = target.read_text(encoding="utf-8")
    stat = target.stat()

    return FileResponse(
        path=f"C-core/{filename}",
        name=filename,
        content=content,
        size=stat.st_size,
        last_modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
    )


# ─── M-memory Dedicated Endpoints ─────────────────────────────────────────────

@router.get("/memory/decisions")
async def read_decisions(admin_email: str = Depends(verify_admin_user)):
    """
    Read the M-memory/decisions.md log file directly.
    """
    decisions_path = ABC_TOM_ROOT / "M-memory" / "decisions.md"
    if not decisions_path.exists():
        return FileResponse(
            path="M-memory/decisions.md",
            name="decisions.md",
            content="# Decisions Log\n\nNo decisions recorded yet.\n",
            size=0,
            last_modified=datetime.now().isoformat(),
        )

    content = decisions_path.read_text(encoding="utf-8")
    stat = decisions_path.stat()

    return FileResponse(
        path="M-memory/decisions.md",
        name="decisions.md",
        content=content,
        size=stat.st_size,
        last_modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
    )


@router.get("/memory/learning-log")
async def read_learning_log(admin_email: str = Depends(verify_admin_user)):
    """
    Read the M-memory/learning-log.md file directly.
    """
    log_path = ABC_TOM_ROOT / "M-memory" / "learning-log.md"
    if not log_path.exists():
        return FileResponse(
            path="M-memory/learning-log.md",
            name="learning-log.md",
            content="# Learning Log\n\nNo entries yet.\n",
            size=0,
            last_modified=datetime.now().isoformat(),
        )

    content = log_path.read_text(encoding="utf-8")
    stat = log_path.stat()

    return FileResponse(
        path="M-memory/learning-log.md",
        name="learning-log.md",
        content=content,
        size=stat.st_size,
        last_modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
    )
