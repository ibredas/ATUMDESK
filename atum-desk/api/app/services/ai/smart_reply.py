"""
Smart Reply Suggestions Service
Generates AI-powered response suggestions for tickets
"""
import logging
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime

import requests
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.ticket import Ticket
from app.models.kb_article import KBArticle
from app.config import get_settings

logger = logging.getLogger(__name__)
_settings = get_settings()


class SmartReplyEngine:
    """Generates intelligent reply suggestions for tickets"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def generate_suggestions(
        self,
        ticket: Ticket,
        num_suggestions: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Generate smart reply suggestions for a ticket.
        Combines canned responses, KB articles, and LLM generation.
        """
        suggestions = []
        
        # 1. Get relevant KB articles
        kb_suggestions = await self._get_kb_suggestions(ticket)
        suggestions.extend(kb_suggestions)
        
        # 2. Generate LLM suggestions if enabled
        if _settings.AI_SMARTER_REPLY:
            llm_suggestions = await self._generate_llm_suggestions(ticket)
            suggestions.extend(llm_suggestions)
        
        # 3. Add generic helpful responses
        generic_suggestions = self._get_generic_suggestions(ticket)
        suggestions.extend(generic_suggestions)
        
        # Return top N suggestions
        return suggestions[:num_suggestions]
    
    async def _get_kb_suggestions(
        self,
        ticket: Ticket
    ) -> List[Dict[str, Any]]:
        """Get relevant KB articles as suggestions"""
        text = f"{ticket.subject} {ticket.description}".lower()
        
        # Simple keyword matching (production would use embeddings)
        keywords = []
        if "password" in text or "login" in text:
            keywords.extend(["password", "login", "reset"])
        if "error" in text or "bug" in text:
            keywords.extend(["error", "troubleshoot", "fix"])
        if "install" in text or "setup" in text:
            keywords.extend(["install", "setup", "configuration"])
        
        if not keywords:
            return []
        
        result = await self.db.execute(
            select(KBArticle).where(
                KBArticle.organization_id == ticket.organization_id,
                KBArticle.is_published == True
            ).limit(3)
        )
        articles = result.scalars().all()
        
        suggestions = []
        for article in articles:
            suggestions.append({
                "type": "kb_article",
                "title": article.title,
                "content": article.content[:300] + "..." if len(article.content) > 300 else article.content,
                "article_id": str(article.id),
                "confidence": 0.7
            })
        
        return suggestions
    
    async def _generate_llm_suggestions(
        self,
        ticket: Ticket
    ) -> List[Dict[str, Any]]:
        """Generate suggestions using LLM"""
        prompt = f"""Generate 2 helpful reply suggestions for this support ticket.

Ticket Subject: {ticket.subject}
Ticket Description: {ticket.description[:500]}

Respond with valid JSON array:
[{{"reply": "response text 1"}}, {{"reply": "response text 2"}}]

Keep replies professional, helpful, and under 100 words."""
        
        try:
            response = requests.post(
                f"{_settings.OLLAMA_URL}/api/generate",
                json={
                    "model": _settings.AI_STANDARD_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.5,
                    "num_predict": 300
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                text = result.get("response", "")
                
                # Parse JSON from response
                import json
                try:
                    suggestions_data = json.loads(text)
                    return [
                        {
                            "type": "ai_generated",
                            "reply": s.get("reply", ""),
                            "confidence": 0.8
                        }
                        for s in suggestions_data[:2]
                    ]
                except json.JSONDecodeError:
                    # If not valid JSON, return as single suggestion
                    return [{
                        "type": "ai_generated",
                        "reply": text[:300],
                        "confidence": 0.6
                    }]
        except Exception as e:
            logger.error(f"LLM suggestion generation failed: {e}")
        
        return []
    
    def _get_generic_suggestions(
        self,
        ticket: Ticket
    ) -> List[Dict[str, Any]]:
        """Get generic helpful responses based on ticket content"""
        text = f"{ticket.subject} {ticket.description}".lower()
        suggestions = []
        
        # Add contextual generic suggestions
        if "?" in ticket.subject or "how" in text:
            suggestions.append({
                "type": "generic",
                "reply": "Thank you for reaching out. I'd be happy to help you with this. Could you please provide more details about the issue you're experiencing?",
                "confidence": 0.5
            })
        
        if "urgent" in text or "asap" in text:
            suggestions.append({
                "type": "generic",
                "reply": "I understand this is urgent. Let me prioritize this and look into it immediately. I'll update you as soon as I have more information.",
                "confidence": 0.6
            })
        
        return suggestions


async def get_smart_replies(
    db: AsyncSession,
    ticket: Ticket,
    num_suggestions: int = 3
) -> List[Dict[str, Any]]:
    """Helper function to get smart reply suggestions"""
    engine = SmartReplyEngine(db)
    return await engine.generate_suggestions(ticket, num_suggestions)
