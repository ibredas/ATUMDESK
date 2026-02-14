"""
Incidents API Routes - CRUD for Major Incident Management
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.auth.deps import get_current_user
from app.models.user import User, UserRole
from app.db.session import get_session

router = APIRouter(tags=["Incidents"])


class IncidentCreate(BaseModel):
    title: str
    severity: str  # SEV1, SEV2, SEV3, SEV4
    customer_impact_summary: Optional[str] = None


class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    customer_impact_summary: Optional[str] = None
    timeline: Optional[list] = None


class IncidentLinkTicket(BaseModel):
    ticket_id: str


@router.get("")
async def list_incidents(
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """List incidents"""
    org_id = str(current_user.organization_id)
    
    where = "WHERE organization_id = :org_id"
    params = {"org_id": org_id, "limit": limit, "offset": offset}
    
    if status:
        where += " AND status = :status"
        params["status"] = status
    if severity:
        where += " AND severity = :severity"
        params["severity"] = severity
    
    result = await db.execute(
        text(f"""
            SELECT id, title, severity, status, commander_id, customer_impact_summary,
                   timeline, start_at, resolved_at, created_at
            FROM incidents
            {where}
            ORDER BY start_at DESC
            LIMIT :limit OFFSET :offset
        """),
        params
    )
    
    incidents = []
    for row in result.fetchall():
        incidents.append({
            "id": str(row[0]),
            "title": row[1],
            "severity": row[2],
            "status": row[3],
            "commander_id": str(row[4]) if row[4] else None,
            "customer_impact_summary": row[5],
            "timeline": row[6],
            "start_at": row[7].isoformat() if row[7] else None,
            "resolved_at": row[8].isoformat() if row[8] else None,
            "created_at": row[9].isoformat() if row[9] else None
        })
    
    return {"incidents": incidents}


@router.post("")
async def create_incident(
    incident: IncidentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Create new incident"""
    if current_user.role not in [UserRole.MANAGER, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Manager or Admin only")
    
    org_id = str(current_user.organization_id)
    
    result = await db.execute(
        text("""
            INSERT INTO incidents (
                id, organization_id, title, severity, status, commander_id,
                customer_impact_summary, timeline, start_at, created_at
            ) VALUES (
                gen_random_uuid(), :org_id, :title, :severity, 'OPEN', :commander_id,
                :impact, JSON_BUILD_ARRAY(JSON_BUILD_OBJECT('time', NOW(), 'action', 'Incident created', 'by', :user_id)),
                NOW(), NOW()
            )
            RETURNING id
        """),
        {
            "org_id": org_id,
            "title": incident.title,
            "severity": incident.severity,
            "commander_id": str(current_user.id),
            "impact": incident.customer_impact_summary,
            "user_id": str(current_user.id)
        }
    )
    
    await db.commit()
    new_id = result.fetchone()[0]
    
    return {"id": str(new_id), "message": "Incident created"}


@router.get("/{incident_id}")
async def get_incident(
    incident_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Get incident details with linked tickets"""
    org_id = str(current_user.organization_id)
    
    result = await db.execute(
        text("""
            SELECT id, title, severity, status, commander_id, customer_impact_summary,
                   timeline, start_at, resolved_at, created_at
            FROM incidents
            WHERE id = :id AND organization_id = :org_id
        """),
        {"id": incident_id, "org_id": org_id}
    )
    
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Get linked tickets
    tickets_result = await db.execute(
        text("""
            SELECT t.id, t.subject, t.status
            FROM incident_ticket_links itl
            JOIN tickets t ON t.id = itl.ticket_id
            WHERE itl.incident_id = :id
        """),
        {"id": incident_id}
    )
    
    tickets = []
    for t in tickets_result.fetchall():
        tickets.append({
            "id": str(t[0]),
            "subject": t[1],
            "status": t[2]
        })
    
    return {
        "id": str(row[0]),
        "title": row[1],
        "severity": row[2],
        "status": row[3],
        "commander_id": str(row[4]) if row[4] else None,
        "customer_impact_summary": row[5],
        "timeline": row[6],
        "start_at": row[7].isoformat() if row[7] else None,
        "resolved_at": row[8].isoformat() if row[8] else None,
        "created_at": row[9].isoformat() if row[9] else None,
        "linked_tickets": tickets
    }


@router.patch("/{incident_id}")
async def update_incident(
    incident_id: str,
    update: IncidentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Update incident"""
    org_id = str(current_user.organization_id)
    
    updates = []
    params = {"id": incident_id, "org_id": org_id, "user_id": str(current_user.id)}
    
    if update.status:
        updates.append("status = :status")
        params["status"] = update.status
    if update.severity:
        updates.append("severity = :severity")
        params["severity"] = update.severity
    if update.title:
        updates.append("title = :title")
        params["title"] = update.title
    
    if not updates:
        raise HTTPException(status_code=400, detail="No updates provided")
    
    # Add timeline entry
    updates.append("timeline = COALESCE(timeline, '[]'::jsonb) || JSON_BUILD_ARRAY(JSON_BUILD_OBJECT('time', NOW(), 'action', 'Updated', 'by', :user_id))")
    
    if update.status == "RESOLVED":
        updates.append("resolved_at = NOW()")
    
    result = await db.execute(
        text(f"""
            UPDATE incidents
            SET {', '.join(updates)}
            WHERE id = :id AND organization_id = :org_id
            RETURNING id
        """),
        params
    )
    
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Incident not found")
    
    await db.commit()
    return {"message": "Incident updated"}


@router.post("/{incident_id}/tickets")
async def link_ticket(
    incident_id: str,
    link: IncidentLinkTicket,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Link ticket to incident"""
    org_id = str(current_user.organization_id)
    
    await db.execute(
        text("""
            INSERT INTO incident_ticket_links (incident_id, ticket_id)
            VALUES (:incident_id, :ticket_id)
            ON CONFLICT DO NOTHING
        """),
        {"incident_id": incident_id, "ticket_id": link.ticket_id}
    )
    
    await db.commit()
    return {"message": "Ticket linked"}
