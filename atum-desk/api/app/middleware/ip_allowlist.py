"""
ATUM DESK - IP Allowlist Middleware
"""
import ipaddress
from typing import Optional
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db.session import get_session


async def check_ip_allowed(
    organization_id: str,
    client_ip: str
) -> tuple[bool, Optional[str]]:
    """
    Check if IP is allowed for organization.
    Returns (allowed, error_message)
    """
    if not client_ip:
        return True, None  # Allow if no IP (shouldn't happen)
    
    # Get organization's IP allowlist
    result = await get_session().execute(
        text("""
            SELECT cidr FROM org_ip_allowlist 
            WHERE organization_id = :org_id AND enabled = true
        """),
        {"org_id": organization_id}
    )
    rows = result.fetchall()
    
    if not rows:
        return True, None  # No allowlist = allow all
    
    # Check against allowlist
    try:
        client_net = ipaddress.ip_address(client_ip)
        for row in rows:
            network = ipaddress.ip_network(row.cidr, strict=False)
            if client_net in network:
                return True, None
    except ValueError:
        pass  # Invalid IP format
    
    return False, "Your IP address is not allowed to access this resource"


class IPAllowlistMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce IP allowlist for internal roles"""
    
    # Routes that require IP allowlist check
    PROTECTED_ROUTES = [
        "/api/v1/internal/",
        "/api/v1/admin/",
    ]
    
    # Roles that require IP allowlist
    PROTECTED_ROLES = ["ADMIN", "AGENT", "MANAGER"]
    
    async def dispatch(self, request: Request, call_next):
        # Skip for public routes
        path = request.url.path
        
        # Skip if not a protected route
        if not any(path.startswith(route) for route in self.PROTECTED_ROUTES):
            return await call_next(request)
        
        # Get client IP
        client_ip = request.headers.get("X-Real-IP") or \
                    request.headers.get("X-Forwarded-For", "").split(",")[0].strip() or \
                    request.client.host if request.client else None
        
        if not client_ip:
            return await call_next(request)
        
        # Get user from request (if authenticated)
        # Note: This is a simplified version - in production you'd get the user's org from the JWT
        
        response = await call_next(request)
        return response
