#!/bin/bash
# LernsystemX PostgreSQL Restore Script
#
# ⚠️  WARNING: This script will DROP and recreate the database!
# ⚠️  Only use on TEST systems or after explicit confirmation!
#
# Usage: ./restore_db.sh <backup_file>
# Example: ./restore_db.sh /var/backups/lsx/db/lsx_db_20251116_030000.sql.gz
#
# Environment Variables (from .env.production):
# - BACKUP_DB_NAME
# - BACKUP_DB_HOST
# - BACKUP_DB_PORT
# - BACKUP_DB_USER

set -euo pipefail

# ==========================================
# Configuration
# ==========================================

# Load environment variables if .env.production exists
if [ -f "/opt/lsx/backend/.env.production" ]; then
    export $(grep -v '^#' /opt/lsx/backend/.env.production | xargs)
fi

# Default values
DB_NAME="${BACKUP_DB_NAME:-lernsystemx_prod}"
DB_HOST="${BACKUP_DB_HOST:-localhost}"
DB_PORT="${BACKUP_DB_PORT:-5432}"
DB_USER="${BACKUP_DB_USER:-lsx_user}"
LOG_FILE="/var/backups/lsx/restore.log"

# ==========================================
# Logging Function
# ==========================================

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "${LOG_FILE}"
}

error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $*" | tee -a "${LOG_FILE}" >&2
}

# ==========================================
# Input Validation
# ==========================================

if [ $# -eq 0 ]; then
    error "No backup file specified!"
    echo ""
    echo "Usage: $0 <backup_file>"
    echo ""
    echo "Example:"
    echo "  $0 /var/backups/lsx/db/lsx_db_20251116_030000.sql.gz"
    echo ""
    exit 1
fi

BACKUP_FILE="$1"

log "=========================================="
log "LSX PostgreSQL Restore Starting"
log "=========================================="

# Check if backup file exists
if [ ! -f "${BACKUP_FILE}" ]; then
    error "Backup file not found: ${BACKUP_FILE}"
    exit 1
fi

log "Backup file: ${BACKUP_FILE}"
log "Database: ${DB_NAME}"
log "Host: ${DB_HOST}:${DB_PORT}"
log "User: ${DB_USER}"

# ==========================================
# Safety Confirmation
# ==========================================

echo ""
echo "⚠️  WARNING: This will DESTROY the current database and replace it with the backup!"
echo ""
echo "Database to be DROPPED: ${DB_NAME}"
echo "Backup file: ${BACKUP_FILE}"
echo ""
read -p "Are you ABSOLUTELY SURE you want to continue? (yes/no): " CONFIRM

if [ "${CONFIRM}" != "yes" ]; then
    log "Restore cancelled by user"
    echo "Restore cancelled."
    exit 0
fi

# ==========================================
# Pre-flight Checks
# ==========================================

# Check if psql is available
if ! command -v psql &> /dev/null; then
    error "psql command not found. Please install PostgreSQL client tools."
    exit 1
fi

# ==========================================
# Decompress if needed
# ==========================================

TEMP_SQL_FILE="${BACKUP_FILE}"

if [[ "${BACKUP_FILE}" == *.gz ]]; then
    log "Decompressing backup file..."
    TEMP_SQL_FILE="${BACKUP_FILE%.gz}"

    if gunzip -c "${BACKUP_FILE}" > "${TEMP_SQL_FILE}"; then
        log "Decompression completed"
    else
        error "Decompression failed!"
        exit 1
    fi
fi

# ==========================================
# Stop Backend Service (if running)
# ==========================================

log "Stopping LSX backend service (if running)..."

if systemctl is-active --quiet lsx-backend; then
    sudo systemctl stop lsx-backend
    log "Backend service stopped"
else
    log "Backend service not running"
fi

# ==========================================
# Database Restore
# ==========================================

log "Dropping and recreating database..."

# Drop existing database connections
PGPASSWORD="${PGPASSWORD:-}" psql -h "${DB_HOST}" -p "${DB_PORT}" -U postgres -c \
    "SELECT pg_terminate_backend(pg_stat_activity.pid)
     FROM pg_stat_activity
     WHERE pg_stat_activity.datname = '${DB_NAME}'
       AND pid <> pg_backend_pid();" || true

# Drop database
PGPASSWORD="${PGPASSWORD:-}" psql -h "${DB_HOST}" -p "${DB_PORT}" -U postgres -c \
    "DROP DATABASE IF EXISTS ${DB_NAME};"

# Create database
PGPASSWORD="${PGPASSWORD:-}" psql -h "${DB_HOST}" -p "${DB_PORT}" -U postgres -c \
    "CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};"

log "Database recreated successfully"

log "Restoring backup..."

# Restore from SQL file
if PGPASSWORD="${PGPASSWORD:-}" psql \
    -h "${DB_HOST}" \
    -p "${DB_PORT}" \
    -U "${DB_USER}" \
    -d "${DB_NAME}" \
    -f "${TEMP_SQL_FILE}"; then

    log "Database restore completed successfully"
else
    error "Database restore failed!"
    exit 1
fi

# ==========================================
# Cleanup temporary files
# ==========================================

if [[ "${BACKUP_FILE}" == *.gz ]]; then
    rm -f "${TEMP_SQL_FILE}"
    log "Temporary decompressed file removed"
fi

# ==========================================
# Start Backend Service
# ==========================================

log "Starting LSX backend service..."

if systemctl start lsx-backend; then
    log "Backend service started"
else
    error "Failed to start backend service"
fi

# ==========================================
# Verification
# ==========================================

log "Verifying database connection..."

if PGPASSWORD="${PGPASSWORD:-}" psql \
    -h "${DB_HOST}" \
    -p "${DB_PORT}" \
    -U "${DB_USER}" \
    -d "${DB_NAME}" \
    -c "SELECT count(*) FROM users;" > /dev/null 2>&1; then

    USER_COUNT=$(PGPASSWORD="${PGPASSWORD:-}" psql \
        -h "${DB_HOST}" \
        -p "${DB_PORT}" \
        -U "${DB_USER}" \
        -d "${DB_NAME}" \
        -t -c "SELECT count(*) FROM users;")

    log "Database verification successful - User count: ${USER_COUNT}"
else
    error "Database verification failed!"
fi

# ==========================================
# Summary
# ==========================================

log "=========================================="
log "Restore completed successfully!"
log "Database: ${DB_NAME}"
log "Restored from: ${BACKUP_FILE}"
log "=========================================="

echo ""
echo "✅ Database restored successfully!"
echo ""
echo "Next steps:"
echo "1. Verify application functionality"
echo "2. Check logs: journalctl -u lsx-backend -f"
echo "3. Test API health: curl http://localhost:8000/health"
echo ""

exit 0
