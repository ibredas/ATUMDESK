from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, HttpUrl
from sqlalchemy import select

from app.db.session import get_session
from app.auth.jwt import get_current_user
from app.models.user import User, UserRole
from app.models.webhook import Webhook

router = APIRouter()

class WebhookCreate(BaseModel):
    url: HttpUrl
    secret: str
    event_types: List[str] # ["ticket.created", "*"]
    description: Optional[str] = None

class WebhookResponse(BaseModel):
    id: str
    url: HttpUrl
    event_types: List[str]
    is_active: bool
    created_at: datetime
    last_triggered_at: Optional[datetime] = None
    failure_count: int

@router.post("", response_model=WebhookResponse, status_code=status.HTTP_201_CREATED)
async def create_webhook(
    webhook_in: WebhookCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Register a new webhook"""
    # Only admins/managers? Let's say yes for now.
    if not current_user.is_staff:
        raise HTTPException(status_code=403, detail="Not authorized")

    webhook = Webhook(
        organization_id=current_user.organization_id,
        url=str(webhook_in.url),
        secret=webhook_in.secret,
        event_types=webhook_in.event_types,
        description=webhook_in.description,
        created_by_id=current_user.id
    )
    
    db.add(webhook)
    await db.commit()
    await db.refresh(webhook)
    
    return WebhookResponse(
        id=str(webhook.id),
        url=webhook.url,
        event_types=webhook.event_types,
        is_active=webhook.is_active,
        created_at=webhook.created_at,
        last_triggered_at=webhook.last_triggered_at,
        failure_count=webhook.failure_count
    )

@router.get("", response_model=List[WebhookResponse])
async def list_webhooks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """List webhooks for organization"""
    if not current_user.is_staff:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    result = await db.execute(
        select(Webhook).where(Webhook.organization_id == current_user.organization_id)
    )
    webhooks = result.scalars().all()
    
    return [
        WebhookResponse(
            id=str(w.id),
            url=w.url,
            event_types=w.event_types,
            is_active=w.is_active,
            created_at=w.created_at,
            last_triggered_at=w.last_triggered_at,
            failure_count=w.failure_count
        ) for w in webhooks
    ]

@router.delete("/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(
    webhook_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Delete a webhook"""
    if not current_user.is_staff:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    from uuid import UUID
    try:
        w_uuid = UUID(webhook_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID")

    result = await db.execute(
        select(Webhook).where(
            Webhook.id == w_uuid,
            Webhook.organization_id == current_user.organization_id
        )
    )
    webhook = result.scalar_one_or_none()
    
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
        
    await db.delete(webhook)
    await db.commit()
