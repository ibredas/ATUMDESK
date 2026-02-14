"""
ATUM DESK - Polars ETL Script
Transforms exported data for DuckDB analytics
"""
import os
import sys
from datetime import datetime
import json

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import structlog

logger = structlog.get_logger("analytics_etl")

EXPORT_DIR = os.getenv("EXPORT_DIR", "/data/ATUM DESK/atum-desk/data/analytics/exports")


def transform_tickets(df):
    """Transform tickets data"""
    import polars as pl
    
    return df.with_columns([
        pl.col("created_at").str.to_datetime("%Y-%m-%dT%H:%M:%S%.f"),
        pl.col("updated_at").str.to_datetime("%Y-%m-%dT%H:%M:%S%.f"),
    ]).with_columns([
        pl.col("status").cast(pl.Categorical),
        pl.col("priority").cast(pl.Categorical),
    ])


def transform_metrics(df):
    """Transform metrics snapshots"""
    import polars as pl
    
    return df.with_columns([
        pl.col("snapshot_ts").str.to_datetime("%Y-%m-%dT%H:%M:%S%.f"),
    ])


def transform_ai_suggestions(df):
    """Transform AI suggestions"""
    import polars as pl
    
    return df.with_columns([
        pl.col("created_at").str.to_datetime("%Y-%m-%dT%H:%M:%S%.f"),
    ]).with_columns([
        pl.col("suggestion_type").cast(pl.Categorical),
    ])


def run_etl():
    """Run ETL transformations"""
    try:
        import polars as pl
    except ImportError:
        logger.warning("polars_not_available")
        return {"status": "skipped", "reason": "polars not installed"}
    
    results = {}
    
    # Process tickets
    tickets_file = os.path.join(EXPORT_DIR, "tickets_latest.parquet")
    if os.path.exists(tickets_file):
        df = pl.read_parquet(tickets_file)
        df_transformed = transform_tickets(df)
        output_file = os.path.join(EXPORT_DIR, "tickets_transformed.parquet")
        df_transformed.write_parquet(output_file)
        results["tickets"] = {"rows": len(df), "output": output_file}
    
    # Process metrics
    metrics_file = os.path.join(EXPORT_DIR, "metrics_latest.parquet")
    if os.path.exists(metrics_file):
        df = pl.read_parquet(metrics_file)
        df_transformed = transform_metrics(df)
        output_file = os.path.join(EXPORT_DIR, "metrics_transformed.parquet")
        df_transformed.write_parquet(output_file)
        results["metrics"] = {"rows": len(df), "output": output_file}
    
    # Process AI suggestions
    ai_file = os.path.join(EXPORT_DIR, "ai_suggestions_latest.parquet")
    if os.path.exists(ai_file):
        df = pl.read_parquet(ai_file)
        df_transformed = transform_ai_suggestions(df)
        output_file = os.path.join(EXPORT_DIR, "ai_suggestions_transformed.parquet")
        df_transformed.write_parquet(output_file)
        results["ai_suggestions"] = {"rows": len(df), "output": output_file}
    
    logger.info("etl_completed", results=results)
    return results


if __name__ == "__main__":
    import asyncio
    result = run_etl()
    print(json.dumps(result, indent=2))
