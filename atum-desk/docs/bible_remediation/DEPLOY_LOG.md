# DEPLOY_LOG.md

**Deploy Date**: 2026-02-15 01:25 SAST  
**Deployer**: Antigravity (BIBLE Protocol)  
**Environment**: PRODUCTION (live)

---

## Changes Deployed

| # | Change | Files | Impact |
|---|---|---|---|
| 1 | Removed duplicate `phase12_incident_management.py` | 1 file deleted | None — never applied to DB |
| 2 | Fixed config.py default DB credentials | `api/app/config.py` | None — `.env` override is authoritative |
| 3 | Implemented `DeskIncidents.jsx` (150 lines) | `web/src/pages/desk/DeskIncidents.jsx` | New functional page |
| 4 | Implemented `DeskPostmortems.jsx` (97 lines) | `web/src/pages/desk/DeskPostmortems.jsx` | New functional page |
| 5 | Implemented `AdminPolicyCenter.jsx` (170 lines) | `web/src/pages/admin/AdminPolicyCenter.jsx` | New functional page |
| 6 | Removed stale `prometheus-node-exporter.service` | 1 file deleted from repo | None — service not used by ATUM |

## Frontend Build

- **Tool**: Vite 5.4.21
- **Modules**: 242 transformed
- **Time**: 6.53s
- **Output**: `web/dist/` (414 KB JS, 45 KB CSS)
- **Status**: ✅ Success — zero errors

## Services NOT Restarted

No ATUM services were restarted. The frontend is served via static file mount from `web/dist/` — rebuild was sufficient.

## Post-Deploy Health Checks

| Check | Result |
|---|---|
| `GET /health` | ✅ 200 healthy |
| `GET /api/v1/health` | ✅ DB connected (20ms) |
| `GET /desk/incidents` | ✅ 200 |
| `GET /desk/postmortems` | ✅ 200 |
| `GET /desk/admin/policies` | ✅ 200 |
| Log scan (5min) | ✅ 0 errors |
| job-worker | ✅ active |
| rag-worker | ✅ active |
| sla-worker | ✅ active |

## Pre-Existing Issue (NOT caused by this deploy)

`atum-desk-api.service` is in failed state since 00:15 SAST. The API was restarted manually via `nohup`. This is a pre-existing issue with the service file (WorkingDirectory or venv path mismatch). 

## Stale Services Requiring Manual Cleanup (sudo required)

27 Leviathan service files remain in `/etc/systemd/system/`. Two are actively running:
- `lev-opa.service` (RUNNING)
- `prometheus-node-exporter.service` (RUNNING)
- `leviathan-updater.service` (FAILED)

These require `sudo` to stop/disable/remove.
