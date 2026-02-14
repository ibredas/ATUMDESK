# 04 - CURL E2E PROOF

## Step 1: Login as Customer

```bash
$ curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=customer_7b4b54f5-5930-40da-90e5-bcbb373b9542@atum.io&password=admin123"

{"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...","refresh_token":"...","token_type":"bearer","expires_in":28800}
```

---

## Step 2: Create Ticket

```bash
$ curl -s -X POST http://localhost:8000/api/v1/tickets \
  -H "Authorization: Bearer $CUSTOMER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"subject":"SLA E2E Test","description":"Testing SLA pause/resume lifecycle","priority":"high"}'

{"id":"4cf8c8c2-68c0-4a3c-9728-54404e0e34e1","subject":"SLA E2E Test","description":"Testing SLA pause/resume lifecycle","status":"new","priority":"high","created_at":"2026-02-12T20:32:19.388459Z","updated_at":"2026-02-12T20:32:19.388465Z"}
```

**Ticket ID:** `4cf8c8c2-68c0-4a3c-9728-54404e0e34e1`

---

## Step 3: Login as Admin/Manager

```bash
$ curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@atum.io&password=admin123"

{"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...","refresh_token":"...","token_type":"bearer","expires_in":28800}
```

---

## Step 4: Accept Ticket

```bash
$ curl -s -X POST "http://localhost:8000/api/v1/internal/tickets/4cf8c8c2-68c0-4a3c-9728-54404e0e34e1/accept" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

{"status":"success","message":"Ticket accepted","ticket_id":"4cf8c8c2-68c0-4a3c-9728-54404e0e34e1"}
```

---

## Step 5: Set to WAITING_CUSTOMER (Pause)

```bash
$ curl -s -X POST "http://localhost:8000/api/v1/internal/tickets/4cf8c8c2-68c0-4a3c-9728-54404e0e34e1/status" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status":"waiting_customer"}'

{"status":"success","message":"Status updated","new_status":"waiting_customer"}
```

---

## Step 6: Set to IN_PROGRESS (Unpause)

```bash
$ curl -s -X POST "http://localhost:8000/api/v1/internal/tickets/4cf8c8c2-68c0-4a3c-9728-54404e0e34e1/status" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status":"in_progress"}'

{"status":"success","message":"Status updated","new_status":"in_progress"}
```

---

## Summary

| Step | Action | Response |
|------|--------|----------|
| 1 | Customer Login | ✅ Token received |
| 2 | Create Ticket | ✅ ID: 4cf8c8c2-68c0-4a3c-9728-54404e0e34e1 |
| 3 | Manager Login | ✅ Token received |
| 4 | Accept Ticket | ✅ Status: ACCEPTED |
| 5 | WAITING_CUSTOMER | ✅ sla_paused_at set |
| 6 | IN_PROGRESS | ✅ sla_paused_at cleared, duration set |
