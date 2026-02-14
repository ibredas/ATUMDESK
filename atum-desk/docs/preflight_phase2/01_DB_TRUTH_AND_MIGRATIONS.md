# 01_DB_TRUTH_AND_MIGRATIONS.md

**Date**: 2026-02-12
**Status**: AUDITED

## 1. Database Connection
- **Host**: `localhost` (from config)
- **Database**: `atum_desk`
- **User**: `atum`
- **Driver**: `asyncpg` (app), `psycopg` (alembic)

## 2. Migration Status
- **Tool**: Alembic
- **Current Head**: `f04a7ec6b3e5` (Add Escalation Level)
- **History**:
    - `ea345e95baa4`: Add Rules/SLA tables
    - `b0dfdbb55d57`: Add Tags
    - `f04a7ec6b3e5`: Add Escalation

## 3. Existing Tables (Conflict Analysis)
| Table | Phase 2 Component | Status | Action Required |
| :--- | :--- | :--- | :--- |
| `kb_articles` | **Knowledge Base** | **EXISTS** (Zombie) | **CONFLICT**: Check schema parity vs Phase 2 requirements. |
| `kb_categories` | **Knowledge Base** | **EXISTS** (Zombie) | **CONFLICT**: Check schema parity. |
| `problems` | Problem Mgmt | *Missing* | Safe to Create. |
| `changes` | Change Mgmt | *Missing* | Safe to Create. |
| `assets` | Asset Mgmt | *Missing* | Safe to Create. |

## 4. Protected Tables (DO NOT TOUCH)
- `users`, `organizations` (Core Identity)
- `tickets`, `comments` (Core Workflow)
- `rules`, `rule_actions` (Phase 1 Logic)
- `sla_calculations`, `sla_policies` (Phase 1 Logic)
- `alembic_version` (System)

## 5. Schema Guardrails
- **Tenant Isolation**: `organization_id` column present on ALL major tables (`kb_articles`, `kb_categories` included).
- **Foreign Keys**: Start enforced on `created_by` (Users) and `organization_id`.
