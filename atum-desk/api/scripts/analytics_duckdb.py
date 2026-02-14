"""
ATUM DESK - DuckDB Analytics Queries
Fast analytics without impacting Postgres
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import structlog

logger = structlog.get_logger("duckdb_analytics")

DUCKDB_PATH = os.getenv("DUCKDB_PATH", "/data/ATUM DESK/atum-desk/data/analytics/atum_analytics.duckdb")
EXPORT_DIR = os.getenv("EXPORT_DIR", "/data/ATUM DESK/atum-desk/data/analytics/exports")


def get_duckdb_connection():
    """Get DuckDB connection"""
    import duckdb
    return duckdb.connect(DUCKDB_PATH)


def ensure_tables():
    """Create tables in DuckDB from Parquet files"""
    conn = get_duckdb_connection()
    
    # Tickets table
    tickets_file = os.path.join(EXPORT_DIR, "tickets_transformed.parquet")
    if os.path.exists(tickets_file):
        conn.execute("CREATE TABLE IF NOT EXISTS tickets AS SELECT * FROM parquet_file(?);", [tickets_file])
    
    # Metrics table
    metrics_file = os.path.join(EXPORT_DIR, "metrics_transformed.parquet")
    if os.path.exists(metrics_file):
        conn.execute("CREATE TABLE IF NOT EXISTS metrics AS SELECT * FROM parquet_file(?);", [metrics_file])
    
    # AI suggestions table
    ai_file = os.path.join(EXPORT_DIR, "ai_suggestions_transformed.parquet")
    if os.path.exists(ai_file):
        conn.execute("CREATE TABLE IF NOT EXISTS ai_suggestions AS SELECT * FROM parquet_file(?);", [ai_file])
    
    conn.close()
    logger.info("duckdb_tables_created")


def query_tickets_by_status():
    """Query tickets by status"""
    conn = get_duckdb_connection()
    result = conn.execute("""
        SELECT status, COUNT(*) as count 
        FROM tickets 
        GROUP BY status 
        ORDER BY count DESC
    """).fetchall()
    conn.close()
    return [{"status": r[0], "count": r[1]} for r in result]


def query_tickets_by_priority():
    """Query tickets by priority"""
    conn = get_duckdb_connection()
    result = conn.execute("""
        SELECT priority, COUNT(*) as count 
        FROM tickets 
        GROUP BY priority 
        ORDER BY count DESC
    """).fetchall()
    conn.close()
    return [{"priority": r[0], "count": r[1]} for r in result]


def query_sla_compliance():
    """Query SLA compliance"""
    conn = get_duckdb_connection()
    result = conn.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE sla_breached = true) as breached,
            ROUND(COUNT(*) FILTER (WHERE sla_breached = false) * 100.0 / NULLIF(COUNT(*), 0), 2) as compliance_pct
        FROM tickets
    """).fetchone()
    conn.close()
    return {
        "total": result[0],
        "breached": result[1],
        "compliance_pct": result[2]
    }


def query_ai_utilization():
    """Query AI feature utilization"""
    conn = get_duckdb_connection()
    result = conn.execute("""
        SELECT 
            suggestion_type,
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE is_used = true) as used,
            ROUND(COUNT(*) FILTER (WHERE is_used = true) * 100.0 / NULLIF(COUNT(*), 0), 2) as usage_rate
        FROM ai_suggestions
        GROUP BY suggestion_type
    """).fetchall()
    conn.close()
    return [{
        "type": r[0], 
        "total": r[1], 
        "used": r[2], 
        "usage_rate": r[3]
    } for r in result]


def query_metrics_trend():
    """Query metrics trend over time"""
    conn = get_duckdb_connection()
    result = conn.execute("""
        SELECT 
            date_trunc('day', snapshot_ts) as day,
            AVG(sla_compliance_pct) as avg_compliance,
            AVG(frt_p50) as avg_frt_p50,
            AVG(mttr_p50) as avg_mttr_p50
        FROM metrics
        GROUP BY day
        ORDER BY day DESC
        LIMIT 30
    """).fetchall()
    conn.close()
    return [{
        "day": str(r[0]), 
        "avg_compliance": r[1], 
        "avg_frt_p50": r[2],
        "avg_mttr_p50": r[3]
    } for r in result]


def refresh():
    """Refresh all DuckDB tables from Parquet"""
    ensure_tables()
    return {
        "tickets_by_status": query_tickets_by_status(),
        "tickets_by_priority": query_tickets_by_priority(),
        "sla_compliance": query_sla_compliance(),
        "ai_utilization": query_ai_utilization(),
        "metrics_trend": query_metrics_trend()
    }


if __name__ == "__main__":
    result = refresh()
    import json
    print(json.dumps(result, indent=2, default=str))
