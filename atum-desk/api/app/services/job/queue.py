"""
ATUM DESK - Job Queue Service
Non-blocking job enqueue for ticket workflows
"""
from uuid import uuid4
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import json

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class JobQueueService:
    """Service to enqueue jobs without blocking the request path"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def enqueue(
        self,
        job_type: str,
        organization_id: str,
        payload: Dict[str, Any],
        priority: str = "medium",
        run_after: Optional[datetime] = None,
    ) -> str:
        """
        Enqueue a job for async processing
        
        Args:
            job_type: TRIAGE_TICKET, KB_SUGGEST, SMART_REPLY, SLA_PREDICT, METRICS_SNAPSHOT
            organization_id: Tenant ID for isolation
            payload: Job payload (ticket_id, etc.)
            priority: low, medium, high, urgent
            run_after: Optional delay before running
            
        Returns:
            job_id
        """
        job_id = str(uuid4())
        
        query = """
            INSERT INTO job_queue (
                id, organization_id, job_type, payload, status,
                priority, run_after, created_at, updated_at
            ) VALUES (
                :id, :org_id, :job_type, :payload, 'PENDING',
                :priority, :run_after, :now, :now
            )
        """
        
        await self.db.execute(
            text(query),
            {
                "id": job_id,
                "org_id": organization_id,
                "job_type": job_type,
                "payload": json.dumps(payload),
                "priority": priority,
                "run_after": run_after,
                "now": datetime.now(timezone.utc),
            }
        )
        await self.db.commit()
        
        return job_id
    
    async def enqueue_ticket_triage(
        self,
        ticket_id: str,
        organization_id: str,
    ) -> str:
        """Enqueue AI triage for a ticket"""
        return await self.enqueue(
            job_type="TRIAGE_TICKET",
            organization_id=organization_id,
            payload={"ticket_id": ticket_id},
            priority="medium",
        )
    
    async def enqueue_kb_suggest(
        self,
        ticket_id: str,
        organization_id: str,
    ) -> str:
        """Enqueue KB suggestions for a ticket"""
        return await self.enqueue(
            job_type="KB_SUGGEST",
            organization_id=organization_id,
            payload={"ticket_id": ticket_id},
            priority="low",
        )
    
    async def enqueue_smart_reply(
        self,
        ticket_id: str,
        organization_id: str,
    ) -> str:
        """Enqueue smart reply generation for a ticket"""
        return await self.enqueue(
            job_type="SMART_REPLY",
            organization_id=organization_id,
            payload={"ticket_id": ticket_id},
            priority="medium",
        )
    
    async def enqueue_sla_predict(
        self,
        ticket_id: str,
        organization_id: str,
    ) -> str:
        """Enqueue SLA prediction for a ticket"""
        return await self.enqueue(
            job_type="SLA_PREDICT",
            organization_id=organization_id,
            payload={"ticket_id": ticket_id},
            priority="low",
        )
    
    async def enqueue_sentiment_analysis(
        self,
        ticket_id: str,
        organization_id: str,
    ) -> str:
        """Enqueue sentiment analysis for a ticket"""
        return await self.enqueue(
            job_type="SENTIMENT_ANALYSIS",
            organization_id=organization_id,
            payload={"ticket_id": ticket_id},
            priority="high",  # Higher priority for escalation detection
        )


async def get_job_queue_service(db: AsyncSession) -> JobQueueService:
    """Factory function"""
    return JobQueueService(db)
