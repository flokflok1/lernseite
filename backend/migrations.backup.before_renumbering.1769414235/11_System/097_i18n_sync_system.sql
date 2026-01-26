-- ============================================================================
-- Migration: 086_i18n_sync_system.sql
-- Description: i18n Sync System (Frontend ↔ Database synchronization)
--              - Audit trail for sync operations (MANUAL vs AUTO modes)
--              - Per-key tracking and conflict resolution
--              - JSONB snapshots for rollback capability
--
-- Version: 2.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-01-16
-- ============================================================================
--
-- Part 3 of 5-part i18n system (split from 038_i18n_complete.sql)
-- Other parts: 084 (core), 085 (languages), 087 (triggers), 088 (namespaces)
--
-- FRONTEND SYNC ARCHITECTURE:
-- This system tracks synchronization between frontend JSON locale files and
-- the database i18n system. It supports both MANUAL and AUTO sync modes,
-- provides conflict resolution, and enables rollback via JSONB snapshots.
--
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. SYNC HISTORY TABLE (Audit Trail)
-- ============================================================================
-- Purpose: Track all sync operations with summary statistics
-- Features: MANUAL vs AUTO mode, scan/apply timestamps, error tracking
-- ============================================================================

CREATE TABLE IF NOT EXISTS translations.i18n_sync_history (
    sync_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sync_mode VARCHAR(20) NOT NULL, -- 'MANUAL' or 'AUTO'
    sync_status VARCHAR(20) NOT NULL, -- 'SCANNING', 'PENDING', 'APPLYING', 'COMPLETED', 'FAILED', 'ROLLED_BACK'

    -- Summary Statistics
    total_keys INTEGER DEFAULT 0,
    keys_added INTEGER DEFAULT 0,
    keys_updated INTEGER DEFAULT 0,
    keys_deleted INTEGER DEFAULT 0,
    keys_skipped INTEGER DEFAULT 0,
    keys_conflicted INTEGER DEFAULT 0,

    -- Languages involved
    languages_affected VARCHAR(10)[] DEFAULT '{}',

    -- Scan Results
    scan_started_at TIMESTAMP,
    scan_completed_at TIMESTAMP,

    -- Apply Results
    apply_started_at TIMESTAMP,
    apply_completed_at TIMESTAMP,

    -- Metadata
    initiated_by UUID REFERENCES core.users(user_id) ON DELETE SET NULL,
    completed_by UUID REFERENCES core.users(user_id) ON DELETE SET NULL,
    error_message TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_sync_mode CHECK (sync_mode IN ('MANUAL', 'AUTO')),
    CONSTRAINT chk_sync_status CHECK (sync_status IN ('SCANNING', 'PENDING', 'APPLYING', 'COMPLETED', 'FAILED', 'ROLLED_BACK')),
    CONSTRAINT chk_sync_stats CHECK (
        keys_added >= 0 AND keys_updated >= 0 AND keys_deleted >= 0 AND
        keys_skipped >= 0 AND keys_conflicted >= 0
    )
);

