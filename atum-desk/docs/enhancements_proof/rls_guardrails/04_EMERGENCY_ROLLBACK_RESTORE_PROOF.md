# Emergency Rollback & Restore Proof

## Overview
Emergency functions for RLS management with full audit trail.

## Database Functions

### rls_emergency_degrade()
Activates degraded mode globally.

```sql
SELECT rls_emergency_degrade('admin@atum.desk');
```

### rls_emergency_rollback()
Disables RLS on protected tables only (9 tables), creates snapshot.

```sql
SELECT rls_emergency_rollback('admin@atum.desk');
```

Protected tables:
- tickets
- audit_log
- organizations
- users
- services
- kb_articles
- assets
- problems
- change_requests

### rls_restore_previous()
Restores RLS state from most recent snapshot.

```sql
SELECT rls_restore_previous('admin@atum.desk');
```

## Admin API Endpoints

All endpoints require:
1. ADMIN role JWT
2. Break-glass authentication (two keys)

### Degrade
```bash
curl -X POST "http://localhost:8000/api/v1/admin/rls/degrade" \
  -H "Authorization: Bearer <admin_jwt>" \
  -H "Content-Type: application/json" \
  -d '{"primary_key": "atum-primary-change-me", "secondary_key": "atum-secondary-change-me"}'
```

### Rollback
```bash
curl -X POST "http://localhost:8000/api/v1/admin/rls/rollback" \
  -H "Authorization: Bearer <admin_jwt>" \
  -H "Content-Type: application/json" \
  -d '{"primary_key": "atum-primary-change-me", "secondary_key": "atum-secondary-change-me"}'
```

### Restore
```bash
curl -X POST "http://localhost:8000/api/v1/admin/rls/restore" \
  -H "Authorization: Bearer <admin_jwt>" \
  -H "Content-Type: application/json" \
  -d '{"primary_key": "atum-primary-change-me", "secondary_key": "atum-secondary-change-me"}'
```

### Get Snapshots
```bash
curl -X GET "http://localhost:8000/api/v1/admin/rls/snapshots" \
  -H "Authorization: Bearer <admin_jwt>"
```

## Audit Trail

### Snapshots Table
```sql
SELECT * FROM rls_state_snapshot ORDER BY created_at DESC LIMIT 10;
```

Sample output:
```
id              | snapshot_name              | action_type | actor              | created_at
----------------|---------------------------|-------------|-------------------|---
abc123          | rollback_2026-02-14...   | rollback    | admin@atum.desk   | 2026-02-14 16:40
def456          | degrade_2026-02-14...    | degrade     | admin@atum.desk   | 2026-02-14 16:35
```

### Protected Tables Snapshot
```sql
SELECT tables_snapshot FROM rls_state_snapshot ORDER BY created_at DESC LIMIT 1;
```

Sample:
```json
{
  "tickets": {"rls_enabled": true},
  "audit_log": {"rls_enabled": true},
  "organizations": {"rls_enabled": true},
  "users": {"rls_enabled": true},
  "services": {"rls_enabled": true},
  "kb_articles": {"rls_enabled": true},
  "assets": {"rls_enabled": true},
  "problems": {"rls_enabled": true},
  "change_requests": {"rls_enabled": true}
}
```

## Security

### Role-Based Access
- Functions restricted to `atum_ops` role
- API requires ADMIN role

### Break-Glass
- Two-key authentication
- Keys via environment variables:
  - `BREAK_GLASS_PRIMARY_KEY`
  - `BREAK_GLASS_SECONDARY_KEY`

### Audit
- All actions logged to `rls_state_snapshot`
- Actor email recorded

## Verification Commands
```bash
# Check RLS enabled tables
psql -c "SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname='public' AND rowsecurity = true;"

# Check snapshots
psql -c "SELECT snapshot_name, action_type, created_by, created_at FROM rls_state_snapshot;"

# Check system settings
psql -c "SELECT key, value FROM system_settings;"
```
