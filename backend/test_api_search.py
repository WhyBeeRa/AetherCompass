import requests
import json

base_url = "http://localhost:8000"

def test_search(query):
    print(f"\nTesting search for: '{query}'")
    try:
        resp = requests.get(f"{base_url}/search/intent?q={query}")
        if resp.status_code == 200:
            results = resp.json()
            print(f"Results found: {len(results)}")
            print(json.dumps(results, indent=2))
        else:
            print(f"Error {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    test_search("Build a React app")
