"""
Auto-KB Article Generator
Automatically creates KB articles from resolved tickets
"""
import logging
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime, timedelta

import requests
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.ticket import Ticket, TicketStatus
from app.models.comment import Comment
from app.models.kb_article import KBArticle
from app.models.kb_category import KBCategory
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class AutoKBGenerator:
    """Automatically generates KB articles from resolved tickets"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def suggest_kb_articles(
        self,
        organization_id: UUID,
        min_tickets: int = 3,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Analyze resolved tickets and suggest KB article topics.
        """
        since = datetime.utcnow() - timedelta(days=days)
        
        # Get resolved tickets
        result = await self.db.execute(
            select(Ticket).where(
                and_(
                    Ticket.organization_id == organization_id,
                    Ticket.status == TicketStatus.RESOLVED,
                    Ticket.resolved_at >= since
                )
            ).order_by(Ticket.resolved_at.desc())
        )
        tickets = result.scalars().all()
        
        if len(tickets) < min_tickets:
            return []
        
        # Group similar tickets by subject keywords
        topic_groups = self._group_by_topics(tickets)
        
        suggestions = []
        for topic, topic_tickets in topic_groups.items():
            if len(topic_tickets) >= min_tickets:
                # Generate KB suggestion
                suggestion = await self._generate_kb_suggestion(topic, topic_tickets)
                if suggestion:
                    suggestions.append(suggestion)
        
        return suggestions[:10]  # Top 10
    
    def _group_by_topics(
        self,
        tickets: List[Ticket]
    ) -> Dict[str, List[Ticket]]:
        """Group tickets by topic keywords"""
        topics = {}
        
        topic_keywords = {
            "password": ["password", "reset", "login", "access"],
            "email": ["email", "mail", "outlook", "gmail"],
            "network": ["wifi", "internet", "network", "vpn", "connection"],
            "software": ["install", "software", "app", "application"],
            "hardware": ["laptop", "computer", "monitor", "printer", "device"],
            "billing": ["invoice", "payment", "charge", "bill"]
        }
        
        for ticket in tickets:
            text = f"{ticket.subject} {ticket.description}".lower()
            matched = False
            
            for topic, keywords in topic_keywords.items():
                if any(kw in text for kw in keywords):
                    if topic not in topics:
                        topics[topic] = []
                    topics[topic].append(ticket)
                    matched = True
                    break
            
            if not matched:
                if "other" not in topics:
                    topics["other"] = []
                topics["other"].append(ticket)
        
        return topics
    
    async def _generate_kb_suggestion(
        self,
        topic: str,
        tickets: List[Ticket]
    ) -> Optional[Dict[str, Any]]:
        """Generate a KB article suggestion from tickets"""
        # Get ticket descriptions for context
        descriptions = [t.description[:300] for t in tickets[:5]]
        combined_text = "\n\n".join(descriptions)
        
        if not settings.AI_ENABLED:
            return {
                "topic": topic,
                "ticket_count": len(tickets),
                "suggested_title": topic.title(),
                "suggested_content": combined_text[:500]
            }
        
        # Use LLM to generate article
        prompt = f"""Generate a helpful KB article based on these support ticket descriptions.
Create a clear title and comprehensive answer that addresses the common issue.

Ticket Descriptions:
{combined_text[:1500]}

Respond with valid JSON:
{{"title": "Article Title", "summary": "Brief overview"}}"""
        
        try:
            response = requests.post(
                f"{settings.OLLAMA_URL}/api/generate",
                json={
                    "model": settings.AI_STANDARD_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                    "temperature": 0.3
                },
                timeout=60
            )
            
            if response.status_code == 200:
                import json
                result = response.json()
                article_data = json.loads(result.get("response", "{}"))
                
                return {
                    "topic": topic,
                    "ticket_count": len(tickets),
                    "suggested_title": article_data.get("title", topic.title()),
                    "suggested_summary": article_data.get("summary", ""),
                    "confidence": 0.7
                }
        except Exception as e:
            logger.error(f"KB generation failed: {e}")
        
        return {
            "topic": topic,
            "ticket_count": len(tickets),
            "suggested_title": topic.title(),
            "confidence": 0.5
        }
    
    async def create_kb_from_ticket(
        self,
        ticket_id: str,
        title: str,
        category_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Create a KB article from a resolved ticket"""
        from uuid import UUID
        try:
            ticket_uuid = UUID(ticket_id)
        except ValueError:
            return None
        
        # Get ticket and comments
        ticket_result = await self.db.execute(
            select(Ticket).where(Ticket.id == ticket_uuid)
        )
        ticket = ticket_result.scalar_one_or_none()
        
        if not ticket:
            return None
        
        # Get resolution comments
        comments_result = await self.db.execute(
            select(Comment).where(
                Comment.ticket_id == ticket_uuid,
                Comment.is_internal == False
            ).order_by(Comment.created_at)
        )
        comments = comments_result.scalars().all()
        
        # Build article content
        content = f"## Issue\n{ticket.description}\n\n## Resolution\n"
        for comment in comments:
            if "resolved" in comment.content.lower() or "fix" in comment.content.lower():
                content += f"{comment.content}\n\n"
        
        # Get category
        category = None
        if category_id:
            category = await self.db.get(KBCategory, UUID(category_id))
        
        # Create KB article
        article = KBArticle(
            organization_id=ticket.organization_id,
            title=title or f"How to: {ticket.subject}",
            content=content[:5000],
            category_id=UUID(category_id) if category_id else None,
            is_published=False,
            created_by=ticket.assigned_to
        )
        
        self.db.add(article)
        await self.db.commit()
        await self.db.refresh(article)
        
        return {
            "article_id": str(article.id),
            "title": article.title,
            "created": True
        }


async def suggest_kb_topics(
    db: AsyncSession,
    organization_id: UUID,
    min_tickets: int = 3
) -> List[Dict[str, Any]]:
    """Helper function for KB suggestions"""
    generator = AutoKBGenerator(db)
    return await generator.suggest_kb_articles(organization_id, min_tickets)
