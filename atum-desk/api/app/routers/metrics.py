"""
ATUM DESK - Prometheus Metrics Endpoint
Tier-2 monitoring with low overhead
"""
import asyncio
from contextlib import asynccontextmanager
from fastapi import APIRouter, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

from app.config import get_settings

router = APIRouter(tags=["Metrics"])
_settings = get_settings()

# Define metrics (LOW cardinality - no tenant/user/ticket IDs)

# HTTP metrics
http_requests_total = Counter(
    'atum_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration = Histogram(
    'atum_http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

# Error metrics
errors_total = Counter(
    'atum_errors_total',
    'Total errors',
    ['error_type', 'endpoint']
)

# Job queue metrics
job_queue_depth = Gauge(
    'atum_job_queue_depth',
    'Job queue depth by type and status',
    ['job_type', 'status']
)

# RAG queue metrics
rag_queue_depth = Gauge(
    'atum_rag_queue_depth',
    'RAG index queue depth',
    ['status']
)

# Worker metrics
worker_job_total = Counter(
    'atum_worker_job_total',
    'Total jobs processed by worker',
    ['worker_name', 'job_type', 'status']
)

# Database metrics
db_pool_connections = Gauge(
    'atum_db_pool_connections',
    'Database connection pool',
    ['state']
)

db_up = Gauge(
    'atum_db_up',
    'Database availability (1=up, 0=down)'
)

# Ollama metrics
ollama_up = Gauge(
    'atum_ollama_up',
    'Ollama availability (1=up, 0=down)'
)

ollama_inference_duration = Histogram(
    'atum_ollama_inference_seconds',
    'Ollama inference duration',
    ['model']
)

# RLS Guardrail metrics
org_context_missing_total = Counter(
    'atum_org_context_missing_total',
    'Total requests missing org context',
    ['endpoint']
)

rls_denied_total = Counter(
    'atum_rls_denied_total',
    'RLS policy denials',
    ['table']
)

rls_emergency_actions_total = Counter(
    'atum_rls_emergency_actions_total',
    'Emergency RLS actions',
    ['action', 'actor']
)


# Health check background task
async def update_health_metrics():
    """Background task to update health metrics"""
    import httpx
    from sqlalchemy import text
    from app.db.base import engine
    
    while True:
        try:
            # Check database
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
                db_up.set(1)
        except Exception:
            db_up.set(0)
        
        try:
            # Check Ollama
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{_settings.OLLAMA_URL}/api/tags")
                if response.status_code == 200:
                    ollama_up.set(1)
                else:
                    ollama_up.set(0)
        except Exception:
            ollama_up.set(0)
        
        # Update queue depths
        try:
            async with engine.connect() as conn:
                # Job queue
                result = await conn.execute(
                    text("SELECT status, COUNT(*) FROM job_queue GROUP BY status")
                )
                for row in result:
                    job_queue_depth.labels(job_type='all', status=row[0]).set(row[1])
                
                # RAG queue (optional table)
                try:
                    result = await conn.execute(
                        text("SELECT status, COUNT(*) FROM rag_index_queue GROUP BY status")
                    )
                    for row in result:
                        rag_queue_depth.labels(status=row[0]).set(row[1])
                except Exception:
                    pass
        except Exception:
            pass
        
        await asyncio.sleep(30)  # Update every 30 seconds


@router.get("/metrics", response_class=Response)
async def metrics():
    """
    Prometheus metrics endpoint
    Returns all registered metrics in Prometheus format
    """
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


@router.get("/api/v1/metrics", response_class=Response)
async def api_metrics():
    """
    Prometheus metrics endpoint (API prefix)
    """
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


@router.get("/api/v1/metrics/dashboard")
async def dashboard_widgets():
    """
    Dashboard widgets data - SLA, AI utilization, RAG health
    """
    from sqlalchemy import text
    from app.db.base import engine
    
    result = {
        "sla_alerts": {"75_percent": 0, "90_percent": 0, "breached": 0},
        "ai_utilization": {"triage_generated": 0, "triage_applied": 0, "reply_generated": 0, "reply_used": 0},
        "rag_health": {"queue_backlog": 0, "last_index_time": None},
        "agent_load": {}
    }
    
    async with engine.connect() as conn:
        # SLA alerts
        try:
            r = await conn.execute(text("""
                SELECT 
                    COUNT(*) FILTER (WHERE sla_breached = true) as breached,
                    0 as at90,
                    0 as at75
                FROM tickets WHERE sla_policy_id IS NOT NULL
            """))
            row = r.fetchone()
            if row:
                result["sla_alerts"]["breached"] = row[0] or 0
        except Exception:
            pass
        
        # AI utilization
        try:
            r = await conn.execute(text("SELECT COUNT(*) FROM ticket_ai_triage"))
            row = r.fetchone()
            result["ai_utilization"]["triage_generated"] = row[0] if row else 0
            
            r = await conn.execute(text("SELECT COUNT(*) FROM ai_suggestions WHERE suggestion_type = 'smart_reply'"))
            row = r.fetchone()
            result["ai_utilization"]["reply_generated"] = row[0] if row else 0
        except Exception:
            pass
        
        # RAG health
        try:
            r = await conn.execute(text("SELECT COUNT(*) FROM rag_index_queue WHERE status = 'PENDING'"))
            row = r.fetchone()
            result["rag_health"]["queue_backlog"] = row[0] if row else 0
        except Exception:
            pass
    
    return result


@router.get("/api/v1/metrics/live")
async def metrics_live():
    """
    Live metrics snapshot — real-time job queue, DB health, and agent load.
    Gap 10: /metrics/live endpoint.
    """
    from sqlalchemy import text
    from app.db.base import engine
    
    result = {
        "timestamp": None,
        "job_queue": {},
        "db_healthy": False,
        "agent_load": {}
    }
    
    import datetime
    result["timestamp"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    async with engine.connect() as conn:
        try:
            await conn.execute(text("SELECT 1"))
            result["db_healthy"] = True
        except Exception:
            pass
        
        # Job queue status
        try:
            r = await conn.execute(text(
                "SELECT job_type, status, COUNT(*) FROM job_queue GROUP BY job_type, status ORDER BY 1, 2"
            ))
            for row in r:
                jtype = row[0]
                if jtype not in result["job_queue"]:
                    result["job_queue"][jtype] = {}
                result["job_queue"][jtype][row[1]] = row[2]
        except Exception:
            pass
        
        # Agent load
        try:
            r = await conn.execute(text("""
                SELECT u.id, u.full_name, COUNT(t.id) as open_tickets
                FROM users u
                LEFT JOIN tickets t ON t.assigned_to = u.id AND t.status NOT IN ('resolved', 'closed')
                WHERE u.role IN ('agent', 'admin')
                GROUP BY u.id, u.full_name
                ORDER BY open_tickets DESC LIMIT 20
            """))
            for row in r:
                result["agent_load"][str(row[0])] = {
                    "name": row[1],
                    "open_tickets": row[2]
                }
        except Exception:
            pass
    
    return result


@router.get("/api/v1/metrics/history")
async def metrics_history(range: str = "24h"):
    """
    Historical metrics snapshots.
    Gap 10: /metrics/history endpoint.
    Args:
        range: Time range — 1h, 6h, 24h, 7d, 30d
    """
    from sqlalchemy import text
    from app.db.base import engine
    
    interval_map = {
        "1h": "1 hour",
        "6h": "6 hours",
        "24h": "24 hours",
        "7d": "7 days",
        "30d": "30 days"
    }
    interval = interval_map.get(range, "24 hours")
    
    snapshots = []
    async with engine.connect() as conn:
        try:
            r = await conn.execute(text(f"""
                SELECT id, organization_id, snapshot_ts,
                       tickets_by_status, tickets_by_priority,
                       frt_p50, frt_p95, mttr_p50, mttr_p95,
                       sla_compliance_pct, agent_load
                FROM metrics_snapshots
                WHERE snapshot_ts >= NOW() - INTERVAL '{interval}'
                ORDER BY snapshot_ts DESC
                LIMIT 500
            """))
            for row in r:
                snapshots.append({
                    "id": str(row[0]),
                    "organization_id": str(row[1]) if row[1] else None,
                    "snapshot_ts": row[2].isoformat() if row[2] else None,
                    "tickets_by_status": row[3],
                    "tickets_by_priority": row[4],
                    "frt_p50": row[5],
                    "frt_p95": row[6],
                    "mttr_p50": row[7],
                    "mttr_p95": row[8],
                    "sla_compliance_pct": row[9],
                    "agent_load": row[10]
                })
        except Exception:
            pass
    
    return {"items": snapshots, "range": range, "count": len(snapshots)}
