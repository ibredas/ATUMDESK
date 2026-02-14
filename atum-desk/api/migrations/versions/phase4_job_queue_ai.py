"""Add job queue and AI tables

Revision ID: phase4_job_queue_ai
Revises: phase3_rag_graph
Create Date: 2026-02-13
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'phase4_job_queue_ai'
down_revision = 'phase3_rag_graph'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # === JOB QUEUE TABLES ===
    op.create_table(
        'job_queue',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=True),
        sa.Column('job_type', sa.String(50), nullable=False),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='PENDING'),
        sa.Column('locked_by', sa.UUID(), nullable=True),
        sa.Column('locked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('run_after', sa.DateTime(timezone=True), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index('ix_job_queue_status_run_after', 'job_queue', ['status', 'run_after'])
    op.create_index('ix_job_queue_locked_at', 'job_queue', ['locked_at'])
    op.create_index('ix_job_queue_organization_id', 'job_queue', ['organization_id'])
    op.create_index('ix_job_queue_job_type', 'job_queue', ['job_type'])
    
    # Job events table
    op.create_table(
        'job_events',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('job_id', sa.UUID(), nullable=False),
        sa.Column('event', sa.String(50), nullable=False),
        sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index('ix_job_events_job_id', 'job_events', ['job_id'])
    
    # === AI TRIAGE TABLE ===
    op.create_table(
        'ticket_ai_triage',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('ticket_id', sa.UUID(), nullable=False),
        sa.Column('suggested_category', sa.String(100), nullable=True),
        sa.Column('suggested_priority', sa.String(20), nullable=True),
        sa.Column('suggested_tags', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('suggested_assignee_id', sa.UUID(), nullable=True),
        sa.Column('sentiment_label', sa.String(20), nullable=True),
        sa.Column('sentiment_score', sa.Float(), nullable=True),
        sa.Column('intent_label', sa.String(50), nullable=True),
        sa.Column('intent_score', sa.Float(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('model_id', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index('ix_ticket_ai_triage_ticket_id', 'ticket_ai_triage', ['ticket_id'])
    op.create_index('ix_ticket_ai_triage_organization_id', 'ticket_ai_triage', ['organization_id'])
    
    # === AI SUGGESTIONS TABLE ===
    op.create_table(
        'ai_suggestions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('ticket_id', sa.UUID(), nullable=False),
        sa.Column('suggestion_type', sa.String(50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('citations', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('model_id', sa.String(100), nullable=True),
        sa.Column('is_used', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index('ix_ai_suggestions_ticket_id', 'ai_suggestions', ['ticket_id'])
    op.create_index('ix_ai_suggestions_type', 'ai_suggestions', ['suggestion_type'])
    op.create_index('ix_ai_suggestions_organization_id', 'ai_suggestions', ['organization_id'])
    
    # === KB SUGGESTIONS TABLE ===
    op.create_table(
        'ticket_kb_suggestions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('ticket_id', sa.UUID(), nullable=False),
        sa.Column('article_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('excerpt', sa.Text(), nullable=True),
        sa.Column('relevance_score', sa.Float(), nullable=False),
        sa.Column('is_helpful', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index('ix_ticket_kb_suggestions_ticket_id', 'ticket_kb_suggestions', ['ticket_id'])
    op.create_index('ix_ticket_kb_suggestions_article_id', 'ticket_kb_suggestions', ['article_id'])
    
    # === METRICS SNAPSHOTS TABLE ===
    op.create_table(
        'metrics_snapshots',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('snapshot_ts', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('tickets_by_status', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('tickets_by_priority', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('frt_p50', sa.Float(), nullable=True),
        sa.Column('frt_p95', sa.Float(), nullable=True),
        sa.Column('mttr_p50', sa.Float(), nullable=True),
        sa.Column('mttr_p95', sa.Float(), nullable=True),
        sa.Column('sla_compliance_pct', sa.Float(), nullable=True),
        sa.Column('agent_load', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index('ix_metrics_snapshots_org_ts', 'metrics_snapshots', ['organization_id', 'snapshot_ts'])
    
    # === SLA PREDICTION FIELDS ===
    op.add_column('tickets', sa.Column('time_to_breach_minutes', sa.Integer(), nullable=True))
    op.add_column('tickets', sa.Column('sla_risk_score', sa.Float(), nullable=True))
    
    # === ORGANIZATION SETTINGS TABLE ===
    op.create_table(
        'org_settings',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False, unique=True),
        sa.Column('auto_escalate_negative_sentiment', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('auto_escalate_threshold', sa.Float(), nullable=True, server_default='0.7'),
        sa.Column('kb_suggestion_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('ai_triage_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_column('tickets', 'sla_risk_score')
    op.drop_column('tickets', 'time_to_breach_minutes')
    op.drop_table('org_settings')
    op.drop_table('metrics_snapshots')
    op.drop_table('ticket_kb_suggestions')
    op.drop_table('ai_suggestions')
    op.drop_table('ticket_ai_triage')
    op.drop_table('job_events')
    op.drop_table('job_queue')
