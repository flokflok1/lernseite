-- ============================================================================
-- Migration: 048_ai_authoring_studio_part3.sql
-- Description: AI Editor (AI Authoring) - Part 3: UX Extensions
--              Tables: authoring_milestones, authoring_changes, authoring_finalization
--              Features: Gamification, Version History, Finalization Workflow
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-01-16
-- ============================================================================
-- Note: Split from original 048_ai_authoring_studio.sql (857 lines)
--       Part 3 of 3: Psychological UX + finalization workflow
-- ============================================================================

-- ============================================================================
-- TABLE: authoring_milestones (Psychologische UX Extension)
-- Description: Celebrate user achievements (Gamification)
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_pipeline.authoring_milestones (
    milestone_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES ai_pipeline.ai_authoring_sessions(session_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,

    -- Milestone details
    milestone_type VARCHAR(50) NOT NULL
        CHECK (milestone_type IN ('first_upload', 'first_analysis', 'first_generation', 'first_refinement', 'course_completed', 'multi_file_master', 'exam_pattern_expert')),

    -- Celebration
    achievement_title VARCHAR(255) NOT NULL,
    celebration_message TEXT NOT NULL,
    badge_earned VARCHAR(100),

    -- Stats
    achievement_data JSONB DEFAULT '{}',  -- {"chapters_created": 12, "lessons_created": 47}

    achieved_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_authoring_milestones_session ON ai_pipeline.authoring_milestones(session_id);
CREATE INDEX IF NOT EXISTS idx_authoring_milestones_user ON ai_pipeline.authoring_milestones(user_id);
CREATE INDEX IF NOT EXISTS idx_authoring_milestones_type ON ai_pipeline.authoring_milestones(milestone_type);

COMMENT ON TABLE ai_pipeline.authoring_milestones IS 'User achievements and celebrations for motivation';
COMMENT ON COLUMN ai_pipeline.authoring_milestones.achievement_data IS 'Statistics about this achievement';

-- ============================================================================
-- ALTER EXISTING TABLES: Add new columns for enhanced functionality
-- ============================================================================

-- Extend ai_authoring_sessions for multi-file support
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'ai_authoring_sessions' AND column_name = 'target_audience') THEN
        ALTER TABLE ai_pipeline.ai_authoring_sessions
            ADD COLUMN target_audience JSONB DEFAULT '{}';
        RAISE NOTICE 'Added column ai_authoring_sessions.target_audience';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'ai_authoring_sessions' AND column_name = 'exam_integration') THEN
        ALTER TABLE ai_pipeline.ai_authoring_sessions
            ADD COLUMN exam_integration JSONB DEFAULT '{}';
        RAISE NOTICE 'Added column ai_authoring_sessions.exam_integration';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'ai_authoring_sessions' AND column_name = 'multi_file_support') THEN
        ALTER TABLE ai_pipeline.ai_authoring_sessions
            ADD COLUMN multi_file_support BOOLEAN DEFAULT false;
        RAISE NOTICE 'Added column ai_authoring_sessions.multi_file_support';
    END IF;
END $$;

COMMENT ON COLUMN ai_pipeline.ai_authoring_sessions.target_audience IS 'Target audience settings: level, background, learning goals';
COMMENT ON COLUMN ai_pipeline.ai_authoring_sessions.exam_integration IS 'Exam integration settings: exam type, years analyzed, focus areas';
COMMENT ON COLUMN ai_pipeline.ai_authoring_sessions.multi_file_support IS 'Session uses multi-file analysis (e.g., 7 years of exams)';

-- Extend ai_session_snapshots for better UX
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'ai_session_snapshots' AND column_name = 'user_friendly_description') THEN
        ALTER TABLE ai_pipeline.ai_session_snapshots
            ADD COLUMN user_friendly_description TEXT;
        RAISE NOTICE 'Added column ai_session_snapshots.user_friendly_description';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'ai_session_snapshots' AND column_name = 'visual_preview_url') THEN
        ALTER TABLE ai_pipeline.ai_session_snapshots
            ADD COLUMN visual_preview_url TEXT;
        RAISE NOTICE 'Added column ai_session_snapshots.visual_preview_url';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'ai_session_snapshots' AND column_name = 'affected_chapters') THEN
        ALTER TABLE ai_pipeline.ai_session_snapshots
            ADD COLUMN affected_chapters INT[] DEFAULT '{}';
        RAISE NOTICE 'Added column ai_session_snapshots.affected_chapters';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'ai_session_snapshots' AND column_name = 'affected_lessons') THEN
        ALTER TABLE ai_pipeline.ai_session_snapshots
            ADD COLUMN affected_lessons INT[] DEFAULT '{}';
        RAISE NOTICE 'Added column ai_session_snapshots.affected_lessons';
    END IF;
END $$;

