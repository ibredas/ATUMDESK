"""
ATUM DESK - Playbooks Router
Mattermost-style runbooks/incident response templates
"""
from datetime import datetime, timezone
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Any

from app.auth.deps import get_current_user
from app.models.user import User
from app.db.session import get_session
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/playbooks", tags=["playbooks"])


class PlaybookStep(BaseModel):
    step_number: int
    title: str
    description: Optional[str] = None
    owner_role: Optional[str] = None
    estimated_minutes: Optional[int] = None


class PlaybookTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    steps: List[PlaybookStep]
    is_active: bool = True


class PlaybookStepUpdate(BaseModel):
    status: str
    owner_id: Optional[str] = None
    notes: Optional[str] = None


@router.get("")
async def list_playbook_templates(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """List all playbook templates for org"""
    result = await db.execute(
        text("""
            SELECT id, name, description, steps, is_active, created_at
            FROM playbook_templates
            WHERE organization_id = :org_id AND is_active = true
            ORDER BY name
        """),
        {"org_id": str(current_user.organization_id)}
    )
    rows = result.fetchall()
    
    return [{
        "id": str(row[0]),
        "name": row[1],
        "description": row[2],
        "steps": row[3] if isinstance(row[3], list) else [],
        "is_active": row[4],
        "created_at": row[5].isoformat() if row[5] else None
    } for row in rows]


@router.post("")
async def create_playbook_template(
    template: PlaybookTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Create a new playbook template"""
    template_id = str(uuid4())
    
    steps_json = [{"step_number": s.step_number, "title": s.title, 
                   "description": s.description, "owner_role": s.owner_role,
                   "estimated_minutes": s.estimated_minutes} for s in template.steps]
    
    await db.execute(
        text("""
            INSERT INTO playbook_templates (id, organization_id, name, description, steps, is_active, created_by, created_at, updated_at)
            VALUES (:id, :org_id, :name, :desc, :steps, :active, :user_id, :now, :now)
        """),
        {
            "id": template_id,
            "org_id": str(current_user.organization_id),
            "name": template.name,
            "desc": template.description,
            "steps": str(steps_json),
            "active": template.is_active,
            "user_id": str(current_user.id),
            "now": datetime.now(timezone.utc)
        }
    )
    await db.commit()
    
    return {"id": template_id, "message": "Playbook template created"}


@router.get("/{template_id}")
async def get_playbook_template(
    template_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Get a playbook template"""
    result = await db.execute(
        text("""
            SELECT id, name, description, steps, is_active, created_at
            FROM playbook_templates
            WHERE id = :id AND organization_id = :org_id
        """),
        {"id": template_id, "org_id": str(current_user.organization_id)}
    )
    row = result.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return {
        "id": str(row[0]),
        "name": row[1],
        "description": row[2],
        "steps": row[3] if isinstance(row[3], list) else [],
        "is_active": row[4],
        "created_at": row[5].isoformat() if row[5] else None
    }


@router.post("/tickets/{ticket_id}/playbook")
async def start_playbook_on_ticket(
    ticket_id: str,
    template_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Start a playbook run on a ticket"""
    run_id = str(uuid4())
    
    # Get template steps
    result = await db.execute(
        text("SELECT steps FROM playbook_templates WHERE id = :id"),
        {"id": template_id}
    )
    row = result.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Template not found")
    
    steps = row[0] if isinstance(row[0], list) else []
    
    # Create playbook run
    await db.execute(
        text("""
            INSERT INTO playbook_runs (id, ticket_id, template_id, organization_id, status, started_at, created_at)
            VALUES (:id, :ticket_id, :template_id, :org_id, 'in_progress', :now, :now)
        """),
        {
            "id": run_id,
            "ticket_id": ticket_id,
            "template_id": template_id,
            "org_id": str(current_user.organization_id),
            "now": datetime.now(timezone.utc)
        }
    )
    
    # Create step logs
    for step in steps:
        step_id = str(uuid4())
        await db.execute(
            text("""
                INSERT INTO playbook_steps_log (id, run_id, step_number, title, description, status, created_at)
                VALUES (:id, :run_id, :step_num, :title, :desc, 'pending', :now)
            """),
            {
                "id": step_id,
                "run_id": run_id,
                "step_num": step.get("step_number", 1),
                "title": step.get("title", "Step"),
                "desc": step.get("description"),
                "now": datetime.now(timezone.utc)
            }
        )
    
    await db.commit()
    
    return {"run_id": run_id, "message": "Playbook started on ticket"}


@router.get("/tickets/{ticket_id}/playbook")
async def get_ticket_playbook_run(
    ticket_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Get active playbook run for a ticket"""
    result = await db.execute(
        text("""
            SELECT pr.id, pr.status, pr.started_at, pr.completed_at,
                   pt.name, pt.description
            FROM playbook_runs pr
            JOIN playbook_templates pt ON pt.id = pr.template_id
            WHERE pr.ticket_id = :ticket_id 
            AND pr.status = 'in_progress'
            ORDER BY pr.started_at DESC
            LIMIT 1
        """),
        {"ticket_id": ticket_id}
    )
    row = result.fetchone()
    
    if not row:
        return {"active_run": None}
    
    # Get steps
    steps_result = await db.execute(
        text("""
            SELECT id, step_number, title, description, status, owner_id, notes, completed_at
            FROM playbook_steps_log
            WHERE run_id = :run_id
            ORDER BY step_number
        """),
        {"run_id": str(row[0])}
    )
    steps = steps_result.fetchall()
    
    return {
        "active_run": {
            "run_id": str(row[0]),
            "status": row[1],
            "started_at": row[2].isoformat() if row[2] else None,
            "completed_at": row[3].isoformat() if row[3] else None,
            "template_name": row[4],
            "template_description": row[5],
            "steps": [{
                "step_id": str(s[0]),
                "step_number": s[1],
                "title": s[2],
                "description": s[3],
                "status": s[4],
                "owner_id": str(s[5]) if s[5] else None,
                "notes": s[6],
                "completed_at": s[7].isoformat() if s[7] else None
            } for s in steps]
        }
    }


@router.patch("/runs/{run_id}/steps/{step_id}")
async def update_playbook_step(
    run_id: str,
    step_id: str,
    update: PlaybookStepUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Update a step status in a playbook run"""
    completed_at = datetime.now(timezone.utc) if update.status == "completed" else None
    
    await db.execute(
        text("""
            UPDATE playbook_steps_log
            SET status = :status, owner_id = :owner_id, notes = :notes, completed_at = :completed_at
            WHERE id = :step_id AND run_id = :run_id
        """),
        {
            "status": update.status,
            "owner_id": update.owner_id,
            "notes": update.notes,
            "completed_at": completed_at,
            "step_id": step_id,
            "run_id": run_id
        }
    )
    
    # Check if all steps completed
    result = await db.execute(
        text("""
            SELECT COUNT(*) FROM playbook_steps_log
            WHERE run_id = :run_id AND status != 'completed'
        """),
        {"run_id": run_id}
    )
    remaining = result.fetchone()[0]
    
    if remaining == 0:
        await db.execute(
            text("""
                UPDATE playbook_runs SET status = 'completed', completed_at = :now WHERE id = :run_id
            """),
            {"run_id": run_id, "now": datetime.now(timezone.utc)}
        )
    
    await db.commit()
    
    return {"message": "Step updated", "remaining_steps": remaining}
