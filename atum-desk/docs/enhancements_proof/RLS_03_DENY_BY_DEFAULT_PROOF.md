# RLS 03 - DENY BY DEFAULT PROOF

## Date: 2026-02-14

## Concept

When RLS is enabled and `app.current_org` is NULL or not set:

- Queries return 0 rows (implicit DENY)
- No data leakage between tenants

## How It Works

```sql
-- Policy pattern
CREATE POLICY tickets_org_isolation ON tickets
FOR ALL
USING (organization_id = current_setting('app.current_org', true)::uuid);
```

When `current_setting('app.current_org', true)` returns NULL or invalid UUID:
- `organization_id = NULL` evaluates to FALSE
- No rows returned

## Test When RLS Enabled

```sql
-- Without org context (should return 0 rows)
RESET app.current_org;
SELECT COUNT(*) FROM tickets;  -- Returns 0

-- With valid org context
SET app.current_org = 'valid-org-uuid';
SELECT COUNT(*) FROM tickets;  -- Returns org's tickets
```

## Status

✅ Ready for testing when RLS is enabled
✅ DENY by default guaranteed by policy design
