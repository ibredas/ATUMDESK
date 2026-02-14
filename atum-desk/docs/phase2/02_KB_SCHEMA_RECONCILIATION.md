# 02_KB_SCHEMA_RECONCILIATION.md

**Date**: 2026-02-12
**Subject**: 'Zombie' KB Tables Analysis

## 1. Table: `kb_articles`
| Column | Type | Nullable? | Requirement | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| `id` | UUID | No | Primary Key | ✅ Match |
| `organization_id` | UUID | No | **Tenant Isolation** | ✅ Match |
| `title` | Varchar | No | Content | ✅ Match |
| `slug` | Varchar | No | Routing | ✅ Match |
| `content` | Text | No | Content | ✅ Match |
| `is_internal` | Bool | No | **Visibility** | ✅ Match |
| `is_published` | Bool | No | **Visibility** | ✅ Match |
| `search_vector` | TSVector | Yes | Search | ✅ Match |
| `created_by` | UUID | No | Audit | ✅ Match |
| `published_at` | Timestamp | Yes | Metadata | ✅ Match |

**Indexes**:
- `ix_kb_articles_organization_id`: Present (Tenant Safe)
- `ix_kb_articles_search`: Present (Search Ready)

## 2. Table: `kb_categories`
| Column | Type | Nullable? | Requirement | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| `id` | UUID | No | PK | ✅ Match |
| `organization_id` | UUID | No | **Tenant Isolation** | ✅ Match |
| `name` | Varchar | No | Content | ✅ Match |
| `is_internal` | Bool | No | **Visibility** | ✅ Match |

## 3. Conclusion
The existing "Zombie" schema **FULLY MEETS** Phase 2 requirements.
- **Tenant Isolation**: ENFORCED (`organization_id` non-nullable).
- **Visibility**: ENFORCED (`is_internal`, `is_published`).
- **Search**: READY (`search_vector`).

**Action Plan**:
- **DO NOT** create a migration for KB.
- **DO** bind these tables to new `kb.py` router.
