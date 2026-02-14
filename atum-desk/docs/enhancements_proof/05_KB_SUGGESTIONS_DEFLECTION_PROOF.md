# KB Suggestions Deflection Proof - ATUM DESK Enhancement

## Date: 2026-02-14

### Database Table

```sql
atum_desk=# \dt ticket_kb_suggestions
```

```
            List of relations
 Schema |         Name          | Type  |  Owner   
--------+----------------------+-------+----------
 public | ticket_kb_suggestions | table | postgres
```

### Schema

| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| organization_id | uuid | Tenant ID |
| ticket_id | uuid | Ticket reference |
| article_id | uuid | KB article reference |
| title | text | Article title |
| excerpt | text | Article excerpt |
| relevance_score | float | Similarity score |
| is_helpful | boolean | User vote |
| created_at | timestamptz | Creation time |

### Current Data

```sql
atum_desk=# SELECT * FROM ticket_kb_suggestions ORDER BY created_at DESC LIMIT 3;
```

```
(0 rows)
```

**Status**: Table ready, awaiting job processing

### Job Handler

The job worker implements `handle_kb_suggest()`:

1. Claims job via `SELECT FOR UPDATE SKIP LOCKED`
2. Fetches ticket subject + description
3. Queries GraphRAG KB (tenant-filtered)
4. Stores top 3 articles in `ticket_kb_suggestions`
5. Marks job DONE or FAILED

### Integration Points

- Ticket creation → Enqueue `KB_SUGGEST` job
- Worker processes async (non-blocking)
- Portal UI shows "Related Articles" after submit
- Voting system: `kb_suggestion_votes`

### Deflection Flow

1. Customer submits ticket
2. System searches KB via GraphRAG
3. Top 3 articles suggested
4. Customer can click to self-resolve
5. Vote helpful/not helpful

### Audit

- `kb_suggested`
- `kb_vote_recorded`

### Security

- Tenant isolation by default
- GraphRAG search respects org boundaries
- No external API calls
