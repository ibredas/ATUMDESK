# Workflow Reality
## Actual Operational Workflows as Implemented

---

## 1. Customer Portal Flow

### Step 1: User Registration/Login
```
Endpoint: POST /api/v1/auth/login
Auth: None
Params: username (email), password
Returns: JWT access_token, refresh_token
```

### Step 2: Create Ticket (Customer)
```
Endpoint: POST /api/v1/tickets
Auth: JWT (CUSTOMER role)
Body: { subject, description, priority, service_id? }
Result:
- ticket created with status=NEW
- sla_started_at = NULL (SLA does NOT start yet)
- requester_id = current user
- organization_id = from user session
```

**Code Reference:** `app/routers/tickets.py:68-100`

### Step 3: View My Tickets
```
Endpoint: GET /api/v1/tickets
Auth: JWT (CUSTOMER role)
Filter: organization_id + requester_id
```

---

## 2. Internal Desk Flow (Manager Accept Gate)

### Step 1: Manager Views Inbox
```
Endpoint: GET /api/v1/internal/tickets/new
Auth: JWT (MANAGER or ADMIN role)
Filter: status = NEW
```

### Step 2: Manager Accepts Ticket
```
Endpoint: POST /api/v1/internal/tickets/{ticket_id}/accept
Auth: JWT (MANAGER or ADMIN role)
Result:
- status changes from NEW → ACCEPTED
- accepted_by = current user
- accepted_at = now()
- **SLA STILL NOT STARTED** (sla_started_at remains NULL)
```

**Code Reference:** `app/routers/internal_tickets.py:75-109`

**CRITICAL BUG:** The accept endpoint does NOT set `sla_started_at`. SLA will never start.

### Step 3: Manager Assigns to Agent
```
Endpoint: POST /api/v1/internal/tickets/{ticket_id}/assign
Auth: JWT (MANAGER or ADMIN role)
Body: { assigned_to: user_id }
```

### Step 4: Update Status
```
Endpoint: POST /api/v1/internal/tickets/{ticket_id}/status
Auth: JWT (MANAGER/ADMIN/AGENT role)
Body: { status: ACCEPTED | IN_PROGRESS | WAITING_CUSTOMER | RESOLVED | CLOSED }
```

---

## 3. SLA Start Point Verification

### Expected Behavior (Per Spec)
- SLA starts when ticket status → ACCEPTED
- `sla_started_at` should be set to `datetime.utcnow()`

### Actual Behavior (Verified in DB)
```sql
SELECT id, status, sla_started_at, sla_due_at, accepted_at FROM tickets;
```
```
id                  | status | sla_started_at | sla_due_at | accepted_at
--------------------+--------+----------------+------------+-------------
85f5ad3f-...        | NEW    | NULL           | NULL       | NULL
66571720-...        | NEW    | NULL           | NULL       | NULL
a81d9979-...        | NEW    | NULL           | NULL       | NULL
```

**VERIFICATION FAILED:** No tickets have SLA started. The SLA worker runs but has nothing to calculate.

---

## 4. WAITING_CUSTOMER Pause Handling

### Implementation Status
- `sla_paused_at` and `sla_paused_duration` columns exist in tickets table
- No code found that sets `sla_paused_at` when status → WAITING_CUSTOMER
- SLA worker does not check for pause state

**Gap:** WAITING_CUSTOMER pause not implemented in code.

---

## 5. Attachments Flow

### Upload
```
Endpoint: POST /api/v1/attachments/ticket/{ticket_id}
Auth: JWT
Body: multipart/form-data (file)
Result:
- File saved to /data/ATUM DESK/atum-desk/data/uploads/{org_id}/
- SHA256 hash computed
- metadata stored in attachments table
- audit_log entry created
```

### Download
```
Endpoint: GET /api/v1/attachments/{attachment_id}/download
Auth: JWT
Verifies: organization_id match
Returns: File stream
```

**Current Status:** No attachments in DB (count = 0)

---

## 6. First Ticket End-to-End Walkthrough

### Complete Flow (Current State)

1. **Customer logs in**
   ```
   POST /api/v1/auth/login
   Body: username=customer@org.com&password=xxx
   ```

2. **Customer creates ticket**
   ```
   POST /api/v1/tickets
   Header: Authorization: Bearer {token}
   Body: {"subject":"Login issue","description":"Cannot login","priority":"HIGH"}
   Response: {id:"...", status:"NEW", ...}
   ```

3. **Customer views their ticket**
   ```
   GET /api/v1/tickets
   Header: Authorization: Bearer {token}
   Response: [{id:"...", status:"NEW", ...}]
   ```

4. **Manager logs in** (different account)

5. **Manager views new tickets**
   ```
   GET /api/v1/internal/tickets/new
   Header: Authorization: Bearer {manager_token}
   Response: [{id:"...", subject:"Login issue", ...}]
   ```

6. **Manager accepts ticket**
   ```
   POST /api/v1/internal/tickets/{ticket_id}/accept
   Header: Authorization: Bearer {manager_token}
   Response: {status:"success", message:"Ticket accepted"}
   ```

7. **Manager assigns to agent**
   ```
   POST /api/v1/internal/tickets/{ticket_id}/assign
   Header: Authorization: Bearer {manager_token}
   Body: {assigned_to:"agent-uuid"}
   ```

8. **SLA Worker runs** (every 60 seconds)
   - Checks tickets with status=ACCEPTED
   - No tickets have sla_started_at set
   - **SLA does NOT start**

### Where It Breaks

| Step | Expected | Actual | Status |
|------|----------|--------|--------|
| Ticket Create | Status=NEW | Status=NEW | ✅ Works |
| Accept Ticket | Set sla_started_at | sla_started_at=NULL | ❌ Breaks |
| SLA Worker | Calculate due dates | No tickets to process | ❌ Breaks |

---

## 7. Comments Flow

### Add Comment
```
Endpoint: POST /api/v1/comments/ticket/{ticket_id}
Auth: JWT
Body: { content, is_internal? }
```

### List Comments
```
Endpoint: GET /api/v1/comments/ticket/{ticket_id}
Auth: JWT
```

---

*Workflow verified via code inspection and DB queries.*
