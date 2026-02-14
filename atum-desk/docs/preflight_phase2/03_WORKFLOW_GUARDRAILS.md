# 03_WORKFLOW_GUARDRAILS.md

**Date**: 2026-02-12
**Status**: AUDITED

## 1. Ticket Lifecycle (Hard-coded Enum)
- **File**: `app/models/ticket.py`
- **States**: `NEW`, `ACCEPTED`, `ASSIGNED`, `IN_PROGRESS`, `WAITING_CUSTOMER`, `RESOLVED`, `CLOSED`, `CANCELLED`.
- **Constraint**: Phase 2 modules (Problem/Change) must NOT alter these core states but *link* to them.

## 2. SLA Logic
- **Trigger**: `ticket_create` (via RulesService).
- **Calculation**: `SLAService.calculate_targets`.
- **Targets**: `first_response_target`, `resolution_target`.
- **Constraint**: Phase 2 must preserve `sla_policy_id` on Tickets.

## 3. Audit Logging
- **Model**: `AuditLog` (`app/models/audit_log.py`).
- **Events**: stored in `audit_logs` table.
- **Requirement**: Phase 2 actions (Article publish, Problem close, Change approve) must emit audit events.

## 4. Workflows to Protect
- **Ticket Creation**: Rules engine currently intercepts `ticket_creation`. Phase 2 must not block this synchronous chain.
- **Escalation**: `check_slas` worker runs every 60s. Phase 2 "Change Management" downtimes should ideally suppress alerts (future scope).
