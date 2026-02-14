# 01 - CHANGELOG

## Summary
Implemented SLA lifecycle management: start on ACCEPT, pause on WAITING_CUSTOMER, worker respects pauses.

## Files Touched

| File | Change |
|------|--------|
| `atum-desk/api/app/routers/internal_tickets.py` | Accept endpoint + Status endpoint |
| `atum-desk/api/scripts/run_sla_worker.py` | Worker pause logic |

## Why It's Safe

1. **Additive only** - No table schema changes
2. **Transaction atomic** - All SLA updates + audit logs in same transaction
3. **No breaking changes** - Existing behavior preserved, enhanced only
4. **Worker graceful** - Skips tickets without SLA, skips paused tickets
5. **Audit trail** - Full old/new values logged

## Implementation Details

### Accept Endpoint
- Sets `sla_started_at` on first accept
- Calculates `sla_due_at` from policy if exists
- Writes audit log with old/new values

### Status Endpoint  
- Enters `WAITING_CUSTOMER`: sets `sla_paused_at = now()`
- Leaves `WAITING_CUSTOMER`: calculates pause duration, adds to `sla_paused_duration`, clears `sla_paused_at`
- Full audit logging of pause state changes

### SLA Worker
- Skips tickets with `sla_started_at IS NULL`
- Skips tickets in `WAITING_CUSTOMER` status
- Logs summary: processed, skipped_null_sla, skipped_paused
