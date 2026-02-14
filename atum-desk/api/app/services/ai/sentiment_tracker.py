"""
Customer Sentiment Tracking Service
Tracks sentiment trends for customers over time
"""
import logging
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.ticket import Ticket
from app.models.user import User
from app.models.comment import Comment
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class SentimentTracker:
    """Tracks and analyzes customer sentiment over time"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_customer_sentiment_profile(
        self,
        user_id: UUID
    ) -> Dict[str, Any]:
        """
        Get sentiment profile for a customer.
        """
        # Get all tickets for this user
        result = await self.db.execute(
            select(Ticket).where(
                Ticket.requester_id == user_id
            ).order_by(Ticket.created_at.desc())
        )
        tickets = result.scalars().all()
        
        if not tickets:
            return {
                "total_tickets": 0,
                "sentiment_profile": "neutral",
                "message": "No ticket history"
            }
        
        # Calculate sentiment distribution
        sentiment_counts = defaultdict(int)
        recent_trend = []
        
        for ticket in tickets:
            # Store sentiment data (would be populated by sentiment analysis job)
            sentiment = getattr(ticket, 'sentiment_score', None) or 0
            if sentiment > 0.2:
                sentiment_counts["positive"] += 1
            elif sentiment < -0.2:
                sentiment_counts["negative"] += 1
            else:
                sentiment_counts["neutral"] += 1
            
            recent_trend.append(sentiment)
        
        # Calculate overall profile
        total = len(tickets)
        positive_pct = (sentiment_counts["positive"] / total) * 100
        negative_pct = (sentiment_counts["negative"] / total) * 100
        
        if negative_pct > 40:
            profile = "frustrated"
        elif positive_pct > 60:
            profile = "satisfied"
        else:
            profile = "neutral"
        
        # Calculate trend
        trend = "stable"
        if len(recent_trend) >= 5:
            first_half = sum(recent_trend[:len(recent_trend)//2]) / (len(recent_trend)//2)
            second_half = sum(recent_trend[len(recent_trend)//2:]) / (len(recent_trend) - len(recent_trend)//2)
            if second_half > first_half + 0.2:
                trend = "improving"
            elif second_half < first_half - 0.2:
                trend = "declining"
        
        return {
            "customer_id": str(user_id),
            "total_tickets": total,
            "sentiment_profile": profile,
            "distribution": dict(sentiment_counts),
            "trend": trend,
            "recommendation": self._get_recommendation(profile, trend)
        }
    
    def _get_recommendation(self, profile: str, trend: str) -> str:
        """Get action recommendation based on profile"""
        if profile == "frustrated":
            return "Priority handling recommended - consider direct contact"
        elif trend == "declining":
            return "Customer satisfaction declining - review recent interactions"
        elif profile == "satisfied" and trend == "improving":
            return "Consider for customer loyalty program"
        return "Standard handling"
    
    async def get_org_sentiment_summary(
        self,
        organization_id: UUID,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get overall sentiment summary for an organization.
        """
        since = datetime.utcnow() - timedelta(days=days)
        
        result = await self.db.execute(
            select(
                func.count(Ticket.id).label("total"),
                func.avg(Ticket.priority).label("avg_priority")
            ).where(
                and_(
                    Ticket.organization_id == organization_id,
                    Ticket.created_at >= since
                )
            )
        )
        stats = result.one()
        
        # Get unique customers
        customers_result = await self.db.execute(
            select(func.count(func.distinct(Ticket.requester_id))).where(
                and_(
                    Ticket.organization_id == organization_id,
                    Ticket.created_at >= since
                )
            )
        )
        unique_customers = customers_result.scalar() or 0
        
        # Sentiment distribution (mock for now - would be from actual sentiment data)
        return {
            "period_days": days,
            "total_tickets": stats.total or 0,
            "unique_customers": unique_customers,
            "sentiment_distribution": {
                "positive": int((stats.total or 0) * 0.4),
                "neutral": int((stats.total or 0) * 0.4),
                "negative": int((stats.total or 0) * 0.2)
            },
            "satisfaction_score": 72.5,  # Would be calculated from CSAT + sentiment
            "trend": "stable"
        }
    
    async def get_sentiment_trend(
        self,
        organization_id: UUID,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get daily sentiment trend data.
        """
        trends = []
        
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=days-i-1)
            date_str = date.strftime("%Y-%m-%d")
            
            # Mock data - in production would query actual sentiment scores
            base_score = 0.1
            variation = (i % 7 - 3) * 0.05
            
            trends.append({
                "date": date_str,
                "sentiment_score": round(base_score + variation, 2),
                "ticket_count": 10 + (i % 5) * 2,
                "avg_resolution_hours": 18 + (i % 10)
            })
        
        return trends


async def get_customer_profile(
    db: AsyncSession,
    user_id: UUID
) -> Dict[str, Any]:
    """Helper function for customer sentiment profile"""
    tracker = SentimentTracker(db)
    return await tracker.get_customer_sentiment_profile(user_id)


async def get_org_sentiment(
    db: AsyncSession,
    organization_id: UUID,
    days: int = 30
) -> Dict[str, Any]:
    """Helper function for organization sentiment"""
    tracker = SentimentTracker(db)
    return await tracker.get_org_sentiment_summary(organization_id, days)
