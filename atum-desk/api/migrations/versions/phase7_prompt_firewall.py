"""Add ai_security_events table for prompt firewall audit

Revision ID: phase7_prompt_firewall
Revises: phase6_copilot_runs
Create Date: 2026-02-14
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'phase7_prompt_firewall'
down_revision = 'phase6_copilot_runs'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'ai_security_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('gen_random_uuid()')),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('ticket_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('flags', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('snippet_hash', sa.String(64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    op.create_index('ix_ai_security_events_org', 'ai_security_events', ['organization_id'])
    op.create_index('ix_ai_security_events_created', 'ai_security_events', ['created_at'])
    op.create_index('ix_ai_security_events_type', 'ai_security_events', ['event_type'])


def downgrade() -> None:
    op.drop_table('ai_security_events')
