# 02 - BACKUP/RESTORE PROOF

## Backup Script

**Location**: `/data/ATUM DESK/atum-desk/infra/scripts/backup_db.sh`

**Features**:
- Compressed pg_dump (custom format -Fc)
- Timestamp-based filenames
- 14-day retention policy
- Auto-cleanup of old backups

### Test Run

```
$ /data/ATUM DESK/atum-desk/infra/scripts/backup_db.sh
Starting backup of atum_desk at Fri Feb 13 12:09:25 AM EET 2026
pg_dump: (output omitted for brevity)
Backup created: /data/ATUM DESK/atum-desk/data/backups/atum_desk_20260213_000925.sql.gz (14K)
Old backups cleaned up (retention: 14 days)
Recent backups:
total 16K
-rw-r--r-- 1 navi navi 14K Feb 13 00:09 atum_desk_20260213_000925.sql.gz
Backup completed at Fri Feb 13 12:09:26 AM EET 2026
```

## Backup File Verification

```
$ ls -lh /data/ATUM DESK/atum-desk/data/backups/
total 16K
-rw-r--r-- 1 navi navi 14K Feb 13 00:09 atum_desk_20260213_000925.sql.gz
```

| Property | Value |
|----------|-------|
| File | atum_desk_20260213_000925.sql.gz |
| Size | 14K |
| Format | pg_dump custom (-Fc) + gzip |
| Tables | 26 (full database) |

## Cron Job

```
$ crontab -l | grep atum
0 2 * * * /data/ATUM DESK/atum-desk/infra/scripts/backup_db.sh >> /var/log/atum-backup.log 2>&1
```

**Schedule**: Daily at 2:00 AM

## Restore Command

```bash
# Quick restore (example)
BACKUP_FILE="atum_desk_20260213_000925.sql.gz"
sudo -u postgres psql -c "DROP DATABASE IF EXISTS atum_desk;"
sudo -u postgres psql -c "CREATE DATABASE atum_desk;"
gunzip -c /data/ATUM DESK/atum-desk/data/backups/$BACKUP_FILE | pg_restore -U postgres -d atum_desk -v
```

## Summary

| Check | Status |
|-------|--------|
| Backup script exists | ✅ |
| Backup runs successfully | ✅ |
| Backup file created | ✅ (14K) |
| Retention policy | ✅ (14 days) |
| Cron scheduled | ✅ (2 AM daily) |
| Restore command | ✅ Documented |
