import time
import requests
import sys

API_BASE = "http://localhost:8000"

def test_flow(query: str):
    print(f"--- Testing Flow for Query: '{query}' ---")
    
    # 1. Trigger Pipeline
    start_time = time.time()
    print("[1] Triggering pipeline POST /pipeline/trigger...")
    try:
        resp = requests.post(f"{API_BASE}/pipeline/trigger?tool_name={query}")
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"Failed to trigger: {e}")
        return

    task_id = data.get("task_id")
    print(f"    Task ID acquired: {task_id}")
    trigger_latency = time.time() - start_time
    print(f"    Trigger Latency: {trigger_latency:.3f}s\n")
    
    # 2. Poll Status
    print("[2] Polling /pipeline/status/{task_id}...")
    poll_start_time = time.time()
    
    while True:
        try:
            status_resp = requests.get(f"{API_BASE}/pipeline/status/{task_id}")
            status_resp.raise_for_status()
            status_data = status_resp.json()
            status = status_data.get("status")
            
            elapsed = time.time() - poll_start_time
            print(f"    Status: {status} (Elapsed: {elapsed:.1f}s)")
            
            if status in ["completed", "completed_rejected", "error"] or status.startswith("failed"):
                break
                
            time.sleep(1)
            
        except Exception as e:
            print(f"Failed polling: {e}")
            return
            
    processing_latency = time.time() - poll_start_time
    print(f"\n[3] Pipeline Resolved with status: {status}")
    print(f"    Total Processing Time: {processing_latency:.3f}s\n")
    
    # 3. Fetch Feed
    print("[4] Fetching /gallery/feed...")
    feed_start_time = time.time()
    try:
        feed_resp = requests.get(f"{API_BASE}/gallery/feed")
        feed_resp.raise_for_status()
        feed_data = feed_resp.json()
    except Exception as e:
        print(f"Failed fetching feed: {e}")
        return
        
    feed_latency = time.time() - feed_start_time
    print(f"    Feed length: {len(feed_data)} items")
    print(f"    Feed Latency: {feed_latency:.3f}s\n")
    
    print(f"--- Flow Complete (Total E2E time: {time.time() - start_time:.3f}s) ---")

if __name__ == "__main__":
    test_query = "AI Design Assistant" if len(sys.argv) < 2 else sys.argv[1]
    test_flow(test_query)
