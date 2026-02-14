"""
ATUM DESK - Authentication Router
"""
from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from app.db.session import get_session
from app.auth.jwt import verify_password, create_access_token, create_refresh_token, decode_token
from app.auth.deps import get_current_user
from app.models.user import User
from sqlalchemy import select

router = APIRouter()
# oath2_scheme moved to deps but needed for tokenUrl? No, creates circular import?
# No, deps imports oauth2_scheme inside.
# Wait, auth router uses OAuth2PasswordRequestForm which is fine.



class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    organization_id: str





@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_session)
):
    """Authenticate user and return JWT tokens"""
    # Extract client IP
    client_ip = request.headers.get("X-Real-IP") or request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
    if not client_ip:
        client_ip = request.client.host if request.client else None
    
    from app.services.security.login_attempt import check_login_allowed, record_failed_login, record_successful_login_db
    
    # Check login lockout first
    if client_ip:
        allowed, error = await check_login_allowed(db, client_ip)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=error
            )
    
    # Find user by email
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        if client_ip:
            await record_failed_login(db, client_ip, username=form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )
    
    # Record successful login
    if client_ip:
        await record_successful_login_db(db, client_ip)
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    from app.config import get_settings
    settings = get_settings()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_session)):
    """Refresh access token using refresh token"""
    payload = decode_token(refresh_token)
    
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    
    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    # Create new tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    from app.config import get_settings
    settings = get_settings()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role.value,
        organization_id=str(current_user.organization_id)
    )


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    organization_id: Optional[str] = None


class RegisterResponse(BaseModel):
    message: str
    user_id: str
    requires_verification: bool


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_session)
):
    """Register a new user account"""
    from app.services.security.password_policy import validate_password
    from app.services.security.email_verification import create_verification_token
    from app.auth.jwt import get_password_hash
    from app.models.organization import Organization
    from app.models.user import UserRole
    from sqlalchemy import text
    
    # Validate password
    is_valid, error = validate_password(request.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    # Check if email exists
    result = await db.execute(
        text("SELECT id FROM users WHERE email = :email"),
        {"email": request.email}
    )
    if result.fetchone():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Get or create organization
    org_id = request.organization_id
    if not org_id:
        # Check if default org exists first
        result = await db.execute(text("SELECT id FROM organizations WHERE slug = 'default' LIMIT 1"))
        org_row = result.fetchone()
        if org_row:
            org_id = str(org_row.id)
        else:
            # Create default organization
            result = await db.execute(
                text("""
                    INSERT INTO organizations (id, name, slug, settings, is_active, created_at, updated_at)
                    VALUES (gen_random_uuid(), :name, :slug, '{}'::json, true, NOW(), NOW())
                    RETURNING id
                """),
                {"name": "Default Organization", "slug": "default"}
            )
            org_id = str(result.fetchone().id)
    
    # Create user (inactive until verified)
    user_id_result = await db.execute(
        text("""
            INSERT INTO users (id, email, password_hash, full_name, role, organization_id, is_active, email_verified, is_email_verified, two_factor_enabled, created_at, updated_at)
            VALUES (gen_random_uuid(), :email, :password_hash, :full_name, :role, :org_id, false, false, false, false, NOW(), NOW())
            RETURNING id
        """),
        {
            "email": request.email,
            "password_hash": get_password_hash(request.password),
            "full_name": request.full_name,
            "role": "CUSTOMER_USER",
            "org_id": org_id
        }
    )
    user_id = str(user_id_result.fetchone().id)
    
    # Create verification token
    token = await create_verification_token(db, user_id)
    
    return RegisterResponse(
        message="Registration successful. Please check your email to verify your account.",
        user_id=user_id,
        requires_verification=True
    )


@router.get("/verify-email")
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_session)
):
    """Verify email address with token"""
    from app.services.security.email_verification import verify_email_token
    
    success, error = await verify_email_token(db, token)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return {"message": "Email verified successfully. You can now log in."}


@router.post("/resend-verification")
async def resend_verification(
    email: str,
    db: AsyncSession = Depends(get_session)
):
    """Resend verification email"""
    from app.services.security.email_verification import create_verification_token
    from sqlalchemy import text
    
    result = await db.execute(
        text("SELECT id, is_email_verified FROM users WHERE email = :email"),
        {"email": email}
    )
    user = result.fetchone()
    
    if not user:
        return {"message": "If the email exists, a verification link has been sent."}
    
    if user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    await create_verification_token(db, str(user.id))
    
    return {"message": "Verification email sent. Please check your inbox."}


@router.post("/forgot-password")
async def forgot_password(
    email: str,
    db: AsyncSession = Depends(get_session)
):
    """Request password reset"""
    from sqlalchemy import text
    from datetime import datetime, timedelta, timezone
    from uuid import uuid4
    import hashlib
    
    # Find user by email
    result = await db.execute(
        text("SELECT id, email FROM users WHERE LOWER(email) = LOWER(:email)"),
        {"email": email}
    )
    row = result.fetchone()
    
    if not row:
        # Don't reveal if user exists
        return {"message": "If the email exists, a reset link has been sent"}
    
    user_id = str(row[0])
    
    # Generate reset token
    token = str(uuid4())
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
    
    # Store token
    await db.execute(
        text("""
            INSERT INTO password_reset_tokens (id, user_id, token_hash, expires_at, created_at)
            VALUES (:id, :user_id, :token_hash, :expires_at, :now)
        """),
        {
            "id": str(uuid4()),
            "user_id": user_id,
            "token_hash": token_hash,
            "expires_at": expires_at,
            "now": datetime.now(timezone.utc)
        }
    )
    await db.commit()
    
    # In production, send email with reset link
    # For now, return token in dev mode
    return {
        "message": "If the email exists, a reset link has been sent",
        "dev_token": token  # Remove in production
    }


@router.post("/reset-password")
async def reset_password(
    token: str,
    new_password: str,
    db: AsyncSession = Depends(get_session)
):
    """Reset password with token"""
    import hashlib
    from sqlalchemy import text
    from datetime import datetime, timezone
    from app.auth.jwt import get_password_hash
    
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    # Find valid token
    result = await db.execute(
        text("""
            SELECT id, user_id, expires_at, used 
            FROM password_reset_tokens 
            WHERE token_hash = :hash AND used = false AND expires_at > NOW()
        """),
        {"hash": token_hash}
    )
    row = result.fetchone()
    
    if not row:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    token_id, user_id, expires_at, used = row
    
    # Update password
    password_hash = get_password_hash(new_password)
    
    await db.execute(
        text("UPDATE users SET password_hash = :hash, updated_at = :now WHERE id = :user_id"),
        {"hash": password_hash, "now": datetime.now(timezone.utc), "user_id": user_id}
    )
    
    # Mark token as used
    await db.execute(
        text("UPDATE password_reset_tokens SET used = true WHERE id = :id"),
        {"id": str(token_id)}
    )
    await db.commit()
    
    return {"message": "Password reset successful"}
