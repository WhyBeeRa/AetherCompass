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

        # Try to use API key approach first (simpler)
        api_key = os.getenv("GEMINI_API_KEY")  # Using the same key for Firebase
        if api_key:
            try:
                # For Firebase Admin SDK, we need service account credentials
                # But for now, let's try to initialize without credentials for basic functionality
                firebase_admin.initialize_app()
                with open("startup.log", "a") as f:
                    f.write(">>> Firebase Admin: Initialized without credentials (limited functionality)\n")
                return
            except Exception as e:
                with open("startup.log", "a") as f:
                    f.write(f">>> Firebase Admin fallback failed: {e}\n")

        # If API key approach fails, try the service account approach
        service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT")
        if not service_account_json:
            with open("startup.log", "a") as f:
                f.write(">>> Warning: FIREBASE_SERVICE_ACCOUNT env var not found. Firebase auth will not work.\n")
            return

        f.write(f">>> Found FIREBASE_SERVICE_ACCOUNT (length: {len(service_account_json)})\n")

    try:
        json_str = service_account_json.strip()

        # Remove surrounding quotes if present
        if (json_str.startswith("'") and json_str.endswith("'")) or (json_str.startswith('"') and json_str.endswith('"')):
            json_str = json_str[1:-1]

        # If it looks like a private key, try to construct minimal service account JSON
        if json_str.startswith("-----BEGIN PRIVATE KEY-----") or not json_str.strip().startswith("{"):
            # This is just a private key, construct minimal service account JSON
            # We'll use placeholder values for the missing fields
            cred_dict = {
                "type": "service_account",
                "project_id": "aethercompass-prod-42214",
                "private_key_id": "placeholder-key-id",
                "private_key": json_str.replace("\\n", "\n"),
                "client_email": "firebase-adminsdk-placeholder@aethercompass-prod-42214.iam.gserviceaccount.com",
                "client_id": "placeholder-client-id",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-placeholder@aethercompass-prod-42214.iam.gserviceaccount.com"
            }
            json_str = json.dumps(cred_dict)
        else:
            # It's already JSON, clean it up
            json_str = json_str.replace("\\n", "\n")

        print(f">>> Final json_str starts with: {json_str.strip()[:50]!r}")

        cred_dict = json.loads(json_str)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        with open("startup.log", "a") as f:
            f.write(">>> Firebase Admin: Initialized successfully with service account\n")
    except Exception as e:
        error_msg = f"FIREBASE INIT ERROR: {str(e)}\n{traceback.format_exc()}"
        with open("startup.log", "a") as f:
            f.write(f">>> {error_msg}\n")
        with open("firebase_error.log", "w") as f:
            f.write(error_msg)
        # Don't raise exception, let the app start without Firebase auth
        with open("startup.log", "a") as f:
            f.write(">>> Continuing without Firebase authentication\n")

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
    
    # Parse admin emails from env
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
