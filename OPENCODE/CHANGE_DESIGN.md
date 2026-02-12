# CHANGE_DESIGN.md
## ATUM DESK - Implementation Design Document

**Version**: 1.0  
**Date**: 2026-02-12  
**Status**: APPROVED for Implementation  
**Scope**: Complete ATUM DESK with all 14 enhancements (Option C)

---

## 1. GOALS & NON-GOALS

### Primary Goals
1. **Build** a production-grade ticketing system with ATUM branding
2. **Deploy** bare-metal using systemd + nginx (NO Docker)
3. **Integrate** local AI (Ollama + ATUM-DESK-AI model)
4. **Enable** real-time updates via WebSocket
5. **Support** multi-tenant organizations with RBAC
6. **Implement** comprehensive SLA management with business hours
7. **Provide** customer portal and staff desk interfaces
8. **Ensure** immutable audit trails for compliance

### Secondary Goals
1. **Knowledge Base** with full-text search
2. **Time tracking** for billing
3. **CSAT surveys** for satisfaction measurement
4. **Dashboard & analytics** for metrics
5. **AI triage** for ticket categorization
6. **2FA** for enhanced security
7. **IP restrictions** for access control

### Non-Goals (Out of Scope)
- ❌ Mobile native apps (web responsive only)
- ❌ External API integrations (all local)
- ❌ Docker/containerization
- ❌ Kubernetes orchestration
- ❌ Multi-region deployment
- ❌ Automatic ticket resolution (AI is advisory only)

---

## 2. SUCCESS METRICS

### Technical Metrics
| Metric | Target | Measurement |
|--------|--------|-------------|
| Page Load Time | < 2s | Lighthouse / Browser DevTools |
| API Response (p95) | < 200ms | Application logs |
| WebSocket Latency | < 100ms | Client-side measurement |
| Concurrent Users | 100+ | Load testing |
| Database Query Time | < 50ms | PostgreSQL logs |
| Test Coverage | > 80% | pytest coverage |
| Uptime | 99.9% | Monitoring |

### Functional Metrics
| Metric | Target | Measurement |
|--------|--------|-------------|
| Ticket Creation → Inbox | < 5s | E2E test |
| AI Triage Response | < 3s | API timing |
| File Upload (10MB) | < 10s | Manual test |
| Search Results | < 500ms | API timing |
| SLA Calculation Accuracy | 100% | Unit tests |

### Business Metrics
| Metric | Target | Measurement |
|--------|--------|-------------|
| First Ticket E2E | Working | Acceptance test |
| All 14 Features | Working | Feature checklist |
| Zero Security Issues | Pass | Security audit |

---

## 3. ARCHITECTURE MAP

### Service Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT BROWSER                        │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTPS (Port 443)
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
│   - REST API             │   Internal IPC     │   (Port 8001)│
│   - Authentication       │                    └──────────────┘
│   - Business Logic       │
└───────────┬──────────────┘
            │
    ┌───────┴───────┐
    ▼               ▼
┌─────────┐   ┌──────────┐   ┌──────────┐
│PostgreSQL│   │  Redis   │   │  Ollama  │
│(Port    │   │(Port     │   │(Port     │
│ 5432)   │   │ 6379)    │   │ 11434)   │
│         │   │          │   │          │
│- Primary│   │- Sessions│   │- AI      │
│- Data   │   │- Cache   │   │  Triage  │
│- Audit  │   │- Rate Lim│   │- Embed   │
└─────────┘   └──────────┘   └──────────┘
```

### Data Flow Map
```
1. TICKET CREATION FLOW:
   Customer → nginx → API → PostgreSQL
                          ↓
                    WebSocket emit
                          ↓
                    Staff Desk (real-time)

2. AUTHENTICATION FLOW:
   User → POST /auth/login → API → PostgreSQL (verify)
                                    ↓
                              JWT Token Generated
                                    ↓
                              Redis (session store)
                                    ↓
   Response: JWT + Refresh Token

3. FILE UPLOAD FLOW:
   User → POST /attachments → API → Validate (type, size, hash)
                                         ↓
                                   Save to /data/ATUM DESK/atum-desk/data/uploads/
                                         ↓
                                   PostgreSQL (metadata)
                                         ↓
                                   Response: download URL

4. AI TRIAGE FLOW:
   Ticket Created → API → Ollama (ATUM-DESK-AI)
                               ↓
                         Suggestions (JSON)
                               ↓
                         API Response
                               ↓
                         Staff Desk (advisory display)

