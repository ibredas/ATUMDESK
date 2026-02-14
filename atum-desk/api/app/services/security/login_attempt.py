"""
ATUM DESK - Login Attempt Service (PostgreSQL-based, NO Redis)
"""
import hashlib
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.audit_log import AuditLog

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


class LoginAttemptService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def record_failed_attempt(self, ip_address: str, username: Optional[str] = None) -> int:
        """Record failed login attempt. Returns current fail count."""
        result = await self.db.execute(
            text("""
                SELECT id, fail_count, locked_until 
                FROM auth_login_attempts 
                WHERE ip_address = :ip AND (locked_until IS NULL OR locked_until < NOW())
                ORDER BY last_attempt_at DESC
                LIMIT 1
            """),
            {"ip": ip_address}
        )
        row = result.fetchone()
        
        # Use database NOW() for consistency
        now_result = await self.db.execute(text("SELECT NOW()"))
        now = now_result.fetchone().now
        
        if row:
            # Update existing record
            new_count = row.fail_count + 1
            locked_until = None
            if new_count >= MAX_LOGIN_ATTEMPTS:
                locked_until = now + timedelta(minutes=LOCKOUT_MINUTES)
            
            await self.db.execute(
                text("""
                    UPDATE auth_login_attempts 
                    SET fail_count = :count, 
                        last_attempt_at = :now,
                        locked_until = :locked
                    WHERE id = :id
                """),
                {"count": new_count, "now": now, "locked": locked_until, "id": row.id}
            )
            return new_count
        else:
            # Create new record
            locked_until = None if MAX_LOGIN_ATTEMPTS > 1 else now + timedelta(minutes=LOCKOUT_MINUTES)
            await self.db.execute(
                text("""
                    INSERT INTO auth_login_attempts (id, ip_address, username, fail_count, last_attempt_at, locked_until)
                    VALUES (gen_random_uuid(), :ip, :user, 1, :now, :locked)
                """),
                {"ip": ip_address, "user": username, "now": now, "locked": locked_until}
            )
            return 1
    
    async def check_locked(self, ip_address: str) -> Optional[datetime]:
        """Check if IP is currently locked. Returns locked_until if locked."""
        result = await self.db.execute(
            text("""
                SELECT locked_until FROM auth_login_attempts 
                WHERE ip_address = :ip AND locked_until > NOW()
                ORDER BY locked_until DESC
                LIMIT 1
            """),
            {"ip": ip_address}
        )
        row = result.fetchone()
        return row.locked_until if row else None
    
    async def record_successful_login(self, ip_address: str):
        """Clear failed attempts after successful login."""
        await self.db.execute(
            text("DELETE FROM auth_login_attempts WHERE ip_address = :ip"),
            {"ip": ip_address}
        )
    
    async def get_fail_count(self, ip_address: str) -> int:
        """Get current fail count for IP."""
        result = await self.db.execute(
            text("""
                SELECT fail_count FROM auth_login_attempts 
                WHERE ip_address = :ip AND (locked_until IS NULL OR locked_until > NOW())
                ORDER BY last_attempt_at DESC
                LIMIT 1
            """),
            {"ip": ip_address}
        )
        row = result.fetchone()
        return row.fail_count if row else 0


async def check_login_allowed(db: AsyncSession, ip_address: str) -> tuple[bool, Optional[str]]:
    """Check if login is allowed. Returns (allowed, error_message)."""
    service = LoginAttemptService(db)
    locked_until = await service.check_locked(ip_address)
    if locked_until:
        # Get current time from database for consistency
        now_result = await db.execute(text("SELECT NOW()"))
        now = now_result.fetchone().now
        remaining = int((locked_until - now).total_seconds() // 60)
        if remaining < 1:
            remaining = 1
        return False, f"Too many failed attempts. Try again in {remaining} minutes."
    return True, None


async def record_failed_login(db: AsyncSession, ip_address: str, username: Optional[str] = None, email: Optional[str] = None):
    """Record failed login and audit it."""
    service = LoginAttemptService(db)
    fail_count = await service.record_failed_attempt(ip_address, username or email)
    
    # Get default organization for audit logging
    org_result = await db.execute(text("SELECT id FROM organizations LIMIT 1"))
    org_row = org_result.fetchone()
    
    # Only log audit if we have an org (skip for failed logins without valid user)
    if org_row:
        org_id = org_row.id
        # Use a placeholder entity_id for auth events (system-level)
        from uuid import UUID
        placeholder_entity_id = UUID("00000000-0000-0000-0000-000000000000")
        
        audit = AuditLog(
            organization_id=org_id,
            action="auth_login_failed",
            entity_type="auth",
            entity_id=placeholder_entity_id,
            new_values={
                "ip_address": str(ip_address),
                "username": username or email,
                "fail_count": fail_count,
                "max_attempts": MAX_LOGIN_ATTEMPTS
            }
        )
        db.add(audit)
        await db.commit()
        
        # Check if locked
        locked_until = await service.check_locked(ip_address)
        if locked_until:
            audit2 = AuditLog(
                organization_id=org_id,
                action="auth_login_locked",
                entity_type="auth",
                entity_id=placeholder_entity_id,
                new_values={"ip_address": str(ip_address), "locked_until": locked_until.isoformat()}
            )
            db.add(audit2)
            await db.commit()


async def record_successful_login_db(db: AsyncSession, ip_address: str):
    """Record successful login and clear failed attempts."""
    service = LoginAttemptService(db)
    await service.record_successful_login(ip_address)
    
    # Get default organization for audit logging
    org_result = await db.execute(text("SELECT id FROM organizations LIMIT 1"))
    org_row = org_result.fetchone()
    
    if org_row:
        from uuid import UUID
        placeholder_entity_id = UUID("00000000-0000-0000-0000-000000000000")
        
        audit = AuditLog(
            organization_id=org_row.id,
            action="auth_login_success",
            entity_type="auth",
            entity_id=placeholder_entity_id,
            new_values={"ip_address": str(ip_address)}
        )
        db.add(audit)
        await db.commit()
