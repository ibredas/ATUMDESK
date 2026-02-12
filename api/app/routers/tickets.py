"""
ATUM DESK - Tickets Router (Customer Portal)
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from sqlalchemy import select, desc

from app.db.session import get_session
from app.auth.jwt import get_current_user
from app.models.user import User, UserRole
from app.models.ticket import Ticket, TicketStatus, TicketPriority

router = APIRouter()


class TicketCreate(BaseModel):
    subject: str = Field(..., min_length=5, max_length=500)
    description: str = Field(..., min_length=10)
    priority: TicketPriority = TicketPriority.MEDIUM
    service_id: Optional[str] = None


class TicketResponse(BaseModel):
    id: str
    subject: str
    description: str
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime


@router.get("", response_model=List[TicketResponse])
async def list_my_tickets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """List tickets for current customer"""
    result = await db.execute(
        select(Ticket)
        .where(
            Ticket.organization_id == current_user.organization_id,
            Ticket.requester_id == current_user.id
        )
        .order_by(desc(Ticket.created_at))
    )
    tickets = result.scalars().all()
    
    return [
        TicketResponse(
            id=str(t.id),
            subject=t.subject,
            description=t.description[:200] + "..." if len(t.description) > 200 else t.description,
            status=t.status.value,
            priority=t.priority.value,
            created_at=t.created_at,
            updated_at=t.updated_at
        ) for t in tickets
    ]


from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from app.services.webhook_service import webhook_service
from app.services.email_notification import email_notification_service

# ... (imports)

@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket_data: TicketCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Create new ticket (customer)"""
    # ... (validation)
    
    # ... (creation)
    
    db.add(new_ticket)
    await db.commit() # Commit expressly so ID is finalized and data persisted for webhook longevity
    await db.refresh(new_ticket)
    
    # Trigger Webhook
    payload = {
        "id": str(new_ticket.id),
        "subject": new_ticket.subject,
        "status": new_ticket.status.value,
        "priority": new_ticket.priority.value,
        "requester_id": str(new_ticket.requester_id),
        "created_at": new_ticket.created_at.isoformat()
    }
    background_tasks.add_task(
        webhook_service.dispatch_event,
        organization_id=new_ticket.organization_id,
        event_type="ticket.created",
        payload=payload
    )

    # Send Email Notification
    email_body = f"""
    <h2>Ticket Created</h2>
    <p>Dear {current_user.full_name},</p>
    <p>Your ticket has been received and is being processed.</p>
    <p><strong>Subject:</strong> {new_ticket.subject}</p>
    <p><strong>Ticket ID:</strong> {new_ticket.id}</p>
    <br>
    <p>Best regards,<br>ATUM DESK Support</p>
    """
    background_tasks.add_task(
        email_notification_service.send_email,
        to_email=current_user.email,
        subject=f"[ATUM DESK] Ticket Received: {new_ticket.subject}",
        body_html=email_body
    )
    
    # Send Slack Notification
    background_tasks.add_task(
        slack_service.send_notification,
        message=f"🎫 *New Ticket Created*\n*ID:* {new_ticket.id}\n*Subject:* {new_ticket.subject}\n*By:* {current_user.email}"
    )
    
    # RAG Indexing
    from app.services.rag.indexer import index_ticket
    background_tasks.add_task(index_ticket, new_ticket)
    
    return TicketResponse(

        id=str(new_ticket.id),
        subject=new_ticket.subject,
        description=new_ticket.description,
        status=new_ticket.status.value,
        priority=new_ticket.priority.value,
        created_at=new_ticket.created_at,
        updated_at=new_ticket.updated_at
    )


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Get ticket details (customer - own tickets only)"""
    from uuid import UUID as UUID_TYPE
    try:
        ticket_uuid = UUID_TYPE(ticket_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ticket ID")
    
    result = await db.execute(
        select(Ticket).where(
            Ticket.id == ticket_uuid,
            Ticket.organization_id == current_user.organization_id,
            Ticket.requester_id == current_user.id
        )
    )
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return TicketResponse(
        id=str(ticket.id),
        subject=ticket.subject,
        description=ticket.description,
        status=ticket.status.value,
        priority=ticket.priority.value,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at
    )
