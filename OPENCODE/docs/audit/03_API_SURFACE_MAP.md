# API Surface Map
## All Discovered Routes

---

## 1. Route Inventory

| Method | Path | Auth | Role | Handler File | Handler Name |
|--------|------|------|------|--------------|--------------|
| GET | `/health` | ❌ No | - | `app/main.py:97` | `health_check` |
| POST | `/api/v1/auth/login` | ❌ No | - | `app/routers/auth.py:42` | `login` |
| POST | `/api/v1/auth/refresh` | ❌ No | - | `app/routers/auth.py:79` | `refresh_token` |
| GET | `/api/v1/auth/me` | ✅ JWT | Any | `app/routers/auth.py:95` | `get_current_user_info` |
| GET | `/api/v1/users` | ✅ JWT | ADMIN | `app/routers/users.py` | (list users) |
| POST | `/api/v1/users` | ✅ JWT | ADMIN | `app/routers/users.py` | (create user) |
| GET | `/api/v1/tickets` | ✅ JWT | CUSTOMER | `app/routers/tickets.py:39` | `list_my_tickets` |
| POST | `/api/v1/tickets` | ✅ JWT | CUSTOMER | `app/routers/tickets.py:68` | `create_ticket` |
| GET | `/api/v1/tickets/{ticket_id}` | ✅ JWT | CUSTOMER | `app/routers/tickets.py` | (get ticket) |
| GET | `/api/v1/internal/tickets/new` | ✅ JWT | MANAGER/ADMIN | `app/routers/internal_tickets.py:39` | `list_new_tickets` |
| POST | `/api/v1/internal/tickets/{ticket_id}/accept` | ✅ JWT | MANAGER/ADMIN | `app/routers/internal_tickets.py:75` | `accept_ticket` |
| POST | `/api/v1/internal/tickets/{ticket_id}/assign` | ✅ JWT | MANAGER/ADMIN | `app/routers/internal_tickets.py:112` | `assign_ticket` |
| POST | `/api/v1/internal/tickets/{ticket_id}/status` | ✅ JWT | MANAGER/ADMIN | `app/routers/internal_tickets.py` | (update status) |
| GET | `/api/v1/comments/ticket/{ticket_id}` | ✅ JWT | Any | `app/routers/comments.py` | (list comments) |
| POST | `/api/v1/comments/ticket/{ticket_id}` | ✅ JWT | Any | `app/routers/comments.py` | (add comment) |
| POST | `/api/v1/attachments/ticket/{ticket_id}` | ✅ JWT | Any | `app/routers/attachments.py` | (upload) |
| GET | `/api/v1/attachments/{attachment_id}/download` | ✅ JWT | Any | `app/routers/attachments.py` | (download) |
| GET | `/api/v1/health` | ❌ No | - | `app/routers/health.py` | (detailed health) |
| GET | `/api/v1/reports/tickets/export` | ✅ JWT | MANAGER/ADMIN | `app/routers/reports.py` | (export) |
| POST | `/api/v1/webhooks` | ✅ JWT | ADMIN | `app/routers/webhooks.py` | (create) |
| GET | `/api/v1/webhooks` | ✅ JWT | ADMIN | `app/routers/webhooks.py` | (list) |
| DELETE | `/api/v1/webhooks/{webhook_id}` | ✅ JWT | ADMIN | `app/routers/webhooks.py` | (delete) |
| GET | `/api/v1/analytics/dashboard` | ✅ JWT | MANAGER/ADMIN | `app/routers/analytics.py` | (dashboard) |
| GET | `/api/v1/rag/search` | ✅ JWT | Any | `app/routers/rag.py` | (search) |
| GET | `/api/v1/rag/tickets/{ticket_id}/similar` | ✅ JWT | AGENT/ADMIN | `app/routers/rag.py` | (similar) |
| GET | `/api/v1/internal/tickets/{ticket_id}/suggestions` | ✅ JWT | AGENT/ADMIN/MANAGER | `app/routers/assistant.py:17` | `get_ticket_suggestions` |

---

## 2. NGINX Proxy Configuration

The NGINX config proxies `/api` to `http://127.0.0.1:8000`:

```nginx
location ^~ /api {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

**All routes ARE reachable through nginx** except:
- `/api/v1/kb/*` - router exists but not registered in main.py
- `/api/v1/reports/*` - router exists but not registered in main.py

---

## 3. Verified Curl Examples

### Health Check (No Auth)
```bash
curl -s http://localhost/api/v1/health
# {"status":"healthy","timestamp":...,"version":"1.0.0",...}
```

### Login (No Auth)
```bash
curl -s -X POST http://localhost/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=password"
# Returns: {"access_token":"...", "refresh_token":"...", "token_type":"bearer", "expires_in":...}
```

### List My Tickets (Auth Required)
```bash
curl -s http://localhost/api/v1/tickets \
  -H "Authorization: Bearer $TOKEN"
```

### Create Ticket (Customer)
```bash
curl -s -X POST http://localhost/api/v1/tickets \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"subject":"Test Issue","description":"This is a test ticket","priority":"MEDIUM"}'
```

### Manager Inbox (Manager Role)
```bash
curl -s http://localhost/api/v1/internal/tickets/new \
  -H "Authorization: Bearer $MANAGER_TOKEN"
```

### Accept Ticket (Manager Role)
```bash
curl -s -X POST http://localhost/api/v1/internal/tickets/{ticket_id}/accept \
  -H "Authorization: Bearer $MANAGER_TOKEN"
```

---

## 4. Missing/Unregistered Routes

The following router files exist but are NOT registered in `app/main.py`:

| File | Intended Prefix | Status |
|------|-----------------|--------|
| `app/routers/kb.py` | `/api/v1/kb` | NOT REGISTERED |
| `app/routers/reports.py` | `/api/v1/reports` | NOT REGISTERED |

These imports exist in main.py but router not included:
```python
# from app.routers import reports  # imported but not included
# from app.routers import kb       # imported but not included
```
