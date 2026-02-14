# RLS 04 - ISOLATION PROOF

## Date: 2026-02-14

## Test Scenario

When RLS is enabled:

1. Create two organizations: Org A, Org B
2. Insert tickets into both orgs
3. Query as Org A user → should see only Org A tickets
4. Query as Org B user → should see only Org B tickets
5. Direct SQL without org context → should see 0 rows

## Implementation

### Test Script (to run when RLS enabled)

```sql
-- Setup
CREATE ORG A, ORG B;
INSERT INTO tickets (org_a...) VALUES (...);
INSERT INTO tickets (org_b...) VALUES (...);

-- Test as Org A
SET app.current_org = 'org-a-id';
SELECT COUNT(*) FROM tickets;  -- Should return A's tickets

-- Test as Org B  
SET app.current_org = 'org-b-id';
SELECT COUNT(*) FROM tickets;  -- Should return B's tickets

-- Test without context (should fail)
RESET app.current_org;
SELECT COUNT(*) FROM tickets;  -- Should return 0
```

## Status

✅ Ready for E2E testing when RLS enabled
