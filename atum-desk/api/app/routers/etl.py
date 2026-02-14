"""
ATUM DESK - ETL Analytics Router
High-performance analytics using Polars
"""
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from uuid import UUID

import polars as pl
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text

from app.db.session import get_session
from app.auth.deps import get_current_user
from app.models.user import User
from app.config import get_settings

router = APIRouter(prefix="/api/v1/etl", tags=["ETL"])
_settings = get_settings()


def ticket_to_polars(tickets: List[Dict]) -> pl.DataFrame:
    """Convert ticket data to Polars DataFrame"""
    if not tickets:
        return pl.DataFrame({
            "ticket_id": pl.Utf8,
            "created_at": pl.Datetime,
            "resolved_at": pl.Datetime,
            "status": pl.Utf8,
            "priority": pl.Utf8,
            "resolution_time_minutes": pl.Float64,
            "agent_id": pl.Utf8,
            "customer_id": pl.Utf8,
        })
    
    return pl.DataFrame(tickets)


@router.get("/metrics/resolution")
async def get_resolution_metrics(
    days: int = Query(default=30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """
    Get resolution metrics using Polars for high-performance analytics
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = text("""
        SELECT 
            t.id as ticket_id,
            t.created_at,
            t.resolved_at,
            t.status,
            t.priority,
            t.assigned_to as agent_id,
            t.requester_id as customer_id,
            EXTRACT(EPOCH FROM (COALESCE(t.resolved_at, NOW()) - t.created_at)) / 60 as resolution_time_minutes
        FROM tickets t
        WHERE t.organization_id = :org_id
        AND t.created_at >= :start_date
    """)
    
    result = await db.execute(
        query, 
        {"org_id": str(current_user.organization_id), "start_date": start_date}
    )
    rows = result.fetchall()
    
    tickets = [
        {
            "ticket_id": str(r.ticket_id),
            "created_at": r.created_at,
            "resolved_at": r.resolved_at,
            "status": r.status,
            "priority": r.priority,
            "resolution_time_minutes": float(r.resolution_time_minutes) if r.resolution_time_minutes else 0,
            "agent_id": str(r.agent_id) if r.agent_id else None,
            "customer_id": str(r.customer_id) if r.customer_id else None,
        }
        for r in rows
    ]
    
    df = ticket_to_polars(tickets)
    
    if df.is_empty():
        return {
            "period_days": days,
            "total_tickets": 0,
            "metrics_by_priority": [],
            "avg_resolution_time": 0,
            "sla_compliance": 0,
        }
    
    metrics = (
        df
        .group_by("priority")
        .agg([
            pl.count().alias("ticket_count"),
            pl.col("resolution_time_minutes").mean().alias("avg_resolution_minutes"),
            pl.col("resolution_time_minutes").median().alias("median_resolution_minutes"),
            pl.col("resolution_time_minutes").min().alias("min_resolution_minutes"),
            pl.col("resolution_time_minutes").max().alias("max_resolution_minutes"),
        ])
        .sort("priority")
    )
    
    sla_targets = {"urgent": 240, "high": 480, "medium": 1440, "low": 2880}
    metrics_list = metrics.to_dicts()
    
    for m in metrics_list:
        m["sla_target_minutes"] = sla_targets.get(m.get("priority", ""), 2880)
        m["sla_usage_pct"] = round(m["avg_resolution_minutes"] / m["sla_target_minutes"] * 100, 2) if m["avg_resolution_minutes"] else 0
    
    avg_resolution = df.select(pl.col("resolution_time_minutes").mean()).item()
    
    return {
        "period_days": days,
        "total_tickets": len(tickets),
        "metrics_by_priority": metrics_list,
        "avg_resolution_time": round(avg_resolution, 2) if avg_resolution else 0,
    }


@router.get("/metrics/trends")
async def get_trend_analysis(
    days: int = Query(default=30, ge=7, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """
    Get ticket trends over time using Polars
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = text("""
        SELECT 
            CAST(t.created_at AS DATE) as date,
            COUNT(*) as tickets_created
        FROM tickets t
        WHERE t.organization_id = :org_id
        AND t.created_at >= :start_date
        GROUP BY CAST(t.created_at AS DATE)
        ORDER BY date
    """)
    
    result = await db.execute(
        query,
        {"org_id": str(current_user.organization_id), "start_date": start_date}
    )
    rows = result.fetchall()
    
    trends = [
        {
            "date": str(r.date) if r.date else None,
            "tickets_created": r.tickets_created,
        }
        for r in rows
    ]
    
    if not trends:
        return {"period_days": days, "trends": []}
    
    return {
        "period_days": days,
        "trends": trends,
    }


@router.get("/metrics/agents")
async def get_agent_performance(
    days: int = Query(default=30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """
    Get agent performance metrics using Polars
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = text("""
        SELECT 
            t.assigned_to as agent_id,
            COUNT(*) as tickets_assigned
        FROM tickets t
        WHERE t.organization_id = :org_id
        AND t.assigned_to IS NOT NULL
        AND t.created_at >= :start_date
        GROUP BY t.assigned_to
        ORDER BY tickets_assigned DESC
    """)
    
    result = await db.execute(
        query,
        {"org_id": str(current_user.organization_id), "start_date": start_date}
    )
    rows = result.fetchall()
    
    agents = [
        {
            "agent_id": str(r.agent_id),
            "tickets_assigned": r.tickets_assigned,
        }
        for r in rows
    ]
    
    return {
        "period_days": days,
        "agents": agents,
    }


@router.get("/export/parquet")
async def export_parquet(
    days: int = Query(default=30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """
    Export ticket data as Parquet file using Polars
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = text("""
        SELECT 
            t.id as ticket_id,
            t.subject,
            t.description,
            t.status,
            t.priority,
            t.created_at,
            t.resolved_at,
            t.updated_at,
            t.assigned_to as agent_id,
            t.requester_id as customer_id
        FROM tickets t
        WHERE t.organization_id = :org_id
        AND t.created_at >= :start_date
        ORDER BY t.created_at DESC
    """)
    
    result = await db.execute(
        query,
        {"org_id": str(current_user.organization_id), "start_date": start_date}
    )
    rows = result.fetchall()
    
    tickets = [
        {
            "ticket_id": str(r.ticket_id),
            "subject": r.subject,
            "description": r.description,
            "status": r.status,
            "priority": r.priority,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "resolved_at": r.resolved_at.isoformat() if r.resolved_at else None,
            "updated_at": r.updated_at.isoformat() if r.updated_at else None,
            "agent_id": str(r.agent_id) if r.agent_id else None,
            "customer_id": str(r.customer_id) if r.customer_id else None,
        }
        for r in rows
    ]
    
    if not tickets:
        return {"error": "No tickets found", "count": 0}
    
    df = pl.DataFrame(tickets)
    
    try:
        export_dir = Path(_settings.DATA_DIR) / "exports"
        export_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        export_dir = Path(__file__).parent.parent / "data" / "exports"
        export_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"tickets_{current_user.organization_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.parquet"
    filepath = export_dir / filename
    df.write_parquet(filepath)
    
    return {
        "filename": filename,
        "path": str(filepath),
        "record_count": len(tickets),
        "file_size_bytes": filepath.stat().st_size,
    }


@router.get("/health")
async def etl_health():
    """ETL service health check"""
    return {
        "status": "healthy",
        "engine": "polars",
        "version": pl.__version__,
    }
