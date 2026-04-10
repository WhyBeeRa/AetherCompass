import socket
import sys
import time
import subprocess
import os

def check_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def main():
    print("=== Aether Environment Guard ===")
    
    ports = {
        "Backend (FastAPI)": 8000,
        "Frontend (Vite)": 5173
    }
    
    all_healthy = True
    
    for name, port in ports.items():
        if check_port(port):
            print(f"[OK] {name} is running on port {port}.")
        else:
            print(f"[ERR] {name} is NOT running on port {port}.")
            all_healthy = False
            
            # Auto-Recovery suggestions (Real implementation might try to start them)
            if port == 8000:
                print("    > Try running: uvicorn backend.main:app --reload")
            elif port == 5173:
                print("    > Try running: npm run dev")
    
    if all_healthy:
        print("\n[SUCCESS] Environment is healthy. Ready for development.")
        sys.exit(0)
    else:
        print("\n[FAIL] Environment check failed. Please start missing services.")
        sys.exit(1)

if __name__ == "__main__":
    main()
