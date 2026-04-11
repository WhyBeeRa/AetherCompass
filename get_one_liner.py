import os
import json
import base64
from dotenv import load_dotenv

def main():
    # Load .env from backend folder specifically
    load_dotenv("backend/.env")
    
    js_str = os.getenv("FIREBASE_SERVICE_ACCOUNT")
    if not js_str:
        print("Error: FIREBASE_SERVICE_ACCOUNT not found in backend/.env")
        return

    try:
        # Clean surrounding quotes
        js_str = js_str.strip()
        if (js_str.startswith("'") and js_str.endswith("'")) or (js_str.startswith('"') and js_str.endswith('"')):
            js_str = js_str[1:-1]
            
        # Parse it to make sure it's valid
        data = json.loads(js_str)
        
        # Convert to one-line JSON string
        one_liner = json.dumps(data)
        
        # Base64 encode it for safety
        b64_str = base64.b64encode(one_liner.encode()).decode()
        
        print("\n--- COPY THIS BASE64 BLOCK ---")
        print(b64_str)
        print("--- END OF BLOCK ---\n")
        print("This is much safer for Render. Paste this into your FIREBASE_SERVICE_ACCOUNT environment variable.")
        
    except Exception as e:
        print(f"Error processing JSON: {e}")

if __name__ == "__main__":
    main()
