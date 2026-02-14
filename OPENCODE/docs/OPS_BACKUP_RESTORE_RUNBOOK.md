# ATUM DESK Backup & Restore Runbook

## Backup Schedule

- **Frequency**: Daily
- **Time**: 2:00 AM (server local time)
- **Retention**: 14 days
- **Location**: `/data/ATUM DESK/atum-desk/data/backups/`

---

## Backup Script

**Location**: `/data/ATOM DESK/atum-desk/infra/scripts/backup_db.sh`

**Usage**:
```bash
# Run manual backup
/data/ATUM DESK/atum-desk/infra/scripts/backup_db.sh

# View recent backups
ls -lh /data/ATUM DESK/atum-desk/data/backups/
```

---

## Automated Scheduling (Cron)

Add to crontab (`crontab -e`):

```cron
# ATUM DESK Daily Backup - 2:00 AM
0 2 * * * /data/ATUM DESK/atum-desk/infra/scripts/backup_db.sh >> /var/log/atum-backup.log 2>&1
```

---

## Manual Restore Procedure

**⚠️ WARNING: This will overwrite the current database!**

### Step 1: Stop API Service
```bash
sudo systemctl stop atum-desk-api
sudo systemctl stop atum-desk-sla-worker
```

### Step 2: Identify Backup File
```bash
ls -lt /data/ATUM DESK/atum-desk/data/backups/
```

### Step 3: Restore Database
```bash
# Drop existing database (requires postgres superuser)
sudo -u postgres psql -c "DROP DATABASE IF EXISTS atum_desk;"
sudo -u postgres psql -c "CREATE DATABASE atum_desk;"

# Restore from backup
gunzip -c /data/ATUM DESK/atum-desk/data/backups/atum_desk_YYYYMMDD_HHMMSS.sql.gz | \
    pg_restore -U postgres -d atum_desk -v
```

### Step 4: Restart Services
```bash
sudo systemctl start atum-desk-api
sudo systemctl start atum-desk-sla-worker
```

### Step 5: Verify
```bash
# Check API health
curl -s http://localhost:8000/api/v1/health

# Verify tickets exist
PGPASSWORD=postgres psql -h 127.0.0.1 -U postgres -d atum_desk -c "SELECT count(*) FROM tickets;"
```

---

## Restore Command (Copy-Paste Ready)

```bash
# Quick restore command (replace TIMESTAMP with actual file)
BACKUP_FILE="atum_desk_20260213_000925.sql.gz"
sudo -u postgres psql -c "DROP DATABASE IF EXISTS atum_desk;"
sudo -u postgres psql -c "CREATE DATABASE atum_desk;"
gunzip -c /data/ATUM DESK/atum-desk/data/backups/$BACKUP_FILE | pg_restore -U postgres -d atum_desk -v
```

---

## Testing Backup Integrity

```bash
# List tables in backup
gunzip -c /data/ATUM DESK/atum-desk/data/backups/atum_desk_latest.sql.gz | pg_restore -l

# Verify backup is valid SQL
gunzip -c /data/ATUM DESK/atum-desk/data/backups/atum_desk_latest.sql.gz | head -50
```

---

## Monitoring

Check backup logs:
```bash
tail -f /var/log/atum-backup.log
```

Verify latest backup exists:
```bash
ls -la /data/ATUM DESK/atum-desk/data/backups/ | tail -2
```
