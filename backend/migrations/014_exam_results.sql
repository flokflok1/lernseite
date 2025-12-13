-- ============================================================================
-- Migration: 014_exam_results.sql
-- Description: Exam attempts and results
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-01-17
-- ============================================================================

-- ============================================================================
-- TABLE: exam_attempts
-- Description: User attempts at exams
-- ============================================================================
CREATE TABLE IF NOT EXISTS exam_attempts (
    attempt_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    exam_id UUID REFERENCES exams(exam_id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    submitted_at TIMESTAMPTZ,
    time_spent_seconds INTEGER,
    status VARCHAR(20) DEFAULT 'in_progress',
    ip_address INET,
    user_agent TEXT,
    CONSTRAINT chk_attempt_status CHECK (status IN ('in_progress', 'submitted', 'graded', 'cancelled', 'expired'))
);

CREATE INDEX IF NOT EXISTS idx_exam_attempts_exam ON exam_attempts(exam_id);
CREATE INDEX IF NOT EXISTS idx_exam_attempts_user ON exam_attempts(user_id, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_exam_attempts_status ON exam_attempts(status);

COMMENT ON TABLE exam_attempts IS 'Individual exam attempts by users';

-- ============================================================================
-- TABLE: exam_results
-- Description: Graded exam results
-- ============================================================================
CREATE TABLE IF NOT EXISTS exam_results (
    result_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    attempt_id UUID REFERENCES exam_attempts(attempt_id) ON DELETE CASCADE UNIQUE,
    exam_id UUID REFERENCES exams(exam_id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    score DECIMAL(5,2) NOT NULL,
    total_points DECIMAL(10,2) NOT NULL,
    percentage DECIMAL(5,2) NOT NULL,
    passed BOOLEAN NOT NULL,
    details JSONB,
    graded_at TIMESTAMPTZ DEFAULT NOW(),
    graded_by UUID REFERENCES users(user_id) ON DELETE SET NULL,
    certificate_issued BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_exam_results_attempt ON exam_results(attempt_id);
CREATE INDEX IF NOT EXISTS idx_exam_results_exam ON exam_results(exam_id);
CREATE INDEX IF NOT EXISTS idx_exam_results_user ON exam_results(user_id, graded_at DESC);
CREATE INDEX IF NOT EXISTS idx_exam_results_passed ON exam_results(passed);
CREATE INDEX IF NOT EXISTS idx_exam_results_score ON exam_results(percentage DESC);

COMMENT ON TABLE exam_results IS 'Graded exam results with scores and pass/fail status';

-- ============================================================================
-- TABLE: exam_answers
-- Description: User answers to exam questions
-- ============================================================================
CREATE TABLE IF NOT EXISTS exam_answers (
    answer_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    attempt_id UUID REFERENCES exam_attempts(attempt_id) ON DELETE CASCADE,
    question_id UUID REFERENCES exam_questions(question_id) ON DELETE CASCADE,
    user_answer JSONB,
    is_correct BOOLEAN,
    points_earned DECIMAL(5,2),
    time_spent_seconds INTEGER,
    flagged_for_review BOOLEAN DEFAULT FALSE,
    answered_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (attempt_id, question_id)
);

CREATE INDEX IF NOT EXISTS idx_exam_answers_attempt ON exam_answers(attempt_id);
CREATE INDEX IF NOT EXISTS idx_exam_answers_question ON exam_answers(question_id);
CREATE INDEX IF NOT EXISTS idx_exam_answers_correct ON exam_answers(is_correct);

COMMENT ON TABLE exam_answers IS 'User answers to individual exam questions';

-- ============================================================================
-- End of Migration: 014_exam_results.sql
-- ============================================================================
