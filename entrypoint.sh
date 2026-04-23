#!/bin/sh
set -e

uv run python seed.py
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
