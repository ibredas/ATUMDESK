# STATE SNAPSHOT - BEFORE CHANGES

**Timestamp:** 2026-02-14T23:34:19+02:00  
**Host:** Hera  
**User:** navi  
**Working Directory:** /data/ATUM DESK

---

## 1. SYSTEM INFORMATION

### Runtime
- **Python:** 3.10.12 (GCC 13.3.0)
- **PostgreSQL:** 16.x (running on localhost:5432)
- **Redis:** Running on localhost:6379
- **nginx:** Running (master + 4 workers)

### Services Running
| Service | PID | Port | Status |
|---------|-----|------|--------|
| PostgreSQL | 1973 | 5432 | Running |
| nginx | 222253 | 80/443 | Running |
| API (uvicorn) | 823558 | 8000 | Running (4 workers) |
| RAG Worker | 324772 | - | Running |
| Job Worker | 501596 | - | Running |

---

## 2. DATABASE STATE

### Table Count
- **Total tables:** 60

### RLS-Enabled Tables (9)
| Table | RLS Enabled | Policy Count |
|-------|-------------|--------------|
| assets | true | 1 |
| audit_log | true | 1 |
| change_requests | true | 1 |
| kb_articles | true | 1 |
| organizations | true | 1 |
| problems | true | 1 |
| services | true | 1 |
| tickets | true | 1 |
| users | true | 1 |

### AI Tables (NOT RLS enabled)
- ticket_ai_triage
- ai_suggestions
- copilot_runs
- ticket_kb_suggestions
- job_queue
- rag_documents, rag_chunks, rag_nodes, rag_edges

### Key Columns
- Tables with `organization_id`: 40
- Tables without `organization_id`: 20 (includes join tables)

---

## 3. ATTACHMENTS TABLE

```
attachments columns:
- id, ticket_id, comment_id
- filename, original_filename, file_path
- file_size, mime_type, file_hash
- uploaded_by, access_count, last_accessed_at, created_at
```

**Missing columns for security:**
- scan_status (not present)
- scanned_at (not present)
- scanner_version (not present)
- scan_result_text (not present)

---

## 4. AUDIT_LOG TABLE

```
audit_log columns:
- id, organization_id, user_id
- action, entity_type, entity_id
- old_values (json), new_values (json)
- ip_address, user_agent, created_at
```

**Missing columns for hash chain:**
- prev_hash (not present)
- row_hash (not present)
- chain_scope (not present)

---

## 5. SYSTEMD SERVICES

| Service File | Purpose |
|--------------|---------|
| atum-desk-api.service | Main FastAPI application |
| atum-desk-job-worker.service | Background job processor |
| atum-desk-rag-worker.service | RAG indexing worker |
| atum-desk-sla-worker.service | SLA processing worker |
| atum-desk-metrics-worker.service | Metrics collection |
| atum-desk-ws.service | WebSocket service |
| atum-desk-watchdog.service | Health monitoring |

---

## 6. KEY DIRECTORIES

| Path | Purpose |
|------|---------|
| /data/ATUM DESK/atum-desk/api | Application code |
| /data/ATUM DESK/atum-desk/infra | Infrastructure (nginx, systemd) |
| /data/ATUM DESK/atum-desk/data | Uploaded files |
| /data/ATUM DESK/atum-desk/docs | Documentation |

---

## 7. WORKER STATUS

### RAG Worker
- PID: 324772
- Status: Running
- Org Context: Sets per job from rag_index_queue.organization_id

### Job Worker  
- PID: 501596
- Status: Running
- Org Context: Sets per job via set_org_context()

### SLA Worker
- Status: NOT RUNNING (checked via systemctl)
- Issue: Need to verify org context handling

---

## 8. EXISTING SECURITY

### Rate Limiting (App-Level)
- Login: 5 attempts per 15 minutes (config.py)
- API: 100 requests per minute
- Ticket create: 10 per hour

### Rate Limiting (NGINX)
- NOT CONFIGURED (gap identified)

### Login Lockout
- Table: auth_login_attempts exists
- Max attempts: 5
- Lockout duration: 15 minutes

---

## 9. FILES TO BE MODIFIED

| File | Change Type |
|------|-------------|
| app/db/session.py | Enhanced context setter |
| app/middleware/rls_context.py | Safety alarm + health |
| app/routers/internal.py | New RLS health endpoint |
| scripts/run_sla_worker.py | Org-by-org processing |
| migrations/ | New migration for AI tables RLS, audit hash |
| app/services/attachment_scanner.py | New ClamAV integration |
| app/routers/attachments.py | Scan integration |
| infra/nginx/atum-desk.conf | Rate limiting zones |
| scripts/verify_audit_chain.py | New verification script |
| infra/systemd/ | New timers |

---

## 10. VERIFICATION STATUS

### ✅ Green
- PostgreSQL running and accepting connections
- API responding on port 8000
- RLS enabled on 9 tenant tables
- Job worker and RAG worker running with org context

### ⚠️ Yellow
- SLA worker status unclear (not running as systemd)
- NGINX rate limiting not configured
- AI tables without RLS
- Attachment scanning not implemented
- Audit hash chain not implemented

### ❌ Red
- None identified (system is operational)

---

**END OF SNAPSHOT**
