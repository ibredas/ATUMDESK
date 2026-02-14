#!/usr/bin/env python3
"""
RAG Worker - Long-running queue consumer for indexing
"""
import asyncio
import logging
import signal
import sys
import os

# Add api directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncpg
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from uuid import UUID
import time
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("rag_worker")

# Database URL
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/atum_desk"

# Worker settings
POLL_INTERVAL = 2  # seconds
MAX_ATTEMPTS = 3
BATCH_SIZE = 10
SHUTDOWN_TIMEOUT = 30

# Import indexer (lazy load to avoid circular imports)
def get_indexer_class():
    from app.services.rag.indexer import RAGIndexer
    return RAGIndexer


class RAGWorker:
    """Long-running RAG indexing worker"""
    
    def __init__(self):
        self.engine = None
        self.running = True
        self.processed = 0
        self.errors = 0
    
    async def start(self):
        """Initialize and start worker"""
        logger.info("Starting RAG Worker...")
        
        self.engine = create_async_engine(DATABASE_URL, echo=False)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        
        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._shutdown)
        signal.signal(signal.SIGINT, self._shutdown)
        
        logger.info("RAG Worker started, polling for jobs...")
        
        while self.running:
            try:
                await self._process_jobs()
            except Exception as e:
                logger.error(f"Worker error: {e}", exc_info=True)
                self.errors += 1
            
            await asyncio.sleep(POLL_INTERVAL)
        
        await self._cleanup()
    
    def _shutdown(self, signum, frame):
        """Handle shutdown signal"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    async def _cleanup(self):
        """Cleanup resources"""
        if self.engine:
            await self.engine.dispose()
        logger.info(f"Worker stopped. Processed: {self.processed}, Errors: {self.errors}")
    
    async def _process_jobs(self):
        """Fetch and process pending jobs"""
        async with self.async_session() as session:
            # Get pending jobs
            stmt = text("""
                SELECT id, organization_id, source_type, source_id, action, attempts
                FROM rag_index_queue
                WHERE status = 'pending'
                ORDER BY priority DESC, created_at ASC
                LIMIT :limit
                FOR UPDATE SKIP LOCKED
            """)
            
            result = await session.execute(stmt, {"limit": BATCH_SIZE})
            rows = result.fetchall()
            
            if not rows:
                return
            
            # Mark as running
            job_ids = [row[0] for row in rows]
            if job_ids:
                await session.execute(
                    text("UPDATE rag_index_queue SET status = 'running', updated_at = now() WHERE id = ANY(:ids)"),
                    {"ids": job_ids}
                )
                await session.commit()
            
            # Process each job
            for row in rows:
                job_id, org_id, source_type, source_id, action, attempts = row
                
                try:
                    await self._process_job(session, job_id, org_id, source_type, source_id, action)
                    await session.execute(
                        text("UPDATE rag_index_queue SET status = 'done', updated_at = now() WHERE id = :id"),
                        {"id": job_id}
                    )
                    self.processed += 1
                    logger.info(f"Completed job {job_id}: {source_type}/{source_id}")
                except Exception as e:
                    logger.error(f"Job {job_id} failed: {e}", exc_info=True)
                    await session.execute(
                        text("""
                            UPDATE rag_index_queue 
                            SET status = CASE 
                                WHEN attempts >= :max_attempts THEN 'failed' 
                                ELSE 'pending' 
                            END,
                            attempts = attempts + 1,
                            last_error = :error,
                            updated_at = now()
                            WHERE id = :id
                        """),
                        {"id": job_id, "error": str(e)[:500], "max_attempts": MAX_ATTEMPTS}
                    )
                    self.errors += 1
                
                await session.commit()
    
    async def _process_job(
        self,
        session: AsyncSession,
        job_id: UUID,
        org_id: UUID,
        source_type: str,
        source_id: UUID,
        action: str,
    ):
        """Process a single index job"""
        from app.services.rag.indexer import RAGIndexer
        from app.services.rag.store import RAGStore
        
        store = RAGStore(session)
        indexer = RAGIndexer(store)
        
        if action == "delete":
            await indexer.delete_index(org_id, source_type, source_id)
            return
        
        # Fetch source data based on type
        if source_type == "ticket":
            await self._index_ticket(session, indexer, org_id, source_id)
        elif source_type == "kb":
            await self._index_kb(session, indexer, org_id, source_id)
        elif source_type == "asset":
            await self._index_asset(session, indexer, org_id, source_id)
        else:
            logger.warning(f"Unknown source type: {source_type}")
    
    async def _index_ticket(
        self,
        session: AsyncSession,
        indexer,
        org_id: UUID,
        ticket_id: UUID,
    ):
        """Index a ticket"""
        stmt = text("""
            SELECT subject, description, resolution, status
            FROM tickets
            WHERE id = :id AND organization_id = :org_id
        """)
        
        result = await session.execute(stmt, {"id": ticket_id, "org_id": org_id})
        row = result.fetchone()
        
        if not row:
            logger.warning(f"Ticket {ticket_id} not found")
            return
        
        await indexer.index_ticket(
            organization_id=org_id,
            ticket_id=ticket_id,
            subject=row[0],
            description=row[1],
            resolution=row[2],
            status=row[3],
        )
    
    async def _index_kb(
        self,
        session: AsyncSession,
        indexer,
        org_id: UUID,
        article_id: UUID,
    ):
        """Index a KB article"""
        stmt = text("""
            SELECT title, content, visibility
            FROM kb_articles
            WHERE id = :id AND organization_id = :org_id
        """)
        
        result = await session.execute(stmt, {"id": article_id, "org_id": org_id})
        row = result.fetchone()
        
        if not row:
            logger.warning(f"KB article {article_id} not found")
            return
        
        await indexer.index_kb_article(
            organization_id=org_id,
            article_id=article_id,
            title=row[0],
            content=row[1],
            visibility=row[2] or "public",
        )
    
    async def _index_asset(
        self,
        session: AsyncSession,
        indexer,
        org_id: UUID,
        asset_id: UUID,
    ):
        """Index an asset"""
        stmt = text("""
            SELECT name, asset_type, metadata_json
            FROM assets
            WHERE id = :id AND organization_id = :org_id
        """)
        
        result = await session.execute(stmt, {"id": asset_id, "org_id": org_id})
        row = result.fetchone()
        
        if not row:
            logger.warning(f"Asset {asset_id} not found")
            return
        
        await indexer.index_asset(
            organization_id=org_id,
            asset_id=asset_id,
            name=row[0],
            asset_type=row[1],
            metadata=row[2] or {},
        )


async def main():
    """Main entry point"""
    worker = RAGWorker()
    
    try:
        await worker.start()
    except KeyboardInterrupt:
        logger.info("Interrupted")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
