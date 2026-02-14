# Database Truth
## PostgreSQL Schema & Data Reality

---

## 1. Connection Settings

| Property | Value |
|----------|-------|
| **Host** | 127.0.0.1 |
| **Port** | 5432 |
| **Database** | atum_desk |
| **User** | atum |
| **Connection String** | `postgresql+psycopg://atum:atum@localhost:5432/atum_desk` |

---

## 2. Tables (21 Total)

```
Schema: public

| Table Name |
|------------|
| alembic_version |
| attachments |
| audit_log |
| canned_responses |
| comments |
| csat_surveys |
| custom_field_values |
| custom_fields |
| kb_articles |
| kb_categories |
| organizations |
| rule_actions |
| rules |
| services |
| sla_calculations |
| sla_policies |
| ticket_relationships |
| tickets |
| time_entries |
| users |
| webhooks |
```

---

## 3. Core Entity Schemas

### tickets

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| id | uuid | NOT NULL | |
| organization_id | uuid | NOT NULL | |
| requester_id | uuid | NOT NULL | |
| service_id | uuid | NULL | |
| subject | varchar(500) | NOT NULL | |
| description | text | NOT NULL | |
| status | ticketstatus | NOT NULL | |
| assigned_to | uuid | NULL | |
| accepted_by | uuid | NULL | |
| accepted_at | timestamptz | NULL | |
| priority | ticketpriority | NOT NULL | |
| sla_policy_id | uuid | NULL | |
| sla_started_at | timestamptz | NULL | |
| sla_due_at | timestamptz | NULL | |
| sla_paused_at | timestamptz | NULL | |
| sla_paused_duration | integer | NOT NULL | 0 |
| parent_ticket_id | uuid | NULL | |
| is_duplicate_of | uuid | NULL | |
| ai_suggested_category | varchar(255) | NULL | |
| ai_suggested_priority | varchar(20) | NULL | |
| ai_confidence_score | double precision | NULL | |
| created_at | timestamptz | NOT NULL | |
| updated_at | timestamptz | NOT NULL | |
| resolved_at | timestamptz | NULL | |
| closed_at | timestamptz | NULL | |
| embedding_vector | vector(768) | NULL | |
| tags | jsonb | NULL | |
| escalation_level | integer | NOT NULL | 0 |

**Indexes:**
- `pk_tickets` (PRIMARY KEY)
- `ix_tickets_assigned_to`
- `ix_tickets_created_at`
- `ix_tickets_escalation_level`
- `ix_tickets_org_created`
- `ix_tickets_org_status`
- `ix_tickets_organization_id`
- `ix_tickets_priority`
- `ix_tickets_requester_id`
- `ix_tickets_sla_due_at`
- `ix_tickets_status`

### users

| Column | Type |
|--------|------|
| id | uuid |
| organization_id | uuid |
| email | varchar |
| full_name | varchar |
| password_hash | varchar |
| role | userrole |
| is_active | boolean |
| created_at | timestamptz |

### organizations

| Column | Type |
|--------|------|
| id | uuid |
| name | varchar |
| created_at | timestamptz |

### audit_log

| Column | Type |
|--------|------|
| id | uuid |
| organization_id | uuid |
| user_id | uuid (nullable) |
| action | varchar |
| entity_type | varchar |
| entity_id | uuid |
| old_values | jsonb |
| new_values | jsonb |
| ip_address | varchar |
| user_agent | varchar |
| created_at | timestamptz |

### attachments

| Column | Type |
|--------|------|
| id | uuid |
| ticket_id | uuid |
| comment_id | uuid |
| filename | varchar |
| original_filename | varchar |
| file_path | varchar |
| file_size | bigint |
| mime_type | varchar |
| file_hash | varchar |
| uploaded_by | uuid |
| access_count | integer |
| last_accessed_at | timestamptz |
| created_at | timestamptz |

---

## 4. Tenant Isolation Verification

**VERIFIED:** All multi-tenant tables have `organization_id` field:
- `tickets` ✅
- `users` ✅
- `organizations` ✅
- `audit_log` ✅
- `attachments` ✅
- `comments` ✅
- `sla_policies` ✅
- `rules` ✅

**Code enforcement:** Queries filter by `organization_id` (see `app/routers/tickets.py:46-50`)

---

## 5. Data Queries & Results

### Ticket Counts by Status
```sql
SELECT status, count(*) FROM tickets GROUP BY status;
```
```
status | count
-------+-------
NEW    |     3
```

### Latest 20 Audit Log Events
```sql
SELECT * FROM audit_log ORDER BY created_at DESC LIMIT 20;
```
```
id                  | action           | entity_type | created_at
--------------------+------------------+-------------+------------------------
7148559a-...        | rule_execution   | ticket      | 2026-02-12 20:26:28
deae79ea-...        | rule_execution   | ticket      | 2026-02-12 20:26:28
bf2d75df-...        | rule_execution   | ticket      | 2026-02-12 20:26:28
2dc1be9b-...        | rule_execution   | ticket      | 2026-02-12 20:26:28
```
**NOTE:** Only 4 audit events exist, all are rule_execution. Missing: ticket create, status changes, comments, logins.

### Attachments Count
```sql
SELECT count(*) FROM attachments;
```
```
count
-------
0
```

### SLA Policies
```sql
SELECT * FROM sla_policies;
```
```
id                  | name              | resolution_time_urgent | timezone | is_active
--------------------+-------------------+------------------------+----------+----------
4450ffdc-...        | Test Policy 7db93ab4 | 60                     | UTC      | t
```

---

## 6. Migrations Applied

```
alembic_version table:
| version_num |
|-------------|
| 1c1c6716c2ab |  (add_pgvector_embedding)
| b0dfdbb55d57 |  (add_tags_to_tickets)
| ea345e95baa4 |  (add_rules_and_sla_tables)
| f04a7ec6b3e5 |  (add_escalation_level)
```

---

## 7. Critical Issues Found

1. **sla_started_at is NULL for all tickets** - SLA never starts
2. **No attachments exist** - upload flow untested in production
3. **Sparse audit_log** - only rule_execution events recorded
4. **All tickets have status=NEW** - none transitioned to ACCEPTED
