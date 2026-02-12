# IMPACT_NOTE.md
## ATUM DESK - Impact Analysis

**Date**: 2026-02-12  
**Scope**: Complete ATUM DESK implementation with all 14 enhancements (Option C)  
**Risk Level**: MEDIUM-HIGH (New system deployment)

---

## 1. WHAT WILL CHANGE

### Files to be Created (Estimated 200+ files)

#### Backend (Python/FastAPI) - ~80 files
```
atum-desk/api/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI application factory
│   ├── config.py                    # Pydantic settings
│   ├── dependencies.py              # FastAPI dependencies
│   ├── auth/                        # Authentication module
│   │   ├── __init__.py
│   │   ├── jwt.py                   # JWT handling
│   │   ├── password.py              # bcrypt hashing
│   │   ├── rbac.py                  # Role-based access
│   │   └── two_factor.py            # TOTP 2FA
│   ├── db/                          # Database module
│   │   ├── __init__.py
│   │   ├── base.py                  # SQLAlchemy base
│   │   ├── session.py               # Async session
│   │   └── init_db.py               # DB initialization
│   ├── models/                      # 14 SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── organization.py
│   │   ├── user.py
│   │   ├── service.py
│   │   ├── ticket.py
│   │   ├── comment.py
│   │   ├── attachment.py
│   │   ├── sla_policy.py
│   │   ├── sla_calculation.py
│   │   ├── audit_log.py
│   │   ├── time_entry.py
│   │   ├── ticket_relationship.py
│   │   ├── custom_field.py
│   │   ├── custom_field_value.py
│   │   ├── canned_response.py
│   │   ├── kb_article.py
│   │   ├── kb_category.py
│   │   └── csat_survey.py
│   ├── routers/                     # 17 API routers
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── organizations.py
│   │   ├── tickets.py
│   │   ├── internal_tickets.py
│   │   ├── comments.py
│   │   ├── attachments.py
│   │   ├── sla.py
│   │   ├── audit.py
│   │   ├── time_tracking.py
│   │   ├── relationships.py
│   │   ├── custom_fields.py
│   │   ├── canned_responses.py
│   │   ├── kb.py
│   │   ├── csat.py
│   │   ├── dashboard.py
│   │   ├── search.py
│   │   └── ai.py
│   ├── services/                    # Business logic
│   │   ├── __init__.py
│   │   ├── ticket_service.py
│   │   ├── sla_service.py
│   │   ├── audit_service.py
│   │   ├── email_service.py
│   │   ├── upload_service.py
│   │   ├── search_service.py
│   │   ├── time_service.py
│   │   ├── kb_service.py
│   │   └── ai_service.py
│   ├── middleware/                  # FastAPI middleware
│   │   ├── __init__.py
│   │   ├── auth_middleware.py
│   │   ├── rbac_middleware.py
│   │   ├── tenant_middleware.py
│   │   ├── rate_limit.py
│   │   └── audit_middleware.py
│   ├── utils/                       # Utilities
│   │   ├── __init__.py
│   │   ├── validators.py
│   │   ├── security.py
│   │   ├── datetime.py
│   │   └── exceptions.py
│   └── websocket/                   # Real-time
│       ├── __init__.py
│       ├── manager.py
│       ├── events.py
│       └── handlers.py
├── migrations/                      # Alembic migrations
│   ├── env.py
│   ├── alembic.ini
│   ├── script.py.mako
│   └── versions/
├── tests/                           # Test suite
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── celery/                          # Background tasks
│   ├── __init__.py
│   ├── config.py
│   └── tasks.py
├── ai/                              # AI integration
│   ├── __init__.py
│   ├── ollama_client.py
│   ├── embeddings.py
│   ├── triage.py
│   └── suggestions.py
├── requirements.txt
└── .env.example
```

