-- ============================================================================
-- Migration: 054_learning_methods_module_to_chapter.sql
-- Description: Renames module_id to chapter_id in learning_methods table
-- Version: 2.1.1
-- Author: LernsystemX Migration System
-- Date: 2025-11-29
-- ============================================================================

-- Rename column module_id → chapter_id in learning_methods
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_name = 'learning_methods' AND column_name = 'module_id') THEN
        ALTER TABLE learning_methods RENAME COLUMN module_id TO chapter_id;
        RAISE NOTICE 'Renamed column in learning_methods: module_id → chapter_id';
    ELSE
        RAISE NOTICE 'Column chapter_id already exists in learning_methods - no migration needed';
    END IF;
END $$;

-- Update indexes
DROP INDEX IF EXISTS idx_learning_methods_module;
DROP INDEX IF EXISTS idx_learning_methods_order;

CREATE INDEX IF NOT EXISTS idx_learning_methods_chapter ON learning_methods(chapter_id);
CREATE INDEX IF NOT EXISTS idx_learning_methods_chapter_order ON learning_methods(chapter_id, order_index);

-- ============================================================================
-- End of Migration: 054_learning_methods_module_to_chapter.sql
-- ============================================================================
