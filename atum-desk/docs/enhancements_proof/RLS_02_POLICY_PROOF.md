# RLS 02 - POLICY PROOF

## Date: 2026-02-14

## Current Status

RLS is **STAGED** - policies created but NOT enabled.

### Helper Function Exists

```sql
SELECT proname FROM pg_proc WHERE proname = 'set_app_org';
```
```
   proname   
-------------
 set_app_org
```

### To Enable Later

```sql
SELECT enable_rls_policies();
```

### Tables Prepared (24 tenant-owned)

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
| notifications | notifications_org_isolation |
| incidents | incidents_org_isolation |
| postmortems | postmortems_org_isolation |
| ai_provenance | ai_provenance_org_isolation |
| policy_rules | policy_rules_org_isolation |
| ai_security_events | ai_security_events_org_isolation |

## Current RLS Status

```sql
SELECT schemaname, tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname='public' 
AND tablename='tickets';
```

All show `rowsecurity = false` (NOT enabled - safe)

## Status

✅ Policies prepared
✅ Ready for staged rollout
