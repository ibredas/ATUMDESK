"""
ATUM DESK - Notifications Router
"""
from datetime import datetime, timezone
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.auth.deps import get_current_user
from app.models.user import User
from app.db.session import get_session
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


class NotificationCreate(BaseModel):
    type: str
    title: str
    message: Optional[str] = None


@router.get("")
async def list_notifications(
    unread_only: bool = False,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """List notifications for current user"""
    query = """
        SELECT id, type, title, message, read, created_at
        FROM notifications
        WHERE organization_id = :org_id AND user_id = :user_id
    """
    if unread_only:
        query += " AND read = false"
    query += " ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
    
    result = await db.execute(
        text(query),
        {
            "org_id": str(current_user.organization_id),
            "user_id": str(current_user.id),
            "limit": limit,
            "offset": offset
        }
    )
    rows = result.fetchall()
    
    return [{
        "id": str(row[0]),
        "type": row[1],
        "title": row[2],
        "message": row[3],
        "read": row[4],
        "created_at": row[5].isoformat() if row[5] else None
    } for row in rows]


@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Get count of unread notifications"""
    result = await db.execute(
        text("""
            SELECT COUNT(*) FROM notifications
            WHERE organization_id = :org_id AND user_id = :user_id AND read = false
        """),
        {"org_id": str(current_user.organization_id), "user_id": str(current_user.id)}
    )
    count = result.fetchone()[0]
    
    return {"unread_count": count}


@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Mark notification as read"""
    await db.execute(
        text("""
            UPDATE notifications SET read = true
            WHERE id = :id AND user_id = :user_id
        """),
        {"id": notification_id, "user_id": str(current_user.id)}
    )
    await db.commit()
    
    return {"message": "Notification marked as read"}


@router.post("/read-all")
async def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Mark all notifications as read"""
    await db.execute(
        text("""
            UPDATE notifications SET read = true
            WHERE organization_id = :org_id AND user_id = :user_id AND read = false
        """),
        {"org_id": str(current_user.organization_id), "user_id": str(current_user.id)}
    )
    await db.commit()
    
    return {"message": "All notifications marked as read"}


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Delete a notification"""
    await db.execute(
        text("DELETE FROM notifications WHERE id = :id AND user_id = :user_id"),
        {"id": notification_id, "user_id": str(current_user.id)}
    )
    await db.commit()
    
    return {"message": "Notification deleted"}
