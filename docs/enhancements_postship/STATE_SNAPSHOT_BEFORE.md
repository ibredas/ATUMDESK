# STATE_SNAPSHOT_BEFORE.md - ATUM DESK Enhancement Deployment

**Date:** 2026-02-13
**Time:** 15:30 UTC
**Host:** Hera
**User:** navi
**CWD:** /data/ATUM DESK

---

## Services Status (Pre-Deployment)

| Service | Status | Uptime |
|---------|--------|--------|
| atum-desk-api.service | active (running) | 4h 28m |
| atum-desk-rag-worker.service | active (running) | 4h 56m |
| atum-desk-sla-worker.service | active (running) | - |
| ollama.service | active (running) | 17h |
| postgresql | active (running) | - |
| redis | active (running) | - |

---

## Port Map

| Port | Service | PID |
|------|---------|-----|
| 8000 | atum-desk-api | 443469, 443468, 443467, 443466 |
| 5432 | postgresql | - |
| 6379 | redis | - |
| 11434 | ollama | 1782 |

---

## Key Paths

| Path | Purpose |
|------|---------|
| /data/ATUM DESK/atum-desk/api | API application |
| /data/ATUM DESK/atum-desk/infra/systemd | systemd units |
| /opt/atum-desk/data | Data exports |
| /data/ATUM DESK/atum-desk/data/uploads | File uploads |

---

## Runtime Versions

- Python: 3.10.12
- PostgreSQL: 16.x
- Node Exporter: Not installed
- Redis: 6.x (to be disabled)

---

## Database Tables (Current)

33 tables including:
- tickets, users, organizations
- kb_articles, kb_categories
- rag_documents, rag_chunks, rag_nodes, rag_edges
- sla_policies, sla_calculations
- audit_log

---

## Alembic Status

- Current: phase3_rag_graph
- Head: phase3_rag_graph
- Pending migration: phase4_job_queue_ai (ready to create)

---

## Pre-Deployment Health Check

### API Endpoints
- /api/v1/auth/login: ✅
- /api/v1/tickets: ✅
- /api/v1/analytics/dashboard: ✅
- /api/v1/rag/search: ✅
- /api/v1/internal/tickets/{id}/copilot: ✅ (47s response)
- /api/v1/etl/health: ✅ (Polars 1.12.0)

### Database
- Connection: ✅
- Tables exist: ✅
- HNSW index on rag_chunks: ✅

---

## Risk Assessment

| Area | Risk Level | Notes |
|------|------------|-------|
| Schema migration | MEDIUM | New tables + columns |
| Redis disable | LOW | Not used by Python |
| New worker service | MEDIUM | New systemd service |
| Monitoring endpoints | LOW | Read-only |

---

## Rollback Plan

1. alembic downgrade to phase3_rag_graph
2. Remove systemd unit atum-desk-job-worker.service
3. Revert API code changes
4. Restart services

---

*Snapshot taken before enhancement deployment*
