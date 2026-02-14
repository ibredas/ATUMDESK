"""
RAG Retriever - Hybrid Vector + Keyword + Graph Expansion
"""
import logging
from typing import List, Dict, Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from app.services.rag.store import RAGStore
from app.services.rag.embeddings import get_embedding
from app.config import get_settings

logger = logging.getLogger(__name__)
_settings = get_settings()


class RAGRetriever:
    """Hybrid retrieval: Vector + Keyword + Graph"""
    
    def __init__(self, store: RAGStore):
        self.store = store
    
    async def search(
        self,
        organization_id: UUID,
        query: str,
        user_role: str = "customer",
        top_k: int = 5,
        graph_depth: int = 2,
        include_graph: bool = True,
    ) -> Dict[str, Any]:
        """
        Full hybrid search:
        1. Vector similarity search
        2. Keyword search (Postgres full-text)
        3. Graph expansion
        4. Merge and rerank
        """
        # 1. Vector search
        query_embedding = get_embedding(query)
        
        # Determine what source types this role can see
        source_types = self._get_visible_source_types(user_role)
        
        vector_results = await self.store.search_similar(
            organization_id=organization_id,
            query_embedding=query_embedding,
            top_k=top_k * 2,  # Get more for merging
            source_types=source_types,
            ef_search=_settings.RAG_HNSW_EF_SEARCH,
        )
        
        # 2. Keyword search
        keyword_results = await self._keyword_search(
            organization_id=organization_id,
            query=query,
            source_types=source_types,
            top_k=top_k * 2,
        )
        
        # 3. Merge results
        merged = self._merge_results(vector_results, keyword_results)
        
        # 4. Graph expansion (if enabled)
        graph_context = {}
        if include_graph and graph_depth > 0:
            # Get unique source IDs from top results
            source_ids = [(r["source_type"], r["source_id"]) for r in merged[:3]]
            
            for src_type, src_id in source_ids:
                if src_type == "ticket":
                    graph_ctx = await self._get_ticket_graph_context(
                        organization_id, src_id, graph_depth
                    )
                    if graph_ctx:
                        graph_context[f"{src_type}:{src_id}"] = graph_ctx
        
        # 5. Build final response
        return {
            "results": merged[:top_k],
            "graph_context": graph_context,
            "query": query,
            "total": len(merged),
        }
    
    async def get_similar_tickets(
        self,
        organization_id: UUID,
        ticket_id: UUID,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """Find tickets similar to a given ticket"""
        # Get ticket info
        query_embedding = get_embedding(f"ticket:{ticket_id}")
        
        results = await self.store.search_similar(
            organization_id=organization_id,
            query_embedding=query_embedding,
            top_k=top_k,
            source_types=["ticket"],
            ef_search=_settings.RAG_HNSW_EF_SEARCH,
        )
        
        # Filter out the original ticket
        return [r for r in results if r["source_id"] != ticket_id]
    
    async def get_ticket_context(
        self,
        organization_id: UUID,
        ticket_id: UUID,
    ) -> Dict[str, Any]:
        """Get full context for a ticket: related KB, assets, problems, changes"""
        context = {
            "ticket_id": str(ticket_id),
            "related_kb": [],
            "similar_tickets": [],
            "related_assets": [],
            "linked_problems": [],
            "linked_changes": [],
        }
        
        # Get similar tickets
        context["similar_tickets"] = await self.get_similar_tickets(
            organization_id, ticket_id, top_k=3
        )
        
        # Get graph context
        graph_nodes = await self.store.get_related_nodes(
            organization_id=organization_id,
            node_id=ticket_id,
            depth=2,
        )
        
        for node in graph_nodes:
            node_type = node["node_type"]
            if node_type == "kb":
                context["related_kb"].append(node)
            elif node_type == "asset":
                context["related_assets"].append(node)
            elif node_type == "problem":
                context["linked_problems"].append(node)
            elif node_type == "change":
                context["linked_changes"].append(node)
        
        return context
    
    def _get_visible_source_types(self, user_role: str) -> Optional[List[str]]:
        """Get which source types a role can see"""
        if user_role in ("agent", "manager", "admin"):
            return ["kb", "ticket", "asset", "problem", "change"]
        elif user_role == "customer":
            return ["kb"]  # Only public KB
        return None
    
    async def _keyword_search(
        self,
        organization_id: UUID,
        query: str,
        source_types: Optional[List[str]],
        top_k: int,
    ) -> List[Dict[str, Any]]:
        """Simple keyword search using ILIKE (fallback)"""
        # Build query
        search_term = f"%{query}%"
        
        source_filter = ""
        params = {"org_id": organization_id, "query": search_term, "limit": top_k}
        
        if source_types:
            placeholders = ", ".join([f":type_{i}" for i in range(len(source_types))])
            source_filter = f"AND d.source_type IN ({placeholders})"
            for i, stype in enumerate(source_types):
                params[f"type_{i}"] = stype
        
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
                1.0 as similarity
            FROM rag_chunks c
            JOIN rag_documents d ON c.document_id = d.id
            WHERE c.organization_id = :org_id 
                AND d.organization_id = :org_id
                AND c.content ILIKE :query
                {source_filter}
            ORDER BY d.updated_at DESC
            LIMIT :limit
        """)
        
        try:
            from app.db.session import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                result = await session.execute(stmt, params)
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
        except Exception as e:
            logger.warning(f"Keyword search failed: {e}")
            return []
    
    def _merge_results(
        self,
        vector_results: List[Dict],
        keyword_results: List[Dict],
    ) -> List[Dict]:
        """Merge and dedupe results from vector and keyword search"""
        seen = set()
        merged = []
        
        # Interleave results by score
        all_results = sorted(
            vector_results + keyword_results,
            key=lambda x: x.get("score", 0),
            reverse=True,
        )
        
        for r in all_results:
            key = (r["source_type"], r["source_id"])
            if key not in seen:
                seen.add(key)
                merged.append(r)
        
        return merged
    
    async def _get_ticket_graph_context(
        self,
        organization_id: UUID,
        ticket_id: UUID,
        depth: int,
    ) -> Dict[str, Any]:
        """Get graph context for a ticket"""
        graph_nodes = await self.store.get_related_nodes(
            organization_id=organization_id,
            node_id=ticket_id,
            depth=depth,
        )
        
        context = {"nodes": graph_nodes, "edges": []}
        
        # Get edges
        try:
            from app.db.session import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                stmt = text("""
                    SELECT id, edge_type, from_node_id, to_node_id, weight
                    FROM rag_edges
                    WHERE organization_id = :org_id
                        AND (from_node_id = :ticket_id OR to_node_id = :ticket_id)
                """)
                result = await session.execute(stmt, {
                    "org_id": organization_id,
                    "ticket_id": ticket_id,
                })
                rows = result.fetchall()
                
                context["edges"] = [
                    {"id": row[0], "type": row[1], "from": row[2], "to": row[3], "weight": row[4]}
                    for row in rows
                ]
        except Exception as e:
            logger.warning(f"Failed to get edges: {e}")
        
        return context
