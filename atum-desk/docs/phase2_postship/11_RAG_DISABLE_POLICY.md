# 11_RAG_DISABLE_POLICY.md

## RAG Indexing Stabilization Policy
**Date**: 2026-02-13
**Status**: ACTIVE
**Feature Flag**: `RAG_INDEX_ON_TICKET_CREATE` (Default: `False`)

### Context
During Phase 2 verification, the inline RAG indexing process triggered `MissingGreenlet` exceptions within `uvicorn` due to async/sync bridging issues in the `langchain_postgres` initialization. To ensure the stability of the core Ticket Lifecycle (Creation/Update), this feature has been moved behind a strict feature flag.

### Policy Rules
1.  **Default State**: RAG Indexing is **OFF** by default in Phase 2.
2.  **Versioning**: This flag will remain `False` for all Phase 2 patches.
3.  **Activation Condition**: The flag may only be enabled in **Phase 3 (Intelligence)** after `pgvector` dependencies and async loop handling are fully refactored.

### Implementation
- **File**: `api/app/routers/tickets.py`
- **Config**: `api/app/config.py`
- **Logic**:
  ```python
  if settings.RAG_INDEX_ON_TICKET_CREATE:
      # ... run indexing ...
  ```

### Phase 3 Migration Plan
Instead of inline indexing on ticket creation (which slows response and risks stability), Phase 3 will move to:
1.  **Async Worker**: A dedicated Celery/RQ worker or separate service.
2.  **Batch Indexing**: Cron-based indexing for existing content.
3.  **Event Driven**: Listen for `ticket.created` webhook/event rather than direct coupling in the API router.
