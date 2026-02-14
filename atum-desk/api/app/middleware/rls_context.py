"""
ATUM DESK - RLS Context Middleware
Automatically sets org context for authenticated requests
Includes degraded mode enforcement for operator-safe control
"""
import logging
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.db.session import set_org_context, set_user_context, set_role_context
from app.config import get_settings

logger = logging.getLogger(__name__)


class RLSContextMiddleware(BaseHTTPMiddleware):
    """Middleware to inject RLS org context from authenticated user"""
    
    EXEMPT_PATHS = {
        "/api/v1/health",
        "/metrics",
        "/health",
        "/api/docs",
        "/api/redoc",
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/internal/rls",
    }
    
    async def dispatch(self, request: Request, call_next):
        settings = get_settings()
        
        # Skip for exempt paths
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)
        
        # Skip for internal/admin endpoints that handle their own RLS
        if request.url.path.startswith("/api/v1/admin/rls"):
            return await call_next(request)
        
        # Get org_id from request state (set by auth dependency)
        org_id = getattr(request.state, "organization_id", None)
        user_id = getattr(request.state, "user_id", None)
        role = getattr(request.state, "role", None)
        
        # RLS Safety Alarm: Log warning if no org context on tenant path
        if not org_id and request.url.path.startswith("/api/v1/"):
            logger.warning(
                "rls_context_missing",
                path=request.url.path,
                method=request.method,
                user_agent=request.headers.get("user-agent", "unknown")
            )
        
        # Check degraded mode - block requests without org context
        if settings.RLS_DEGRADED_MODE:
            if not org_id:
                try:
                    from app.routers.metrics import org_context_missing_total
                    org_context_missing_total.labels(endpoint=request.url.path).inc()
                except Exception:
                    pass
                
                return JSONResponse(
                    status_code=403,
                    content={
                        "error": "ORG_CONTEXT_MISSING",
                        "message": "Organization context required - RLS degraded mode active",
                        "detail": "Request blocked because RLS degraded and no organization context was provided"
                    }
                )
        
        # Set context for this request
        if org_id:
            set_org_context(str(org_id))
        if user_id:
            set_user_context(str(user_id))
        if role:
            set_role_context(str(role))
        
        response = await call_next(request)
        
        # Clear context after request
        set_org_context(None)
        set_user_context(None)
        set_role_context(None)
        
        return response
