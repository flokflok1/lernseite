-- =====================================================
-- Migration 077: i18n Sync System (Frontend ↔ DB Sync)
-- =====================================================
-- Purpose: Create audit trail, resolution tracking, and snapshots for i18n synchronization
-- Features:
--   - Track all sync operations (scan, apply, rollback)
--   - Record per-key resolution decisions (ADD/SKIP/UPDATE/DELETE)
--   - Backup JSONB snapshots for rollback capability
--   - Support both MANUAL and AUTO sync modes
--
-- Tables:
-- - translations.i18n_sync_history (sync operation log)
-- - translations.i18n_sync_details (per-key decisions)
-- - translations.i18n_sync_snapshots (JSONB backup data)
--
-- Created: 2026-01-15
-- Author: i18n System Migration
-- =====================================================

BEGIN;

-- =====================================================
-- 1. SYNC HISTORY TABLE (Audit Trail)
-- =====================================================

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
    languages_affected VARCHAR(10)[] DEFAULT '{}', -- e.g. '{de,en,pl}'

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
        keys_added >= 0 AND
        keys_updated >= 0 AND
        keys_deleted >= 0 AND
        keys_skipped >= 0 AND
        keys_conflicted >= 0
    )
);

CREATE INDEX idx_sync_history_status ON translations.i18n_sync_history(sync_status);
CREATE INDEX idx_sync_history_mode ON translations.i18n_sync_history(sync_mode);
CREATE INDEX idx_sync_history_initiated_by ON translations.i18n_sync_history(initiated_by);
CREATE INDEX idx_sync_history_created ON translations.i18n_sync_history(created_at DESC);
CREATE INDEX idx_sync_history_languages ON translations.i18n_sync_history USING GIN (languages_affected);

COMMENT ON TABLE translations.i18n_sync_history IS 'Audit trail of all i18n synchronization operations (MANUAL vs AUTO modes)';
COMMENT ON COLUMN translations.i18n_sync_history.sync_id IS 'Unique identifier for this sync operation';
COMMENT ON COLUMN translations.i18n_sync_history.sync_mode IS 'MANUAL: admin selects actions per-key, AUTO: system decides based on rules';
COMMENT ON COLUMN translations.i18n_sync_history.sync_status IS 'Operation progress (SCANNING → PENDING → APPLYING → COMPLETED/FAILED)';
COMMENT ON COLUMN translations.i18n_sync_history.languages_affected IS 'Array of language codes involved in this sync (e.g., de, en, pl)';
COMMENT ON COLUMN translations.i18n_sync_history.initiated_by IS 'Admin user who started the sync';

-- =====================================================
-- 2. SYNC DETAILS TABLE (Per-Key Decisions)
-- =====================================================

CREATE TABLE IF NOT EXISTS translations.i18n_sync_details (
    detail_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sync_id UUID NOT NULL REFERENCES translations.i18n_sync_history(sync_id) ON DELETE CASCADE,

    -- Key Information
    namespace_code VARCHAR(100) NOT NULL,
    key_path VARCHAR(500) NOT NULL,
    language VARCHAR(10) NOT NULL, -- 'de', 'en', 'pl'

    -- Action and Status
    action VARCHAR(20) NOT NULL, -- 'ADD', 'UPDATE', 'DELETE', 'SKIP', 'CONFLICT'
    resolution_status VARCHAR(20) NOT NULL, -- 'PENDING', 'RESOLVED', 'MANUAL_OVERRIDE', 'FAILED'

    -- Comparison Data
    frontend_value TEXT, -- Value from JSON
    database_value TEXT, -- Current database value
    similarity_score NUMERIC(5,2), -- 0.00 to 1.00 (how similar they are)

    -- Resolution Details (if CONFLICT or MANUAL_OVERRIDE)
    conflict_reason VARCHAR(255), -- Why it's a conflict (e.g., 'VALUE_CHANGED')
    manual_resolution_value TEXT, -- Admin-edited value (for MANUAL mode)
    resolved_by UUID REFERENCES core.users(user_id) ON DELETE SET NULL, -- Admin who resolved

    -- Change Detection
    is_new BOOLEAN DEFAULT FALSE, -- True if key doesn't exist in DB
    is_changed BOOLEAN DEFAULT FALSE, -- True if frontend value differs from DB
    is_deleted BOOLEAN DEFAULT FALSE, -- True if in DB but not in frontend JSON
    change_magnitude VARCHAR(20), -- 'MINOR' (<5%), 'MODERATE' (5-10%), 'MAJOR' (>10%)

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_action CHECK (action IN ('ADD', 'UPDATE', 'DELETE', 'SKIP', 'CONFLICT')),
    CONSTRAINT chk_resolution CHECK (resolution_status IN ('PENDING', 'RESOLVED', 'MANUAL_OVERRIDE', 'FAILED')),
    CONSTRAINT chk_similarity CHECK (similarity_score >= 0 AND similarity_score <= 1),
    CONSTRAINT chk_magnitude CHECK (change_magnitude IN ('MINOR', 'MODERATE', 'MAJOR'))
);

CREATE INDEX idx_sync_details_sync_id ON translations.i18n_sync_details(sync_id);
CREATE INDEX idx_sync_details_action ON translations.i18n_sync_details(action);
CREATE INDEX idx_sync_details_status ON translations.i18n_sync_details(resolution_status);
CREATE INDEX idx_sync_details_namespace ON translations.i18n_sync_details(namespace_code);
CREATE INDEX idx_sync_details_language ON translations.i18n_sync_details(language);
CREATE INDEX idx_sync_details_key ON translations.i18n_sync_details(key_path);
CREATE INDEX idx_sync_details_conflict ON translations.i18n_sync_details(sync_id, action) WHERE action = 'CONFLICT';
CREATE INDEX idx_sync_details_pending ON translations.i18n_sync_details(sync_id, resolution_status) WHERE resolution_status = 'PENDING';

