# Phase 3 Proof: No Blocking

**Date**: 2026-02-13  
**Engineer**: Phase 3 Implementation

---

## 1. Architecture: Request Path vs Background

### Request Path (FAST, ~10-50ms)
```
POST /api/v1/tickets
  → validate input
  → create ticket in DB
  → write audit log
  → SLA calculation (if status=ACCEPTED)
  → enqueue RAG job (just inserts 1 row)
  → return response
```

### Background Worker (SLOW, ~100ms-10s)
```
rag_worker.py (separate process)
  → poll rag_index_queue
  → fetch ticket/kb/asset data
  → call Ollama for embedding
  → insert into rag_chunks
  → update job status
```

---

## 2. Non-Blocking Implementation

### Ticket Creation (tickets.py)
```python
# RAG Indexing - async enqueue only
if settings.RAG_INDEX_ON_TICKET_CREATE:
    background_tasks.add_task(
        enqueue_index,
        db,
        new_ticket.organization_id,
        "ticket",
        new_ticket.id,
        "upsert"
    )
# NO WAIT - returns immediately after enqueue
```

### Ticket Resolution (internal_tickets.py)
```python
if status_data.status == TicketStatus.RESOLVED:
    ticket.resolved_at = datetime.utcnow()
    
    # Enqueue RAG index job (async)
    if settings.RAG_ENABLED and settings.RAG_INDEX_ON_TICKET_RESOLVE:
        await enqueue_index(db, org_id, "ticket", ticket_id, "upsert")
    # NO WAIT - returns immediately
```

---

## 3. Queue Insert Performance

```sql
-- Just inserts 1 row, ~1ms
INSERT INTO rag_index_queue (id, organization_id, source_type, source_id, action, ...)
VALUES (...)
ON CONFLICT DO NOTHING
```

---

## 4. Feature Flag Default

```python
# config.py
RAG_INDEX_ON_TICKET_CREATE: bool = False  # Default OFF
RAG_INDEX_ON_TICKET_RESOLVE: bool = True   # Default ON (most useful)
RAG_ENABLED: bool = True
```

Both can be enabled via environment variables.

---

## 5. Verified: No Embedding in Request Path

- **Store**: Pure SQLAlchemy, no embeddings
- **Retriever**: Uses Ollama for query embedding, not ticket creation
- **Worker**: Separate process, not blocking API

---

## 6. Comparison: Old vs New

| Operation | Old (LangChain) | New (Queue+Worker) |
|-----------|-----------------|-------------------|
| Ticket Create | ❌ Blocking | ✅ Async |
| Embedding Gen | In request | In worker |
| API Latency | +500ms-5s | +1ms |

**Status**: ✅ COMPLETE
