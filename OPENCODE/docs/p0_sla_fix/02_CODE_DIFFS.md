# 02 - CODE DIFFS

## File: `atum-desk/api/app/routers/internal_tickets.py`

### Accept Endpoint Changes

```python
# BEFORE:
ticket.status = TicketStatus.ACCEPTED
ticket.accepted_by = current_user.id
ticket.accepted_at = datetime.utcnow()

# AFTER:
old_status = ticket.status.value
old_accepted_at = ticket.accepted_at
old_sla_started_at = ticket.sla_started_at
old_sla_due_at = ticket.sla_due_at

ticket.status = TicketStatus.ACCEPTED
ticket.accepted_by = current_user.id
ticket.accepted_at = datetime.utcnow()

# Start SLA when ticket is accepted (only if not already started)
if not ticket.sla_started_at:
    ticket.sla_started_at = datetime.utcnow()
    
    # Calculate SLA due dates based on policy and priority
    if ticket.sla_policy_id:
        from app.services.sla_service import SLAService
        sla_service = SLAService(db)
        await sla_service.calculate_targets(ticket)
    else:
        import logging
        logging.getLogger("sla").warning(f"No SLA policy for ticket {ticket.id}")

# Audit log with old/new values
from app.models.audit_log import AuditLog
audit = AuditLog(
    organization_id=ticket.organization_id,
    user_id=current_user.id,
    action="ticket_accepted",
    entity_type="ticket",
    entity_id=ticket.id,
    old_values={
        "status": old_status,
        "accepted_at": old_accepted_at.isoformat() if old_accepted_at else None,
        "sla_started_at": old_sla_started_at.isoformat() if old_sla_started_at else None,
        "sla_due_at": old_sla_due_at.isoformat() if old_sla_due_at else None
    },
    new_values={
        "status": "ACCEPTED",
        "accepted_by": str(current_user.id),
        "accepted_at": ticket.accepted_at.isoformat() if ticket.accepted_at else None,
        "sla_started_at": ticket.sla_started_at.isoformat() if ticket.sla_started_at else None,
        "sla_due_at": ticket.sla_due_at.isoformat() if ticket.sla_due_at else None
    }
)
db.add(audit)
```

### Status Endpoint Changes (Pause Logic)

```python
# Handle SLA pause for WAITING_CUSTOMER
now = datetime.utcnow()
if status_data.status == TicketStatus.WAITING_CUSTOMER:
    # Entering WAITING_CUSTOMER - pause SLA if not already paused
    if ticket.sla_started_at is not None and ticket.sla_paused_at is None:
        ticket.sla_paused_at = now
elif old_status == TicketStatus.WAITING_CUSTOMER.value:
    # Leaving WAITING_CUSTOMER - unpause SLA
    if ticket.sla_paused_at is not None:
        # Handle timezone-aware comparison
        if ticket.sla_paused_at.tzinfo is not None:
            pause_delta = now.replace(tzinfo=None) - ticket.sla_paused_at.replace(tzinfo=None)
        else:
            pause_delta = now - ticket.sla_paused_at
        ticket.sla_paused_duration = (ticket.sla_paused_duration or 0) + int(pause_delta.total_seconds())
        ticket.sla_paused_at = None
```

### Audit Log Changes

```python
# Before:
old_values={"status": old_status}
new_values={"status": status_data.status.value}

# After:
old_values={
    "status": old_status,
    "sla_paused_at": old_sla_paused_at.isoformat() if old_sla_paused_at else None,
    "sla_paused_duration": old_sla_paused_duration
},
new_values={
    "status": status_data.status.value,
    "sla_paused_at": ticket.sla_paused_at.isoformat() if ticket.sla_paused_at else None,
    "sla_paused_duration": ticket.sla_paused_duration
}
```

---

## File: `atum-desk/api/scripts/run_sla_worker.py`

```python
# BEFORE:
query = select(Ticket.id).where(
    Ticket.status != 'closed',
    Ticket.status != 'resolved',
    Ticket.sla_policy_id.is_not(None)
)

# AFTER:
query = select(
    Ticket.id, 
    Ticket.status, 
    Ticket.sla_started_at, 
    Ticket.sla_paused_at, 
    Ticket.sla_paused_duration
).where(
    Ticket.sla_started_at.is_not(None),
    Ticket.status.notin_([TicketStatus.CLOSED, TicketStatus.RESOLVED])
)

# Processing loop:
processed_count = 0
skipped_null_sla_count = 0
skipped_paused_count = 0

for tid, status, sla_started_at, sla_paused_at, sla_paused_duration in tickets:
    if sla_started_at is None:
        skipped_null_sla_count += 1
        continue
    
    if status == TicketStatus.WAITING_CUSTOMER:
        skipped_paused_count += 1
        continue
    
    await sla_service.check_breaches(tid)
    processed_count += 1

logger.info(f"SLA Worker Summary: processed={processed_count}, skipped_null_sla={skipped_null_sla_count}, skipped_paused={skipped_paused_count}")
```
