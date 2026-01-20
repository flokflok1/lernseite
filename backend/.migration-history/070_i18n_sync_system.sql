-- ============================================================================
-- Migration 070: i18n Synchronization System
-- ============================================================================
-- Description: Complete i18n sync system for managing translation synchronization
--              between frontend translation files and database translations.
--              Tracks sync history, changes, and user resolutions.
-- Version: 1.0.0
-- Author: Claude (i18n Sync Implementation)
-- Date: 2026-01-15
-- ============================================================================

-- Create schema if not exists
CREATE SCHEMA IF NOT EXISTS i18n;

-- ============================================================================
-- Main Sync History Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS i18n.i18n_syncs (
    sync_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Sync metadata
    mode VARCHAR(10) NOT NULL CHECK (mode IN ('MANUAL', 'AUTO')),
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('PENDING', 'SCANNING', 'COMPLETED', 'FAILED', 'ROLLED_BACK')),

    -- Operation details
    languages_synced VARCHAR[] NOT NULL,  -- e.g., ['de', 'en', 'pl']
    total_keys INT NOT NULL DEFAULT 0,
    new_keys INT NOT NULL DEFAULT 0,
    changed_keys INT NOT NULL DEFAULT 0,
    deleted_keys INT NOT NULL DEFAULT 0,
    conflicted_keys INT NOT NULL DEFAULT 0,

    -- Performance metrics
    scan_duration_ms INT,  -- Milliseconds to complete scan

    -- User tracking
    initiated_by_user_id UUID NOT NULL,
    initiated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP,

    -- Rollback tracking
    rolled_back_by_user_id UUID,
    rolled_back_at TIMESTAMP,
    rollback_reason TEXT,
    parent_sync_id UUID REFERENCES i18n.i18n_syncs(sync_id) ON DELETE SET NULL,

    -- Metadata
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Foreign keys
    CONSTRAINT fk_initiated_by_user FOREIGN KEY (initiated_by_user_id)
        REFERENCES core.users(user_id) ON DELETE RESTRICT,
    CONSTRAINT fk_rolled_back_by_user FOREIGN KEY (rolled_back_by_user_id)
        REFERENCES core.users(user_id) ON DELETE SET NULL
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_i18n_syncs_status
    ON i18n.i18n_syncs(status);
CREATE INDEX IF NOT EXISTS idx_i18n_syncs_mode
    ON i18n.i18n_syncs(mode);
CREATE INDEX IF NOT EXISTS idx_i18n_syncs_initiated_by
    ON i18n.i18n_syncs(initiated_by_user_id);
CREATE INDEX IF NOT EXISTS idx_i18n_syncs_initiated_at
    ON i18n.i18n_syncs(initiated_at DESC);
CREATE INDEX IF NOT EXISTS idx_i18n_syncs_status_initiated
    ON i18n.i18n_syncs(status, initiated_at DESC);

