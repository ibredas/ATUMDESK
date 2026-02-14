# ROLLBACK PLAN

**Date:** 2026-02-14  
**Purpose:** Instructions for rolling back gap fixes if needed

---

## ROLLBACK TRIGGERS

Rollback immediately if:
- [ ] API returns 500 errors on startup
- [ ] Login endpoint fails
- [ ] RLS health check returns errors
- [ ] Worker cannot process jobs
- [ ] File upload returns 500
- [ ] NGINX fails config test

---

## GAP-1: RLS Bootstrap Rollback

### If context setter causes issues:

```bash
# No code rollback needed - context setter is additive
# If issues, check logs for "rls_context_missing" warnings
```

### If bootstrap policies cause issues:

```sql
-- Remove bootstrap policies
DROP POLICY IF EXISTS users_auth_lookup ON users;
DROP POLICY IF EXISTS organizations_admin_list ON organizations;
```

---

## GAP-2: Worker Org Context Rollback

### If SLA worker causes issues:

```bash
# Restore previous version
cd /data/ATUM DESK/atum-desk
git checkout HEAD~1 -- api/scripts/run_sla_worker.py

# Restart worker
systemctl restart atum-desk-sla-worker
```

---

## GAP-3: AI Tables RLS Rollback

### If AI table RLS causes issues:

```sql
-- Disable RLS on AI tables
ALTER TABLE ticket_ai_triage DISABLE ROW LEVEL SECURITY;
ALTER TABLE ai_suggestions DISABLE ROW LEVEL SECURITY;
ALTER TABLE copilot_runs DISABLE ROW LEVEL SECURITY;
ALTER TABLE ticket_kb_suggestions DISABLE ROW LEVEL SECURITY;

-- Remove policies
DROP POLICY IF EXISTS ticket_ai_triage_org_isolation ON ticket_ai_triage;
DROP POLICY IF EXISTS ai_suggestions_org_isolation ON ai_suggestions;
DROP POLICY IF EXISTS copilot_runs_org_isolation ON copilot_runs;
DROP POLICY IF EXISTS ticket_kb_suggestions_org_isolation ON ticket_kb_suggestions;
```

---

## GAP-4: Attachment Safety Rollback

### If attachment scanning causes issues:

```sql
-- Remove scan columns
ALTER TABLE attachments DROP COLUMN IF EXISTS scan_status;
ALTER TABLE attachments DROP COLUMN IF EXISTS scanned_at;
ALTER TABLE attachments DROP COLUMN IF EXISTS scanner_version;
ALTER TABLE attachments DROP COLUMN IF EXISTS scan_result_text;
```

### If scanner service causes issues:

```python
# Disable scanner in config
# Set ATTACHMENT_SCANNER_ENABLED = False
```

### If quarantine causes issues:

```bash
# Remove nginx protection
# Edit infra/nginx/atum-desk.conf, remove quarantine location block

# Reload nginx
nginx -s reload
```

---

## GAP-5: Rate Limiting Rollback

### If rate limiting is too aggressive:

```bash
# Restore nginx config
cd /data/ATUM DESK/atum-desk
git checkout HEAD~1 -- infra/nginx/atum-desk.conf

# Test and reload
nginx -t
nginx -s reload
```

### Default values to restore:
```
API: 100r/s burst 50
Login: 5r/s burst 10  
Auth: 3r/s burst 5
```

---

## GAP-6: Audit Hash Chain Rollback

### If audit hash chain causes issues:

```sql
-- Drop trigger
DROP TRIGGER IF EXISTS audit_hash_trigger ON audit_log;

-- Remove columns
ALTER TABLE audit_log DROP COLUMN IF EXISTS prev_hash;
ALTER TABLE audit_log DROP COLUMN IF EXISTS row_hash;
ALTER TABLE audit_log DROP COLUMN IF EXISTS chain_scope;

-- Drop function
DROP FUNCTION IF EXISTS compute_audit_hash;
DROP FUNCTION IF EXISTS audit_hash_trigger_func;
```

---

## EMERGENCY FULL ROLLBACK

If everything fails:

```bash
# Restore entire codebase
cd /data/ATUM DESK/atum-desk
git checkout HEAD~1 -- api/ infra/

# Restart services
systemctl restart atum-desk-api
systemctl restart atum-desk-sla-worker
systemctl restart atum-desk-job-worker

# Reload nginx
nginx -s reload
```

---

## VERIFICATION AFTER ROLLBACK

After any rollback:

```bash
# Check API health
curl http://localhost:8000/api/v1/health

# Check RLS status
psql -c "SELECT COUNT(*) FROM pg_policies;"

# Check worker logs
journalctl -u atum-desk-api -n 50
```

---

**END OF ROLLBACK PLAN**
