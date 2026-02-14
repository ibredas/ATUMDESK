# AI Triage Proof - ATUM DESK Enhancement

## Date: 2026-02-14

### Database Table

```sql
atum_desk=# \dt ticket_ai_triage
```

```
            List of relations
 Schema |        Name        | Type  |  Owner   
--------+--------------------+-------+----------
 public | ticket_ai_triage   | table | postgres
```

### Schema

| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| organization_id | uuid | Tenant ID |
| ticket_id | uuid | Ticket reference |
| suggested_category | text | AIuggested category |
-s| suggested_priority | text | AI-suggested priority |
| suggested_tags | jsonb | AI-suggested tags |
| suggested_assignee_id | uuid | AI-suggested assignee |
| sentiment_label | text | positive/neutral/negative |
| sentiment_score | float | 0-1 confidence |
| intent_label | text | request/question/problem |
| intent_score | float | 0-1 confidence |
| confidence | float | Overall confidence |
| model_id | text | Ollama model used |
| created_at | timestamptz | Creation time |

### Current Data

```sql
atum_desk=# SELECT * FROM ticket_ai_triage ORDER BY created_at DESC LIMIT 3;
```

```
 id | organization_id | ticket_id | suggested_category | suggested_priority | suggested_tags | suggested_assignee_id | sentiment_label | sentiment_score | intent_label | intent_score | confidence | model_id | created_at 
----+-----------------+-----------+--------------------+--------------------+----------------+-----------------------+-----------------+-----------------+--------------+--------------+------------+----------+------------
(0 rows)
```

**Status**: Table ready, awaiting job processing

### Job Handler

The job worker implements `handle_triage_ticket()`:

1. Claims job via `SELECT FOR UPDATE SKIP LOCKED`
2. Fetches ticket details
3. Calls Ollama for triage analysis
4. Stores results in `ticket_ai_triage`
5. Marks job DONE or FAILED
6. Logs event to `job_events`

### Integration Points

- Ticket creation → Enqueue `TRIAGE_TICKET` job
- Worker processes async (non-blocking)
- UI panel shows suggestions + "Apply" button
- Audit: `ticket_triaged`, `ticket_triage_applied`

### Security

- Tenant isolation: All queries filter by `organization_id`
- No external API calls (local Ollama only)
- Full audit trail
