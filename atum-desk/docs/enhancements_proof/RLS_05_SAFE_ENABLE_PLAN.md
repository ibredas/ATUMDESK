# RLS 05 - SAFE ENABLE PLAN

## Date: 2026-02-14

## Current Status

RLS is **STAGED** - not yet enabled.

## Rollout Steps

### Phase 1: Staging (NOW - Ready)
- [x] Create policies
- [x] Create helper functions  
- [x] Create context injection
- [ ] Test in staging environment

### Phase 2: Canary Org (After Staging Tests)
```sql
-- Enable RLS on one table first
ALTER TABLE tickets ENABLE ROW LEVEL SECURITY;
-- Test ticket operations
-- If all works, continue
```

### Phase 3: Full Enable (After Canary)
```sql
-- Enable all at once
SELECT enable_rls_policies();

-- Verify
SELECT schemaname, tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname='public' 
AND rowsecurity = true;
```

### Phase 4: Monitor
- Watch error logs
- Check for query failures
- Verify tenant isolation

## Emergency Rollback

```sql
-- If issues, disable
SELECT disable_rls_policies();
-- Or per-table
ALTER TABLE tickets DISABLE ROW LEVEL SECURITY;
```

## Verification Commands

```bash
# Check RLS status
psql -c "SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname='public';"

# Check policies
psql -c "SELECT tablename, policyname FROM pg_policies;"

# Test isolation
SET app.current_org = 'test-org';
SELECT COUNT(*) FROM tickets;
```

## Status

✅ Infrastructure ready
✅ Safe staged rollout prepared
