# PHASE 0: BACKUP DESIGN DOCUMENT

## Backup Strategy

### 0.1 Database Backup
**Command**: pg_dump -U postgres -h localhost -Fc atum_desk | gzip > "backup_file"
**Format**: Custom PostgreSQL format (compressed with gzip)
**Why**: 
- Custom format allows selective restore
- Gzip compression reduces size by ~80%
- Compatible with pg_restore

### 0.2 Configuration Backup
**Files to backup**:
1. All .env files in atum-desk/api/
2. All systemd service files (atum-desk-*.service)
3. Nginx configuration
4. Any custom scripts

**Format**: tar.gz archive with timestamp

### 0.3 State Documentation
**Capture**:
- Running PIDs
- Service statuses
- Port allocations
- Git commit hash
- Environment state

### Safety Measures
1. Verify PostgreSQL is running before backup
2. Check disk space before starting
3. Use timestamped filenames
4. Verify backup integrity after creation
5. Create checksum for verification

### Rollback Plan
If backup fails:
1. Document failure reason
2. Check disk space
3. Verify PostgreSQL connectivity
4. Retry with verbose output