COMMENT ON COLUMN ai_pipeline.ai_session_snapshots.user_friendly_description IS 'Human-readable snapshot description: "Kapitel 3 wurde aufgeteilt"';
COMMENT ON COLUMN ai_pipeline.ai_session_snapshots.visual_preview_url IS 'Optional visual preview for snapshot (thumbnail)';

-- ============================================================================
-- Triggers for updated_at timestamps
-- ============================================================================
DROP TRIGGER IF EXISTS update_authoring_generations_updated_at ON ai_pipeline.authoring_generations;
CREATE TRIGGER update_authoring_generations_updated_at BEFORE UPDATE ON ai_pipeline.authoring_generations
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_authoring_journey_updated_at ON ai_pipeline.authoring_user_journey;
CREATE TRIGGER update_authoring_journey_updated_at BEFORE UPDATE ON ai_pipeline.authoring_user_journey
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- EDIT MODE EXTENSIONS (2025-01-07): Support für bestehende Kurse bearbeiten
-- ============================================================================

-- Extend ai_authoring_sessions for edit mode support
DO $$
BEGIN
    -- Session Type (new_course, edit_existing, extend_existing)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'ai_authoring_sessions' AND column_name = 'session_type') THEN
        ALTER TABLE ai_pipeline.ai_authoring_sessions
            ADD COLUMN session_type VARCHAR(50) DEFAULT 'new_course'
                CHECK (session_type IN ('new_course', 'edit_existing', 'extend_existing'));
        RAISE NOTICE 'Added column ai_authoring_sessions.session_type';
    END IF;

    -- Original course data (when loading existing course)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'ai_authoring_sessions' AND column_name = 'original_course_data') THEN
        ALTER TABLE ai_pipeline.ai_authoring_sessions
            ADD COLUMN original_course_data JSONB DEFAULT '{}';
        RAISE NOTICE 'Added column ai_authoring_sessions.original_course_data';
    END IF;

    -- When was course loaded? (for conflict detection)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'ai_authoring_sessions' AND column_name = 'course_loaded_at') THEN
        ALTER TABLE ai_pipeline.ai_authoring_sessions
            ADD COLUMN course_loaded_at TIMESTAMPTZ;
        RAISE NOTICE 'Added column ai_authoring_sessions.course_loaded_at';
    END IF;

    -- Course version at load time (for optimistic locking)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'ai_authoring_sessions' AND column_name = 'course_version_at_load') THEN
        ALTER TABLE ai_pipeline.ai_authoring_sessions
            ADD COLUMN course_version_at_load INTEGER;
        RAISE NOTICE 'Added column ai_authoring_sessions.course_version_at_load';
    END IF;
END $$;

COMMENT ON COLUMN ai_pipeline.ai_authoring_sessions.session_type IS 'Session mode: new_course (from scratch), edit_existing (modify course), extend_existing (add chapters)';
COMMENT ON COLUMN ai_pipeline.ai_authoring_sessions.original_course_data IS 'Original course state when loaded (full snapshot for diff & conflict detection)';
COMMENT ON COLUMN ai_pipeline.ai_authoring_sessions.course_loaded_at IS 'Timestamp when course was loaded into session (conflict detection)';
COMMENT ON COLUMN ai_pipeline.ai_authoring_sessions.course_version_at_load IS 'Course version number at load time (optimistic locking)';

