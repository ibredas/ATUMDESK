"""
ATUM DESK - Internal Tickets Router (Staff)
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from sqlalchemy import select, desc, and_

from app.db.session import get_session
from app.auth.deps import get_current_user
from app.models.user import User, UserRole
from app.models.ticket import Ticket, TicketStatus, TicketPriority
from app.config import get_settings

router = APIRouter()


class TicketAssignRequest(BaseModel):
    assigned_to: str


class TicketStatusRequest(BaseModel):
    status: TicketStatus


class InternalTicketResponse(BaseModel):
    id: str
    subject: str
    description: str
    status: str
    priority: str
    requester_email: str
    assigned_to: Optional[str]
    created_at: datetime
    updated_at: datetime


@router.get("/", response_model=List[InternalTicketResponse])
async def list_all_tickets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """List all tickets for internal staff (agent/manager/admin)"""
    if current_user.role not in [UserRole.AGENT, UserRole.MANAGER, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Base query
    query = (
        select(Ticket, User.email)
        .join(User, Ticket.requester_id == User.id)
        .where(Ticket.organization_id == current_user.organization_id)
        .order_by(desc(Ticket.created_at))
    )
    
    # If agent, maybe restrict? Spec says agents see all org tickets or assigned?
    # Usually Helpdesk agents see all unassigned + assigned to them.
    # But for now, let's allow seeing full org tickets for "Inbox" view, 
    # matching the frontend client-side filtering approach.
    
    result = await db.execute(query)
    
    tickets = []
    for ticket, requester_email in result.all():
        tickets.append(InternalTicketResponse(
            id=str(ticket.id),
            subject=ticket.subject,
            description=ticket.description[:200] + "..." if ticket.description and len(ticket.description) > 200 else (ticket.description or ""),
            status=ticket.status.value,
            priority=ticket.priority.value,
            requester_email=requester_email,
            assigned_to=str(ticket.assigned_to) if ticket.assigned_to else None,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at
        ))
    
    return tickets


@router.get("/new", response_model=List[InternalTicketResponse])
async def list_new_tickets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """List new unaccepted tickets (manager inbox)"""
    if current_user.role not in [UserRole.MANAGER, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    result = await db.execute(
        select(Ticket, User.email)
        .join(User, Ticket.requester_id == User.id)
        .where(
            Ticket.organization_id == current_user.organization_id,
            Ticket.status == TicketStatus.NEW
        )
        .order_by(desc(Ticket.created_at))
    )
    
    tickets = []
    for ticket, requester_email in result.all():
        tickets.append(InternalTicketResponse(
            id=str(ticket.id),
            subject=ticket.subject,
            description=ticket.description[:200] + "..." if len(ticket.description) > 200 else ticket.description,
            status=ticket.status.value,
            priority=ticket.priority.value,
            requester_email=requester_email,
            assigned_to=str(ticket.assigned_to) if ticket.assigned_to else None,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at
        ))
    
    return tickets


@router.post("/{ticket_id}/accept")
async def accept_ticket(
    ticket_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Accept a new ticket (manager)"""
    if current_user.role not in [UserRole.MANAGER, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    from uuid import UUID as UUID_TYPE
    try:
        ticket_uuid = UUID_TYPE(ticket_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ticket ID")
    
    result = await db.execute(
        select(Ticket).where(
            Ticket.id == ticket_uuid,
            Ticket.organization_id == current_user.organization_id,
            Ticket.status == TicketStatus.NEW
        )
    )
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found or already accepted")
    
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
            logging.getLogger("sla").warning(f"No SLA policy for ticket {ticket.id}, SLA started but no due date set")
    
    # Write audit log for acceptance with old and new values
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
    
    await db.flush()
    
    return {"status": "success", "message": "Ticket accepted", "ticket_id": ticket_id}


@router.post("/{ticket_id}/assign")
async def assign_ticket(
    ticket_id: str,
    assign_data: TicketAssignRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Assign ticket to agent (manager)"""
    if current_user.role not in [UserRole.MANAGER, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    from uuid import UUID as UUID_TYPE
    try:
        ticket_uuid = UUID_TYPE(ticket_id)
        agent_uuid = UUID_TYPE(assign_data.assigned_to)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    # Verify agent exists and is in same org
    agent_result = await db.execute(
        select(User).where(
            User.id == agent_uuid,
            User.organization_id == current_user.organization_id,
            User.role.in_([UserRole.AGENT, UserRole.MANAGER]),
            User.is_active == True
        )
    )
    if not agent_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Get ticket
    result = await db.execute(
        select(Ticket).where(
            Ticket.id == ticket_uuid,
            Ticket.organization_id == current_user.organization_id
        )
    )
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    ticket.assigned_to = agent_uuid
    ticket.status = TicketStatus.ASSIGNED
    
    await db.flush()
    
    return {"status": "success", "message": "Ticket assigned", "ticket_id": ticket_id}


@router.post("/{ticket_id}/status")
async def update_ticket_status(
    ticket_id: str,
    status_data: TicketStatusRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Update ticket status (agent+)"""
    if current_user.role not in [UserRole.AGENT, UserRole.MANAGER, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    from uuid import UUID as UUID_TYPE
    try:
        ticket_uuid = UUID_TYPE(ticket_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ticket ID")
    
    result = await db.execute(
        select(Ticket).where(
            Ticket.id == ticket_uuid,
            Ticket.organization_id == current_user.organization_id
        )
    )
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Check if agent can modify this ticket
    if current_user.role == UserRole.AGENT:
        if ticket.assigned_to != current_user.id:
            raise HTTPException(status_code=403, detail="Not assigned to this ticket")
    
    old_status = ticket.status.value
    old_sla_paused_at = ticket.sla_paused_at
    old_sla_paused_duration = ticket.sla_paused_duration
    
    ticket.status = status_data.status
    
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
    
    if status_data.status == TicketStatus.RESOLVED:
        ticket.resolved_at = datetime.utcnow()
        
        # RAG Indexing on resolve (per spec - only resolved tickets are indexed)
        settings = get_settings()
        if settings.RAG_ENABLED and settings.RAG_INDEX_ON_TICKET_RESOLVE:
            try:
                from app.services.rag.indexer import enqueue_index
                await enqueue_index(
                    db,
                    ticket.organization_id,
                    "ticket",
                    ticket.id,
                    "upsert"
                )
            except Exception as e:
                import logging
                logging.getLogger("internal_tickets").warning(f"RAG indexing enqueue failed for ticket {ticket.id}: {e}", exc_info=True)
                
    elif status_data.status == TicketStatus.CLOSED:
        ticket.closed_at = datetime.utcnow()
    
    # Audit Log for status change with pause info
    from app.models.audit_log import AuditLog
    audit = AuditLog(
        organization_id=ticket.organization_id,
        user_id=current_user.id,
        action="ticket_status_changed",
        entity_type="ticket",
        entity_id=ticket.id,
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
    )
    db.add(audit)
    
    await db.flush()
    
    return {"status": "success", "message": "Status updated", "new_status": status_data.status.value}
