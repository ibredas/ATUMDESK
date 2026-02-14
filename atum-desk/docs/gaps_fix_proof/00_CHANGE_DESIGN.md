# CHANGE DESIGN - ATUM DESK GAPS FIX

**Date:** 2026-02-14  
**Goal:** Eliminate all critical internet-facing gaps for production deployment

---

## 1. GOAL & NON-GOALS

### Goals
- Fix RLS bootstrap issues (GAP-1)
- Fix worker org context (GAP-2)
- Add RLS to AI tables (GAP-3)
- Implement attachment safety with ClamAV (GAP-4)
- Add NGINX rate limiting (GAP-5)
- Implement audit hash chain (GAP-6)

### Non-Goals
- Do NOT break existing Phase 2+3 GraphRAG
- Do NOT change authentication flow
- Do NOT add external SaaS dependencies
- Do NOT use Docker/Celery/Redis for queuing

---

## 2. SUCCESS METRICS

| Metric | Target |
|--------|--------|
| RLS health check | Returns `healthy` |
| Worker org context | 100% of jobs have org_id |
| AI tables RLS | All 4+ tables protected |
| Attachment scanning | EICAR blocked |
| NGINX rate limit | 429 on excessive requests |
| Audit chain | Verify returns PASS |

---

## 3. ARCHITECTURE MAP

### Service Map
```
[Client] → [nginx:80] → [uvicorn:8000] → [PostgreSQL:5432]
                              ↓
                        [Workers]
                        - job_worker
                        - rag_worker  
                        - sla_worker
```

### Dataflow Map
```
Upload → Validate → ClamAV Scan → Move to uploads/
                                    ↓
                              Download → Headers hardened
```

### Integration Points
- `app/db/session.py` → PostgreSQL session context
- `app/middleware/rls_context.py` → RLS enforcement
- `scripts/*.py` → Worker processing
- `infra/nginx/atum-desk.conf` → Rate limiting

---

## 4. PROPOSED APPROACH

### GAP-1: RLS Bootstrap
- Enhance `set_org_context()` in session.py
- Add bootstrap-safe policies for users/organizations
- Add RLS health alarm in middleware
- Create `/internal/rls/health` endpoint

### GAP-2: Worker Org Context
- Update `run_sla_worker.py` to loop org-by-org
- Add org_id NOT NULL constraint to job_queue
- Validate org_id in job processing

### GAP-3: AI Tables RLS
- Create migration to enable RLS on:
  - ticket_ai_triage
  - ai_suggestions
  - copilot_runs
  - ticket_kb_suggestions
- Create org isolation policies

### GAP-4: Attachment Safety
- Install ClamAV (system packages)
- Create `/data/ATUM DESK/atum-desk/data/quarantine` directory
- Create `attachment_scanner.py` service
- Add scan columns to attachments table
- Update upload pipeline
- Add download headers

### GAP-5: Rate Limiting
- Add NGINX rate limit zones:
  - login: 1r/s burst 5
  - api: 10r/s burst 20

### GAP-6: Audit Hash Chain
- Add columns: prev_hash, row_hash, chain_scope
- Create hash computation function
- Create trigger for auto-hashing
- Create verification script

---

## 5. ALTERNATIVES CONSIDERED

### GAP-1: RLS Bootstrap
- **Option A:** Use app-level filtering (rejected - not secure)
- **Option B:** Use PostgreSQL session context (chosen)

### GAP-4: Attachment Scanning
- **Option A:** External VirusTotal API (rejected - external dependency)
- **Option B:** ClamAV local (chosen)

### GAP-5: Rate Limiting
- **Option A:** Redis-based (rejected - no Redis for rate limiting)
- **Option B:** NGINX-based (chosen)

---

## 6. VERIFICATION PLAN

### GAP-1
```bash
# RLS health check
curl http://localhost:8000/internal/rls/health

# Bootstrap test - login works
curl -X POST http://localhost:8000/api/v1/auth/login -d '{"email":"admin@atum.desk","password":"..."}'
```

### GAP-2
```bash
# Check worker logs
journalctl -u atum-desk-job-worker -f | grep org_id

# Verify org_id constraint
psql -c "SELECT organization_id FROM job_queue WHERE organization_id IS NULL" 
```

### GAP-3
```bash
# Check RLS on AI tables
psql -c "SELECT tablename, rowsecurity FROM pg_tables WHERE tablename IN ('ticket_ai_triage', 'ai_suggestions', 'copilot_runs');"
```

### GAP-4
```bash
# Test EICAR block
echo 'X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*' > /tmp/eicar.txt
curl -X POST -F "file=@/tmp/eicar.txt" http://localhost:8000/api/v1/attachments/upload
# Expected: 403 or scan failure
```

### GAP-5
```bash
# Test rate limiting
for i in {1..10}; do curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/api/v1/tickets; done
# Expected: Some 429 responses
```

### GAP-6
```bash
# Verify chain
python scripts/verify_audit_chain.py
# Expected: VERIFIED
```

---

## 7. ROLLBACK PLAN

### GAP-1
```sql
-- Disable RLS on problematic tables
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE organizations DISABLE ROW LEVEL SECURITY;
```

### GAP-2
```bash
# Revert worker to previous version
git checkout HEAD~1 -- scripts/run_sla_worker.py
```

### GAP-3
```sql
-- Disable RLS on AI tables
ALTER TABLE ticket_ai_triage DISABLE ROW LEVEL SECURITY;
ALTER TABLE ai_suggestions DISABLE ROW LEVEL SECURITY;
```

### GAP-4
```sql
-- Remove scan columns
ALTER TABLE attachments DROP COLUMN IF EXISTS scan_status;
```
```bash
# Remove NGINX rate limits (reload config)
nginx -s reload
```

### GAP-5
```bash
# Restore nginx config
cp infra/nginx/atum-desk.conf.bak infra/nginx/atum-desk.conf
nginx -s reload
```

### GAP-6
```sql
-- Drop trigger and columns
DROP TRIGGER IF EXISTS audit_hash_trigger ON audit_log;
ALTER TABLE audit_log DROP COLUMN IF EXISTS prev_hash;
ALTER TABLE audit_log DROP COLUMN IF EXISTS row_hash;
ALTER TABLE audit_log DROP COLUMN IF EXISTS chain_scope;
```

---

## 8. IMPLEMENTATION ORDER

1. GAP-1: RLS Bootstrap (highest risk, do first)
2. GAP-2: Worker Org Context
3. GAP-3: AI Tables RLS
4. GAP-4: Attachment Safety
5. GAP-5: Rate Limiting
6. GAP-6: Audit Hash Chain

---

**END OF CHANGE DESIGN**
