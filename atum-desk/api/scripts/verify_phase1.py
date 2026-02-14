import asyncio
import logging
import sys
import os
import uuid
from datetime import datetime, timedelta
from sqlalchemy import select, delete

# Add path
sys.path.append(os.getcwd())

from app.db.base import AsyncSessionLocal
from app.models.ticket import Ticket, TicketPriority, TicketStatus
from app.models.rules import Rule, RuleAction
from app.models.sla_policy import SLAPolicy
from app.models.sla_calculation import SLACalculation
from app.models.organization import Organization
from app.models.user import User
from app.services.rules_service import RulesService
from app.services.sla_service import SLAService

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Verification")

async def verify_phase1():
    async with AsyncSessionLocal() as db:
        logger.info("--- Starting Phase 1 Verification ---")

        # 1. Setup Data
        # Get Admin User & Org
        query = select(User).limit(1)
        res = await db.execute(query)
        user = res.scalar_one()
        org_id = user.organization_id
        
        logger.info(f"Using User: {user.email} Org: {org_id}")

        # Create Test Rule
        rule_name = f"Test Rule {uuid.uuid4().hex[:8]}"
        rule = Rule(
            name=rule_name,
            event_type="ticket_create",
            conditions={"priority": "urgent"},
            actions=[
                RuleAction(action_type="add_tag", action_data={"tag": "vip_urgent"}),
                RuleAction(action_type="set_priority", action_data={"value": "urgent"}) # Redundant but checking logic
            ],
            execution_order=1
        )
        db.add(rule)
        
        # Create Test SLA Policy
        policy = SLAPolicy(
            organization_id=org_id,
            name=f"Test Policy {uuid.uuid4().hex[:8]}",
            response_time_urgent=10, # 10 mins
            resolution_time_urgent=60, # 1 hour
            is_active=True
        )
        db.add(policy)
        await db.commit()
        await db.refresh(rule)
        await db.refresh(policy)
        
        logger.info(f"Created Rule: {rule.name}")
        logger.info(f"Created Policy: {policy.name}")

        # 2. Simulate Ticket Creation (Calling Services Manually as Router would)
        logger.info("Creating Test Ticket...")
        ticket = Ticket(
            organization_id=org_id,
            requester_id=user.id,
            subject="Verification Ticket Phase 1",
            description="Testing Rules & SLA",
            priority=TicketPriority.URGENT,
            status=TicketStatus.NEW,
            sla_policy_id=policy.id # In real app, we might auto-assign policy
        )
        db.add(ticket)
        await db.commit()
        await db.refresh(ticket)
        
        # 3. Validation: Rules
        logger.info("Executing RulesService...")
        rules_service = RulesService(db)
        await rules_service.evaluate_ticket(ticket, "ticket_create")
        
        # Commit the changes made by RulesService
        await db.commit()
        # Check if tag was added
        await db.refresh(ticket)
        logger.info(f"Ticket Tags: {ticket.tags}")
        if "vip_urgent" in (ticket.tags or []):
            logger.info("✅ SUCCESS: Rule applied 'vip_urgent' tag.")
        else:
            logger.error("❌ FAILURE: Rule did not apply tag.")

        # 4. Validation: SLA
        logger.info("Executing SLAService...")
        sla_service = SLAService(db)
        await sla_service.calculate_targets(ticket)
        
        # Check targets
        q_sla = select(SLACalculation).where(SLACalculation.ticket_id == ticket.id)
        res_sla = await db.execute(q_sla)
        sla_calc = res_sla.scalar_one_or_none()
        
        if sla_calc:
            logger.info(f"SLA Response Target: {sla_calc.first_response_target}")
            logger.info(f"SLA Resolution Target: {sla_calc.resolution_target}")
            
            if sla_calc.first_response_target and sla_calc.resolution_target:
                 logger.info("✅ SUCCESS: SLA Targets calculated.")
            else:
                 logger.error("❌ FAILURE: SLA Targets missing.")
        else:
            logger.error("❌ FAILURE: SLACalculation record not found.")

        # Cleanup
        logger.info("Cleaning up...")
        await db.delete(ticket)
        await db.delete(rule)
        await db.delete(policy)
        if sla_calc:
            await db.delete(sla_calc)
        await db.commit()
        logger.info("--- Verification Complete ---")

if __name__ == "__main__":
    asyncio.run(verify_phase1())
