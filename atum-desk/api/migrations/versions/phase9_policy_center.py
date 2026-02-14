"""Add policy_rules table for Policy Center

Revision ID: phase9_policy_center
Revises: phase8_rls_enforcement
Create Date: 2026-02-14
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'phase9_policy_center'
down_revision = 'phase8_rls_enforcement'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'policy_rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('gen_random_uuid()')),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('target', sa.String(50), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('effect', sa.String(10), nullable=False),
        sa.Column('condition_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    op.create_index('ix_policy_rules_org', 'policy_rules', ['organization_id'])
    op.create_index('ix_policy_rules_target_action', 'policy_rules', ['target', 'action'])
    op.create_index('ix_policy_rules_priority', 'policy_rules', ['priority'])


def downgrade() -> None:
    op.drop_table('policy_rules')
