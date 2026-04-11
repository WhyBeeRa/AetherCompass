#!/bin/bash
# Start script for Render
# If we're already in backend, don't try to cd.
# uvicorn handles the port via --port $PORT

PORT=${PORT:-8000}
python -m uvicorn main:app --host 0.0.0.0 --port $PORT
