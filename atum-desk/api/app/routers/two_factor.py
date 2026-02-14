"""
ATUM DESK - Two-Factor Authentication Router
"""
import secrets
import pyotp
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.auth.deps import get_current_user
from app.models.user import User
from app.models.audit_log import AuditLog

router = APIRouter(prefix="/api/v1/auth/2fa", tags=["2FA"])


class TwoFactorEnableResponse(BaseModel):
    secret: str
    qr_code: str
    backup_codes: List[str]


class TwoFactorVerifyRequest(BaseModel):
    code: str


class TwoFactorDisableRequest(BaseModel):
    password: str
    code: str


@router.post("/enable", response_model=TwoFactorEnableResponse)
async def enable_2fa(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Enable 2FA for the current user"""
    if current_user.two_factor_enabled:
        raise HTTPException(
            status_code=400,
            detail="2FA is already enabled"
        )
    
    # Generate secret
    secret = pyotp.random_base32()
    
    # Generate backup codes
    backup_codes = [secrets.token_hex(8) for _ in range(8)]
    
    # Store temporarily (not enabled yet - requires verification)
    current_user.two_factor_secret = secret
    current_user.two_factor_backup_codes = backup_codes
    
    # Audit log
    audit = AuditLog(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        action="2fa_enable_initiated",
        entity_type="user",
        entity_id=current_user.id,
        new_values={"method": "TOTP"}
    )
    db.add(audit)
    await db.commit()
    
    # Generate provisioning URI for authenticator apps
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        name=current_user.email,
        issuer_name="ATUM DESK"
    )
    
    return TwoFactorEnableResponse(
        secret=secret,
        qr_code=provisioning_uri,
        backup_codes=backup_codes
    )


@router.post("/verify")
async def verify_2fa(
    request: TwoFactorVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Verify and activate 2FA"""
    if not current_user.two_factor_secret:
        raise HTTPException(
            status_code=400,
            detail="2FA not initiated. Call /enable first."
        )
    
    # Verify TOTP code
    totp = pyotp.TOTP(current_user.two_factor_secret)
    if not totp.verify(request.code):
        raise HTTPException(
            status_code=400,
            detail="Invalid verification code"
        )
    
    # Enable 2FA
    current_user.two_factor_enabled = True
    current_user.two_factor_secret = current_user.two_factor_secret  # Keep the secret
    
    # Audit log
    audit = AuditLog(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        action="2fa_enabled",
        entity_type="user",
        entity_id=current_user.id,
        new_values={"method": "TOTP"}
    )
    db.add(audit)
    await db.commit()
    
    return {"message": "2FA enabled successfully"}


@router.post("/disable")
async def disable_2fa(
    request: TwoFactorDisableRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Disable 2FA for the current user"""
    if not current_user.two_factor_enabled:
        raise HTTPException(
            status_code=400,
            detail="2FA is not enabled"
        )
    
    # Verify password first (simplified - in production use proper auth)
    # For now, accept backup code or TOTP code
    totp = pyotp.TOTP(current_user.two_factor_secret) if current_user.two_factor_secret else None
    
    valid = False
    if totp and totp.verify(request.code):
        valid = True
    elif request.code in (current_user.two_factor_backup_codes or []):
        valid = True
    
    if not valid:
        raise HTTPException(
            status_code=400,
            detail="Invalid code"
        )
    
    # Disable 2FA
    current_user.two_factor_enabled = False
    current_user.two_factor_secret = None
    current_user.two_factor_backup_codes = None
    
    # Audit log
    audit = AuditLog(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        action="2fa_disabled",
        entity_type="user",
        entity_id=current_user.id,
        new_values={}
    )
    db.add(audit)
    await db.commit()
    
    return {"message": "2FA disabled successfully"}


@router.get("/status")
async def get_2fa_status(
    current_user: User = Depends(get_current_user)
):
    """Get 2FA status for current user"""
    return {
        "enabled": current_user.two_factor_enabled,
        "has_backup_codes": bool(current_user.two_factor_backup_codes)
    }