#### Frontend (React/Vite) - ~100 files
```
atum-desk/web/
├── public/
│   ├── index.html
│   └── brand/
│       ├── logo.svg                 # ATUM brand assets
│       ├── wordmark.svg
│       ├── atum-silhouette.svg
│       └── favicon.svg
├── src/
│   ├── main.jsx
│   ├── App.jsx
│   ├── index.css
│   ├── atum/                        # ATUM Design System
│   │   ├── tokens/
│   │   │   ├── colors.js
│   │   │   ├── typography.js
│   │   │   ├── spacing.js
│   │   │   ├── shadows.js
│   │   │   └── animations.js
│   │   ├── components/              # 20+ UI components
│   │   │   ├── AtumShell.jsx
│   │   │   ├── AtumCard.jsx
│   │   │   ├── AtumButton.jsx
│   │   │   ├── AtumInput.jsx
│   │   │   ├── AtumSelect.jsx
│   │   │   ├── AtumTextarea.jsx
│   │   │   ├── AtumTable.jsx
│   │   │   ├── AtumPill.jsx
│   │   │   ├── AtumModal.jsx
│   │   │   ├── AtumToast.jsx
│   │   │   ├── AtumTabs.jsx
│   │   │   ├── AtumDropzone.jsx
│   │   │   ├── AtumSearch.jsx
│   │   │   ├── AtumSidebar.jsx
│   │   │   ├── AtumHeader.jsx
│   │   │   ├── AtumTimeline.jsx
│   │   │   ├── AtumChart.jsx
│   │   │   └── AtumRichText.jsx
│   │   └── layouts/
│   │       ├── PortalLayout.jsx
│   │       └── DeskLayout.jsx
│   ├── components/                  # Feature components
│   │   ├── auth/
│   │   ├── tickets/
│   │   ├── comments/
│   │   ├── kb/
│   │   ├── dashboard/
│   │   ├── ai/
│   │   └── common/
│   ├── pages/                       # Route pages
│   │   ├── LandingPage.jsx          # ATUM clone
│   │   ├── portal/
│   │   │   ├── PortalLogin.jsx
│   │   │   ├── PortalTickets.jsx
│   │   │   ├── PortalTicketNew.jsx
│   │   │   ├── PortalTicketDetail.jsx
│   │   │   └── PortalKnowledgeBase.jsx
│   │   └── desk/
│   │       ├── DeskLogin.jsx
│   │       ├── DeskDashboard.jsx
│   │       ├── DeskInbox.jsx
│   │       ├── DeskTicketDetail.jsx
│   │       ├── DeskReports.jsx
│   │       ├── DeskAdmin.jsx
│   │       ├── DeskKBAdmin.jsx
│   │       ├── DeskCannedResponses.jsx
│   │       └── DeskCustomFields.jsx
│   ├── hooks/                       # Custom React hooks
│   ├── contexts/                    # React contexts
│   ├── api/                         # API client
│   ├── utils/                       # Frontend utilities
│   └── router.jsx
├── package.json
├── vite.config.js
├── tailwind.config.js
└── eslint.config.js
```

#### Infrastructure - ~25 files
```
atum-desk/infra/
├── nginx/
│   └── atum-desk.conf               # nginx site config
├── systemd/
│   ├── atum-desk-api.service        # API service unit
│   ├── atum-desk-ws.service         # WebSocket service unit
│   └── atum-desk-worker.service     # Celery worker unit
├── scripts/
│   ├── install.sh                   # Installation script
│   ├── setup-db.sh                  # Database setup
│   ├── setup-ssl.sh                 # SSL certificate setup
│   ├── backup.sh                    # Backup script
│   └── update.sh                    # Update script
└── config/
    ├── postgresql.conf              # PostgreSQL tuning
    ├── redis.conf                   # Redis config
    └── ollama.service               # Ollama systemd unit
```

#### Documentation - ~8 files
```
atum-desk/docs/
├── ATUM_UI_AUDIT.md                 # Brand specifications
├── RUNBOOK.md                       # Operations guide
├── ACCEPTANCE_TESTS.md              # E2E test procedures
├── API_REFERENCE.md                 # API documentation
├── DEPLOYMENT.md                    # Deployment guide
├── SECURITY.md                      # Security hardening
└── TROUBLESHOOTING.md               # Common issues
```

### Services to be Created

| Service Name | Type | Port | Purpose |
|--------------|------|------|---------|
| atum-desk-api | systemd | 8000 | FastAPI REST API |
| atum-desk-ws | systemd | 8001 | WebSocket server |
| atum-desk-worker | systemd | - | Celery background worker |

### Database Changes

**New Database**: `atum_desk` (PostgreSQL)

