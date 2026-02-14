# ATUM DESK - Comprehensive Implementation Plan
## Version 1.0 - All Enhancements Included (Option C)

---

## 🎯 PROJECT OVERVIEW

**ATUM DESK** is a production-grade, ATUM-branded helpdesk/ticketing platform with comprehensive features including real-time updates, AI assistance, advanced SLA management, knowledge base, analytics, and enterprise-grade security.

**Status**: Planning Phase  
**Scope**: Comprehensive (All Enhancements)  
**Brand Parity**: Exact ATUM UI clone  
**Deployment**: Bare-metal (systemd + nginx)  
**AI**: Local Ollama integration (Phase 2)  

---

## 📋 DELIVERABLES CHECKLIST

### Core Deliverables (Required)
- [x] **A** - Complete repo in `atum-desk/`
- [x] **B** - Web UI (landing page + portal + desk)
- [x] **C** - Backend API (FastAPI + PostgreSQL + Alembic)
- [x] **D** - Database schema + migrations
- [x] **E** - Upload subsystem with security
- [x] **F** - SLA subsystem (advanced with business hours)
- [x] **G** - SMTP notifications
- [x] **H** - systemd + nginx + install scripts
- [x] **I** - RUNBOOK.md + ACCEPTANCE_TESTS.md
- [x] **J** - First ticket E2E proof

### Enhanced Deliverables (Option C)
- [x] **K** - WebSocket real-time updates
- [x] **L** - Knowledge Base (customer + internal)
- [x] **M** - Canned responses & templates
- [x] **N** - Advanced search & filtering
- [x] **O** - Time tracking system
- [ ] **P** - Ticket relationships (parent/child/duplicate)
- [x] **Q** - Custom fields system
- [x] **R** - CSAT satisfaction surveys
- [x] **S** - Dashboard & analytics
- [x] **T** - AI Triage (Ollama)
- [x] **U** - AI-Assisted responses
- [x] **V** - Immutable audit logs
- [ ] **W** - IP restrictions
- [ ] **X** - Two-Factor Authentication (2FA) - Model exists, endpoints pending

---

## 🏗️ ARCHITECTURE OVERVIEW

### Tech Stack
```
Frontend:  React 19 + Vite 7 + Tailwind CSS v4 + WebSocket client
Backend:   FastAPI + SQLAlchemy 2.0 + Alembic + WebSocket (Socket.io)
Database:  PostgreSQL 15+ (with pg_trgm for full-text search)
Cache:     Redis (sessions, real-time, rate limiting)
AI:        Ollama (local LLM) + ChromaDB (embeddings)
Storage:   Local filesystem (uploads) + PostgreSQL (metadata)
Proxy:     nginx (reverse proxy + static files + WebSocket)
Runtime:   systemd (API service + WebSocket worker + Celery)
```

