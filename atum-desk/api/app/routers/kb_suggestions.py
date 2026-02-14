"""
KB Suggestions API Routes - Analytics for KB deflection
"""
import json
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text

from app.auth.deps import get_current_user
from app.models.user import User, UserRole
from app.db.session import get_session

router = APIRouter(tags=["KB Suggestions"])


@router.get("/summary")
async def get_kb_suggestions_summary(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Get KB suggestions summary with deflection analytics"""
    
    org_id = str(current_user.organization_id)
    
    where_clause = "WHERE organization_id = :org_id"
    params = {"org_id": org_id}
    
    if date_from:
        where_clause += " AND created_at >= :date_from"
        params["date_from"] = date_from
    if date_to:
        where_clause += " AND created_at <= :date_to"
        params["date_to"] = date_to
    
    # Total suggestions
    result = await db.execute(
        text(f"""
            SELECT COUNT(*) as total FROM ticket_kb_suggestions {where_clause}
        """),
        params
    )
    total_suggestions = result.scalar() or 0
    
    # Helpful votes
    result = await db.execute(
        text(f"""
            SELECT COUNT(*) as helpful FROM ticket_kb_suggestions 
            {where_clause} AND is_helpful = true
        """),
        params
    )
    helpful_count = result.scalar() or 0
    
    # Deflection rate (tickets where user marked helpful)
    result = await db.execute(
        text(f"""
            SELECT COUNT(DISTINCT ticket_id) as deflected FROM ticket_kb_suggestions 
            {where_clause} AND is_helpful = true
        """),
        params
    )
    deflected_tickets = result.scalar() or 0
    
    deflection_rate = (deflected_tickets / total_suggestions * 100) if total_suggestions > 0 else 0
    
    # Top articles
    result = await db.execute(
        text(f"""
            SELECT article_id, title, COUNT(*) as suggestion_count, 
                   SUM(CASE WHEN is_helpful = true THEN 1 ELSE 0 END) as helpful_count
            FROM ticket_kb_suggestions
            {where_clause}
            GROUP BY article_id, title
            ORDER BY suggestion_count DESC
            LIMIT 10
        """),
        params
    )
    top_articles = []
    for row in result.fetchall():
        top_articles.append({
            "article_id": str(row[0]),
            "title": row[1],
            "suggestion_count": row[2],
            "helpful_count": row[3]
        })
    
    # Failing suggestions (never marked helpful)
    result = await db.execute(
        text(f"""
            SELECT ticket_id, article_id, title, relevance_score, created_at
            FROM ticket_kb_suggestions
            {where_clause}
            AND is_helpful IS NULL
            ORDER BY relevance_score ASC
            LIMIT 20
        """),
        params
    )
    failing_suggestions = []
    for row in result.fetchall():
        failing_suggestions.append({
            "ticket_id": str(row[0]),
            "article_id": str(row[1]),
            "title": row[2],
            "relevance_score": float(row[3]) if row[3] else 0,
            "created_at": row[4].isoformat() if row[4] else None
        })
    
    return {
        "total_suggestions": total_suggestions,
        "helpful_count": helpful_count,
        "deflection_rate": round(deflection_rate, 2),
        "deflected_tickets": deflected_tickets,
        "top_articles": top_articles,
        "failing_suggestions": failing_suggestions
    }


@router.get("/list")
async def list_kb_suggestions(
    ticket_id: Optional[str] = Query(None),
    article_id: Optional[str] = Query(None),
    is_helpful: Optional[bool] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """List KB suggestions with filters"""
    
    org_id = str(current_user.organization_id)
    
    where_clause = "WHERE organization_id = :org_id"
    params = {"org_id": org_id, "limit": limit, "offset": offset}
    
    if ticket_id:
        where_clause += " AND ticket_id = :ticket_id"
        params["ticket_id"] = ticket_id
    if article_id:
        where_clause += " AND article_id = :article_id"
        params["article_id"] = article_id
    if is_helpful is not None:
        where_clause += " AND is_helpful = :is_helpful"
        params["is_helpful"] = is_helpful
    if date_from:
        where_clause += " AND created_at >= :date_from"
        params["date_from"] = date_from
    if date_to:
        where_clause += " AND created_at <= :date_to"
        params["date_to"] = date_to
    
    result = await db.execute(
        text(f"""
            SELECT id, ticket_id, article_id, title, excerpt, 
                   relevance_score, is_helpful, created_at
            FROM ticket_kb_suggestions
            {where_clause}
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :offset
        """),
        params
    )
    
    suggestions = []
    for row in result.fetchall():
        suggestions.append({
            "id": str(row[0]),
            "ticket_id": str(row[1]),
            "article_id": str(row[2]),
            "title": row[3],
            "excerpt": row[4],
            "relevance_score": float(row[5]) if row[5] else 0,
            "is_helpful": row[6],
            "created_at": row[7].isoformat() if row[7] else None
        })
    
    return {"suggestions": suggestions, "limit": limit, "offset": offset}


@router.post("/vote")
async def vote_kb_suggestion(
    suggestion_id: str,
    is_helpful: bool,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Vote on a KB suggestion helpfulness"""
    
    org_id = str(current_user.organization_id)
    
    result = await db.execute(
        text("""
            UPDATE ticket_kb_suggestions 
            SET is_helpful = :is_helpful
            WHERE id = :id AND organization_id = :org_id
            RETURNING id
        """),
        {"id": suggestion_id, "org_id": org_id, "is_helpful": is_helpful}
    )
    
    updated = result.fetchone()
    
    if not updated:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    
    await db.commit()
    
    return {"message": "Vote recorded", "is_helpful": is_helpful}
