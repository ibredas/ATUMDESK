# Security Hardening Proof - ATUM DESK Enhancement

## Date: 2026-02-14

## Rate Limiting (NGINX)

### Configuration

```nginx
# /etc/nginx/nginx.conf or included file
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/s;
limit_req_zone $binary_remote_addr zone=login_limit:10m rate=5r/s;
limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=3r/s;
```

### Applied to Routes

- `/api/v1/auth/login` - 5 req/sec, burst 10
- `/api/v1/auth/*` - 3 req/sec, burst 5
- `/api/*` - 100 req/sec, burst 50

### Test

```bash
# Login rate limit test
for i in {1..15}; do curl -s -o /dev/null -w "%{http_code}\n" \
  -X POST http://localhost/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"wrong"}'; done

# Expected: 200 200 200 200 200 429 429 429...
```

## IP Restrictions

### Database Table

```sql
atum_desk=# \dt org_ip_allowlist
```

```
            List of relations
 Schema |       Name        | Type  |  Owner   
--------+-------------------+-------+----------
 public | org_ip_allowlist | table | postgres
```

### Schema

| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| organization_id | uuid | Tenant ID |
| cidr | text | CIDR notation |
| description | text | Description |
| enabled | boolean | Active flag |
| created_by | uuid | Creator user |
| created_at | timestamptz | Creation time |

### Implementation

- Middleware: `app/middleware/ip_allowlist.py`
- Checks on every admin/internal request
- Falls through if no allowlist configured
- Per-organization settings

## Login Attempt Tracking

### Database Table

```sql
atum_desk=# \dt auth_login_attempts
```

```
            List of relations
 Schema |         Name          | Type  |  Owner   
--------+----------------------+-------+----------
 public | auth_login_attempts  | table | postgres
```

### Schema

| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| ip_address | text | Client IP |
| username | text | Username attempted |
| fail_count | int | Failed attempts |
| locked_until | timestamptz | Lock expiration |
| last_attempt_at | timestamptz | Last attempt |
| created_at | timestamptz | Creation time |

### Features

- Rate limiting based on IP
- Account lockout after 5 attempts
- 15-minute lockout duration
- PostgreSQL-backed (no Redis)

## Email Verification

### Database Table

```sql
atum_desk=# \dt email_verification_tokens
```

```
            List of relations
 Schema |          Name            | Type  |  Owner   
--------+-------------------------+-------+----------
 public | email_verification_tokens| table | postgres
```

### Schema

| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| user_id | uuid | User reference |
| token_hash | text | Hashed token |
| expires_at | timestamptz | TTL |
| used_at | timestamptz | Used timestamp |
| created_at | timestamptz | Creation time |

## Password Policy

### Implementation

- Minimum 8 characters
- Complexity requirements (configurable)
- Rate limited login attempts
- Full audit trail

## Cookie Security

### Configuration

- `HttpOnly: true` - Prevents XSS theft
- `Secure: true` - HTTPS only
- `SameSite: strict/lax` - CSRF protection
- JWT in headers (not cookies) for API

## Systemd Hardening

### API Service

```ini
MemoryMax=2G
MemoryHigh=1G
CPUQuota=150%
LimitNOFILE=65536
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=read-only
PrivateTmp=true
ProtectKernelTunables=true
ProtectControlGroups=true
```

### Job Worker

```ini
MemoryMax=512M
MemoryHigh=384M
CPUQuota=50%
LimitNOFILE=4096
```

### SLA Worker

```ini
MemoryMax=256M
MemoryHigh=192M
CPUQuota=30%
```

### RAG Worker

```ini
MemoryMax=512M
MemoryHigh=384M
CPUQuota=100%
```
