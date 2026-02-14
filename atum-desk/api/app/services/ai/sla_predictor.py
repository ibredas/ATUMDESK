"""
SLA Breach Prediction Service
Predicts when tickets will breach SLA based on historical patterns
"""
import logging
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.ticket import Ticket, TicketStatus, TicketPriority
from app.config import get_settings

logger = logging.getLogger(__name__)
_settings = get_settings()

PRIORITY_HOURS = {
    "urgent": 1,
    "high": 4,
    "medium": 24,
    "low": 72
}


class SLABreachPredictor:
    """Predicts SLA breaches before they happen"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def predict_breach(
        self,
        ticket: Ticket
    ) -> Dict[str, Any]:
        """
        Predict if ticket will breach SLA and when.
        Returns prediction with confidence and recommendations.
        """
        if not ticket.sla_due_at:
            return {
                "will_breach": False,
                "reason": "no_sla",
                "confidence": 0.0
            }
        
        now = datetime.utcnow()
        time_until_due = (ticket.sla_due_at - now).total_seconds() / 3600
        
        # Get historical resolution time for similar tickets
        avg_resolution_hours = await self._get_avg_resolution_time(
            ticket.organization_id,
            ticket.priority.value if hasattr(ticket.priority, 'value') else str(ticket.priority)
        )
        
        # Calculate breach probability
        will_breach = False
        breach_probability = 0.0
        
        if time_until_due > 0:
            # More time needed than available
            if avg_resolution_hours > time_until_due:
                will_breach = True
                breach_probability = min(0.95, (avg_resolution_hours - time_until_due) / avg_resolution_hours + 0.3)
            else:
                # Check for other risk factors
                risk_score = await self._calculate_risk_score(ticket)
                breach_probability = risk_score * 0.5
                will_breach = risk_score > 0.7
        
        # Generate recommendations
        recommendations = []
        if will_breach or breach_probability > 0.5:
            recommendations = self._generate_recommendations(ticket, time_until_due, avg_resolution_hours)
        
        return {
            "will_breach": will_breach,
            "breach_probability": round(breach_probability, 2),
            "time_until_due_hours": round(time_until_due, 1),
            "estimated_resolution_hours": round(avg_resolution_hours, 1),
            "confidence": 0.75,
            "recommendations": recommendations,
            "predicted_at": now.isoformat()
        }
    
    async def _get_avg_resolution_time(
        self,
        organization_id: UUID,
        priority: str
    ) -> float:
        """Get average resolution time for similar tickets"""
        # Get resolved tickets in last 30 days
        since = datetime.utcnow() - timedelta(days=30)
        
        result = await self.db.execute(
            select(
                func.avg(
                    func.extract('epoch', Ticket.resolved_at - Ticket.created_at) / 3600
                )
            ).where(
                and_(
                    Ticket.organization_id == organization_id,
                    Ticket.priority == TicketPriority[priority.upper()],
                    Ticket.status == TicketStatus.RESOLVED,
                    Ticket.resolved_at >= since,
                    Ticket.resolved_at.isnot(None)
                )
            )
        )
        
        avg_hours = result.scalar()
        if avg_hours is None:
            # Use default based on priority
            return PRIORITY_HOURS.get(priority.lower(), 24)
        
        return float(avg_hours)
    
    async def _calculate_risk_score(self, ticket: Ticket) -> float:
        """Calculate risk score based on various factors"""
        risk = 0.0
        
        # Factor 1: Unassigned
        if not ticket.assigned_to:
            risk += 0.3
        
        # Factor 2: High priority
        if ticket.priority in [TicketPriority.HIGH, TicketPriority.URGENT]:
            risk += 0.2
        
        # Factor 3: Age of ticket
        age_hours = (datetime.utcnow() - ticket.created_at).total_seconds() / 3600
        if age_hours > 24:
            risk += 0.2
        elif age_hours > 48:
            risk += 0.3
        
        # Factor 4: Escalation level
        if ticket.escalation_level > 0:
            risk += ticket.escalation_level * 0.1
        
        # Factor 5: Current status
        if ticket.status == TicketStatus.WAITING_CUSTOMER:
            risk += 0.15
        
        return min(1.0, risk)
    
    def _generate_recommendations(
        self,
        ticket: Ticket,
        time_until_due: float,
        est_resolution: float
    ) -> List[str]:
        """Generate actionable recommendations"""
        recs = []
        
        if not ticket.assigned_to:
            recs.append("Assign ticket to an agent immediately")
        
        if time_until_due < est_resolution:
            recs.append(f"Priority override needed - only {time_until_due:.1f}h remaining but ~{est_resolution:.1f}h needed")
        
        if ticket.priority == TicketPriority.LOW and time_until_due < 4:
            recs.append("Consider upgrading priority to high/urgent")
        
        recs.append("Notify team lead for potential escalation")
        
        return recs
    
    async def get_breach_risk_tickets(
        self,
        organization_id: UUID,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get all tickets at risk of SLA breach"""
        result = await self.db.execute(
            select(Ticket).where(
                and_(
                    Ticket.organization_id == organization_id,
                    Ticket.status.in_([TicketStatus.NEW, TicketStatus.IN_PROGRESS, TicketStatus.ASSIGNED]),
                    Ticket.sla_due_at.isnot(None),
                    Ticket.sla_due_at > datetime.utcnow()
                )
            ).order_by(Ticket.sla_due_at)
            .limit(limit)
        )
        
        tickets = result.scalars().all()
        risk_tickets = []
        
        for ticket in tickets:
            prediction = await self.predict_breach(ticket)
            if prediction["breach_probability"] > 0.3:
                risk_tickets.append({
                    "ticket_id": str(ticket.id),
                    "subject": ticket.subject,
                    "priority": ticket.priority.value if hasattr(ticket.priority, 'value') else str(ticket.priority),
                    "sla_due_at": ticket.sla_due_at.isoformat() if ticket.sla_due_at else None,
                    **prediction
                })
        
        return risk_tickets


