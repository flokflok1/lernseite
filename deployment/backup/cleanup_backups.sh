#!/bin/bash
# LernsystemX Backup Cleanup Script
#
# This script removes old backups based on retention policy
# Usage: ./cleanup_backups.sh
#
# Environment Variables (from .env.production):
# - BACKUP_DIR
# - BACKUP_RETENTION_DAYS

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
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"
DB_BACKUP_DIR="${BACKUP_DIR}/db"
LOG_FILE="${BACKUP_DIR}/cleanup.log"

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
# Main Cleanup Logic
# ==========================================

log "=========================================="
log "LSX Backup Cleanup Starting"
log "=========================================="
log "Backup directory: ${DB_BACKUP_DIR}"
log "Retention policy: ${RETENTION_DAYS} days"

# Check if backup directory exists
if [ ! -d "${DB_BACKUP_DIR}" ]; then
    log "Backup directory does not exist: ${DB_BACKUP_DIR}"
    exit 0
fi

# Count total backups before cleanup
TOTAL_BACKUPS=$(find "${DB_BACKUP_DIR}" -name "lsx_db_*.sql*" -type f | wc -l)
log "Total backups found: ${TOTAL_BACKUPS}"

# Safety check: Never delete if less than 2 backups exist
if [ "${TOTAL_BACKUPS}" -lt 2 ]; then
    log "Less than 2 backups exist - skipping cleanup for safety"
    exit 0
fi

# Find and delete old backups
DELETED_COUNT=0

log "Finding backups older than ${RETENTION_DAYS} days..."

while IFS= read -r backup_file; do
    BACKUP_NAME=$(basename "${backup_file}")
    BACKUP_SIZE=$(du -h "${backup_file}" | cut -f1)

    log "Deleting: ${BACKUP_NAME} (${BACKUP_SIZE})"

    if rm -f "${backup_file}"; then
        ((DELETED_COUNT++))
    else
        error "Failed to delete: ${backup_file}"
    fi
done < <(find "${DB_BACKUP_DIR}" -name "lsx_db_*.sql*" -type f -mtime +${RETENTION_DAYS})

# ==========================================
# Summary
# ==========================================

REMAINING_BACKUPS=$((TOTAL_BACKUPS - DELETED_COUNT))

log "=========================================="
log "Cleanup Summary"
log "Deleted: ${DELETED_COUNT} backups"
log "Remaining: ${REMAINING_BACKUPS} backups"
log "=========================================="

# List remaining backups
if [ "${REMAINING_BACKUPS}" -gt 0 ]; then
    log "Remaining backups:"
    find "${DB_BACKUP_DIR}" -name "lsx_db_*.sql*" -type f -printf "  - %f (%TY-%Tm-%Td %TH:%TM)\n" | tee -a "${LOG_FILE}"
fi

exit 0