-- ============================================================================
-- Sync Changes Table (detailed change tracking)
-- ============================================================================
CREATE TABLE IF NOT EXISTS i18n.sync_changes (
    change_id BIGSERIAL PRIMARY KEY,
    sync_id UUID NOT NULL REFERENCES i18n.i18n_syncs(sync_id) ON DELETE CASCADE,

    -- Key information
    translation_key VARCHAR(255) NOT NULL,
    language_code VARCHAR(10) NOT NULL,

    -- Change details
    change_type VARCHAR(20) NOT NULL
        CHECK (change_type IN ('NEW', 'CHANGED', 'DELETED', 'CONFLICT')),

    -- Values
    frontend_value TEXT,  -- Current value in frontend translation file
    database_value TEXT,  -- Current value in database
    previous_value TEXT,  -- Previous database value

    -- Similarity score (for conflict detection)
    similarity_score FLOAT DEFAULT 0.0 CHECK (similarity_score >= 0 AND similarity_score <= 1.0),

    -- Resolution
    resolution VARCHAR(20)
        CHECK (resolution IS NULL OR resolution IN ('ADD', 'UPDATE', 'DELETE', 'SKIP')),
    resolution_notes TEXT,
    resolved_at TIMESTAMP,

    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_sync_changes_sync_id
    ON i18n.sync_changes(sync_id);
CREATE INDEX IF NOT EXISTS idx_sync_changes_key_lang
    ON i18n.sync_changes(translation_key, language_code);
CREATE INDEX IF NOT EXISTS idx_sync_changes_change_type
    ON i18n.sync_changes(change_type);
CREATE INDEX IF NOT EXISTS idx_sync_changes_resolution
    ON i18n.sync_changes(resolution);
CREATE INDEX IF NOT EXISTS idx_sync_changes_sync_type_resolution
    ON i18n.sync_changes(sync_id, change_type, resolution);

-- ============================================================================
-- Sync Resolutions Table (user decisions)
-- ============================================================================
CREATE TABLE IF NOT EXISTS i18n.sync_resolutions (
    resolution_id BIGSERIAL PRIMARY KEY,
    sync_id UUID NOT NULL REFERENCES i18n.i18n_syncs(sync_id) ON DELETE CASCADE,
    change_id BIGINT NOT NULL REFERENCES i18n.sync_changes(change_id) ON DELETE CASCADE,

    -- Decision information
    translation_key VARCHAR(255) NOT NULL,
    language_code VARCHAR(10) NOT NULL,

    -- User decision
    chosen_action VARCHAR(20) NOT NULL
        CHECK (chosen_action IN ('ADD', 'UPDATE', 'DELETE', 'SKIP')),

    -- Tracking
    decided_by_user_id UUID NOT NULL REFERENCES core.users(user_id) ON DELETE RESTRICT,
    decided_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Notes
    decision_notes TEXT,

    -- Applied status
    applied BOOLEAN DEFAULT FALSE,
    applied_at TIMESTAMP,

    CONSTRAINT fk_change_uniq UNIQUE(change_id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_sync_resolutions_sync_id
    ON i18n.sync_resolutions(sync_id);
CREATE INDEX IF NOT EXISTS idx_sync_resolutions_change_id
    ON i18n.sync_resolutions(change_id);
CREATE INDEX IF NOT EXISTS idx_sync_resolutions_decided_by
    ON i18n.sync_resolutions(decided_by_user_id);
CREATE INDEX IF NOT EXISTS idx_sync_resolutions_applied
    ON i18n.sync_resolutions(applied, applied_at DESC);

-- ============================================================================
-- Update Triggers
-- ============================================================================

-- Trigger for i18n_syncs.updated_at
CREATE OR REPLACE FUNCTION i18n.update_i18n_sync_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_i18n_sync_updated_at ON i18n.i18n_syncs;
CREATE TRIGGER trg_i18n_sync_updated_at
    BEFORE UPDATE ON i18n.i18n_syncs
    FOR EACH ROW
    EXECUTE FUNCTION i18n.update_i18n_sync_updated_at();

-- ============================================================================
-- Grant Permissions
-- ============================================================================
GRANT SELECT, INSERT, UPDATE, DELETE ON i18n.i18n_syncs TO PUBLIC;
GRANT SELECT, INSERT, UPDATE, DELETE ON i18n.sync_changes TO PUBLIC;
GRANT SELECT, INSERT, UPDATE, DELETE ON i18n.sync_resolutions TO PUBLIC;
GRANT USAGE, SELECT ON SEQUENCE i18n.sync_changes_change_id_seq TO PUBLIC;
GRANT USAGE, SELECT ON SEQUENCE i18n.sync_resolutions_resolution_id_seq TO PUBLIC;

-- ============================================================================
-- Verification
-- ============================================================================
DO $$
DECLARE
    table_count INT;
BEGIN
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_schema = 'i18n' AND table_name IN ('i18n_syncs', 'sync_changes', 'sync_resolutions');

    IF table_count != 3 THEN
        RAISE EXCEPTION 'Not all i18n_sync tables were created! Expected 3, got %', table_count;
    END IF;

    RAISE NOTICE 'Migration 070 completed successfully!';
    RAISE NOTICE '  - i18n schema created';
    RAISE NOTICE '  - i18n_syncs table created (sync history)';
    RAISE NOTICE '  - sync_changes table created (detailed changes)';
    RAISE NOTICE '  - sync_resolutions table created (user decisions)';
    RAISE NOTICE '  - Indexes and triggers created';
END $$;
