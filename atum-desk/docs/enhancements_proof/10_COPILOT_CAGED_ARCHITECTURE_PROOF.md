# Caged AI Copilot Architecture Proof - ATUM DESK Enhancement

## Date: 2026-02-14

### Architecture Overview

```
User Query → Memory Layer → Planner (LLM #1) → Tool Router → Tools
                                                        ↓
                                          Evidence Aggregator
                                                        ↓
                                    Output Generator (LLM #2) → Suggestions
```

### Core Components

1. **Memory Layer**
   - Ticket thread context
   - Organization settings/policies
   - Similar tickets (GraphRAG)
   - KB evidence (GraphRAG)

2. **Planner (LLM Call #1)**
   - Bounded JSON plan, max 5 steps
   - Confidence required
   - Strict tool whitelist

3. **Tool Router**
   - Whitelist only allowed tools
   - Reject anything not permitted

4. **Tools (Suggest-Only)**
   - `rag.search_kb()` - KB articles
   - `rag.similar_tickets()` - Similar tickets
   - `tickets.suggest_classification()` - Category
   - `comments.draft_reply()` - Draft response
   - `sla.predict_breach()` - SLA prediction

5. **Evidence Aggregator**
   - Collect citations/snippets
   - Rank relevance
   - Enforce: "no evidence = no claims"

6. **Output Generator (LLM Call #2)**
   - Structured suggestions
   - Evidence cards
   - Confidence flags
   - Apply buttons (manual only)

### Database Table

```sql
atum_desk=# \dt copilot_runs
```

```
            List of relations
 Schema |     Name     | Type  |  Owner   
--------+--------------+-------+----------
 public | copilot_runs | table | postgres
```

### Schema

| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| organization_id | uuid | Tenant ID |
| ticket_id | uuid | Ticket reference |
| user_id | uuid | User reference |
| plan_json | jsonb | Planner output |
| tool_trace | Tool execution log |
| output_json | jsonb | Final output |
| model_id | text | Ollama model_json | jsonb |
| latency_ms | int | Execution time |
| status | text | success/failed |
| error_message | text | Error details |
| created_at | timestamptz | Creation time |

### Current Data

```sql
atum_desk=# SELECT organization_id, ticket_id, created_at FROM copilot_runs ORDER BY created_at DESC LIMIT 5;
```

```
(0 rows)
```

### API Endpoints

```
GET /api/v1/tickets/{id}/copilot
GET /api/v1/tickets/{id}/copilot/runs
GET /api/v1/tickets/{id}/copilot/runs/{run_id}/trace
```

### Caged Rules (Enforced)

1. **NEVER auto-execute destructive actions**
   - Everything is "suggest + human apply"

2. **Bounded loops only**
   - Max 4-6 steps
   - Strict timeouts

3. **Two LLM calls max**
   - Planner + Output
   - Unless MVP uses one call

4. **ALL factual claims must include citations**
   - From: GraphRAG KB OR ticket thread OR system artifacts
   - If missing evidence → switch to "insufficient evidence + questions/checklist mode"

5. **Full trace logging**
   - Plan JSON
   - Tool calls + results
   - Output JSON
   - Timings

### Citations Gating

If no evidence found:
```json
{
  "insufficient_evidence": true,
  "questions": [
    "What is the customer's exact issue?",
    "What troubleshooting steps have been尝试ed?"
  ],
  "checklist": [
    "Check KB articles manually",
    "Search similar tickets"
  ],
  "confidence": 0.1,
  "citations": []
}
```

### Replay Endpoint

Admins can replay any copilot run:
- Full plan JSON
- All tool traces
- Final output
- Latency breakdown

### Security

- Tenant isolation: All queries filter by `organization_id`
- Role-based access (Agent+ only)
- Manager+ for trace replay
- Full audit trail
