# LernsystemX Backup & Recovery Guide

**Version:** 1.0
**Last Updated:** 2025-11-17
**Target Audience:** System Administrators, DevOps Engineers

---

## Table of Contents

1. [Overview](#overview)
2. [Backup Strategy](#backup-strategy)
3. [Prerequisites](#prerequisites)
4. [Manual Backup](#manual-backup)
5. [Automated Backups](#automated-backups)
6. [Restore Procedures](#restore-procedures)
7. [Backup Verification](#backup-verification)
8. [Disaster Recovery](#disaster-recovery)
9. [GDPR & Data Protection](#gdpr--data-protection)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The LernsystemX (LSX) backup system provides:

- ✅ **Automated daily backups** of PostgreSQL database
- ✅ **Compressed backups** to save disk space (gzip)
- ✅ **Retention policy** (default: 30 days)
- ✅ **systemd timers** for automated execution
- ✅ **Manual backup/restore scripts**
- ✅ **Optional remote backup** (S3/MinIO)
- ✅ **GDPR-compliant** data handling

### What is Backed Up?

| Component | Status | Frequency |
|-----------|--------|-----------|
| **PostgreSQL Database** | ✅ Backed up | Daily (3:00 AM) |
| **Redis Cache** | ❌ Not backed up | Reconstructable from DB |
| **File Uploads** | 📋 Optional | Manual/separate process |
| **Application Code** | 📋 Version controlled | Git repository |

> **Note:** Redis is **not backed up** because it contains only cache data that can be reconstructed from the PostgreSQL database.

---

## Backup Strategy

### RPO & RTO Targets

| Metric | Target | Description |
|--------|--------|-------------|
| **RPO** (Recovery Point Objective) | 24 hours | Maximum acceptable data loss |
| **RTO** (Recovery Time Objective) | 2 hours | Maximum acceptable downtime |

### Backup Schedule

| Task | Frequency | Time | systemd Timer |
|------|-----------|------|---------------|
| **Database Backup** | Daily | 3:00 AM | `lsx-backup-db.timer` |
| **Backup Cleanup** | Weekly | Sunday 4:00 AM | `lsx-backup-cleanup.timer` |

### Retention Policy

```
┌──────────────────────────────────────────────┐
│  Backup Retention: 30 days (default)         │
│  Minimum Backups: 2 (safety check)           │
│  Cleanup Runs: Weekly                        │
└──────────────────────────────────────────────┘
```

**Default Settings:**
- Backups older than **30 days** are automatically deleted
- At least **2 backups** are always kept (even if older than retention period)
- Cleanup runs **weekly** to remove old backups

**Customization:**
Edit `/opt/lsx/backend/.env.production`:
```env
BACKUP_RETENTION_DAYS=60  # Keep backups for 60 days
```

---

## Prerequisites

### Required Tools

On the **production server**, ensure these are installed:

```bash
# PostgreSQL client tools (for pg_dump/pg_restore)
sudo apt-get install postgresql-client

# Compression tools
sudo apt-get install gzip

# Optional: AWS CLI (for remote backups)
sudo apt-get install awscli
```

### Directory Structure

Create backup directories:

```bash
sudo mkdir -p /var/backups/lsx/db
sudo chown -R postgres:postgres /var/backups/lsx
sudo chmod 750 /var/backups/lsx
```

### Environment Variables

Ensure these are set in `/opt/lsx/backend/.env.production`:

```env
BACKUP_DIR=/var/backups/lsx
BACKUP_RETENTION_DAYS=30
BACKUP_DB_NAME=lernsystemx_prod
BACKUP_DB_HOST=localhost
BACKUP_DB_PORT=5432
BACKUP_DB_USER=lsx_user
BACKUP_ENABLE_COMPRESSION=True
```

---

## Manual Backup

### Create Backup Manually

```bash
# Navigate to backup scripts directory
cd /opt/lsx/deployment/backup

# Execute backup script
sudo -u postgres bash backup_db.sh
```

**Output:**
```
[2025-11-17 15:30:00] ==========================================
[2025-11-17 15:30:00] LSX PostgreSQL Backup Starting
[2025-11-17 15:30:00] ==========================================
[2025-11-17 15:30:00] Backup directory: /var/backups/lsx/db
[2025-11-17 15:30:00] Database: lernsystemx_prod
[2025-11-17 15:30:00] Host: localhost:5432
[2025-11-17 15:30:00] User: lsx_user
[2025-11-17 15:30:00] Starting database backup...
[2025-11-17 15:30:15] Database dump completed successfully
[2025-11-17 15:30:15] Compressing backup...
[2025-11-17 15:30:20] Compression completed: /var/backups/lsx/db/lsx_db_20251117_153000.sql.gz
[2025-11-17 15:30:20] Backup file size: 15M
[2025-11-17 15:30:20] ==========================================
[2025-11-17 15:30:20] Backup completed successfully!
[2025-11-17 15:30:20] File: /var/backups/lsx/db/lsx_db_20251117_153000.sql.gz
[2025-11-17 15:30:20] Size: 15M
[2025-11-17 15:30:20] ==========================================
```

### List Existing Backups

```bash
ls -lh /var/backups/lsx/db/
```

**Example output:**
```
-rw-r--r-- 1 postgres postgres  15M Nov 17 03:00 lsx_db_20251117_030000.sql.gz
-rw-r--r-- 1 postgres postgres  14M Nov 16 03:00 lsx_db_20251116_030000.sql.gz
-rw-r--r-- 1 postgres postgres  14M Nov 15 03:00 lsx_db_20251115_030000.sql.gz
```

### Download Backup to Local Machine

```bash
# From your local machine
scp user@server:/var/backups/lsx/db/lsx_db_20251117_030000.sql.gz ./
```

---

## Automated Backups

### Enable Automated Backups

```bash
# Copy systemd service files
sudo cp /opt/lsx/deployment/systemd/lsx-backup-db.service /etc/systemd/system/
sudo cp /opt/lsx/deployment/systemd/lsx-backup-db.timer /etc/systemd/system/
sudo cp /opt/lsx/deployment/systemd/lsx-backup-cleanup.service /etc/systemd/system/
sudo cp /opt/lsx/deployment/systemd/lsx-backup-cleanup.timer /etc/systemd/system/

# Reload systemd daemon
sudo systemctl daemon-reload

# Enable timers (start on boot)
sudo systemctl enable lsx-backup-db.timer
sudo systemctl enable lsx-backup-cleanup.timer

# Start timers immediately
sudo systemctl start lsx-backup-db.timer
sudo systemctl start lsx-backup-cleanup.timer
```

### Verify Timers

```bash
# List all timers
systemctl list-timers

# Check backup timer status
systemctl status lsx-backup-db.timer

# Check cleanup timer status
systemctl status lsx-backup-cleanup.timer
```

**Expected output:**
```
● lsx-backup-db.timer - LernsystemX Database Backup Timer
     Loaded: loaded (/etc/systemd/system/lsx-backup-db.timer; enabled)
     Active: active (waiting) since Mon 2025-11-17 10:00:00 UTC; 5h ago
    Trigger: Tue 2025-11-18 03:00:00 UTC; 12h left
   Triggers: ● lsx-backup-db.service
```

### View Backup Logs

```bash
# View backup logs
journalctl -u lsx-backup-db.service -f

# View last 50 backup log entries
journalctl -u lsx-backup-db.service -n 50

# View cleanup logs
journalctl -u lsx-backup-cleanup.service -n 50
```

### Trigger Backup Manually (via systemd)

```bash
# Manually trigger backup without waiting for timer
sudo systemctl start lsx-backup-db.service

# Check status
systemctl status lsx-backup-db.service
```

---

## Restore Procedures

### ⚠️ IMPORTANT: Pre-Restore Checklist

Before restoring a backup:

1. ✅ **Verify backup file exists and is not corrupted**
2. ✅ **Test restore on staging environment first** (if possible)
3. ✅ **Create current backup before restoring** (safety measure)
4. ✅ **Notify users of expected downtime**
5. ✅ **Stop application services**

### Restore from Backup

```bash
# Navigate to backup scripts directory
cd /opt/lsx/deployment/backup

# Restore from specific backup file
sudo bash restore_db.sh /var/backups/lsx/db/lsx_db_20251117_030000.sql.gz
```

**Interactive confirmation required:**
```
⚠️  WARNING: This will DESTROY the current database and replace it with the backup!

Database to be DROPPED: lernsystemx_prod
Backup file: /var/backups/lsx/db/lsx_db_20251117_030000.sql.gz

Are you ABSOLUTELY SURE you want to continue? (yes/no):
```

Type `yes` and press Enter to proceed.

**Restore process:**
```
[2025-11-17 16:00:00] ==========================================
[2025-11-17 16:00:00] LSX PostgreSQL Restore Starting
[2025-11-17 16:00:00] ==========================================
[2025-11-17 16:00:00] Backup file: /var/backups/lsx/db/lsx_db_20251117_030000.sql.gz
[2025-11-17 16:00:00] Database: lernsystemx_prod
[2025-11-17 16:00:00] Host: localhost:5432
[2025-11-17 16:00:00] User: lsx_user
[2025-11-17 16:00:00] Decompressing backup file...
[2025-11-17 16:00:05] Decompression completed
[2025-11-17 16:00:05] Stopping LSX backend service (if running)...
[2025-11-17 16:00:10] Backend service stopped
[2025-11-17 16:00:10] Dropping and recreating database...
[2025-11-17 16:00:15] Database recreated successfully
[2025-11-17 16:00:15] Restoring backup...
[2025-11-17 16:02:30] Database restore completed successfully
[2025-11-17 16:02:30] Temporary decompressed file removed
[2025-11-17 16:02:30] Starting LSX backend service...
[2025-11-17 16:02:35] Backend service started
[2025-11-17 16:02:35] Verifying database connection...
[2025-11-17 16:02:36] Database verification successful - User count: 1250
[2025-11-17 16:02:36] ==========================================
[2025-11-17 16:02:36] Restore completed successfully!
[2025-11-17 16:02:36] Database: lernsystemx_prod
[2025-11-17 16:02:36] Restored from: /var/backups/lsx/db/lsx_db_20251117_030000.sql.gz
[2025-11-17 16:02:36] ==========================================

✅ Database restored successfully!

Next steps:
1. Verify application functionality
2. Check logs: journalctl -u lsx-backend -f
3. Test API health: curl http://localhost:8000/health
```

### Post-Restore Verification

```bash
# 1. Check backend service status
systemctl status lsx-backend

# 2. Check health endpoint
curl http://localhost:8000/health

# 3. Check database connection
sudo -u postgres psql -d lernsystemx_prod -c "SELECT count(*) FROM users;"

# 4. Verify Redis connection
redis-cli ping

# 5. Check application logs
journalctl -u lsx-backend -n 100 --no-pager
```

---

## Backup Verification

### Test Backup Integrity

It's critical to **regularly test** that backups can be restored successfully.

**Monthly Test Procedure:**

```bash
# 1. Create test database
sudo -u postgres psql -c "CREATE DATABASE lernsystemx_test_restore;"

# 2. Restore latest backup to test database
gunzip -c /var/backups/lsx/db/lsx_db_20251117_030000.sql.gz | \
    sudo -u postgres psql -d lernsystemx_test_restore

# 3. Verify data
sudo -u postgres psql -d lernsystemx_test_restore -c "SELECT count(*) FROM users;"

# 4. Cleanup test database
sudo -u postgres psql -c "DROP DATABASE lernsystemx_test_restore;"
```

**Automated Verification Script** (optional):

Create `/opt/lsx/deployment/backup/verify_backup.sh`:

```bash
#!/bin/bash
# Test latest backup can be restored

LATEST_BACKUP=$(ls -t /var/backups/lsx/db/lsx_db_*.sql.gz | head -1)
TEST_DB="lernsystemx_verify_$(date +%s)"

echo "Testing backup: ${LATEST_BACKUP}"

# Create test database
sudo -u postgres psql -c "CREATE DATABASE ${TEST_DB};"

# Restore
gunzip -c "${LATEST_BACKUP}" | sudo -u postgres psql -d "${TEST_DB}" > /dev/null 2>&1

# Verify
USER_COUNT=$(sudo -u postgres psql -d "${TEST_DB}" -t -c "SELECT count(*) FROM users;")

# Cleanup
sudo -u postgres psql -c "DROP DATABASE ${TEST_DB};"

if [ "${USER_COUNT}" -gt 0 ]; then
    echo "✅ Backup verification successful - ${USER_COUNT} users found"
    exit 0
else
    echo "❌ Backup verification failed - no users found"
    exit 1
fi
```

---

## Disaster Recovery

### Complete System Failure

In case of **complete server failure**, follow these steps:

#### 1. Setup New Server

```bash
# Install dependencies
sudo apt-get update
sudo apt-get install postgresql redis-server python3.12 nginx

# Create LSX user
sudo adduser lsx
```

#### 2. Restore Application Code

```bash
# Clone repository
git clone https://github.com/your-org/lernsystemx.git /opt/lsx
cd /opt/lsx/backend

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 3. Restore Database

```bash
# Copy backup from remote storage or backup server
scp backup-server:/var/backups/lsx/db/lsx_db_20251117_030000.sql.gz /tmp/

# Create database
sudo -u postgres psql -c "CREATE DATABASE lernsystemx_prod;"
sudo -u postgres psql -c "CREATE USER lsx_user WITH PASSWORD 'SECURE_PASSWORD';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE lernsystemx_prod TO lsx_user;"

# Restore backup
gunzip -c /tmp/lsx_db_20251117_030000.sql.gz | \
    sudo -u postgres psql -d lernsystemx_prod
```

#### 4. Configure Environment

```bash
# Copy production config
cp /opt/lsx/backend/.env.production.example /opt/lsx/backend/.env.production

# Edit with correct values
nano /opt/lsx/backend/.env.production
```

#### 5. Start Services

```bash
# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Start Gunicorn
sudo systemctl start lsx-backend
sudo systemctl enable lsx-backend

# Start Nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

#### 6. Verify

```bash
# Check health
curl http://localhost:8000/health

# Check frontend
curl http://localhost/
```

---

## GDPR & Data Protection

### Personal Data in Backups

Backups contain **personal data** (user emails, names, learning progress).

**GDPR Compliance:**

| Requirement | Implementation |
|-------------|----------------|
| **Data Minimization** | Only essential database is backed up |
| **Retention Limits** | 30-day default retention policy |
| **Encryption** | Optional encryption at rest |
| **Access Control** | Only `postgres` user has access |
| **Right to Erasure** | Backups are time-limited (auto-deleted) |

### User Data Deletion

When a user requests account deletion (GDPR Art. 17):

1. ✅ **User is deleted from production database** (immediate)
2. ❌ **User remains in backups** (until retention expires)

**Important:** Document this in your **Privacy Policy**:

> "Deleted account data may remain in our backup systems for up to 30 days before permanent removal."

### Backup Encryption (Optional)

To enable backup encryption:

```env
# In .env.production
BACKUP_ENABLE_ENCRYPTION=True
BACKUP_ENCRYPTION_KEY=YOUR_SECURE_32_BYTE_KEY_HERE
```

**Note:** Encryption requires additional tools (e.g., `gpg` or `openssl`). Implement custom encryption in `backup_db.sh` if required.

---

## Troubleshooting

### Backup Fails

**Symptom:** Backup script fails with error

**Common Causes:**

1. **Disk space full**
   ```bash
   df -h /var/backups/lsx
   ```
   Solution: Free up disk space or increase retention policy

2. **PostgreSQL not running**
   ```bash
   systemctl status postgresql
   ```
   Solution: Start PostgreSQL

3. **Authentication failure**
   ```bash
   sudo -u postgres psql -d lernsystemx_prod -c "SELECT 1;"
   ```
   Solution: Check `pg_hba.conf` and user permissions

4. **Permissions issue**
   ```bash
   ls -la /var/backups/lsx
   ```
   Solution: `sudo chown -R postgres:postgres /var/backups/lsx`

### Restore Fails

**Symptom:** Restore script fails with error

**Common Causes:**

1. **Backup file corrupted**
   ```bash
   gunzip -t /var/backups/lsx/db/lsx_db_20251117_030000.sql.gz
   ```
   Solution: Use different backup file

2. **Database already exists with active connections**
   ```bash
   sudo -u postgres psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'lernsystemx_prod';"
   ```

3. **Insufficient disk space**
   ```bash
   df -h /
   ```
   Solution: Free up disk space

### Timer Not Running

**Symptom:** Backups are not running automatically

**Debugging:**

```bash
# Check timer status
systemctl list-timers | grep lsx

# Check if timer is enabled
systemctl is-enabled lsx-backup-db.timer

# Check service logs
journalctl -u lsx-backup-db.service -n 50
```

**Solution:**
```bash
sudo systemctl enable lsx-backup-db.timer
sudo systemctl start lsx-backup-db.timer
```

### Backup Size Too Large

**Symptom:** Backups consume too much disk space

**Solutions:**

1. **Reduce retention period:**
   ```env
   BACKUP_RETENTION_DAYS=14  # Keep only 2 weeks
   ```

2. **Check database size:**
   ```sql
   SELECT pg_size_pretty(pg_database_size('lernsystemx_prod'));
   ```

3. **Analyze large tables:**
   ```sql
   SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
   FROM pg_tables
   WHERE schemaname = 'public'
   ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
   LIMIT 10;
   ```

4. **Consider archiving old data** (e.g., analytics older than 1 year)

---

## Next Steps

After setting up backup & recovery:

1. ✅ **Test restore procedure** on staging environment
2. ✅ **Schedule monthly backup verification**
3. ✅ **Document disaster recovery plan**
4. ✅ **Setup remote backup** (S3/MinIO) for off-site storage
5. ✅ **Configure monitoring/alerts** for backup failures

---

**Document Version:** 1.0
**Last Updated:** 2025-11-17
**Next Review:** Phase 19 (Monitoring & Alerting)
