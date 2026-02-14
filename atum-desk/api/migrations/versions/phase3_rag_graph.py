"""Phase 3: RAG tables + GraphRAG + HNSW index

Revision ID: phase3_rag_graph
Revises: ae2bcdc8e643
Create Date: 2026-02-13

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg
import pgvector.sqlalchemy.vector

revision: str = 'phase3_rag_graph'
down_revision: Union[str, Sequence[str], None] = 'ae2bcdc8e643'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

RAG_EMBED_DIM = 1536  # ATUM-DESK-AI dimension

def upgrade() -> None:
    # === RAG DOCUMENTS ===
    op.create_table(
        'rag_documents',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', pg.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('source_type', sa.String(50), nullable=False),  # 'kb'|'ticket'|'asset'|'problem'|'change'
        sa.Column('source_id', pg.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(1000)),
        sa.Column('visibility', sa.String(20)),  # 'public'|'internal'
        sa.Column('metadata_json', pg.JSONB, default={}),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()')),
    )
    op.create_index('ix_rag_documents_org_source', 'rag_documents', ['organization_id', 'source_type', 'source_id'], unique=True)
    
    # === RAG CHUNKS ===
    op.create_table(
        'rag_chunks',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', pg.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('document_id', pg.UUID(as_uuid=True), sa.ForeignKey('rag_documents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('chunk_index', sa.Integer, nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('embedding', pgvector.sqlalchemy.vector.VECTOR(dim=RAG_EMBED_DIM)),
        sa.Column('token_count', sa.Integer),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_rag_chunks_org_doc', 'rag_chunks', ['organization_id', 'document_id'])
    op.create_index('ix_rag_chunks_org', 'rag_chunks', ['organization_id'])
    
    # === RAG INDEX QUEUE ===
    op.create_table(
        'rag_index_queue',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', pg.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('source_type', sa.String(50), nullable=False),
        sa.Column('source_id', pg.UUID(as_uuid=True), nullable=False),
        sa.Column('action', sa.String(20), nullable=False),  # 'upsert'|'delete'
        sa.Column('priority', sa.Integer, default=5),
        sa.Column('status', sa.String(20), default='pending'),  # pending|running|done|failed
        sa.Column('attempts', sa.Integer, default=0),
        sa.Column('last_error', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()')),
    )
    op.create_index('ix_rag_queue_status', 'rag_index_queue', ['status', 'priority', 'created_at'])
    
    # === RAG NODES (GraphRAG) ===
    op.create_table(
        'rag_nodes',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', pg.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('node_type', sa.String(50), nullable=False),  # ticket|kb|asset|service|problem|change|user|tag
        sa.Column('node_id', pg.UUID(as_uuid=True), nullable=False),
        sa.Column('label', sa.String(500)),
        sa.Column('metadata_json', pg.JSONB, default={}),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_rag_nodes_org_type_id', 'rag_nodes', ['organization_id', 'node_type', 'node_id'], unique=True)
    
    # === RAG EDGES (GraphRAG) ===
    op.create_table(
        'rag_edges',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', pg.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('from_node_id', pg.UUID(as_uuid=True), sa.ForeignKey('rag_nodes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('to_node_id', pg.UUID(as_uuid=True), sa.ForeignKey('rag_nodes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('edge_type', sa.String(50), nullable=False),  # relates_to|duplicate_of|uses_asset|belongs_service|solves|mentioned_tag|linked_problem|linked_change
        sa.Column('weight', sa.Float, default=1.0),
        sa.Column('metadata_json', pg.JSONB, default={}),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_rag_edges_from', 'rag_edges', ['organization_id', 'from_node_id'])
    op.create_index('ix_rag_edges_to', 'rag_edges', ['organization_id', 'to_node_id'])
    op.create_index('ix_rag_edges_type', 'rag_edges', ['organization_id', 'edge_type'])
    
    # === HNSW INDEX (non-concurrent for migration, can be recreated concurrently later) ===
    # Note: CONCURRENTLY requires out-of-transaction execution
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_rag_chunks_hnsw 
        ON rag_chunks 
        USING hnsw (embedding vector_cosine_ops)
        WITH (m=16, ef_construction=64)
    """)
    
    # === RAG CONFIG (for storing embed dimension) ===
    op.create_table(
        'rag_config',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True, default=sa.text('gen_random_uuid()')),
        sa.Column('organization_id', pg.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column('embed_dim', sa.Integer, nullable=False, default=RAG_EMBED_DIM),
        sa.Column('embed_model', sa.String(100), nullable=False, default='ATUM-DESK-AI:latest'),
        sa.Column('hnsw_ef_search', sa.Integer, default=100),
        sa.Column('top_k', sa.Integer, default=5),
        sa.Column('graph_depth', sa.Integer, default=2),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()')),
    )


def downgrade() -> None:
    op.drop_table('rag_config')
    op.drop_table('rag_edges')
    op.drop_table('rag_nodes')
    op.drop_table('rag_index_queue')
    op.drop_table('rag_chunks')
    op.drop_table('rag_documents')
    
    op.execute("DROP INDEX IF EXISTS ix_rag_chunks_hnsw")
