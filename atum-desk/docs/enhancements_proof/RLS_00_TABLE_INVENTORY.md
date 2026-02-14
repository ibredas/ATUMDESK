# RLS TABLE INVENTORY - ATUM DESK

## Generated: 2026-02-14

### Summary

This document classifies all database tables by tenant ownership.

---

## A) TENANT-OWNED TABLES (have organization_id)

These tables MUST have RLS policies applied:

| Table | Has org_id | RLS Required |
|-------|------------|---------------|
| tickets | YES | YES |
| comments | YES | YES |
| attachments | YES | YES |
| audit_log | YES | YES |
| kb_articles | YES | YES |
| problems | YES | YES |
| change_requests | YES | YES |
| assets | YES | YES |
| rag_documents | YES | YES |
| rag_chunks | YES | YES |
| rag_nodes | YES | YES |
| rag_edges | YES | YES |
| job_queue | YES | YES |
| ai_suggestions | YES | YES |
| copilot_runs | YES | YES |
| ticket_ai_triage | YES | YES |
| ticket_kb_suggestions | YES | YES |
| metrics_snapshots | YES | YES |
| notifications | YES | YES |
| incidents | YES | YES |
| postmortems | YES | YES |
| ai_provenance | YES | YES |
| policy_rules | YES | YES |
| ai_security_events | YES | YES |

**Total: 24 tables**

---

## B) GLOBAL TABLES (no organization_id)

These tables do NOT require RLS (system-wide):

| Table | Purpose |
|-------|---------|
| users | Global user directory |
| organizations | Tenants list |
| alembic_version | Migration tracking |
| auth_login_attempts | Global security |
| email_verification_tokens | Global auth |
| password_reset_tokens | Global auth |
| org_settings | Per-org but managed globally |
| org_ip_allowlist | Per-org but managed globally |
| sla_policies | Global + org reference |
| custom_fields | Global catalog |
| kb_categories | Global KB structure |
| service_forms | Global templates |
| canned_responses | Global templates |
| rag_index_queue | System queue |
| rag_config | System config |
| change_approvals | Links to changes |
| problem_ticket_links | Links to problems |
| ticket_asset_links | Links to assets |
| ticket_locks | System locks |
| ticket_relationships | Links tickets |
| time_entries | Time tracking |
| csat_surveys | Surveys |
| custom_field_values | Values |
| webhooks | Webhook configs |
| playbook_templates | Global |
| playbook_steps_log | System logs |
| playbook_runs | System runs |
| form_submissions | Form data |
| service_forms | Form defs |

**Total: 28 tables**

---

## C) MIXED/NEEDS-DECISION

| Table | Decision | Reason |
|-------|----------|---------|
| incident_ticket_links | NO RLS | Link table, uses composite key |
| job_events | NO RLS | Event log, references job_queue |

---

## RLS POLICIES REQUIRED (Category A)

### Example Policy SQL:

```sql
-- Tickets policy
CREATE POLICY tickets_org_isolation ON tickets
FOR ALL
USING (organization_id = current_setting('app.current_org', true)::uuid);
```

### Policy Pattern for All Tenant Tables:

```sql
CREATE POLICY {table}_org_isolation ON {table}
FOR ALL
USING (organization_id = current_setting('app.current_org', true)::uuid);
```

---

## DENY DEFAULT BEHAVIOR

When `app.current_org` is NULL or not set:
- Queries return 0 rows (implicit DENY)
- No data leakage between tenants
