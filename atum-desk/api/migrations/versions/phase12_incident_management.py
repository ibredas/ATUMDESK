"""
Add Incident Management Tables

Revision ID: phase12_incident_management
Revises: phase11_provenance_gate
Create Date: 2026-02-15

Tables:
- incident_records: Major incident tracking
- incident_events: Timeline events
- incident_postmortems: Postmortem documents
"""
from alembic import op
import sqlalchemy as sa

revision = 'phase12_incident_management'
down_revision = 'phase11_provenance_gate'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Incident records table
    op.execute("""
        CREATE TYPE incident_severity AS ENUM ('SEV1', 'SEV2', 'SEV3', 'SEV4');
        CREATE TYPE incident_status AS ENUM ('OPEN', 'MITIGATING', 'RESOLVED', 'CLOSED');
    """)
    
    op.execute("""
        CREATE TABLE IF NOT EXISTS incident_records (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            organization_id UUID NOT NULL REFERENCES organizations(id),
            title VARCHAR(500) NOT NULL,
            status incident_status NOT NULL DEFAULT 'OPEN',
            severity incident_severity NOT NULL DEFAULT 'SEV3',
            linked_ticket_ids JSONB DEFAULT '[]',
            linked_problem_id UUID,
            started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            resolved_at TIMESTAMPTZ,
            created_by UUID REFERENCES users(id),
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        
        CREATE INDEX idx_incident_org ON incident_records(organization_id);
        CREATE INDEX idx_incident_status ON incident_records(status);
        CREATE INDEX idx_incident_severity ON incident_records(severity);
    """)
    
    # Incident timeline events
    op.execute("""
        CREATE TABLE IF NOT EXISTS incident_events (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            organization_id UUID NOT NULL REFERENCES organizations(id),
            incident_id UUID NOT NULL REFERENCES incident_records(id) ON DELETE CASCADE,
            event_type VARCHAR(50) NOT NULL,
            content TEXT NOT NULL,
            created_by UUID REFERENCES users(id),
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        
        CREATE INDEX idx_incident_events_incident ON incident_events(incident_id);
    """)
    
    # Incident postmortems
    op.execute("""
        CREATE TABLE IF NOT EXISTS incident_postmortems (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            incident_id UUID NOT NULL REFERENCES incident_records(id) ON DELETE CASCADE,
            organization_id UUID NOT NULL REFERENCES organizations(id),
            impact_summary TEXT NOT NULL,
            root_cause TEXT NOT NULL,
            timeline TEXT NOT NULL,
            what_went_well TEXT,
            what_went_wrong TEXT,
            action_items JSONB DEFAULT '[]',
            public_summary TEXT,
            internal_notes TEXT,
            created_by UUID REFERENCES users(id),
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        
        CREATE INDEX idx_postmortem_incident ON incident_postmortems(incident_id);
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS incident_postmortems")
    op.execute("DROP TABLE IF EXISTS incident_events")
    op.execute("DROP TABLE IF EXISTS incident_records")
    op.execute("DROP TYPE IF EXISTS incident_severity")
    op.execute("DROP TYPE IF EXISTS incident_status")
