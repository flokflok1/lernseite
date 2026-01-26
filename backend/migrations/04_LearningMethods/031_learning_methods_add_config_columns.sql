-- ============================================================================
-- Migration: 031_learning_methods_add_config_columns.sql
-- Version: 1.0.0
-- Description: Add configuration columns to learning_method_types (ui_schema, prompt_template, agent_support)
-- Author: LernsystemX Migration System
-- Date: 2026-01-26
-- Phase: 2 (Content Layer - Configuration Enhancement)
-- ============================================================================

-- ============================================================================
-- ALTER TABLE: Add new configuration columns
-- This migration enables 100% DB-driven Learning Methods (no hardcoded Python)
-- ============================================================================

ALTER TABLE learning_methods.learning_method_types
ADD COLUMN IF NOT EXISTS prompt_template VARCHAR(255) COMMENT 'KI Prompt Template key (e.g., deep_explanation, flashcards)',
ADD COLUMN IF NOT EXISTS default_config JSONB DEFAULT '{}' COMMENT 'Default LM-specific configuration',
ADD COLUMN IF NOT EXISTS agent_support JSONB COMMENT 'Agent support configuration: {agent_can_handle, requires_fresh_ai, knowledge_domains, knowledge_cacheable, complexity_threshold}',
ADD COLUMN IF NOT EXISTS ui_schema JSONB DEFAULT '{}' COMMENT 'Dynamic form schema for frontend rendering';

-- Create index on active methods for fast lookup
CREATE INDEX IF NOT EXISTS idx_lm_types_ui_schema ON learning_methods.learning_method_types USING GIN(ui_schema);
CREATE INDEX IF NOT EXISTS idx_lm_types_agent_support ON learning_methods.learning_method_types USING GIN(agent_support);

-- ============================================================================
-- Verification
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '✓ Successfully added configuration columns to learning_method_types';
    RAISE NOTICE '  New columns: prompt_template, default_config, agent_support, ui_schema';
    RAISE NOTICE '  Learning Methods can now be 100% DB-driven!';
END $$;

-- ============================================================================
-- End of Migration: 031_learning_methods_add_config_columns.sql
-- ============================================================================
