# 06_PHASE2_COMPATIBILITY_MATRIX.md

**Date**: 2026-02-12
**Status**: READY

| Module | Risk | Status | Conflict Strategy |
| :--- | :--- | :--- | :--- |
| **Knowledge Base** | 🔴 HIGH | **Zombie State** | **Tables & Models exist.** Do NOT create new migration for table creation. Use `alembic stamp` if revisions desync, or `upgrade` if pending. Must reconcile existing columns with requirements. |
| **Problem Mgmt** | 🟢 LOW | Green Field | Standard Implementation. |
| **Change Mgmt** | 🟢 LOW | Green Field | Standard Implementation. |
| **Asset Mgmt** | 🟢 LOW | Green Field | Standard Implementation. |

## kb_articles Reconciliation
Existing columns:
- `title`, `slug`, `content`, `excerpt`
- `is_internal`, `is_published`
- `view_count`, `helpful_count`
- `search_vector` (PGVector/TSVector)

*Verdict*: The existing schema is remarkably complete. Phase 2 KB work is primarily **API & UI Implementation**, not DB design.

## Migration Strategy
1.  **Detect**: Run `alembic check` to see if `kb_` tables are tracked.
2.  **Adjust**: If Alembic thinks they don't exist, we must fake connection or skip creation in new migration.
3.  **Execute**: Create migration *only* for Problems, Changes, Assets.
