"""Add security tables: login attempts, email verification, IP allowlist

Revision ID: phase5_security_hardening
Revises: phase4_job_queue_ai
Create Date: 2026-02-13

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'phase5_security_hardening'
down_revision = 'phase4_job_queue_ai'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # A2) Login attempt tracking (PostgreSQL - no Redis)
    op.create_table(
        'auth_login_attempts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('gen_random_uuid()')),
        sa.Column('ip_address', sa.String(45), nullable=False),  # IPv6 compatible
        sa.Column('username', sa.String(255), nullable=True),  # Can be null for username enumeration prevention
        sa.Column('fail_count', sa.Integer, default=1, nullable=False),
        sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_attempt_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_auth_login_attempts_ip', 'auth_login_attempts', ['ip_address'])
    op.create_index('ix_auth_login_attempts_username', 'auth_login_attempts', ['username'])
    op.create_index('ix_auth_login_attempts_locked_until', 'auth_login_attempts', ['locked_until'])
    
    # A6) Email verification tokens
    op.create_table(
        'email_verification_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token_hash', sa.String(255), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_email_verification_user_id', 'email_verification_tokens', ['user_id'])
    op.create_index('ix_email_verification_token_hash', 'email_verification_tokens', ['token_hash'])
    
    # C) IP Allowlist
    op.create_table(
        'org_ip_allowlist',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('gen_random_uuid()')),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('cidr', sa.String(45), nullable=False),  # CIDR notation: 192.168.1.0/24
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('enabled', sa.Boolean, default=True, nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_org_ip_allowlist_org', 'org_ip_allowlist', ['organization_id'])
    op.create_index('ix_org_ip_allowlist_cidr', 'org_ip_allowlist', ['cidr'])
    
    # Add is_verified to users if not exists
    try:
        op.add_column('users', sa.Column('is_email_verified', sa.Boolean, server_default='false', nullable=False))
    except Exception:
        pass  # Column may already exist


def downgrade() -> None:
    op.drop_table('org_ip_allowlist')
    op.drop_table('email_verification_tokens')
    op.drop_table('auth_login_attempts')
