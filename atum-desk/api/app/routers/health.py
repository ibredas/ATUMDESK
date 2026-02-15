"""
ATUM DESK - Health Check Router
"""
import shutil
import time
from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db.session import get_session
from app.config import get_settings

router = APIRouter()
settings = get_settings()

@router.get("", response_model=Dict[str, Any])
async def health_check(
    db: AsyncSession = Depends(get_session)
):
    """
    Check system health:
    - Database connectivity
    
    - Disk space
    """
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.APP_VERSION,
        "components": {}
    }
    
    # 1. Database Check
    try:
        start_time = time.time()
        await db.execute(text("SELECT 1"))
        db_latency = round((time.time() - start_time) * 1000, 2)
        health_status["components"]["database"] = {
            "status": "connected",
            "latency_ms": db_latency
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["components"]["database"] = {
            "status": "disconnected",
            "error": str(e)
        }
        
    # 2. Disk Space Check (Upload Directory)
    try:
        total, used, free = shutil.disk_usage(settings.UPLOAD_DIR)
        free_gb = round(free / (2**30), 2)
        health_status["components"]["disk"] = {
            "status": "ok",
            "free_gb": free_gb
        }
        if free_gb < 1:  # Warning if less than 1GB
            health_status["components"]["disk"]["warning"] = "Low disk space"
    except Exception as e:
        health_status["components"]["disk"] = {
            "status": "error",
            "error": str(e)
        }
        
    return health_status
