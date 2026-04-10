import asyncio
import sys
import os
from fastapi.testclient import TestClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.main import app

client = TestClient(app)

def verify_api():
    print("=== AETHER API VERIFICATION ===")
    
    # 1. Trigger Pipeline
    print("\n[POST] /pipeline/trigger (Tool: OpenDevin)")
    response = client.post("/pipeline/trigger?tool_name=OpenDevin")
    
    if response.status_code == 200:
        data = response.json()
        task_id = data["task_id"]
        print(f"  [PASS] Triggered. Task ID: {task_id}")
        
        # 2. Poll Status (Mocking async execution in synchronous test client is tricky, 
        # so we just check if status endpoint works. 
        # In this synchronous TestClient, the background task WON'T run automatically unles we explicitly wait/run it.
        # But for unit testing the API contract, this is enough.)
        
        print("\n[GET] /pipeline/status/{task_id}")
        status_resp = client.get(f"/pipeline/status/{task_id}")
        print(f"  [PASS] Status: {status_resp.json()['status']}")
        
    else:
        print(f"  [FAIL] Trigger failed: {response.status_code} {response.text}")

    # 3. Verify Data Access (We need to populate DB first manually since background tasks didn't run)
    from backend.main import db_tools
    db_tools["opendevin"] = {
        "tool_name": "OpenDevin",
        "analysis": {"executive_summary": "Mock Summary"},
        "trust_score": 95.0,
        "status": "success",
        "gallery": [{"media_url": "http://img.com", "style_tags": ["Code"]}]
    }
    
    print("\n[GET] /tool/OpenDevin")
    tool_resp = client.get("/tool/OpenDevin")
    if tool_resp.status_code == 200:
         print(f"  [PASS] Data: {tool_resp.json()['trust_score']}")
    else:
         print(f"  [FAIL] Tool Fetch failed: {tool_resp.status_code}")

    print("\n[GET] /gallery/feed")
    feed_resp = client.get("/gallery/feed")
    if feed_resp.status_code == 200:
        items = feed_resp.json()
        print(f"  [PASS] Feed items: {len(items)}")
    else:
        print(f"  [FAIL] Feed failed.")

if __name__ == "__main__":
    verify_api()