5. SLA CALCULATION FLOW:
   Ticket Accepted → SLA Service → Check Business Hours
                                        ↓
                                  Calculate Due Date
                                        ↓
                                  PostgreSQL (update ticket)
                                        ↓
                                  Background Worker (monitor)
```

### Dependency Map
```
atum-desk-api
├── Requires: PostgreSQL (5432)
├── Requires: Redis (6379)
├── Requires: Ollama (11434) - optional
├── Provides: REST API (8000)
└── Used by: nginx, WebSocket

atum-desk-ws
├── Requires: atum-desk-api (auth validation)
├── Requires: Redis (pub/sub)
├── Provides: WebSocket (8001)
└── Used by: nginx

atum-desk-worker
├── Requires: Redis (Celery broker)
├── Requires: PostgreSQL
├── Provides: Background tasks
└── Used by: atum-desk-api

nginx
├── Requires: atum-desk-api (8000)
├── Requires: atum-desk-ws (8001) - via proxy
├── Provides: HTTPS (443)
└── Used by: Client browsers

PostgreSQL
├── Used by: atum-desk-api
├── Used by: atum-desk-worker
└── Provides: Data persistence

Redis
├── Used by: atum-desk-api (sessions, cache)
├── Used by: atum-desk-ws (pub/sub)
├── Used by: atum-desk-worker (Celery)
└── Provides: Caching, messaging

