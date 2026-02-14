# RC GATE - PHASE 2

## Release Criteria Checkpoint

### ✅ Core Infrastructure

| Criteria | Evidence |
|----------|----------|
| API Service Running | `systemctl status atum-desk-api` - active (running) |
| Web UI Accessible | Frontend served at / via FastAPI |
| Database Connected | PostgreSQL 16 on localhost:5432 |
| TLS/HTTPS Working | Certificate valid until Feb 2027 |
| HTTP→HTTPS Redirect | 301 redirect configured |

### ✅ SLA Lifecycle

| Criteria | Evidence |
|----------|----------|
| SLA Starts on ACCEPT | `sla_started_at` set when ticket accepted |
| SLA Due Calculated | `sla_due_at` computed from policy |
| Pause on WAITING_CUSTOMER | `sla_paused_at` set on status change |
| Unpause on Exit | Duration accumulated, pause cleared |
| Worker Respects Pauses | Worker skips WAITING_CUSTOMER tickets |

### ✅ Hardening

| Criteria | Evidence |
|----------|----------|
| Request Size Limit | nginx: 10MB, FastAPI: 50MB |
| Rate Limiting | API: 10r/s, Login: 1r/s |
| Extension Whitelist | 24 safe types configured |
| Backups | Script exists, cron scheduled (2 AM daily) |
| Security Headers | HSTS, X-Frame, CSP, etc. |

### ✅ Audit Logging

| Criteria | Evidence |
|----------|----------|
| Ticket Created | `ticket_created` event logged |
| Ticket Accepted | `ticket_accepted` event logged |
| Status Changes | `ticket_status_changed` event logged |
| Attachments | Upload/download events logged |

### ✅ Phase 2 Modules

| Module | Routes | Status |
|--------|--------|--------|
| Knowledge Base | `/api/v1/kb/*` | ✅ Registered |
| Problems | `/api/v1/problems/*` | ✅ Registered |
| Changes | `/api/v1/changes/*` | ✅ Registered |
| Assets | `/api/v1/assets/*` | ✅ Registered |

### ✅ No Breaking Changes

- Existing ticket workflow preserved
- No database schema modifications
- No external API dependencies added
- No CDN leaks (fonts local)

---

## Deployment Verified

- **Commit**: 16edf6e859ca96aacb85ee67c44be9de9bab6486
- **API Service**: Running (4 workers)
- **SLA Worker**: Running (60s interval)
- **Services**: All healthy

---

## Ready for Release

**Status**: ✅ PASSED ALL CHECKS

Phase 2 is ready for production deployment.
