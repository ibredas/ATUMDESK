"""Add copilot_runs table for AI Copilot trace logging

Revision ID: phase6_copilot_runs
Revises: phase5_security_hardening
Create Date: 2026-02-14
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'phase6_copilot_runs'
down_revision = 'phase5_security_hardening'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'copilot_runs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('gen_random_uuid()')),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ticket_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('plan_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('tool_trace_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('output_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('model_id', sa.String(100), nullable=True),
        sa.Column('latency_ms', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    op.create_index('ix_copilot_runs_org_ticket', 'copilot_runs', ['organization_id', 'ticket_id'])
    op.create_index('ix_copilot_runs_created_at', 'copilot_runs', ['created_at'])
    op.create_index('ix_copilot_runs_user_id', 'copilot_runs', ['user_id'])


def downgrade() -> None:
    op.drop_table('copilot_runs')
