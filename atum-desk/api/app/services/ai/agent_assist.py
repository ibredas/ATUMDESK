"""
Agent Assist Service
Real-time AI assistance for agents while handling tickets
"""
import logging
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime

import requests
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.models.ticket import Ticket, TicketStatus
from app.models.comment import Comment
from app.models.user import User
from app.models.canned_response import CannedResponse
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class AgentAssist:
    """Real-time AI assistance for support agents"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_assist_suggestions(
        self,
        ticket_id: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive assistance suggestions for a ticket.
        Combines multiple AI services for real-time help.
        """
        from uuid import UUID
        try:
            ticket_uuid = UUID(ticket_id)
        except ValueError:
            return {"error": "Invalid ticket ID"}
        
        ticket_result = await self.db.execute(
            select(Ticket).where(Ticket.id == ticket_uuid)
        )
        ticket = ticket_result.scalar_one_or_none()
        
        if not ticket:
            return {"error": "Ticket not found"}
        
        requester_result = await self.db.execute(
            select(User).where(User.id == ticket.requester_id)
        )
        requester = requester_result.scalar_one_or_none()
        
        suggestions = {
            "ticket_id": ticket_id,
            "timestamp": datetime.utcnow().isoformat(),
            "suggestions": []
        }
        
        if ticket.priority.value != "urgent":
            suggestions["suggestions"].append({
                "type": "priority",
                "message": "Consider upgrading priority based on issue type",
                "priority": "low"
            })
        
        if requester:
            count_result = await self.db.execute(
                select(func.count(Ticket.id)).where(
                    Ticket.requester_id == requester.id
                )
            )
            ticket_count = count_result.scalar() or 0
            
            if ticket_count > 10:
                suggestions["suggestions"].append({
                    "type": "context",
                    "message": f"Repeat customer ({ticket_count} previous tickets)",
                    "priority": "medium"
                })
        
        similar = await self._find_similar_tickets(ticket)
        if similar:
            suggestions["suggestions"].append({
                "type": "similar_tickets",
                "message": f"Found {len(similar)} similar resolved tickets",
                "data": similar[:3],
                "priority": "medium"
            })
        
        canned = await self._suggest_canned_responses(ticket)
        if canned:
            suggestions["suggestions"].append({
                "type": "canned_response",
                "message": f"Matching canned responses: {', '.join([r['title'] for r in canned[:2]])}",
                "data": canned,
                "priority": "high"
            })
        
        kb_suggestions = await self._get_kb_suggestions(ticket)
        if kb_suggestions:
            suggestions["suggestions"].append({
                "type": "knowledge_base",
                "message": f"Found {len(kb_suggestions)} relevant KB articles",
                "data": kb_suggestions[:2],
                "priority": "high"
            })
        
        if ticket.sla_due_at:
            hours_left = (ticket.sla_due_at - datetime.utcnow()).total_seconds() / 3600
            if hours_left < 4 and ticket.status != TicketStatus.RESOLVED:
                suggestions["suggestions"].append({
                    "type": "sla_warning",
                    "message": f"SLA due in {hours_left:.1f} hours",
                    "priority": "high"
                })
        
        if context and settings.AI_SMARTER_REPLY:
            ai_reply = await self._generate_response_suggestion(ticket, context)
            if ai_reply:
                suggestions["suggestions"].append({
                    "type": "ai_reply",
                    "message": "AI suggests the following response:",
                    "data": {"suggested_reply": ai_reply},
                    "priority": "high"
                })
        
        return suggestions
    
    async def _find_similar_tickets(self, ticket: Ticket) -> List[Dict[str, Any]]:
        keywords = []
        text = f"{ticket.subject} {ticket.description}".lower()
        
        important_words = ["password", "login", "error", "install", "network", "email", "software"]
        keywords = [w for w in important_words if w in text]
        
        if not keywords:
            return []
        
        result = await self.db.execute(
            select(Ticket).where(
                and_(
                    Ticket.organization_id == ticket.organization_id,
                    Ticket.status == TicketStatus.RESOLVED,
                    Ticket.id != ticket.id
                )
            ).limit(5)
        )
        
        similar = []
        for t in result.scalars():
            t_text = f"{t.subject} {t.description}".lower()
            if any(kw in t_text for kw in keywords):
                similar.append({
                    "id": str(t.id),
                    "subject": t.subject,
                    "resolution": t.description[:200]
                })
        
        return similar
    
    async def _suggest_canned_responses(self, ticket: Ticket) -> List[Dict[str, Any]]:
        text = f"{ticket.subject} {ticket.description}".lower()
        
        result = await self.db.execute(
            select(CannedResponse).where(
                CannedResponse.organization_id == ticket.organization_id,
                CannedResponse.is_active == True
            ).limit(10)
        )
        
        responses = result.scalars().all()
        
        scored = []
        for resp in responses:
            resp_text = f"{resp.title} {resp.content}".lower()
            matches = sum(1 for kw in ["password", "error", "install", "help", "thank", "sorry"] if kw in resp_text)
            if matches > 0:
                scored.append((resp, matches))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        
        return [
            {
                "id": str(r.id),
                "title": r.title,
                "content": r.content[:200]
            }
            for r, _ in scored[:3]
        ]
    
    async def _get_kb_suggestions(self, ticket: Ticket) -> List[Dict[str, Any]]:
        from app.models.kb_article import KBArticle
        
        text = f"{ticket.subject} {ticket.description}".lower()
        keywords = [w for w in ["password", "setup", "error", "install", "network"] if w in text]
        
        if not keywords:
            return []
        
        result = await self.db.execute(
            select(KBArticle).where(
                KBArticle.organization_id == ticket.organization_id,
                KBArticle.is_published == True
            ).limit(5)
        )
        
        articles = []
        for a in result.scalars():
            a_text = f"{a.title} {a.content}".lower()
            if any(kw in a_text for kw in keywords):
                articles.append({
                    "id": str(a.id),
                    "title": a.title,
                    "excerpt": a.content[:150]
                })
        
        return articles
    
    async def _generate_response_suggestion(self, ticket: Ticket, context: str) -> Optional[str]:
        prompt = f"""Generate a helpful, professional response to this support ticket.

Ticket Subject: {ticket.subject}
Ticket: {ticket.description[:500]}

Agent's current reply context: {context}

Generate a completion or suggestion for the agent's response:"""
        
        try:
            response = requests.post(
                f"{settings.OLLAMA_URL}/api/generate",
                json={
                    "model": settings.AI_STANDARD_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.5,
                    "num_predict": 200
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
        except Exception as e:
            logger.error(f"AI suggestion failed: {e}")
        
        return None
    
    async def get_quick_actions(self, ticket_id: str) -> Dict[str, Any]:
        from uuid import UUID
        try:
            ticket_uuid = UUID(ticket_id)
        except ValueError:
            return {"error": "Invalid ticket ID"}
        
        result = await self.db.execute(
            select(Ticket).where(Ticket.id == ticket_uuid)
        )
        ticket = result.scalar_one_or_none()
        
        if not ticket:
            return {"error": "Ticket not found"}
        
        actions = []
        
        if ticket.status == TicketStatus.WAITING_CUSTOMER:
            actions.append({
                "action": "close_waiting",
                "label": "Close - Customer Waiting",
                "priority": "medium"
            })
        
        if ticket.priority.value in ["high", "urgent"] and ticket.escalation_level < 2:
            actions.append({
                "action": "escalate",
                "label": "Escalate Ticket",
                "priority": "high"
            })
        
        if not ticket.assigned_to:
            actions.append({
                "action": "assign",
                "label": "Assign to Me",
                "priority": "high"
            })
        
        return {
            "ticket_id": ticket_id,
            "actions": actions
        }


async def get_agent_assist(db: AsyncSession, ticket_id: str, context: Optional[str] = None) -> Dict[str, Any]:
    assist = AgentAssist(db)
    return await assist.get_assist_suggestions(ticket_id, context)


async def get_quick_actions(db: AsyncSession, ticket_id: str) -> Dict[str, Any]:
    assist = AgentAssist(db)
    return await assist.get_quick_actions(ticket_id)