**Tables to Create (18 tables)**:
1. organizations - Multi-tenant root
2. users - Authentication & RBAC
3. services - Ticket categories
4. tickets - Core ticket entity
5. comments - Public/internal notes
6. attachments - File uploads
7. sla_policies - SLA definitions
8. sla_calculation - SLA time tracking
9. audit_log - Immutable audit trail
10. time_entries - Time tracking
11. ticket_relationships - Parent/child/duplicate
12. custom_fields - Dynamic fields
13. custom_field_values - Field values
14. canned_responses - Templates
15. kb_categories - KB organization
16. kb_articles - Knowledge base
17. csat_surveys - Satisfaction surveys
18. alembic_version - Migration tracking

**PostgreSQL Extensions Required**:
- uuid-ossp (UUID generation)
- pg_trgm (Full-text search)
- pgvector (AI embeddings) - optional

---

## 2. WHO DEPENDS ON IT

### External Dependencies (Already Installed)
- **PostgreSQL 16**: System service, no changes needed
- **Redis 7**: System service, no changes needed
- **nginx**: Will be reconfigured to proxy ATUM DESK
- **Ollama**: Already running with ATUM-DESK-AI model

### Internal Dependencies (To Be Created)
- API depends on PostgreSQL and Redis
- WebSocket depends on API authentication
- Frontend depends on API and WebSocket
- AI service depends on Ollama
- Background workers depend on Redis (Celery)

### No External Service Dependencies
- ✅ No external APIs
- ✅ No cloud services
- ✅ No SaaS dependencies
- ✅ Fully offline capable

---

## 3. WHAT CAN BREAK

### High Risk Failures

#### 1. Database Migration Failures
**Scenario**: Alembic migration fails mid-way  
**Impact**: Database in inconsistent state  
**Mitigation**: 
- Test migrations in development first
- Create database backup before migration
- Use transaction-based migrations
- Have rollback scripts ready

#### 2. Port Conflicts
**Scenario**: Ports 8000/8001 already in use  
**Impact**: Services fail to start  
**Mitigation**:
- Check ports before starting services
- Use dynamic port allocation as fallback
- Document port requirements clearly

#### 3. File Permission Issues
**Scenario**: Upload directory not writable  
**Impact**: File uploads fail  
**Mitigation**:
- Create directories with proper permissions during install
- Use dedicated service user
- Test upload functionality immediately after deployTo activate it, set these ENVs: IMAP_HOST=imap.gmail.com (example) IMAP_USER=support@atum.desk IMAP_PASSWORD=your-app-password

Next P1 Item: Webhooks (Outbound events)?

#### 4. Multi-tenant Isolation Breach
**Scenario**: Query missing org_id filter  
**Impact**: Data leakage between organizations  
**Mitigation**:
- Enforce org_id in all queries
- Use database RLS policies
- Comprehensive integration tests

### Medium Risk Failures

#### 5. WebSocket Connection Issues
**Scenario**: WebSocket upgrade fails through nginx  
**Impact**: Real-time updates don't work  
**Mitigation**:
- Proper nginx configuration for WebSocket
- Fallback to polling mode
- Connection health monitoring

#### 6. AI Service Unavailable
**Scenario**: Ollama not responding  
**Impact**: AI features fail gracefully  
**Mitigation**:
- Implement circuit breaker pattern
- Graceful degradation (AI features become unavailable but system works)
- Health checks for AI service

#### 7. Email Delivery Failures
**Scenario**: SMTP server not configured  
**Impact**: No email notifications  
**Mitigation**:
- Make email optional in config
- Log emails when SMTP unavailable
- Queue emails for retry

### Low Risk Failures

#### 8. Performance Issues
**Scenario**: Slow queries under load  
**Impact**: Degraded user experience  
**Mitigation**:
- Database indexing strategy
- Query optimization
- Caching layer (Redis)

---

## 4. WHAT MUST NOT CHANGE

### Existing System Components (Protected)
- ✅ PostgreSQL configuration (except adding atum_desk database)
- ✅ Redis configuration (using separate DB index)
- ✅ nginx main config (only adding site config)
- ✅ System user permissions
- ✅ Firewall rules
- ✅ Existing databases
- ✅ Running services (nginx, postgres, redis, ollama)

### Constraints
1. **No Docker**: Bare-metal deployment only
2. **No External APIs**: All services must be local
3. **No Breaking Changes**: Existing services continue working
4. **Port 80/443**: Must remain with nginx (proxy to ATUM DESK)
5. **Localhost Binding**: Database and cache remain localhost-only

---

