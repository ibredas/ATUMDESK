# 02_API_SURFACE_AND_ROUTE_CONFLICTS.md

**Date**: 2026-02-12
**Status**: AUDITED

## 1. Current API Structure
**Base URL**: `/api/v1`

| Tag | Route Prefix | Auth | Status |
| :--- | :--- | :--- | :--- |
| **Auth** | `/api/v1/auth` | Public/JWT | Active |
| **Users** | `/api/v1/users` | Bearer | Active |
| **Tickets** | `/api/v1/tickets` | Bearer | Active |
| **Internal** | `/api/v1/internal/tickets` | Agent-Only | Active |
| **Comments** | `/api/v1/comments` | Bearer | Active |
| **Webhooks** | `/api/v1/webhooks` | Admin | Active |
| **Reports** | `/api/v1/reports` | Admin/Agent | Active |
| **Analytics** | `/api/v1/analytics` | Admin | Active |
| **RAG** | `/api/v1/rag` | Bearer | Active |
| **Health** | `/api/v1/health` | Public | Active |

## 2. Phase 2 Proposed Routes (Gap Analysis)

| Module | Proposed Route | Conflict? | Notes |
| :--- | :--- | :--- | :--- |
| **KB** | `/api/v1/kb/articles` | **NO** | `kb.py` router missing. Safe to add. |
| **KB** | `/api/v1/kb/categories` | **NO** | Safe to add. |
| **Problem** | `/api/v1/problems` | **NO** | Safe to add. |
| **Change** | `/api/v1/changes` | **NO** | Safe to add. |
| **Assets** | `/api/v1/assets` | **NO** | Safe to add. |

## 3. Findings
- **Zombie KB**: While `kb_` tables exist in DB, NO API endpoints expose them.
- **Strategy**: Phase 2 implementation will involve *wiring up* the existing models to new routers, rather than creating models from scratch.
