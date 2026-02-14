# Smart Reply Proof - ATUM DESK Enhancement

## Date: 2026-02-14

### Database Table

```sql
atum_desk=# \dt ai_suggestions
```

```
            List of relations
 Schema |       Name       | Type  |  Owner   
--------+------------------+-------+----------
 public | ai_suggestions   | table | postgres
```

### Schema

| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| organization_id | uuid | Tenant ID |
| ticket_id | uuid | Ticket reference |
| suggestion_type | text | smart_reply, etc |
| content | text | Generated content |
| citations | jsonb | Source references |
| confidence | float | AI confidence |
| model_id | text | Ollama model |
| is_used | boolean | If suggestion applied |
| created_at | timestamptz | Creation time |
| expires_at | timestamptz | Expiration (30 min) |

### Current Data

```sql
atum_desk=# SELECT * FROM ai_suggestions ORDER BY created_at DESC LIMIT 3;
```

```
 id | organization_id | ticket_id | suggestion_type | content | citations | confidence | model_id | is_used | created_at | expires_at 
----+-----------------+-----------+----------------+---------+-----------+------------+----------+---------+------------+------------
(0 rows)
```

**Status**: Table ready, awaiting job processing

### Endpoint

```
GET /api/v1/internal/tickets/{id}/smart-reply
```

Behavior:
1. Check cache (30 min TTL)
2. If fresh, return cached suggestion
3. Else, enqueue `SMART_REPLY` job
4. Return "pending" status

### Job Handler

The job worker implements `handle_smart_reply()`:

1. Claims job via `SELECT FOR UPDATE SKIP LOCKED`
2. Fetches ticket + thread context
3. Calls Ollama for reply generation
4. Stores in `ai_suggestions` with citations
5. Marks job DONE or FAILED

### Citations System

All factual claims include:
- KB article IDs + titles + excerpts
- Similar ticket IDs + subjects + excerpts
- Relevance scores

### Audit

- `smart_reply_generated`
- `smart_reply_applied`

### Security

- Tenant isolation by default
- No auto-execution (suggest-only)
- Full citation required for claims
