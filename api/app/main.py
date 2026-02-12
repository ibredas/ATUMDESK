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
from app.routers import auth, users, tickets, internal_tickets, comments, attachments, health

settings = get_settings()
logger = structlog.get_logger()


from app.services.email_ingestion import email_ingestion_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    logger.info("Starting ATUM DESK API", version=settings.APP_VERSION)
    await init_db()
    logger.info("Database initialized")
    
    # Start Email Ingestion
    asyncio.create_task(email_ingestion_service.start_polling())
    
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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL] if settings.FRONTEND_URL else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
app.include_router(comments.router, prefix="/api/v1/comments", tags=["Comments"])
app.include_router(attachments.router, prefix="/api/v1/attachments", tags=["Attachments"])
app.include_router(health.router, prefix="/api/v1/health", tags=["System Health"])

from app.routers import webhooks
app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["Webhooks"])

from app.routers import analytics
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])

from app.routers import rag
app.include_router(rag.router, prefix="/api/v1/rag", tags=["RAG"])

from app.routers import assistant
app.include_router(assistant.router, prefix="/api/v1/internal", tags=["Assistant"])






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
