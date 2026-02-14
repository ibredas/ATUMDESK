"""
Sentiment-Triggered Escalation Service
Analyzes ticket sentiment and automatically escalates negative/urgent cases
"""
import logging
from typing import Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.ticket import Ticket, TicketPriority, TicketStatus
from app.models.user import User, UserRole
from app.config import get_settings

logger = logging.getLogger(__name__)
_settings = get_settings()

SENTIMENT_ESCALATION_THRESHOLD = -0.3
URGENT_SENTIMENT_THRESHOLD = 0.8


class SentimentEscalationService:
    """Service for handling sentiment-based ticket escalation"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def analyze_and_escalate(
        self,
        ticket: Ticket,
        sentiment_score: float,
        sentiment_label: str,
        urgency_level: str
    ) -> bool:
        """
        Analyze sentiment and escalate if needed.
        Returns True if escalation was triggered.
        """
        if not _settings.AI_SENTIMENT_ANALYSIS:
            return False
        
        escalation_triggered = False
        
        # Check if negative sentiment triggers escalation
        if sentiment_score < SENTIMENT_ESCALATION_THRESHOLD:
            await self._escalate_ticket(
                ticket=ticket,
                reason="negative_sentiment",
                sentiment_score=sentiment_score,
                sentiment_label=sentiment_label
            )
            escalation_triggered = True
        
        # Check if urgent sentiment triggers escalation
        elif urgency_level in ["high", "critical"] and ticket.priority != TicketPriority.URGENT:
            await self._escalate_ticket(
                ticket=ticket,
                reason="urgent_sentiment",
                urgency_level=urgency_level
            )
            escalation_triggered = True
        
        # Check escalation level threshold
        if ticket.escalation_level < 3:
            if sentiment_score < -0.7:
                await self._increase_escalation(ticket, "severe_negative_sentiment")
                escalation_triggered = True
        
        return escalation_triggered
    
    async def _escalate_ticket(
        self,
        ticket: Ticket,
        reason: str,
        **kwargs
    ):
        """Escalate ticket to higher priority and notify managers"""
        old_priority = ticket.priority
        
        # Upgrade priority if not already urgent
        if ticket.priority != TicketPriority.URGENT:
            if ticket.priority == TicketPriority.LOW:
                ticket.priority = TicketPriority.MEDIUM
            elif ticket.priority == TicketPriority.MEDIUM:
                ticket.priority = TicketPriority.HIGH
            elif ticket.priority == TicketPriority.HIGH:
                ticket.priority = TicketPriority.URGENT
        
        # Increment escalation level
        ticket.escalation_level += 1
        
        await self.db.commit()
        await self.db.refresh(ticket)
        
        # Log escalation
        logger.info(
            f"Sentiment escalation triggered for ticket {ticket.id}: "
            f"reason={reason}, old_priority={old_priority}, "
            f"new_priority={ticket.priority}, escalation_level={ticket.escalation_level}"
        )
        
        # Create audit log entry
        await self._log_escalation(ticket, reason, kwargs)
    
    async def _increase_escalation(self, ticket: Ticket, reason: str):
        """Increase escalation level without priority change"""
        ticket.escalation_level += 1
        await self.db.commit()
        
        logger.info(
            f"Escalation level increased for ticket {ticket.id}: "
            f"reason={reason}, new_level={ticket.escalation_level}"
        )
    
    async def _log_escalation(
        self,
        ticket: Ticket,
        reason: str,
        details: dict
    ):
        """Log escalation action to audit"""
        from app.models.audit_log import AuditLog
        
        audit = AuditLog(
            organization_id=ticket.organization_id,
            user_id=ticket.requester_id,
            action="sentiment_escalation",
            entity_type="ticket",
            entity_id=ticket.id,
            new_values={
                "reason": reason,
                "details": details,
                "priority": ticket.priority.value if hasattr(ticket.priority, 'value') else str(ticket.priority),
                "escalation_level": ticket.escalation_level
            }
        )
        self.db.add(audit)
        await self.db.commit()
    
    async def get_escalation_recommendations(
        self,
        ticket: Ticket
    ) -> list[str]:
        """Get AI-generated escalation recommendations"""
        recommendations = []
        
        if ticket.escalation_level >= 2:
            recommendations.append("Consider assigning to senior agent")
        
        if ticket.escalation_level >= 3:
            recommendations.append("Manager review recommended")
        
        if ticket.priority == TicketPriority.URGENT:
            recommendations.append("Immediate response required")
        
        return recommendations


async def check_sentiment_escalation(
    db: AsyncSession,
    ticket: Ticket,
    sentiment_score: float,
    sentiment_label: str,
    urgency_level: str
) -> bool:
    """Helper function to check and trigger escalation"""
    service = SentimentEscalationService(db)
    return await service.analyze_and_escalate(
        ticket=ticket,
        sentiment_score=sentiment_score,
        sentiment_label=sentiment_label,
        urgency_level=urgency_level
    )
