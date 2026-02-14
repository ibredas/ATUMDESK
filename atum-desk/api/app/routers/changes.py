import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, or_, and_
from pydantic import BaseModel

from app.db.session import get_session
from app.auth.deps import get_current_user
from app.models.user import User, UserRole
from app.models.change import ChangeRequest, ChangeApproval

router = APIRouter()

# --- Pydantic Models ---
class ChangeCreate(BaseModel):
    title: str
    description: str
    type: str # standard, normal, emergency
    risk_level: Optional[str] = "low"
    planned_start: Optional[datetime] = None
    planned_end: Optional[datetime] = None
    implementation_plan: Optional[str] = None
    rollback_plan: Optional[str] = None

class ChangeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    risk_level: Optional[str] = None
    planned_start: Optional[datetime] = None
    planned_end: Optional[datetime] = None
    implementation_plan: Optional[str] = None
    rollback_plan: Optional[str] = None

class ApprovalCreate(BaseModel):
    decision: str # approved, rejected
    comment: Optional[str] = None

class ChangeResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    status: str
    type: str
    risk_level: str
    planned_start: Optional[datetime]
    planned_end: Optional[datetime]
    created_at: datetime
    updated_at: datetime

# --- Routes ---

@router.get("", response_model=List[ChangeResponse])
async def list_changes(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """List Changes (Agent Only)"""
    if current_user.role == UserRole.CUSTOMER_USER:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    query = select(ChangeRequest).where(ChangeRequest.organization_id == current_user.organization_id)
    
    if status:
        query = query.where(ChangeRequest.status == status)
        
    result = await db.execute(query.order_by(desc(ChangeRequest.updated_at)))
    return result.scalars().all()

@router.post("", response_model=ChangeResponse)
async def create_change(
    data: ChangeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Create Change Request"""
    if current_user.role == UserRole.CUSTOMER_USER:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    change = ChangeRequest(
        organization_id=current_user.organization_id,
        title=data.title,
        description=data.description,
        type=data.type,
        risk_level=data.risk_level,
        planned_start=data.planned_start,
        planned_end=data.planned_end,
        implementation_plan=data.implementation_plan,
        rollback_plan=data.rollback_plan,
        created_by=current_user.id,
        status="draft"
    )
    db.add(change)
    await db.commit()
    await db.refresh(change)
    return change

@router.get("/{change_id}", response_model=ChangeResponse)
async def get_change(
    change_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Get Change Detail"""
    if current_user.role == UserRole.CUSTOMER_USER:
        raise HTTPException(status_code=403, detail="Not authorized")

    query = select(ChangeRequest).where(
        ChangeRequest.id == change_id, 
        ChangeRequest.organization_id == current_user.organization_id
    )
    result = await db.execute(query)
    change = result.scalar_one_or_none()
    
    if not change:
        raise HTTPException(status_code=404, detail="Change not found")
        
    return change

@router.put("/{change_id}", response_model=ChangeResponse)
async def update_change(
    change_id: uuid.UUID,
    data: ChangeUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Update Change Request"""
    if current_user.role == UserRole.CUSTOMER_USER:
        raise HTTPException(status_code=403, detail="Not authorized")

    query = select(ChangeRequest).where(
        ChangeRequest.id == change_id, 
        ChangeRequest.organization_id == current_user.organization_id
    )
    result = await db.execute(query)
    change = result.scalar_one_or_none()
    
    if not change:
        raise HTTPException(status_code=404, detail="Change not found")
        
    # Logic Update: Enforce status transitions? MVP: Allow direct edit for now.
    
    if data.title: change.title = data.title
    if data.description: change.description = data.description
    if data.status: change.status = data.status
    if data.risk_level: change.risk_level = data.risk_level
    if data.planned_start: change.planned_start = data.planned_start
    if data.planned_end: change.planned_end = data.planned_end
    if data.implementation_plan: change.implementation_plan = data.implementation_plan
    if data.rollback_plan: change.rollback_plan = data.rollback_plan
    
    change.updated_by = current_user.id
    
    await db.commit()
    await db.refresh(change)
    return change

@router.post("/{change_id}/approve", status_code=201)
async def submit_approval(
    change_id: uuid.UUID,
    data: ApprovalCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Submit Approval Decision"""
    if current_user.role == UserRole.CUSTOMER_USER:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    query = select(ChangeRequest).where(ChangeRequest.id == change_id, ChangeRequest.organization_id == current_user.organization_id)
    change = (await db.execute(query)).scalar_one_or_none()
    
    if not change:
        raise HTTPException(status_code=404, detail="Change not found")

    # Record Approval
    approval = ChangeApproval(
        organization_id=current_user.organization_id,
        change_request_id=change_id,
        approver_id=current_user.id,
        decision=data.decision,
        comment=data.comment
    )
    db.add(approval)
    
    # Auto-update status based on decision?
    # For MVP: If approved, set to approved. If rejected, set to rejected.
    if data.decision == "approved":
        change.status = "approved"
    elif data.decision == "rejected":
        change.status = "rejected"
        
    await db.commit()
    return {"status": "recorded"}
