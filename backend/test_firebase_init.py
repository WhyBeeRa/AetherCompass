import os
import json
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, auth

def test_init():
    load_dotenv()
    service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT")
    if not service_account_json:
        print("Error: FIREBASE_SERVICE_ACCOUNT not found in .env")
        return

    try:
        if (service_account_json.startswith("'") and service_account_json.endswith("'")) or (service_account_json.startswith('"') and service_account_json.endswith('"')):
            service_account_json = service_account_json[1:-1]
        
        # DEBUG: Print the character at 172 and surrounding context
        print(f"String length: {len(service_account_json)}")
        if len(service_account_json) > 180:
            print(f"Char at 172: {service_account_json[172]!r}")
            print(f"Context: {service_account_json[160:185]!r}")
            
        # Try loading WITHOUT the manual replace first
        try:
            cred_dict = json.loads(service_account_json)
            print("Successfully loaded JSON without manual replace")
        except Exception as e1:
            print(f"Default load failed: {e1}")
            # Try with the manual replace
            service_account_json_replaced = service_account_json.replace("\\n", "\n")
            cred_dict = json.loads(service_account_json_replaced)
            print("Successfully loaded JSON WITH manual replace")

        cred = credentials.Certificate(cred_dict)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        print("Success: Firebase Admin initialized successfully!")
        
        # Test parsing ADMIN_EMAILS
        admin_emails_str = os.getenv("ADMIN_EMAILS", "")
        admin_emails = [e.strip() for e in admin_emails_str.split(",") if e.strip()]
        print(f"Admin Emails: {admin_emails}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_init()
