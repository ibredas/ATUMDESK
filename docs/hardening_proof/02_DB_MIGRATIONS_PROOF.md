# 02_DB_MIGRATIONS_PROOF.md

## Database Migrations Proof

**Date:** 2026-02-13

---

## Migration Applied

```
$ alembic current
phase5_security_hardening (head)

$ alembic heads
phase5_security_hardening (head)
```

---

## Tables Created

| Table | Status |
|-------|--------|
| auth_login_attempts | ✅ Created |
| email_verification_tokens | ✅ Created |
| org_ip_allowlist | ✅ Created |
| ticket_relationships | ✅ Already existed |

---

## auth_login_attempts Schema

| Column | Type |
|--------|------|
| id | UUID |
| ip_address | String(45) |
| username | String(255) |
| fail_count | Integer |
| locked_until | DateTime |
| last_attempt_at | DateTime |
| created_at | DateTime |

**Indexes:** ip_address, username, locked_until

---

## email_verification_tokens Schema

| Column | Type |
|--------|------|
| id | UUID |
| user_id | UUID (FK) |
| token_hash | String(255) |
| expires_at | DateTime |
| used_at | DateTime |
| created_at | DateTime |

---

## org_ip_allowlist Schema

| Column | Type |
|--------|------|
| id | UUID |
| organization_id | UUID (FK) |
| cidr | String(45) |
| description | String(255) |
| enabled | Boolean |
| created_by | UUID (FK) |
| created_at | DateTime |

---

*Proof generated: 2026-02-13*
