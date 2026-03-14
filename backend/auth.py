import json
import os
import traceback
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import Header, HTTPException
from dotenv import load_dotenv

load_dotenv()

def initialize_firebase_admin():
    with open("startup.log", "a") as f:
        f.write(">>> CALLING initialize_firebase_admin()\n")
        if firebase_admin._apps:
            f.write(">>> Firebase Admin already initialized. Skipping.\n")
            return
            
        service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT")
        if not service_account_json:
            f.write(">>> Warning: FIREBASE_SERVICE_ACCOUNT env var not found.\n")
            return

        f.write(f">>> Found FIREBASE_SERVICE_ACCOUNT (length: {len(service_account_json)})\n")

    try:
        json_str = service_account_json.strip()
        print(f">>> json_str starts with: {json_str[:20]!r}")
        print(f">>> json_str ends with: {json_str[-20:]!r}")
        
        if (json_str.startswith("'") and json_str.endswith("'")) or (json_str.startswith('"') and json_str.endswith('"')):
            json_str = json_str[1:-1]
        
        # Don't replace if it already looks like a valid JSON object starting with {
        if not json_str.strip().startswith("{"):
             json_str = json_str.replace("\\n", "\n")
        
        print(f">>> After cleanup, starts with: {json_str.strip()[:20]!r}")
        
        cred_dict = json.loads(json_str)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        with open("startup.log", "a") as f:
            f.write(">>> Firebase Admin: Initialized successfully\n")
    except Exception as e:
        error_msg = f"FIREBASE INIT ERROR: {str(e)}\n{traceback.format_exc()}"
        with open("startup.log", "a") as f:
            f.write(f">>> {error_msg}\n")
        with open("firebase_error.log", "w") as f:
            f.write(error_msg)

print(">>> auth.py module loaded")
initialize_firebase_admin()

def verify_admin_user(authorization: str = Header(None)) -> str:
    # Double-check initialization for late-running workers
    initialize_firebase_admin()
    
    """
    FastAPI Dependency that extracts the Firebase Bearer token,
    verifies it, checks if the email is an admin, and returns the email.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Token")
    
    token = authorization.split(" ")[1]
    
    # Parse admin emails from .env
    admin_emails_str = os.getenv("ADMIN_EMAILS", "")
    admin_emails = [e.strip() for e in admin_emails_str.split(",") if e.strip()]

    try:
        decoded_token = auth.verify_id_token(token)
        email = decoded_token.get("email")
        
        if email not in admin_emails:
            raise HTTPException(status_code=403, detail=f"Not Authorized: {email} is not an admin")
            
        return email
        
    except Exception as e:
        print(f"[Auth Error] {e}")
        raise HTTPException(status_code=401, detail="Invalid Token")
