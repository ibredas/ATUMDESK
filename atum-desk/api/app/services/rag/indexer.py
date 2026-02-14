"""
RAG Indexer - Queue-based indexer for worker
"""
import logging
from typing import List, Dict, Any, Optional
from uuid import UUID
import json

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.rag.store import RAGStore
from app.services.rag.embeddings import get_embedding, get_embeddings_batch

logger = logging.getLogger(__name__)

CHUNK_MAX_TOKENS = 512
CHUNK_OVERLAP = 50


class RAGIndexer:
    """Index content into RAG store"""
    
    def __init__(self, store: RAGStore):
        self.store = store
    
    async def index_ticket(
        self,
        organization_id: UUID,
        ticket_id: UUID,
        subject: str,
        description: str,
        resolution: Optional[str] = None,
        status: str = "new",
    ) -> bool:
        """
        Index a ticket into RAG.
        Only indexes RESOLVED tickets (per spec).
        """
        if status not in ("resolved", "closed"):
            logger.debug(f"Skipping indexing for non-resolved ticket {ticket_id}")
            return False
        
        try:
            # Create document
            doc_id = await self.store.upsert_document(
                organization_id=organization_id,
                source_type="ticket",
                source_id=ticket_id,
                title=subject,
                visibility="internal",
                metadata={"status": status},
            )
            
            # Create chunks
            chunks = []
            
            # Chunk 1: Problem (subject + description)
            problem_text = f"Subject: {subject}\n\nDescription: {description}"
            chunks.append({
                "content": problem_text,
                "token_count": len(problem_text.split()),
            })
            
            # Chunk 2: Resolution (if available)
            if resolution:
                resolution_text = f"Resolution: {resolution}"
                chunks.append({
                    "content": resolution_text,
                    "token_count": len(resolution_text.split()),
                })
            
            # Generate embeddings
            for chunk in chunks:
                chunk["embedding"] = get_embedding(chunk["content"])
            
            # Store chunks
            await self.store.insert_chunks(doc_id, organization_id, chunks)
            
            # Build graph nodes
            await self._index_ticket_graph(organization_id, ticket_id, subject)
            
            logger.info(f"Indexed ticket {ticket_id} for org {organization_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to index ticket {ticket_id}: {e}", exc_info=True)
            raise
    
    async def index_kb_article(
        self,
        organization_id: UUID,
        article_id: UUID,
        title: str,
        content: str,
        visibility: str = "public",
    ) -> bool:
        """Index a KB article"""
        try:
            doc_id = await self.store.upsert_document(
                organization_id=organization_id,
                source_type="kb",
                source_id=article_id,
                title=title,
                visibility=visibility,
            )
            
            # Chunk the content
            chunks = self._chunk_text(content)
            
            # Generate embeddings
            for chunk in chunks:
                chunk["embedding"] = get_embedding(chunk["content"])
            
            await self.store.insert_chunks(doc_id, organization_id, chunks)
            
            # Build graph nodes
            await self._index_kb_graph(organization_id, article_id, title)
            
            logger.info(f"Indexed KB article {article_id} for org {organization_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to index KB article {article_id}: {e}", exc_info=True)
            raise
    
    async def index_asset(
        self,
        organization_id: UUID,
        asset_id: UUID,
        name: str,
        asset_type: str,
        metadata: Dict[str, Any],
    ) -> bool:
        """Index an asset"""
        try:
            doc_id = await self.store.upsert_document(
                organization_id=organization_id,
                source_type="asset",
                source_id=asset_id,
                title=name,
                visibility="internal",
                metadata=metadata,
            )
            
            # Create summary chunk
            summary = f"Asset: {name} ({asset_type})\n"
            if metadata:
                summary += json.dumps(metadata, default=str)
            
            chunks = [{"content": summary, "token_count": len(summary.split())}]
            
            for chunk in chunks:
                chunk["embedding"] = get_embedding(chunk["content"])
            
            await self.store.insert_chunks(doc_id, organization_id, chunks)
            
            # Build graph
            await self.store.upsert_node(
                organization_id=organization_id,
                node_type="asset",
                node_id=asset_id,
                label=name,
            )
            
            logger.info(f"Indexed asset {asset_id} for org {organization_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to index asset {asset_id}: {e}", exc_info=True)
            raise
    
    async def delete_index(
        self,
        organization_id: UUID,
        source_type: str,
        source_id: UUID,
    ) -> bool:
        """Delete index for a source"""
        try:
            # Delete from graph first
            await self.store.delete_node_edges(organization_id, source_id)
            
            # Delete document (cascades to chunks)
            result = await self.store.delete_document(organization_id, source_type, source_id)
            
            logger.info(f"Deleted index for {source_type}/{source_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to delete index for {source_type}/{source_id}: {e}")
            raise
    
    def _chunk_text(self, text: str, max_tokens: int = CHUNK_MAX_TOKENS) -> List[Dict]:
        """Split text into chunks"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), max_tokens - CHUNK_OVERLAP):
            chunk_words = words[i:i + max_tokens]
            chunk_text = " ".join(chunk_words)
            
            chunks.append({
                "content": chunk_text,
                "token_count": len(chunk_words),
            })
            
            if len(chunks) >= 10:  # Limit chunks per document
                break
        
        return chunks
    
    async def _index_ticket_graph(
        self,
        organization_id: UUID,
        ticket_id: UUID,
        subject: str,
    ) -> None:
        """Build graph nodes for ticket"""
        # Create node for ticket
        await self.store.upsert_node(
            organization_id=organization_id,
            node_type="ticket",
            node_id=ticket_id,
            label=subject,
        )
    
    async def _index_kb_graph(
        self,
        organization_id: UUID,
        article_id: UUID,
        title: str,
    ) -> None:
        """Build graph nodes for KB article"""
        await self.store.upsert_node(
            organization_id=organization_id,
            node_type="kb",
            node_id=article_id,
            label=title,
        )


async def enqueue_index(
    db: AsyncSession,
    organization_id: UUID,
    source_type: str,
    source_id: UUID,
    action: str = "upsert",
) -> UUID:
    """Helper to enqueue a job (used by request handlers)"""
    store = RAGStore(db)
    return await store.enqueue_index(organization_id, source_type, source_id, action)
