# IMPACT_NOTE.md

**Date**: 2026-02-15  
**Scope**: Fix forensic audit findings from MINMAX agent deployments

---

## What Will Change

| Change | Files/Services Affected |
|---|---|
| Remove duplicate `phase12_incident_management.py` migration | 1 file deleted |
| Fix config.py default DB credentials | `api/app/config.py` |
| Implement 3 stub frontend pages | `DeskIncidents.jsx`, `DeskPostmortems.jsx`, `AdminPolicyCenter.jsx` |
| Remove stale `prometheus-node-exporter.service` from repo | 1 file deleted |
| Stop + remove 27 Leviathan service files from systemd | 27 service files (requires `sudo`) |

## Who Depends On It

| Component | Dependencies |
|---|---|
| `phase12_incident_management.py` | Nothing — never applied, `phase10_incidents.py` already created the tables |
| `config.py` | All runtime — but `.env` overrides the default, so no runtime impact |
| Frontend stubs | Router links from `App.jsx` and `DeskSidebar.jsx` |
| Leviathan services | Nothing in ATUM DESK depends on them |

## What Can Break

| Risk | Likelihood | Mitigation |
|---|---|---|
| Frontend build fails after JSX changes | LOW | Syntax-check before build |
| Config change breaks DB connection | NONE | `.env` override is authoritative |
| Removing phase12 migration breaks alembic chain | NONE | It was never applied; DB head is phase11 |
| Stopping lev-opa affects security | NONE | ATUM DESK has no dependency on OPA |

## What Must NOT Change

- Running ATUM services (api, job-worker, rag-worker, sla-worker)
- Database schema (63 tables at phase11 head)
- Existing working frontend pages
- `.env` file
- Nginx configuration

## Restart Order

1. No ATUM service restarts needed for most changes
2. Frontend rebuild (`npx vite build`) after JSX changes
3. Uvicorn restart only if `config.py` changes affect runtime

## Rollback Triggers

- If `vite build` fails → revert JSX changes
- If API crashes after config change → restore original `config.py` from git
- If alembic history broken → restore `phase12` migration file
