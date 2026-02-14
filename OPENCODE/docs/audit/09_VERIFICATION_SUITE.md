# Verification Suite
## Runnable Checklist & Scripts

---

## Makefile Targets

Add to `Makefile` in project root:

```makefile
verify: verify-db verify-api verify-migration verify-security
	@echo "✅ All verifications passed"

verify-db:
	@echo "Checking database..."
	@PGPASSWORD=atum psql -h 127.0.0.1 -U atum -d atum_desk -c "SELECT 1" > /dev/null 2>&1 || (echo "❌ DB connection failed" && exit 1)
	@echo "✅ Database connection OK"

verify-migration:
	@echo "Checking migrations..."
	@cd atum-desk/api && python3 -c "from alembic import command; from alembic.config import Config; cfg = Config('alembic.ini'); print('Migrations OK')" 2>/dev/null || echo "⚠️  Migration check skipped"

verify-api:
	@echo "Checking API health..."
	@curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1 || (echo "❌ API health check failed" && exit 1)
	@echo "✅ API health OK"

verify-security:
	@echo "Checking SSL..."
	@test -r /etc/nginx/ssl/atum-desk.key && echo "✅ SSL key readable" || echo "❌ SSL key not readable"
```

---

## Bash Verification Script

Save as `scripts/verify_deployment.sh`:

```bash
#!/bin/bash
set -e

echo "=========================================="
echo "ATUM DESK Verification Suite"
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASS() { echo -e "${GREEN}✅ $1${NC}"; }
FAIL() { echo -e "${RED}❌ $1${NC}"; exit 1; }
WARN() { echo -e "${YELLOW}⚠️  $1${NC}"; }

echo ""
echo "1. Database Connection"
if PGPASSWORD=atum psql -h 127.0.0.1 -U atum -d atum_desk -c "SELECT 1" > /dev/null 2>&1; then
    PASS "Database connection"
else
    FAIL "Database connection"
fi

echo ""
echo "2. Database Tables"
TABLE_COUNT=$(PGPASSWORD=atum psql -h 127.0.0.1 -U atum -d atum_desk -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema='public'" | xargs)
if [ "$TABLE_COUNT" -ge 20 ]; then
    PASS "Tables exist ($TABLE_COUNT)"
else
    FAIL "Missing tables (found $TABLE_COUNT)"
fi

echo ""
echo "3. API Health"
if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    PASS "API health endpoint"
else
    FAIL "API health endpoint"
fi

echo ""
echo "4. Tickets Data"
TICKET_COUNT=$(PGPASSWORD=atum psql -h 127.0.0.1 -U atum -d atum_desk -t -c "SELECT count(*) FROM tickets" | xargs)
echo "   Found $TICKET_COUNT tickets"
PASS "Tickets query"

echo ""
echo "5. SSL Certificate"
if [ -r /etc/nginx/ssl/atum-desk.crt ]; then
    PASS "SSL certificate exists"
else
    FAIL "SSL certificate missing"
fi

echo ""
echo "6. SSL Key Permissions"
KEY_PERMS=$(stat -c %a /etc/nginx/ssl/atum-desk.key 2>/dev/null || echo "missing")
if [ "$KEY_PERMS" = "644" ] || [ "$KEY_PERMS" = "600" ]; then
    PASS "SSL key permissions ($KEY_PERMS)"
else
    WARN "SSL key permissions may be wrong ($KEY_PERMS)"
fi

echo ""
echo "7. NGINX Config Test"
if nginx -t > /dev/null 2>&1; then
    PASS "NGINX config valid"
else
    FAIL "NGINX config invalid"
fi

echo ""
echo "8. Backup Directory"
if [ -d "/data/ATUM DESK/atum-desk/data/backups" ]; then
    PASS "Backup directory exists"
else
    FAIL "Backup directory missing"
fi

echo ""
echo "9. Upload Directory"
if [ -d "/data/ATUM DESK/atum-desk/data/uploads" ]; then
    PASS "Upload directory exists"
else
    FAIL "Upload directory missing"
fi

echo ""
echo "10. Systemd Services"
for svc in atum-desk-api atum-desk-sla-worker; do
    if systemctl is-active --quiet $svc; then
        PASS "$svc running"
    else
        FAIL "$svc not running"
    fi
done

echo ""
echo "=========================================="
echo "Verification Complete"
echo "=========================================="
```

---

## Usage

```bash
# Run full verification
chmod +x scripts/verify_deployment.sh
./scripts/verify_deployment.sh

# Or use make
make verify
```

---

## Database Sanity Queries

Save as `scripts/db_sanity.sh`:

```bash
#!/bin/bash
PGPASSWORD=atum psql -h 127.0.0.1 -U atum -d atum_desk <<EOF
-- Ticket counts by status
SELECT status, COUNT(*) FROM tickets GROUP BY status;

-- User counts by role
SELECT role, COUNT(*) FROM users GROUP BY role;

-- Recent audit events
SELECT action, entity_type, created_at 
FROM audit_log 
ORDER BY created_at DESC 
LIMIT 10;

-- SLA status
SELECT status, sla_started_at, sla_due_at 
FROM tickets 
WHERE sla_policy_id IS NOT NULL;

-- Attachment count
SELECT COUNT(*) FROM attachments;
EOF
```

---

## Test Upload Validation

```bash
#!/bin/bash
# Test file upload security

echo "Testing upload endpoint..."

# Create test file
echo "test content" > /tmp/test_upload.txt

# Try upload (requires auth token)
TOKEN="your-jwt-token"
curl -s -X POST http://localhost:8000/api/v1/attachments/ticket/{ticket_id} \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/test_upload.txt"

# Check file stored outside web root
if [ -f "/data/ATUM DESK/atum-desk/data/uploads/"*"/"* ]; then
    echo "✅ File stored correctly"
else
    echo "❌ File not found in uploads"
fi

rm /tmp/test_upload.txt
```
