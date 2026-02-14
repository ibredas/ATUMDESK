"""
ATUM DESK - Ticket Locks Router
Collision-proof assignment system (FreeScout-style)
"""
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import get_current_user
from app.models.user import User
from app.db.session import get_session

router = APIRouter(prefix="/api/v1/tickets", tags=["ticket-locks"])

LOCK_TTL_MINUTES = 5


@router.post("/{ticket_id}/lock")
async def claim_ticket_lock(
    ticket_id: str,
    lock_type: str = "viewing",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Claim/lock a ticket to prevent collisions"""
    if lock_type not in ("viewing", "editing", "claim"):
        raise HTTPException(status_code=400, detail="Invalid lock_type")
    
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=LOCK_TTL_MINUTES)
    
    result = await db.execute(
        text("""
            INSERT INTO ticket_locks (id, ticket_id, user_id, lock_type, locked_at, expires_at, created_at)
            VALUES (:id, :ticket_id, :user_id, :lock_type, :now, :expires_at, :now)
            ON CONFLICT (ticket_id) 
            WHERE expires_at > NOW()
            DO UPDATE SET 
                user_id = EXCLUDED.user_id,
                lock_type = EXCLUDED.lock_type,
                locked_at = EXCLUDED.locked_at,
                expires_at = EXCLUDED.expires_at
            RETURNING id
        """),
        {
            "id": str(uuid4()),
            "ticket_id": ticket_id,
            "user_id": str(current_user.id),
            "lock_type": lock_type,
            "now": datetime.now(timezone.utc),
            "expires_at": expires_at
        }
    )
    await db.commit()
    
    lock_id = result.fetchone()
    
    return {
        "message": "Ticket locked",
        "lock_id": str(lock_id[0]) if lock_id else None,
        "expires_at": expires_at.isoformat()
    }


@router.delete("/{ticket_id}/lock")
async def release_ticket_lock(
    ticket_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Release a ticket lock"""
    await db.execute(
        text("""
            DELETE FROM ticket_locks 
            WHERE ticket_id = :ticket_id 
            AND user_id = :user_id
            AND expires_at > NOW()
        """),
        {"ticket_id": ticket_id, "user_id": str(current_user.id)}
    )
    await db.commit()
    
    return {"message": "Ticket lock released"}


@router.get("/{ticket_id}/lock")
async def get_ticket_lock(
    ticket_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Get current lock status for a ticket"""
    result = await db.execute(
        text("""
            SELECT tl.id, tl.lock_type, tl.locked_at, tl.expires_at, 
                   u.id as user_id, u.full_name as user_name
            FROM ticket_locks tl
            JOIN users u ON u.id = tl.user_id
            WHERE tl.ticket_id = :ticket_id 
            AND tl.expires_at > NOW()
        """),
        {"ticket_id": ticket_id}
    )
    row = result.fetchone()
    
    if not row:
        return {"locked": False}
    
    return {
        "locked": True,
        "lock_id": str(row[0]),
        "lock_type": row[1],
        "locked_at": row[2].isoformat() if row[2] else None,
        "expires_at": row[3].isoformat() if row[3] else None,
        "user_id": str(row[4]),
        "user_name": row[5]
    }


@router.post("/{ticket_id}/lock/force-release")
async def force_release_lock(
    ticket_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Admin force-release a ticket lock"""
    if current_user.role not in ("admin", "manager"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    await db.execute(
        text("DELETE FROM ticket_locks WHERE ticket_id = :ticket_id"),
        {"ticket_id": ticket_id}
    )
    await db.commit()
    
    return {"message": "Lock force-released by admin"}


@router.post("/{ticket_id}/claim")
async def claim_ticket(
    ticket_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Claim a ticket (assign to self)"""
    # First create a lock
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=LOCK_TTL_MINUTES)
    
    await db.execute(
        text("""
            INSERT INTO ticket_locks (id, ticket_id, user_id, lock_type, locked_at, expires_at, created_at)
            VALUES (:id, :ticket_id, :user_id, 'claim', :now, :expires_at, :now)
            ON CONFLICT (ticket_id) 
            WHERE expires_at > NOW()
            DO UPDATE SET 
                user_id = EXCLUDED.user_id,
                lock_type = 'claim',
                locked_at = EXCLUDED.locked_at,
                expires_at = EXCLUDED.expires_at
        """),
        {
            "id": str(uuid4()),
            "ticket_id": ticket_id,
            "user_id": str(current_user.id),
            "now": datetime.now(timezone.utc),
            "expires_at": expires_at
        }
    )
    
    # Then assign the ticket
    await db.execute(
        text("""
            UPDATE tickets 
            SET assigned_to = :user_id, updated_at = :now
            WHERE id = :ticket_id
        """),
        {"user_id": str(current_user.id), "ticket_id": ticket_id, "now": datetime.now(timezone.utc)}
    )
    await db.commit()
    
    return {"message": "Ticket claimed", "assigned_to": current_user.full_name}
