"""
ATUM DESK - Analytics Export Script
Exports Postgres data to Parquet for DuckDB analytics
"""
import os
import sys
from datetime import datetime, timezone
import json
import asyncio

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import structlog
from sqlalchemy import create_engine, text

logger = structlog.get_logger("analytics_export")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/atum_desk")
EXPORT_DIR = os.getenv("EXPORT_DIR", "/data/ATUM DESK/atum-desk/data/analytics/exports")


async def export_tickets():
    """Export tickets to Parquet"""
    try:
        import pandas as pd
        
        engine = create_engine(DATABASE_URL)
        query = """
            SELECT 
                id, organization_id, subject, description, status, priority,
                category, assigned_to, created_at, updated_at, resolved_at, closed_at,
                sla_breached, time_to_breach_minutes, sla_risk_score
            FROM tickets
            WHERE created_at > NOW() - INTERVAL '30 days'
        """
        df = pd.read_sql(query, engine)
        
        filepath = os.path.join(EXPORT_DIR, f"tickets_{datetime.now().strftime('%Y%m%d')}.parquet")
        df.to_parquet(filepath, index=False)
        
        logger.info("tickets_exported", filepath=filepath, rows=len(df))
        return filepath
        
    except ImportError:
        logger.warning("pandas_not_available")
        return None
    except Exception as e:
        logger.error("export_failed", error=str(e))
        return None


async def export_metrics_snapshots():
    """Export metrics snapshots to Parquet"""
    try:
        import pandas as pd
        
        engine = create_engine(DATABASE_URL)
        query = """
            SELECT 
                organization_id, snapshot_ts, tickets_by_status, tickets_by_priority,
                frt_p50, frt_p95, mttr_p50, mttr_p95, sla_compliance_pct
            FROM metrics_snapshots
            WHERE snapshot_ts > NOW() - INTERVAL '30 days'
        """
        df = pd.read_sql(query, engine)
        
        filepath = os.path.join(EXPORT_DIR, f"metrics_{datetime.now().strftime('%Y%m%d')}.parquet")
        df.to_parquet(filepath, index=False)
        
        logger.info("metrics_exported", filepath=filepath, rows=len(df))
        return filepath
        
    except Exception as e:
        logger.error("export_failed", error=str(e))
        return None


async def export_ai_suggestions():
    """Export AI suggestions to Parquet"""
    try:
        import pandas as pd
        
        engine = create_engine(DATABASE_URL)
        query = """
            SELECT 
                organization_id, ticket_id, suggestion_type, content,
                confidence, is_used, created_at
            FROM ai_suggestions
            WHERE created_at > NOW() - INTERVAL '30 days'
        """
        df = pd.read_sql(query, engine)
        
        filepath = os.path.join(EXPORT_DIR, f"ai_suggestions_{datetime.now().strftime('%Y%m%d')}.parquet")
        df.to_parquet(filepath, index=False)
        
        logger.info("ai_suggestions_exported", filepath=filepath, rows=len(df))
        return filepath
        
    except Exception as e:
        logger.error("export_failed", error=str(e))
        return None


async def run_export():
    """Run all exports"""
    os.makedirs(EXPORT_DIR, exist_ok=True)
    
    logger.info("export_started", export_dir=EXPORT_DIR)
    
    results = {
        "tickets": await export_tickets(),
        "metrics": await export_metrics_snapshots(),
        "ai_suggestions": await export_ai_suggestions(),
    }
    
    logger.info("export_completed", results=results)
    return results


if __name__ == "__main__":
    asyncio.run(run_export())
