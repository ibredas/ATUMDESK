# RLS Health Endpoint Proof

## Endpoint
`GET /api/v1/admin/rls/health`

## Authentication
Requires ADMIN role JWT token.

## Curl Command
```bash
curl -X GET "http://localhost:8000/api/v1/admin/rls/health" \
  -H "Authorization: Bearer <admin_jwt_token>"
```

## Sample Output (Healthy)
```json
{
  "status": "healthy",
  "rls_enabled_tables": [
    {
      "table": "tickets",
      "enabled": true,
      "policy_count": 1
    },
    {
      "table": "audit_log",
      "enabled": true,
      "policy_count": 1
    },
    {
      "table": "organizations",
      "enabled": true,
      "policy_count": 1
    },
    {
      "table": "users",
      "enabled": true,
      "policy_count": 1
    },
    {
      "table": "services",
      "enabled": true,
      "policy_count": 1
    },
    {
      "table": "kb_articles",
      "enabled": true,
      "policy_count": 1
    },
    {
      "table": "assets",
      "enabled": true,
      "policy_count": 1
    },
    {
      "table": "problems",
      "enabled": true,
      "policy_count": 1
    },
    {
      "table": "change_requests",
      "enabled": true,
      "policy_count": 1
    }
  ],
  "total_tables_with_rls": 9,
  "context_validation": {
    "middleware_active": true,
    "current_setting_works": true,
    "current_value": "3572b1aa-aae2-4c54-a499-2001a989bf74"
  },
  "degraded_mode": {
    "global_override": false,
    "orgs_in_degraded_mode": [],
    "effective": false
  },
  "worker_status": {
    "job_worker_rls_safe": true,
    "rag_worker_rls_safe": true,
    "sla_worker_rls_safe": true
  },
  "timestamp": "2026-02-14T16:30:00.000Z"
}
```

## Sample Output (Degraded)
```json
{
  "status": "degraded",
  "rls_enabled_tables": [
    {
      "table": "tickets",
      "enabled": true,
      "policy_count": 1
    }
  ],
  "total_tables_with_rls": 1,
  "context_validation": {
    "middleware_active": true,
    "current_setting_works": true,
    "current_value": null
  },
  "degraded_mode": {
    "global_override": true,
    "orgs_in_degraded_mode": [],
    "effective": true
  },
  "worker_status": {
    "job_worker_rls_safe": true,
    "rag_worker_rls_safe": true,
    "sla_worker_rls_safe": true
  },
  "timestamp": "2026-02-14T16:35:00.000Z"
}
```

## Status Values
- `healthy`: RLS enabled on protected tables, no degraded mode
- `degraded`: RLS degraded mode active (global or per-org)
- `critical`: No RLS policies found

## Verification Commands
```bash
# Check RLS status directly
psql -c "SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname='public' AND rowsecurity = true;"

# Check policies
psql -c "SELECT tablename, policyname FROM pg_policies;"

# Test context setting
psql -c "SET app.current_org = 'test-org'; SELECT current_setting('app.current_org', true);"
```
