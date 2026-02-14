import asyncio
import logging
import sys
import os
from datetime import datetime
from sqlalchemy import select, text
from time import sleep

# Add path
sys.path.append(os.getcwd())

from app.db.base import AsyncSessionLocal
from app.models.ticket import Ticket, TicketStatus
from app.models.organization import Organization
from app.services.sla_service import SLAService

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SLAWorker")


async def run_worker():
    logger.info("Starting SLA Worker...")
    
    while True:
        processed_count = 0
        skipped_null_sla_count = 0
        skipped_paused_count = 0
        
        try:
            async with AsyncSessionLocal() as db:
                # Get all active organizations
                org_query = select(Organization.id, Organization.name).where(
                    Organization.is_active == True
                )
                org_result = await db.execute(org_query)
                organizations = org_result.all()
                
                logger.info(f"Processing SLA for {len(organizations)} organizations...")
                
                # Process org-by-org with proper RLS context
                for org_id, org_name in organizations:
                    # Set org context for this org's tickets
                    await db.execute(text(f"SET LOCAL app.current_org = '{org_id}'"))
                    logger.debug(f"Processing SLA for org: {org_name} ({org_id})")
                    
                    sla_service = SLAService(db)
                    
                    # Fetch tickets for this org that have SLA started
                    query = select(Ticket.id, Ticket.status, Ticket.sla_started_at, Ticket.sla_paused_at, Ticket.sla_paused_duration).where(
                        Ticket.organization_id == org_id,
                        Ticket.sla_started_at.is_not(None),
                        Ticket.status.notin_([TicketStatus.CLOSED, TicketStatus.RESOLVED])
                    )
                    result = await db.execute(query)
                    tickets = result.all()
                    
                    for tid, status, sla_started_at, sla_paused_at, sla_paused_duration in tickets:
                        # Skip if SLA never started
                        if sla_started_at is None:
                            skipped_null_sla_count += 1
                            continue
                        
                        # Skip if ticket is in WAITING_CUSTOMER (paused state)
                        if status == TicketStatus.WAITING_CUSTOMER:
                            skipped_paused_count += 1
                            continue
                        
                        # Process active ticket
                        await sla_service.check_breaches(tid)
                        processed_count += 1
                    
                    logger.debug(f"Completed SLA for org: {org_name}, tickets processed: {len(tickets)}")
                    
                    # Clear org context for next org
                    await db.execute(text("SET LOCAL app.current_org = NULL"))
            
            # Log summary
            logger.info(f"SLA Worker Summary: processed={processed_count}, skipped_null_sla={skipped_null_sla_count}, skipped_paused={skipped_paused_count}")
            
            # Sleep for 60 seconds
            await asyncio.sleep(60)
            
        except Exception as e:
            logger.error(f"Worker crashed: {e}")
            await asyncio.sleep(10) # Prevent tight loop on DB failure

if __name__ == "__main__":
    try:
        asyncio.run(run_worker())
    except KeyboardInterrupt:
        logger.info("Worker stopped.")
