from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.auth.jwt import get_current_user
from app.models.user import User, UserRole
from app.models.ticket import Ticket
from app.db.session import get_session
from app.config import get_settings
from src.domain.services.smart_reply_engine import SmartReplyEngine, SmartReplyConfig

# We reuse the internal tickets router or create a new sub-router?
# This snippet assumes we append to internal_tickets.py via replace or separate file.
# But internal_tickets.py is big. Let's create a NEW file `app/routers/assistant.py`.

router = APIRouter()

@router.get("/tickets/{ticket_id}/suggestions")
async def get_ticket_suggestions(
    ticket_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Get AI suggestions (Sentiment, RAG, Reply) for a ticket.
    """
    # 1. Check permissions (Agent/Admin)
    if current_user.role not in [UserRole.AGENT, UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(status_code=403, detail="Not authorized")

    # 2. Fetch Ticket
    from uuid import UUID
    try:
        t_uuid = UUID(ticket_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")
        
    result = await db.execute(select(Ticket).where(Ticket.id == t_uuid))
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # 3. Instantiate Engine
    config = SmartReplyConfig(
        organization_id=ticket.organization_id,
        ai_model="ATUM-DESK-AI:latest", # Should match settings
        enabled=True
    )
    engine = SmartReplyEngine(config)
    
    # 4. Generate
    suggestions = await engine.generate_replies(
        ticket_content=f"{ticket.subject}\n{ticket.description}",
        ticket_history=[], # Todo
        customer_info={"name": "Customer"}, # Todo: fetch user name
        organization_id=str(ticket.organization_id)
    )
    
    return suggestions
