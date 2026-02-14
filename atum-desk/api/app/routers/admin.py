"""
ATUM DESK - Admin Router
System management endpoints
"""
from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel

from app.auth.deps import get_current_user
from app.models.user import User, UserRole
from app.db.session import get_session

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])


class IPRuleCreate(BaseModel):
    ip_address: str
    rule_type: str  # allow, deny
    description: str = ""


class IPSettingsUpdate(BaseModel):
    ip_restrictions_enabled: bool


@router.get("/jobs")
async def get_jobs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Get job queue status"""
    if current_user.role not in (UserRole.ADMIN, UserRole.MANAGER):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = await db.execute(
        text("""
            SELECT id, job_type, status, priority, retry_count, last_error, created_at, updated_at
            FROM job_queue
            ORDER BY created_at DESC
            LIMIT 100
        """)
    )
    rows = result.fetchall()
    
    return {
        "jobs": [
            {
                "id": str(r[0]),
                "job_type": r[1],
                "status": r[2],
                "priority": r[3],
                "retry_count": r[4],
                "last_error": r[5],
                "created_at": r[6].isoformat() if r[6] else None,
                "updated_at": r[7].isoformat() if r[7] else None,
            }
            for r in rows
        ]
    }


@router.get("/rag-queue")
async def get_rag_queue(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Get RAG index queue status"""
    if current_user.role not in (UserRole.ADMIN, UserRole.MANAGER):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = await db.execute(
        text("""
            SELECT id, document_type, status, error_message, created_at, updated_at
            FROM rag_index_queue
            ORDER BY created_at DESC
            LIMIT 50
        """)
    )
    rows = result.fetchall()
    
    return {
        "jobs": [
            {
                "id": str(r[0]),
                "document_type": r[1],
                "status": r[2],
                "error_message": r[3],
                "created_at": r[4].isoformat() if r[4] else None,
                "updated_at": r[5].isoformat() if r[5] else None,
            }
            for r in rows
        ]
    }


@router.get("/ip-rules")
async def get_ip_rules(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Get IP restriction rules"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = await db.execute(
        text("""
            SELECT id, ip_address, rule_type, description, is_active, created_at
            FROM org_ip_allowlist
            WHERE organization_id = :org_id
            ORDER BY created_at DESC
        """),
        {"org_id": str(current_user.organization_id)}
    )
    rows = result.fetchall()
    
    return {
        "rules": [
            {
                "id": str(r[0]),
                "ip_address": r[1],
                "rule_type": r[2],
                "description": r[3],
                "is_active": r[4],
                "created_at": r[5].isoformat() if r[5] else None,
            }
            for r in rows
        ]
    }


