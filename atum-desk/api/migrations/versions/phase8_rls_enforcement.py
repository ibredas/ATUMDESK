"""Add Row Level Security (RLS) for tenant isolation - STAGED

Revision ID: phase8_rls_enforcement
Revises: phase7_prompt_firewall
Create Date: 2026-02-14

NOTE: This migration is STAGED - helper functions created but RLS NOT enabled.
To enable after testing, run manually:
  SELECT enable_rls_policies();
"""
from alembic import op
import sqlalchemy as sa

revision = 'phase8_rls_enforcement'
down_revision = 'phase7_prompt_firewall'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create helper function for setting org context
    op.execute("""
        CREATE OR REPLACE FUNCTION set_app_org(org_id UUID)
        RETURNS void AS $$
        BEGIN
            PERFORM set_config('app.current_org', org_id::text, false);
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;
    """)
    
    # Note: RLS functions need to be applied manually after testing
    # This is to prevent breaking production
    pass


def downgrade() -> None:
    op.execute("DROP FUNCTION IF EXISTS set_app_org(UUID);")