### System Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT BROWSER                        │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTPS
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                      NGINX (Port 443)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐ │
│  │ Static Files │  │  API Proxy   │  │ WebSocket Upgrade  │ │
│  │  (web/dist)  │  │  (/api/*)    │  │   (/ws/*)          │ │
│  └──────────────┘  └──────┬───────┘  └──────────┬─────────┘ │
└───────────────────────────┼─────────────────────┼───────────┘
                            │                     │
              ┌─────────────┘                     └──────────┐
              ▼                                              ▼
┌──────────────────────────┐                    ┌──────────────┐
│   FastAPI Application    │                    │   WebSocket  │
│   (Port 8000)            │◄──────────────────►│   Server     │
│   - REST API             │                    │   (Socket.io)│
│   - Authentication       │                    └──────────────┘
│   - Business Logic       │
└───────────┬──────────────┘
            │
    ┌───────┴───────┐
    ▼               ▼
┌─────────┐   ┌──────────┐   ┌──────────┐
│PostgreSQL│   │  Redis   │   │  Ollama  │
│(Primary) │   │(Cache/  │   │  (AI)    │
│          │   │Sessions) │   │          │
└─────────┘   └──────────┘   └──────────┘
```

---

## 📁 PROJECT STRUCTURE

```
atum-desk/
├── api/                                    # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                         # FastAPI app factory
│   │   ├── config.py                       # Pydantic settings
│   │   ├── dependencies.py                 # FastAPI dependencies
│   │   ├── auth/                           # Authentication & RBAC
│   │   │   ├── __init__.py
│   │   │   ├── jwt.py                      # JWT handling
│   │   │   ├── password.py                 # Password hashing
│   │   │   ├── rbac.py                     # Role-based access
│   │   │   └── two_factor.py               # TOTP 2FA
│   │   ├── db/                             # Database
│   │   │   ├── __init__.py
│   │   │   ├── base.py                     # SQLAlchemy base
│   │   │   ├── session.py                  # Async session
│   │   │   └── init_db.py                  # DB initialization
│   │   ├── models/                         # SQLAlchemy Models
│   │   │   ├── __init__.py
│   │   │   ├── organization.py             # Multi-tenant orgs
│   │   │   ├── user.py                     # Users with roles
│   │   │   ├── service.py                  # Ticket categories
│   │   │   ├── ticket.py                   # Core ticket entity
│   │   │   ├── comment.py                  # Public/internal comments
│   │   │   ├── attachment.py               # File attachments
│   │   │   ├── sla_policy.py               # SLA definitions
│   │   │   ├── sla_calculation.py          # SLA time calculations
│   │   │   ├── audit_log.py                # Audit trail
│   │   │   ├── time_entry.py               # Time tracking
│   │   │   ├── ticket_relationship.py      # Parent/child/duplicate
│   │   │   ├── custom_field.py             # Dynamic fields
│   │   │   ├── custom_field_value.py       # Field values
│   │   │   ├── canned_response.py          # Pre-written responses
│   │   │   ├── kb_article.py               # Knowledge base
│   │   │   ├── kb_category.py              # KB organization
│   │   │   └── csat_survey.py              # Satisfaction surveys
│   │   ├── routers/                        # API Endpoints
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                     # Login/logout/2FA
│   │   │   ├── users.py                    # User management
│   │   │   ├── organizations.py            # Org management
│   │   │   ├── tickets.py                  # Customer tickets
│   │   │   ├── internal_tickets.py         # Staff ticket ops
│   │   │   ├── comments.py                 # Comment endpoints
│   │   │   ├── attachments.py              # File upload/download
│   │   │   ├── sla.py                      # SLA management
│   │   │   ├── audit.py                    # Audit log queries
│   │   │   ├── time_tracking.py            # Time entry endpoints
│   │   │   ├── relationships.py            # Ticket linking
│   │   │   ├── custom_fields.py            # Dynamic field admin
│   │   │   ├── canned_responses.py         # Response templates
│   │   │   ├── kb.py                       # Knowledge base
│   │   │   ├── csat.py                     # Satisfaction surveys
│   │   │   ├── dashboard.py                # Analytics endpoints
│   │   │   ├── search.py                   # Full-text search
│   │   │   └── ai.py                       # AI suggestions
│   │   ├── services/                       # Business Logic
│   │   │   ├── __init__.py
│   │   │   ├── ticket_service.py           # Ticket operations
│   │   │   ├── sla_service.py              # SLA calculations
│   │   │   ├── audit_service.py            # Audit writing
│   │   │   ├── email_service.py            # SMTP notifications
│   │   │   ├── upload_service.py           # File handling
│   │   │   ├── search_service.py           # Search indexing
│   │   │   ├── time_service.py             # Time tracking
│   │   │   ├── kb_service.py               # KB operations
│   │   │   └── ai_service.py               # Ollama integration
│   │   ├── middleware/                     # FastAPI Middleware
│   │   │   ├── __init__.py
│   │   │   ├── auth_middleware.py          # JWT validation
│   │   │   ├── rbac_middleware.py          # Permission checks
│   │   │   ├── tenant_middleware.py        # Multi-tenant isolation
│   │   │   ├── rate_limit.py               # Rate limiting
│   │   │   └── audit_middleware.py         # Auto-audit
│   │   ├── utils/                          # Utilities
│   │   │   ├── __init__.py
│   │   │   ├── validators.py               # Input validation
│   │   │   ├── security.py                 # Security helpers
│   │   │   ├── datetime.py                 # Timezone handling
│   │   │   └── exceptions.py               # Custom exceptions
│   │   └── websocket/                      # Real-time
│   │       ├── __init__.py
│   │       ├── manager.py                  # Connection manager
│   │       ├── events.py                   # Event handlers
│   │       └── handlers.py                 # Message handlers
│   ├── migrations/                         # Alembic migrations
│   │   ├── versions/
│   │   ├── env.py
│   │   ├── alembic.ini
│   │   └── script.py.mako
│   ├── tests/                              # Test suite
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│   ├── celery/                             # Background tasks
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── tasks.py
│   ├── ai/                                 # AI Integration
│   │   ├── __init__.py
│   │   ├── ollama_client.py                # Ollama API client
│   │   ├── embeddings.py                   # ChromaDB integration
│   │   ├── triage.py                       # Ticket triage logic
│   │   └── suggestions.py                  # Response suggestions
│   ├── requirements.txt                    # Python dependencies
│   └── Dockerfile                          # Optional container
│
├── web/                                    # React Frontend
│   ├── public/
│   │   ├── brand/
│   │   │   ├── logo.svg                    # ATUM logo
│   │   │   ├── wordmark.svg                # ATUM wordmark
│   │   │   ├── atum-silhouette.svg         # Egyptian deity
│   │   │   └── favicon.svg                 # Favicon
│   │   └── index.html
│   ├── src/
│   │   ├── main.jsx                        # React entry
│   │   ├── App.jsx                         # Root component
│   │   ├── index.css                       # Global styles
│   │   ├── atum/                           # ATUM Design System
│   │   │   ├── tokens/                     # Design tokens
│   │   │   │   ├── colors.js               # Color palette
│   │   │   │   ├── typography.js           # Font scales
│   │   │   │   ├── spacing.js              # Spacing system
│   │   │   │   ├── shadows.js              # Shadow definitions
│   │   │   │   └── animations.js           # Keyframe animations
│   │   │   ├── components/                 # ATUM UI Components
│   │   │   │   ├── AtumShell.jsx           # Main layout shell
│   │   │   │   ├── AtumCard.jsx            # Glass card
│   │   │   │   ├── AtumButton.jsx          # Button variants
│   │   │   │   ├── AtumInput.jsx           # Input fields
│   │   │   │   ├── AtumSelect.jsx          # Dropdowns
│   │   │   │   ├── AtumTextarea.jsx        # Multi-line input
│   │   │   │   ├── AtumTable.jsx           # Data tables
│   │   │   │   ├── AtumPill.jsx            # Status/priority badges
│   │   │   │   ├── AtumModal.jsx           # Dialog modal
│   │   │   │   ├── AtumToast.jsx           # Notifications
│   │   │   │   ├── AtumTabs.jsx            # Tab navigation
│   │   │   │   ├── AtumDropzone.jsx        # File upload zone
│   │   │   │   ├── AtumSearch.jsx          # Search input
│   │   │   │   ├── AtumSidebar.jsx         # Navigation sidebar
│   │   │   │   ├── AtumHeader.jsx          # Top header bar
│   │   │   │   ├── AtumTimeline.jsx        # Activity timeline
│   │   │   │   ├── AtumChart.jsx           # Analytics charts
│   │   │   │   └── AtumRichText.jsx        # Rich text editor
│   │   │   └── layouts/                    # Layout components
│   │   │       ├── PortalLayout.jsx        # Customer portal layout
│   │   │       └── DeskLayout.jsx          # Staff desk layout
│   │   ├── components/                     # Feature components
│   │   │   ├── auth/
│   │   │   │   ├── LoginForm.jsx
│   │   │   │   ├── TwoFactorForm.jsx
│   │   │   │   └── PasswordReset.jsx
│   │   │   ├── tickets/
│   │   │   │   ├── TicketList.jsx
│   │   │   │   ├── TicketDetail.jsx
│   │   │   │   ├── TicketForm.jsx
│   │   │   │   ├── TicketFilters.jsx
│   │   │   │   ├── TicketTimeline.jsx
│   │   │   │   ├── TicketRelationships.jsx
│   │   │   │   └── TicketTimeTracking.jsx
│   │   │   ├── comments/
│   │   │   │   ├── CommentThread.jsx
│   │   │   │   ├── CommentForm.jsx
│   │   │   │   └── CommentTypes.jsx
│   │   │   ├── kb/
│   │   │   │   ├── KBArticle.jsx
│   │   │   │   ├── KBCategory.jsx
│   │   │   │   ├── KBSearch.jsx
│   │   │   │   └── KBEditor.jsx
│   │   │   ├── dashboard/
│   │   │   │   ├── DashboardStats.jsx
│   │   │   │   ├── DashboardCharts.jsx
│   │   │   │   ├── DashboardQueue.jsx
│   │   │   │   └── DashboardActivity.jsx
│   │   │   ├── ai/
│   │   │   │   ├── TriagePanel.jsx
│   │   │   │   ├── SuggestionPanel.jsx
│   │   │   │   └── SimilarTickets.jsx
│   │   │   └── common/
│   │   │       ├── FileUploader.jsx
│   │   │       ├── FilePreview.jsx
│   │   │       ├── StatusBadge.jsx
│   │   │       ├── PriorityBadge.jsx
│   │   │       ├── UserAvatar.jsx
│   │   │       ├── SearchFilters.jsx
│   │   │       ├── CannedResponsePicker.jsx
│   │   │       ├── TimeTracker.jsx
│   │   │       ├── CustomFieldRenderer.jsx
│   │   │       ├── CSATWidget.jsx
│   │   │       ├── AuditLogViewer.jsx
│   │   │       └── RealTimeIndicator.jsx
│   │   ├── pages/                          # Route pages
│   │   │   ├── LandingPage.jsx             # ATUM landing (clone)
│   │   │   ├── portal/
│   │   │   │   ├── PortalLogin.jsx
│   │   │   │   ├── PortalTickets.jsx
│   │   │   │   ├── PortalTicketNew.jsx
│   │   │   │   ├── PortalTicketDetail.jsx
│   │   │   │   └── PortalKnowledgeBase.jsx
│   │   │   └── desk/
│   │   │       ├── DeskLogin.jsx
│   │   │       ├── DeskDashboard.jsx
│   │   │       ├── DeskInbox.jsx
│   │   │       ├── DeskTicketDetail.jsx
│   │   │       ├── DeskReports.jsx
│   │   │       ├── DeskAdmin.jsx
│   │   │       ├── DeskKBAdmin.jsx
│   │   │       ├── DeskCannedResponses.jsx
│   │   │       └── DeskCustomFields.jsx
│   │   ├── hooks/                          # Custom React hooks
│   │   │   ├── useAuth.js
│   │   │   ├── useTickets.js
│   │   │   ├── useWebSocket.js
│   │   │   ├── useSearch.js
│   │   │   └── useRealtime.js
│   │   ├── contexts/                       # React contexts
│   │   │   ├── AuthContext.jsx
│   │   │   ├── TicketContext.jsx
│   │   │   └── RealtimeContext.jsx
│   │   ├── api/                            # API client
│   │   │   ├── client.js                   # Axios instance
│   │   │   ├── auth.js
│   │   │   ├── tickets.js
│   │   │   ├── comments.js
│   │   │   ├── attachments.js
│   │   │   ├── kb.js
│   │   │   ├── dashboard.js
│   │   │   ├── search.js
│   │   │   └── ai.js
│   │   ├── utils/                          # Frontend utilities
│   │   │   ├── formatters.js
│   │   │   ├── validators.js
│   │   │   └── constants.js
│   │   └── router.jsx                      # React Router config
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── eslint.config.js
│
├── infra/                                  # Infrastructure
│   ├── nginx/
│   │   └── atum-desk.conf                  # nginx site config
│   ├── systemd/
│   │   ├── atum-desk-api.service           # API service
│   │   ├── atum-desk-ws.service            # WebSocket service
│   │   └── atum-desk-worker.service        # Celery worker
│   ├── scripts/
│   │   ├── install.sh                      # Installation script
│   │   ├── setup-db.sh                     # Database setup
│   │   ├── setup-ssl.sh                    # SSL certificate setup
│   │   ├── backup.sh                       # Backup script
│   │   └── update.sh                       # Update script
│   └── config/
│       ├── postgresql.conf                 # PostgreSQL tuning
│       ├── redis.conf                      # Redis config
│       └── ollama.service                  # Ollama systemd unit
│
├── docs/                                   # Documentation
│   ├── ATUM_UI_AUDIT.md                    # Brand specifications
│   ├── RUNBOOK.md                          # Operations guide
│   ├── ACCEPTANCE_TESTS.md                 # E2E test procedures
│   ├── API_REFERENCE.md                    # API documentation
│   ├── DEPLOYMENT.md                       # Deployment guide
│   ├── SECURITY.md                         # Security hardening
│   └── TROUBLESHOOTING.md                  # Common issues
│
└── data/                                   # Runtime data (gitignored)
    ├── uploads/                            # File attachments
    ├── exports/                            # Export files
    └── backups/                            # Database backups
```

---

## 🗄️ DATABASE SCHEMA

### Core Tables

```sql
-- Organizations (Multi-tenant root)
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    domain VARCHAR(255),
    settings JSONB DEFAULT '{}',
    business_hours JSONB,                    -- Enhanced: Business hours config
    holidays JSONB,                          -- Enhanced: Holiday calendar
    allowed_ips INET[],                      -- Enhanced: IP restrictions
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Users with RBAC
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('customer_user', 'customer_admin', 'agent', 'manager', 'admin')),
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    last_login TIMESTAMP WITH TIME ZONE,
    
    -- Enhanced: 2FA fields
    two_factor_enabled BOOLEAN DEFAULT false,
    two_factor_secret VARCHAR(255),
    two_factor_backup_codes VARCHAR(255)[],
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(organization_id, email)
);

-- Services (Ticket categories)
CREATE TABLE services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    default_priority VARCHAR(20) DEFAULT 'medium',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tickets (Core entity)
CREATE TABLE tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    requester_id UUID REFERENCES users(id),
    service_id UUID REFERENCES services(id),
    
    -- Ticket content
    subject VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    
    -- Status workflow
    status VARCHAR(50) NOT NULL DEFAULT 'new' CHECK (status IN ('new', 'accepted', 'assigned', 'in_progress', 'waiting_customer', 'resolved', 'closed', 'cancelled')),
    
    -- Assignment
    assigned_to UUID REFERENCES users(id),
    accepted_by UUID REFERENCES users(id),
    accepted_at TIMESTAMP WITH TIME ZONE,
    
    -- Priority & categorization
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    
    -- SLA tracking
    sla_policy_id UUID REFERENCES sla_policies(id),
    sla_started_at TIMESTAMP WITH TIME ZONE,
    sla_due_at TIMESTAMP WITH TIME ZONE,
    sla_paused_at TIMESTAMP WITH TIME ZONE,
    sla_paused_duration INTEGER DEFAULT 0,   -- seconds
    
    -- Enhanced: Ticket relationships
    parent_ticket_id UUID REFERENCES tickets(id),
    is_duplicate_of UUID REFERENCES tickets(id),
    
    -- Enhanced: AI triage
    ai_suggested_category VARCHAR(255),
    ai_suggested_priority VARCHAR(20),
    ai_confidence_score FLOAT,
    ai_embedding VECTOR(1536),               -- pgvector extension
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE,
    closed_at TIMESTAMP WITH TIME ZONE
);

-- Comments (Public and internal)
CREATE TABLE comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticket_id UUID REFERENCES tickets(id),
    author_id UUID REFERENCES users(id),
    content TEXT NOT NULL,
    is_internal BOOLEAN DEFAULT false,       -- Internal notes hidden from customer
    is_ai_generated BOOLEAN DEFAULT false,   -- Enhanced: AI-drafted responses
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Attachments
CREATE TABLE attachments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticket_id UUID REFERENCES tickets(id),
    comment_id UUID REFERENCES comments(id),
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    file_hash VARCHAR(64) NOT NULL,          -- SHA-256 for integrity
    uploaded_by UUID REFERENCES users(id),
    access_count INTEGER DEFAULT 0,          -- Audit tracking
    last_accessed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- SLA Policies (Enhanced with business hours)
CREATE TABLE sla_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Response times (minutes)
    response_time_low INTEGER,
    response_time_medium INTEGER,
    response_time_high INTEGER,
    response_time_urgent INTEGER,
    
    -- Resolution times (minutes)
    resolution_time_low INTEGER,
    resolution_time_medium INTEGER,
    resolution_time_high INTEGER,
    resolution_time_urgent INTEGER,
    
    -- Enhanced: Business hours config
    business_hours_enabled BOOLEAN DEFAULT false,
    business_hours_schedule JSONB,           -- {"monday": {"start": "09:00", "end": "17:00"}}
    timezone VARCHAR(50) DEFAULT 'UTC',
    
    -- Enhanced: Escalation rules
    escalation_enabled BOOLEAN DEFAULT false,
    escalation_rules JSONB,                  -- [{"threshold": 80, "notify": ["manager"]}]
    
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enhanced: Time tracking
CREATE TABLE time_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticket_id UUID REFERENCES tickets(id),
    user_id UUID REFERENCES users(id),
    duration_minutes INTEGER NOT NULL,       -- Duration in minutes
    description TEXT,
    is_billable BOOLEAN DEFAULT true,
    started_at TIMESTAMP WITH TIME ZONE,
    ended_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enhanced: Ticket relationships
CREATE TABLE ticket_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_ticket_id UUID REFERENCES tickets(id),
    target_ticket_id UUID REFERENCES tickets(id),
    relationship_type VARCHAR(50) NOT NULL CHECK (relationship_type IN ('parent', 'child', 'duplicate', 'related', 'blocked_by', 'blocks')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(source_ticket_id, target_ticket_id, relationship_type)
);

-- Enhanced: Custom fields
CREATE TABLE custom_fields (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    name VARCHAR(255) NOT NULL,
    field_type VARCHAR(50) NOT NULL CHECK (field_type IN ('text', 'number', 'date', 'dropdown', 'checkbox', 'multiselect')),
    options JSONB,                           -- For dropdown/multiselect
    is_required BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE custom_field_values (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    custom_field_id UUID REFERENCES custom_fields(id),
    ticket_id UUID REFERENCES tickets(id),
    value JSONB NOT NULL,                    -- Store as JSON for flexibility
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(custom_field_id, ticket_id)
);

-- Enhanced: Canned responses
CREATE TABLE canned_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    shortcut VARCHAR(50),                    -- e.g., "/greeting"
    category VARCHAR(100),
    is_personal BOOLEAN DEFAULT false,       -- Personal vs shared
    created_by UUID REFERENCES users(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enhanced: Knowledge Base
CREATE TABLE kb_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    parent_id UUID REFERENCES kb_categories(id),
    is_internal BOOLEAN DEFAULT false,       -- Internal only
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE kb_articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id UUID REFERENCES kb_categories(id),
    organization_id UUID REFERENCES organizations(id),
    title VARCHAR(500) NOT NULL,
    slug VARCHAR(500) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    excerpt TEXT,
    is_internal BOOLEAN DEFAULT false,       -- Internal vs customer-facing
    is_published BOOLEAN DEFAULT false,
    view_count INTEGER DEFAULT 0,
    helpful_count INTEGER DEFAULT 0,
    unhelpful_count INTEGER DEFAULT 0,
    
    -- Enhanced: Search
    search_vector TSVECTOR,                  -- Full-text search
    
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enhanced: CSAT Surveys
CREATE TABLE csat_surveys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticket_id UUID REFERENCES tickets(id),
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    respondent_email VARCHAR(255),
    is_internal BOOLEAN DEFAULT false,       -- Internal agent rating
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audit Log (Enhanced - Immutable)
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,            -- e.g., "ticket_created", "ticket_accepted"
    entity_type VARCHAR(100) NOT NULL,       -- e.g., "ticket", "comment", "attachment"
    entity_id UUID NOT NULL,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
) WITH (fillfactor=100);                     -- Prevent updates (append-only)

-- Prevent updates/deletes on audit log
CREATE OR REPLACE FUNCTION prevent_audit_modification()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Audit log entries cannot be modified or deleted';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER audit_log_immutable
    BEFORE UPDATE OR DELETE ON audit_log
    FOR EACH ROW EXECUTE FUNCTION prevent_audit_modification();
```

### Indexes for Performance

```sql
-- Tenant isolation indexes
CREATE INDEX idx_tickets_org ON tickets(organization_id);
CREATE INDEX idx_tickets_requester ON tickets(requester_id);
CREATE INDEX idx_comments_ticket ON comments(ticket_id);
CREATE INDEX idx_attachments_ticket ON attachments(ticket_id);

-- Status/workflow indexes
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_assigned ON tickets(assigned_to);
CREATE INDEX idx_tickets_sla_due ON tickets(sla_due_at) WHERE sla_due_at IS NOT NULL;

-- Enhanced: Full-text search indexes
CREATE INDEX idx_tickets_search ON tickets USING GIN(to_tsvector('english', subject || ' ' || COALESCE(description, '')));
CREATE INDEX idx_kb_articles_search ON kb_articles USING GIN(search_vector);

-- Enhanced: Time-based queries
CREATE INDEX idx_tickets_created ON tickets(created_at);
CREATE INDEX idx_audit_created ON audit_log(created_at);
CREATE INDEX idx_time_entries_ticket ON time_entries(ticket_id);

-- Enhanced: Vector search (pgvector extension required)
CREATE INDEX idx_tickets_embedding ON tickets USING ivfflat (ai_embedding vector_cosine_ops);
```

---

## 🔌 API ENDPOINTS

### Authentication
```
POST   /api/v1/auth/login                    # Email/password login
POST   /api/v1/auth/2fa/setup               # Setup 2FA (TOTP)
POST   /api/v1/auth/2fa/verify              # Verify 2FA code
POST   /api/v1/auth/logout                  # Logout
POST   /api/v1/auth/refresh                 # Refresh JWT token
POST   /api/v1/auth/password/reset          # Request password reset
POST   /api/v1/auth/password/change         # Change password
GET    /api/v1/me                           # Get current user
PUT    /api/v1/me                           # Update profile
```

### Organizations (Admin only)
```
GET    /api/v1/organizations                # List organizations
POST   /api/v1/organizations                # Create organization
GET    /api/v1/organizations/:id            # Get organization
PUT    /api/v1/organizations/:id            # Update organization
DELETE /api/v1/organizations/:id            # Delete organization
GET    /api/v1/organizations/:id/stats      # Organization stats
```

### Users
```
GET    /api/v1/users                        # List users (manager+)
POST   /api/v1/users                        # Create user (manager+)
GET    /api/v1/users/:id                    # Get user
PUT    /api/v1/users/:id                    # Update user
DELETE /api/v1/users/:id                    # Deactivate user
GET    /api/v1/users/:id/tickets            # Get user's tickets
GET    /api/v1/users/:id/time-entries       # Get user's time entries
```

### Tickets (Customer Portal)
```
GET    /api/v1/tickets                      # List my tickets
POST   /api/v1/tickets                      # Create ticket
GET    /api/v1/tickets/:id                  # Get ticket detail
POST   /api/v1/tickets/:id/comments         # Add comment
POST   /api/v1/tickets/:id/attachments      # Upload attachment
GET    /api/v1/tickets/:id/attachments/:aid # Download attachment
```

### Internal Tickets (Staff)
```
GET    /api/v1/internal/tickets             # List all tickets (with filters)
GET    /api/v1/internal/tickets/new         # NEW tickets queue (manager inbox)
GET    /api/v1/internal/tickets/assigned    # My assigned tickets
GET    /api/v1/internal/tickets/unassigned  # Unassigned tickets
GET    /api/v1/internal/tickets/:id         # Get ticket (full detail)

POST   /api/v1/internal/tickets/:id/accept  # Manager accepts ticket
POST   /api/v1/internal/tickets/:id/assign  # Assign to agent
POST   /api/v1/internal/tickets/:id/unassign # Unassign ticket
POST   /api/v1/internal/tickets/:id/status  # Change status
POST   /api/v1/internal/tickets/:id/priority # Change priority
POST   /api/v1/internal/tickets/:id/service # Change service

POST   /api/v1/internal/tickets/:id/comments           # Add comment
POST   /api/v1/internal/tickets/:id/comments/internal  # Add internal note

GET    /api/v1/internal/tickets/:id/time-entries       # Get time entries
POST   /api/v1/internal/tickets/:id/time-entries       # Log time
PUT    /api/v1/internal/tickets/:id/time-entries/:eid  # Edit time entry
DELETE /api/v1/internal/tickets/:id/time-entries/:eid  # Delete time entry

GET    /api/v1/internal/tickets/:id/relationships      # Get relationships
POST   /api/v1/internal/tickets/:id/relationships      # Create relationship
DELETE /api/v1/internal/tickets/:id/relationships/:rid # Remove relationship

GET    /api/v1/internal/tickets/:id/audit             # Get audit log
```

### Attachments
```
GET    /api/v1/attachments/:id              # Get attachment metadata
GET    /api/v1/attachments/:id/download     # Download file
DELETE /api/v1/attachments/:id              # Delete attachment (admin only)
```

### SLA Management
```
GET    /api/v1/sla/policies                 # List SLA policies
POST   /api/v1/sla/policies                 # Create SLA policy
GET    /api/v1/sla/policies/:id             # Get SLA policy
PUT    /api/v1/sla/policies/:id             # Update SLA policy
DELETE /api/v1/sla/policies/:id             # Delete SLA policy
GET    /api/v1/sla/breaches                 # List SLA breaches
GET    /api/v1/sla/metrics                  # SLA metrics
```

### Knowledge Base
```
GET    /api/v1/kb/categories                # List KB categories
POST   /api/v1/kb/categories                # Create category (admin)
GET    /api/v1/kb/categories/:id            # Get category
PUT    /api/v1/kb/categories/:id            # Update category
DELETE /api/v1/kb/categories/:id            # Delete category

GET    /api/v1/kb/articles                  # List articles
POST   /api/v1/kb/articles                  # Create article
GET    /api/v1/kb/articles/:id              # Get article
GET    /api/v1/kb/articles/:slug            # Get article by slug
PUT    /api/v1/kb/articles/:id              # Update article
DELETE /api/v1/kb/articles/:id              # Delete article
POST   /api/v1/kb/articles/:id/helpful      # Mark as helpful
POST   /api/v1/kb/articles/:id/unhelpful    # Mark as unhelpful
```

### Canned Responses
```
GET    /api/v1/canned-responses             # List canned responses
POST   /api/v1/canned-responses             # Create canned response
GET    /api/v1/canned-responses/:id         # Get canned response
PUT    /api/v1/canned-responses/:id         # Update canned response
DELETE /api/v1/canned-responses/:id         # Delete canned response
GET    /api/v1/canned-responses/search      # Search canned responses
```

### Custom Fields
```
GET    /api/v1/custom-fields                # List custom fields
POST   /api/v1/custom-fields                # Create custom field
GET    /api/v1/custom-fields/:id            # Get custom field
PUT    /api/v1/custom-fields/:id            # Update custom field
DELETE /api/v1/custom-fields/:id            # Delete custom field
```

### Search
```
GET    /api/v1/search                       # Global search
GET    /api/v1/search/tickets               # Search tickets only
GET    /api/v1/search/kb                    # Search knowledge base
GET    /api/v1/search/suggestions           # Autocomplete suggestions
```

### Dashboard & Analytics
```
GET    /api/v1/dashboard/stats              # Dashboard statistics
GET    /api/v1/dashboard/queue              # Queue metrics
GET    /api/v1/dashboard/activity           # Recent activity
GET    /api/v1/dashboard/agent-performance  # Agent performance (manager+)
GET    /api/v1/dashboard/trends             # Ticket trends
GET    /api/v1/dashboard/sla-compliance     # SLA compliance report
GET    /api/v1/dashboard/csat               # CSAT scores
```

### Audit Log
```
GET    /api/v1/audit                        # Query audit log
GET    /api/v1/audit/export                 # Export audit log (CSV/PDF)
GET    /api/v1/audit/entity/:type/:id       # Audit for specific entity
```

### AI Integration
```
GET    /api/v1/ai/triage/:ticket_id         # Get AI triage suggestions
POST   /api/v1/ai/suggest-response          # Get AI response suggestions
GET    /api/v1/ai/similar-tickets/:ticket_id # Find similar tickets
GET    /api/v1/ai/suggest-kb/:ticket_id     # Suggest KB articles
```

### CSAT
```
GET    /api/v1/csat/surveys                 # List CSAT surveys
POST   /api/v1/csat/surveys                 # Submit CSAT (public)
GET    /api/v1/csat/metrics                 # CSAT metrics
GET    /api/v1/csat/ticket/:ticket_id       # Get ticket CSAT
```

### WebSocket (Real-time)
```
WS     /ws/v1/notifications                 # Real-time notifications
WS     /ws/v1/ticket/:id                    # Ticket activity stream
```

---

## 🎨 UI ROUTES

### Public
```
GET    /                          # Landing page (ATUM clone)
GET    /login                     # Universal login portal
```

### Customer Portal
```
GET    /portal                    # Portal home
GET    /portal/login              # Customer login
GET    /portal/tickets            # My tickets list
GET    /portal/tickets/new        # Create new ticket
GET    /portal/tickets/:id        # Ticket detail
GET    /portal/kb                 # Knowledge base
GET    /portal/kb/:slug           # KB article
```

### Staff Desk
```
GET    /desk                      # Dashboard (redirect)
GET    /desk/login                # Staff login
GET    /desk/dashboard            # Dashboard with stats
GET    /desk/inbox                # NEW tickets queue
GET    /desk/tickets              # All tickets (search/filter)
GET    /desk/tickets/:id          # Ticket detail
GET    /desk/reports              # Reports & analytics
GET    /desk/admin                # Admin panel
GET    /desk/admin/users          # User management
GET    /desk/admin/organizations  # Organization settings
GET    /desk/admin/services       # Service management
GET    /desk/admin/sla            # SLA policies
GET    /desk/admin/kb             # Knowledge base admin
GET    /desk/admin/canned         # Canned responses
GET    /desk/admin/fields         # Custom fields
GET    /desk/admin/audit          # Audit log viewer
GET    /desk/profile              # My profile
```

---

## 🔒 SECURITY IMPLEMENTATION

### Authentication
- [ ] JWT tokens with refresh token rotation
- [ ] bcrypt password hashing (cost factor 12)
- [ ] Rate limiting: 5 login attempts per 15 minutes per IP
- [ ] Session timeout: 8 hours
- [ ] Concurrent session limit: 3 per user

### Two-Factor Authentication (2FA)
- [ ] TOTP (Time-based One-Time Password) using RFC 6238
- [ ] QR code generation for setup
- [ ] Backup codes (10 single-use codes)
- [ ] 2FA enforced for admin/manager roles (optional)

### Authorization (RBAC)
```
customer_user:     View own tickets, create tickets, add comments, view KB
customer_admin:    All customer_user + view org tickets, manage org users
agent:             View assigned tickets, update tickets, add internal notes
manager:           All agent + accept tickets, assign tickets, view all tickets, view reports
admin:             Full system access, manage all settings
```

### Multi-Tenant Isolation
- [ ] Every query filtered by organization_id
- [ ] Database-level RLS (Row Level Security) policies
- [ ] Subdomain-based organization resolution
- [ ] IP restrictions per organization

### Upload Security
- [ ] File type whitelist: images, documents, archives
- [ ] Max file size: 50MB
- [ ] Filename sanitization (UUID + safe characters only)
- [ ] Storage outside web root
- [ ] SHA-256 hash verification
- [ ] Virus scanning (ClamAV integration - optional)

### Audit & Compliance
- [ ] Immutable audit log (append-only)
- [ ] All state changes logged with before/after values
- [ ] IP address and user agent tracking
- [ ] GDPR-compliant data export/deletion
- [ ] Data retention policies (configurable)

### Rate Limiting
```
Auth endpoints:         5 requests per 15 minutes
Ticket creation:        10 tickets per hour per user
API general:            100 requests per minute per user
WebSocket connections:  5 concurrent per user
```

### Network Security
- [ ] HTTPS only (TLS 1.3)
- [ ] HSTS headers
- [ ] Secure cookies (HttpOnly, Secure, SameSite)
- [ ] CORS configured for same-origin
- [ ] IP allowlists for desk access (optional)
- [ ] WAF rules (via nginx)

---

## ⚡ PERFORMANCE OPTIMIZATION

### Database
- [ ] Connection pooling (PgBouncer)
- [ ] Query optimization with EXPLAIN ANALYZE
- [ ] Materialized views for dashboards
- [ ] Partitioning for audit_log (by month)
- [ ] Read replicas for reporting (future)

### Caching (Redis)
- [ ] Session storage
- [ ] Rate limiting counters
- [ ] Dashboard stats (5-minute TTL)
- [ ] KB article cache
- [ ] Query result cache

### Frontend
- [ ] Code splitting by route
- [ ] Lazy loading for heavy components
- [ ] Image optimization
- [ ] Service worker for offline access
- [ ] Debounced search inputs

### WebSocket
- [ ] Connection poolinghttps://github.com/ibredas/ATUM_DESK-.git
- [ ] Event batching
- [ ] Automatic reconnection
- [ ] Presence tracking (who's viewing ticket)

---

## 🤖 AI INTEGRATION (OLLAMA)

### Setup
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull models
ollama pull qwen2.5-coder:7b    # Code/structure understanding
ollama pull nomic-embed-text     # Embeddings for similarity
ollama pull llama3.1:8b          # General reasoning
```

### Features

#### 1. Smart Triage (Advisory Only)
- [ ] Analyze ticket content
- [ ] Suggest category (service)
- [ ] Suggest priority
- [ ] Confidence score
- [ ] Similar tickets lookup

#### 2. Response Suggestions
- [ ] Draft response based on context
- [ ] Tone adjustment options
- [ ] Grammar/spelling check
- [ ] Canned response matching

#### 3. Knowledge Base Integration
- [ ] Suggest relevant articles
- [ ] Auto-article generation from tickets
- [ ] Content gap analysis

#### 4. Embeddings & Similarity
- [ ] Generate embeddings for all tickets
- [ ] Find similar resolved tickets
- [ ] KB article recommendations
- [ ] Duplicate ticket detection

---

## 📊 ACCEPTANCE TESTS

### Test 1: End-to-End First Ticket
```gherkin
Feature: Complete ticket lifecycle

Scenario: Customer creates ticket, staff processes it
  Given a customer user exists
  And a manager user exists
  And an agent user exists
  And services are configured
  
  # Customer creates ticket
  When the customer logs in
  And creates a ticket with subject "Cannot login"
  And attaches "screenshot.png"
  Then the ticket status is "NEW"
  And the ticket appears in the manager inbox
  
  # Manager accepts
  When the manager logs in
  And views the inbox
  And accepts the ticket
  Then the ticket status is "ACCEPTED"
  And SLA timer starts
  And audit log records "ticket_accepted"
  
  # Manager assigns
  When the manager assigns the ticket to the agent
  Then the ticket status is "ASSIGNED"
  And the agent receives notification
  
  # Agent works
  When the agent logs in
  And adds an internal note "Investigating..."
  And adds a public comment "Working on this"
  Then the customer sees the public comment
  And the customer does NOT see the internal note
  
  # Wait for customer
  When the agent changes status to "WAITING_CUSTOMER"
  Then the SLA timer pauses
  
  # Customer replies
  When the customer adds a comment
  Then the ticket returns to "IN_PROGRESS"
  And the SLA timer resumes
  
  # Resolution
  When the agent resolves the ticket
  Then the ticket status is "RESOLVED"
  And customer receives satisfaction survey
  
  # Closure
  When the customer submits CSAT rating 5 stars
  And the manager closes the ticket
  Then the ticket status is "CLOSED"
  And the ticket is read-only
```

### Test 2: Real-time Updates
```gherkin
Feature: WebSocket real-time updates

Scenario: Multiple users see updates instantly
  Given customer and agent are viewing the same ticket
  When the customer adds a comment
  Then the agent sees the comment within 2 seconds
  And a notification appears
```

### Test 3: SLA Compliance
```gherkin
Feature: SLA calculations

Scenario: Business hours and pauses
  Given a ticket with 4-hour SLA
  And business hours are 9-5 weekdays
  When the ticket is accepted at 4 PM Friday
  Then the SLA due is 11 AM Monday
  
  When the ticket moves to WAITING_CUSTOMER
  Then the SLA timer pauses
  
  When the customer replies 24 hours later
  Then the SLA due extends by 24 hours
```

### Test 4: Security & RBAC
```gherkin
Feature: Role-based access control

Scenario: Tenant isolation
  Given customer A from Org 1
  And customer B from Org 2
  When customer A creates a ticket
  Then customer B cannot see the ticket
  And the API returns 404 for customer B
  
Scenario: Admin access
  Given an agent tries to access admin panel
  Then access is denied (403)
  
Scenario: Audit trail
  Given a manager accepts a ticket
  Then the audit log contains:
    - User ID
    - Action: ticket_accepted
    - Timestamp
    - IP address
```

### Test 5: AI Features
```gherkin
Feature: AI assistance

Scenario: Smart triage
  Given a ticket with content "Server down, urgent!"
  When AI triage is requested
  Then AI suggests priority: "urgent"
  And confidence score > 0.7
  
Scenario: Similar tickets
  Given a ticket about "password reset"
  When similar tickets are requested
  Then tickets with similar content are returned
  
Scenario: Response suggestion
  Given a ticket about login issues
  When AI response is requested
  Then a helpful response is generated
```

---

## 🚀 DEPLOYMENT STEPS

### Prerequisites
```bash
# System packages
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip postgresql-15 redis-server nginx git

# Node.js 20+
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

### Installationhttps://github.com/ibredas/ATUM_DESK-.git
```bash
# 1. Clone repository
cd /opt
git clone <repository> atum-desk
cd atum-desk

# 2. Run install script
sudo ./infra/scripts/install.sh

# 3. Configure environment
sudo nano /opt/atum-desk/api/.env

# 4. Initialize database
sudo ./infra/scripts/setup-db.sh

# 5. Start services
sudo systemctl start atum-desk-api
sudo systemctl start atum-desk-ws
sudo systemctl start atum-desk-worker

# 6. Configure nginx
sudo cp infra/nginx/atum-desk.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/atum-desk.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Verification
```bash
# Check services
sudo systemctl status atum-desk-api
sudo systemctl status atum-desk-ws
sudo systemctl status atum-desk-worker

# Check logs
sudo journalctl -u atum-desk-api -f

# Run acceptance tests
cd /opt/atum-desk/api
python -m pytest tests/e2e/
```

---

## 📈 SUCCESS METRICS

### Performance Targets
- Page load time: < 2 seconds
- API response time (p95): < 200ms
- WebSocket latency: < 100ms
- Concurrent users: 100+
- File upload: 50MB in < 30 seconds

### Quality Targets
- Test coverage: > 80%
- Zero critical security vulnerabilities
- 99.9% uptime
- < 0.1% error rate

### User Experience
- End-to-end ticket creation: < 2 minutes
- Manager accept-to-assign: < 1 minute
- Search results: < 500ms

---

## 📋 IMPLEMENTATION PHASES

### Phase 0: Foundation (Days 1-3)
- [ ] Create ATUM_UI_AUDIT.md
- [ ] Scaffold project structure
- [ ] Copy brand assets
- [ ] Setup PostgreSQL + Redis
- [ ] Initialize FastAPI app
- [ ] Setup Vite + React

### Phase 1: Core Backend (Days 4-8)
- [ ] Database models & migrations
- [ ] Authentication & RBAC
- [ ] Basic ticket CRUD
- [ ] Comments & attachments
- [ ] Audit logging
- [ ] Unit tests

### Phase 2: Advanced Backend (Days 9-13)
- [ ] SLA engine with business hours
- [ ] Time tracking
- [ ] Ticket relationships
- [ ] Custom fields
- [ ] Canned responses
- [ ] Knowledge Base
- [ ] CSAT surveys
- [ ] Search (full-text + pgvector)
- [ ] Dashboard analytics

### Phase 3: Web UI (Days 14-20)
- [ ] ATUM design system
- [ ] Landing page (exact clone)
- [ ] Portal UI (customer)
- [ ] Desk UI (staff)
- [ ] Real-time WebSocket
- [ ] File upload/download
- [ ] Search interface
- [ ] Dashboard charts

### Phase 4: AI Integration (Days 21-24)
- [ ] Ollama client
- [ ] Triage suggestions
- [ ] Response suggestions
- [ ] Similar tickets
- [ ] KB embeddings

### Phase 5: Operations (Days 25-27)
- [ ] nginx configuration
- [ ] systemd services
- [ ] Install scripts
- [ ] Backup scripts
- [ ] SSL setup

### Phase 6: Documentation & Testing (Days 28-30)
- [ ] RUNBOOK.md
- [ ] ACCEPTANCE_TESTS.md
- [ ] API documentation
- [ ] End-to-end testing
- [ ] Performance tuning
- [ ] Security audit

---

## 🎯 READY TO BUILD

This comprehensive plan includes **all enhancements**:
- ✅ Core ticketing with ACCEPT workflow
- ✅ Real-time WebSocket updates
- ✅ Advanced SLA with business hours
- ✅ Knowledge Base
- ✅ Canned responses
- ✅ Time tracking
- ✅ Ticket relationships
- ✅ Custom fields
- ✅ CSAT surveys
- ✅ Dashboard & analytics
- ✅ Full-text search
- ✅ AI triage (Ollama)
- ✅ 2FA & IP restrictions
- ✅ Immutable audit logshttps://github.com/ibredas/ATUM_DESK-.git

**Total Estimated Time**: 30 days  
**Complexity**: High  
**Result**: Enterprise-grade ticketing platform

---

*Document Version: 1.0*  
*Last Updated: 2026-02-12*  
*Status: Ready for Implementation*
