import requests
import json

# Replace with an actual token if needed, or mock it in a test env
# But I can just check the endpoint existence

url = "http://127.0.0.1:8000/admin/vault/tool/test"
try:
    # This should fail with 401/403 since no token, proving it exists
    res = requests.delete(url)
    print(f"Status: {res.status_code}")
    print(f"Detail: {res.json()}")
except Exception as e:
    print(f"Error: {e}")
