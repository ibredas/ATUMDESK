# 05_API_ROUTE_MAP_AND_RBAC_MATRIX.md

## Phase 2 API Route Map & RBAC Matrix

**Source Analysis**: `grep` + Code Review of `routers/*.py`.

### 1. Knowledge Base (`kb.py`)
| Method | Endpoint | RBAC Role | Tenant Scoped? | Logic |
|---|---|---|---|---|
| `GET` | `/api/v1/kb/categories` | **Any** | ✅ Yes | Customer sees public only; Agent sees all. |
| `POST` | `/api/v1/kb/categories` | **Agent** | ✅ Yes | Explicit `403` for Customer. |
| `GET` | `/api/v1/kb/articles` | **Any** | ✅ Yes | Customer forced `is_internal=False`. Agent can filter. |
| `GET` | `/api/v1/kb/articles/{id}` | **Any** | ✅ Yes | Customer gets `404` if internal. |
| `POST` | `/api/v1/kb/articles` | **Agent** | ✅ Yes | Explicit `403` for Customer. |
| `PUT` | `/api/v1/kb/articles/{id}` | **Agent** | ✅ Yes | Explicit `403` for Customer. |
| `POST` | `/api/v1/kb/articles/{id}/publish` | **Agent** | ✅ Yes | Explicit `403` for Customer. |

### 2. Problem Management (`problems.py`)
| Method | Endpoint | RBAC Role | Tenant Scoped? | Logic |
|---|---|---|---|---|
| `GET` | `/api/v1/problems` | **Agent** | ✅ Yes | Explicit `403` for Customer. |
| `POST` | `/api/v1/problems` | **Agent** | ✅ Yes | Explicit `403` for Customer. |
| `GET` | `/api/v1/problems/{id}` | **Agent** | ✅ Yes | Explicit `403` for Customer. |
| `PUT` | `/api/v1/problems/{id}` | **Agent** | ✅ Yes | Explicit `403` for Customer. |
| `POST` | `/api/v1/problems/{id}/link-ticket`| **Agent** | ✅ Yes | Explicit `403` for Customer. |

### 3. Change Management (`changes.py`)
| Method | Endpoint | RBAC Role | Tenant Scoped? | Logic |
|---|---|---|---|---|
| `GET` | `/api/v1/changes` | **Agent** | ✅ Yes | Explicit `403` for Customer. |
| `POST` | `/api/v1/changes` | **Agent** | ✅ Yes | Explicit `403` for Customer. |
| `GET` | `/api/v1/changes/{id}` | **Agent** | ✅ Yes | Explicit `403` for Customer. |
| `PUT` | `/api/v1/changes/{id}` | **Agent** | ✅ Yes | Explicit `403` for Customer. |
| `POST` | `/api/v1/changes/{id}/approve` | **Agent** | ✅ Yes | Explicit `403` for Customer. |

### 4. Asset Management (`assets.py`)
| Method | Endpoint | RBAC Role | Tenant Scoped? | Logic |
|---|---|---|---|---|
| `GET` | `/api/v1/assets` | **Agent** | ✅ Yes | Explicit `403` for Customer. |
| `POST` | `/api/v1/assets` | **Agent** | ✅ Yes | Explicit `403` for Customer. |
| `GET` | `/api/v1/assets/{id}` | **Agent** | ✅ Yes | Explicit `403` for Customer. |
| `PUT` | `/api/v1/assets/{id}` | **Agent** | ✅ Yes | Explicit `403` for Customer. |
| `POST` | `/api/v1/assets/{id}/link-ticket`| **Agent** | ✅ Yes | Explicit `403` for Customer. |

## Conclusion
Strict RBAC is enforced at the router level. Customers are completely blocked from ITSM-Lite write operations and internal read operations.
