"""
ATUM DESK - Rules Router (Workflow Builder)
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from app.db.session import get_session
from app.auth.deps import get_current_user
from app.models.user import User, UserRole
from app.models.rules import Rule, RuleAction
from app.models.audit_log import AuditLog

router = APIRouter(prefix="/api/v1/rules", tags=["Rules"])


class RuleActionCreate(BaseModel):
    action_type: str = Field(..., description="e.g., set_priority, assign_to, add_tag")
    action_data: dict = Field(default_factory=dict, description="Action parameters")


class RuleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    event_type: str = Field(..., description="e.g., ticket_create, ticket_update")
    conditions: dict = Field(default_factory=dict, description="JSON conditions")
    execution_order: int = Field(default=0)
    is_active: bool = Field(default=True)
    actions: List[RuleActionCreate] = Field(default_factory=list)


class RuleResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    event_type: str
    conditions: dict
    execution_order: int
    is_active: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


@router.get("", response_model=List[RuleResponse])
async def list_rules(
    event_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """List all rules (admin/agent only)"""
    if current_user.role not in [UserRole.ADMIN, UserRole.AGENT]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    query = select(Rule).options(selectinload(Rule.actions))
    
    if event_type:
        query = query.where(Rule.event_type == event_type)
    
    result = await db.execute(query.order_by(Rule.execution_order))
    rules = result.scalars().all()
    
    return [
        RuleResponse(
            id=str(r.id),
            name=r.name,
            description=r.description,
            event_type=r.event_type,
            conditions=r.conditions,
            execution_order=r.execution_order,
            is_active=r.is_active,
            created_at=r.created_at.isoformat(),
            updated_at=r.updated_at.isoformat()
        ) for r in rules
    ]


@router.post("", response_model=RuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rule(
    rule_data: RuleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Create a new rule (admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Create rule
    rule = Rule(
        name=rule_data.name,
        description=rule_data.description,
        event_type=rule_data.event_type,
        conditions=rule_data.conditions,
        execution_order=rule_data.execution_order,
        is_active=rule_data.is_active
    )
    db.add(rule)
    await db.flush()
    
    # Add actions
    for action_data in rule_data.actions:
        action = RuleAction(
            rule_id=rule.id,
            action_type=action_data.action_type,
            action_data=action_data.action_data
        )
        db.add(action)
    
    # Audit log
    audit = AuditLog(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        action="rule_created",
        entity_type="rule",
        entity_id=rule.id,
        new_values={"name": rule.name, "event_type": rule.event_type}
    )
    db.add(audit)
    
    await db.commit()
    await db.refresh(rule)
    
    return RuleResponse(
        id=str(rule.id),
        name=rule.name,
        description=rule.description,
        event_type=rule.event_type,
        conditions=rule.conditions,
        execution_order=rule.execution_order,
        is_active=rule.is_active,
        created_at=rule.created_at.isoformat(),
        updated_at=rule.updated_at.isoformat()
    )


@router.get("/{rule_id}", response_model=RuleResponse)
async def get_rule(
    rule_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Get rule details (admin/agent)"""
    if current_user.role not in [UserRole.ADMIN, UserRole.AGENT]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        rule_uuid = UUID(rule_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid rule ID")
    
    result = await db.execute(
        select(Rule).options(selectinload(Rule.actions)).where(Rule.id == rule_uuid)
    )
    rule = result.scalar_one_or_none()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    return RuleResponse(
        id=str(rule.id),
        name=rule.name,
        description=rule.description,
        event_type=rule.event_type,
        conditions=rule.conditions,
        execution_order=rule.execution_order,
        is_active=rule.is_active,
        created_at=rule.created_at.isoformat(),
        updated_at=rule.updated_at.isoformat()
    )


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(
    rule_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Delete a rule (admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        rule_uuid = UUID(rule_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid rule ID")
    
    result = await db.execute(select(Rule).where(Rule.id == rule_uuid))
    rule = result.scalar_one_or_none()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    # Audit log
    audit = AuditLog(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        action="rule_deleted",
        entity_type="rule",
        entity_id=rule.id,
        new_values={"name": rule.name}
    )
    db.add(audit)
    
    await db.delete(rule)
    await db.commit()
    
    return None


@router.post("/simulate")
async def simulate_rule(
    event_type: str,
    conditions: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Simulate rule evaluation against sample data"""
    if current_user.role not in [UserRole.ADMIN, UserRole.AGENT]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Get matching rules
    result = await db.execute(
        select(Rule)
        .options(selectinload(Rule.actions))
        .where(Rule.event_type == event_type, Rule.is_active == True)
        .order_by(Rule.execution_order)
    )
    rules = result.scalars().all()
    
    simulation_results = []
    for rule in rules:
        matches = True
        for field, expected in conditions.items():
            actual = conditions.get(field)
            if str(actual).lower() != str(expected).lower():
                matches = False
                break
        
        if matches:
            simulation_results.append({
                "rule_id": str(rule.id),
                "rule_name": rule.name,
                "would_match": True,
                "actions": [
                    {"type": a.action_type, "data": a.action_data}
                    for a in rule.actions
                ]
            })
    
    return {
        "event_type": event_type,
        "input_conditions": conditions,
        "matching_rules": simulation_results
    }
