#!/bin/bash
# Start script for Render
# CRITICAL: --workers 1 to prevent FastEmbed model RAM duplication (~130MB per worker)
# On Render free tier (512MB), multiple workers would cause OOM crash.

PORT=${PORT:-8000}
python -m uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1
