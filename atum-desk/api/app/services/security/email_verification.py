"""
ATUM DESK - Email Verification Service
"""
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.models.user import User
from app.models.audit_log import AuditLog
from app.services.email_notification import EmailNotificationService

TOKEN_EXPIRE_HOURS = 24


def generate_verification_token() -> str:
    """Generate a secure verification token."""
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """Hash token for storage."""
    return hashlib.sha256(token.encode()).hexdigest()


async def create_verification_token(db: AsyncSession, user_id: str) -> str:
    """Create email verification token for user."""
    token = generate_verification_token()
    token_hash = hash_token(token)
    expires_at = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    
    await db.execute(
        text("""
            INSERT INTO email_verification_tokens (id, user_id, token_hash, expires_at)
            VALUES (gen_random_uuid(), :user_id, :token_hash, :expires_at)
        """),
        {"user_id": user_id, "token_hash": token_hash, "expires_at": expires_at}
    )
    
    # Send email
    user_result = await db.execute(
        text("SELECT email, full_name, organization_id FROM users WHERE id = :id"),
        {"id": user_id}
    )
    user_row = user_result.fetchone()
    
    if user_row:
        email_service = EmailNotificationService()
        await email_service.send_email(
            to_email=user_row.email,
            subject="Verify your ATUM DESK account",
            body_html=f"""
            Hello {user_row.full_name},

            Please verify your email address by clicking the link below:

            Your verification token: {token}

            This token expires in {TOKEN_EXPIRE_HOURS} hours.

            If you didn't create this account, please ignore this email.
            """
        )
        
        # Audit
        audit = AuditLog(
            organization_id=user_row.organization_id,
            action="email_verification_sent",
            entity_type="user",
            entity_id=user_id,
            new_values={"email": user_row.email}
        )
        db.add(audit)
        await db.commit()
    
    return token


async def verify_email_token(db: AsyncSession, token: str) -> tuple[bool, Optional[str]]:
    """
    Verify email token.
    Returns (success, error_message)
    """
    token_hash = hash_token(token)
    
    # Find valid token
    result = await db.execute(
        text("""
            SELECT id, user_id, expires_at, used_at 
            FROM email_verification_tokens 
            WHERE token_hash = :hash AND used_at IS NULL AND expires_at > NOW()
            ORDER BY created_at DESC LIMIT 1
        """),
        {"hash": token_hash}
    )
    row = result.fetchone()
    
    if not row:
        return False, "Invalid or expired verification token"
    
    # Mark token as used
    await db.execute(
        text("UPDATE email_verification_tokens SET used_at = NOW() WHERE id = :id"),
        {"id": row.id}
    )
    
    # Update user as verified
    await db.execute(
        text("UPDATE users SET is_email_verified = true WHERE id = :id"),
        {"id": row.user_id}
    )
    
    # Audit
    audit = AuditLog(
        organization_id=None,
        action="email_verified",
        entity_type="user",
        entity_id=row.user_id,
        new_values={}
    )
    db.add(audit)
    await db.commit()
    
    return True, None


async def is_email_verified(db: AsyncSession, user_id: str) -> bool:
    """Check if user email is verified."""
    result = await db.execute(
        text("SELECT is_email_verified FROM users WHERE id = :id"),
        {"id": user_id}
    )
    row = result.fetchone()
    return row.is_email_verified if row else False
