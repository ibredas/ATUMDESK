#!/usr/bin/env python3
"""
ATUM DESK - Job Worker
PostgreSQL-backed job queue processor
Long-running worker with exponential backoff
"""
import os
import sys
import asyncio
import logging
import time
import json
from datetime import datetime, timezone
from uuid import uuid4
from typing import Optional, Dict, Any

import structlog
import psycopg
from psycopg import AsyncConnection

# Configure logging
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

logger = structlog.get_logger("job_worker")

# Configuration
_raw_db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/atum_desk")
# Normalize SQLAlchemy-style URLs (e.g. postgresql+asyncpg://) to raw psycopg format
DATABASE_URL = _raw_db_url.replace("postgresql+asyncpg://", "postgresql://").replace("postgresql+psycopg://", "postgresql://")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "ATUM-DESK-COPILOT:latest")

# Job types
JOB_TYPES = {
    "TRIAGE_TICKET": "handle_triage_ticket",
    "KB_SUGGEST": "handle_kb_suggest",
    "SMART_REPLY": "handle_smart_reply",
    "SLA_PREDICT": "handle_sla_predict",
    "METRICS_SNAPSHOT": "handle_metrics_snapshot",
    "SENTIMENT_ANALYSIS": "handle_sentiment_analysis",
    "CLEANUP_LOGS": "handle_cleanup_logs",
}

# Retry configuration
MAX_RETRIES = 3
BASE_BACKOFF = 5  # seconds



