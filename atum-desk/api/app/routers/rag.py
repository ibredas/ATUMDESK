"""
RAG API Routes - Tenant-isolated semantic search
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import get_current_user
from app.models.user import User
from app.db.session import get_session
from app.services.rag.store import RAGStore
from app.services.rag.retriever import RAGRetriever
from app.config import get_settings

router = APIRouter(tags=["RAG"])
_settings = get_settings()


@router.get("/search")
async def search_knowledge(
    q: str = Query(..., min_length=1, max_length=500),
    limit: int = Query(default=5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Semantic search across KB, tickets, and assets.
    Tenant-isolated by organization_id.
    """
    if not _settings.RAG_ENABLED:
        raise HTTPException(status_code=503, detail="RAG service is disabled")
    
    store = RAGStore(db)
    retriever = RAGRetriever(store)
    
    results = await retriever.search(
        organization_id=current_user.organization_id,
        query=q,
        user_role=current_user.role.value,
        top_k=limit,
        graph_depth=_settings.RAG_GRAPH_DEPTH,
    )
    
    return results


@router.get("/tickets/{ticket_id}/similar")
async def find_similar_tickets(
    ticket_id: str,
    limit: int = Query(default=5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Find tickets similar to a specific ticket"""
    if not _settings.RAG_ENABLED:
        raise HTTPException(status_code=503, detail="RAG service is disabled")
    
    # Only agents+ can access
    if current_user.role.value not in ("agent", "manager", "admin"):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        ticket_uuid = UUID(ticket_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ticket ID")
    
    store = RAGStore(db)
    retriever = RAGRetriever(store)
    
    results = await retriever.get_similar_tickets(
        organization_id=current_user.organization_id,
        ticket_id=ticket_uuid,
        top_k=limit,
    )
    
    return {"ticket_id": ticket_id, "similar": results}


@router.get("/tickets/{ticket_id}/context")
async def get_ticket_context(
    ticket_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Get full context for a ticket: related KB, assets, problems, changes"""
    if not _settings.RAG_ENABLED:
        raise HTTPException(status_code=503, detail="RAG service is disabled")
    
    # Only agents+ can access
    if current_user.role.value not in ("agent", "manager", "admin"):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        ticket_uuid = UUID(ticket_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ticket ID")
    
    store = RAGStore(db)
    retriever = RAGRetriever(store)
    
    context = await retriever.get_ticket_context(
        organization_id=current_user.organization_id,
        ticket_id=ticket_uuid,
    )
    
    return context


@router.get("/health")
async def rag_health():
    """RAG service health check"""
    return {
        "enabled": _settings.RAG_ENABLED,
        "embed_model": _settings.OLLAMA_EMBEDDING_MODEL,
        "embed_dim": _settings.RAG_EMBED_DIM,
        "top_k": _settings.RAG_TOP_K,
        "graph_depth": _settings.RAG_GRAPH_DEPTH,
    }
