# Gap Matrix & Fix Plan
## Prioritized Issues with Evidence and Solutions

---

## Gap Matrix

| # | Gap | Impact | Evidence | Root Cause | Fix Strategy |
|---|-----|--------|----------|------------|--------------|
| 1 | **NGINX SSL Broken** | P0 | `nginx: [emerg] cannot load certificate key` | SSL key file permissions wrong | `chmod 644 /etc/nginx/ssl/atum-desk.key` |
| 2 | **SLA Not Starting** | P0 | All tickets have `sla_started_at=NULL` | Accept endpoint doesn't set SLA start | Add `sla_started_at = datetime.utcnow()` in accept endpoint |
| 3 | **No Backups** | P0 | `/data/ATUM DESK/atum-desk/data/backups/` empty | No backup script exists | Create `backup.sh` with pg_dump + cron |
| 4 | **Google Fonts Leak** | P1 | HTML has `fonts.googleapis.com` link | CDN used instead of local | Download fonts locally, update CSS |
| 5 | **IMAP Errors** | P1 | `IMAP Connection Error: AUTHENTICATIONFAILED` | No IMAP credentials in .env | Add credentials OR disable email ingestion |
| 6 | **KB Routes Not Registered** | P2 | `kb.py` exists but not in main.py | Import exists but `include_router` missing | Add `app.include_router(kb.router)` to main.py |
| 7 | **Reports Routes Not Registered** | P2 | `reports.py` exists but not in main.py | Import exists but `include_router` missing | Add `app.include_router(reports.router)` to main.py |
| 8 | **No Download Audit** | P2 | Attachments downloads not logged | Download endpoint missing audit call | Add audit_log entry in download endpoint |
| 9 | **Request Size Not Limited** | P0 | No `client_max_body_size` in nginx | Config missing | Add `client_max_body_size 10M;` |
| 10 | **Sparse Audit Log** | P2 | Only 4 events (rule_execution) | Missing audit calls in key endpoints | Add audit_log calls for ticket create, status change, login |

---

## Files to Edit

| Gap | File | Change |
|-----|------|--------|
| 1 | `/etc/nginx/ssl/atum-desk.key` | chmod 644 |
| 2 | `atum-desk/api/app/routers/internal_tickets.py` | Add SLA start logic in accept endpoint |
| 3 | NEW: `atum-desk/infra/scripts/backup.sh` | Create backup script |
| 4 | `atum-desk/web/index.html` OR `atum-desk/web/vite.config.js` | Remove Google Fonts |
| 5 | `atum-desk/api/.env` | Add IMAP creds OR disable |
| 6 | `atum-desk/api/app/main.py` | Add `app.include_router(kb.router)` |
| 7 | `atum-desk/api/app/main.py` | Add `app.include_router(reports.router)` |
| 9 | `/etc/nginx/sites-available/atum-desk.conf` | Add `client_max_body_size 10M;` |

---

## Tests to Add

| Gap | Test |
|-----|------|
| 2 | Verify `sla_started_at` is set after accept |
| 3 | Run backup script, verify output |
| 6 | Call KB endpoint, verify 200 response |
| 7 | Call reports endpoint, verify 200 response |
| 8 | Download attachment, verify audit_log entry |
| 10 | Create ticket, verify audit_log entry created |

---

## Fix Order (Locked Sequence)

This sequence preserves uptime and minimizes risk:

1. **Fix 1** - SSL Key Permissions → Reload NGINX
2. **Fix 9** - Add Request Size Limit → Reload NGINX
3. **Fix 5** - Configure or Disable IMAP → Restart API
4. **Fix 2** - SLA Start Logic → Deploy Code → Restart API
5. **Fix 3** - Create Backup Script → No restart needed
6. **Fix 4** - Fix Fonts (defer - requires rebuild)
7. **Fix 6,7** - Register Routes → Deploy Code → Restart API
8. **Fix 8,10** - Add Audit Logging → Deploy Code → Restart API

---

## Non-Breaking Changes

The following fixes are safe to apply without breaking existing functionality:
- SSL key permissions (filesystem only)
- Request size limit in nginx config
- Backup script creation
- Disabling IMAP (config only)
- Adding audit logging (additive)
- Registering KB/Reports routes (additive)

---

## High-Risk Changes

- SLA start logic change requires careful DB migration consideration
- Font changes require frontend rebuild