-- ============================================================================
-- TABLE: authoring_changes
-- Description: Track all changes made during authoring session (edit mode)
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_pipeline.authoring_changes (
    change_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES ai_pipeline.ai_authoring_sessions(session_id) ON DELETE CASCADE,

    -- Change type & target
    change_type VARCHAR(50) NOT NULL
        CHECK (change_type IN (
            'chapter_added', 'chapter_edited', 'chapter_deleted', 'chapter_reordered',
            'lesson_added', 'lesson_edited', 'lesson_deleted', 'lesson_reordered',
            'method_added', 'method_edited', 'method_deleted',
            'course_meta_edited', 'course_settings_edited'
        )),

    -- Entity reference
    entity_type VARCHAR(50) NOT NULL
        CHECK (entity_type IN ('course', 'chapter', 'lesson', 'method')),
    entity_id UUID,  -- NULL for new entities (not yet in DB)
    temp_id VARCHAR(100),  -- Temporary ID in draft_structure before finalization

    -- Change details
    before_data JSONB,  -- State before change (NULL for additions)
    after_data JSONB,   -- State after change (NULL for deletions)
    diff JSONB DEFAULT '{}',  -- Structured diff for UI display

    -- User context
    user_action TEXT,  -- Human-readable: "Kapitel 3 umbenannt in 'Advanced Topics'"
    changed_by UUID REFERENCES core.users(user_id) ON DELETE SET NULL,

    -- Sequencing (for undo/redo)
    sequence_number INT NOT NULL,
    is_reverted BOOLEAN DEFAULT false,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_authoring_changes_session ON ai_pipeline.authoring_changes(session_id, sequence_number);
CREATE INDEX IF NOT EXISTS idx_authoring_changes_type ON ai_pipeline.authoring_changes(change_type);
CREATE INDEX IF NOT EXISTS idx_authoring_changes_entity ON ai_pipeline.authoring_changes(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_authoring_changes_not_reverted ON ai_pipeline.authoring_changes(session_id)
    WHERE is_reverted = false;

COMMENT ON TABLE ai_pipeline.authoring_changes IS 'Detailed change tracking for edit mode (enables undo/redo, conflict detection, changelog)';
COMMENT ON COLUMN ai_pipeline.authoring_changes.before_data IS 'Complete entity state before change (NULL for additions)';
COMMENT ON COLUMN ai_pipeline.authoring_changes.after_data IS 'Complete entity state after change (NULL for deletions)';
COMMENT ON COLUMN ai_pipeline.authoring_changes.diff IS 'Structured diff for UI: {"title": {"old": "...", "new": "..."}}';
COMMENT ON COLUMN ai_pipeline.authoring_changes.sequence_number IS 'Sequential order for undo/redo functionality';

-- ============================================================================
-- TABLE: authoring_finalization
-- Description: Merge strategy, conflict resolution, and finalization results
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_pipeline.authoring_finalization (
    finalization_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES ai_pipeline.ai_authoring_sessions(session_id) ON DELETE CASCADE,

    -- Finalization strategy
    merge_strategy VARCHAR(50) NOT NULL DEFAULT 'safe_merge'
        CHECK (merge_strategy IN ('safe_merge', 'force_overwrite', 'create_new_version', 'interactive')),

    -- Pre-flight checks
    has_conflicts BOOLEAN DEFAULT false,
    conflicts JSONB DEFAULT '[]',  -- [{"type": "concurrent_edit", "entity": "chapter-123", ...}]
    conflict_resolution JSONB DEFAULT '{}',  -- {"chapter-123": "use_mine"}

    -- What was applied?
    changes_applied JSONB DEFAULT '[]',  -- [{"change_id": "...", "status": "applied"}]
    changes_skipped JSONB DEFAULT '[]',  -- [{"change_id": "...", "reason": "conflict"}]

    -- Results (IDs of affected entities)
    created_course_id UUID REFERENCES courses.courses(course_id) ON DELETE SET NULL,
    created_chapter_ids UUID[] DEFAULT '{}',
    created_lesson_ids UUID[] DEFAULT '{}',
    created_method_ids UUID[] DEFAULT '{}',
    updated_chapter_ids UUID[] DEFAULT '{}',
    updated_lesson_ids UUID[] DEFAULT '{}',
    updated_method_ids UUID[] DEFAULT '{}',
    deleted_chapter_ids UUID[] DEFAULT '{}',
    deleted_lesson_ids UUID[] DEFAULT '{}',
    deleted_method_ids UUID[] DEFAULT '{}',

    -- Statistics
    total_changes INT DEFAULT 0,
    successful_changes INT DEFAULT 0,
    failed_changes INT DEFAULT 0,

    -- Rollback support
    rollback_data JSONB,  -- Snapshot for rollback if needed
    rollback_at TIMESTAMPTZ,

    -- Status
    status VARCHAR(50) DEFAULT 'pending'
        CHECK (status IN ('pending', 'pre_check', 'in_progress', 'completed', 'failed', 'rolled_back', 'partially_completed')),
    error_message TEXT,
    warnings JSONB DEFAULT '[]',

    -- Timing
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_finalization_session ON ai_pipeline.authoring_finalization(session_id);
CREATE INDEX IF NOT EXISTS idx_finalization_course ON ai_pipeline.authoring_finalization(created_course_id);
CREATE INDEX IF NOT EXISTS idx_finalization_status ON ai_pipeline.authoring_finalization(status);
CREATE INDEX IF NOT EXISTS idx_finalization_conflicts ON ai_pipeline.authoring_finalization(has_conflicts)
    WHERE has_conflicts = true;

COMMENT ON TABLE ai_pipeline.authoring_finalization IS 'Finalization process: merge changes back to DB with conflict detection & resolution';
COMMENT ON COLUMN ai_pipeline.authoring_finalization.merge_strategy IS 'safe_merge: detect conflicts, force_overwrite: ignore conflicts, create_new_version: create course copy, interactive: ask user';
COMMENT ON COLUMN ai_pipeline.authoring_finalization.conflicts IS 'Detected conflicts: concurrent edits, deleted entities, validation errors';
COMMENT ON COLUMN ai_pipeline.authoring_finalization.conflict_resolution IS 'User decisions for each conflict: use_mine, use_theirs, merge_both';
COMMENT ON COLUMN ai_pipeline.authoring_finalization.rollback_data IS 'DB snapshot before finalization (for rollback if something fails)';

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON ai_pipeline.authoring_changes TO lernsystem;
GRANT SELECT, INSERT, UPDATE, DELETE ON ai_pipeline.authoring_finalization TO lernsystem;

-- ============================================================================
-- End of Migration: 055_ai_authoring_studio.sql
-- ============================================================================
