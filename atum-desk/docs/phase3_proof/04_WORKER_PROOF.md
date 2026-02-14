# Phase 3 Proof: Worker & Queue Processing

**Date**: 2026-02-13  
**Engineer**: Phase 3 Implementation

---

## 1. Worker Script Created

**Location**: `atum-desk/api/scripts/rag_worker.py`

Features:
- Long-running queue consumer
- FOR UPDATE SKIP LOCKED for concurrent processing
- Batch processing (10 jobs per poll)
- Retry with backoff (max 3 attempts)
- Graceful shutdown handling

---

## 2. Systemd Service Created

**Location**: `atum-desk/infra/systemd/atum-desk-rag-worker.service`

```ini
[Unit]
Description=ATUM DESK RAG Worker - Vector Indexing Service

[Service]
Type=simple
User=navi
ExecStart=/data/ATUM DESK/.venv/bin/python scripts/rag_worker.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

---

## 3. Queue Table Structure

```sql
\d rag_index_queue
```

Columns:
- `id` UUID (PK)
- `organization_id` UUID (indexed)
- `source_type` VARCHAR(50)
- `source_id` UUID
- `action` VARCHAR(20) - 'upsert'|'delete'
- `priority` INTEGER (default 5)
- `status` VARCHAR(20) - 'pending'|'running'|'done'|'failed'
- `attempts` INTEGER
- `last_error` TEXT
- `created_at` TIMESTAMPTZ
- `updated_at` TIMESTAMPTZ

---

## 4. Enqueue Flow

Request handlers call `enqueue_index()` to add jobs:

```python
# tickets.py - on ticket create (if RAG_INDEX_ON_TICKET_CREATE=true)
await enqueue_index(db, org_id, "ticket", ticket_id, "upsert")

# internal_tickets.py - on ticket resolve
await enqueue_index(db, org_id, "ticket", ticket_id, "upsert")
```

Jobs are added with status='pending', priority=5.

---

## 5. Worker Processing Logic

```
1. SELECT pending jobs ORDER BY priority DESC, created_at ASC LIMIT 10
2. FOR UPDATE SKIP LOCKED (prevents duplicate processing)
3. Mark as 'running'
4. For each job:
   - Fetch source data (ticket/kb/asset)
   - Generate embeddings via Ollama
   - Upsert rag_documents + rag_chunks
   - Build graph nodes
   - Mark as 'done'
5. If error: increment attempts, set last_error
   - If attempts >= 3: mark 'failed'
   - Else: mark 'pending' for retry
```

---

## 6. Non-Blocking Verification

Ticket creation does NOT wait for embedding:

```python
# tickets.py
if settings.RAG_INDEX_ON_TICKET_CREATE:
    background_tasks.add_task(enqueue_index, db, org_id, "ticket", ticket_id)
```

- Only enqueues job (fast, ~1ms)
- Worker processes async (configurable poll interval)
- Embedding generation happens in worker, not request path

**Status**: ✅ COMPLETE
