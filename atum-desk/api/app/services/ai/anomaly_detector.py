"""
Anomaly Detection Service
Detects unusual patterns in ticket data
"""
import logging
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.ticket import Ticket, TicketStatus, TicketPriority
from app.models.user import User
from app.config import get_settings

logger = logging.getLogger(__name__)
_settings = get_settings()


class AnomalyDetector:
    """Detects anomalous patterns in ticket data"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def detect_ticket_anomalies(
        self,
        organization_id: UUID,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Detect anomalies in ticket patterns for an organization.
        """
        since = datetime.utcnow() - timedelta(days=days)
        
        # Get ticket statistics
        stats = await self._get_ticket_stats(organization_id, since)
        
        # Get historical baseline (30 days before)
        historical_since = since - timedelta(days=30)
        historical_stats = await self._get_ticket_stats(organization_id, historical_since)
        
        anomalies = []
        
        # Check for volume anomaly
        if stats["total_tickets"] > historical_stats["avg_daily"] * 2:
            anomalies.append({
                "type": "volume_spike",
                "severity": "high",
                "message": f"Ticket volume 2x higher than average",
                "details": {
                    "current": stats["total_tickets"],
                    "historical_avg": historical_stats["avg_daily"]
                },
                "recommendation": "Consider scaling support team or investigating root cause"
            })
        
        # Check for priority distribution anomaly
        urgent_pct = stats["urgent_pct"]
        if urgent_pct > 30:
            anomalies.append({
                "type": "high_urgent_rate",
                "severity": "medium",
                "message": f"High volume of urgent tickets ({urgent_pct}%)",
                "recommendation": "Review urgent ticket categorization for accuracy"
            })
        
        # Check for unassigned tickets backlog
        if stats["unassigned_count"] > 20:
            anomalies.append({
                "type": "backlog",
                "severity": "high",
                "message": f"{stats['unassigned_count']} tickets unassigned",
                "recommendation": "Enable auto-assignment or add capacity"
            })
        
        # Check for SLA breach pattern
        if stats["breached_count"] > 5:
            anomalies.append({
                "type": "sla_breaches",
                "severity": "high",
                "message": f"{stats['breached_count']} SLA breaches in {days} days",
                "recommendation": "Review SLA policies and team capacity"
            })
        
        # Check for response time anomaly
        if stats["avg_response_hours"] > 24:
            anomalies.append({
                "type": "slow_response",
                "severity": "medium",
                "message": f"Average response time: {stats['avg_response_hours']:.1f}h",
                "recommendation": "Review agent workload distribution"
            })
        
        return {
            "anomalies": anomalies,
            "anomaly_count": len(anomalies),
            "period_days": days,
            "severity_counts": {
                "high": len([a for a in anomalies if a["severity"] == "high"]),
                "medium": len([a for a in anomalies if a["severity"] == "medium"])
            }
        }
    
    async def _get_ticket_stats(
        self,
        organization_id: UUID,
        since: datetime
    ) -> Dict[str, Any]:
        """Get ticket statistics for a period"""
        # Total tickets
        total_result = await self.db.execute(
            select(func.count(Ticket.id)).where(
                and_(
                    Ticket.organization_id == organization_id,
                    Ticket.created_at >= since
                )
            )
        )
        total_tickets = total_result.scalar() or 0
        
        # By priority
        priority_result = await self.db.execute(
            select(Ticket.priority, func.count(Ticket.id)).where(
                and_(
                    Ticket.organization_id == organization_id,
                    Ticket.created_at >= since
                )
            ).group_by(Ticket.priority)
        )
        priority_counts = {str(p): c for p, c in priority_result.fetchall()}
        
        # Unassigned count
        unassigned_result = await self.db.execute(
            select(func.count(Ticket.id)).where(
                and_(
                    Ticket.organization_id == organization_id,
                    Ticket.created_at >= since,
                    Ticket.assigned_to.is_(None),
                    Ticket.status.in_([TicketStatus.NEW, TicketStatus.ASSIGNED])
                )
            )
        )
        unassigned_count = unassigned_result.scalar() or 0
        
        # Breached count
        breached_result = await self.db.execute(
            select(func.count(Ticket.id)).where(
                and_(
                    Ticket.organization_id == organization_id,
                    Ticket.created_at >= since,
                    Ticket.sla_due_at < datetime.utcnow(),
                    Ticket.status.in_([TicketStatus.NEW, TicketStatus.IN_PROGRESS, TicketStatus.ASSIGNED])
                )
            )
        )
        breached_count = breached_result.scalar() or 0
        
        days_span = max(1, (datetime.utcnow() - since).days)
        
        return {
            "total_tickets": total_tickets,
            "avg_daily": total_tickets / days_span,
            "priority_counts": priority_counts,
            "urgent_pct": (priority_counts.get("urgent", 0) / max(1, total_tickets)) * 100,
            "unassigned_count": unassigned_count,
            "breached_count": breached_count,
            "avg_response_hours": 18.5  # Placeholder - would calculate from actual data
        }
    
    async def detect_agent_anomalies(
        self,
        organization_id: UUID,
        days: int = 7
    ) -> Dict[str, Any]:
        """Detect anomalies in agent performance"""
        since = datetime.utcnow() - timedelta(days=days)
        
        # Get agent ticket counts
        result = await self.db.execute(
            select(
                User.id,
                User.full_name,
                func.count(Ticket.id).label("ticket_count")
            ).join(
                Ticket, Ticket.assigned_to == User.id
            ).where(
                and_(
                    User.organization_id == organization_id,
                    Ticket.created_at >= since
                )
            ).group_by(User.id, User.full_name)
        )
        
        agent_stats = []
        for user_id, name, count in result.fetchall():
            agent_stats.append({
                "agent_id": str(user_id),
                "name": name,
                "tickets": count
            })
        
        if not agent_stats:
            return {"anomalies": [], "message": "No agent data available"}
        
        # Calculate average
        avg_tickets = sum(a["tickets"] for a in agent_stats) / len(agent_stats)
        
        anomalies = []
        
        # Find overloaded agents
        for agent in agent_stats:
            if agent["tickets"] > avg_tickets * 2:
                anomalies.append({
                    "type": "agent_overload",
                    "severity": "high",
                    "agent_id": agent["agent_id"],
                    "agent_name": agent["name"],
                    "ticket_count": agent["tickets"],
                    "recommendation": f"Consider reassigning some tickets from {agent['name']}"
                })
            
            if agent["tickets"] < avg_tickets * 0.2:
                anomalies.append({
                    "type": "agent_underutilized",
                    "severity": "low",
                    "agent_id": agent["agent_id"],
                    "agent_name": agent["name"],
                    "ticket_count": agent["tickets"],
                    "recommendation": f"Check if {agent['name']} needs more tickets assigned"
                })
        
        return {
            "anomalies": anomalies,
            "agent_count": len(agent_stats),
            "avg_tickets_per_agent": round(avg_tickets, 1)
        }


async def detect_anomalies(
    db: AsyncSession,
    organization_id: UUID,
    days: int = 7
) -> Dict[str, Any]:
    """Helper function for anomaly detection"""
    detector = AnomalyDetector(db)
    ticket_anomalies = await detector.detect_ticket_anomalies(organization_id, days)
    agent_anomalies = await detector.detect_agent_anomalies(organization_id, days)
    
    return {
        **ticket_anomalies,
        "agent_anomalies": agent_anomalies["anomalies"]
    }
