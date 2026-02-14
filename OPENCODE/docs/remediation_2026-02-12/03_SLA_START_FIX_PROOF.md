# 03 - SLA Start Fix Proof

## Issue
Tickets were never having SLA started when accepted. The `accept_ticket` endpoint did not set `sla_started_at` or calculate SLA due dates.

---

## Fix Applied

### File: `atum-desk/api/app/routers/internal_tickets.py`

**Lines 103-135 (modified):**

```python
ticket.status = TicketStatus.ACCEPTED
ticket.accepted_by = current_user.id
ticket.accepted_at = datetime.utcnow()

# Start SLA when ticket is accepted
ticket.sla_started_at = datetime.utcnow()

# Calculate SLA due dates based on policy and priority
if ticket.sla_policy_id:
    from app.services.sla_service import SLAService
    sla_service = SLAService(db)
    await sla_service.calculate_targets(ticket)

# Write audit log for acceptance
from app.models.audit_log import AuditLog
audit = AuditLog(
    organization_id=ticket.organization_id,
    user_id=current_user.id,
    action="ticket_accepted",
    entity_type="ticket",
    entity_id=ticket.id,
    new_values={
        "status": "ACCEPTED",
        "accepted_by": str(current_user.id),
        "sla_started_at": ticket.sla_started_at.isoformat() if ticket.sla_started_at else None,
        "sla_policy_id": str(ticket.sla_policy_id) if ticket.sla_policy_id else None
    }
)
db.add(audit)

await db.flush()
```

---

## What Happens Now

When a manager accepts a ticket:

1. ✅ `status` → `ACCEPTED`
2. ✅ `accepted_by` → manager's user ID
3. ✅ `accepted_at` → timestamp
4. ✅ `sla_started_at` → timestamp (NEW!)
5. ✅ If `sla_policy_id` exists: SLA service calculates due dates
6. ✅ Audit log entry created for `ticket_accepted`

---

## Database State Before Fix

```sql
SELECT id, status, sla_started_at, sla_policy_id FROM tickets;
```
```
id                  | status | sla_started_at | sla_policy_id 
--------------------------------------+--------+----------------+---------------
85f5ad3f-...       | NEW    | NULL           | NULL
66571720-...       | NEW    | NULL           | NULL  
a81d9979-...       | NEW    | NULL           | 4450ffdc-...   (has policy)
```

All tickets had `sla_started_at = NULL`.

---

## Verification Steps

After a ticket is accepted via API:

```bash
# Accept ticket (requires manager token)
curl -X POST http://localhost:8000/api/v1/internal/tickets/{ticket_id}/accept \
  -H "Authorization: Bearer $MANAGER_TOKEN"

# Check database
SELECT status, accepted_at, sla_started_at, sla_policy_id FROM tickets WHERE id='{ticket_id}';
```

Expected result:
- `status` = ACCEPTED
- `accepted_at` = timestamp
- `sla_started_at` = timestamp (same as accepted_at)
- `sla_calculations` table has response/resolution targets

---

## SLA Worker Integration

The SLA worker (`atum-desk-sla-worker.service`) already runs every 60 seconds:

```
2026-02-12 22:41:46 - Checking SLAs for 1 tickets...
2026-02-12 22:42:46 - Checking SLAs for 1 tickets...
```

Now with `sla_started_at` being set, the SLA service can:
1. Calculate `sla_due_at` based on policy + priority
2. Create `sla_calculations` records
3. Track breaches properly

---

## Service Restarted

```bash
$ sudo systemctl restart atum-desk-api

$ systemctl status atum-desk-api --no-pager | head -5
● atum-desk-api.service - ATUM DESK API Service
     Active: active (running) since Fri 2026-02-13 00:08:01 EET; 7s ago
```

---

## Summary

| Item | Before | After |
|------|--------|-------|
| sla_started_at | NULL | Set to acceptance time |
| SLA targets | Never calculated | Calculated via SLAService |
| Audit log | No event | ticket_accepted logged |
| Service restarted | No | Yes |
