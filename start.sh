#!/bin/bash
# Start script for Render
# If we're in the root, cd into backend
if [ -d "backend" ]; then
    cd backend
fi

# Run uvicorn
# Use the PORT environment variable if provided by Render, else default to 8000
PORT=${PORT:-8000}
python -m uvicorn main:app --host 0.0.0.0 --port $PORT
