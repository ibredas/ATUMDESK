"""
Ticket Thread Summarization Service
Generates concise summaries of long ticket conversations
"""
import logging
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime

import requests
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.models.comment import Comment
from app.models.ticket import Ticket
from app.config import get_settings

logger = logging.getLogger(__name__)
_settings = get_settings()


class ThreadSummarizer:
    """AI-powered ticket thread summarization"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def summarize_thread(
        self,
        ticket_id: str,
        max_length: int = 200
    ) -> Dict[str, Any]:
        """
        Generate a summary of the ticket conversation thread.
        """
        from uuid import UUID
        try:
            ticket_uuid = UUID(ticket_id)
        except ValueError:
            return {"error": "Invalid ticket ID"}
        
        # Get ticket
        ticket_result = await self.db.execute(
            select(Ticket).where(Ticket.id == ticket_uuid)
        )
        ticket = ticket_result.scalar_one_or_none()
        
        if not ticket:
            return {"error": "Ticket not found"}
        
        # Get all comments ordered by time
        comments_result = await self.db.execute(
            select(Comment).where(
                Comment.ticket_id == ticket_uuid
            ).order_by(desc(Comment.created_at))
        )
        comments = comments_result.scalars().all()
        
        if not comments:
            return {
                "summary": ticket.description[:max_length],
                "message_count": 0
            }
        
        # Build conversation text
        conversation = f"Original Request: {ticket.description}\n\n"
        for i, comment in enumerate(comments[:10]):  # Last 10 comments
            author = "Customer" if not comment.is_internal else "Agent"
            conversation += f"{author}: {comment.content}\n"
        
        # Generate summary using LLM
        if _settings.AI_ENABLED:
            try:
                summary = await self._generate_summary(conversation, max_length)
                return {
                    "summary": summary,
                    "message_count": len(comments),
                    "generated_at": datetime.utcnow().isoformat()
                }
            except Exception as e:
                logger.error(f"Summary generation failed: {e}")
        
        # Fallback: simple truncation
        return {
            "summary": conversation[:max_length] + "...",
            "message_count": len(comments),
            "method": "truncation"
        }
    
    async def _generate_summary(
        self,
        conversation: str,
        max_length: int
    ) -> str:
        """Use LLM to generate summary"""
        prompt = f"""Summarize this support ticket conversation in {max_length} characters or less.
Focus on: what the issue is, current status, and what action is needed.

Conversation:
{conversation[:2000]}

Provide a concise summary:"""
        
        response = requests.post(
            f"{_settings.OLLAMA_URL}/api/generate",
            json={
                "model": _settings.AI_FAST_MODEL,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.3,
                "num_predict": max_length
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "").strip()
        
        return conversation[:max_length]
    
    async def generate_tl_dr(
        self,
        ticket_id: str
    ) -> Dict[str, Any]:
        """Generate a TL;DR for the ticket"""
        result = await self.summarize_thread(ticket_id, max_length=100)
        
        if "error" in result:
            return result
        
        return {
            "tldr": result["summary"],
            "message_count": result.get("message_count", 0)
        }
    
    async def extract_key_points(
        self,
        ticket_id: str
    ) -> List[str]:
        """Extract key points from ticket conversation"""
        from uuid import UUID
        try:
            ticket_uuid = UUID(ticket_id)
        except ValueError:
            return []
        
        ticket_result = await self.db.execute(
            select(Ticket).where(Ticket.id == ticket_uuid)
        )
        ticket = ticket_result.scalar_one_or_none()
        
        if not ticket:
            return []
        
        # Use LLM to extract key points
        prompt = f"""Extract 3-5 key points from this support ticket.
Format as a JSON array of strings.

Ticket:
Subject: {ticket.subject}
Description: {ticket.description[:500]}"""
        
        try:
            response = requests.post(
                f"{_settings.OLLAMA_URL}/api/generate",
                json={
                    "model": _settings.AI_FAST_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                import json
                result = response.json()
                points = json.loads(result.get("response", "[]"))
                if isinstance(points, list):
                    return points
        except Exception as e:
            logger.error(f"Key points extraction failed: {e}")
        
        return []


async def summarize_ticket_thread(
    db: AsyncSession,
    ticket_id: str,
    max_length: int = 200
) -> Dict[str, Any]:
    """Helper function for thread summarization"""
    summarizer = ThreadSummarizer(db)
    return await summarizer.summarize_thread(ticket_id, max_length)


async def extract_ticket_key_points(
    db: AsyncSession,
    ticket_id: str
) -> List[str]:
    """Helper function to extract key points"""
    summarizer = ThreadSummarizer(db)
    return await summarizer.extract_key_points(ticket_id)