## 5. RESTART REQUIREMENTS

### Service Restart Order

```
Phase 1: No Restart Required
- PostgreSQL (already running)
- Redis (already running)
- nginx (reload only)
- Ollama (already running)

Phase 2: New Service Registration
- atum-desk-api (new)
- atum-desk-ws (new)
- atum-desk-worker (new)

Phase 3: nginx Reload
- Test new config: nginx -t
- Reload: systemctl reload nginx
```

### Zero-Downtime Strategy
- nginx reload is zero-downtime
- New services don't affect existing ones
- Database migrations run before service start
- Rollback possible by stopping new services

---

## 6. ROLLBACK TRIGGER CONDITIONS

### Immediate Rollback Required If:

1. **Service Health Check Fails**
   - API not responding on port 8000
   - WebSocket not accepting connections
   - Database connection failures

2. **Security Issues**
   - Unauthorized access to data
   - Authentication bypass
   - File upload vulnerabilities

3. **Data Integrity Issues**
   - Database corruption
   - Migration failures
   - Data loss in any form

4. **Performance Degradation**
   - Response times > 5 seconds
   - 100% CPU usage sustained
   - Memory exhaustion

5. **Port Conflicts**
   - Cannot bind to required ports
   - Conflicts with existing services

### Rollback Procedure (High-Level)
```bash
# 1. Stop new services
sudo systemctl stop atum-desk-api
sudo systemctl stop atum-desk-ws
sudo systemctl stop atum-desk-worker

# 2. Restore nginx config
sudo rm /etc/nginx/sites-enabled/atum-desk.conf
sudo systemctl reload nginx

# 3. Restore database (if needed)
# sudo -u postgres dropdb atum_desk
# sudo -u postgres createdb atum_desk
# pg_restore atum_desk_backup.dump

# 4. Remove installation
sudo rm -rf /data/ATUM DESK/atum-desk
```

---

## 7. CONFLICT PREVENTION CHECKLIST

- [x] Port conflicts checked: 8000, 8001 available
- [x] Path conflicts checked: /data/ATUM DESK/atum-desk/ is new
- [x] Service name conflicts checked: atum-desk-* are new
- [x] Database name conflicts checked: atum_desk is new
- [x] nginx site config conflicts: atum-desk.conf is new
- [x] Systemd unit name conflicts: all new names
- [x] Import/module conflicts: fresh Python project
- [x] Config key conflicts: isolated .env file
- [x] Permissions/ownership: will use navi user
- [x] Disk headroom: 450G available (need ~2G)
- [x] RAM headroom: 18G available (need ~2G)

---

## 8. SUCCESS METRICS

### Deployment Success
- [ ] All services start without errors
- [ ] API responds to health check
- [ ] Database migrations applied successfully
- [ ] Frontend builds without errors
- [ ] nginx proxies correctly
- [ ] First ticket can be created end-to-end

### Feature Success (Option C - All Enhancements)
- [ ] WebSocket real-time updates working
- [ ] Knowledge base searchable
- [ ] SLA tracking with business hours
- [ ] Time tracking functional
- [ ] CSAT surveys sent and collected
- [ ] Dashboard with analytics
- [ ] AI triage providing suggestions
- [ ] 2FA working
- [ ] Audit logs recording all actions
- [ ] IP restrictions configurable

### Performance Targets
- Page load time: < 2 seconds
- API response time (p95): < 200ms
- WebSocket latency: < 100ms
- Concurrent users: 100+

---

## 9. MODIFICATION SAFETY MATRIX

| Change Type | Risk Level | Safety Measures |
|-------------|------------|-----------------|
| New service (API) | HIGH | Port plan, unit name uniqueness, health checks |
| New service (WebSocket) | HIGH | Port plan, nginx WebSocket config |
| New service (Worker) | MEDIUM | Celery config, Redis connection |
| Database schema | CRITICAL | Backup, migration script, rollback plan |
| nginx config | MEDIUM | Config test, backup existing |
| React frontend | LOW | Build verification, static files |
| Systemd units | MEDIUM | Enable/disable rules, restart policy |

---

**Impact Analysis Status**: COMPLETE  
**Risk Assessment**: MEDIUM-HIGH (manageable with proper procedures)  
**Recommendation**: PROCEED with implementation following BIBLE PROTOCOLS  
**Next Step**: Create CHANGE_DESIGN.md
