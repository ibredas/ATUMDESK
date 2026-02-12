"""
Smart Reply System - AI-Powered Response Suggestions
Generates contextual responses based on ticket content and history
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from enum import Enum

from src.domain.entities import TicketId, UserId


class ReplyTone(Enum):
    """Tone options for generated replies"""
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    EMPATHETIC = "empathetic"
    TECHNICAL = "technical"
    APOLOGETIC = "apologetic"
    ASSERTIVE = "assertive"


class ReplyType(Enum):
    """Types of smart replies"""
    ACKNOWLEDGMENT = "acknowledgment"  # "We received your ticket..."
    RESOLUTION = "resolution"           # Solution to the problem
    CLARIFICATION = "clarification"     # Asking for more info
    UPDATE = "update"                   # Status update
    ESCALATION = "escalation"          # Escalating to higher tier
    FOLLOW_UP = "follow_up"            # Checking if resolved
    CLOSURE = "closure"                # Closing the ticket


@dataclass
class ReplyTemplate:
    """Template for smart replies"""
    id: UUID = field(default_factory=uuid4)
    organization_id: Optional[UUID] = None
    name: str = ""
    reply_type: ReplyType = ReplyType.ACKNOWLEDGMENT
    tone: ReplyTone = ReplyTone.PROFESSIONAL
    template: str = ""  # Template with placeholders like {{customer_name}}
    variables: List[str] = field(default_factory=list)
    category: str = ""  # e.g., "password_reset", "bug_report"
    tags: List[str] = field(default_factory=list)
    is_ai_generated: bool = False
    usage_count: int = 0
    success_rate: float = 0.0  # % of times it resolved the ticket
    created_by: Optional[UserId] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def render(self, variables: Dict[str, str]) -> str:
        """Render template with variables"""
        result = self.template
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, str(value))
        return result
    
    def record_usage(self, was_successful: bool):
        """Record template usage and update success rate"""
        self.usage_count += 1
        # Update success rate with exponential moving average
        alpha = 0.1  # Smoothing factor
        success = 1.0 if was_successful else 0.0
        self.success_rate = (self.success_rate * (1 - alpha)) + (success * alpha)
        self.updated_at = datetime.utcnow()


@dataclass
class GeneratedReply:
    """AI-generated reply suggestion"""
    id: UUID = field(default_factory=uuid4)
    ticket_id: TicketId = field(default=None)
    reply_type: ReplyType = ReplyType.ACKNOWLEDGMENT
    tone: ReplyTone = ReplyTone.PROFESSIONAL
    content: str = ""
    confidence_score: float = 0.0  # 0.0 - 1.0
    
    # Source tracking
    generated_by: str = "ai"  # "ai", "template", "hybrid"
    template_id: Optional[UUID] = None
    ai_model: str = "ATUM-DESK-AI"
    
    # Context
    context_used: Dict[str, Any] = field(default_factory=dict)
    similar_tickets: List[TicketId] = field(default_factory=list)
    kb_articles_suggested: List[UUID] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def is_high_confidence(self) -> bool:
        """Check if reply has high confidence"""
        return self.confidence_score >= 0.8
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "ticket_id": str(self.ticket_id),
            "reply_type": self.reply_type.value,
            "tone": self.tone.value,
            "content": self.content,
            "confidence_score": self.confidence_score,
            "generated_by": self.generated_by,
            "similar_tickets": [str(t) for t in self.similar_tickets],
            "kb_articles": [str(k) for k in self.kb_articles_suggested],
        }


@dataclass
class SmartReplyConfig:
    """Configuration for smart reply system"""
    organization_id: Optional[UUID] = None
    
    # AI Settings
    enabled: bool = True
    ai_model: str = "ATUM-DESK-AI"
    min_confidence_threshold: float = 0.6
    max_suggestions: int = 3
    
    # Tone preferences
    default_tone: ReplyTone = ReplyTone.PROFESSIONAL
    allowed_tones: List[ReplyTone] = field(default_factory=lambda: [
        ReplyTone.PROFESSIONAL,
        ReplyTone.FRIENDLY,
        ReplyTone.EMPATHETIC,
    ])
    
    # Auto-reply settings
    enable_auto_reply: bool = False
    auto_reply_threshold: float = 0.95  # Only auto-reply if confidence > 95%
    auto_reply_types: List[ReplyType] = field(default_factory=lambda: [
        ReplyType.ACKNOWLEDGMENT,
    ])
    
    # Learning
    enable_learning: bool = True
    track_reply_effectiveness: bool = True
    
    # Templates
    use_templates: bool = True
    prioritize_templates: bool = False
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


class SmartReplyEngine:
    """
    Engine for generating smart reply suggestions
    Combines AI generation with template matching
    """
    
    def __init__(self, config: SmartReplyConfig):
        self.config = config
    
    async def generate_replies(
        self,
        ticket_content: str,
        ticket_history: List[Dict[str, Any]],
        customer_info: Dict[str, Any],
        tone: Optional[ReplyTone] = None,
        organization_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate comprehensive AI assistance: Replies, RAG Context, Sentiment.
        Returns a Dict with 'suggestions', 'sentiment', 'similar_tickets'.
        """
        if not self.config.enabled:
            return {}
        
        tone = tone or self.config.default_tone
        
        # 1. Concurrent Execution: Sentiment + RAG
        import asyncio
        from app.services.ai.sentiment import analyze_sentiment
        from app.services.rag.retriever import search_similar_tickets
        
        tasks = [
            analyze_sentiment(ticket_content),
        ]
        
        if organization_id:
            tasks.append(search_similar_tickets(ticket_content, organization_id, limit=3))
        else:
            tasks.append(asyncio.sleep(0)) # No-op
            
        results = await asyncio.gather(*tasks)
        sentiment_result = results[0]
        similar_docs = results[1] if organization_id else []
        
        # 2. Generate Reply using RAG Context
        # Construct Context Filtered from RAG
        rag_context = "\n".join([f"- {d.page_content}" for d in similar_docs])
        
        from langchain_ollama import ChatOllama
        from langchain_core.prompts import ChatPromptTemplate
        
        llm = ChatOllama(
            model=self.config.ai_model,
            base_url="http://localhost:11434", # Should use settings
            temperature=0.7,
        )
        
        prompt = ChatPromptTemplate.from_template("""
        You are a helpful support agent.
        Customer: {customer_name}
        Ticket: {ticket_content}
        Tone: {tone}
        
        Relevant Past Tickets/KB:
        {rag_context}
        
        Draft a short, helpful response.
        """)
        
        reply_chain = prompt | llm
        
        try:
            ai_reply_text = await reply_chain.ainvoke({
                "customer_name": customer_info.get("name", "Customer"),
                "ticket_content": ticket_content,
                "tone": tone.value,
                "rag_context": rag_context
            })
            
            # Extract string if it's a generic object (ChatOllama returns AIMessage usually, but invoke returns text string sometimes or AIMessage)
            # chain.invoke returns AIMessage. content attribute has str.
            content = ai_reply_text.content if hasattr(ai_reply_text, 'content') else str(ai_reply_text)
            
        except Exception:
            content = "AI generation failed."

        # 3. Assemble Response
        return {
            "sentiment": sentiment_result.dict(),
            "similar_tickets": [{"content": d.page_content, "metadata": d.metadata} for d in similar_docs],
            "reply_suggestion": GeneratedReply(
                content=content,
                confidence_score=sentiment_result.score, # Proxy
                tone=tone,
                reply_type=ReplyType.Resolution # Assume resolution
            )
        }
    
    async def analyze_reply_effectiveness(
        self,
        reply_id: UUID,
        ticket_resolution_time: float,
        customer_satisfaction: Optional[int],
        ticket_reopened: bool,
    ) -> Dict[str, Any]:
        """
        Analyze how effective a reply was
        
        Returns effectiveness metrics
        """
        metrics = {
            "reply_id": str(reply_id),
            "resolution_time": ticket_resolution_time,
            "satisfaction": customer_satisfaction,
            "reopened": ticket_reopened,
        }
        
        # Calculate effectiveness score
        score = 0.5  # Base score
        
        if customer_satisfaction:
            score += (customer_satisfaction / 5.0) * 0.3
        
        if not ticket_reopened:
            score += 0.2
        
        # Resolution time factor (faster is better)
        if ticket_resolution_time < 3600:  # Less than 1 hour
            score += 0.1
        
        metrics["effectiveness_score"] = min(score, 1.0)
        
        return metrics
    
    def should_auto_reply(self, confidence_score: float, reply_type: ReplyType) -> bool:
        """Determine if reply should be sent automatically"""
        if not self.config.enable_auto_reply:
            return False
        
        if confidence_score < self.config.auto_reply_threshold:
            return False
        
        if reply_type not in self.config.auto_reply_types:
            return False
        
        return True
