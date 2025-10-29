#!/bin/sh
echo "Running Alembic migrations..."
uv run alembic upgrade head

echo "Starting FastAPI server..."
uvicorn main:app --host 0.0.0.0 --port 8000
