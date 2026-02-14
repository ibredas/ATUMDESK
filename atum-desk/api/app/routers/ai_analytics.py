"""
AI Analytics Router - Advanced AI-Powered Insights
"""
import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID

import requests
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from app.auth.deps import get_current_user
from app.models.user import User, UserRole
from app.models.ticket import Ticket, TicketStatus, TicketPriority
from app.db.session import get_session
from app.config import get_settings
from app.services.ai.preferences import get_ai_preferences, update_ai_preferences

router = APIRouter(prefix="/api/v1/ai", tags=["AI Analytics"])
_settings = get_settings()
logger = logging.getLogger(__name__)


@router.get("/insights/dashboard")
async def get_ai_dashboard_insights(
    days: int = Query(default=7, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Get AI-powered dashboard insights for the organization.
    Includes trends, predictions, and recommendations.
    """
    if current_user.role not in (UserRole.AGENT, UserRole.MANAGER, UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Admin/Manager/Agent access required")
    
    org_id = current_user.organization_id
    
    # Get ticket stats
    since = datetime.utcnow() - timedelta(days=days)
    
    # Total tickets
    total_result = await db.execute(
        select(func.count(Ticket.id)).where(
            and_(
                Ticket.organization_id == org_id,
                Ticket.created_at >= since
            )
        )
    )
    total_tickets = total_result.scalar() or 0
    
    # By status
    status_result = await db.execute(
        select(Ticket.status, func.count(Ticket.id))
        .where(
            and_(
                Ticket.organization_id == org_id,
                Ticket.created_at >= since
            )
        )
        .group_by(Ticket.status)
    )
    by_status = {str(row[0]): row[1] for row in status_result.fetchall()}
    
    # By priority
    priority_result = await db.execute(
        select(Ticket.priority, func.count(Ticket.id))
        .where(
            and_(
                Ticket.organization_id == org_id,
                Ticket.created_at >= since
            )
        )
        .group_by(Ticket.priority)
    )
    by_priority = {str(row[0]): row[1] for row in priority_result.fetchall()}
    
    # Average resolution time (mock for now - would need actual resolution data)
    avg_resolution_hours = 24.5  # Placeholder
    
    # AI-generated insights
    insights = await _generate_insights(
        total_tickets=total_tickets,
        by_status=by_status,
        by_priority=by_priority,
        days=days
    )
    
    return {
        "period_days": days,
        "total_tickets": total_tickets,
        "by_status": by_status,
        "by_priority": by_priority,
        "avg_resolution_hours": avg_resolution_hours,
        "insights": insights,
        "generated_at": datetime.utcnow().isoformat()
    }


@router.get("/insights/trends")
async def get_trend_analysis(
    metric: str = Query(default="tickets", pattern="^(tickets|priority|sla)$"),
    days: int = Query(default=30, ge=7, le=90),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Get trend analysis for tickets, priority, or SLA.
    """
    if current_user.role not in (UserRole.AGENT, UserRole.MANAGER, UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Access denied")
    
    org_id = current_user.organization_id
    
    # Generate mock trend data (in production, this would query actual data)
    trends = []
    for i in range(days):
        date = (datetime.utcnow() - timedelta(days=days-i)).strftime("%Y-%m-%d")
        if metric == "tickets":
            value = 10 + (i % 7) * 2 + (i // 7)
        elif metric == "priority":
            value = ["low", "medium", "high", "urgent"][i % 4]
        else:
            value = 85 + (i % 10)
        trends.append({"date": date, "value": value})
    
    return {
        "metric": metric,
        "period_days": days,
        "trends": trends,
        "summary": {
            "trend": "increasing" if trends[-1]["value"] > trends[0]["value"] else "decreasing",
            "change_percent": 15.5
        }
    }


@router.get("/insights/predictions")
async def get_ai_predictions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Get AI predictions for upcoming ticket volume and SLA risks.
    """
    if current_user.role not in (UserRole.AGENT, UserRole.MANAGER, UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Generate predictions (in production, this would use actual ML)
    predictions = {
        "ticket_volume": {
            "next_7_days": {
                "predicted": 85,
                "confidence": 0.78,
                "trend": "increasing"
            },
            "next_30_days": {
                "predicted": 380,
                "confidence": 0.72,
                "trend": "stable"
            }
        },
        "sla_risks": {
            "at_risk": 12,
            "likely_breach": 3,
            "recommendations": [
                "Prioritize 5 high-priority tickets approaching SLA limit",
                "Assign 2 unassigned tickets to available agents",
                "Consider escalating 3 tickets marked as urgent"
            ]
        },
        "category_distribution": {
            "technical": 45,
            "billing": 20,
            "account": 15,
            "inquiry": 12,
            "security": 5,
            "other": 3
        }
    }
    
    return predictions


@router.get("/insights/agent-performance")
async def get_agent_performance_insights(
    days: int = Query(default=7, ge=1, le=30),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Get AI-analyzed agent performance metrics.
    """
    if current_user.role not in (UserRole.MANAGER, UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Manager/Admin access required")
    
    # Mock agent performance data
    agents = [
        {
            "agent_id": str(UUID(int=1)),
            "name": "Agent A",
            "tickets_resolved": 45,
            "avg_response_time_minutes": 15,
            "sla_compliance": 92.5,
            "customer_satisfaction": 4.2,
            "ai_suggestions_accepted": 28
        },
        {
            "agent_id": str(UUID(int=2)),
            "name": "Agent B",
            "tickets_resolved": 38,
            "avg_response_time_minutes": 22,
            "sla_compliance": 88.0,
            "customer_satisfaction": 4.5,
            "ai_suggestions_accepted": 35
        }
    ]
    
    return {
        "period_days": days,
        "agents": agents,
        "summary": {
            "top_performer": "Agent B",
            "most_efficient": "Agent A",
            "ai_adoption_rate": 72.5
        }
    }


@router.post("/analyze/text")
async def analyze_text(
    text: str,
    analysis_type: str = Query(default="sentiment", pattern="^(sentiment|summary|classification)$"),
    current_user: User = Depends(get_current_user),
):
    """
    Analyze text using AI - sentiment, summary, or classification.
    """
    if not text or len(text) < 3:
        raise HTTPException(status_code=400, detail="Text too short")
    
    if analysis_type == "sentiment":
        prompt = f"""Analyze the sentiment of this text. Return JSON:
{{"sentiment": "positive/neutral/negative", "score": -1.0 to 1.0, "reason": "brief explanation"}}

Text: {text[:500]}"""
    
    elif analysis_type == "summary":
        prompt = f"""Summarize this text in 2-3 sentences. Return JSON:
{{"summary": "summary text"}}

Text: {text[:1000]}"""
    
    else:  # classification
        prompt = f"""Classify this text into one of: TECHNICAL, BILLING, ACCOUNT, INQUIRY, SECURITY, INFRA. Return JSON:
{{"category": "CATEGORY", "confidence": 0.0-1.0}}

Text: {text[:500]}"""
    
    try:
        response = requests.post(
            f"{_settings.OLLAMA_URL}/api/generate",
            json={
                "model": "qwen2.5:0.5b",
                "prompt": prompt,
                "stream": False,
                "format": "json",
            },
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        ai_text = result.get("response", "{}")
        
        parsed = json.loads(ai_text)
        return {"result": parsed, "model_used": "qwen2.5:0.5b"}
    
    except Exception as e:
        logger.error(f"Text analysis failed: {e}")
        return {"error": str(e)}


@router.get("/models/status")
async def get_ai_models_status(
    current_user: User = Depends(get_current_user),
):
    """
    Get status of all AI models in the system.
    """
    if current_user.role not in (UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        response = requests.get(
            f"{_settings.OLLAMA_URL}/api/tags",
            timeout=10
        )
        models = response.json().get("models", [])
        
        model_details = []
        for m in models:
            model_details.append({
                "name": m.get("name"),
                "size": m.get("size"),
                "modified_at": m.get("modified_at"),
                "status": "ready"
            })
        
        return {
            "ollama_status": "connected",
            "models": model_details,
            "default_model": _settings.OLLAMA_MODEL,
            "embedding_model": _settings.OLLAMA_EMBEDDING_MODEL
        }
    
    except Exception as e:
        return {
            "ollama_status": "error",
            "error": str(e),
            "models": []
        }


async def _generate_insights(
    total_tickets: int,
    by_status: dict,
    by_priority: dict,
    days: int
) -> List[dict]:
    """Generate AI-powered insights from ticket data."""
    
    insights = []
    
    # Analyze volume
    daily_avg = total_tickets / days
    if daily_avg > 20:
        insights.append({
            "type": "volume",
            "severity": "info",
            "message": f"High ticket volume: ~{daily_avg:.0f} tickets/day",
            "recommendation": "Consider scaling agent availability"
        })
    
    # Analyze priority distribution
    urgent = by_priority.get("urgent", 0) + by_priority.get("high", 0)
    if urgent > total_tickets * 0.3:
        insights.append({
            "type": "priority",
            "severity": "warning",
            "message": f"High priority tickets: {urgent} ({urgent*100//total_tickets}%)",
            "recommendation": "Review high-priority queue for blockers"
        })
    
    # Analyze status
    open_tickets = by_status.get("new", 0) + by_status.get("in_progress", 0)
    if open_tickets > 50:
        insights.append({
            "type": "backlog",
            "severity": "warning",
            "message": f"Large open queue: {open_tickets} tickets",
            "recommendation": "Prioritize backlog clearance"
        })
    
    # Always add positive insight
    insights.append({
        "type": "performance",
        "severity": "success",
        "message": "AI features actively helping agents",
        "recommendation": "Continue using copilot for faster resolution"
    })
    
    return insights


@router.get("/preferences")
async def get_ai_preferences_endpoint(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Get AI preferences for the current organization.
    """
    if current_user.role not in (UserRole.MANAGER, UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Manager/Admin access required")
    
    prefs = await get_ai_preferences(db, current_user.organization_id)
    return {"preferences": prefs}


@router.put("/preferences")
async def update_ai_preferences_endpoint(
    preferences: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Update AI preferences for the current organization.
    """
    if current_user.role not in (UserRole.MANAGER, UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Manager/Admin access required")
    
    updated = await update_ai_preferences(
        db, 
        current_user.organization_id, 
        preferences
    )
    return {"preferences": updated}


@router.get("/sla/predictions")
async def get_sla_predictions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Get SLA breach predictions for at-risk tickets.
    """
    if current_user.role not in (UserRole.AGENT, UserRole.MANAGER, UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Access denied")
    
    from app.services.ai.sla_predictor import SLABreachPredictor
    predictor = SLABreachPredictor(db)
    predictions = await predictor.get_breach_risk_tickets(
        organization_id=current_user.organization_id,
        limit=20
    )
    
    return {
        "at_risk_count": len(predictions),
        "predictions": predictions
    }


@router.get("/tickets/{ticket_id}/sla-prediction")
async def get_ticket_sla_prediction(
    ticket_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Get SLA breach prediction for a specific ticket.
    """
    from uuid import UUID
    from app.services.ai.sla_predictor import SLABreachPredictor, EstimatedResolutionTime
    
    try:
        ticket_uuid = UUID(ticket_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ticket ID")
    
    result = await db.execute(
        select(Ticket).where(
            Ticket.id == ticket_uuid,
            Ticket.organization_id == current_user.organization_id
        )
    )
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    predictor = SLABreachPredictor(db)
    resolution_predictor = EstimatedResolutionTime(db)
    
    breach_prediction = await predictor.predict_breach(ticket)
    resolution_prediction = await resolution_predictor.predict(ticket)
    
    return {
        "ticket_id": ticket_id,
        "breach_prediction": breach_prediction,
        "estimated_resolution": resolution_prediction
    }


@router.post("/classify")
async def classify_ticket_content(
    subject: str,
    description: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Classify ticket content into categories using AI.
    """
    if current_user.role not in (UserRole.AGENT, UserRole.MANAGER, UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Access denied")
    
    from app.services.ai.category_classifier import classify_ticket
    result = await classify_ticket(db, subject, description)
    
    return result


@router.get("/tickets/{ticket_id}/smart-replies")
async def get_smart_replies_endpoint(
    ticket_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Get AI-generated reply suggestions for a ticket.
    """
    if current_user.role not in (UserRole.AGENT, UserRole.MANAGER, UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Access denied")
    
    from uuid import UUID
    from app.services.ai.smart_reply import get_smart_replies
    
    try:
        ticket_uuid = UUID(ticket_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ticket ID")
    
    result = await db.execute(
        select(Ticket).where(
            Ticket.id == ticket_uuid,
            Ticket.organization_id == current_user.organization_id
        )
    )
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    suggestions = await get_smart_replies(db, ticket, num_suggestions=3)
    
    return {
        "ticket_id": ticket_id,
        "suggestions": suggestions
    }


@router.get("/tickets/{ticket_id}/summary")
async def get_ticket_summary(
    ticket_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Get AI-generated summary of ticket conversation thread.
    """
    if current_user.role not in (UserRole.AGENT, UserRole.MANAGER, UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Access denied")
    
    from app.services.ai.thread_summarizer import ThreadSummarizer
    summarizer = ThreadSummarizer(db)
    summary = await summarizer.summarize_thread(ticket_id)
    
    return summary


@router.get("/tickets/{ticket_id}/key-points")
async def get_ticket_key_points(
    ticket_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Extract key points from ticket conversation.
    """
    if current_user.role not in (UserRole.AGENT, UserRole.MANAGER, UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Access denied")
    
    from app.services.ai.thread_summarizer import ThreadSummarizer
    summarizer = ThreadSummarizer(db)
    points = await summarizer.extract_key_points(ticket_id)
    
    return {"key_points": points}


@router.get("/anomalies")
async def get_anomalies(
    days: int = Query(default=7, ge=1, le=30),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Get detected anomalies in ticket patterns.
    """
    if current_user.role not in (UserRole.MANAGER, UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Manager/Admin access required")
    
    from app.services.ai.anomaly_detector import detect_anomalies
    result = await detect_anomalies(db, current_user.organization_id, days)
    
    return result


@router.get("/kb/suggestions")
async def get_kb_suggestions(
    min_tickets: int = Query(default=3, ge=2, le=10),
    days: int = Query(default=30, ge=7, le=90),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Get AI-suggested KB article topics from resolved tickets.
    """
    if current_user.role not in (UserRole.MANAGER, UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Manager/Admin access required")
    
    from app.services.ai.auto_kb_generator import suggest_kb_topics
    suggestions = await suggest_kb_topics(db, current_user.organization_id, min_tickets)
    
    return {
        "suggestions": suggestions,
        "count": len(suggestions)
    }


@router.get("/analytics/overview")
async def get_ai_analytics_overview(
    days: int = Query(default=7, ge=1, le=30),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Get comprehensive AI analytics overview.
    Combines insights, predictions, and anomalies.
    """
    if current_user.role not in (UserRole.AGENT, UserRole.MANAGER, UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Access denied")
    
    from app.services.ai.anomaly_detector import detect_anomalies
    from app.services.ai.sla_predictor import SLABreachPredictor
    
    # Get anomalies
    anomalies = await detect_anomalies(db, current_user.organization_id, days)
    
    # Get SLA risks
    sla_predictor = SLABreachPredictor(db)
    risk_tickets = await sla_predictor.get_breach_risk_tickets(
        organization_id=current_user.organization_id,
        limit=10
    )
    
    return {
        "period_days": days,
        "anomalies": anomalies,
        "sla_risks": {
            "count": len(risk_tickets),
            "tickets": risk_tickets
        },
        "summary": {
            "needs_attention": anomalies.get("anomaly_count", 0) + len(risk_tickets),
            "status": "healthy" if (anomalies.get("anomaly_count", 0) == 0 and len(risk_tickets) == 0) else "action_needed"
        }
    }


@router.get("/sentiment/customer/{user_id}")
async def get_customer_sentiment_profile(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Get sentiment profile for a specific customer.
    """
    if current_user.role not in (UserRole.AGENT, UserRole.MANAGER, UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Access denied")
    
    from uuid import UUID
    from app.services.ai.sentiment_tracker import get_customer_profile
    
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    profile = await get_customer_profile(db, user_uuid)
    return profile


@router.get("/sentiment/organization")
async def get_org_sentiment_summary(
    days: int = Query(default=30, ge=7, le=90),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Get sentiment summary for the organization.
    """
    if current_user.role not in (UserRole.AGENT, UserRole.MANAGER, UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Access denied")
    
    from app.services.ai.sentiment_tracker import get_org_sentiment
    summary = await get_org_sentiment(db, current_user.organization_id, days)
    return summary


@router.get("/sentiment/trend")
async def get_sentiment_trend(
    days: int = Query(default=30, ge=7, le=90),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Get daily sentiment trend over time.
    """
    if current_user.role not in (UserRole.AGENT, UserRole.MANAGER, UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Access denied")
    
    from app.services.ai.sentiment_tracker import SentimentTracker
    tracker = SentimentTracker(db)
    trends = await tracker.get_sentiment_trend(current_user.organization_id, days)
    return {"trends": trends}


@router.get("/agent-assist/{ticket_id}")
async def get_agent_assist(
    ticket_id: str,
    context: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Get AI-assisted suggestions for handling a ticket.
    """
    if current_user.role not in (UserRole.AGENT, UserRole.MANAGER, UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Access denied")
    
    from app.services.ai.agent_assist import get_agent_assist
    suggestions = await get_agent_assist(db, ticket_id, context)
    return suggestions


@router.get("/agent-assist/{ticket_id}/quick-actions")
async def get_quick_actions_endpoint(
    ticket_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Get quick action suggestions for a ticket.
    """
    if current_user.role not in (UserRole.AGENT, UserRole.MANAGER, UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Access denied")
    
    from app.services.ai.agent_assist import get_quick_actions
    actions = await get_quick_actions(db, ticket_id)
    return actions