class JobWorker:
    def __init__(self, worker_id: str = None):
        self.worker_id = worker_id or str(uuid4())
        self.running = True
        self.conn: Optional[AsyncConnection] = None
    
    async def connect(self):
        """Connect to database"""
        self.conn = await AsyncConnection.connect(DATABASE_URL, autocommit=False)
        logger.info("connected_to_database", worker_id=self.worker_id)
    
    async def set_org_context(self, org_id: str):
        """Set RLS org context for this connection"""
        if org_id:
            await self.conn.execute(f"SET LOCAL app.current_org = '{org_id}'")
            logger.debug("org_context_set", org_id=org_id)
    
    async def clear_org_context(self):
        """Clear RLS org context"""
        await self.conn.execute("SET LOCAL app.current_org = NULL")
    
    async def close(self):
        """Close database connection"""
        if self.conn:
            await self.conn.close()
            logger.info("database_connection_closed")
    
    async def claim_job(self) -> Optional[Dict[str, Any]]:
        """Claim a pending job using SELECT FOR UPDATE SKIP LOCKED"""
        now = datetime.now(timezone.utc)
        
        query = """
            UPDATE job_queue
            SET status = 'RUNNING',
                locked_by = %s::uuid,
                locked_at = %s,
                updated_at = %s
            WHERE id = (
                SELECT id FROM job_queue
                WHERE status = 'PENDING'
                AND (run_after IS NULL OR run_after <= %s)
                ORDER BY 
                    CASE priority 
                        WHEN 'urgent' THEN 1 
                        WHEN 'high' THEN 2 
                        WHEN 'medium' THEN 3 
                        ELSE 4 
                    END,
                    created_at
                LIMIT 1
                FOR UPDATE SKIP LOCKED
            )
            RETURNING id, organization_id, job_type, payload
        """
        
        async with self.conn.cursor() as cur:
            await cur.execute(
                query, 
                (self.worker_id, now, now, now)
            )
            row = await cur.fetchone()
            
            if row:
                await self.conn.commit()
                return {
                    "id": str(row[0]),
                    "organization_id": str(row[1]) if row[1] else None,
                    "job_type": row[2],
                    "payload": row[3] if row[3] else {}
                }
            return None
    
    async def complete_job(self, job_id: str, success: bool = True, error: str = None):
        """Mark job as complete or failed"""
        status = 'DONE' if success else 'FAILED'
        
        query = """
            UPDATE job_queue
            SET status = %s,
                last_error = %s,
                updated_at = %s
            WHERE id = %s::uuid
        """
        
        async with self.conn.cursor() as cur:
            await cur.execute(query, (status, error, datetime.now(timezone.utc), job_id))
            await self.conn.commit()
        
        # Log event
        await self.log_event(job_id, "completed" if success else "failed", {"error": error})
    
    async def log_event(self, job_id: str, event: str, details: Dict = None):
        """Log job event"""
        query = """
            INSERT INTO job_events (id, job_id, event, details, created_at)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        async with self.conn.cursor() as cur:
            await cur.execute(
                query, 
                (str(uuid4()), job_id, event, json.dumps(details) if details else None, datetime.now(timezone.utc))
            )
            await self.conn.commit()

    async def audit_log_write(self, org_id: str, action: str, entity_type: str,
                               entity_id: str, new_values: Dict = None, user_id: str = None):
        """Gap 14: Write audit log entry from worker"""
        query = """
            INSERT INTO audit_log (id, organization_id, user_id, action, entity_type, entity_id, new_values, created_at)
            VALUES (%s, %s::uuid, %s, %s, %s, %s::uuid, %s, %s)
        """
        try:
            async with self.conn.cursor() as cur:
                await cur.execute(query, (
                    str(uuid4()), org_id, user_id, action, entity_type, entity_id,
                    json.dumps(new_values) if new_values else None,
                    datetime.now(timezone.utc)
                ))
                await self.conn.commit()
        except Exception as e:
            logger.warning("audit_log_write_failed", error=str(e), action=action)

    
    async def handle_triage_ticket(self, job: Dict[str, Any]) -> bool:
        """AI triage job handler - categorize and prioritize ticket"""
        payload = job.get("payload", {})
        ticket_id = payload.get("ticket_id")
        org_id = job.get("organization_id")
        
        if not ticket_id:
            await self.complete_job(job["id"], False, "Missing ticket_id")
            return False
        
        logger.info("processing_triage_job", ticket_id=ticket_id, org_id=org_id)
        
        try:
            # Simulate AI Triage (replace with actual LLM call in production)
            await asyncio.sleep(1) 
            
            triage_result = {
                "category": "technical",
                "priority": "medium",
                "tags": ["auto-triaged", "needs-review"],
                "confidence": 0.85
            }
            
            # Store result
            insert_query = """
                INSERT INTO ticket_ai_triage 
                (id, organization_id, ticket_id, suggested_category, suggested_priority, suggested_tags, created_at)
                VALUES (%s, %s::uuid, %s::uuid, %s, %s, %s, %s)
            """
            
            async with self.conn.cursor() as cur:
                await cur.execute(insert_query, (
                    str(uuid4()), org_id, ticket_id, 
                    triage_result["category"], triage_result["priority"], 
                    json.dumps(triage_result["tags"]), datetime.now(timezone.utc)
                ))
                await self.conn.commit()
            
            # Gap 14: Audit Log
            await self.audit_log_write(
                org_id=org_id,
                action="ai_triage_generated",
                entity_type="ticket",
                entity_id=ticket_id,
                new_values=triage_result
            )

            await self.complete_job(job["id"], True)
            return True
            
        except Exception as e:
            logger.error("triage_job_failed", error=str(e))
            await self.complete_job(job["id"], False, str(e))
            return False

    async def handle_cleanup_logs(self, job: Dict[str, Any]) -> bool:
        """Gap 17: Cleanup old logs based on retention policy"""
        org_id = job.get("organization_id")
        retention_days = 365 
        
        if org_id:
             async with self.conn.cursor() as cur:
                await cur.execute("SELECT audit_retention_days FROM org_settings WHERE organization_id = %s::uuid", (org_id,))
                row = await cur.fetchone()
                if row and row[0]:
                    retention_days = row[0]

        logger.info("running_cleanup", org_id=org_id, retention_days=retention_days)
        cutoff = f"NOW() - INTERVAL '{retention_days} days'"
        
        async with self.conn.cursor() as cur:
            # Cleanup audit logs
            q1 = f"DELETE FROM audit_log WHERE created_at < {cutoff}"
            if org_id: q1 += f" AND organization_id = '{org_id}'"
            await cur.execute(q1)
            audit_deleted = cur.rowcount
            
            # Cleanup job queue
            q2 = f"DELETE FROM job_queue WHERE status IN ('DONE', 'FAILED') AND updated_at < {cutoff}"
            if org_id: q2 += f" AND organization_id = '{org_id}'"
            await cur.execute(q2)
            jobs_deleted = cur.rowcount
            
            await self.conn.commit()
            
        logger.info("cleanup_completed", audit_deleted=audit_deleted, jobs_deleted=jobs_deleted)
        await self.complete_job(job["id"], True)
        return True
        
        # Get ticket details
        query = """
            SELECT subject, description, priority, status 
            FROM tickets 
            WHERE id = %s::uuid
        """
        
        async with self.conn.cursor() as cur:
            await cur.execute(query, (ticket_id,))
            row = await cur.fetchone()
            
            if not row:
                await self.complete_job(job["id"], False, "Ticket not found")
                return False
            
            subject, description, current_priority, status = row[0], row[1], row[2], row[3]
        
        # Call Ollama for triage analysis
        prompt = f"""Analyze this support ticket and provide triage recommendations.

