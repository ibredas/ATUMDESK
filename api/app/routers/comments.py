"""
ATUM DESK - Comments Router
"""
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from sqlalchemy import select, desc

from app.db.session import get_session
from app.auth.deps import get_current_user
from app.models.user import User, UserRole
from app.models.ticket import Ticket
from app.models.comment import Comment

router = APIRouter()


class CommentCreate(BaseModel):
    content: str
    is_internal: bool = False


class CommentResponse(BaseModel):
    id: str
    content: str
    author_name: str
    is_internal: bool
    is_ai_generated: bool
    created_at: datetime


@router.get("/ticket/{ticket_id}", response_model=List[CommentResponse])
async def list_comments(
    ticket_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """List comments for a ticket"""
    from uuid import UUID as UUID_TYPE
    try:
        ticket_uuid = UUID_TYPE(ticket_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ticket ID")
    
    # Verify ticket access
    result = await db.execute(
        select(Ticket).where(
            Ticket.id == ticket_uuid,
            Ticket.organization_id == current_user.organization_id
        )
    )
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Customer can only see their own tickets
    if current_user.role == UserRole.CUSTOMER_USER:
        if ticket.requester_id != current_user.id:
            raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Build query
    query = select(Comment, User.full_name).join(
        User, Comment.author_id == User.id
    ).where(
        Comment.ticket_id == ticket_uuid
    ).order_by(desc(Comment.created_at))
    
    # Customers can't see internal comments
    if current_user.role == UserRole.CUSTOMER_USER:
        query = query.where(Comment.is_internal == False)
    
    result = await db.execute(query)
    
    comments = []
    for comment, author_name in result.all():
        comments.append(CommentResponse(
            id=str(comment.id),
            content=comment.content,
            author_name=author_name,
            is_internal=comment.is_internal,
            is_ai_generated=comment.is_ai_generated,
            created_at=comment.created_at
        ))
    
    return comments


@router.post("/ticket/{ticket_id}", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    ticket_id: str,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Add comment to ticket"""
    from uuid import UUID as UUID_TYPE
    try:
        ticket_uuid = UUID_TYPE(ticket_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ticket ID")
    
    # Verify ticket access
    result = await db.execute(
        select(Ticket).where(
            Ticket.id == ticket_uuid,
            Ticket.organization_id == current_user.organization_id
        )
    )
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Authorization checks
    if current_user.role == UserRole.CUSTOMER_USER:
        if ticket.requester_id != current_user.id:
            raise HTTPException(status_code=404, detail="Ticket not found")
        # Customers can't create internal comments
        if comment_data.is_internal:
            raise HTTPException(status_code=403, detail="Cannot create internal comments")
    
    # Create comment
    new_comment = Comment(
        ticket_id=ticket_uuid,
        author_id=current_user.id,
        content=comment_data.content,
        is_internal=comment_data.is_internal
    )
    
    db.add(new_comment)
    await db.flush()
    
    return CommentResponse(
        id=str(new_comment.id),
        content=new_comment.content,
        author_name=current_user.full_name,
        is_internal=new_comment.is_internal,
        is_ai_generated=new_comment.is_ai_generated,
        created_at=new_comment.created_at
    )