COMMENT ON TABLE translations.i18n_sync_details IS 'Per-key tracking for sync operations (what action, why, current status)';
COMMENT ON COLUMN translations.i18n_sync_details.action IS 'Planned action: ADD (new), UPDATE (changed), DELETE (removed), SKIP (ignore), CONFLICT (needs decision)';
COMMENT ON COLUMN translations.i18n_sync_details.resolution_status IS 'PENDING (awaiting decision), RESOLVED (decided), MANUAL_OVERRIDE (admin edited), FAILED (error)';
COMMENT ON COLUMN translations.i18n_sync_details.similarity_score IS 'Text similarity 0-1 (1.0 = identical, used to detect minor changes vs major rewrites)';
COMMENT ON COLUMN translations.i18n_sync_details.conflict_reason IS 'Why conflict detected: VALUE_CHANGED, MANUAL_EDIT, LANGUAGE_MISMATCH, etc.';
COMMENT ON COLUMN translations.i18n_sync_details.change_magnitude IS 'How big the change is: MINOR <5%, MODERATE 5-10%, MAJOR >10% (helps auto-decide in AUTO mode)';

-- =====================================================
-- 3. SYNC SNAPSHOTS TABLE (Backup/Rollback)
-- =====================================================

CREATE TABLE IF NOT EXISTS translations.i18n_sync_snapshots (
    snapshot_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sync_id UUID NOT NULL REFERENCES translations.i18n_sync_history(sync_id) ON DELETE CASCADE,

    -- Snapshot Type
    snapshot_type VARCHAR(50) NOT NULL, -- 'PRE_SYNC', 'POST_SYNC', 'ROLLBACK'

    -- Database State (JSONB for flexible structure)
    -- Structure: {
    --   "namespace_code": {
    --     "de": {"key_path": "translation_text", ...},
    --     "en": {...},
    --     "pl": {...}
    --   },
    --   ...
    -- }
    db_state JSONB NOT NULL,

    -- Statistics
    total_keys INTEGER DEFAULT 0,
    affected_keys INTEGER DEFAULT 0,
    languages_covered VARCHAR(10)[] DEFAULT '{}',

    -- Metadata
    snapshot_reason TEXT, -- 'Initial backup before sync', 'Rollback point', etc.
    created_by UUID REFERENCES core.users(user_id) ON DELETE SET NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_snapshot_type CHECK (snapshot_type IN ('PRE_SYNC', 'POST_SYNC', 'ROLLBACK'))
);

CREATE INDEX idx_snapshot_sync_id ON translations.i18n_sync_snapshots(sync_id);
CREATE INDEX idx_snapshot_type ON translations.i18n_sync_snapshots(snapshot_type);
CREATE INDEX idx_snapshot_created ON translations.i18n_sync_snapshots(created_at DESC);
CREATE INDEX idx_snapshot_languages ON translations.i18n_sync_snapshots USING GIN (languages_covered);

COMMENT ON TABLE translations.i18n_sync_snapshots IS 'JSONB snapshots of database state before/after sync for rollback capability';
COMMENT ON COLUMN translations.i18n_sync_snapshots.snapshot_type IS 'PRE_SYNC (backup), POST_SYNC (after apply), ROLLBACK (when rolling back)';
COMMENT ON COLUMN translations.i18n_sync_snapshots.db_state IS 'Full JSONB snapshot of translations for all affected namespaces/languages';
COMMENT ON COLUMN translations.i18n_sync_snapshots.snapshot_reason IS 'Human-readable reason for this snapshot (e.g., "Backup before AUTO sync #5")';

-- =====================================================
-- 4. UPDATED_AT TRIGGER FUNCTION
-- =====================================================

CREATE OR REPLACE FUNCTION translations.update_sync_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers to history and details
CREATE TRIGGER trg_sync_history_updated_at
    BEFORE UPDATE ON translations.i18n_sync_history
    FOR EACH ROW EXECUTE FUNCTION translations.update_sync_updated_at();

CREATE TRIGGER trg_sync_details_updated_at
    BEFORE UPDATE ON translations.i18n_sync_details
    FOR EACH ROW EXECUTE FUNCTION translations.update_sync_updated_at();

-- =====================================================
-- 5. CONSTRAINTS AND RELATIONSHIPS
-- =====================================================

-- Ensure at least one sync detail per sync operation
-- (This is checked at application level, not database level)

-- Ensure only one snapshot of each type per sync
ALTER TABLE translations.i18n_sync_snapshots
ADD CONSTRAINT uq_snapshot_type_per_sync
UNIQUE (sync_id, snapshot_type);

-- =====================================================
-- 6. VERIFICATION QUERIES
-- =====================================================

-- Show recent syncs with status summary
-- SELECT
--     sync_id,
--     sync_mode,
--     sync_status,
--     keys_added + keys_updated + keys_deleted as total_changes,
--     keys_conflicted,
--     created_at
-- FROM translations.i18n_sync_history
-- ORDER BY created_at DESC
-- LIMIT 20;

-- Show pending resolutions that need admin action
-- SELECT
--     h.sync_id,
--     COUNT(*) as pending_count,
--     STRING_AGG(DISTINCT d.conflict_reason, ', ') as conflict_reasons
-- FROM translations.i18n_sync_history h
-- JOIN translations.i18n_sync_details d ON h.sync_id = d.sync_id
-- WHERE d.resolution_status = 'PENDING' AND h.sync_status = 'PENDING'
-- GROUP BY h.sync_id;

COMMIT;

-- =====================================================
-- END MIGRATION 077
-- =====================================================
