-- ============================================================
-- Migration 110: Spaced Repetition scheduling table
-- Schema: learning_methods
-- Purpose: SM-2 based review scheduling for all LM types
-- ============================================================

-- Spaced Repetition scheduling for all learning method instances
CREATE TABLE IF NOT EXISTS learning_methods.review_schedule (
    schedule_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,
    method_id UUID NOT NULL REFERENCES learning_methods.learning_method_instances(method_id) ON DELETE CASCADE,

    -- SM-2 algorithm state
    easiness_factor FLOAT NOT NULL DEFAULT 2.5,       -- EF >= 1.3
    interval_days INTEGER NOT NULL DEFAULT 1,          -- Current interval
    repetition_number INTEGER NOT NULL DEFAULT 0,      -- Successful reps in a row
    next_review_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), -- When to review

    -- Performance tracking
    mastery_score FLOAT NOT NULL DEFAULT 0.0,          -- 0-100
    current_streak INTEGER NOT NULL DEFAULT 0,
    total_reviews INTEGER NOT NULL DEFAULT 0,
    last_quality INTEGER,                              -- Last response quality (0-5)
    last_reviewed_at TIMESTAMPTZ,

    -- Adaptive difficulty
    difficulty_level VARCHAR(20) NOT NULL DEFAULT 'medium',  -- easy/medium/hard
    confidence FLOAT NOT NULL DEFAULT 0.5,             -- 0.0-1.0

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_review_user_method UNIQUE (user_id, method_id),
    CONSTRAINT chk_easiness CHECK (easiness_factor >= 1.3),
    CONSTRAINT chk_mastery CHECK (mastery_score >= 0 AND mastery_score <= 100),
    CONSTRAINT chk_confidence CHECK (confidence >= 0 AND confidence <= 1),
    CONSTRAINT chk_difficulty CHECK (difficulty_level IN ('easy', 'medium', 'hard'))
);

-- Index: find due reviews for a user (composite on user + due date)
CREATE INDEX IF NOT EXISTS idx_review_schedule_user_due
    ON learning_methods.review_schedule (user_id, next_review_at);

-- Index: look up all schedules for a given learning method instance
CREATE INDEX IF NOT EXISTS idx_review_schedule_method
    ON learning_methods.review_schedule (method_id);

-- Curriculum-level aggregation view for quick knowledge map
-- Links review_schedule → learning_method_instances → chapters → courses → curriculum_positions
CREATE OR REPLACE VIEW learning_methods.curriculum_mastery AS
SELECT
    rs.user_id,
    cp.id AS position_id,
    cs.section_code,
    cp.position_number AS position_code,
    cp.display_name AS position_title,
    AVG(rs.mastery_score) AS avg_mastery,
    MIN(rs.mastery_score) AS min_mastery,
    COUNT(*) AS lm_count,
    COUNT(*) FILTER (WHERE rs.mastery_score >= 80) AS mastered_count,
    MIN(rs.next_review_at) AS earliest_review
FROM learning_methods.review_schedule rs
JOIN learning_methods.learning_method_instances lmi
    ON lmi.method_id = rs.method_id
JOIN courses.chapters ch
    ON ch.chapter_id = lmi.chapter_id
-- Link chapter back to curriculum position via course metadata
JOIN courses.courses c
    ON c.course_id = ch.course_id
    AND c.detected_exam_type IS NOT NULL
LEFT JOIN assessments.curriculum_positions cp
    ON cp.id = (ch.ai_metadata->>'curriculum_position_id')::INTEGER
LEFT JOIN assessments.curriculum_sections cs
    ON cs.id = cp.section_id
WHERE cp.id IS NOT NULL
GROUP BY rs.user_id, cp.id, cs.section_code, cp.position_number, cp.display_name;
