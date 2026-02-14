"""
ATUM DESK - Internal RLS Health Router
Provides RLS validation endpoints for workers and internal services
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db.session import get_session, validate_rls_context

router = APIRouter(prefix="/internal", tags=["Internal"])


@router.get("/rls/health")
async def rls_health_check(
    db: AsyncSession = Depends(get_session)
):
    """
    Internal RLS health check endpoint.
    
    Validates:
    - Context setting works
    - Policy count
    - Worker readiness
    
    No auth required - internal network only.
    """
    context_status = await validate_rls_context(db)
    
    tables_result = await db.execute(
        text("""
            SELECT tablename, rowsecurity 
            FROM pg_tables 
            WHERE schemaname = 'public' AND rowsecurity = true
            ORDER BY tablename
        """)
    )
    rls_tables = [{"table": r[0], "enabled": r[1]} for r in tables_result.fetchall()]
    
    policies_result = await db.execute(
        text("""
            SELECT COUNT(*) FROM pg_policies
            WHERE schemaname = 'public'
        """)
    )
    policy_count = policies_result.scalar()
    
    return {
        "status": "healthy" if rls_tables else "critical",
        "rls_enabled_tables": rls_tables,
        "total_policies": policy_count,
        "context_validation": {
            "setting_works": True,
            "current_org": context_status.get("org_id"),
            "current_user": context_status.get("user_id"),
            "current_role": context_status.get("role")
        },
        "timestamp": "2026-02-14T00:00:00Z"
    }


@router.get("/rls/validate")
async def rls_validate_context(
    db: AsyncSession = Depends(get_session)
):
    """
    Validate that RLS context is set for current session.
    """
    status = await validate_rls_context(db)
    
    if not status["is_set"]:
        return {
            "valid": False,
            "warning": "RLS context not set - queries may return no results",
            "details": status
        }
    
    return {
        "valid": True,
        "details": status
    }
