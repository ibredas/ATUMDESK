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
from app.models.problem import Problem, ProblemTicketLink
from app.models.ticket import Ticket

router = APIRouter()

# --- Pydantic Models ---
class ProblemCreate(BaseModel):
    title: str
    description: str
    severity: Optional[str] = "medium"
    root_cause: Optional[str] = None
    workaround: Optional[str] = None

class ProblemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    severity: Optional[str] = None
    root_cause: Optional[str] = None
    workaround: Optional[str] = None

class LinkTicketRequest(BaseModel):
    ticket_id: uuid.UUID
    link_type: str = "relates_to"

class ProblemResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    status: str
    severity: Optional[str]
    root_cause: Optional[str]
    workaround: Optional[str]
    created_at: datetime
    updated_at: datetime
    # We could include linked ticket count here

# --- Routes ---

@router.get("", response_model=List[ProblemResponse])
async def list_problems(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """List problems (Agent Only)"""
    if current_user.role == UserRole.CUSTOMER_USER:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    query = select(Problem).where(Problem.organization_id == current_user.organization_id)
    
    if status:
        query = query.where(Problem.status == status)
        
    result = await db.execute(query.order_by(desc(Problem.updated_at)))
    return result.scalars().all()

@router.post("", response_model=ProblemResponse)
async def create_problem(
    data: ProblemCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Create Problem (Agent Only)"""
    if current_user.role == UserRole.CUSTOMER_USER:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    problem = Problem(
        organization_id=current_user.organization_id,
        title=data.title,
        description=data.description,
        severity=data.severity,
        root_cause=data.root_cause,
        workaround=data.workaround,
        created_by=current_user.id,
        status="open"
    )
    db.add(problem)
    await db.commit()
    await db.refresh(problem)
    return problem

@router.get("/{problem_id}", response_model=ProblemResponse)
async def get_problem(
    problem_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Get Problem Detail"""
    if current_user.role == UserRole.CUSTOMER_USER:
        raise HTTPException(status_code=403, detail="Not authorized")

    query = select(Problem).where(
        Problem.id == problem_id, 
        Problem.organization_id == current_user.organization_id
    )
    result = await db.execute(query)
    problem = result.scalar_one_or_none()
    
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
        
    return problem

@router.put("/{problem_id}", response_model=ProblemResponse)
async def update_problem(
    problem_id: uuid.UUID,
    data: ProblemUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Update Problem"""
    if current_user.role == UserRole.CUSTOMER_USER:
        raise HTTPException(status_code=403, detail="Not authorized")

    query = select(Problem).where(
        Problem.id == problem_id, 
        Problem.organization_id == current_user.organization_id
    )
    result = await db.execute(query)
    problem = result.scalar_one_or_none()
    
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
        
    if data.title: problem.title = data.title
    if data.description: problem.description = data.description
    if data.status: problem.status = data.status
    if data.severity: problem.severity = data.severity
    if data.root_cause: problem.root_cause = data.root_cause
    if data.workaround: problem.workaround = data.workaround
    
    problem.updated_by = current_user.id
    
    await db.commit()
    await db.refresh(problem)
    return problem

@router.post("/{problem_id}/link-ticket", status_code=201)
async def link_ticket(
    problem_id: uuid.UUID,
    data: LinkTicketRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Link a ticket to this problem"""
    if current_user.role == UserRole.CUSTOMER_USER:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    # Check problem exists
    query = select(Problem).where(Problem.id == problem_id, Problem.organization_id == current_user.organization_id)
    if not (await db.execute(query)).scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Problem not found")

    # Check ticket exists
    t_query = select(Ticket).where(Ticket.id == data.ticket_id, Ticket.organization_id == current_user.organization_id)
    if not (await db.execute(t_query)).scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    link = ProblemTicketLink(
        organization_id=current_user.organization_id,
        problem_id=problem_id,
        ticket_id=data.ticket_id,
        link_type=data.link_type,
        created_by=current_user.id
    )
    db.add(link)
    await db.commit()
    return {"status": "linked"}
