from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List, Dict, Any

from app.db.session import get_session
from app.auth.deps import get_current_user
from app.models.user import User
from app.models.ticket import Ticket, TicketStatus, TicketPriority

router = APIRouter()

@router.get("/dashboard", response_model=Dict[str, Any])
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Get dashboard statistics for the organization"""
    
    # Base query for org
    base_query = select(Ticket).where(Ticket.organization_id == current_user.organization_id)
    
    # Execute queries (could be optimized with group_by, but simple count is safer for now)
    # Total
    total_result = await db.execute(select(func.count()).select_from(Ticket).where(Ticket.organization_id == current_user.organization_id))
    total = total_result.scalar() or 0
    
    # Open
    open_statuses = [TicketStatus.NEW, TicketStatus.ACCEPTED, TicketStatus.ASSIGNED, TicketStatus.IN_PROGRESS]
    open_result = await db.execute(select(func.count()).select_from(Ticket).where(
        Ticket.organization_id == current_user.organization_id,
        Ticket.status.in_(open_statuses)
    ))
    open_count = open_result.scalar() or 0
    
    # Resolved
    resolved_result = await db.execute(select(func.count()).select_from(Ticket).where(
        Ticket.organization_id == current_user.organization_id,
        Ticket.status == TicketStatus.RESOLVED
    ))
    resolved_count = resolved_result.scalar() or 0
    
    # Urgent
    urgent_result = await db.execute(select(func.count()).select_from(Ticket).where(
        Ticket.organization_id == current_user.organization_id,
        Ticket.priority == TicketPriority.URGENT,
        Ticket.status.in_(open_statuses) # Only count open urgent tickets
    ))
    urgent_count = urgent_result.scalar() or 0
    
    # Recent Tickets (limit 8)
    recent_result = await db.execute(
        select(Ticket)
        .where(Ticket.organization_id == current_user.organization_id)
        .order_by(desc(Ticket.created_at))
        .limit(8)
    )
    recent_tickets = recent_result.scalars().all()
    
    recent_data = [{
        "id": str(t.id),
        "subject": t.subject,
        "status": t.status.value,
        "priority": t.priority.value,
        "created_at": t.created_at
    } for t in recent_tickets]

    return {
        "stats": {
            "total": total,
            "open": open_count,
            "resolved": resolved_count,
            "urgent": urgent_count
        },
        "recent_tickets": recent_data
    }
