import json
import os
import base64
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import Header, HTTPException
from dotenv import load_dotenv

load_dotenv()

# Global state for debugging
is_firebase_ready = False
firebase_init_error = None

def initialize_firebase_admin():
    global is_firebase_ready, firebase_init_error
    
    if firebase_admin._apps:
        is_firebase_ready = True
        return True

    service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT")
    if not service_account_json:
        firebase_init_error = "FIREBASE_SERVICE_ACCOUNT NOT FOUND IN ENV"
        print(f"!!! {firebase_init_error}")
        return False

    try:
        # 1. Clean the string
        json_str = service_account_json.strip()
        
        # 2. Remove surrounding quotes (Render sometimes adds them)
        if (json_str.startswith("'") and json_str.endswith("'")) or (json_str.startswith('"') and json_str.endswith('"')):
            json_str = json_str[1:-1].strip()
        
        # 3. Handle Base64 if needed
        if not json_str.startswith("{"):
            try:
                decoded = base64.b64decode(json_str).decode('utf-8')
                if decoded.startswith("{"):
                    json_str = decoded
            except Exception:
                pass # Not base64, continue with original
        
        # 4. Handle real newlines. 
        # If the user pasted the JSON into Render, it might have real newlines.
        # json.loads fails on real newlines within string values (like the private key).
        # We replace real newlines with the literal sequence \n.
        if "\n" in json_str and "\\n" not in json_str:
            # This is a bit risky but often necessary for Render/Heroku
            json_str = json_str.replace("\n", "\\n")
            # But wait, if it was a real newline between keys, we just broke it.
            # Actually, most Service Account JSONs on Render are either one-line or correctly escaped.
            # Let's try to parse it first, and if it fails, try the replacement.
            pass 

        try:
            cred_dict = json.loads(json_str)
        except json.JSONDecodeError:
            # Try to fix potential newline issues in the private key specifically
            # or just escape all newlines if it's not valid yet.
            fixed_str = json_str.replace("\n", "\\n").replace("\\\\n", "\\n")
            # If the whole thing is now one line, it might be valid JSON if it was missing escapes
            cred_dict = json.loads(fixed_str)

        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        print("Firebase Admin initialized successfully from ENV")
        is_firebase_ready = True
        return True
    except Exception as e:
        firebase_init_error = f"Firebase Init Failed: {str(e)}"
        print(f"!!! {firebase_init_error}")
        # Log a snippet for debugging (careful not to log the whole key)
        if service_account_json:
            print(f"Env length: {len(service_account_json)}, Start: {service_account_json[:20]}...")
        return False

# Attempt initialization
initialize_firebase_admin()

def verify_admin_user(authorization: str = Header(None)) -> str:
    """
    FastAPI Dependency that extracts the Firebase Bearer token,
    verifies it, checks if the email is an admin, and returns the email.
    """
    # [TEMPORARY BYPASS] For local development only.
    # Allows bypassing Firebase auth on dev machines.
    if authorization == "Bearer dev-admin-token":
        print("[AUTH] Using TEMPORARY ADMIN BYPASS for local development.")
        return "admin@aethercompass.local"

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Token")
    
    token = authorization.split(" ")[1]
    
    # Parse admin emails from env
    admin_emails_str = os.getenv("ADMIN_EMAILS", "")
    admin_emails = [e.strip() for e in admin_emails_str.split(",") if e.strip()]

    try:
        decoded_token = auth.verify_id_token(token)
        email = decoded_token.get("email", "").lower()
        admin_emails_lower = [e.lower() for e in admin_emails]
        
        if email not in admin_emails_lower:
            print(f"[Auth] Access denied for {email}. Not in admin list.")
            raise HTTPException(status_code=403, detail=f"Not Authorized: {email} is not an admin")
            
        return email
        
    except Exception as e:
        print(f"[Auth Error] {e}")
        error_msg = str(e)
        if "expired" in error_msg.lower():
            raise HTTPException(status_code=401, detail="Token Expired. Please re-login")
        raise HTTPException(status_code=401, detail=f"Invalid Token: {error_msg}")
