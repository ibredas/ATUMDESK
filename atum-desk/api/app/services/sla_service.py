from datetime import datetime, timedelta
from typing import Optional
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ticket import Ticket
from app.models.sla_policy import SLAPolicy
from app.models.sla_calculation import SLACalculation
from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)

class SLAService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate_targets(self, ticket: Ticket):
        """
        Calculate and set SLA targets for a ticket based on its policy.
        SLA only starts when ticket is in ACCEPTED status (per spec).
        """
        # SLA spec: Only compute targets for ACCEPTED tickets
        from app.models.ticket import TicketStatus
        if ticket.status != TicketStatus.ACCEPTED:
            logger.debug(f"SLA targets skipped for ticket {ticket.id}: status is {ticket.status.value}, not ACCEPTED")
            return

        if not ticket.sla_policy_id:
            logger.debug(f"Ticket {ticket.id} has no SLA policy.")
            return

        policy = await self.db.get(SLAPolicy, ticket.sla_policy_id)
        if not policy:
            return

        # Simple 24/7 calculation for Phase 1
        now = datetime.utcnow()
        
        response_minutes = policy.get_response_time(ticket.priority)
        resolution_minutes = policy.get_resolution_time(ticket.priority)
        
        # Create or update calculation record
        query = select(SLACalculation).where(SLACalculation.ticket_id == ticket.id)
        result = await self.db.execute(query)
        calc = result.scalar_one_or_none()
        
        if not calc:
            calc = SLACalculation(ticket_id=ticket.id)
            self.db.add(calc)
        
        if response_minutes:
            calc.first_response_target = now + timedelta(minutes=response_minutes)
        
        if resolution_minutes:
            calc.resolution_target = now + timedelta(minutes=resolution_minutes)
            
        # Update ticket/calc
        await self.db.commit()
        logger.info(f"SLA Targets set for Ticket {ticket.id}")

    async def check_breaches(self, ticket_id: str):
        """
        Check if a ticket has breached its SLA targets.
        """
        query = select(SLACalculation).where(SLACalculation.ticket_id == ticket_id)
        result = await self.db.execute(query)
        calc = result.scalar_one_or_none()
        
        if not calc:
            return

        now = datetime.utcnow()
        changed = False

        # Check Response Breach
        if calc.first_response_target and not calc.first_response_actual:
            if now > calc.first_response_target and not calc.first_response_breached:
                calc.first_response_breached = True
                calc.breach_reason = "Response time exceeded"
                changed = True
                await self._log_breach(ticket_id, "response")

        # Check Resolution Breach
        if calc.resolution_target and not calc.resolution_actual:
            if now > calc.resolution_target and not calc.resolution_breached:
                calc.resolution_breached = True
                calc.breach_reason = "Resolution time exceeded"
                changed = True
                await self._log_breach(ticket_id, "resolution")
        
        if changed:
            await self.db.commit()

    async def _log_breach(self, ticket_id, breach_type):
        ticket = await self.db.get(Ticket, ticket_id)
        if ticket:
            audit = AuditLog(
                organization_id=ticket.organization_id,
                entity_type="ticket",
                entity_id=ticket.id,
                action="sla_breach",
                new_values={"breach_type": breach_type}
            )
            self.db.add(audit)
            logger.warning(f"SLA BREACH ({breach_type}) for Ticket {ticket.id}")
