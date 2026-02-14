from typing import List, Dict, Any
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.rules import Rule, RuleAction
from app.models.ticket import Ticket
from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)

class RulesService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def evaluate_ticket(self, ticket: Ticket, event_type: str):
        """
        Evaluate a ticket against active rules for a given event type.
        """
        query = select(Rule).where(
            Rule.event_type == event_type,
            Rule.is_active == True
        ).order_by(Rule.execution_order)
        
        result = await self.db.execute(query)
        rules = result.scalars().all()

        match_count = 0
        for rule in rules:
            if self._matches_condition(ticket, rule.conditions):
                logger.info(f"Rule '{rule.name}' matched for Ticket {ticket.id}")
                await self._execute_actions(ticket, rule.actions)
                match_count += 1
        
        return match_count

    def _matches_condition(self, ticket: Ticket, conditions: Dict[str, Any]) -> bool:
        if not conditions:
            return True

        for field, expected_value in conditions.items():
            actual_value = getattr(ticket, field.lower(), None)
            
            # Handle Enums (e.g. TicketPriority)
            if hasattr(actual_value, "value"):
                actual_value = actual_value.value
                
            if str(expected_value).lower() != str(actual_value).lower():
                return False
        
        return True

    async def _execute_actions(self, ticket: Ticket, actions: List[RuleAction]):
        for action in actions:
            try:
                if action.action_type == "set_priority":
                    new_priority = action.action_data.get("value")
                    if new_priority:
                        ticket.priority = new_priority
                
                elif action.action_type == "assign_to":
                    user_id = action.action_data.get("user_id")
                    if user_id:
                        ticket.assigned_to = user_id

                elif action.action_type == "add_tag":
                    tag = action.action_data.get("tag")
                    if tag:
                        current_tags = ticket.tags or []
                        if tag not in current_tags:
                            ticket.tags = current_tags + [tag]
                
                # Audit Log
                audit = AuditLog(
                    organization_id=ticket.organization_id,
                    entity_type="ticket",
                    entity_id=ticket.id,
                    action="rule_execution",
                    new_values={"rule_action": action.action_type, "data": action.action_data}
                )
                self.db.add(audit)

            except Exception as e:
                logger.error(f"Failed to execute action {action.action_type}: {e}")
