-- ============================================================================
-- Migration: 014_exam_results.sql
-- Version: 1.0.0
-- Description: Database migration
-- Author: LernsystemX Migration System
-- Date: 2026-01-02
-- ============================================================================

CREATE TABLE IF NOT EXISTS assessments.exam_attempts (
    attempt_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    exam_id UUID REFERENCES assessments.exams(exam_id) ON DELETE CASCADE,
    user_id UUID REFERENCES core.users(user_id) ON DELETE CASCADE,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    submitted_at TIMESTAMPTZ,
    time_spent_seconds INTEGER,
    status VARCHAR(20) DEFAULT 'in_progress',
    ip_address INET,
    user_agent TEXT,
    CONSTRAINT chk_attempt_status CHECK (status IN ('in_progress', 'submitted', 'graded', 'cancelled', 'expired'))
);

CREATE INDEX IF NOT EXISTS idx_exam_attempts_exam ON assessments.exam_attempts(exam_id);
CREATE INDEX IF NOT EXISTS idx_exam_attempts_user ON assessments.exam_attempts(user_id, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_exam_attempts_status ON assessments.exam_attempts(status);

COMMENT ON TABLE assessments.exam_attempts IS 'Individual exam attempts by users';

-- ============================================================================
-- TABLE: exam_results
-- Description: Graded exam results
-- ============================================================================
CREATE TABLE IF NOT EXISTS assessments.exam_results (
    result_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    attempt_id UUID REFERENCES assessments.exam_attempts(attempt_id) ON DELETE CASCADE UNIQUE,
    exam_id UUID REFERENCES assessments.exams(exam_id) ON DELETE CASCADE,
    user_id UUID REFERENCES core.users(user_id) ON DELETE CASCADE,
    score DECIMAL(5,2) NOT NULL,
    total_points DECIMAL(10,2) NOT NULL,
    percentage DECIMAL(5,2) NOT NULL,
    passed BOOLEAN NOT NULL,
    details JSONB,
    graded_at TIMESTAMPTZ DEFAULT NOW(),
    graded_by UUID REFERENCES core.users(user_id) ON DELETE SET NULL,
    certificate_issued BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_exam_results_attempt ON assessments.exam_results(attempt_id);
CREATE INDEX IF NOT EXISTS idx_exam_results_exam ON assessments.exam_results(exam_id);
CREATE INDEX IF NOT EXISTS idx_exam_results_user ON assessments.exam_results(user_id, graded_at DESC);
CREATE INDEX IF NOT EXISTS idx_exam_results_passed ON assessments.exam_results(passed);
CREATE INDEX IF NOT EXISTS idx_exam_results_score ON assessments.exam_results(percentage DESC);

COMMENT ON TABLE assessments.exam_results IS 'Graded exam results with scores and pass/fail status';

-- ============================================================================
-- TABLE: exam_answers
-- Description: User answers to exam questions
-- ============================================================================
CREATE TABLE IF NOT EXISTS assessments.exam_answers (
    answer_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    attempt_id UUID REFERENCES assessments.exam_attempts(attempt_id) ON DELETE CASCADE,
    question_id UUID REFERENCES assessments.exam_questions(question_id) ON DELETE CASCADE,
    user_answer JSONB,
    is_correct BOOLEAN,
    points_earned DECIMAL(5,2),
    time_spent_seconds INTEGER,
    flagged_for_review BOOLEAN DEFAULT FALSE,
    answered_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (attempt_id, question_id)
);

CREATE INDEX IF NOT EXISTS idx_exam_answers_attempt ON assessments.exam_answers(attempt_id);
CREATE INDEX IF NOT EXISTS idx_exam_answers_question ON assessments.exam_answers(question_id);
CREATE INDEX IF NOT EXISTS idx_exam_answers_correct ON assessments.exam_answers(is_correct);

COMMENT ON TABLE assessments.exam_answers IS 'User answers to individual exam questions';

-- ============================================================================
-- Exam Trainer extensions (added 2026-03-15)
-- ============================================================================

-- Additional columns for timed exam attempts
ALTER TABLE assessments.exam_attempts
  ADD COLUMN IF NOT EXISTS time_limit_minutes INTEGER,
  ADD COLUMN IF NOT EXISTS completed_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS score NUMERIC,
  ADD COLUMN IF NOT EXISTS total_points NUMERIC,
  ADD COLUMN IF NOT EXISTS passed BOOLEAN,
  ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();

-- Extend status constraint to include 'completed'
ALTER TABLE assessments.exam_attempts
  DROP CONSTRAINT IF EXISTS chk_attempt_status;
ALTER TABLE assessments.exam_attempts
  ADD CONSTRAINT chk_attempt_status CHECK (
    status IN ('in_progress', 'submitted', 'graded', 'cancelled', 'expired', 'completed')
  );

-- ============================================================================
-- End of Migration: 014_exam_results.sql
-- ============================================================================
