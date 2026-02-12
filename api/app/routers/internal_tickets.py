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
from app.auth.jwt import get_current_user
from app.models.user import User, UserRole
from app.models.ticket import Ticket, TicketStatus, TicketPriority

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
    
    ticket.status = TicketStatus.ACCEPTED
    ticket.accepted_by = current_user.id
    ticket.accepted_at = datetime.utcnow()
    
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
    
    ticket.status = status_data.status
    
    if status_data.status == TicketStatus.RESOLVED:
        ticket.resolved_at = datetime.utcnow()
    elif status_data.status == TicketStatus.CLOSED:
        ticket.closed_at = datetime.utcnow()
    
    await db.flush()
    
    return {"status": "success", "message": "Status updated", "new_status": status_data.status.value}
