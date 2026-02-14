"""
ATUM DESK - Audit Log Router
"""
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func

from app.db.session import get_session
from app.auth.deps import get_current_user
from app.models.user import User, UserRole
from app.models.audit_log import AuditLog

router = APIRouter(prefix="/api/v1/audit", tags=["Audit"])


class AuditLogResponse(BaseModel):
    id: str
    organization_id: str
    user_id: Optional[str]
    action: str
    entity_type: Optional[str]
    entity_id: Optional[str]
    old_values: Optional[dict]
    new_values: Optional[dict]
    created_at: str

    class Config:
        from_attributes = True


@router.get("", response_model=List[AuditLogResponse])
async def list_audit_logs(
    entity_type: Optional[str] = None,
    action: Optional[str] = None,
    entity_id: Optional[str] = None,
    user_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """List audit logs (admin/agent only)"""
    if current_user.role not in [UserRole.ADMIN, UserRole.AGENT]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Build query
    query = select(AuditLog).where(
        AuditLog.organization_id == current_user.organization_id
    )
    
    if entity_type:
        query = query.where(AuditLog.entity_type == entity_type)
    if action:
        query = query.where(AuditLog.action == action)
    if entity_id:
        query = query.where(AuditLog.entity_id == UUID(entity_id))
    if user_id:
        query = query.where(AuditLog.user_id == UUID(user_id))
    if start_date:
        query = query.where(AuditLog.created_at >= start_date)
    if end_date:
        query = query.where(AuditLog.created_at <= end_date)
    
    # Order by most recent first
    query = query.order_by(desc(AuditLog.created_at))
    
    # Paginate
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    result = await db.execute(query)
    logs = result.scalars().all()
    
    return [
        AuditLogResponse(
            id=str(log.id),
            organization_id=str(log.organization_id),
            user_id=str(log.user_id) if log.user_id else None,
            action=log.action,
            entity_type=log.entity_type,
            entity_id=str(log.entity_id) if log.entity_id else None,
            old_values=log.old_values,
            new_values=log.new_values,
            created_at=log.created_at.isoformat()
        ) for log in logs
    ]


@router.get("/export")
async def export_audit_logs(
    entity_type: Optional[str] = None,
    action: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    format: str = Query("json", regex="^(json|csv)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Export audit logs (admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Build query (no pagination for export)
    query = select(AuditLog).where(
        AuditLog.organization_id == current_user.organization_id
    )
    
    if entity_type:
        query = query.where(AuditLog.entity_type == entity_type)
    if action:
        query = query.where(AuditLog.action == action)
    if start_date:
        query = query.where(AuditLog.created_at >= start_date)
    if end_date:
        query = query.where(AuditLog.created_at <= end_date)
    
    query = query.order_by(desc(AuditLog.created_at)).limit(10000)
    
    result = await db.execute(query)
    logs = result.scalars().all()
    
    if format == "csv":
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Action", "Entity Type", "Entity ID", "User ID", "Created At", "Old Values", "New Values"])
        
        for log in logs:
            writer.writerow([
                str(log.id),
                log.action,
                log.entity_type,
                str(log.entity_id) if log.entity_id else "",
                str(log.user_id) if log.user_id else "",
                log.created_at.isoformat(),
                str(log.old_values) if log.old_values else "",
                str(log.new_values) if log.new_values else ""
            ])
        
        return {
            "format": "csv",
            "data": output.getvalue(),
            "count": len(logs)
        }
    
    return {
        "format": "json",
        "data": [
            {
                "id": str(log.id),
                "action": log.action,
                "entity_type": log.entity_type,
                "entity_id": str(log.entity_id) if log.entity_id else None,
                "user_id": str(log.user_id) if log.user_id else None,
                "created_at": log.created_at.isoformat(),
                "old_values": log.old_values,
                "new_values": log.new_values
            } for log in logs
        ],
        "count": len(logs)
    }


@router.get("/stats")
async def get_audit_stats(
    days: int = Query(7, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Get audit log statistics"""
    if current_user.role not in [UserRole.ADMIN, UserRole.AGENT]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    from datetime import timedelta
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Count by action
    action_count = await db.execute(
        select(AuditLog.action, func.count(AuditLog.id))
        .where(
            AuditLog.organization_id == current_user.organization_id,
            AuditLog.created_at >= start_date
        )
        .group_by(AuditLog.action)
    )
    
    # Count by entity type
    entity_count = await db.execute(
        select(AuditLog.entity_type, func.count(AuditLog.id))
        .where(
            AuditLog.organization_id == current_user.organization_id,
            AuditLog.created_at >= start_date
        )
        .group_by(AuditLog.entity_type)
    )
    
    # Total count
    total = await db.execute(
        select(func.count(AuditLog.id))
        .where(
            AuditLog.organization_id == current_user.organization_id,
            AuditLog.created_at >= start_date
        )
    )
    
    return {
        "period_days": days,
        "total_actions": total.scalar(),
        "by_action": {row[0]: row[1] for row in action_count if row[0]},
        "by_entity_type": {row[0]: row[1] for row in entity_count if row[0]}
    }
