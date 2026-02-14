# ATUM DESK - Executive Summary
## Audit Date: 2026-02-12

---

## Current Status (10 Bullets)

1. **API Service**: RUNNING - uvicorn on port 8000 with 4 workers, managed by systemd
2. **Web UI**: RUNNING - React SPA served from `/atum-desk/web/dist` via FastAPI
3. **Database**: RUNNING - PostgreSQL 16, 21 tables, connection healthy
4. **SLA Worker**: RUNNING - systemd timer checks tickets every minute
5. **NGINX**: BROKEN - SSL key permission error prevents HTTPS serving
6. **Email Ingestion**: BROKEN - IMAP authentication failing (no credentials configured)
7. **Backups**: MISSING - backup directory empty, no backup scripts exist
8. **Brand Assets**: PARTIAL - logos exist but fonts leak to Google CDN
9. **SLA Logic**: BROKEN - SLA never starts (sla_started_at is NULL for all tickets)
10. **Tenant Isolation**: VERIFIED - organization_id field present on all entities

---

## Reality vs Spec Table

| Component | Spec Requirement | Status | Evidence |
|-----------|-----------------|--------|----------|
| **Architecture** | NGINX → FastAPI → Postgres → uploads | PASS | Config verified at `/etc/nginx/sites-available/atum-desk.conf` |
| **TLS/HTTPS** | Enforced via NGINX | **FAIL** | `nginx: [emerg] cannot load certificate key: Permission denied` |
| **HTTP→HTTPS** | Redirect all traffic | PASS | Config: `return 301 https://$host$request_uri` |
| **Rate Limiting** | Auth: 1r/s, API: 10r/s | PASS | NGINX config: `zone=atum_login_limit:10m rate=1r/s` |
| **Security Headers** | HSTS, X-Frame, CSP | PASS | Headers present in nginx config |
| **Database** | PostgreSQL with tenant isolation | PASS | 21 tables with organization_id on all |
| **SLA Start** | Must start at ACCEPTED | **FAIL** | No code sets sla_started_at on accept |
| **Uploads** | Outside web root, auth-gated | PASS | `/data/ATUM DESK/atum-desk/data/uploads/` |
| **Backups** | Automated daily backups | **FAIL** | Directory empty, no scripts |
| **No Third-Party** | No external SaaS APIs | PASS | Only IMAP (optional), no Slack/Webhooks |

---

## Top 10 Gaps Blocking "First Ticket End-to-End"

| # | Gap | Impact | Root Cause |
|---|-----|--------|-------------|
| 1 | **NGINX SSL Broken** | P0 | SSL key file permissions wrong (chmod 644 needed) |
| 2 | **SLA Not Starting** | P0 | No code sets `sla_started_at` when ticket accepted |
| 3 | **No Backups** | P0 | Missing backup script entirely |
| 4 | **Google Fonts Leak** | P1 | HTML uses fonts.googleapis.com CDN |
| 5 | **IMAP Errors** | P1 | No credentials in .env for email ingestion |
| 6 | **Missing KB Routes** | P2 | `kb.py` router created but not registered in main.py |
| 7 | **Missing Reports Routes** | P2 | `reports.py` router created but not registered |
| 8 | **Zero Attachments** | P2 | No files uploaded, upload flow untested in production |
| 9 | **No Manager Inbox UI** | P2 | API exists at `/api/v1/internal/tickets/new` but UI incomplete |
| 10 | **Audit Log Sparse** | P2 | Only 4 events (rule_execution), missing ticket lifecycle events |

---

## Quick Fix Priority

1. **FIX NGINX SSL** → `chmod 644 /etc/nginx/ssl/atum-desk.key` + reload
2. **FIX SLA START** → Add `sla_started_at = datetime.utcnow()` in accept endpoint
3. **CREATE BACKUP SCRIPT** → Add pg_dump cron job
4. **FIX FONTS** → Copy font files locally, remove Google Fonts link
5. **CONFIGURE IMAP** → Add credentials to .env or disable email ingestion

---

*This summary is based on live system inspection. See detailed reports in subsequent documents.*
