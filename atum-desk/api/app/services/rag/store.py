"""
RAG Store - Pure SQLAlchemy + pgvector (No LangChain)
"""
import uuid
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID

from sqlalchemy import select, insert, update, delete, text, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import UUID, JSONB
import pgvector.sqlalchemy.vector

from app.config import get_settings

logger = logging.getLogger(__name__)

RAG_EMBED_DIM = 1536  # ATUM-DESK-AI dimension


class RAGStore:
    """Pure SQLAlchemy RAG storage - no LangChain"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    # === Document Operations ===
    
    async def upsert_document(
        self,
        organization_id: UUID,
        source_type: str,
        source_id: UUID,
        title: Optional[str] = None,
        visibility: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> UUID:
        """Create or update a RAG document"""
        doc_id = uuid.uuid4()
        
        stmt = insert(text("""
            INSERT INTO rag_documents (id, organization_id, source_type, source_id, title, visibility, metadata_json, created_at, updated_at)
            VALUES (:id, :org_id, :source_type, :source_id, :title, :visibility, :metadata, now(), now())
            ON CONFLICT (organization_id, source_type, source_id) 
            DO UPDATE SET 
                title = EXCLUDED.title,
                visibility = EXCLUDED.visibility,
                metadata_json = EXCLUDED.metadata_json,
                updated_at = now()
            RETURNING id
        """)).bindparams(
            id=doc_id,
            org_id=organization_id,
            source_type=source_type,
            source_id=source_id,
            title=title,
            visibility=visibility,
            metadata=metadata or {},
        )
        
        result = await self.session.execute(stmt)
        await self.session.commit()
        
        # Get existing or new ID
        if result.returns_rows:
            row = result.fetchone()
            return row[0] if row else doc_id
        return doc_id
    
    async def get_document(
        self,
        organization_id: UUID,
        source_type: str,
        source_id: UUID,
    ) -> Optional[Dict]:
        """Get a document by source"""
        stmt = select(text("""
            SELECT id, organization_id, source_type, source_id, title, visibility, metadata_json, created_at, updated_at
            FROM rag_documents
            WHERE organization_id = :org_id AND source_type = :source_type AND source_id = :source_id
        """)).bindparams(org_id=organization_id, source_type=source_type, source_id=source_id)
        
        result = await self.session.execute(stmt)
        row = result.fetchone()
        
        if row:
            return {
                "id": row[0],
                "organization_id": row[1],
                "source_type": row[2],
                "source_id": row[3],
                "title": row[4],
                "visibility": row[5],
                "metadata_json": row[6],
                "created_at": row[7],
                "updated_at": row[8],
            }
        return None
    
    async def delete_document(
        self,
        organization_id: UUID,
        source_type: str,
        source_id: UUID,
    ) -> bool:
        """Delete document and all its chunks"""
        # Delete chunks first (cascade should handle this but being explicit)
        await self.session.execute(
            text("""
                DELETE FROM rag_chunks 
                WHERE document_id IN (
                    SELECT id FROM rag_documents 
                    WHERE organization_id = :org_id AND source_type = :source_type AND source_id = :source_id
                )
            """),
            {"org_id": organization_id, "source_type": source_type, "source_id": source_id}
        )
        
        # Delete document
        result = await self.session.execute(
            text("""
                DELETE FROM rag_documents 
                WHERE organization_id = :org_id AND source_type = :source_type AND source_id = :source_id
                RETURNING id
            """),
            {"org_id": organization_id, "source_type": source_type, "source_id": source_id}
        )
        
        await self.session.commit()
        return result.fetchone() is not None
    
    # === Chunk Operations ===
    
    async def insert_chunks(
        self,
        document_id: UUID,
        organization_id: UUID,
        chunks: List[Dict[str, Any]],
    ) -> List[UUID]:
        """Insert chunks with embeddings"""
        chunk_ids = []
        
        for idx, chunk in enumerate(chunks):
            chunk_id = uuid.uuid4()
            
            stmt = text("""
                INSERT INTO rag_chunks (id, organization_id, document_id, chunk_index, content, embedding, token_count, created_at)
                VALUES (:id, :org_id, :doc_id, :idx, :content, :embedding, :tokens, now())
            """)
            
            embedding_arr = chunk.get("embedding")
            if embedding_arr is None:
                embedding_arr = [0.0] * RAG_EMBED_DIM
            
            await self.session.execute(stmt, {
                "id": chunk_id,
                "org_id": organization_id,
                "doc_id": document_id,
                "idx": idx,
                "content": chunk["content"],
                "embedding": embedding_arr,
                "tokens": chunk.get("token_count"),
            })
            chunk_ids.append(chunk_id)
        
        await self.session.commit()
        return chunk_ids
    
    async def search_similar(
        self,
        organization_id: UUID,
        query_embedding: List[float],
        top_k: int = 5,
        source_types: Optional[List[str]] = None,
        ef_search: int = 100,
    ) -> List[Dict[str, Any]]:
        """Vector similarity search with tenant filtering"""
        
        # Convert embedding to string format for pgvector
        embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
        
        # Build source filter if provided
        source_filter = ""
        params = {
            "query": embedding_str,
            "org_id": organization_id,
            "top_k": top_k,
        }
        
        if source_types:
            placeholders = ", ".join([f":type_{i}" for i in range(len(source_types))])
            source_filter = f"AND d.source_type IN ({placeholders})"
            for i, stype in enumerate(source_types):
                params[f"type_{i}"] = stype
        
        # Use HNSW with cosine distance
        stmt = text(f"""
            SELECT 
                c.id as chunk_id,
                c.content,
                c.chunk_index,
                d.id as doc_id,
                d.source_type,
                d.source_id,
                d.title,
                d.visibility,
                1 - (c.embedding <=> :query) as similarity
            FROM rag_chunks c
            JOIN rag_documents d ON c.document_id = d.id
            WHERE c.organization_id = :org_id 
                AND d.organization_id = :org_id
                {source_filter}
            ORDER BY c.embedding <=> :query
            LIMIT :top_k
        """)
        
        result = await self.session.execute(stmt, params)
        rows = result.fetchall()
        
        return [
            {
                "chunk_id": row[0],
                "content": row[1],
                "chunk_index": row[2],
                "document_id": row[3],
                "source_type": row[4],
                "source_id": row[5],
                "title": row[6],
                "visibility": row[7],
                "score": row[8],
            }
            for row in rows
        ]
    
    # === Index Queue Operations ===
    
    async def enqueue_index(
        self,
        organization_id: UUID,
        source_type: str,
        source_id: UUID,
        action: str = "upsert",
        priority: int = 5,
    ) -> UUID:
        """Add job to index queue"""
        job_id = uuid.uuid4()
        
        stmt = text("""
            INSERT INTO rag_index_queue (id, organization_id, source_type, source_id, action, priority, status, attempts, created_at, updated_at)
            VALUES (:id, :org_id, :source_type, :source_id, :action, :priority, 'pending', 0, now(), now())
            ON CONFLICT DO NOTHING
        """)
        
        await self.session.execute(stmt, {
            "id": job_id,
            "org_id": organization_id,
            "source_type": source_type,
            "source_id": source_id,
            "action": action,
            "priority": priority,
        })
        
        await self.session.commit()
        return job_id
    
    async def get_pending_jobs(
        self,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get pending index jobs"""
        stmt = text("""
            SELECT id, organization_id, source_type, source_id, action, priority, status, attempts, last_error, created_at
            FROM rag_index_queue
            WHERE status = 'pending'
            ORDER BY priority DESC, created_at ASC
            LIMIT :limit
            FOR UPDATE SKIP LOCKED
        """)
        
        result = await self.session.execute(stmt, {"limit": limit})
        rows = result.fetchall()
        
        return [
            {
                "id": row[0],
                "organization_id": row[1],
                "source_type": row[2],
                "source_id": row[3],
                "action": row[4],
                "priority": row[5],
                "status": row[6],
                "attempts": row[7],
                "last_error": row[8],
                "created_at": row[9],
            }
            for row in rows
        ]
    
    async def mark_job_running(self, job_id: UUID) -> None:
        """Mark job as running"""
        await self.session.execute(
            text("UPDATE rag_index_queue SET status = 'running', updated_at = now() WHERE id = :id"),
            {"id": job_id}
        )
        await self.session.commit()
    
    async def mark_job_done(self, job_id: UUID) -> None:
        """Mark job as done"""
        await self.session.execute(
            text("UPDATE rag_index_queue SET status = 'done', updated_at = now() WHERE id = :id"),
            {"id": job_id}
        )
        await self.session.commit()
    
    async def mark_job_failed(self, job_id: UUID, error: str) -> None:
        """Mark job as failed with error"""
        await self.session.execute(
            text("""
                UPDATE rag_index_queue 
                SET status = 'failed', last_error = :error, attempts = attempts + 1, updated_at = now() 
                WHERE id = :id
            """),
            {"id": job_id, "error": error[:1000]}  # Truncate error message
        )
        await self.session.commit()
    
    async def reset_stale_jobs(self, max_attempts: int = 3) -> None:
        """Reset jobs that have been running too long or exceeded attempts"""
        await self.session.execute(
            text("""
                UPDATE rag_index_queue
                SET status = 'pending', updated_at = now()
                WHERE status = 'running' 
                    AND updated_at < now() - interval '10 minutes'
            """)
        )
        await self.session.execute(
            text("""
                UPDATE rag_index_queue
                SET status = 'pending', updated_at = now()
                WHERE status = 'failed' 
                    AND attempts < :max_attempts
            """),
            {"max_attempts": max_attempts}
        )
        await self.session.commit()
    
    # === Graph Operations ===
    
    async def upsert_node(
        self,
        organization_id: UUID,
        node_type: str,
        node_id: UUID,
        label: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> UUID:
        """Create or update a graph node"""
        node_uuid = uuid.uuid4()
        
        await self.session.execute(text("""
            INSERT INTO rag_nodes (id, organization_id, node_type, node_id, label, metadata_json, created_at)
            VALUES (:id, :org_id, :node_type, :node_id, :label, :metadata, now())
            ON CONFLICT (organization_id, node_type, node_id) 
            DO UPDATE SET label = EXCLUDED.label, metadata_json = EXCLUDED.metadata_json
        """), {
            "id": node_uuid,
            "org_id": organization_id,
            "node_type": node_type,
            "node_id": node_id,
            "label": label,
            "metadata": metadata or {},
        })
        
        await self.session.commit()
        return node_uuid
    
    async def upsert_edge(
        self,
        organization_id: UUID,
        from_node_id: UUID,
        to_node_id: UUID,
        edge_type: str,
        weight: float = 1.0,
        metadata: Optional[Dict] = None,
    ) -> UUID:
        """Create or update a graph edge"""
        edge_uuid = uuid.uuid4()
        
        await self.session.execute(text("""
            INSERT INTO rag_edges (id, organization_id, from_node_id, to_node_id, edge_type, weight, metadata_json, created_at)
            VALUES (:id, :org_id, :from_id, :to_id, :edge_type, :weight, :metadata, now())
            ON CONFLICT DO NOTHING
        """), {
            "id": edge_uuid,
            "org_id": organization_id,
            "from_id": from_node_id,
            "to_id": to_node_id,
            "edge_type": edge_type,
            "weight": weight,
            "metadata": metadata or {},
        })
        
        await self.session.commit()
        return edge_uuid
    
    async def get_related_nodes(
        self,
        organization_id: UUID,
        node_id: UUID,
        edge_types: Optional[List[str]] = None,
        depth: int = 2,
    ) -> List[Dict[str, Any]]:
        """Get related nodes via graph traversal"""
        
        if depth == 1:
            # Direct neighbors
            if edge_types:
                placeholders = ", ".join([f":type_{i}" for i in range(len(edge_types))])
                type_filter = f"AND e.edge_type IN ({placeholders})"
                params = {"org_id": organization_id, "node_id": node_id}
                for i, etype in enumerate(edge_types):
                    params[f"type_{i}"] = etype
            else:
                type_filter = ""
                params = {"org_id": organization_id, "node_id": node_id}
            
            stmt = text(f"""
                SELECT DISTINCT n.id, n.node_type, n.node_id, n.label, e.edge_type, e.weight
                FROM rag_edges e
                JOIN rag_nodes n ON (e.to_node_id = n.id OR e.from_node_id = n.id)
                WHERE e.organization_id = :org_id 
                    AND (e.from_node_id = :node_id OR e.to_node_id = :node_id)
                    {type_filter}
            """)
        else:
            # Simplified depth-2: get both direct neighbors and their neighbors
            stmt = text("""
                WITH direct AS (
                    SELECT DISTINCT CASE 
                        WHEN e.from_node_id = :node_id THEN e.to_node_id 
                        ELSE e.from_node_id 
                    END as neighbor_id
                    FROM rag_edges e
                    WHERE e.organization_id = :org_id 
                        AND (e.from_node_id = :node_id OR e.to_node_id = :node_id)
                )
                SELECT DISTINCT n.id, n.node_type, n.node_id, n.label, e.edge_type, e.weight
                FROM rag_edges e
                JOIN rag_nodes n ON (e.to_node_id = n.id OR e.from_node_id = n.id)
                WHERE e.organization_id = :org_id 
                    AND (e.from_node_id IN (SELECT neighbor_id FROM direct) OR e.to_node_id IN (SELECT neighbor_id FROM direct))
            """)
            params = {"org_id": organization_id, "node_id": node_id}
        
        result = await self.session.execute(stmt, params)
        rows = result.fetchall()
        
        return [
            {
                "node_id": row[0],
                "node_type": row[1],
                "node_uuid": row[2],
                "label": row[3],
                "edge_type": row[4],
                "weight": row[5],
            }
            for row in rows
        ]
    
    async def delete_node_edges(self, organization_id: UUID, node_id: UUID) -> None:
        """Delete all edges for a node"""
        await self.session.execute(text("""
            DELETE FROM rag_edges 
            WHERE organization_id = :org_id 
                AND (from_node_id = :node_id OR to_node_id = :node_id)
        """), {"org_id": organization_id, "node_id": node_id})
        await self.session.commit()


async def get_rag_store(session: AsyncSession) -> RAGStore:
    """Dependency for getting RAG store"""
    return RAGStore(session)
