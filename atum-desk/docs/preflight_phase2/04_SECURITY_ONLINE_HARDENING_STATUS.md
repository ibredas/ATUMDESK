# 04_SECURITY_ONLINE_HARDENING_STATUS.md

**Date**: 2026-02-12
**Status**: AUDITED

## 1. Network Perimeter
- **NGINX**: Active on Ports 80/443.
- **SSL**: Assumed self-signed (local environment) or real certs.
- **Headers**:
    - `HSTS` (Strict-Transport-Security)
    - `X-Frame-Options: DENY`
    - `X-Content-Type-Options: nosniff`
    *Verification Status: Hardening scripts ran in Phase 1 start (16edf6e).*

## 2. Access Control
- **Rate Limiting**: Configured in `app/config.py` (`RATE_LIMIT_API=100`).
- **RBAC**: Enforced via `UserRole` Enum in `app/models/user.py`.

## 3. Data Safety
- **Backups**: `scripts/backup-db.sh` (Not verified in list, need to check if exists).
- **Uploads**:
    - Path: `/data/ATUM DESK/atum-desk/data/uploads`
    - Restrictions: Extension whitelist in `app/config.py`.

## 4. Gaps
- **Rate Limit Middleware**: Not explicitly visible in `main.py` middleware stack, likely handled at NGINX level or via decorator dependency (needs confirmation).
- **Backup Script**: Need to confirm existence.
