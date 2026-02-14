"""
ATUM DESK - Database Session Management
With RLS Org Context Injection

This module provides guaranteed org context setting for:
- Every FastAPI request DB session
- Every worker DB session
"""
from typing import AsyncGenerator, Optional
from contextvars import ContextVar
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import AsyncSessionLocal

logger = logging.getLogger(__name__)

org_context_var: ContextVar[Optional[str]] = ContextVar('org_context', default=None)
user_context_var: ContextVar[Optional[str]] = ContextVar('user_context', default=None)
role_context_var: ContextVar[Optional[str]] = ContextVar('role_context', default=None)


async def set_rls_context(
    session: AsyncSession,
    org_id: Optional[str] = None,
    user_id: Optional[str] = None,
    role: Optional[str] = None
) -> None:
    """
    Guaranteed RLS context setter - MUST be called before any tenant query.
    
    Uses SET LOCAL for transaction-scoped context that doesn't leak to other sessions.
    
    Args:
        session: Active AsyncSession
        org_id: Organization UUID
        user_id: User UUID  
        role: User role (ADMIN, AGENT, CUSTOMER)
    """
    if org_id:
        await session.execute(text(f"SET LOCAL app.current_org = '{org_id}'"))
        logger.debug("rls_context_set org_id=%s", org_id)
    if user_id:
        await session.execute(text(f"SET LOCAL app.current_user = '{user_id}'"))
        logger.debug("rls_context_set user_id=%s", user_id)
    if role:
        await session.execute(text(f"SET LOCAL app.current_role = '{role}'"))
        logger.debug("rls_context_set role=%s", role)


async def validate_rls_context(session: AsyncSession) -> dict:
    """
    Validate that RLS context is properly set.
    Returns dict with context status.
    """
    result = await session.execute(text("SELECT current_setting('app.current_org', true), current_setting('app.current_user', true), current_setting('app.current_role', true)"))
    row = result.fetchone()
    
    return {
        "org_id": row[0] if row else None,
        "user_id": row[1] if row else None,
        "role": row[2] if row else None,
        "is_set": row[0] is not None and row[0] != '' if row else False
    }


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session for dependency injection with org context"""
    async with AsyncSessionLocal() as session:
        org_id = org_context_var.get()
        user_id = user_context_var.get()
        role = role_context_var.get()
        
        await set_rls_context(session, org_id, user_id, role)
        
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def set_org_context(org_id: Optional[str]) -> None:
    """Set org context for current request"""
    if org_id:
        org_context_var.set(str(org_id))
    else:
        org_context_var.set(None)


def set_user_context(user_id: Optional[str]) -> None:
    """Set user context for current request"""
    if user_id:
        user_context_var.set(str(user_id))
    else:
        user_context_var.set(None)


def set_role_context(role: Optional[str]) -> None:
    """Set role context for current request"""
    if role:
        role_context_var.set(str(role))
    else:
        role_context_var.set(None)


async def get_session_with_org(org_id: str) -> AsyncGenerator[AsyncSession, None]:
    """Get session with explicit org context (for workers/scripts)"""
    async with AsyncSessionLocal() as session:
        await set_rls_context(session, org_id=org_id)
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_session_with_rls(
    org_id: Optional[str] = None,
    user_id: Optional[str] = None,
    role: Optional[str] = None
) -> AsyncGenerator[AsyncSession, None]:
    """Get session with explicit RLS context (for workers/scripts)"""
    async with AsyncSessionLocal() as session:
        await set_rls_context(session, org_id, user_id, role)
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_global_session() -> AsyncGenerator[AsyncSession, None]:
    """Get session without org context (for global queries only)"""
    async with AsyncSessionLocal() as session:
        await session.execute(text("SET LOCAL app.current_org = NULL"))
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
