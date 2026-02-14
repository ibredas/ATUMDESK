# Phase 3 Preflight Report

**Date**: 2026-02-13  
**Engineer**: Phase 3 Implementation

---

## 1. pgvector Version & Capabilities

| Feature | Status |
|---------|--------|
| pgvector version | 0.6.0 |
| PostgreSQL version | 16.11 (Ubuntu 16.11-0ubuntu0.24.04.1) |
| iterative_scan | NOT AVAILABLE (pgvector 0.8.0+ feature) |
| vector_dims | AVAILABLE |
| vector_norm | AVAILABLE |
| HNSW indexing | AVAILABLE |

**Decision**: Use `hnsw.ef_search` tuning (set to 100+) for tenant-filtered queries instead of iterative_scan.

---

## 2. Ollama Embedding Model

| Item | Value |
|------|-------|
| Configured model | `nomic-embed-text:latest` |
| Status | NOT INSTALLED - needs pull |
| Fallback available | ATUM-DESK-AI:latest (can generate embeddings) |
| Default dimension | 768 (nomic-embed-text) |

**Action**: Will use `nomic-embed-text` - needs to be pulled.

---

## 3. Existing Database Schema

### Tables (27 total)
```
alembic_version
assets
attachments
audit_log
canned_responses
change_approvals
change_requests
comments
csat_surveys
custom_field_values
custom_fields
kb_articles
kb_categories
organizations
problem_ticket_links
problems
rule_actions
rules
services
sla_calculations
sla_policies
ticket_asset_links
ticket_relationships
tickets
time_entries
users
webhooks
```

### Existing Relationship Tables (for GraphRAG)
- `ticket_relationships` - Ticket↔Ticket (parent/child/duplicate/related)
- `ticket_asset_links` - Ticket↔Asset
- `problem_ticket_links` - Problem↔Ticket

### Existing embedding column
- `tickets.embedding_vector` - VECTOR(768) - DEPRECATED, will be ignored

---

## 4. Synchronous RAG Indexing Check

| Endpoint | Status | Notes |
|----------|--------|-------|
| Ticket creation | ✅ NON-BLOCKING | Uses `background_tasks.add_task()` |
| RAG indexer call | ✅ ASYNC | Via FastAPI BackgroundTasks |

**Verification**: `app/routers/tickets.py:133-134` shows:
```python
from app.services.rag.indexer import index_ticket
background_tasks.add_task(index_ticket, new_ticket)
```

This is non-blocking. However, the indexer itself currently calls LangChain synchronously - will be replaced with queue-based worker.

---

## 5. Implementation Decisions

1. **HNSW Index**: Use `vector_cosine_ops` with `m=16, ef_construction=64`
2. **Tenant filtering**: Set `hnsw.ef_search=100` for filtered queries
3. **Embedding model**: Pull `nomic-embed-text` or use ATUM-DESK-AI fallback
4. **Worker**: Long-running systemd service with sleep/backoff
5. **Storage**: Pure SQLAlchemy + pgvector (no LangChain)

---

## 6. Action Items Before Phase 3.1

- [x] Preflight complete
- [ ] Pull nomic-embed-text model (or configure fallback)
- [ ] Create alembic migration for RAG tables
- [ ] Implement pure SQLAlchemy store
