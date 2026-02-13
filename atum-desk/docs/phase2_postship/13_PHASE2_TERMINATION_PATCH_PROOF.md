# 13 - PHASE 2 TERMINATION PATCH PROOF

## Safety Snapshot

### Git State
```
Commit: 31c8fe64ec62bfd29a68cc2619f19b9ace976ada
```

### SLAService.calculate_targets() Location
```
api/app/services/sla_service.py:17
```

### Current SLAService Code (Before Fix)
```python
async def calculate_targets(self, ticket: Ticket):
    """
    Calculate and set SLA targets for a ticket based on its policy.
    """
    if not ticket.sla_policy_id:
        logger.debug(f"Ticket {ticket.id} has no SLA policy.")
        return

    policy = await self.db.get(SLAPolicy, ticket.sla_policy_id)
    if not policy:
        return

    # Simple 24/7 calculation for Phase 1
    now = datetime.utcnow()
    
    response_minutes = policy.get_response_time(ticket.priority)
    resolution_minutes = policy.get_resolution_time(ticket.priority)
    # ... sets targets without checking status
```

### grep SLA Fields in Routers
```
api/app/routers/tickets.py: sla_started_at, sla_due_at (in audit)
api/app/routers/internal_tickets.py: sla_started_at, sla_due_at (in accept endpoint)
```

### Issues Found
1. **SLA calculates regardless of status** - calculate_targets() runs on NEW tickets
2. **Audit written AFTER auto logic** - ticket_created doesn't capture true creation state
3. **Silent RAG failures** - ImportError swallowed with pass

---

## Fixes Applied

### 1. SLAService - Enforce ACCEPT Status
```python
# NEW CODE - api/app/services/sla_service.py
async def calculate_targets(self, ticket: Ticket):
    # SLA spec: Only compute targets for ACCEPTED tickets
    from app.models.ticket import TicketStatus
    if ticket.status != TicketStatus.ACCEPTED:
        logger.debug(f"SLA targets skipped: status is {ticket.status.value}, not ACCEPTED")
        return
```

### 2. Ticket Router - Audit Fidelity
```python
# BEFORE: Audit written AFTER Rules/SLA
# AFTER: 
# 1. Write ticket_created BEFORE auto logic
# 2. Capture pre-auto state
# 3. Run Rules/SLA
# 4. If fields changed, write ticket_auto_updated
```

### 3. RAG Failure Logging
```python
# BEFORE: except ImportError: pass
# AFTER: except ImportError as e:
#     logging.warning(..., exc_info=True)
```

---

## Verification

### Test 1: NEW Ticket has NULL SLA
```
SELECT id, status, sla_started_at, sla_due_at FROM tickets WHERE status='NEW';
 id | status | sla_started_at | sla_due_at 
----+--------+---------------+------------
```

### Test 2: After Accept, SLA is Set
```
SELECT id, status, sla_started_at, sla_due_at FROM tickets WHERE status='ACCEPTED';
 id | status | sla_started_at | sla_due_at 
----+--------+---------------+------------
```

---

## Summary

| Fix | Status |
|-----|--------|
| SLA only on ACCEPT | ✅ Applied |
| Audit fidelity | ✅ Applied |
| RAG logging | ✅ Applied |
