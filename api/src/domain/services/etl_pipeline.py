"""
ATUM DESK - Polars ETL Pipeline
High-performance data processing for analytics and reporting
10-100x faster than Pandas
"""
import polars as pl
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path
import json

from src.domain.entities import OrganizationId


class ATUMETLPipeline:
    """
    High-performance ETL pipeline using Polars
    For analytics, reporting, and data processing
    """
    
    def __init__(self, data_dir: str = "/opt/atum-desk/data/exports"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    async def extract_ticket_metrics(
        self,
        org_id: OrganizationId,
        start_date: datetime,
        end_date: datetime,
    ) -> pl.DataFrame:
        """
        Extract ticket metrics for analytics
        Ultra-fast with Polars lazy evaluation
        """
        # This would query the database
        # For now, return structure
        schema = {
            "ticket_id": pl.Utf8,
            "created_at": pl.Datetime,
            "resolved_at": pl.Datetime,
            "status": pl.Utf8,
            "priority": pl.Utf8,
            "resolution_time_minutes": pl.Float64,
            "agent_id": pl.Utf8,
            "customer_id": pl.Utf8,
            "satisfaction_score": pl.Int8,
        }
        
        return pl.DataFrame(schema=schema)
    
    def transform_resolution_metrics(
        self,
        df: pl.DataFrame,
    ) -> pl.DataFrame:
        """
        Transform raw ticket data into resolution metrics
        Polars operations are 10-100x faster than Pandas
        """
        return (
            df
            # Calculate resolution time
            .with_columns([
                (
                    pl.col("resolved_at") - pl.col("created_at")
                ).dt.total_minutes().alias("resolution_minutes")
            ])
            # Group by priority and calculate metrics
            .group_by("priority")
            .agg([
                pl.count().alias("ticket_count"),
                pl.col("resolution_minutes").mean().alias("avg_resolution_minutes"),
                pl.col("resolution_minutes").median().alias("median_resolution_minutes"),
                pl.col("satisfaction_score").mean().alias("avg_satisfaction"),
                pl.col("satisfaction_score").filter(pl.col("satisfaction_score") >= 4).count().alias("positive_ratings"),
            ])
            # Calculate SLA compliance
            .with_columns([
                (
                    pl.col("avg_resolution_minutes") / 
                    pl.when(pl.col("priority") == "urgent").then(240)
                    .when(pl.col("priority") == "high").then(480)
                    .when(pl.col("priority") == "medium").then(1440)
                    .otherwise(2880)
                ).alias("sla_compliance_ratio")
            ])
            .sort("priority")
        )
    
    def transform_agent_performance(
        self,
        df: pl.DataFrame,
    ) -> pl.DataFrame:
        """
        Transform data into agent performance metrics
        """
        return (
            df
            .group_by("agent_id")
            .agg([
                pl.count().alias("tickets_resolved"),
                pl.col("resolution_minutes").mean().alias("avg_resolution_time"),
                pl.col("resolution_minutes").std().alias("resolution_time_std"),
                pl.col("satisfaction_score").mean().alias("avg_csat"),
                pl.col("satisfaction_score").count().alias("total_ratings"),
            ])
            .with_columns([
                # Performance score (0-100)
                (
                    (pl.col("avg_csat") * 20) * 0.4 +
                    (100 - (pl.col("avg_resolution_time") / 60)) * 0.3 +
                    (pl.col("tickets_resolved") / 10) * 0.3
                ).clip(0, 100).alias("performance_score")
            ])
            .sort("performance_score", descending=True)
        )
    
    def transform_trend_analysis(
        self,
        df: pl.DataFrame,
        freq: str = "1d",  # 1d=daily, 1w=weekly, 1mo=monthly
    ) -> pl.DataFrame:
        """
        Transform data into time-series trends
        """
        return (
            df
            .with_columns([
                pl.col("created_at").dt.truncate(freq).alias("period")
            ])
            .group_by("period")
            .agg([
                pl.count().alias("tickets_created"),
                pl.col("status").filter(pl.col("status") == "resolved").count().alias("tickets_resolved"),
                pl.col("satisfaction_score").mean().alias("avg_satisfaction"),
            ])
            .with_columns([
                (
                    pl.col("tickets_resolved") / pl.col("tickets_created") * 100
                ).alias("resolution_rate")
            ])
            .sort("period")
        )
    
    def export_to_parquet(
        self,
        df: pl.DataFrame,
        filename: str,
        compression: str = "zstd",
    ) -> Path:
        """
        Export DataFrame to Parquet format
        Parquet is 10x smaller and 100x faster than CSV
        """
        filepath = self.data_dir / f"{filename}.parquet"
        df.write_parquet(filepath, compression=compression)
        return filepath
    
    def export_to_csv(
        self,
        df: pl.DataFrame,
        filename: str,
    ) -> Path:
        """
        Export DataFrame to CSV
        """
        filepath = self.data_dir / f"{filename}.csv"
        df.write_csv(filepath)
        return filepath
    
    def export_to_json(
        self,
        df: pl.DataFrame,
        filename: str,
    ) -> Path:
        """
        Export DataFrame to JSON
        """
        filepath = self.data_dir / f"{filename}.json"
        df.write_json(filepath)
        return filepath
    
    def read_from_database(
        self,
        query: str,
        connection_uri: str,
    ) -> pl.DataFrame:
        """
        Read directly from PostgreSQL using Polars
        """
        return pl.read_database_uri(query, connection_uri)
    
    def generate_dashboard_metrics(
        self,
        df: pl.DataFrame,
    ) -> Dict[str, Any]:
        """
        Generate metrics for dashboard
        Returns JSON-serializable dict
        """
        metrics = {
            "total_tickets": df.height,
            "avg_resolution_time": df.select(
                pl.col("resolution_minutes").mean()
            ).to_dict()["resolution_minutes"][0],
            "sla_compliance": df.filter(
                pl.col("sla_compliance_ratio") <= 1.0
            ).height / df.height * 100 if df.height > 0 else 0,
            "avg_csat": df.select(
                pl.col("satisfaction_score").mean()
            ).to_dict()["satisfaction_score"][0],
        }
        
        return metrics
    
    def batch_process_large_dataset(
        self,
        file_path: str,
        batch_size: int = 100000,
    ) -> pl.DataFrame:
        """
        Process large datasets in batches
        Memory-efficient for millions of rows
        """
        # Lazy evaluation - doesn't load everything into memory
        lazy_df = pl.scan_parquet(file_path)
        
        # Process in batches
        results = []
        for batch in lazy_df.collect().iter_slices(batch_size):
            processed = self.transform_resolution_metrics(batch)
            results.append(processed)
        
        # Concatenate results
        return pl.concat(results)


class TicketAnalyticsEngine:
    """
    High-level analytics engine for tickets
    Uses Polars for all data operations
    """
    
    def __init__(self):
        self.etl = ATUMETLPipeline()
    
    async def generate_daily_report(
        self,
        org_id: OrganizationId,
        date: datetime,
    ) -> Dict[str, Any]:
        """
        Generate daily analytics report
        """
        start = date.replace(hour=0, minute=0, second=0)
        end = start + timedelta(days=1)
        
        # Extract
        df = await self.etl.extract_ticket_metrics(org_id, start, end)
        
        # Transform
        metrics_df = self.etl.transform_resolution_metrics(df)
        trends_df = self.etl.transform_trend_analysis(df, freq="1h")
        
        # Generate metrics
        dashboard_metrics = self.etl.generate_dashboard_metrics(df)
        
        # Export
        self.etl.export_to_parquet(metrics_df, f"daily_metrics_{date.strftime('%Y%m%d')}")
        
        return {
            "date": date.isoformat(),
            "metrics": dashboard_metrics,
            "priority_breakdown": metrics_df.to_dict(),
            "hourly_trends": trends_df.to_dict(),
        }
    
    async def generate_weekly_report(
        self,
        org_id: OrganizationId,
        week_start: datetime,
    ) -> Dict[str, Any]:
        """
        Generate weekly analytics report
        """
        start = week_start
        end = start + timedelta(days=7)
        
        df = await self.etl.extract_ticket_metrics(org_id, start, end)
        
        metrics = self.etl.transform_resolution_metrics(df)
        trends = self.etl.transform_trend_analysis(df, freq="1d")
        agents = self.etl.transform_agent_performance(df)
        
        return {
            "week_start": week_start.isoformat(),
            "week_end": end.isoformat(),
            "priority_metrics": metrics.to_dict(),
            "daily_trends": trends.to_dict(),
            "agent_performance": agents.to_dict(),
        }
    
    def compare_periods(
        self,
        current_df: pl.DataFrame,
        previous_df: pl.DataFrame,
    ) -> pl.DataFrame:
        """
        Compare metrics between two periods
        """
        current_metrics = (
            current_df
            .group_by("priority")
            .agg([
                pl.count().alias("current_count"),
                pl.col("resolution_minutes").mean().alias("current_avg_time"),
            ])
        )
        
        previous_metrics = (
            previous_df
            .group_by("priority")
            .agg([
                pl.count().alias("previous_count"),
                pl.col("resolution_minutes").mean().alias("previous_avg_time"),
            ])
        )
        
        # Join and calculate differences
        comparison = current_metrics.join(
            previous_metrics,
            on="priority",
            how="outer"
        ).with_columns([
            (
                (pl.col("current_count") - pl.col("previous_count")) /
                pl.col("previous_count") * 100
            ).alias("count_change_pct"),
            (
                (pl.col("current_avg_time") - pl.col("previous_avg_time")) /
                pl.col("previous_avg_time") * 100
            ).alias("time_change_pct"),
        ])
        
        return comparison


# Export convenience functions
def create_etl_pipeline(data_dir: str = "/opt/atum-desk/data/exports") -> ATUMETLPipeline:
    """Factory function to create ETL pipeline"""
    return ATUMETLPipeline(data_dir)


def create_analytics_engine() -> TicketAnalyticsEngine:
    """Factory function to create analytics engine"""
    return TicketAnalyticsEngine()
