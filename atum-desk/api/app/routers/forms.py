"""
ATUM DESK - Service Forms Router
osTicket-style dynamic forms for service catalog
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

router = APIRouter(prefix="/api/v1/forms", tags=["service-forms"])


class FormField(BaseModel):
    field_name: str
    field_type: str  # text, number, date, dropdown, checkbox, multiselect, textarea
    label: str
    required: bool = False
    options: Optional[List[str]] = None  # For dropdown/multiselect
    validation: Optional[str] = None  # Regex pattern
    default_value: Optional[str] = None


class ServiceFormCreate(BaseModel):
    service_id: Optional[str] = None
    name: str
    fields: List[FormField]


class FormSubmissionCreate(BaseModel):
    form_id: str
    field_values: dict


@router.get("/services")
async def list_service_forms(
    service_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """List forms for a service"""
    query = """
        SELECT id, service_id, name, fields, is_active, created_at
        FROM service_forms
        WHERE organization_id = :org_id AND is_active = true
    """
    params = {"org_id": str(current_user.organization_id)}
    
    if service_id:
        query += " AND service_id = :service_id"
        params["service_id"] = service_id
    
    query += " ORDER BY name"
    
    result = await db.execute(text(query), params)
    rows = result.fetchall()
    
    return [{
        "id": str(row[0]),
        "service_id": str(row[1]) if row[1] else None,
        "name": row[2],
        "fields": row[3] if isinstance(row[3], list) else [],
        "is_active": row[4],
        "created_at": row[5].isoformat() if row[5] else None
    } for row in rows]


@router.post("/services")
async def create_service_form(
    form: ServiceFormCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Create a new service form"""
    form_id = str(uuid4())
    
    fields_json = [{
        "field_name": f.field_name,
        "field_type": f.field_type,
        "label": f.label,
        "required": f.required,
        "options": f.options,
        "validation": f.validation,
        "default_value": f.default_value
    } for f in form.fields]
    
    await db.execute(
        text("""
            INSERT INTO service_forms (id, organization_id, service_id, name, fields, is_active, created_at, updated_at)
            VALUES (:id, :org_id, :service_id, :name, :fields, true, :now, :now)
        """),
        {
            "id": form_id,
            "org_id": str(current_user.organization_id),
            "service_id": form.service_id,
            "name": form.name,
            "fields": str(fields_json),
            "now": datetime.now(timezone.utc)
        }
    )
    await db.commit()
    
    return {"id": form_id, "message": "Form created"}


@router.get("/services/{form_id}")
async def get_service_form(
    form_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Get a service form"""
    result = await db.execute(
        text("""
            SELECT id, service_id, name, fields, is_active, created_at
            FROM service_forms
            WHERE id = :id AND organization_id = :org_id
        """),
        {"id": form_id, "org_id": str(current_user.organization_id)}
    )
    row = result.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Form not found")
    
    return {
        "id": str(row[0]),
        "service_id": str(row[1]) if row[1] else None,
        "name": row[2],
        "fields": row[3] if isinstance(row[3], list) else [],
        "is_active": row[4],
        "created_at": row[5].isoformat() if row[5] else None
    }


@router.put("/services/{form_id}")
async def update_service_form(
    form_id: str,
    form: ServiceFormCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Update a service form"""
    fields_json = [{
        "field_name": f.field_name,
        "field_type": f.field_type,
        "label": f.label,
        "required": f.required,
        "options": f.options,
        "validation": f.validation,
        "default_value": f.default_value
    } for f in form.fields]
    
    await db.execute(
        text("""
            UPDATE service_forms 
            SET name = :name, fields = :fields, service_id = :service_id, updated_at = :now
            WHERE id = :id AND organization_id = :org_id
        """),
        {
            "id": form_id,
            "org_id": str(current_user.organization_id),
            "service_id": form.service_id,
            "name": form.name,
            "fields": str(fields_json),
            "now": datetime.now(timezone.utc)
        }
    )
    await db.commit()
    
    return {"message": "Form updated"}


@router.delete("/services/{form_id}")
async def delete_service_form(
    form_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Soft delete a service form"""
    await db.execute(
        text("""
            UPDATE service_forms SET is_active = false, updated_at = :now
            WHERE id = :id AND organization_id = :org_id
        """),
        {"id": form_id, "org_id": str(current_user.organization_id), "now": datetime.now(timezone.utc)}
    )
    await db.commit()
    
    return {"message": "Form deleted"}


@router.post("/submissions")
async def submit_form(
    submission: FormSubmissionCreate,
    ticket_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Submit a form as part of ticket creation"""
    submission_id = str(uuid4())
    
    await db.execute(
        text("""
            INSERT INTO form_submissions (id, ticket_id, form_id, organization_id, field_values, submitted_at)
            VALUES (:id, :ticket_id, :form_id, :org_id, :field_values, :now)
        """),
        {
            "id": submission_id,
            "ticket_id": ticket_id,
            "form_id": submission.form_id,
            "org_id": str(current_user.organization_id),
            "field_values": str(submission.field_values),
            "now": datetime.now(timezone.utc)
        }
    )
    await db.commit()
    
    return {"submission_id": submission_id, "message": "Form submitted"}


@router.get("/tickets/{ticket_id}/submissions")
async def get_ticket_form_submissions(
    ticket_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Get form submissions for a ticket"""
    result = await db.execute(
        text("""
            SELECT fs.id, fs.form_id, sf.name, fs.field_values, fs.submitted_at
            FROM form_submissions fs
            JOIN service_forms sf ON sf.id = fs.form_id
            WHERE fs.ticket_id = :ticket_id AND fs.organization_id = :org_id
            ORDER BY fs.submitted_at DESC
        """),
        {"ticket_id": ticket_id, "org_id": str(current_user.organization_id)}
    )
    rows = result.fetchall()
    
    return [{
        "submission_id": str(row[0]),
        "form_id": str(row[1]),
        "form_name": row[2],
        "field_values": row[3],
        "submitted_at": row[4].isoformat() if row[4] else None
    } for row in rows]
