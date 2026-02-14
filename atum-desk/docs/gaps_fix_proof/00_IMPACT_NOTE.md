# IMPACT NOTE - GAP FIXES IMPLEMENTATION

**Date:** 2026-02-14  
**Author:** Max Builder AI

---

## 1. CHANGES OVERVIEW

### GAP-1: RLS Bootstrap Fixes
- **Files Modified:** `app/db/session.py`, `app/middleware/rls_context.py`, `app/routers/internal.py`
- **Risk:** Medium - Changes session handling, may affect all DB queries
- **Impact:** All API requests, all workers

### GAP-2: Worker Org Context
- **Files Modified:** `scripts/run_sla_worker.py`
- **Risk:** Medium - Worker processing logic changes
- **Impact:** SLA processing only

### GAP-3: AI Tables RLS
- **Files Modified:** New migration `phase10_ai_tables_rls.py`
- **Risk:** Medium - Enables RLS on 4+ tables
- **Impact:** AI feature queries

### GAP-4: Attachment Safety
- **Files Modified:** New service, attachments.py, nginx config
- **Risk:** High - File handling changes
- **Impact:** File upload/download operations

### GAP-5: Rate Limiting
- **Files Modified:** `infra/nginx/atum-desk.conf`
- **Risk:** Medium - NGINX config changes
- **Impact:** All API traffic

### GAP-6: Audit Hash Chain
- **Files Modified:** New migration, new verification script
- **Risk:** Low - Adds columns + trigger, no query changes
- **Impact:** Audit log writes only

---

## 2. DEPENDENCY LIST

| Component | Depends On |
|-----------|------------|
| RLS Context Setter | PostgreSQL session management |
| Worker Org Context | job_queue.organization_id |
| AI Tables RLS | RLS context setter |
| Attachment Scanner | ClamAV daemon |
| NGINX Rate Limiting | NGINX service restart |
| Audit Hash Chain | PostgreSQL triggers |

---

## 3. FAILURE MODES

### GAP-1: RLS Bootstrap
- **Failure:** Org context not set → queries return 0 rows
- **Mitigation:** Health check endpoint to verify context works
- **Rollback:** Disable RLS on affected tables

### GAP-2: Worker Org Context
- **Failure:** Jobs process wrong org's data
- **Mitigation:** Logging shows org_id per job
- **Rollback:** Revert worker script

### GAP-3: AI Tables RLS
- **Failure:** AI features stop working
- **Mitigation:** Test before enabling
- **Rollback:** `ALTER TABLE xxx DISABLE ROW LEVEL SECURITY`

### GAP-4: Attachment Safety
- **Failure:** Files not scanned, false positives
- **Mitigation:** Configurable scanning, fallback to clean
- **Rollback:** Disable scan in config

### GAP-5: Rate Limiting
- **Failure:** Legitimate requests blocked
- **Mitigation:** Tunable limits, burst allowances
- **Rollback:** Remove NGINX rate limit directives

### GAP-6: Audit Hash Chain
- **Failure:** New audit entries fail
- **Mitigation:** Trigger exception handling
- **Rollback:** Drop trigger, keep columns

---

## 4. CONSTRAINTS

### MUST NOT CHANGE
- Existing API routes (no breaking changes)
- Phase 2+3 GraphRAG behavior
- Login/authentication flow (must remain working)
- Tenant isolation (MUST NOT create cross-org leaks)

### MUST PRESERVE
- File upload size limits
- Allowed extension list
- Job queue processing
- RAG indexing workflow

---

## 5. RESTART REQUIREMENTS

| Change | Restart Required | Order |
|--------|------------------|-------|
| session.py | API restart | 1 |
| rls_context.py | API restart | 1 |
| internal.py | API restart | 1 |
| run_sla_worker.py | Worker restart | 2 |
| New migration | API restart | 1 |
| attachment_scanner.py | API restart | 1 |
| nginx.conf | NGINX reload | 0 (concurrent) |
| verify_audit_chain.py | No restart | N/A |

---

## 6. ROLLBACK TRIGGERS

Immediate rollback if:
- [ ] API returns 500 errors on startup
- [ ] Login endpoint fails
- [ ] RLS health check fails
- [ ] Worker cannot process jobs
- [ ] File upload returns 500
- [ ] NGINX fails config test

---

## 7. BACKUP PLAN

### Database
- Pre-migration backup: `pg_dump atum_desk > pre_gaps_backup.sql`

### Files
- Config files: Copy before overwrite
  - `infra/nginx/atum-desk.conf` → `.bak`

### Code
- Git stash for uncommitted changes before major operations

---

## 8. CONFLICT PREVENTION

| Check | Status |
|-------|--------|
| Port 8000 in use | ✅ (API running) |
| Port 5432 in use | ✅ (PostgreSQL) |
| Port 80 in use | ✅ (nginx) |
| Service names unique | ✅ |
| Config keys unique | ✅ |
| Path conflicts | ✅ None |

---

## 9. DISK/RESOURCE HEADROOM

- **Disk:** /data/ATUM DESK has ~15GB free
- **Memory:** System has 16GB RAM, ~8GB free
- **CPU:** 4 cores available

---

## 10. VERIFICATION CHECKLIST

Before declaring success:
- [ ] API health endpoint responds
- [ ] Login works
- [ ] Worker processes jobs
- [ ] Files upload/download work
- [ ] RLS isolation verified
- [ ] No cross-org data leaks
- [ ] Audit chain verifies

---

**END OF IMPACT NOTE**