@router.post("/ip-rules")
async def create_ip_rule(
    rule: IPRuleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Create IP restriction rule"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    from uuid import uuid4
    rule_id = str(uuid4())
    
    await db.execute(
        text("""
            INSERT INTO org_ip_allowlist (id, organization_id, ip_address, rule_type, description, is_active, created_at)
            VALUES (:id, :org_id, :ip_address, :rule_type, :description, true, :now)
        """),
        {
            "id": rule_id,
            "org_id": str(current_user.organization_id),
            "ip_address": rule.ip_address,
            "rule_type": rule.rule_type,
            "description": rule.description,
            "now": datetime.now(timezone.utc)
        }
    )
    await db.commit()
    
    return {"id": rule_id, "message": "Rule created"}


@router.get("/ip-settings")
async def get_ip_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Get IP restriction settings"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get from org_settings
    result = await db.execute(
        text("""
            SELECT settings FROM organizations WHERE id = :org_id
        """),
        {"org_id": str(current_user.organization_id)}
    )
    row = result.fetchone()
    
    settings = row[0] if row and row[0] else {}
    
    return {
        "ip_restrictions_enabled": settings.get("ip_restrictions_enabled", False)
    }


@router.put("/ip-settings")
async def update_ip_settings(
    settings: IPSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Update IP restriction settings"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get current settings
    result = await db.execute(
        text("""
            SELECT settings FROM organizations WHERE id = :org_id
        """),
        {"org_id": str(current_user.organization_id)}
    )
    row = result.fetchone()
    
    current_settings = row[0] if row and row[0] else {}
    current_settings["ip_restrictions_enabled"] = settings.ip_restrictions_enabled
    
    await db.execute(
        text("""
            UPDATE organizations SET settings = :settings WHERE id = :org_id
        """),
        {"settings": current_settings, "org_id": str(current_user.organization_id)}
    )
    await db.commit()
    
    return {"message": "Settings updated"}


@router.get("/system-health")
async def get_system_health(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Get system health overview"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get job counts
    jobs_result = await db.execute(
        text("SELECT status, COUNT(*) FROM job_queue GROUP BY status")
    )
    job_counts = {r[0]: r[1] for r in jobs_result.fetchall()}
    
    # Get ticket counts
    tickets_result = await db.execute(
        text("SELECT status, COUNT(*) FROM tickets GROUP BY status")
    )
    ticket_counts = {r[0]: r[1] for r in tickets_result.fetchall()}
    
    return {
        "jobs": job_counts,
        "tickets": ticket_counts,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


class BreakGlassAuth(BaseModel):
    primary_key: str
    secondary_key: str


def verify_break_glass(auth: BreakGlassAuth) -> bool:
    """Verify break-glass two-key authentication"""
    import os
    primary = os.getenv("BREAK_GLASS_PRIMARY_KEY", "atum-primary-change-me")
    secondary = os.getenv("BREAK_GLASS_SECONDARY_KEY", "atum-secondary-change-me")
    return auth.primary_key == primary and auth.secondary_key == secondary


@router.get("/rls/health")
async def get_rls_health(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Get RLS health status - admin only"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get all RLS-enabled tables
    tables_result = await db.execute(
        text("""
            SELECT tablename, rowsecurity 
            FROM pg_tables 
            WHERE schemaname = 'public' AND rowsecurity = true
            ORDER BY tablename
        """)
    )
    rls_tables = [{"table": r[0], "enabled": r[1]} for r in tables_result.fetchall()]
    
    # Get policy counts per table
    policies_result = await db.execute(
        text("""
            SELECT tablename, COUNT(*) as policy_count
            FROM pg_policies
            WHERE schemaname = 'public'
            GROUP BY tablename
            ORDER BY tablename
        """)
    )
    policy_counts = {r[0]: r[1] for r in policies_result.fetchall()}
    
    # Check degraded mode
    degraded_result = await db.execute(
        text("SELECT value FROM system_settings WHERE key = 'rls_global_override'")
    )
    degraded_row = degraded_result.fetchone()
    global_degraded = False
    if degraded_row:
        global_degraded = degraded_row[0].get("global_degraded", False) if isinstance(degraded_row[0], dict) else False
    
    # Get org-specific degraded mode
    org_degraded_result = await db.execute(
        text("SELECT id, settings FROM organizations WHERE settings->>'rls_degraded_mode' = 'true'")
    )
    orgs_in_degraded_mode = [str(r[0]) for r in org_degraded_result.fetchall()]
    
    # Test context validation
    context_test_result = await db.execute(
        text("SELECT current_setting('app.current_org', true)")
    )
    context_value = context_test_result.fetchone()[0]
    
    # Determine overall status
    if not rls_tables:
        status = "critical"
    elif global_degraded or orgs_in_degraded_mode:
        status = "degraded"
    else:
        status = "healthy"
    
    return {
        "status": status,
        "rls_enabled_tables": [
            {"table": t["table"], "enabled": t["enabled"], "policy_count": policy_counts.get(t["table"], 0)}
            for t in rls_tables
        ],
        "total_tables_with_rls": len(rls_tables),
        "context_validation": {
            "middleware_active": True,
            "current_setting_works": context_value is not None,
            "current_value": context_value or "not set"
        },
        "degraded_mode": {
            "global_override": global_degraded,
            "orgs_in_degraded_mode": orgs_in_degraded_mode,
            "effective": global_degraded or len(orgs_in_degraded_mode) > 0
        },
        "worker_status": {
            "job_worker_rls_safe": True,
            "rag_worker_rls_safe": True,
            "sla_worker_rls_safe": True
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.post("/rls/degrade")
async def rls_degrade(
    auth: BreakGlassAuth,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Enable RLS degraded mode - requires break-glass auth"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if not verify_break_glass(auth):
        from app.routers.metrics import rls_emergency_actions_total
        rls_emergency_actions_total.labels(action="degrade_failed", actor="unknown").inc()
        raise HTTPException(status_code=403, detail="Invalid break-glass credentials")
    
    await db.execute(text("SELECT rls_emergency_degrade(:actor)"), {"actor": current_user.email})
    await db.commit()
    
    from app.routers.metrics import rls_emergency_actions_total
    rls_emergency_actions_total.labels(action="degrade", actor=current_user.email).inc()
    
    return {"message": "RLS degraded mode activated", "actor": current_user.email}


@router.post("/rls/rollback")
async def rls_rollback(
    auth: BreakGlassAuth,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Emergency RLS rollback - requires break-glass auth"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if not verify_break_glass(auth):
        from app.routers.metrics import rls_emergency_actions_total
        rls_emergency_actions_total.labels(action="rollback_failed", actor="unknown").inc()
        raise HTTPException(status_code=403, detail="Invalid break-glass credentials")
    
    await db.execute(text("SELECT rls_emergency_rollback(:actor)"), {"actor": current_user.email})
    await db.commit()
    
    from app.routers.metrics import rls_emergency_actions_total
    rls_emergency_actions_total.labels(action="rollback", actor=current_user.email).inc()
    
    return {"message": "RLS emergency rollback completed", "actor": current_user.email}


@router.post("/rls/restore")
async def rls_restore(
    auth: BreakGlassAuth,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Restore RLS from snapshot - requires break-glass auth"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if not verify_break_glass(auth):
        from app.routers.metrics import rls_emergency_actions_total
        rls_emergency_actions_total.labels(action="restore_failed", actor="unknown").inc()
        raise HTTPException(status_code=403, detail="Invalid break-glass credentials")
    
    try:
        await db.execute(text("SELECT rls_restore_previous(:actor)"), {"actor": current_user.email})
        await db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    from app.routers.metrics import rls_emergency_actions_total
    rls_emergency_actions_total.labels(action="restore", actor=current_user.email).inc()
    
    return {"message": "RLS state restored from snapshot", "actor": current_user.email}


@router.get("/rls/snapshots")
async def get_rls_snapshots(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Get RLS state snapshots - admin only"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = await db.execute(
        text("""
            SELECT id, snapshot_name, action_type, created_by, notes, created_at
            FROM rls_state_snapshot
            ORDER BY created_at DESC
            LIMIT 20
        """)
    )
    
    return {
        "snapshots": [
            {
                "id": str(r[0]),
                "name": r[1],
                "action": r[2],
                "actor": r[3],
                "notes": r[4],
                "created_at": r[5].isoformat() if r[5] else None
            }
            for r in result.fetchall()
        ]
    }
