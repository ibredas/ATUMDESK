"""
Smart Auto-Assignment Service - AI-Powered Ticket Routing
"""
import logging
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ticket import Ticket, TicketPriority, TicketStatus
from app.models.user import User, UserRole

logger = logging.getLogger(__name__)


class SmartAssignmentEngine:
    """
    AI-powered ticket assignment engine.
    Assigns tickets to the best available agent based on:
    - Current workload
    - Historical performance
    - Priority matching
    - Skills/categories
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def find_best_agent(
        self,
        ticket_priority: str,
        organization_id: UUID,
        ticket_category: Optional[str] = None,
    ) -> Optional[User]:
        """
        Find the best available agent for a ticket.
        Returns None if no suitable agent found.
        """
        # Get all active agents in org
        agents_result = await self.db.execute(
            select(User).where(
                and_(
                    User.organization_id == organization_id,
                    User.is_active == True,
                    User.role.in_([UserRole.AGENT, UserRole.MANAGER])
                )
            )
        )
        agents = agents_result.scalars().all()
        
        if not agents:
            logger.warning(f"No agents found for org {organization_id}")
            return None
        
        # Score each agent
        agent_scores = []
        for agent in agents:
            score = await self._calculate_agent_score(
                agent=agent,
                ticket_priority=ticket_priority,
                ticket_category=ticket_category,
                organization_id=organization_id
            )
            agent_scores.append((agent, score))
        
        # Sort by score (highest first)
        agent_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return best agent
        best_agent = agent_scores[0][0] if agent_scores else None
        logger.info(f"Smart assignment: selected agent {best_agent.email if best_agent else 'None'}")
        
        return best_agent
    
    async def _calculate_agent_score(
        self,
        agent: User,
        ticket_priority: str,
        ticket_category: Optional[str],
        organization_id: UUID
    ) -> float:
        """
        Calculate agent suitability score (0-100).
        """
        score = 50.0  # Base score
        
        # Factor 1: Current workload (40% weight)
        workload_score = await self._get_workload_score(agent.id, organization_id)
        score += workload_score * 0.4
        
        # Factor 2: Performance history (30% weight)
        perf_score = await self._get_performance_score(agent.id, organization_id)
        score += perf_score * 0.3
        
        # Factor 3: Priority handling (20% weight)
        priority_score = self._get_priority_match_score(agent, ticket_priority)
        score += priority_score * 0.2
        
        # Factor 4: Availability (10% weight)
        # Check if agent is currently locked/assigned many tickets
        availability_score = 1.0 if workload_score < 30 else 0.5
        score += availability_score * 0.1
        
        return min(100.0, max(0.0, score))
    
    async def _get_workload_score(self, agent_id: UUID, org_id: UUID) -> float:
        """Get workload score - fewer open tickets = higher score."""
        result = await self.db.execute(
            select(func.count(Ticket.id)).where(
                and_(
                    Ticket.assigned_to == agent_id,
                    Ticket.organization_id == org_id,
                    Ticket.status.in_([TicketStatus.NEW, TicketStatus.IN_PROGRESS])
                )
            )
        )
        open_tickets = result.scalar() or 0
        
        # Fewer tickets = higher score
        if open_tickets == 0:
            return 100.0
        elif open_tickets <= 3:
            return 80.0
        elif open_tickets <= 7:
            return 60.0
        elif open_tickets <= 15:
            return 40.0
        else:
            return 20.0
    
    async def _get_performance_score(self, agent_id: UUID, org_id: UUID) -> float:
        """Get performance score based on resolution history."""
        # Get tickets resolved in last 30 days
        since = datetime.utcnow() - timedelta(days=30)
        result = await self.db.execute(
            select(func.count(Ticket.id)).where(
                and_(
                    Ticket.assigned_to == agent_id,
                    Ticket.organization_id == org_id,
                    Ticket.status == TicketStatus.RESOLVED,
                    Ticket.updated_at >= since
                )
            )
        )
        resolved = result.scalar() or 0
        
        # Score based on resolution count
        if resolved >= 50:
            return 100.0
        elif resolved >= 30:
            return 85.0
        elif resolved >= 15:
            return 70.0
        elif resolved >= 5:
            return 55.0
        else:
            return 40.0
    
    def _get_priority_match_score(self, agent: User, ticket_priority: str) -> float:
        """Check if agent is suitable for priority level."""
        # Higher role = better for urgent
        if ticket_priority == "urgent":
            if agent.role == UserRole.ADMIN:
                return 100.0
            elif agent.role == UserRole.MANAGER:
                return 85.0
            else:
                return 70.0
        elif ticket_priority == "high":
            return 80.0
        else:
            return 70.0
    
    async def auto_assign_ticket(self, ticket: Ticket) -> bool:
        """
        Automatically assign a ticket to the best agent.
        Returns True if assigned, False otherwise.
        """
        if ticket.assigned_to:
            logger.info(f"Ticket {ticket.id} already assigned")
            return False
        
        best_agent = await self.find_best_agent(
            ticket_priority=ticket.priority.value if hasattr(ticket.priority, 'value') else str(ticket.priority),
            ticket_category=None,
            organization_id=ticket.organization_id
        )
        
        if best_agent:
            ticket.assigned_to = best_agent.id
            ticket.status = TicketStatus.IN_PROGRESS
            ticket.updated_at = datetime.utcnow()
            await self.db.commit()
            logger.info(f"Auto-assigned ticket {ticket.id} to {best_agent.email}")
            return True
        
        return False


async def smart_assign_ticket(db: AsyncSession, ticket: Ticket) -> bool:
    """Helper function for smart ticket assignment."""
    engine = SmartAssignmentEngine(db)
    return await engine.auto_assign_ticket(ticket)
