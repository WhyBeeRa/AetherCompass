import json
import os
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import Header, HTTPException
from dotenv import load_dotenv

load_dotenv()

def initialize_firebase_admin():
    if firebase_admin._apps:
        return True

    service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT")
    if not service_account_json:
        print("FIREBASE_SERVICE_ACCOUNT NOT FOUND")
        return False

    try:
        json_str = service_account_json.strip()
        # Remove surrounding quotes if present
        if (json_str.startswith("'") and json_str.endswith("'")) or (json_str.startswith('"') and json_str.endswith('"')):
            json_str = json_str[1:-1]
        
        # Unescape escaped newlines if they are literal backslash+n
        json_str = json_str.replace("\\\\n", "\\n").replace("\\n", "\n")
        
        cred_dict = json.loads(json_str)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        print("Firebase Admin initialized successfully")
        return True
    except Exception as e:
        print(f"Firebase Init Error: {e}")
        return False

# Attempt initialization
is_firebase_ready = initialize_firebase_admin()

def verify_admin_user(authorization: str = Header(None)) -> str:
    """
    FastAPI Dependency that extracts the Firebase Bearer token,
    verifies it, checks if the email is an admin, and returns the email.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Token")
    
    token = authorization.split(" ")[1]
    
    # Parse admin emails from env
    admin_emails_str = os.getenv("ADMIN_EMAILS", "")
    admin_emails = [e.strip() for e in admin_emails_str.split(",") if e.strip()]

    try:
        decoded_token = auth.verify_id_token(token)
        email = decoded_token.get("email")
        
        if email not in admin_emails:
            print(f"[Auth] Access denied for {email}. Not in admin list.")
            raise HTTPException(status_code=403, detail=f"Not Authorized: {email} is not an admin")
            
        return email
        
    except Exception as e:
        print(f"[Auth Error] {e}")
        error_msg = str(e)
        if "expired" in error_msg.lower():
            raise HTTPException(status_code=401, detail="Token Expired. Please re-login.")
        raise HTTPException(status_code=401, detail=f"Invalid Token: {error_msg}")
