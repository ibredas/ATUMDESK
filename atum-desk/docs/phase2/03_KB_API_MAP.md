# 03_KB_API_MAP.md

**Date**: 2026-02-12
**Status**: IMPLEMENTED

## 1. Endpoints

| Method | Path | Auth | Visibility Rule | Meaning |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/kb/categories` | ANY | Customer: Public Only<br>Agent: All | Browse categories |
| `GET` | `/api/v1/kb/articles` | ANY | Customer: Public + Published Only<br>Agent: Filterable | Search/List articles |
| `GET` | `/api/v1/kb/articles/{id}` | ANY | Customer: Public + Published Only<br>Agent: All | Read article |
| `POST` | `/api/v1/kb/articles` | AGENT | N/A | Create article |
| `POST` | `/api/v1/kb/categories` | AGENT | N/A | Create category |
| `POST` | `/api/v1/kb/articles/{id}/publish` | AGENT | N/A | Publish/Unpublish |

## 2. Security Controls
- **Tenant Isolation**: ALL queries filter by `organization_id == current_user.organization_id`.
- **RBAC**:
    - Customers cannot create/edit/publish.
    - Customers cannot see `is_internal=True` items.
    - Customers cannot see `is_published=False` items.
    
## 3. Example Usage
```bash
# Public Search
curl -H "Authorization: Bearer $USER_TOKEN" \
     "http://localhost:8000/api/v1/kb/articles?search=password"

# Agent Internal Search
curl -H "Authorization: Bearer $AGENT_TOKEN" \
     "http://localhost:8000/api/v1/kb/articles?visibility=internal"
```
