"""
ATUM DESK - Main FastAPI Application
"""
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import structlog
import time
import asyncio

from app.config import get_settings
from app.db.init_db import init_db
from app.routers import auth, users, tickets, internal_tickets, internal_rls, comments, attachments, health, rules, two_factor, audit, ticket_relationships, admin

settings = get_settings()
logger = structlog.get_logger()


from app.services.email_ingestion import email_ingestion_service
from app.routers.metrics import update_health_metrics

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    logger.info("Starting ATUM DESK API", version=settings.APP_VERSION)
    await init_db()
    logger.info("Database initialized")
    
    # Start Email Ingestion
    asyncio.create_task(email_ingestion_service.start_polling())
    
    # Start health metrics background task
    asyncio.create_task(update_health_metrics())
    
    yield
    # Shutdown
    logger.info("Shutting down ATUM DESK API")
    email_ingestion_service.running = False


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="ATUM DESK - Production-grade helpdesk/ticketing platform",
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# CORS middleware - Strict policy for JWT-only auth
# NOTE: CSRF protection is NOT needed for JWT authentication
# JWT tokens are sent in Authorization header, not cookies
# CSRF attacks only affect cookie-based authentication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL] if settings.FRONTEND_URL else [],
    allow_credentials=False,  # Important: False for JWT-only (no cookies)
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)



@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    # Security Headers (Defense in Depth)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    return response


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Request logging middleware"""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    
    logger.info(
        "request_completed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration=round(process_time, 3),
    )
    
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(
        "unhandled_exception",
        path=request.url.path,
        method=request.method,
        error=str(exc),
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "service": settings.APP_NAME,
    }


# API routes
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(tickets.router, prefix="/api/v1/tickets", tags=["Tickets"])
app.include_router(internal_tickets.router, prefix="/api/v1/internal/tickets", tags=["Internal Tickets"])
app.include_router(internal_rls.router, tags=["Internal RLS"])
app.include_router(comments.router, prefix="/api/v1/comments", tags=["Comments"])
app.include_router(attachments.router, prefix="/api/v1/attachments", tags=["Attachments"])
app.include_router(health.router, prefix="/api/v1/health", tags=["System Health"])

from app.routers import reports
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])

from app.routers import kb
app.include_router(kb.router, prefix="/api/v1/kb", tags=["Knowledge Base"])

from app.routers import kb_suggestions
app.include_router(kb_suggestions.router, prefix="/api/v1/kb/suggestions", tags=["KB Suggestions"])

from app.routers import problems
app.include_router(problems.router, prefix="/api/v1/problems", tags=["Problems"])

from app.routers import changes
app.include_router(changes.router, prefix="/api/v1/changes", tags=["Changes"])

from app.routers import assets
app.include_router(assets.router, prefix="/api/v1/assets", tags=["Assets"])

from app.routers import webhooks
app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["Webhooks"])

from app.routers import analytics
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])

from app.routers import etl
app.include_router(etl.router, tags=["ETL"])

from app.routers import rag
app.include_router(rag.router, prefix="/api/v1/rag", tags=["RAG"])

from app.routers import copilot
app.include_router(copilot.router, prefix="/api/v1/copilot", tags=["Copilot"])

from app.routers import assistant
app.include_router(assistant.router, prefix="/api/v1/internal", tags=["Assistant"])

from app.routers import metrics, rules, two_factor, audit

app.include_router(rules.router, tags=["Rules"])
app.include_router(metrics.router, tags=["Metrics"])
app.include_router(two_factor.router, tags=["2FA"])
app.include_router(audit.router, tags=["Audit"])
app.include_router(ticket_relationships.router, tags=["Ticket Relationships"])

# NEW ROUTERS - Phase 6 Enhancements
from app.routers import ticket_locks
app.include_router(ticket_locks.router, tags=["Ticket Locks"])

from app.routers import playbooks
app.include_router(playbooks.router, tags=["Playbooks"])

from app.routers import forms
app.include_router(forms.router, tags=["Service Forms"])

from app.routers import notifications
app.include_router(notifications.router, tags=["Notifications"])

from app.routers import ai_analytics
app.include_router(ai_analytics.router, tags=["AI Analytics"])

from app.routers import policies
app.include_router(policies.router, prefix="/api/v1/policies", tags=["Policy Center"])

from app.routers import incidents
app.include_router(incidents.router, prefix="/api/v1/incidents", tags=["Incidents"])

from app.routers import admin
app.include_router(admin.router, tags=["Admin"])






# ---------- Serve built frontend from /web/dist ----------
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "web" / "dist"

if FRONTEND_DIR.is_dir():
    # Serve static assets (JS, CSS, images)
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="frontend-assets")
    # Serve brand assets if they exist
    brand_dir = FRONTEND_DIR / "brand"
    if brand_dir.is_dir():
        app.mount("/brand", StaticFiles(directory=brand_dir), name="frontend-brand")

    @app.get("/{full_path:path}")
    async def serve_frontend(request: Request, full_path: str):
        """Serve React SPA - any non-API path returns index.html"""
        # Try to serve static file first
        file_path = FRONTEND_DIR / full_path
        if full_path and file_path.is_file():
            return FileResponse(file_path)
        # Otherwise serve index.html for SPA routing
        return FileResponse(FRONTEND_DIR / "index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