Ollama
├── Used by: atum-desk-api (AI service)
└── Provides: AI inference
```

---

## 4. PROPOSED APPROACH

### Phase 0: Foundation (Day 1)
**Goal**: Project scaffold and brand assets

**Tasks**:
1. Create directory structure
2. Set up Python virtual environment
3. Initialize React project with Vite
4. Create ATUM design system tokens
5. Generate brand assets (logo, wordmark, favicon)

**Deliverables**:
- `/atum-desk/api/` with requirements.txt
- `/atum-desk/web/` with package.json
- `/atum-desk/infra/` with systemd templates
- Brand assets in `/web/public/brand/`

### Phase 1: Core Backend (Days 2-4)
**Goal**: Database and essential API

**Tasks**:
1. SQLAlchemy models (core tables)
2. Alembic migrations
3. Authentication (JWT, bcrypt)
4. RBAC middleware
5. Core API endpoints:
   - Auth (/auth/*)
   - Users (/users/*)
   - Tickets (/tickets/*, /internal/tickets/*)
   - Comments (/comments/*)
6. Basic file upload

**Deliverables**:
- Working API on port 8000
- Database schema deployed
- Authentication functional
- Ticket CRUD operations

### Phase 2: Advanced Backend (Days 5-7)
**Goal**: Enhanced features and AI

**Tasks**:
1. SLA engine with business hours
2. Audit logging (immutable)
3. Email notifications (SMTP)
4. Ollama integration (ATUM-DESK-AI)
5. AI triage service
6. WebSocket manager
7. Celery background tasks
8. Advanced models:
   - Time entries
   - Ticket relationships
   - Custom fields
   - Canned responses
   - KB articles/categories
   - CSAT surveys

**Deliverables**:
- SLA calculations working
- AI suggestions functional
- WebSocket server on port 8001
- Background tasks processing

### Phase 3: Web UI (Days 8-11)
**Goal**: Complete frontend

**Tasks**:
1. ATUM component library
2. Landing page (ATUM clone)
3. Customer portal:
   - Login
   - Ticket list/create/detail
   - Knowledge base
4. Staff desk:
   - Login with 2FA
   - Dashboard
   - Inbox
   - Ticket management
   - Admin panels
5. WebSocket client integration
6. AI panels in desk interface

**Deliverables**:
- Built frontend in `/web/dist/`
- All routes functional
- Real-time updates working

### Phase 4: Operations (Days 12-13)
**Goal**: Production deployment

**Tasks**:
1. nginx configuration
2. systemd service units
3. Installation scripts
4. Database setup script
5. SSL setup (optional)
6. Backup script
7. Environment configuration

**Deliverables**:
- `atum-desk-api.service` (systemd)
- `atum-desk-ws.service` (systemd)
- `atum-desk-worker.service` (systemd)
- `install.sh` (one-command install)
- nginx site config

### Phase 5: Documentation & Testing (Day 14)
**Goal**: Quality assurance and docs

**Tasks**:
1. API documentation
2. RUNBOOK.md
3. ACCEPTANCE_TESTS.md
4. Security hardening guide
5. Unit tests (core logic)
6. Integration tests (API)
7. E2E test (first ticket)

**Deliverables**:
- Complete documentation
- Test suite passing
- First ticket E2E proof

---

## 5. ALTERNATIVES CONSIDERED

### Alternative A: Minimal MVP (Core Only)
**Scope**: Basic ticketing without enhancements
**Pros**:
- Faster delivery (5-7 days)
- Simpler codebase
- Lower risk

**Cons**:
- No AI features
- No real-time updates
- No SLA management
- Not competitive

**Verdict**: ❌ REJECTED - Does not meet requirements

### Alternative B: Standard Features (Option B)
**Scope**: Core + 7 enhancements
**Pros**:
- Moderate complexity
- Good feature set
- Reasonable timeline (10-12 days)

**Cons**:
- Missing AI triage
- Missing 2FA
- Missing IP restrictions

**Verdict**: ❌ REJECTED - Missing critical security and AI features

### Alternative C: Comprehensive (Option C) ✅ SELECTED
**Scope**: Core + all 14 enhancements
**Pros**:
- Complete feature set
- AI-powered assistance
- Enterprise security
- Competitive advantage

**Cons**:
- Higher complexity
- Longer timeline (14 days)
- More testing required

**Verdict**: ✅ APPROVED - Meets all requirements and vision

---

## 6. INTEGRATION PLAN

### Touchpoint 1: Database
**Integration**: PostgreSQL  
**Method**: SQLAlchemy async ORM  
**Config**: Connection pool, 20 connections max  
**Migration**: Alembic with version control  
**Backup**: pg_dump nightly

### Touchpoint 2: Cache
**Integration**: Redis  
**Method**: redis-py async client  
**Usage**: Sessions, rate limits, pub/sub  
**Config**: DB index 1 (separate from other uses)

### Touchpoint 3: Web Server
**Integration**: nginx  
**Method**: Reverse proxy + static files  
**Config**: 
- `/` → `/web/dist/index.html`
- `/api/*` → `http://localhost:8000`
- `/ws/*` → `http://localhost:8001` (WebSocket)

### Touchpoint 4: AI Service
**Integration**: Ollama HTTP API  
**Method**: httpx async client  
**Model**: ATUM-DESK-AI:latest  
**Fallback**: Circuit breaker, graceful degradation

### Touchpoint 5: Background Tasks
**Integration**: Celery + Redis  
**Method**: celery[redis] with async tasks  
**Tasks**: Email sending, SLA monitoring, AI embedding

### Touchpoint 6: File Storage
**Integration**: Local filesystem  
**Path**: `/data/ATUM DESK/atum-desk/data/uploads/`  
**Security**: UUID filenames, mime type validation, SHA-256 hash

---

## 7. VERIFICATION PLAN

### Unit Tests
```
Coverage Target: 80%+
Location: /api/tests/unit/
Framework: pytest
Test Files:
- test_auth.py (JWT, bcrypt, 2FA)
- test_models.py (SQLAlchemy models)
- test_sla.py (SLA calculations)
- test_permissions.py (RBAC)
- test_validators.py (input validation)
```

### Integration Tests
```
Location: /api/tests/integration/
Test Scenarios:
- Database connectivity
- Redis operations
- API endpoint responses
- Authentication flow
- File upload/download
- WebSocket connections
```

### E2E Tests (ACCEPTANCE_TESTS.md)
```
Test 1: First Ticket Lifecycle
- Customer creates ticket
- Manager accepts and assigns
- Agent works and resolves
- Customer rates (CSAT)
- Manager closes

Test 2: Real-time Updates
- WebSocket notifications
- Multi-user viewing

Test 3: SLA Compliance
- Business hours calculation
- Pause on waiting customer

Test 4: Security & RBAC
- Tenant isolation
- Role-based access
- Audit trail

Test 5: AI Features
- Triage suggestions
- Similar tickets
- Response suggestions
```

### Smoke Tests
```
Checklist:
- [ ] Service starts without errors
- [ ] API responds to /health
- [ ] Database connection OK
- [ ] Redis connection OK
- [ ] Ollama reachable (optional)
- [ ] nginx proxies correctly
- [ ] Frontend loads
- [ ] Login works
- [ ] Ticket creation works
```

---

## 8. ROLLBACK PLAN

### Rollback Triggers
1. Service fails to start
2. Database migration error
3. API returns 500 errors
4. Security vulnerability detected
5. Performance unacceptable

### Rollback Steps
```bash
# Step 1: Stop services
sudo systemctl stop atum-desk-worker
sudo systemctl stop atum-desk-ws
sudo systemctl stop atum-desk-api

# Step 2: Disable services
sudo systemctl disable atum-desk-worker
sudo systemctl disable atum-desk-ws
sudo systemctl disable atum-desk-api

# Step 3: Restore nginx
sudo rm -f /etc/nginx/sites-enabled/atum-desk.conf
sudo nginx -t
sudo systemctl reload nginx

# Step 4: Restore database (if needed)
# sudo -u postgres dropdb atum_desk
# sudo -u postgres pg_restore -d atum_desk backup.dump

# Step 5: Remove installation
sudo rm -rf /data/ATUM DESK/atum-desk

# Step 6: Remove systemd units
sudo rm -f /etc/systemd/system/atum-desk-*.service
sudo systemctl daemon-reload
```

### Data Preservation
- Database backups before migrations
- Upload files preserved in separate backup
- Configuration files backed up

---

## 9. TECHNOLOGY CHOICES

### Backend
| Component | Choice | Rationale |
|-----------|--------|-----------|
| Framework | FastAPI | Modern, async, automatic docs |
| ORM | SQLAlchemy 2.0 | Mature, async support |
| Migrations | Alembic | Industry standard |
| Auth | python-jose + passlib | JWT + bcrypt |
| HTTP Client | httpx | Async, modern |
| Tasks | Celery | Battle-tested background jobs |
| Logging | structlog | Structured logging |

### Frontend
| Component | Choice | Rationale |
|-----------|--------|-----------|
| Framework | React 19 | Latest features |
| Build Tool | Vite 7 | Fast dev, optimized builds |
| Styling | Tailwind CSS v4 | Utility-first, ATUM compatible |
| Router | React Router DOM v6 | Standard routing |
| Charts | Recharts | React-native charts |
| HTTP | Axios | Mature HTTP client |
| WebSocket | Socket.io-client | Reliable real-time |

### Database
| Component | Choice | Rationale |
|-----------|--------|-----------|
| Primary | PostgreSQL 16 | ACID, JSON support, full-text search |
| Extensions | pg_trgm, uuid-ossp | Search, UUID generation |
| Cache | Redis 7 | Sessions, pub/sub, rate limiting |

### AI
| Component | Choice | Rationale |
|-----------|--------|-----------|
| LLM | ATUM-DESK-AI (Ollama) | Custom model, local, fast |
| Embeddings | nomic-embed-text (Ollama) | Local embeddings |
| Vector Store | ChromaDB (optional) | Local vector search |

### Infrastructure
| Component | Choice | Rationale |
|-----------|--------|-----------|
| Server | nginx | High performance, WebSocket support |
| Process Manager | systemd | Native Linux integration |
| Language | Python 3.10+ | FastAPI requirement |
| Node | v20+ | React 19 requirement |

---

## 10. RISK MITIGATION

### Risk 1: Complexity Overrun
**Mitigation**: Phased approach, daily checkpoints, scope freeze after Phase 2

### Risk 2: AI Integration Issues
**Mitigation**: Circuit breaker pattern, graceful degradation, fallback to manual

### Risk 3: Database Performance
**Mitigation**: Proper indexing, query optimization, connection pooling

### Risk 4: Security Vulnerabilities
**Mitigation**: Input validation, parameterized queries, audit logs, security review

### Risk 5: WebSocket Reliability
**Mitigation**: Reconnection logic, fallback to polling, connection health monitoring

---

## 11. APPROVAL

**Design Status**: ✅ APPROVED  
**Implementation Start**: 2026-02-12  
**Target Completion**: 2026-02-26 (14 days)  
**Protocol**: BIBLE PROTOCOLS 10-Step Agent Doctrine  

**Required Artifacts**:
- [x] STATE_SNAPSHOT_BEFORE.md
- [x] IMPACT_NOTE.md
- [x] CHANGE_DESIGN.md (this document)
- [ ] CHANGELOG.patch (during build)
- [ ] TEST_REPORT.md (after testing)
- [ ] DEPLOY_LOG.md (during deploy)
- [ ] STATE_SNAPSHOT_AFTER.md (final)
- [ ] ROLLBACK_PLAN.md (detailed)

---

**Next Step**: Proceed to Step 4 - BUILD
