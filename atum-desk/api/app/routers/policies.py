"""
Policy Center API Routes - CRUD + Simulation
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.auth.deps import get_current_user
from app.models.user import User, UserRole
from app.db.session import get_session

router = APIRouter(tags=["Policy Center"])


class PolicyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    target: str
    action: str
    effect: str
    condition_json: Optional[dict] = None
    priority: int = 100
    enabled: bool = True


class PolicyResponse(BaseModel):
    id: str
    name: str
    target: str
    action: str
    effect: str
    enabled: bool
    priority: int


class PolicySimulateRequest(BaseModel):
    action: str
    target: str
    user_id: str
    roles: List[str]
    resource_context: Optional[dict] = None


@router.get("")
async def list_policies(
    target: Optional[str] = Query(None),
    enabled: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """List all policy rules"""
    org_id = str(current_user.organization_id)
    
    where = "WHERE organization_id = :org_id OR organization_id IS NULL"
    params = {"org_id": org_id}
    
    if target:
        where += " AND target = :target"
        params["target"] = target
    if enabled is not None:
        where += " AND enabled = :enabled"
        params["enabled"] = enabled
    
    result = await db.execute(
        text(f"""
            SELECT id, name, description, target, action, effect, condition_json, priority, enabled, created_at
            FROM policy_rules
            {where}
            ORDER BY priority DESC
        """),
        params
    )
    
    policies = []
    for row in result.fetchall():
        policies.append({
            "id": str(row[0]),
            "name": row[1],
            "description": row[2],
            "target": row[3],
            "action": row[4],
            "effect": row[5],
            "condition_json": row[6],
            "priority": row[7],
            "enabled": row[8],
            "created_at": row[9].isoformat() if row[9] else None
        })
    
    return {"policies": policies}


@router.post("")
async def create_policy(
    policy: PolicyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Create a new policy rule"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin only")
    
    org_id = str(current_user.organization_id)
    
    result = await db.execute(
        text("""
            INSERT INTO policy_rules (
                id, organization_id, name, description, target, action, effect,
                condition_json, priority, enabled, created_by, created_at
            ) VALUES (
                gen_random_uuid(), :org_id, :name, :description, :target, :action, :effect,
                :condition_json, :priority, :enabled, :created_by, NOW()
            )
            RETURNING id
        """),
        {
            "org_id": org_id,
            "name": policy.name,
            "description": policy.description,
            "target": policy.target,
            "action": policy.action,
            "effect": policy.effect,
            "condition_json": policy.condition_json,
            "priority": policy.priority,
            "enabled": policy.enabled,
            "created_by": str(current_user.id)
        }
    )
    
    await db.commit()
    new_id = result.fetchone()[0]
    
    return {"id": str(new_id), "message": "Policy created"}


@router.delete("/{policy_id}")
async def delete_policy(
    policy_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Delete a policy rule"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin only")
    
    org_id = str(current_user.organization_id)
    
    result = await db.execute(
        text("""
            DELETE FROM policy_rules 
            WHERE id = :id AND (organization_id = :org_id OR organization_id IS NULL)
            RETURNING id
        """),
        {"id": policy_id, "org_id": org_id}
    )
    
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Policy not found")
    
    await db.commit()
    return {"message": "Policy deleted"}


@router.post("/simulate")
async def simulate_policy(
    request: PolicySimulateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Simulate a policy decision"""
    org_id = str(current_user.organization_id)
    
    result = await db.execute(
        text("""
            SELECT id, name, effect, condition_json, priority
            FROM policy_rules
            WHERE target = :target 
            AND action = :action 
            AND enabled = true
            AND (organization_id = :org_id OR organization_id IS NULL)
            ORDER BY priority DESC
            LIMIT 1
        """),
        {"target": request.target, "action": request.action, "org_id": org_id}
    )
    
    row = result.fetchone()
    
    if not row:
        return {
            "decision": "ALLOW",
            "reason": "No matching policy - default allow",
            "matched_policy": None
        }
    
    policy_id, name, effect, conditions, priority = row
    
    # Simple evaluation
    if conditions and "roles" in conditions:
        allowed_roles = conditions.get("roles", [])
        if not any(r in allowed_roles for r in request.roles):
            return {
                "decision": "DENY",
                "reason": f"Role not in allowed list: {allowed_roles}",
                "matched_policy": {"id": str(policy_id), "name": name}
            }
    
    return {
        "decision": effect,
        "reason": f"Matched policy: {name}",
        "matched_policy": {"id": str(policy_id), "name": name}
    }
