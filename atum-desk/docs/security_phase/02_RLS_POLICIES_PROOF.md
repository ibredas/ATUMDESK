# RLS POLICIES PROOF - ATUM DESK Security Phase

## Date: 2026-02-14

## Implementation

### Migration Status

```bash
$ alembic current
phase8_rls_enforcement (head)
```

### Helper Function Created

```sql
atum_desk=# \df set_app_org
```

Function created for setting organization context.

### RLS STAGED - NOT ENABLED BY DEFAULT

**WARNING**: RLS is NOT enabled by default to prevent production breakage.

To enable after testing, run manually:
```sql
SELECT enable_rls_policies();
```

To disable:
```sql
SELECT disable_rls_policies();
```

### Tables Prepared for RLS

| Table | Policy Name |
|-------|-------------|
| tickets | tickets_org_isolation |
| comments | comments_org_isolation |
| attachments | attachments_org_isolation |
| audit_log | audit_log_org_isolation |
| kb_articles | kb_articles_org_isolation |
| problems | problems_org_isolation |
| change_requests | change_requests_org_isolation |
| assets | assets_org_isolation |
| rag_documents | rag_documents_org_isolation |
| rag_chunks | rag_chunks_org_isolation |
| rag_nodes | rag_nodes_org_isolation |
| rag_edges | rag_edges_org_isolation |
| job_queue | job_queue_org_isolation |
| ai_suggestions | ai_suggestions_org_isolation |
| copilot_runs | copilot_runs_org_isolation |
| ticket_ai_triage | ticket_ai_triage_org_isolation |
| ticket_kb_suggestions | ticket_kb_suggestions_org_isolation |
| metrics_snapshots | metrics_snapshots_org_isolation |

### Current RLS Status

```sql
atum_desk=# SELECT schemaname, tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('tickets', 'comments', 'kb_articles');
```

All show `rowsecurity = false` (not enabled)

### Policy

RLS policies use:
```sql
organization_id = current_setting('app.current_org', true)::uuid
```

This requires application to set the org context per-session.

## Verification

```bash
# Check helper function exists
psql -c "SELECT proname FROM pg_proc WHERE proname = 'set_app_org';"

# Verify tables exist
psql -c "\dt" | wc -l
```

## Next Steps

1. Test RLS in staging environment
2. Verify application queries work with org context
3. Enable RLS in production after testing

## Risk Assessment

| Risk | Level | Mitigation |
|------|-------|------------|
| Breaking production queries | HIGH | RLS NOT enabled by default |
| Performance impact | Medium | Test with large datasets |
| Migration failure | Medium | Staged approach |
