-- ============================================================================
-- Migration: 053_rename_modules_to_chapters.sql
-- Description: Renames modules table to chapters (modules → chapters refactoring)
-- Version: 2.1.0
-- Author: LernsystemX Migration System
-- Date: 2025-11-28
-- ============================================================================

-- Check if 'modules' table exists and 'chapters' doesn't
-- This migration safely renames the table if needed

-- ============================================================================
-- STEP 1: Rename the main table
-- ============================================================================
DO $$
BEGIN
    -- Check if modules table exists and chapters doesn't
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'modules')
       AND NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'chapters') THEN

        -- Rename the table
        ALTER TABLE modules RENAME TO chapters;
        RAISE NOTICE 'Renamed table: modules → chapters';

        -- Rename primary key column
        ALTER TABLE chapters RENAME COLUMN module_id TO chapter_id;
        RAISE NOTICE 'Renamed column: module_id → chapter_id';

    ELSIF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'chapters') THEN
        RAISE NOTICE 'Table chapters already exists - no migration needed';
    ELSE
        -- Neither table exists - create fresh
        RAISE NOTICE 'Neither modules nor chapters table exists - will be created by 009_chapters.sql';
    END IF;
END $$;

-- ============================================================================
-- STEP 2: Rename related tables if they exist
-- ============================================================================

-- module_theory → chapter_theory
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'module_theory')
       AND NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'chapter_theory') THEN
        ALTER TABLE module_theory RENAME TO chapter_theory;
        ALTER TABLE chapter_theory RENAME COLUMN module_id TO chapter_id;
        RAISE NOTICE 'Renamed table: module_theory → chapter_theory';
    END IF;
END $$;

-- module_resources → chapter_resources
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'module_resources')
       AND NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'chapter_resources') THEN
        ALTER TABLE module_resources RENAME TO chapter_resources;
        ALTER TABLE chapter_resources RENAME COLUMN module_id TO chapter_id;
        RAISE NOTICE 'Renamed table: module_resources → chapter_resources';
    END IF;
END $$;

-- ============================================================================
-- STEP 3: Update foreign key columns in other tables
-- ============================================================================

-- lessons table: module_id → chapter_id
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'lessons' AND column_name = 'module_id') THEN
        ALTER TABLE lessons RENAME COLUMN module_id TO chapter_id;
        RAISE NOTICE 'Renamed column in lessons: module_id → chapter_id';
    END IF;
END $$;

-- learning_method_instances table: module_id → chapter_id
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'learning_method_instances' AND column_name = 'module_id') THEN
        ALTER TABLE learning_method_instances RENAME COLUMN module_id TO chapter_id;
        RAISE NOTICE 'Renamed column in learning_method_instances: module_id → chapter_id';
    END IF;
END $$;

-- module_progress → chapter_progress
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'module_progress')
       AND NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'chapter_progress') THEN
        ALTER TABLE module_progress RENAME TO chapter_progress;
        RAISE NOTICE 'Renamed table: module_progress → chapter_progress';
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'chapter_progress' AND column_name = 'module_id') THEN
        ALTER TABLE chapter_progress RENAME COLUMN module_id TO chapter_id;
        RAISE NOTICE 'Renamed column in chapter_progress: module_id → chapter_id';
    END IF;
END $$;

-- user_progress table: current_module_id → current_chapter_id
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'user_progress' AND column_name = 'current_module_id') THEN
        ALTER TABLE user_progress RENAME COLUMN current_module_id TO current_chapter_id;
        RAISE NOTICE 'Renamed column in user_progress: current_module_id → current_chapter_id';
    END IF;
END $$;

-- exam_results table: module_id → chapter_id
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'exam_results' AND column_name = 'module_id') THEN
        ALTER TABLE exam_results RENAME COLUMN module_id TO chapter_id;
        RAISE NOTICE 'Renamed column in exam_results: module_id → chapter_id';
    END IF;
END $$;

-- ============================================================================
-- STEP 4: Update indexes (drop old, create new)
-- ============================================================================
DO $$
BEGIN
    -- Drop old indexes if they exist
    DROP INDEX IF EXISTS idx_modules_course;
    DROP INDEX IF EXISTS idx_modules_order;
    DROP INDEX IF EXISTS idx_modules_published;
    DROP INDEX IF EXISTS idx_module_theory_module;
    DROP INDEX IF EXISTS idx_module_resources_module;

    RAISE NOTICE 'Dropped old module indexes';
END $$;

-- Create new indexes if table exists
CREATE INDEX IF NOT EXISTS idx_chapters_course ON chapters(course_id);
CREATE INDEX IF NOT EXISTS idx_chapters_order ON chapters(course_id, order_index);
CREATE INDEX IF NOT EXISTS idx_chapters_published ON chapters(published) WHERE published = TRUE;

-- Update lessons foreign key index
DROP INDEX IF EXISTS idx_lessons_module;
CREATE INDEX IF NOT EXISTS idx_lessons_chapter ON lessons(chapter_id);

-- ============================================================================
-- STEP 5: Verify migration
-- ============================================================================
DO $$
DECLARE
    chapters_exists BOOLEAN;
    modules_exists BOOLEAN;
BEGIN
    SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'chapters') INTO chapters_exists;
    SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'modules') INTO modules_exists;

    IF chapters_exists AND NOT modules_exists THEN
        RAISE NOTICE '✓ Migration successful: chapters table exists, modules table removed';
    ELSIF chapters_exists AND modules_exists THEN
        RAISE WARNING '⚠ Both chapters and modules tables exist - manual cleanup may be needed';
    ELSE
        RAISE WARNING '⚠ Unexpected state: chapters=%s, modules=%s', chapters_exists, modules_exists;
    END IF;
END $$;

-- ============================================================================
-- End of Migration: 053_rename_modules_to_chapters.sql
-- ============================================================================
