#!/usr/bin/env python3
"""
ATUM DESK - Metrics Snapshot Worker
Captures metrics snapshots for live dashboard
"""
import os
import asyncio
import logging
import json
from datetime import datetime, timezone
from uuid import uuid4
from typing import Dict, Any, Optional

import structlog
import psycopg
from psycopg import AsyncConnection

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger("metrics_snapshot_worker")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://atum:atum@localhost:5432/atum_desk")
SNAPSHOT_INTERVAL = int(os.getenv("SNAPSHOT_INTERVAL", "30"))


class MetricsSnapshotWorker:
    def __init__(self):
        self.conn: Optional[AsyncConnection] = None
        self.running = True
    
    async def connect(self):
        self.conn = await AsyncConnection.connect(DATABASE_URL, autocommit=False)
        logger.info("connected_to_database")
    
    async def close(self):
        if self.conn:
            await self.conn.close()
    
    async def capture_snapshot(self, org_id: str) -> bool:
        try:
            async with self.conn.cursor() as cur:
                await cur.execute("""
                    SELECT 
                        status,
                        priority,
                        COUNT(*) as count
                    FROM tickets 
                    WHERE organization_id = %s
                    GROUP BY status, priority
                """, (org_id,))
                
                rows = await cur.fetchall()
                
                tickets_by_status = {}
                tickets_by_priority = {}
                
                for row in rows:
                    status, priority, count = row
                    tickets_by_status[status] = tickets_by_status.get(status, 0) + count
                    tickets_by_priority[priority] = tickets_by_priority.get(priority, 0) + count
                
                await cur.execute("""
                    SELECT 
                        COUNT(*) FILTER (WHERE status = 'closed') as closed,
                        COUNT(*) FILTER (WHERE sla_breached = true) as breached,
                        COUNT(*) as total
                    FROM tickets 
                    WHERE organization_id = %s
                """, (org_id,))
                
                row = await cur.fetchone()
                closed, breached, total = row[0], row[1], row[2]
                sla_compliance_pct = ((total - breached) / total * 100) if total > 0 else 100.0
                
                await cur.execute("""
                    SELECT 
                        PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (closed_at - created_at))),
                        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (closed_at - created_at)))
                    FROM tickets 
                    WHERE organization_id = %s AND status = 'closed' AND closed_at IS NOT NULL
                """, (org_id,))
                
                row = await cur.fetchone()
                frt_p50 = row[0] / 60 if row[0] else None
                frt_p95 = row[1] / 60 if row[1] else None
                
                snapshot_id = str(uuid4())
                await cur.execute("""
                    INSERT INTO metrics_snapshots (
                        id, organization_id, snapshot_ts,
                        tickets_by_status, tickets_by_priority,
                        frt_p50, frt_p95, mttr_p50, mttr_p95,
                        sla_compliance_pct, agent_load, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    snapshot_id, org_id, datetime.now(timezone.utc),
                    json.dumps(tickets_by_status), json.dumps(tickets_by_priority),
                    frt_p50, frt_p95, frt_p50, frt_p95,
                    sla_compliance_pct, json.dumps({}),
                    datetime.now(timezone.utc)
                ))
                
                await self.conn.commit()
                logger.info("snapshot_captured", org_id=org_id, ticket_count=total)
                return True
                
        except Exception as e:
            logger.error("snapshot_failed", org_id=org_id, error=str(e))
            return False
    
    async def run(self):
        await self.connect()
        
        while self.running:
            try:
                async with self.conn.cursor() as cur:
                    await cur.execute("SELECT id FROM organizations")
                    orgs = await cur.fetchall()
                
                for org in orgs:
                    await self.capture_snapshot(str(org[0]))
                
                await asyncio.sleep(SNAPSHOT_INTERVAL)
                
            except Exception as e:
                logger.error("worker_error", error=str(e))
                await asyncio.sleep(5)
        
        await self.close()


async def main():
    worker = MetricsSnapshotWorker()
    try:
        await worker.run()
    except KeyboardInterrupt:
        worker.running = False
        await worker.close()


if __name__ == "__main__":
    asyncio.run(main())
