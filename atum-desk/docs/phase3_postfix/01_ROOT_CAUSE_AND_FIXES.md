# Root Cause Analysis & Fixes

**Date**: 2026-02-13

---

## Issue 1: PostgreSQL Connection - FATAL: role "atum" does not exist

### Root Cause
- Default alembic/env.py was using `postgresql://atum:atum@localhost:5432/atum_desk`
- But actual credentials in `.env` are `postgresql+asyncpg://postgres:postgres@localhost:5432/atum_desk`

### Fix Applied
- Updated all scripts and worker to use correct DATABASE_URL from `.env`
- Verified connection works with `postgres` user

### Canonical DATABASE_URL (redacted)
```
DATABASE_URL=postgresql+asyncpg://postgres:****@localhost:5432/atum_desk
```

---

## Issue 2: Systemd RAG Worker - status=203/EXEC

### Root Cause
- ExecStart path contained spaces: `/data/ATUM DESK/...`
- systemd cannot handle spaces in path without proper escaping

### Fix Applied
- Updated service file to use:
  - `WorkingDirectory=/data/ATUM DESK/atum-desk/api`
  - `EnvironmentFile=/data/ATUM DESK/atum-desk/api/.env`
  - `ExecStart=/bin/bash -lc "/data/ATUM DESK/.venv/bin/python scripts/rag_worker.py"`

### New Unit File
```ini
[Service]
WorkingDirectory=/data/ATUM DESK/atum-desk/api
EnvironmentFile=/data/ATUM DESK/atum-desk/api/.env
ExecStart=/bin/bash -lc "/data/ATUM DESK/.venv/bin/python scripts/rag_worker.py"
Restart=always
RestartSec=3
```

---

## Summary

| Issue | Root Cause | Fix |
|-------|------------|-----|
| DB Connection | Wrong credentials | Use postgres:postgres from .env |
| Systemd 203 | Path with spaces | Use /bin/bash -lc wrapper |
