from typing import List, Optional
from langchain_core.documents import Document
from app.models.ticket import Ticket
from app.services.rag.store import get_vector_store

async def index_ticket(ticket: Ticket):
    """
    Index a ticket into the vector store.
    Performs semantic chunking (Problem vs Resolution).
    """
    store = get_vector_store()
    
    # Chunk 1: The Problem (Subject + Description)
    problem_text = f"Subject: {ticket.subject}\nDescription: {ticket.description}"
    problem_doc = Document(
        page_content=problem_text,
        metadata={
            "ticket_id": str(ticket.id),
            "type": "problem",
            "status": ticket.status.value,
            "priority": ticket.priority.value,
            "organization_id": str(ticket.organization_id),
        }
    )
    
    docs = [problem_doc]
    
    # Chunk 2: The Resolution (if resolved)
    # We need to fetch resolution notes or comments.
    # For now, we just index the problem.
    
    try:
        # Add to store
        # langchain_postgres.PGVector supports async via aadd_documents
        await store.aadd_documents(docs)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to index ticket {ticket.id}: {e}")
        # Build resilience: Don't crash the server for background task failure
