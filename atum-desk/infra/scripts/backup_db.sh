#!/bin/bash
# ATUM DESK Database Backup Script
# Location: /data/ATUM DESK/atum-desk/infra/scripts/backup_db.sh

set -e

# Configuration
BACKUP_DIR="/data/ATUM DESK/atum-desk/data/backups"
DB_NAME="atum_desk"
DB_USER="postgres"
RETENTION_DAYS=14

# Timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/atum_desk_${TIMESTAMP}.sql.gz"

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

echo "Starting backup of $DB_NAME at $(date)"

# Create backup using pg_dump
# -Fc for custom format (compressed)
# -v for verbose
pg_dump -U "$DB_USER" -h localhost -Fc -v "$DB_NAME" | gzip > "$BACKUP_FILE"

# Verify backup was created
if [ -f "$BACKUP_FILE" ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "Backup created: $BACKUP_FILE ($BACKUP_SIZE)"
else
    echo "ERROR: Backup failed!"
    exit 1
fi

# Cleanup old backups (keep last N days)
find "$BACKUP_DIR" -name "atum_desk_*.sql.gz" -mtime +$RETENTION_DAYS -delete
echo "Old backups cleaned up (retention: $RETENTION_DAYS days)"

# List recent backups
echo "Recent backups:"
ls -lh "$BACKUP_DIR" | tail -5

echo "Backup completed at $(date)"
