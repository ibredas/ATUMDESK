# ATUM DESK - Rollback Plan

**Version**: 1.0  
**Date**: 2026-02-12  
**Status**: Prepared

---

## Immediate Rollback Triggers

Execute rollback if ANY of the following occur:

1. **Service Health Check Failure**
   - API not responding on port 8000
   - Database connection errors
   - nginx configuration errors

2. **Security Issues**
   - Unauthorized data access
   - Authentication bypass
   - File upload vulnerabilities

3. **Data Integrity Issues**
   - Database corruption
   - Migration failures
   - Data loss detected

4. **Performance Degradation**
   - Response times > 5 seconds
   - 100% CPU usage sustained
   - Memory exhaustion

5. **Port Conflicts**
   - Cannot bind to required ports
   - Service conflicts

---

## Rollback Procedure

### Step 1: Stop All ATUM DESK Services
```bash
sudo systemctl stop atum-desk-worker
sudo systemctl stop atum-desk-ws
sudo systemctl stop atum-desk-api
```

### Step 2: Disable Services
```bash
sudo systemctl disable atum-desk-worker
sudo systemctl disable atum-desk-ws
sudo systemctl disable atum-desk-api
```

### Step 3: Remove Systemd Units
```bash
sudo rm -f /etc/systemd/system/atum-desk-*.service
sudo systemctl daemon-reload
```

### Step 4: Restore nginx Configuration
```bash
# Remove ATUM DESK site
sudo rm -f /etc/nginx/sites-enabled/atum-desk.conf
sudo rm -f /etc/nginx/sites-available/atum-desk.conf

# Test nginx config
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

### Step 5: Database Rollback (Optional)
```bash
# If database needs to be removed:
sudo -u postgres dropdb atum_desk

# To restore from backup (if available):
# sudo -u postgres pg_restore -d atum_desk /path/to/backup.dump
```

### Step 6: Remove Installation
```bash
# Remove application directory
sudo rm -rf "/data/ATUM DESK/atum-desk"

# Remove data directory
sudo rm -rf "/data/ATUM DESK/atum-desk/data"
```

### Step 7: Verify Rollback
```bash
# Check no ATUM DESK services running
sudo systemctl status atum-desk-api 2>&1 | grep "Active:" || echo "✓ API service stopped"
sudo systemctl status atum-desk-ws 2>&1 | grep "Active:" || echo "✓ WS service stopped"
sudo systemctl status atum-desk-worker 2>&1 | grep "Active:" || echo "✓ Worker service stopped"

# Check ports are free
sudo ss -tlnp | grep -E "8000|8001" || echo "✓ Ports 8000/8001 free"

# Check nginx still working
curl -s -o /dev/null -w "%{http_code}" http://localhost || echo "✓ nginx responding"
```

---

## Data Preservation (Before Rollback)

### Backup Database
```bash
# Create backup before rollback
BACKUP_FILE="/data/ATUM DESK/atum-desk/data/backups/atum_desk_$(date +%Y%m%d_%H%M%S).dump"
sudo -u postgres pg_dump -Fc atum_desk > "$BACKUP_FILE"
echo "Database backed up to: $BACKUP_FILE"
```

### Backup Uploads
```bash
# Backup uploads
UPLOAD_BACKUP="/data/ATUM DESK/atum-desk/data/backups/uploads_$(date +%Y%m%d_%H%M%S).tar.gz"
tar -czf "$UPLOAD_BACKUP" -C "/data/ATUM DESK/atum-desk/data" uploads/
echo "Uploads backed up to: $UPLOAD_BACKUP"
```

### Backup Configuration
```bash
# Backup .env
CONFIG_BACKUP="/data/ATUM DESK/atum-desk/data/backups/env_$(date +%Y%m%d_%H%M%S)"
cp "/data/ATUM DESK/atum-desk/api/.env" "$CONFIG_BACKUP"
echo "Config backed up to: $CONFIG_BACKUP"
```

---

## Post-Rollback Checklist

- [ ] All ATUM DESK services stopped
- [ ] Systemd units removed
- [ ] nginx configuration restored
- [ ] Ports 8000/8001 free
- [ ] Database preserved or removed as requested
- [ ] Upload files preserved or removed as requested
- [ ] Original services (PostgreSQL, Redis, nginx) still running
- [ ] No error messages in system logs

---

## Emergency Contacts

**System Administrator**: navi  
**Installation Directory**: /data/ATUM DESK/atum-desk  
**Database**: atum_desk (PostgreSQL)  

---

## Recovery After Rollback

To re-deploy ATUM DESK after rollback:

```bash
# 1. Restore from backup (if available)
# sudo -u postgres pg_restore -d atum_desk /path/to/backup.dump

# 2. Re-run installation
bash /data/ATUM\ DESK/atum-desk/infra/scripts/install.sh

# 3. Start services
sudo systemctl start atum-desk-api
sudo systemctl start atum-desk-ws
sudo systemctl start atum-desk-worker
```

---

**Last Updated**: 2026-02-12  
**Rollback Plan Status**: COMPLETE
