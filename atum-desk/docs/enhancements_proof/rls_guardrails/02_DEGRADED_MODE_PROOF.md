# Degraded Mode Proof

## Overview
When RLS degraded mode is enabled, requests without organization context are blocked with a 403 error and `ORG_CONTEXT_MISSING` error code.

## Enabling Degraded Mode

### Option 1: Global Override
```bash
# Via Admin API (requires break-glass keys)
curl -X POST "http://localhost:8000/api/v1/admin/rls/degrade" \
  -H "Authorization: Bearer <admin_jwt>" \
  -H "Content-Type: application/json" \
  -d '{"primary_key": "atum-primary-change-me", "secondary_key": "atum-secondary-change-me"}'
```

### Option 2: Per-Org Setting
```sql
-- Direct database
UPDATE organizations 
SET settings = settings || '{"rls_degraded_mode": true}'::jsonb
WHERE id = 'organization-uuid';
```

### Option 3: Environment Variable
```bash
# In .env
RLS_DEGRADED_MODE=true
```

## Blocking Behavior

When degraded mode is active AND a request lacks org context:

```json
{
  "error": "ORG_CONTEXT_MISSING",
  "message": "Organization context required - RLS degraded mode active",
  "detail": "Request blocked mode is enabled because RLS degraded and no organization context was provided"
}
```

## Test Scenarios

### 1. Missing Org Context Blocked
```bash
# Without auth token - blocked
curl -X GET "http://localhost:8000/api/v1/tickets" \
  -H "Content-Type: application/json"

# Response: 403 Forbidden
# {"error":"ORG_CONTEXT_MISSING",...}
```

### 2. Valid Org Context Allowed
```bash
# With valid auth token - allowed
curl -X GET "http://localhost:8000/api/v1/tickets" \
  -H "Authorization: Bearer <valid_jwt_with_org>"

# Response: 200 OK (or appropriate status based on RLS)
```

### 3. Exempt Paths Still Work
```bash
# Health checks exempt
curl -X GET "http://localhost:8000/api/v1/health"

# Response: 200 OK (no org required)

# Metrics exempt  
curl -X GET "http://localhost:8000/metrics"

# Response: 200 OK (Prometheus format)
```

## Exempt Paths
The following paths are exempt from degraded mode blocking:
- `/api/v1/health`
- `/metrics`
- `/health`
- `/api/docs`
- `/api/redoc`
- `/api/v1/auth/login`
- `/api/v1/auth/register`
- `/api/v1/admin/rls/*` (admin endpoints)

## Verification
```bash
# Check degraded mode status
psql -c "SELECT value FROM system_settings WHERE key = 'rls_global_override';"

# Check per-org degraded mode
psql -c "SELECT id, settings FROM organizations WHERE settings->>'rls_degraded_mode' = 'true';"
```