class EstimatedResolutionTime:
    """Predicts estimated time to resolve tickets"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def predict(
        self,
        ticket: Ticket
    ) -> Dict[str, Any]:
        """Predict estimated resolution time for a ticket"""
        # Base time from priority
        priority = ticket.priority.value if hasattr(ticket.priority, 'value') else str(ticket.priority)
        base_hours = PRIORITY_HOURS.get(priority.lower(), 24)
        
        # Adjustments based on factors
        multiplier = 1.0
        
        # Has assignee - typically faster
        if ticket.assigned_to:
            multiplier *= 0.7
        
        # Has category - can use historical data
        if ticket.ai_suggested_category:
            multiplier *= 0.9
        
        # Escalation level
        if ticket.escalation_level > 0:
            multiplier *= 1.3  # More complex
        
        estimated_hours = base_hours * multiplier
        
        return {
            "estimated_hours": round(estimated_hours, 1),
            "estimated_human": self._format_hours(estimated_hours),
            "confidence": 0.65,
            "based_on": {
                "priority": priority,
                "has_assignee": bool(ticket.assigned_to),
                "escalation_level": ticket.escalation_level
            }
        }
    
    def _format_hours(self, hours: float) -> str:
        """Format hours into human-readable string"""
        if hours < 1:
            return f"{int(hours * 60)} minutes"
        elif hours < 24:
            return f"{round(hours, 1)} hours"
        else:
            days = hours / 24
            return f"{round(days, 1)} days"


async def predict_sla_breach(db: AsyncSession, ticket: Ticket) -> Dict[str, Any]:
    """Helper function for SLA breach prediction"""
    predictor = SLABreachPredictor(db)
    return await predictor.predict_breach(ticket)


async def predict_resolution_time(db: AsyncSession, ticket: Ticket) -> Dict[str, Any]:
    """Helper function for resolution time prediction"""
    predictor = EstimatedResolutionTime(db)
    return await predictor.predict(ticket)
