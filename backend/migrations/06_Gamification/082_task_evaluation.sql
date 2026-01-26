-- ============================================================================
-- Migration: 082_task_evaluation.sql
-- Version: 1.0.0
-- Description: Task Evaluation System (AI Auto-Grading, Rubrics, Feedback)
-- Author: LernsystemX Migration System
-- Date: 2026-01-26
-- Phase: 4 (System Features - Tutor Task Evaluation)
-- ============================================================================

-- ============================================================================
-- TABLE: support_systems.task_submissions
-- Description: Student submissions for tasks/exercises
-- ============================================================================

CREATE TABLE IF NOT EXISTS support_systems.task_submissions (
    submission_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    method_id UUID NOT NULL REFERENCES learning_methods.learning_method_instances(method_id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,

    -- Submission content
    student_answer JSONB NOT NULL,
    submission_format VARCHAR(50),  -- text, code, file, drawing, etc.
    attempt_number INTEGER DEFAULT 1,

    -- Metadata
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    time_spent_seconds INTEGER,

    -- Constraints
    UNIQUE(method_id, student_id, attempt_number)
);

CREATE INDEX IF NOT EXISTS idx_task_submissions_method ON support_systems.task_submissions(method_id);
CREATE INDEX IF NOT EXISTS idx_task_submissions_student ON support_systems.task_submissions(student_id);
CREATE INDEX IF NOT EXISTS idx_task_submissions_submitted ON support_systems.task_submissions(submitted_at DESC);

COMMENT ON TABLE support_systems.task_submissions IS 'Student task/exercise submissions';

-- ============================================================================
-- TABLE: support_systems.task_evaluations
-- Description: AI evaluations of student submissions
-- ============================================================================

CREATE TABLE IF NOT EXISTS support_systems.task_evaluations (
    evaluation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    submission_id UUID NOT NULL REFERENCES support_systems.task_submissions(submission_id) ON DELETE CASCADE,

    -- Evaluation results
    score DECIMAL(5,2) NOT NULL,  -- 0.0-100.0
    max_score DECIMAL(5,2) DEFAULT 100.0,
    percentage DECIMAL(5,2),  -- score / max_score * 100

    -- Pass/Fail
    is_passing BOOLEAN DEFAULT FALSE,
    passing_threshold DECIMAL(5,2) DEFAULT 70.0,

    -- Evaluation details
    rubric_id UUID REFERENCES support_systems.grading_rubrics(rubric_id),
    evaluation_method VARCHAR(50),  -- automated, hybrid, manual
    ai_model VARCHAR(100),
    evaluation_confidence DECIMAL(3,2),  -- 0.0-1.0

    -- Summary
    summary_feedback TEXT,
    evaluation_completed_at TIMESTAMPTZ,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_task_evaluations_submission ON support_systems.task_evaluations(submission_id);
CREATE INDEX IF NOT EXISTS idx_task_evaluations_score ON support_systems.task_evaluations(score DESC);
CREATE INDEX IF NOT EXISTS idx_task_evaluations_passing ON support_systems.task_evaluations(is_passing);
CREATE INDEX IF NOT EXISTS idx_task_evaluations_created ON support_systems.task_evaluations(created_at DESC);

COMMENT ON TABLE support_systems.task_evaluations IS 'AI evaluations of student task submissions';
COMMENT ON COLUMN support_systems.task_evaluations.evaluation_confidence IS 'How confident is AI in this evaluation (0.0-1.0)?';

-- ============================================================================
-- TABLE: support_systems.grading_rubrics
-- Description: Rubrics used for evaluation (scoring criteria)
-- ============================================================================

CREATE TABLE IF NOT EXISTS support_systems.grading_rubrics (
    rubric_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    method_id UUID REFERENCES learning_methods.learning_method_instances(method_id) ON DELETE CASCADE,

    -- Rubric metadata
    name VARCHAR(100) NOT NULL,
    description TEXT,
    total_points DECIMAL(5,2) NOT NULL,

    -- Evaluation type
    evaluation_type VARCHAR(50) DEFAULT 'points',  -- points, percentage, rubric_levels

    -- Criteria list (JSONB format)
    -- Example: {
    --   "criteria": [
    --     {"name": "Correctness", "points": 40, "description": "..."},
    --     {"name": "Clarity", "points": 30, "description": "..."},
    --     {"name": "Completeness", "points": 30, "description": "..."}
    --   ]
    -- }
    criteria JSONB DEFAULT '{"criteria": []}',

    -- Evaluation prompt
    evaluation_prompt_id UUID REFERENCES ai_pipeline.prompts(prompt_id),

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_grading_rubrics_method ON support_systems.grading_rubrics(method_id);

COMMENT ON TABLE support_systems.grading_rubrics IS 'Grading rubrics with criteria for task evaluation';
COMMENT ON COLUMN support_systems.grading_rubrics.criteria IS 'JSONB array of criteria with names, points, descriptions';

-- ============================================================================
-- TABLE: support_systems.evaluation_feedback
-- Description: Detailed feedback for each rubric criterion
-- ============================================================================

CREATE TABLE IF NOT EXISTS support_systems.evaluation_feedback (
    feedback_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    evaluation_id UUID NOT NULL REFERENCES support_systems.task_evaluations(evaluation_id) ON DELETE CASCADE,

    -- Criterion being evaluated
    criterion_name VARCHAR(100) NOT NULL,
    criterion_max_points DECIMAL(5,2),

    -- Feedback
    points_earned DECIMAL(5,2) NOT NULL,
    feedback_text TEXT NOT NULL,
    feedback_type VARCHAR(50),  -- positive, constructive, informational

    -- Evidence from submission
    evidence TEXT,  -- What in the student's work led to this feedback?

    -- Improvement suggestions
    suggestion_for_improvement TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_evaluation_feedback_evaluation ON support_systems.evaluation_feedback(evaluation_id);
CREATE INDEX IF NOT EXISTS idx_evaluation_feedback_criterion ON support_systems.evaluation_feedback(criterion_name);

COMMENT ON TABLE support_systems.evaluation_feedback IS 'Detailed per-criterion feedback from evaluation';

-- ============================================================================
-- TABLE: support_systems.evaluation_appeals
-- Description: Student appeals against evaluation scores
-- ============================================================================

CREATE TABLE IF NOT EXISTS support_systems.evaluation_appeals (
    appeal_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    evaluation_id UUID NOT NULL REFERENCES support_systems.task_evaluations(evaluation_id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,

    -- Appeal content
    appeal_reason TEXT NOT NULL,
    appeal_evidence TEXT,

    -- Resolution
    status VARCHAR(50) DEFAULT 'pending',  -- pending, reviewed, approved, rejected
    reviewer_id UUID REFERENCES core.users(user_id) ON DELETE SET NULL,
    reviewer_decision TEXT,
    new_score DECIMAL(5,2),  -- Updated score if approved

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    reviewed_at TIMESTAMPTZ,

    -- Constraints
    CONSTRAINT chk_appeal_status CHECK (status IN ('pending', 'reviewed', 'approved', 'rejected'))
);

CREATE INDEX IF NOT EXISTS idx_evaluation_appeals_student ON support_systems.evaluation_appeals(student_id);
CREATE INDEX IF NOT EXISTS idx_evaluation_appeals_status ON support_systems.evaluation_appeals(status);
CREATE INDEX IF NOT EXISTS idx_evaluation_appeals_created ON support_systems.evaluation_appeals(created_at DESC);

COMMENT ON TABLE support_systems.evaluation_appeals IS 'Student appeals against evaluation decisions';

-- ============================================================================
-- Function: calculate_task_score()
-- Description: Calculate final score for a task based on rubric
-- ============================================================================

CREATE OR REPLACE FUNCTION calculate_task_score(p_evaluation_id UUID)
RETURNS DECIMAL AS $$
DECLARE
    v_total_score DECIMAL := 0;
BEGIN
    SELECT SUM(points_earned) INTO v_total_score
    FROM support_systems.evaluation_feedback
    WHERE evaluation_id = p_evaluation_id;

    RETURN COALESCE(v_total_score, 0);
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- End of Migration: 082_task_evaluation.sql
-- ============================================================================
