# IMPACT_NOTE.md - ATUM DESK Enhancement Deployment

**Date:** 2026-02-13

---

## What Will Change

### New Database Tables
- `job_queue` - PostgreSQL-backed job queue
- `job_events` - Job event log
- `ticket_ai_triage` - AI triage results
- `ai_suggestions` - Smart reply/KB suggestions
- `ticket_kb_suggestions` - KB article suggestions
- `metrics_snapshots` - Dashboard metrics snapshots
- `org_settings` - Organization settings

### New Columns (tickets table)
- `time_to_breach_minutes` - SLA prediction
- `sla_risk_score` - SLA risk percentage

### New Files
- `migrations/versions/phase4_job_queue_ai.py` - Alembic migration
- `scripts/job_worker.py` - Job worker script
- `infra/systemd/atum-desk-job-worker.service` - Systemd unit

### New API Endpoints
- `/api/v1/metrics` - Prometheus metrics (NEW)

### Modified Services
- atum-desk-api - Additional endpoints
- atum-desk-job-worker (NEW)

---

## Dependencies

| Component | Depends On |
|-----------|------------|
| job_worker.py | psycopg, httpx, structlog |
| Metrics endpoint | prometheus-client |
| Ticket → Job enqueue | job_queue table |

---

## What Can Break

| Failure Mode | Probability | Impact | Mitigation |
|--------------|-------------|--------|------------|
| Migration fails | LOW | Service down | Rollback migration |
| Job worker crashes | LOW | Jobs queue | Auto-restart systemd |
| Metrics endpoint slow | LOW | API slow | Non-blocking |
| Redis conflict | NONE | None | Redis will be disabled |

---

## What Must NOT Change

- Existing API endpoints (must remain functional)
- Database schema for tickets, users, organizations (only adding columns)
- RAG system (must remain intact)
- SLA worker (must remain running)
- Authentication flow

---

## Restarts Required

1. alembic upgrade head (database)
2. sudo systemctl daemon-reload
3. sudo systemctl enable --now atum-desk-job-worker.service
4. sudo systemctl restart atum-desk-api

---

## Rollback Trigger Conditions

- Migration fails to apply
- Any existing endpoint returns 500
- Service fails to start
- Database connection errors

---

## Rollback Steps

```bash
# 1. Stop job worker
sudo systemctl stop atum-desk-job-worker

# 2. Rollback migration
cd /data/ATUM DESK/atum-desk/api
alembic downgrade phase3_rag_graph

# 3. Restart API
sudo systemctl restart atum-desk-api

# 4. Verify
curl http://localhost:8000/api/v1/health
```

---

*Impact analysis complete*
