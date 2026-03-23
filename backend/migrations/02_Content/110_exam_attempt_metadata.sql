-- ============================================================================
-- Migration: 110_exam_attempt_metadata.sql
-- Description: Add metadata JSONB column to exam_attempts for practice state
-- ============================================================================

ALTER TABLE assessments.exam_attempts
  ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}';

COMMENT ON COLUMN assessments.exam_attempts.metadata IS
  'JSONB: practice_state, config, adaptive state for practice mode sessions';

-- ============================================================================
-- End of Migration: 110_exam_attempt_metadata.sql
-- ============================================================================
