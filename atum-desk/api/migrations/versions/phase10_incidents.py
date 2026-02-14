"""Add incidents and postmortems tables

Revision ID: phase10_incidents
Revises: phase9_policy_center
Create Date: 2026-02-14
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'phase10_incidents'
down_revision = 'phase9_policy_center'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'incidents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('gen_random_uuid()')),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('severity', sa.String(10), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='OPEN'),
        sa.Column('commander_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('customer_impact_summary', sa.Text(), nullable=True),
        sa.Column('timeline', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('start_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    op.create_index('ix_incidents_org', 'incidents', ['organization_id'])
    op.create_index('ix_incidents_status', 'incidents', ['status'])
    
    op.create_table(
        'incident_ticket_links',
        sa.Column('incident_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ticket_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('incident_id', 'ticket_id')
    )
    
    op.create_table(
        'postmortems',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('gen_random_uuid()')),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('incident_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('root_cause', sa.Text(), nullable=True),
        sa.Column('contributing_factors', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('what_went_well', sa.Text(), nullable=True),
        sa.Column('what_went_wrong', sa.Text(), nullable=True),
        sa.Column('action_items', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    op.create_index('ix_postmortems_org', 'postmortems', ['organization_id'])
    op.create_index('ix_postmortems_incident', 'postmortems', ['incident_id'])


def downgrade() -> None:
    op.drop_table('postmortems')
    op.drop_table('incident_ticket_links')
    op.drop_table('incidents')
