-- ============================================================================
-- Migration: 047 - Course-Specific Prompts (Phase C1.4)
-- ============================================================================
-- Description:
--   This migration adds support for course-specific AI prompt customization.
--   Allows administrators to override global AI prompts for specific courses.
--
-- Dependencies:
--   - 008_courses.sql (courses table)
--   - 001_core_users_roles.sql (users table)
--   - 019_ai_prompts.sql (global AI prompts)
--
-- Phase: C1.4 - Prompt-System für Kurs/Modul/Prüfung
-- Date: 2025-01-23
-- ============================================================================

-- ============================================================================
-- 1. Create course_prompts table
-- ============================================================================

CREATE TABLE IF NOT EXISTS courses.course_prompts (
    -- Primary key
    course_prompt_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Course reference (CASCADE delete if course is deleted)
    course_id UUID NOT NULL REFERENCES courses.courses(course_id) ON DELETE CASCADE,

    -- Scope: Which operation does this prompt apply to?
    -- Values: 'course_generation', 'chapter_generation', 'exam_generation'
    scope TEXT NOT NULL CHECK (scope IN (
        'course_generation',
        'chapter_generation',
        'exam_generation',
        'lesson_generation',
        'quiz_generation'
    )),

    -- Optional language override (e.g., 'de', 'en', 'fr')
    -- If NULL, uses course default language
    language TEXT,

    -- System prompt (defines AI role and behavior)
    prompt_system TEXT,

    -- User prompt template (with placeholders like {{course_title}}, {{topic}})
    prompt_user_template TEXT,

    -- Additional metadata (JSONB for flexibility)
    -- Example: {"temperature": 0.7, "max_tokens": 2000, "tags": ["beginner"]}
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Active flag (allows disabling without deleting)
    is_active BOOLEAN DEFAULT TRUE NOT NULL,

    -- Audit fields
    created_by UUID REFERENCES core.users(user_id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,

    -- Unique constraint: One prompt per (course, scope, language)
    -- Allows multiple prompts for same course but different scopes/languages
    CONSTRAINT uq_course_prompts_course_scope_lang UNIQUE (course_id, scope, language)
);

-- ============================================================================
-- 2. Create indexes for performance
-- ============================================================================

-- Index for fast lookup by course and scope
CREATE INDEX IF NOT EXISTS idx_course_prompts_course_scope
    ON courses.course_prompts (course_id, scope)
    WHERE is_active = TRUE;

-- Index for fast lookup by scope (to find all courses with custom prompts for a specific scope)
CREATE INDEX IF NOT EXISTS idx_course_prompts_scope
    ON courses.course_prompts (scope)
    WHERE is_active = TRUE;

-- Index for audit queries (created_by, created_at)
CREATE INDEX IF NOT EXISTS idx_course_prompts_audit
    ON courses.course_prompts (created_by, created_at DESC);

-- ============================================================================
-- 3. Create trigger for updated_at auto-update
-- ============================================================================

CREATE OR REPLACE FUNCTION update_course_prompts_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_course_prompts_updated_at
    BEFORE UPDATE ON courses.course_prompts
    FOR EACH ROW
    EXECUTE FUNCTION update_course_prompts_updated_at();

-- ============================================================================
-- 4. Add comments for documentation
-- ============================================================================

COMMENT ON TABLE courses.course_prompts IS
    'Course-specific AI prompt overrides (Phase C1.4). Allows customization of AI generation behavior per course.';

COMMENT ON COLUMN courses.course_prompts.course_prompt_id IS
    'Primary key (UUID)';

COMMENT ON COLUMN courses.course_prompts.course_id IS
    'Foreign key to courses table. Cascade deletes when course is deleted.';

COMMENT ON COLUMN courses.course_prompts.scope IS
    'Scope of this prompt: course_generation, chapter_generation, exam_generation, lesson_generation, quiz_generation';

COMMENT ON COLUMN courses.course_prompts.language IS
    'Optional language override (e.g., de, en, fr). If NULL, uses course default language.';

COMMENT ON COLUMN courses.course_prompts.prompt_system IS
    'System prompt that defines AI role and behavior (e.g., "You are an expert teacher...")';

COMMENT ON COLUMN courses.course_prompts.prompt_user_template IS
    'User prompt template with placeholders (e.g., "Generate a module about {{topic}} for {{course_title}}")';

COMMENT ON COLUMN courses.course_prompts.metadata IS
    'Additional metadata in JSONB format (temperature, max_tokens, tags, etc.)';

COMMENT ON COLUMN courses.course_prompts.is_active IS
    'Active flag. Set to FALSE to disable without deleting.';

COMMENT ON COLUMN courses.course_prompts.created_by IS
    'User who created this prompt override';

COMMENT ON COLUMN courses.course_prompts.created_at IS
    'Timestamp when this prompt was created';

COMMENT ON COLUMN courses.course_prompts.updated_at IS
    'Timestamp when this prompt was last updated (auto-updated by trigger)';

-- ============================================================================
-- 5. Grant permissions (assuming standard role setup)
-- ============================================================================

-- Admins can do everything
-- GRANT SELECT, INSERT, UPDATE, DELETE ON courses.course_prompts TO lsx_admin;  -- Role optional

-- Support/Moderators can view
-- GRANT SELECT ON courses.course_prompts TO lsx_support;  -- Role optional

-- Normal users cannot access this table directly (only via API)
-- REVOKE ALL ON courses.course_prompts FROM PUBLIC;  -- Role optional

-- ============================================================================
-- 6. Rollback instructions (for reference)
-- ============================================================================

-- To rollback this migration:
-- DROP TRIGGER IF EXISTS trigger_course_prompts_updated_at ON courses.course_prompts ;
-- DROP FUNCTION IF EXISTS update_course_prompts_updated_at();
-- DROP TABLE IF EXISTS course_prompts CASCADE;

-- ============================================================================
-- End of Migration 047
-- ============================================================================
