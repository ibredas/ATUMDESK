#!/bin/bash
# ATUM DESK API Startup Script

export PYTHONPATH="/data/ATUM DESK/atum-desk/api"
export ENVIRONMENT="production"
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/atum_desk"
export REDIS_URL="redis://localhost:6379/0"
export SECRET_KEY="atum-desk-production-secret-key-change-this"

cd "/data/ATUM DESK/atum-desk/api"
exec "/data/ATUM DESK/atum-desk/api/.venv/bin/uvicorn" app.main:app --host 0.0.0.0 --port 8000 --workers 2
