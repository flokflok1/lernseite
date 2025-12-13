#!/bin/bash
# LernsystemX PostgreSQL Backup Script
#
# This script creates compressed PostgreSQL backups with timestamps
# Usage: ./backup_db.sh
#
# Environment Variables (from .env.production):
# - BACKUP_DIR
# - BACKUP_DB_NAME
# - BACKUP_DB_HOST
# - BACKUP_DB_PORT
# - BACKUP_DB_USER
# - BACKUP_ENABLE_COMPRESSION

set -euo pipefail

# ==========================================
# Configuration
# ==========================================

# Load environment variables if .env.production exists
if [ -f "/opt/lsx/backend/.env.production" ]; then
    export $(grep -v '^#' /opt/lsx/backend/.env.production | xargs)
fi

# Default values
BACKUP_DIR="${BACKUP_DIR:-/var/backups/lsx}"
DB_NAME="${BACKUP_DB_NAME:-lernsystemx_prod}"
DB_HOST="${BACKUP_DB_HOST:-localhost}"
DB_PORT="${BACKUP_DB_PORT:-5432}"
DB_USER="${BACKUP_DB_USER:-lsx_user}"
ENABLE_COMPRESSION="${BACKUP_ENABLE_COMPRESSION:-true}"

# Backup directory structure
DB_BACKUP_DIR="${BACKUP_DIR}/db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILENAME="lsx_db_${TIMESTAMP}.sql"
LOG_FILE="${BACKUP_DIR}/backup.log"

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
# Pre-flight Checks
# ==========================================

log "=========================================="
log "LSX PostgreSQL Backup Starting"
log "=========================================="

# Check if pg_dump is available
if ! command -v pg_dump &> /dev/null; then
    error "pg_dump command not found. Please install PostgreSQL client tools."
    exit 1
fi

# Create backup directories if they don't exist
mkdir -p "${DB_BACKUP_DIR}"
mkdir -p "$(dirname "${LOG_FILE}")"

log "Backup directory: ${DB_BACKUP_DIR}"
log "Database: ${DB_NAME}"
log "Host: ${DB_HOST}:${DB_PORT}"
log "User: ${DB_USER}"

# ==========================================
# Database Backup
# ==========================================

log "Starting database backup..."

BACKUP_PATH="${DB_BACKUP_DIR}/${BACKUP_FILENAME}"

# Execute pg_dump
if PGPASSWORD="${PGPASSWORD:-}" pg_dump \
    -h "${DB_HOST}" \
    -p "${DB_PORT}" \
    -U "${DB_USER}" \
    -d "${DB_NAME}" \
    -F p \
    --no-owner \
    --no-acl \
    --clean \
    --if-exists \
    -f "${BACKUP_PATH}"; then

    log "Database dump completed successfully"
else
    error "Database dump failed!"
    exit 1
fi

# ==========================================
# Compression (if enabled)
# ==========================================

if [ "${ENABLE_COMPRESSION}" = "true" ] || [ "${ENABLE_COMPRESSION}" = "True" ]; then
    log "Compressing backup..."

    if gzip -9 "${BACKUP_PATH}"; then
        BACKUP_PATH="${BACKUP_PATH}.gz"
        log "Compression completed: ${BACKUP_PATH}"
    else
        error "Compression failed, keeping uncompressed backup"
    fi
fi

# ==========================================
# Backup Verification
# ==========================================

if [ -f "${BACKUP_PATH}" ]; then
    BACKUP_SIZE=$(du -h "${BACKUP_PATH}" | cut -f1)
    log "Backup file size: ${BACKUP_SIZE}"
    log "Backup saved to: ${BACKUP_PATH}"
else
    error "Backup file not found after creation!"
    exit 1
fi

# ==========================================
# Optional: Remote Backup (S3/MinIO)
# ==========================================

REMOTE_ENABLED="${BACKUP_REMOTE_ENABLED:-false}"

if [ "${REMOTE_ENABLED}" = "true" ] || [ "${REMOTE_ENABLED}" = "True" ]; then
    log "Remote backup enabled - uploading to S3..."

    if command -v aws &> /dev/null; then
        S3_BUCKET="${BACKUP_S3_BUCKET:-lsx-backups}"
        S3_KEY="db/$(basename "${BACKUP_PATH}")"

        if aws s3 cp "${BACKUP_PATH}" "s3://${S3_BUCKET}/${S3_KEY}"; then
            log "Remote backup uploaded to s3://${S3_BUCKET}/${S3_KEY}"
        else
            error "Remote backup upload failed (non-critical)"
        fi
    else
        log "AWS CLI not found - skipping remote backup"
    fi
fi

# ==========================================
# Summary
# ==========================================

log "=========================================="
log "Backup completed successfully!"
log "File: ${BACKUP_PATH}"
log "Size: ${BACKUP_SIZE}"
log "=========================================="

exit 0
