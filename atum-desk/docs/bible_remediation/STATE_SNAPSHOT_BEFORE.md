# STATE_SNAPSHOT_BEFORE.md

**Timestamp**: 2026-02-15 01:20 SAST  
**Host**: Hera  
**User**: navi  
**CWD**: /data/ATUM DESK  

---

## 1. ATUM Services (Running)

| Service | State | Description |
|---|---|---|
| `atum-desk-api.service` | ✅ active (enabled) | Main FastAPI uvicorn on port 8000 |
| `atum-desk-job-worker.service` | ✅ active (running) | PostgreSQL-backed job queue |
| `atum-desk-rag-worker.service` | ✅ active (running) | RAG vector indexing |
| `atum-desk-sla-worker.service` | ✅ active (running) | SLA breach checker |
| `atum-desk-watchdog.timer` | ✅ enabled | Watchdog health timer |

## 2. Stale Leviathan Services (STILL IN SYSTEMD)

27 Leviathan service files remain in `/etc/systemd/system/`. Two are actively running.

| Service | State | Action Needed |
|---|---|---|
| `lev-opa.service` | RUNNING | Stop + disable + delete |
| `leviathan-updater.service` | FAILED | Disable + delete |
| `prometheus-node-exporter.service` | RUNNING | Stop + disable + delete |
| Other 24 leviathan-*.service files | Inactive | Delete |

## 3. Port Map

| Port | Owner | Purpose |
|---|---|---|
| 8000 | python (uvicorn) | ATUM DESK API + SPA |
| 5432 | postgres | PostgreSQL 16 |
| 11434 | ollama | Ollama LLM server |
| 80 | nginx | HTTP proxy |
| 443 | nginx | HTTPS proxy |
| 22 | sshd | SSH |

## 4. Runtime Versions

| Component | Version |
|---|---|
| Python | 3.10.12 |
| Node.js | v20.20.0 |
| PostgreSQL | 16 |
| Venv | `/data/ATUM DESK/atum-desk/api/.venv` |

## 5. Disk & Memory

| Resource | Used | Available |
|---|---|---|
| `/` (root) | 38G / 47G (86%) | 6.5G free |
| `/data` | 49G / 301G (18%) | 237G free |
| RAM | 10Gi / 15Gi | 5.1Gi available |

## 6. Database State

| Item | Value |
|---|---|
| Alembic HEAD | `phase11_provenance_gate` |
| Total tables | 63 |
| Connection | `postgres:postgres@localhost:5432/atum_desk` |
| Latency | 6.91ms |

## 7. Health Check Results

| Endpoint | Response |
|---|---|
| `GET /health` | ✅ `{"status":"healthy","version":"1.0.0"}` |
| `GET /api/v1/health` | ✅ DB connected (6.91ms), disk OK |

## 8. Log Health (Last 1h)

All ATUM services: **0 errors, 0 warnings**.
