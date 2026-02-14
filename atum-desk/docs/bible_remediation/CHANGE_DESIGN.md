# CHANGE_DESIGN.md

**Date**: 2026-02-15  
**Protocol**: BIBLE 10-Step Remediation  

---

## Goal

Fix all issues identified in the forensic audit of ATUM DESK (FORENSIC_AUDIT_24H.md).

## Non-Goals

- No new features
- No schema changes (no new migrations)
- No service architecture changes

## Success Metrics

1. Zero duplicate migration files for the same concept
2. All frontend pages render real content (no "Coming soon" stubs)
3. Zero stale Leviathan service files in systemd
4. Config.py defaults match production reality
5. Frontend build succeeds cleanly
6. All existing endpoints still respond correctly

---

## ARCH_MAP (Step 2: ANALYZE)

### Service Map

```
atum-desk-api (port 8000) → PostgreSQL (5432) + Ollama (11434)
atum-desk-job-worker → PostgreSQL (polling job_queue table)
atum-desk-rag-worker → PostgreSQL (polling rag_index_queue)
atum-desk-sla-worker → PostgreSQL (checking ticket SLA deadlines)
nginx (80/443) → proxy_pass 8000
```

### Dataflow Map

```
User → Nginx (80/443) → Uvicorn (8000) → FastAPI Routers → PostgreSQL
                                          ↓
                                   Ollama (11434) for AI
                                          ↓
                                   Background Workers (job, rag, sla)
```

### Dependency Map (What Relies on What)

- All routers → `get_session()` → PostgreSQL
- All AI services → Ollama (11434)
- Frontend → Vite build → `/web/dist/`
- API serves frontend from `/web/dist/`

### Integration Points

- `main.py` wires all routers (30+)
- `App.jsx` wires all frontend routes
- Alembic migration chain: `1c1c6716c2ab → ... → ae2bcdc8e643 → phase3 → ... → phase11`

### Failure Points

- Duplicate incident tables (`incidents` from phase10, `incident_records` from phase12)
- Empty frontend pages break user trust
- Stale services consume resources and create confusion

---

## Proposed Fixes (Step 3: DESIGN)

### Fix 1: Remove `phase12_incident_management.py`

**Rationale**: `phase10_incidents.py` already created `incidents`, `incident_ticket_links`, and `postmortems` tables. `phase12` creates a conflicting set (`incident_records`, `incident_events`, `incident_postmortems`) that was never applied. Remove the unapplied duplicate.

**Risk**: NONE — migration was never applied.

### Fix 2: Fix config.py default credentials

**Change**: Update default DATABASE_URL from `atum:atum` to `postgres:postgres` to match the `.env` production value.

**Risk**: NONE — `.env` override is authoritative; this just fixes the fallback default.

### Fix 3: Implement 3 stub frontend pages

**DeskIncidents.jsx**: List view with API fetch from `/api/v1/incidents`
**DeskPostmortems.jsx**: List view (read-only, linked to incidents)  
**AdminPolicyCenter.jsx**: Policy rules list with API fetch from `/api/v1/policies`

**Risk**: LOW — isolated page components, no shared state.

### Fix 4: Remove stale `prometheus-node-exporter.service`

**Change**: Delete from repo `infra/systemd/prometheus-node-exporter.service`

**Risk**: NONE — file only in repo, not actively deployed for ATUM.

### Fix 5: Stop + remove Leviathan services from systemd

**Action**: Requires `sudo` — user must execute.
Stop `lev-opa.service`, `prometheus-node-exporter.service`.
Disable and remove all 27 leviathan-*.service files.

---

## Verification Plan

1. `vite build` succeeds after JSX changes
2. `curl /health` still returns 200
3. All 3 new pages render (browser check)
4. Alembic history is clean (no broken chain)
5. No new errors in service logs

## Rollback Plan

- All changes are in git — `git revert HEAD` restores everything
- Backup of deleted migration file kept in this design doc