CREATE INDEX IF NOT EXISTS idx_sync_history_status ON translations.i18n_sync_history(sync_status);
CREATE INDEX IF NOT EXISTS idx_sync_history_mode ON translations.i18n_sync_history(sync_mode);
CREATE INDEX IF NOT EXISTS idx_sync_history_initiated_by ON translations.i18n_sync_history(initiated_by);
CREATE INDEX IF NOT EXISTS idx_sync_history_created ON translations.i18n_sync_history(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_sync_history_languages ON translations.i18n_sync_history USING GIN (languages_affected);

COMMENT ON TABLE translations.i18n_sync_history IS 'Audit trail of all i18n synchronization operations (MANUAL vs AUTO modes)';

-- ============================================================================
-- 2. SYNC DETAILS TABLE (Per-Key Decisions)
-- ============================================================================
-- Purpose: Track individual key-level decisions during sync
-- Features: Action tracking (ADD/UPDATE/DELETE), conflict detection,
--           similarity scoring, manual resolution support
-- ============================================================================

CREATE TABLE IF NOT EXISTS translations.i18n_sync_details (
    detail_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sync_id UUID NOT NULL REFERENCES translations.i18n_sync_history(sync_id) ON DELETE CASCADE,

    -- Key Information
    namespace_code VARCHAR(100) NOT NULL,
    key_path VARCHAR(500) NOT NULL,
    language VARCHAR(10) NOT NULL,

    -- Action and Status
    action VARCHAR(20) NOT NULL, -- 'ADD', 'UPDATE', 'DELETE', 'SKIP', 'CONFLICT'
    resolution_status VARCHAR(20) NOT NULL, -- 'PENDING', 'RESOLVED', 'MANUAL_OVERRIDE', 'FAILED'

    -- Comparison Data
    frontend_value TEXT,
    database_value TEXT,
    similarity_score NUMERIC(5,2),

    -- Resolution Details
    conflict_reason VARCHAR(255),
    manual_resolution_value TEXT,
    resolved_by UUID REFERENCES core.users(user_id) ON DELETE SET NULL,

    -- Change Detection
    is_new BOOLEAN DEFAULT FALSE,
    is_changed BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    change_magnitude VARCHAR(20), -- 'MINOR', 'MODERATE', 'MAJOR'

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_action CHECK (action IN ('ADD', 'UPDATE', 'DELETE', 'SKIP', 'CONFLICT')),
    CONSTRAINT chk_resolution CHECK (resolution_status IN ('PENDING', 'RESOLVED', 'MANUAL_OVERRIDE', 'FAILED')),
    CONSTRAINT chk_similarity CHECK (similarity_score >= 0 AND similarity_score <= 1),
    CONSTRAINT chk_magnitude CHECK (change_magnitude IN ('MINOR', 'MODERATE', 'MAJOR'))
);

CREATE INDEX IF NOT EXISTS idx_sync_details_sync_id ON translations.i18n_sync_details(sync_id);
CREATE INDEX IF NOT EXISTS idx_sync_details_action ON translations.i18n_sync_details(action);
CREATE INDEX IF NOT EXISTS idx_sync_details_status ON translations.i18n_sync_details(resolution_status);
CREATE INDEX IF NOT EXISTS idx_sync_details_namespace ON translations.i18n_sync_details(namespace_code);
CREATE INDEX IF NOT EXISTS idx_sync_details_language ON translations.i18n_sync_details(language);
CREATE INDEX IF NOT EXISTS idx_sync_details_key ON translations.i18n_sync_details(key_path);
CREATE INDEX IF NOT EXISTS idx_sync_details_conflict ON translations.i18n_sync_details(sync_id, action) WHERE action = 'CONFLICT';
CREATE INDEX IF NOT EXISTS idx_sync_details_pending ON translations.i18n_sync_details(sync_id, resolution_status) WHERE resolution_status = 'PENDING';

COMMENT ON TABLE translations.i18n_sync_details IS 'Per-key tracking for sync operations with conflict resolution';

-- ============================================================================
-- 3. SYNC SNAPSHOTS TABLE (Backup/Rollback)
-- ============================================================================
-- Purpose: Store JSONB snapshots of database state for rollback capability
-- Features: PRE_SYNC (before), POST_SYNC (after), ROLLBACK (restored state)
--           Stores complete i18n state as JSONB for point-in-time restore
-- ============================================================================

CREATE TABLE IF NOT EXISTS translations.i18n_sync_snapshots (
    snapshot_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sync_id UUID NOT NULL REFERENCES translations.i18n_sync_history(sync_id) ON DELETE CASCADE,

    -- Snapshot Type
    snapshot_type VARCHAR(50) NOT NULL, -- 'PRE_SYNC', 'POST_SYNC', 'ROLLBACK'

    -- Database State (JSONB)
    db_state JSONB NOT NULL,

    -- Statistics
    total_keys INTEGER DEFAULT 0,
    affected_keys INTEGER DEFAULT 0,
    languages_covered VARCHAR(10)[] DEFAULT '{}',

    -- Metadata
    snapshot_reason TEXT,
    created_by UUID REFERENCES core.users(user_id) ON DELETE SET NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_snapshot_type CHECK (snapshot_type IN ('PRE_SYNC', 'POST_SYNC', 'ROLLBACK'))
);

CREATE INDEX IF NOT EXISTS idx_snapshot_sync_id ON translations.i18n_sync_snapshots(sync_id);
CREATE INDEX IF NOT EXISTS idx_snapshot_type ON translations.i18n_sync_snapshots(snapshot_type);
CREATE INDEX IF NOT EXISTS idx_snapshot_created ON translations.i18n_sync_snapshots(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_snapshot_languages ON translations.i18n_sync_snapshots USING GIN (languages_covered);

COMMENT ON TABLE translations.i18n_sync_snapshots IS 'JSONB snapshots of database state before/after sync for rollback capability';

-- Ensure only one snapshot of each type per sync
ALTER TABLE translations.i18n_sync_snapshots
ADD CONSTRAINT IF NOT EXISTS uq_snapshot_type_per_sync
UNIQUE (sync_id, snapshot_type);

-- ============================================================================
-- 4. SYNC SYSTEM TRIGGERS (Auto-update timestamps)
-- ============================================================================
-- Purpose: Automatically update updated_at timestamps on record modification
-- ============================================================================

CREATE OR REPLACE FUNCTION translations.update_sync_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_sync_history_updated_at ON translations.i18n_sync_history;
CREATE TRIGGER trg_sync_history_updated_at
    BEFORE UPDATE ON translations.i18n_sync_history
    FOR EACH ROW EXECUTE FUNCTION translations.update_sync_updated_at();

DROP TRIGGER IF EXISTS trg_sync_details_updated_at ON translations.i18n_sync_details;
CREATE TRIGGER trg_sync_details_updated_at
    BEFORE UPDATE ON translations.i18n_sync_details
    FOR EACH ROW EXECUTE FUNCTION translations.update_sync_updated_at();

COMMIT;

-- ============================================================================
-- END MIGRATION 086 (i18n Sync System - Frontend ↔ Database)
-- ============================================================================
