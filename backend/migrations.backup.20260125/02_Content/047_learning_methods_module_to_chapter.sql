-- ============================================================================
-- Migration: 047_learning_methods_module_to_chapter.sql
-- Version: 1.0.0
-- Description: Database migration
-- Author: LernsystemX Migration System
-- Date: 2026-01-02
-- ============================================================================

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_schema = 'learning_methods' AND table_name = 'learning_method_instances' AND column_name = 'module_id') THEN
        ALTER TABLE learning_methods.learning_method_instances RENAME COLUMN module_id TO chapter_id;
        RAISE NOTICE 'Renamed column in learning_method_instances: module_id → chapter_id';
    ELSE
        RAISE NOTICE 'Column chapter_id already exists in learning_method_instances - no migration needed';
    END IF;
END $$;

-- Update indexes
DROP INDEX IF EXISTS learning_methods.idx_lm_instances_module;
DROP INDEX IF EXISTS learning_methods.idx_lm_instances_order;

-- Note: idx_lm_instances_chapter and idx_lm_instances_order are already created in 011_learning_methods.sql

-- ============================================================================
-- End of Migration: 054_learning_methods_module_to_chapter.sql
-- ============================================================================
