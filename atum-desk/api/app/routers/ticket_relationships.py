"""
ATUM DESK - Ticket Relationships Router
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.auth.deps import get_current_user
from app.models.user import User, UserRole
from app.models.audit_log import AuditLog
from sqlalchemy import text

router = APIRouter(prefix="/api/v1/internal/tickets", tags=["Ticket Relationships"])


class TicketRelationshipResponse(BaseModel):
    id: str
    source_ticket_id: str
    target_ticket_id: str
    relationship_type: str
    created_at: str


class CreateRelationshipRequest(BaseModel):
    target_ticket_id: str
    relationship_type: str = Field(..., description="parent_of, child_of, duplicate_of, related_to")


RELATIONSHIP_TYPES = ["parent_of", "child_of", "duplicate_of", "related_to"]


def validate_relationship_type(rel_type: str) -> bool:
    return rel_type in RELATIONSHIP_TYPES


async def check_cycle(db: AsyncSession, from_id: str, to_id: str, rel_type: str) -> bool:
    """
    Check if adding this relationship would create a cycle.
    E.g., A->B, then B->A would create a cycle.
    """
    # If new relation is "related_to" or "duplicate_of", no cycle check needed
    if rel_type in ["related_to", "duplicate_of"]:
        return False
    
    # Check if target already has a path to source (would create cycle)
    # Simple check: if A->B, and we add B->A, that's a cycle
    
    # Get all relationships involving the target ticket
    result = await db.execute(
        text("""
            SELECT source_ticket_id, target_ticket_id, relationship_type
            FROM ticket_relationships
            WHERE source_ticket_id = :ticket OR target_ticket_id = :ticket
        """),
        {"ticket": to_id}
    )
    
    existing = {row.relationship_type: (str(row.source_ticket_id), str(row.target_ticket_id)) 
                for row in result.fetchall()}
    
    # If target is already a parent of source, adding source as parent of target creates cycle
    for rel, (src, tgt) in existing.items():
        if rel == "parent_of" and tgt == from_id:
            return True
    
    return False


@router.post("/{ticket_id}/relationships", response_model=TicketRelationshipResponse, status_code=status.HTTP_201_CREATED)
async def create_relationship(
    ticket_id: str,
    request: CreateRelationshipRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Create a relationship between tickets"""
    if current_user.role not in [UserRole.ADMIN, UserRole.AGENT]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    if not validate_relationship_type(request.relationship_type):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid relationship type. Must be one of: {RELATIONSHIP_TYPES}"
        )
    
    # Check if tickets exist
    for tid in [ticket_id, request.target_ticket_id]:
        result = await db.execute(
            text("SELECT id FROM tickets WHERE id = :id"),
            {"id": tid}
        )
        if not result.fetchone():
            raise HTTPException(status_code=404, detail=f"Ticket {tid} not found")
    
    # Check for cycle
    if await check_cycle(db, ticket_id, request.target_ticket_id, request.relationship_type):
        raise HTTPException(
            status_code=400,
            detail="Cannot create relationship: would create a cycle"
        )
    
    # Check if relationship already exists
    result = await db.execute(
        text("""
            SELECT id FROM ticket_relationships 
            WHERE source_ticket_id = :source AND target_ticket_id = :target
            AND relationship_type = :type
        """),
        {"source": ticket_id, "target": request.target_ticket_id, "type": request.relationship_type}
    )
    if result.fetchone():
        raise HTTPException(status_code=400, detail="Relationship already exists")
    
    # Create relationship
    result = await db.execute(
        text("""
            INSERT INTO ticket_relationships (id, source_ticket_id, target_ticket_id, relationship_type, created_at)
            VALUES (gen_random_uuid(), :source, :target, :type, NOW())
            RETURNING id, created_at
        """),
        {"source": ticket_id, "target": request.target_ticket_id, "type": request.relationship_type}
    )
    row = result.fetchone()
    
    # Audit
    audit = AuditLog(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        action="ticket_relationship_added",
        entity_type="ticket",
        entity_id=ticket_id,
        new_values={
            "relationship_type": request.relationship_type,
            "target_ticket_id": request.target_ticket_id
        }
    )
    db.add(audit)
    await db.commit()
    
    return TicketRelationshipResponse(
        id=str(row.id),
        source_ticket_id=ticket_id,
        target_ticket_id=request.target_ticket_id,
        relationship_type=request.relationship_type,
        created_at=row.created_at.isoformat()
    )


@router.get("/{ticket_id}/relationships", response_model=List[TicketRelationshipResponse])
async def list_relationships(
    ticket_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """List all relationships for a ticket"""
    if current_user.role not in [UserRole.ADMIN, UserRole.AGENT, UserRole.CUSTOMER]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    result = await db.execute(
        text("""
            SELECT id, source_ticket_id, target_ticket_id, relationship_type, created_at
            FROM ticket_relationships
            WHERE source_ticket_id = :ticket OR target_ticket_id = :ticket
            ORDER BY created_at DESC
        """),
        {"ticket": ticket_id}
    )
    
    return [
        TicketRelationshipResponse(
            id=str(row.id),
            source_ticket_id=str(row.source_ticket_id),
            target_ticket_id=str(row.target_ticket_id),
            relationship_type=row.relationship_type,
            created_at=row.created_at.isoformat()
        ) for row in result.fetchall()
    ]


@router.delete("/{ticket_id}/relationships/{relationship_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_relationship(
    ticket_id: str,
    relationship_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Delete a ticket relationship"""
    if current_user.role not in [UserRole.ADMIN, UserRole.AGENT]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Check if relationship exists
    result = await db.execute(
        text("""
            SELECT id, relationship_type, target_ticket_id
            FROM ticket_relationships 
            WHERE id = :id AND source_ticket_id = :ticket
        """),
        {"id": relationship_id, "ticket": ticket_id}
    )
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Relationship not found")
    
    # Delete
    await db.execute(
        text("DELETE FROM ticket_relationships WHERE id = :id"),
        {"id": relationship_id}
    )
    
    # Audit
    audit = AuditLog(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        action="ticket_relationship_removed",
        entity_type="ticket",
        entity_id=ticket_id,
        new_values={
            "relationship_type": row.relationship_type,
            "target_ticket_id": str(row.target_ticket_id)
        }
    )
    db.add(audit)
    await db.commit()
    
    return None
