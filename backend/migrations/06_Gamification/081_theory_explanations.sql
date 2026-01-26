-- ============================================================================
-- Migration: 081_theory_explanations.sql
-- Version: 1.0.0
-- Description: Theory Sheet Explanations (AI-Generated Theory Content & Q&A)
-- Author: LernsystemX Migration System
-- Date: 2026-01-26
-- Phase: 4 (System Features - Tutor Theory)
-- ============================================================================

-- ============================================================================
-- TABLE: support_systems.theory_sheets
-- Description: Theory content that tutors can explain
-- ============================================================================

CREATE TABLE IF NOT EXISTS support_systems.theory_sheets (
    sheet_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chapter_id UUID NOT NULL REFERENCES courses.chapters(chapter_id) ON DELETE CASCADE,

    -- Identification
    title VARCHAR(255) NOT NULL,
    topic VARCHAR(100),
    order_index INTEGER DEFAULT 0,

    -- Content
    content TEXT NOT NULL,  -- Markdown format
    learning_objectives TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- Metadata
    difficulty_level VARCHAR(20) DEFAULT 'medium',  -- beginner, intermediate, advanced
    estimated_duration_minutes INTEGER,
    key_concepts TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- AI Integration
    ai_summary TEXT,  -- Auto-generated summary by AI
    explanation_prompt_id UUID REFERENCES ai_pipeline.prompts(prompt_id),

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    CONSTRAINT chk_difficulty CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced'))
);

CREATE INDEX IF NOT EXISTS idx_theory_sheets_chapter ON support_systems.theory_sheets(chapter_id);
CREATE INDEX IF NOT EXISTS idx_theory_sheets_difficulty ON support_systems.theory_sheets(difficulty_level);

COMMENT ON TABLE support_systems.theory_sheets IS 'Theory content for tutor explanations and Q&A';

-- ============================================================================
-- TABLE: support_systems.theory_explanations
-- Description: AI-generated explanations of theory sheets
-- ============================================================================

CREATE TABLE IF NOT EXISTS support_systems.theory_explanations (
    explanation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sheet_id UUID NOT NULL REFERENCES support_systems.theory_sheets(sheet_id) ON DELETE CASCADE,

    -- Generation info
    explanation_text TEXT NOT NULL,
    ai_model VARCHAR(100),
    prompt_used UUID REFERENCES ai_pipeline.prompts(prompt_id),

    -- Quality tracking
    student_satisfactions_count INTEGER DEFAULT 0,
    average_satisfaction DECIMAL(3,2),
    was_helpful_count INTEGER DEFAULT 0,

    -- Timestamps
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    generated_by UUID REFERENCES core.users(user_id)
);

CREATE INDEX IF NOT EXISTS idx_theory_explanations_sheet ON support_systems.theory_explanations(sheet_id);
CREATE INDEX IF NOT EXISTS idx_theory_explanations_model ON support_systems.theory_explanations(ai_model);

COMMENT ON TABLE support_systems.theory_explanations IS 'AI-generated explanations of theory sheets';

-- ============================================================================
-- TABLE: support_systems.student_questions
-- Description: Questions students ask about theory (Q&A with tutor)
-- ============================================================================

CREATE TABLE IF NOT EXISTS support_systems.student_questions (
    question_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sheet_id UUID REFERENCES support_systems.theory_sheets(sheet_id) ON DELETE SET NULL,
    chapter_id UUID NOT NULL REFERENCES courses.chapters(chapter_id) ON DELETE CASCADE,

    -- Question
    student_id UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,

    -- Context
    context_type VARCHAR(50),  -- reading_theory, doing_exercise, stuck_on_concept
    affected_concept VARCHAR(200),

    -- Tutor response
    tutor_response TEXT,
    response_prompt_id UUID REFERENCES ai_pipeline.prompts(prompt_id),
    ai_model VARCHAR(100),
    response_confidence DECIMAL(3,2),  -- 0.0-1.0

    -- Quality feedback
    student_satisfied BOOLEAN,
    satisfaction_rating INTEGER,  -- 1-5
    student_feedback TEXT,

    -- Followup
    has_followup_questions BOOLEAN DEFAULT FALSE,
    resolved BOOLEAN DEFAULT FALSE,

    -- Timestamps
    asked_at TIMESTAMPTZ DEFAULT NOW(),
    answered_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_student_questions_sheet ON support_systems.student_questions(sheet_id);
CREATE INDEX IF NOT EXISTS idx_student_questions_student ON support_systems.student_questions(student_id);
CREATE INDEX IF NOT EXISTS idx_student_questions_chapter ON support_systems.student_questions(chapter_id);
CREATE INDEX IF NOT EXISTS idx_student_questions_resolved ON support_systems.student_questions(resolved) WHERE resolved = FALSE;

COMMENT ON TABLE support_systems.student_questions IS 'Student questions about theory with AI tutor responses';
COMMENT ON COLUMN support_systems.student_questions.response_confidence IS 'How confident is the AI in its answer (0.0-1.0)?';

-- ============================================================================
-- TABLE: support_systems.clarification_requests
-- Description: Track what students struggle with for tutor improvement
-- ============================================================================

CREATE TABLE IF NOT EXISTS support_systems.clarification_requests (
    request_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sheet_id UUID REFERENCES support_systems.theory_sheets(sheet_id) ON DELETE SET NULL,
    student_id UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,

    -- What needs clarification
    concept VARCHAR(200) NOT NULL,
    description TEXT,
    difficulty_indicator INTEGER,  -- 1-5: how hard is this concept?

    -- Response
    clarification_provided TEXT,
    clarification_type VARCHAR(50),  -- additional_example, simpler_explanation, visualization, analogy
    ai_model VARCHAR(100),

    -- Feedback
    was_helpful BOOLEAN,
    student_comment TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_clarification_concept ON support_systems.clarification_requests(concept);
CREATE INDEX IF NOT EXISTS idx_clarification_student ON support_systems.clarification_requests(student_id);
CREATE INDEX IF NOT EXISTS idx_clarification_resolved ON support_systems.clarification_requests(resolved_at);

COMMENT ON TABLE support_systems.clarification_requests IS 'Tracks concepts that need clarification for tutor improvement';

-- ============================================================================
-- Function: log_student_understanding()
-- Description: Helper function to track student understanding patterns
-- ============================================================================

CREATE OR REPLACE FUNCTION log_student_understanding(
    p_sheet_id UUID,
    p_student_id UUID,
    p_understood BOOLEAN,
    p_concept VARCHAR
)
RETURNS void AS $$
BEGIN
    -- Track understanding in clarification_requests if student struggled
    IF NOT p_understood THEN
        INSERT INTO support_systems.clarification_requests
            (sheet_id, student_id, concept, difficulty_indicator, created_at)
        VALUES
            (p_sheet_id, p_student_id, p_concept, 3, CURRENT_TIMESTAMP)
        ON CONFLICT DO NOTHING;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- End of Migration: 081_theory_explanations.sql
-- ============================================================================
