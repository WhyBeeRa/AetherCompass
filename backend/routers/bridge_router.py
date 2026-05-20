import os
import json
import re
from fastapi import APIRouter, Depends, HTTPException, Header, Body
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from persistence import AetherVault

router = APIRouter(
    prefix="/api/admin/bridge",
    tags=["Local-to-Prod Bridge"]
)

vault = AetherVault()
UNSPLASH_PATTERN = re.compile(r"https?://images\.unsplash\.com/", re.IGNORECASE)

def verify_bridge_key(authorization: str = Header(None)):
    """Simple strong API key validation for the server-to-server bridge."""
    expected_key = os.getenv("ADMIN_API_KEY")
    if not expected_key:
        # Fallback to dev mode if env is not fully configured, though in prod it should be set
        expected_key = "dev_secret_bridge_key_123!"
        
    # Check if header matches (could be passed as Bearer or just raw)
    if authorization == expected_key or authorization == f"Bearer {expected_key}":
        return True
        
    raise HTTPException(status_code=403, detail="Invalid or missing ADMIN_API_KEY")

class AuditUpdatePayload(BaseModel):
    trust_score: float
    executive_summary: str
    time_to_value: str
    privacy_grade: str
    skill_multiplier: str

@router.get("/pending")
def get_pending_audits(authorized: bool = Depends(verify_bridge_key)):
    """
    Returns a list of tools where audit_pending == True.
    """
    pending = vault.get_audit_pending_tools()
    return {"status": "success", "tools": pending}

@router.put("/update/{tool_id}")
def update_tool_audit(tool_id: str, payload: AuditUpdatePayload, authorized: bool = Depends(verify_bridge_key)):
    """
    Accepts JSON payload from local factory, updates tool, clears Unsplash placeholders, and sets audit_pending = False.
    """
    success = vault.apply_bridge_audit_update(
        tool_id=tool_id,
        trust_score=payload.trust_score,
        executive_summary=payload.executive_summary,
        time_to_value=payload.time_to_value,
        privacy_grade=payload.privacy_grade,
        skill_multiplier=payload.skill_multiplier
    )
    if not success:
        raise HTTPException(status_code=404, detail="Tool not found")
        
    return {"status": "success", "message": f"Tool {tool_id} updated and marked as audited."}

@router.post("/trigger/{tool_id}")
def trigger_tool_audit(tool_id: str, authorized: bool = Depends(verify_bridge_key)):
    """
    Sets audit_pending = True for a specific tool so the local engine will pick it up.
    """
    success = vault.set_audit_pending(tool_id, True)
    if not success:
        raise HTTPException(status_code=404, detail="Tool not found")
        
    return {"status": "success", "message": f"Tool {tool_id} added to audit queue."}