Subject: {subject}
Description: {description}

Respond with JSON:
{{
  "suggested_category": "TECHNICAL|BILLING|ACCOUNT|INQUIRY|SECURITY|INFRA",
  "suggested_priority": "low|medium|high|urgent",
  "sentiment_label": "positive|neutral|negative",
  "sentiment_score": 0.0-1.0,
  "intent_label": "request|question|problem|compliment",
  "intent_score": 0.0-1.0,
  "confidence": 0.0-1.0,
  "summary": "2-3 sentence summary"
}}
"""
        
        try:
            import httpx
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{OLLAMA_URL}/api/generate",
                    json={
                        "model": OLLAMA_MODEL,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"num_predict": 300}
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    response_text = result.get("response", "")
                    
                    # Parse JSON from response
                    import re
                    json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
                    if json_match:
                        triage_data = json.loads(json_match.group())
                    else:
                        triage_data = {
                            "suggested_category": "INQUIRY",
                            "suggested_priority": "medium",
                            "sentiment_label": "neutral",
                            "sentiment_score": 0.5,
                            "confidence": 0.5
                        }
                else:
                    triage_data = {
                        "suggested_category": "INQUIRY",
                        "suggested_priority": "medium",
                        "sentiment_label": "neutral",
                        "sentiment_score": 0.5,
                        "confidence": 0.3
                    }
        except Exception as e:
            logger.warning("ollama_triage_failed", error=str(e))
            triage_data = {
                "suggested_category": "INQUIRY",
                "suggested_priority": "medium",
                "sentiment_label": "neutral",
                "sentiment_score": 0.5,
                "confidence": 0.3
            }
        
        # Store triage result
        triage_id = str(uuid4())
        query = """
            INSERT INTO ticket_ai_triage (
                id, organization_id, ticket_id, suggested_category, suggested_priority,
                sentiment_label, sentiment_score, intent_label, intent_score,
                confidence, model_id, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        async with self.conn.cursor() as cur:
            await cur.execute(query, (
                triage_id, org_id, ticket_id,
                triage_data.get("suggested_category", "INQUIRY"),
                triage_data.get("suggested_priority", "medium"),
                triage_data.get("sentiment_label", "neutral"),
                triage_data.get("sentiment_score", 0.5),
                triage_data.get("intent_label", "request"),
                triage_data.get("intent_score", 0.5),
                triage_data.get("confidence", 0.5),
                OLLAMA_MODEL,
                datetime.now(timezone.utc)
            ))
            await self.conn.commit()
        
        # Gap 14: Audit Log
        await self.audit_log_write(
            org_id=org_id,
            action="ai_triage_generated",
            entity_type="ticket",
            entity_id=ticket_id,
            new_values={
                "category": triage_data.get("suggested_category"),
                "priority": triage_data.get("suggested_priority"),
                "sentiment": triage_data.get("sentiment_label"),
                "confidence": triage_data.get("confidence")
            }
        )

        await self.complete_job(job["id"], True)
        logger.info("triage_completed", ticket_id=ticket_id, triage_id=triage_id)
        return True
    
    async def handle_kb_suggest(self, job: Dict[str, Any]) -> bool:
        """KB suggestion job handler - find related articles"""
        payload = job.get("payload", {})
        ticket_id = payload.get("ticket_id")
        org_id = job.get("organization_id")
        
        if not ticket_id:
            await self.complete_job(job["id"], False, "Missing ticket_id")
            return False
        
        logger.info("processing_kb_suggest_job", ticket_id=ticket_id)
        
        # Get ticket details
        query = "SELECT subject, description FROM tickets WHERE id = %s::uuid"
        
        async with self.conn.cursor() as cur:
            await cur.execute(query, (ticket_id,))
            row = await cur.fetchone()
            
            if not row:
                await self.complete_job(job["id"], False, "Ticket not found")
                return False
            
            subject, description = row[0], row[1]
        
        # Search KB via RAG (reuse existing RAG retriever)
        try:
            from app.services.rag.retriever import RAGRetriever
            from app.services.rag.store import RAGStore
            from sqlalchemy.ext.asyncio import create_async_engine
            
            engine = create_async_engine(DATABASE_URL.replace("postgresql+psycopg", "postgresql+asyncpg"))
            
            async with engine.begin() as conn:
                store = RAGStore(conn)
                retriever = RAGRetriever(store)
                
                results = await retriever.search(
                    organization_id=org_id,
                    query=f"{subject} {description[:500]}",
                    user_role="agent",
                    top_k=3,
                    graph_depth=2
                )
            
            # Store KB suggestions
            for kb_result in results.get("results", []):
                suggestion_id = str(uuid4())
                query = """
                    INSERT INTO ticket_kb_suggestions (
                        id, organization_id, ticket_id, article_id, title,
                        excerpt, relevance_score, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                async with self.conn.cursor() as cur:
                    await cur.execute(query, (
                        suggestion_id, org_id, ticket_id,
                        kb_result.get("id", str(uuid4())),
                        kb_result.get("title", "Unknown"),
                        kb_result.get("content", "")[:200],
                        kb_result.get("score", 0.5),
                        datetime.now(timezone.utc)
                    ))
            await self.conn.commit()
            
        except Exception as e:
            logger.warning("kb_suggest_failed", error=str(e))
        
        await self.complete_job(job["id"], True)
        logger.info("kb_suggest_completed", ticket_id=ticket_id)
        return True
    
    async def handle_smart_reply(self, job: Dict[str, Any]) -> bool:
        """Smart reply generation job handler"""
        payload = job.get("payload", {})
        ticket_id = payload.get("ticket_id")
        org_id = job.get("organization_id")
        
        if not ticket_id:
            await self.complete_job(job["id"], False, "Missing ticket_id")
            return False
        
        logger.info("processing_smart_reply_job", ticket_id=ticket_id)
        
        # Get ticket details
        query = "SELECT subject, description FROM tickets WHERE id = %s::uuid"
        
        async with self.conn.cursor() as cur:
            await cur.execute(query, (ticket_id,))
            row = await cur.fetchone()
            
            if not row:
                await self.complete_job(job["id"], False, "Ticket not found")
                return False
            
            subject, description = row[0], row[1]
        
        # Generate smart reply via Ollama
        prompt = f"""Generate a professional customer service reply for this ticket.

Subject: {subject}
Description: {description}

Respond with ONLY valid JSON (no markdown):
{{
  "suggested_reply": "Professional draft reply",
  "next_steps": ["action 1", "action 2"],
  "confidence": 0.0-1.0
}}
"""
        
        try:
            import httpx
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{OLLAMA_URL}/api/generate",
                    json={
                        "model": OLLAMA_MODEL,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"num_predict": 400}
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    response_text = result.get("response", "")
                    
                    import re
                    json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
                    if json_match:
                        reply_data = json.loads(json_match.group())
                    else:
                        reply_data = {"suggested_reply": "Thank you for contacting us.", "confidence": 0.3}
                else:
                    reply_data = {"suggested_reply": "Thank you for contacting us.", "confidence": 0.3}
        except Exception as e:
            logger.warning("smart_reply_failed", error=str(e))
            reply_data = {"suggested_reply": "Thank you for contacting us.", "confidence": 0.3}
        
        # Store suggestion
        suggestion_id = str(uuid4())
        expires_at = datetime.now(timezone.utc).timestamp() + 1800  # 30 min
        
        query = """
            INSERT INTO ai_suggestions (
                id, organization_id, ticket_id, suggestion_type, content,
                confidence, model_id, created_at, expires_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        async with self.conn.cursor() as cur:
            await cur.execute(query, (
                suggestion_id, org_id, ticket_id, "SMART_REPLY",
                reply_data.get("suggested_reply", "Thank you for contacting us."),
                reply_data.get("confidence", 0.5),
                OLLAMA_MODEL,
                datetime.now(timezone.utc),
                datetime.fromtimestamp(expires_at, timezone.utc)
            ))
            await self.conn.commit()
        
        await self.complete_job(job["id"], True)
        logger.info("smart_reply_completed", ticket_id=ticket_id)
        return True
    
    async def handle_sla_predict(self, job: Dict[str, Any]) -> bool:
        """SLA prediction job handler"""
        payload = job.get("payload", {})
        ticket_id = payload.get("ticket_id")
        org_id = job.get("organization_id")
        
        if not ticket_id:
            await self.complete_job(job["id"], False, "Missing ticket_id")
            return False
        
        logger.info("processing_sla_predict_job", ticket_id=ticket_id)
        
        # Get SLA policy and ticket details
        query = """
            SELECT t.created_at, t.status, t.priority, t.sla_due_at,
                   sp.resolution_time_low, sp.resolution_time_medium, 
                   sp.resolution_time_high, sp.resolution_time_urgent
            FROM tickets t
            LEFT JOIN sla_policies sp ON sp.organization_id = t.organization_id AND sp.is_active = true
            WHERE t.id = %s::uuid
        """
        
        async with self.conn.cursor() as cur:
            await cur.execute(query, (ticket_id,))
            row = await cur.fetchone()
            
            if not row:
                await self.complete_job(job["id"], False, "Ticket not found")
                return False
        
        created_at, status, priority = row[0], row[1], row[2]
        sla_times = {
            "low": row[3] or 2880,
            "medium": row[4] or 1440,
            "high": row[5] or 480,
            "urgent": row[6] or 240
        }
        
        # Calculate SLA prediction
        if status in ("resolved", "closed"):
            time_to_breach = None
            sla_risk_score = 0.0
        else:
            sla_target = sla_times.get(priority, 1440)
            elapsed_minutes = (datetime.now(timezone.utc) - created_at).total_seconds() / 60
            time_to_breach = sla_target - elapsed_minutes
            sla_risk_score = min(1.0, elapsed_minutes / sla_target) if sla_target > 0 else 0.0
        
        # Update ticket
        query = """
            UPDATE tickets
            SET time_to_breach_minutes = %s,
                sla_risk_score = %s,
                updated_at = %s
            WHERE id = %s::uuid
        """
        
        async with self.conn.cursor() as cur:
            await cur.execute(query, (
                int(time_to_breach) if time_to_breach else None,
                round(sla_risk_score, 3) if sla_risk_score else None,
                datetime.now(timezone.utc),
                ticket_id
            ))
            await self.conn.commit()
        
        await self.complete_job(job["id"], True)
        logger.info("sla_predict_completed", ticket_id=ticket_id, risk=sla_risk_score)
        return True
    
    async def handle_metrics_snapshot(self, job: Dict[str, Any]) -> bool:
        """Metrics snapshot job handler"""
        payload = job.get("payload", {})
        org_id = payload.get("organization_id") or job.get("organization_id")
        
        if not org_id:
            await self.complete_job(job["id"], False, "Missing organization_id")
            return False
        
        logger.info("processing_metrics_snapshot", org_id=org_id)
        
        # Get metrics
        query = """
            SELECT status, priority, COUNT(*) as count
            FROM tickets
            WHERE organization_id = %s::uuid
            GROUP BY status, priority
        """
        
        async with self.conn.cursor() as cur:
            await cur.execute(query, (org_id,))
            rows = await cur.fetchall()
        
        tickets_by_status = {}
        tickets_by_priority = {}
        
        for row in rows:
            status, priority, count = row[0], row[1], row[2]
            tickets_by_status[status] = tickets_by_status.get(status, 0) + count
            tickets_by_priority[priority] = tickets_by_priority.get(priority, 0) + count
        
        # Calculate SLA compliance (simplified)
        sla_compliance = 95.0  # Placeholder
        
        # Store snapshot
        snapshot_id = str(uuid4())
        query = """
            INSERT INTO metrics_snapshots (
                id, organization_id, snapshot_ts, tickets_by_status,
                tickets_by_priority, sla_compliance_pct, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        async with self.conn.cursor() as cur:
            await cur.execute(query, (
                snapshot_id, org_id, datetime.now(timezone.utc),
                json.dumps(tickets_by_status), json.dumps(tickets_by_priority),
                sla_compliance, datetime.now(timezone.utc)
            ))
            await self.conn.commit()
        
        await self.complete_job(job["id"], True)
        logger.info("metrics_snapshot_completed", org_id=org_id)
        return True
    
    async def handle_sentiment_analysis(self, job: Dict[str, Any]) -> bool:
        """Sentiment analysis job handler — detect escalation risk"""
        payload = job.get("payload", {})
        ticket_id = payload.get("ticket_id")
        org_id = job.get("organization_id")

        if not ticket_id:
            await self.complete_job(job["id"], False, "Missing ticket_id")
            return False

        logger.info("processing_sentiment_job", ticket_id=ticket_id, org_id=org_id)

        # Get ticket details
        query = "SELECT subject, description FROM tickets WHERE id = %s::uuid"

        async with self.conn.cursor() as cur:
            await cur.execute(query, (ticket_id,))
            row = await cur.fetchone()

            if not row:
                await self.complete_job(job["id"], False, "Ticket not found")
                return False

            subject, description = row[0], row[1]

        # Call Ollama for sentiment analysis
        prompt = f"""Analyze the sentiment and escalation risk of this support ticket.

Subject: {subject}
Description: {description}

Respond with ONLY valid JSON (no markdown):
{{
  "sentiment_label": "positive|neutral|negative|angry",
  "sentiment_score": 0.0-1.0,
  "escalation_risk": "low|medium|high",
  "escalation_score": 0.0-1.0,
  "key_phrases": ["phrase1", "phrase2"]
}}
"""

        try:
            import httpx
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{OLLAMA_URL}/api/generate",
                    json={
                        "model": OLLAMA_MODEL,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"num_predict": 200}
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    response_text = result.get("response", "")

                    import re
                    json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
                    if json_match:
                        sentiment_data = json.loads(json_match.group())
                    else:
                        sentiment_data = {
                            "sentiment_label": "neutral",
                            "sentiment_score": 0.5,
                            "escalation_risk": "low",
                            "escalation_score": 0.2
                        }
                else:
                    sentiment_data = {
                        "sentiment_label": "neutral",
                        "sentiment_score": 0.5,
                        "escalation_risk": "low",
                        "escalation_score": 0.2
                    }
        except Exception as e:
            logger.warning("sentiment_analysis_failed", error=str(e))
            sentiment_data = {
                "sentiment_label": "neutral",
                "sentiment_score": 0.5,
                "escalation_risk": "low",
                "escalation_score": 0.2
            }

        # Store as AI suggestion (no new table needed)
        suggestion_id = str(uuid4())
        query = """
            INSERT INTO ai_suggestions (
                id, organization_id, ticket_id, suggestion_type, content,
                confidence, model_id, created_at, expires_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        async with self.conn.cursor() as cur:
            await cur.execute(query, (
                suggestion_id, org_id, ticket_id, "SENTIMENT_ANALYSIS",
                json.dumps(sentiment_data),
                sentiment_data.get("sentiment_score", 0.5),
                OLLAMA_MODEL,
                datetime.now(timezone.utc),
                datetime.now(timezone.utc)  # No expiry for sentiment
            ))
            await self.conn.commit()

        # ── Gap 1 fix: Check org_settings for auto-escalation ──
        escalation_risk = sentiment_data.get("escalation_risk", "low")
        escalation_score = float(sentiment_data.get("escalation_score", 0))
        sentiment_label = sentiment_data.get("sentiment_label", "neutral")

        if escalation_risk in ("high",) or sentiment_label in ("negative", "angry"):
            try:
                async with self.conn.cursor() as cur:
                    # Read org setting
                    await cur.execute(
                        "SELECT auto_escalate_negative_sentiment, auto_escalate_threshold FROM org_settings WHERE organization_id = %s::uuid",
                        (org_id,)
                    )
                    org_row = await cur.fetchone()
                    auto_escalate = org_row[0] if org_row else False
                    threshold = float(org_row[1]) if org_row and org_row[1] else 0.7

                    if auto_escalate and escalation_score >= threshold:
                        # Escalate: set priority urgent + bump escalation_level
                        await cur.execute(
                            "UPDATE tickets SET priority = 'urgent', escalation_level = escalation_level + 1, updated_at = %s WHERE id = %s::uuid",
                            (datetime.now(timezone.utc), ticket_id)
                        )
                        # Audit log
                        await cur.execute("""
                            INSERT INTO audit_log (id, organization_id, action, entity_type, entity_id, new_values, created_at)
                            VALUES (%s, %s::uuid, %s, %s, %s::uuid, %s, %s)
                        """, (
                            str(uuid4()), org_id, "sentiment_auto_escalated", "ticket", ticket_id,
                            json.dumps({"escalation_risk": escalation_risk, "escalation_score": escalation_score,
                                        "sentiment_label": sentiment_label, "new_priority": "urgent"}),
                            datetime.now(timezone.utc)
                        ))
                        await self.conn.commit()
                        logger.info("sentiment_auto_escalated", ticket_id=ticket_id,
                                    escalation_score=escalation_score, sentiment=sentiment_label)

                        # Attempt SMTP notification (best-effort)
                        try:
                            import smtplib
                            from email.mime.text import MIMEText
                            smtp_host = os.getenv("SMTP_HOST")
                            smtp_user = os.getenv("SMTP_USER")
                            smtp_pass = os.getenv("SMTP_PASSWORD")
                            smtp_from = os.getenv("SMTP_FROM", "support@atum.desk")
                            if smtp_host and smtp_user and smtp_pass and smtp_pass != "your-gmail-app-password":
                                msg = MIMEText(f"Ticket {ticket_id} auto-escalated to URGENT.\nSentiment: {sentiment_label} (score: {escalation_score})")
                                msg["Subject"] = f"[ATUM DESK] Auto-Escalation: Ticket {ticket_id[:8]}..."
                                msg["From"] = smtp_from
                                msg["To"] = smtp_user  # Notify admin
                                with smtplib.SMTP(smtp_host, int(os.getenv("SMTP_PORT", "587"))) as s:
                                    s.starttls()
                                    s.login(smtp_user, smtp_pass)
                                    s.send_message(msg)
                                logger.info("escalation_email_sent", ticket_id=ticket_id)
                        except Exception as smtp_err:
                            logger.debug("escalation_email_skipped", reason=str(smtp_err))

            except Exception as esc_err:
                logger.warning("escalation_check_failed", error=str(esc_err))

        await self.complete_job(job["id"], True)
        logger.info("sentiment_analysis_completed", ticket_id=ticket_id,
                     sentiment=sentiment_data.get("sentiment_label"),
                     escalation_risk=escalation_risk)
        return True

    async def handle_cleanup_logs(self, job: Dict[str, Any]) -> bool:
        """Gap 17: Cleanup old logs based on retention policy"""
        org_id = job.get("organization_id")
        retention_days = 365 
        
        if org_id:
             async with self.conn.cursor() as cur:
                await cur.execute("SELECT audit_retention_days FROM org_settings WHERE organization_id = %s::uuid", (org_id,))
                row = await cur.fetchone()
                if row and row[0]:
                    retention_days = row[0]

        logger.info("running_cleanup", org_id=org_id, retention_days=retention_days)
        cutoff = f"NOW() - INTERVAL '{retention_days} days'"
        
        async with self.conn.cursor() as cur:
            # Cleanup audit logs
            q1 = f"DELETE FROM audit_log WHERE created_at < {cutoff}"
            if org_id: q1 += f" AND organization_id = '{org_id}'"
            await cur.execute(q1)
            audit_deleted = cur.rowcount
            
            # Cleanup job queue
            q2 = f"DELETE FROM job_queue WHERE status IN ('DONE', 'FAILED') AND updated_at < {cutoff}"
            if org_id: q2 += f" AND organization_id = '{org_id}'"
            await cur.execute(q2)
            jobs_deleted = cur.rowcount
            
            await self.conn.commit()
            
        logger.info("cleanup_completed", audit_deleted=audit_deleted, jobs_deleted=jobs_deleted)
        await self.complete_job(job["id"], True)
        return True

    async def process_job(self, job: Dict[str, Any]) -> bool:
        """Process a single job"""
        job_type = job.get("job_type")
        org_id = job.get("organization_id")
        
        # Set RLS org context per job (CRITICAL for tenant isolation)
        await self.set_org_context(org_id)
        
        handler_name = JOB_TYPES.get(job_type)
        
        if not handler_name:
            await self.complete_job(job["id"], False, f"Unknown job type: {job_type}")
            return False
        
        handler = getattr(self, handler_name, None)
        
        if not handler:
            await self.complete_job(job["id"], False, f"Handler not found: {handler_name}")
            return False
        
        try:
            return await handler(job)
        except Exception as e:
            logger.error("job_processing_error", job_id=job["id"], error=str(e))
            await self.complete_job(job["id"], False, str(e))
            return False
        finally:
            await self.clear_org_context()
    
    async def run(self):
        """Main worker loop"""
        await self.connect()
        
        backoff = 1
        max_backoff = 60
        
        while self.running:
            try:
                job = await self.claim_job()
                
                if job:
                    logger.info("job_claimed", job_id=job["id"], job_type=job["job_type"])
                    await self.process_job(job)
                    backoff = 1  # Reset backoff on success
                else:
                    # No job available, backoff
                    await asyncio.sleep(backoff)
                    backoff = min(backoff * 1.5, max_backoff)
                    
            except Exception as e:
                logger.error("worker_error", error=str(e))
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, max_backoff)
        
        await self.close()


async def main():
    worker = JobWorker()
    
    # Handle shutdown
    import signal
    
    def signal_handler(sig):
        logger.info("shutdown_signal_received", signal=sig)
        worker.running = False
    
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda s=sig: signal_handler(s))
    
    logger.info("job_worker_starting", worker_id=worker.worker_id)
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
