"""Add ai_provenance table for tracking AI evidence

Revision ID: phase11_provenance_gate
Revises: phase10_incidents
Create Date: 2026-02-14
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'phase11_provenance_gate'
down_revision = 'phase10_incidents'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'ai_provenance',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('gen_random_uuid()')),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ticket_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('ai_feature', sa.String(50), nullable=False),
        sa.Column('evidence_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('risk_score', sa.Float(), nullable=True),
        sa.Column('policy_decision_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    op.create_index('ix_ai_provenance_org_ticket', 'ai_provenance', ['organization_id', 'ticket_id'])
    op.create_index('ix_ai_provenance_feature', 'ai_provenance', ['ai_feature'])
    op.create_index('ix_ai_provenance_created', 'ai_provenance', ['created_at'])


def downgrade() -> None:
    op.drop_table('ai_provenance')
