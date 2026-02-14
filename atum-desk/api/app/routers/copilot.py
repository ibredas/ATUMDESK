"""
Copilot API Routes - Agentic AI Assistant for Staff
Caged Copilot Architecture with full trace logging
"""
import json
import logging
import time
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone

import requests
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from sqlalchemy.dialects.postgresql import insert

from app.auth.deps import get_current_user
from app.models.user import User, UserRole
from app.models.ticket import Ticket
from app.db.session import get_session
from app.services.rag.store import RAGStore
from app.services.rag.retriever import RAGRetriever
from app.services.ai.prompt_firewall import prompt_firewall
from app.config import get_settings

router = APIRouter(tags=["Copilot"])
_settings = get_settings()
logger = logging.getLogger(__name__)


@router.get("/{ticket_id}/copilot")
async def get_copilot_suggestions(
    ticket_id: str,
    action: str = Query(default="full", pattern="^(full|summarize|reply|context)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Get AI copilot suggestions for a ticket with full trace logging.
    Agents, Managers, Admins only.
    """
    start_time = time.time()
    plan_json = None
    tool_trace = []
    output_json = None
    status = "success"
    error_message = None

    try:
        if current_user.role not in (UserRole.AGENT, UserRole.MANAGER, UserRole.ADMIN):
            raise HTTPException(status_code=403, detail="Copilot is for staff only")
        
        ticket_uuid = UUID(ticket_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ticket ID")
    
    result = await db.execute(
        select(Ticket).where(Ticket.id == ticket_uuid)
    )
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    if ticket.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        plan_json = _build_plan(action, ticket)
        tool_trace.append({
            "tool": "planner",
            "result": "Plan created",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        store = RAGStore(db)
        retriever = RAGRetriever(store)
        
        tool_trace.append({
            "tool": "rag.search_kb",
            "input": {"query": ticket.subject, "top_k": 8},
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        kb_results = await retriever.search(
            organization_id=current_user.organization_id,
            query=ticket.subject,
            user_role=current_user.role.value,
            top_k=8,
        )
        
        tool_trace.append({
            "tool": "rag.search_kb",
            "result": {"count": len(kb_results.get("results", []))},
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        tool_trace.append({
            "tool": "rag.similar_tickets",
            "input": {"ticket_id": str(ticket_uuid), "top_k": 5},
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        similar_tickets = await retriever.get_similar_tickets(
            organization_id=current_user.organization_id,
            ticket_id=ticket_uuid,
            top_k=5,
        )
        
        tool_trace.append({
            "tool": "rag.similar_tickets",
            "result": {"count": len(similar_tickets)},
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        related_kb = kb_results.get("results", [])
        context = _build_context(ticket, similar_tickets, related_kb)
        
        has_evidence = len(related_kb) > 0 or len(similar_tickets) > 0
        
        if not has_evidence:
            output_json = {
                "insufficient_evidence": True,
                "questions": [
                    "What is the customer's exact issue?",
                    "What troubleshooting steps have been尝试ed?",
                    "Are there any error messages?"
                ],
                "checklist": [
                    "Check KB articles manually",
                    "Search similar tickets",
                    "Request more details from customer"
                ],
                "confidence": 0.1,
                "citations": []
            }
        else:
            ai_response = await _generate_copilot_response(
                ticket=ticket,
                context=context,
                action=action,
            )
            
            citations = _extract_citations(related_kb, similar_tickets)
            
            output_json = {
                **ai_response,
                "insufficient_evidence": False,
                "citations": citations,
                "confidence": ai_response.get("confidence", 0.7)
            }
        
        tool_trace.append({
            "tool": "output_generator",
            "result": output_json,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        status = "failed"
        error_message = str(e)
        logger.error(f"Copilot error: {e}")
        output_json = {
            "error": error_message,
            "insufficient_evidence": True,
            "questions": ["An error occurred. Please try again."],
            "confidence": 0
        }
    
    latency_ms = int((time.time() - start_time) * 1000)
    
    await _store_copilot_run(
        db=db,
        organization_id=str(current_user.organization_id),
        ticket_id=str(ticket_uuid),
        user_id=str(current_user.id),
        plan_json=plan_json,
        tool_trace_json=tool_trace,
        output_json=output_json,
        model_id=_settings.OLLAMA_MODEL,
        latency_ms=latency_ms,
        status=status,
        error_message=error_message
    )
    
    await _store_provenance(
        db=db,
        organization_id=str(current_user.organization_id),
        ticket_id=str(ticket_uuid),
        ai_feature="copilot",
        evidence=citations,
        confidence=output_json.get("confidence", 0) if output_json else 0,
        risk_score=0.0
    )
    
    return output_json


async def _store_copilot_run(
    db: AsyncSession,
    organization_id: str,
    ticket_id: str,
    user_id: str,
    plan_json: dict,
    tool_trace_json: list,
    output_json: dict,
    model_id: str,
    latency_ms: int,
    status: str,
    error_message: str = None
):
    """Store copilot run in database"""
    from uuid import uuid4
    try:
        await db.execute(
            text("""
                INSERT INTO copilot_runs (
                    id, organization_id, ticket_id, user_id,
                    plan_json, tool_trace_json, output_json,
                    model_id, latency_ms, status, error_message, created_at
                ) VALUES (
                    :id, :org_id, :ticket_id, :user_id,
                    :plan_json, :tool_trace_json, :output_json,
                    :model_id, :latency_ms, :status, :error_message, :created_at
                )
            """),
            {
                "id": str(uuid4()),
                "org_id": organization_id,
                "ticket_id": ticket_id,
                "user_id": user_id,
                "plan_json": json.dumps(plan_json),
                "tool_trace_json": json.dumps(tool_trace_json),
                "output_json": json.dumps(output_json),
                "model_id": model_id,
                "latency_ms": latency_ms,
                "status": status,
                "error_message": error_message,
                "created_at": datetime.now(timezone.utc)
            }
        )
        await db.commit()
    except Exception as e:
        logger.error(f"Failed to store copilot run: {e}")


async def _store_provenance(
    db: AsyncSession,
    organization_id: str,
    ticket_id: str,
    ai_feature: str,
    evidence: list,
    confidence: float,
    risk_score: float = 0.0,
):
    """Store AI provenance evidence for audit"""
    from uuid import uuid4
    try:
        await db.execute(
            text("""
                INSERT INTO ai_provenance (
                    id, organization_id, ticket_id, ai_feature, evidence_json,
                    confidence, risk_score, created_at
                ) VALUES (
                    :id, :org_id, :ticket_id, :feature, :evidence,
                    :confidence, :risk_score, :created_at
                )
            """),
            {
                "id": str(uuid4()),
                "org_id": organization_id,
                "ticket_id": ticket_id,
                "feature": ai_feature,
                "evidence": json.dumps(evidence),
                "confidence": confidence,
                "risk_score": risk_score,
                "created_at": datetime.now(timezone.utc)
            }
        )
        await db.commit()
    except Exception as e:
        logger.error(f"Failed to store provenance: {e}")


@router.get("/{ticket_id}/copilot/runs")
async def get_copilot_runs(
    ticket_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Get copilot runs for a ticket (Admin/Manager only for trace)"""
    if current_user.role not in (UserRole.AGENT, UserRole.MANAGER, UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Copilot is for staff only")
    
    try:
        ticket_uuid = UUID(ticket_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ticket ID")
    
    result = await db.execute(
        text("""
            SELECT id, user_id, model_id, latency_ms, status, created_at
            FROM copilot_runs
            WHERE ticket_id = :ticket_id AND organization_id = :org_id
            ORDER BY created_at DESC
            LIMIT 10
        """),
        {"ticket_id": str(ticket_uuid), "org_id": str(current_user.organization_id)}
    )
    
    runs = result.fetchall()
    return {
        "runs": [
            {
                "id": str(r[0]),
                "user_id": str(r[1]),
                "model_id": r[2],
                "latency_ms": r[3],
                "status": r[4],
                "created_at": r[5].isoformat() if r[5] else None
            }
            for r in runs
        ]
    }


@router.get("/{ticket_id}/copilot/runs/{run_id}/trace")
async def get_copilot_trace(
    ticket_id: str,
    run_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Get full trace for a copilot run (Admin/Manager only)"""
    if current_user.role not in (UserRole.MANAGER, UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Trace only for managers")
    
    result = await db.execute(
        text("""
            SELECT plan_json, tool_trace_json, output_json, latency_ms, status, error_message, created_at
            FROM copilot_runs
            WHERE id = :run_id AND organization_id = :org_id
        """),
        {"run_id": run_id, "org_id": str(current_user.organization_id)}
    )
    
    run = result.fetchone()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    return {
        "plan": json.loads(run[0]) if run[0] else None,
        "tool_trace": json.loads(run[1]) if run[1] else [],
        "output": json.loads(run[2]) if run[2] else None,
        "latency_ms": run[3],
        "status": run[4],
        "error_message": run[5],
        "created_at": run[6].isoformat() if run[6] else None
    }


def _build_plan(action: str, ticket: Ticket) -> dict:
    """Build execution plan"""
    return {
        "steps": [
            {"id": 1, "tool": "rag.search_kb", "description": "Search KB for relevant articles"},
            {"id": 2, "tool": "rag.similar_tickets", "description": "Find similar resolved tickets"},
            {"id": 3, "tool": "tickets.suggest_classification", "description": "Analyze ticket category"},
            {"id": 4, "tool": "output_generator", "description": "Generate response with citations"}
        ],
        "max_steps": 4,
        "action": action,
        "ticket_id": str(ticket.id)
    }


def _extract_citations(kb_results: list, similar_tickets: list) -> list:
    """Extract citations from RAG results"""
    citations = []
    
    for kb in kb_results[:5]:
        citations.append({
            "type": "kb",
            "id": str(kb.get("source_id", "")),
            "title": kb.get("title", ""),
            "excerpt": kb.get("content", "")[:200],
            "score": kb.get("score", 0)
        })
    
    for t in similar_tickets[:5]:
        citations.append({
            "type": "ticket",
            "id": str(t.get("source_id", "")),
            "title": t.get("title", ""),
            "excerpt": t.get("content", "")[:200],
            "score": t.get("score", 0)
        })
    
    return citations


def _build_context(
    ticket: Ticket,
    similar_tickets: List[dict],
    related_kb: List[dict],
) -> dict:
    """Build context for AI generation"""
    
    similar_format = []
    for t in similar_tickets[:5]:
        similar_format.append({
            "id": str(t.get("source_id", "")),
            "title": t.get("title", ""),
            "excerpt": t.get("content", "")[:200],
            "score": t.get("score", 0),
        })
    
    kb_format = []
    for kb in related_kb[:8]:
        if kb.get("source_type") == "kb":
            kb_format.append({
                "id": str(kb.get("source_id", "")),
                "title": kb.get("title", ""),
                "excerpt": kb.get("content", "")[:200],
                "score": kb.get("score", 0),
            })
    
    return {
        "ticket": {
            "id": str(ticket.id),
            "subject": ticket.subject,
            "description": ticket.description,
            "status": ticket.status.value if hasattr(ticket.status, 'value') else str(ticket.status),
            "priority": ticket.priority.value if hasattr(ticket.priority, 'value') else str(ticket.priority),
        },
        "similar_tickets": similar_format,
        "related_kb": kb_format,
    }


async def _generate_copilot_response(
    ticket: Ticket,
    context: dict,
    action: str,
) -> dict:
    """Generate copilot response using Ollama with citations"""
    
    if action == "summarize":
        prompt = _build_summarize_prompt(ticket, context)
    elif action == "reply":
        prompt = _build_reply_prompt(ticket, context)
    elif action == "context":
        prompt = _build_context_prompt(ticket, context)
    else:
        prompt = _build_full_prompt(ticket, context)
    
    try:
        response = requests.post(
            f"{_settings.OLLAMA_URL}/api/generate",
            json={
                "model": _settings.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json",
            },
            timeout=_settings.OLLAMA_TIMEOUT,
        )
        response.raise_for_status()
        
        result = response.json()
        ai_text = result.get("response", "{}")
        
        try:
            parsed = json.loads(ai_text)
        except json.JSONDecodeError:
            parsed = {"summary": ai_text, "error": "Failed to parse JSON"}
        
        return parsed
        
    except Exception as e:
        logger.error(f"Copilot generation failed: {e}")
        return {
            "summary": f"Ticket: {ticket.subject}",
            "suggested_reply": "AI generation failed. Please try again.",
            "next_steps": ["Review ticket manually", "Check KB articles"],
            "confidence": 0.1,
        }


def _build_summarize_prompt(ticket: Ticket, context: dict) -> str:
    base_prompt = f"""Summarize this ticket.

Ticket Subject: {ticket.subject}
Ticket Description: {ticket.description}
Status: {ticket.status}
Priority: {ticket.priority}

Provide a brief summary in JSON format:
{{"summary": "2-3 sentence summary"}}"""
    return prompt_firewall.apply_caged_template(base_prompt)


def _build_reply_prompt(ticket: Ticket, context: dict) -> str:
    similar = context.get("similar_tickets", [])
    kb = context.get("related_kb", [])
    
    similar_text = "\n".join([f"- {s['title']}: {s['excerpt']}" for s in similar[:2]])
    kb_text = "\n".join([f"- {k['title']}: {k['excerpt']}" for k in kb[:2]])
    
    base_prompt = f"""Draft a professional reply to this ticket.

Ticket:
Subject: {ticket.subject}
Description: {ticket.description}

Similar solved tickets:
{similar_text}

Relevant KB articles:
{kb_text}

Generate a draft reply in JSON format:
{{
  "suggested_reply": "The draft reply text",
  "confidence": 0.85,
  "key_points": ["point 1", "point 2"]
}}"""
    return prompt_firewall.apply_caged_template(base_prompt)


def _build_context_prompt(ticket: Ticket, context: dict) -> str:
    similar = context.get("similar_tickets", [])
    kb = context.get("related_kb", [])
    
    base_prompt = f"""Analyze this ticket and provide context.

Ticket: {ticket.subject}
Description: {ticket.description}

Similar tickets: {[s['title'] for s in similar]}
KB articles: {[k['title'] for k in kb]}

Provide context analysis in JSON:
{{
  "risk_notes": ["potential issue 1", "potential issue 2"],
  "missing_info": ["info needed"],
  "suggested_actions": ["action 1", "action 2"]
}}"""
    return prompt_firewall.apply_caged_template(base_prompt)


def _build_full_prompt(ticket: Ticket, context: dict) -> str:
    similar = context.get("similar_tickets", [])
    kb = context.get("related_kb", [])
    
    similar_text = "\n".join([f"- {s['title']}: {s['excerpt'][:100]}" for s in similar[:2]])
    kb_text = "\n".join([f"- {k['title']}: {k['excerpt'][:100]}" for k in kb[:2]])
    
    base_prompt = f"""Analyze this support ticket and provide comprehensive assistance.

TICKET:
Subject: {ticket.subject}
Description: {ticket.description}
Status: {ticket.status}
Priority: {ticket.priority}

SIMILAR SOLVED TICKETS:
{similar_text}

RELEVANT KB ARTICLES:
{kb_text}

Generate a complete response in JSON format:
{{
  "summary": "2-3 sentence ticket summary",
  "suggested_reply": "Professional draft reply to customer",
  "next_steps": ["action 1", "action 2", "action 3"],
  "confidence": 0.85
}}"""
    return prompt_firewall.apply_caged_template(base_prompt)
