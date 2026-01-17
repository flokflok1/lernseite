-- ============================================================================
-- Migration: 048_ai_authoring_studio_part2.sql
-- Description: AI Editor (AI Authoring) - Part 2: Multi-File System
--              Tables: authoring_files, authoring_analysis, authoring_generations,
--                     authoring_refinements, authoring_user_journey, ai_decision_explanations
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-01-16
-- ============================================================================
-- Note: Split from original 048_ai_authoring_studio.sql (857 lines)
--       Part 2 of 3: Multi-file course authoring system
-- ============================================================================

-- EXTENSIONS (2025-01-07): Multi-File Kurs Studio System
-- ============================================================================

-- ============================================================================
-- TABLE: authoring_files
-- Description: File upload and management for multi-file course authoring
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_pipeline.authoring_files (
    file_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES ai_pipeline.ai_authoring_sessions(session_id) ON DELETE CASCADE,

    -- File metadata
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    storage_path TEXT NOT NULL,

    -- Extracted content
    extracted_text TEXT,
    extracted_metadata JSONB DEFAULT '{}',

    -- Processing status
    analysis_status VARCHAR(50) DEFAULT 'pending'
        CHECK (analysis_status IN ('pending', 'processing', 'completed', 'failed')),
    ai_analysis_id UUID,  -- Reference to authoring_analysis
    processing_error TEXT,

    -- Upload info
    uploaded_by UUID REFERENCES core.users(user_id) ON DELETE SET NULL,
    uploaded_at TIMESTAMPTZ DEFAULT NOW(),

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_authoring_files_session ON ai_pipeline.authoring_files(session_id);
CREATE INDEX IF NOT EXISTS idx_authoring_files_status ON ai_pipeline.authoring_files(analysis_status);
CREATE INDEX IF NOT EXISTS idx_authoring_files_type ON ai_pipeline.authoring_files(file_type);

COMMENT ON TABLE ai_pipeline.authoring_files IS 'Uploaded files for multi-file course authoring (e.g., 7 years of IHK exams)';
COMMENT ON COLUMN ai_pipeline.authoring_files.extracted_text IS 'Full text extracted from PDF/DOC for AI analysis';
COMMENT ON COLUMN ai_pipeline.authoring_files.extracted_metadata IS 'File metadata: page count, images, tables detected';

-- ============================================================================
-- TABLE: authoring_analysis
-- Description: Multi-file AI analysis with exam pattern recognition
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_pipeline.authoring_analysis (
    analysis_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES ai_pipeline.ai_authoring_sessions(session_id) ON DELETE CASCADE,

    -- Multi-file analysis
    file_ids UUID[] NOT NULL,
    analysis_type VARCHAR(50) NOT NULL
        CHECK (analysis_type IN ('single_file', 'multi_file', 'exam_pattern', 'content_structure', 'quality_check')),

    -- Analysis results
    topics_found JSONB DEFAULT '[]',
    difficulty_analysis JSONB DEFAULT '{}',
    exam_patterns JSONB DEFAULT '{}',  -- KRITISCH für IHK-Prüfungen!
    content_structure JSONB DEFAULT '{}',
    quality_metrics JSONB DEFAULT '{}',

    -- Exam pattern insights (Psychologische UX Extension)
    exam_insights JSONB DEFAULT '{}',  -- {"häufige_themen": [...], "schwierigkeitsverteilung": {...}}
    user_feedback_on_insights TEXT,
    insights_applied BOOLEAN DEFAULT false,

    -- AI metadata
    ai_provider VARCHAR(50) NOT NULL,
    ai_model VARCHAR(100) NOT NULL,
    tokens_used INT DEFAULT 0,
    prompt_used TEXT,

    -- Status tracking
    status VARCHAR(50) DEFAULT 'queued'
        CHECK (status IN ('queued', 'processing', 'completed', 'failed')),
    error_message TEXT,

    -- Timing
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    processing_duration_ms INTEGER,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_authoring_analysis_session ON ai_pipeline.authoring_analysis(session_id);
CREATE INDEX IF NOT EXISTS idx_authoring_analysis_type ON ai_pipeline.authoring_analysis(analysis_type);
CREATE INDEX IF NOT EXISTS idx_authoring_analysis_status ON ai_pipeline.authoring_analysis(status);

COMMENT ON TABLE ai_pipeline.authoring_analysis IS 'Multi-file AI analysis for course generation (exam pattern detection across years)';
COMMENT ON COLUMN ai_pipeline.authoring_analysis.exam_patterns IS 'Recognized patterns in exam files: recurring topics, difficulty trends, question types';
COMMENT ON COLUMN ai_pipeline.authoring_analysis.exam_insights IS 'User-friendly insights from exam analysis for UI display';

-- ============================================================================
-- TABLE: authoring_generations
-- Description: Long-running course generation jobs with progress tracking
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_pipeline.authoring_generations (
    generation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES ai_pipeline.ai_authoring_sessions(session_id) ON DELETE CASCADE,

    -- Generation scope
    generation_scope VARCHAR(50) NOT NULL
        CHECK (generation_scope IN ('full_course', 'single_chapter', 'single_lesson', 'method_set')),
    scope_details JSONB DEFAULT '{}',

    -- Progress tracking
    status VARCHAR(50) DEFAULT 'queued'
        CHECK (status IN ('queued', 'initializing', 'generating', 'completed', 'failed', 'cancelled')),
    progress_percentage INT DEFAULT 0
        CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    current_step VARCHAR(100),
    steps_total INT DEFAULT 0,
    steps_completed INT DEFAULT 0,

    -- Generated content references
    generated_course_id UUID REFERENCES courses.courses(course_id) ON DELETE SET NULL,
    generated_chapter_ids UUID[] DEFAULT '{}',
    generated_lesson_ids UUID[] DEFAULT '{}',
    generated_chapters INT DEFAULT 0,
    generated_lessons INT DEFAULT 0,
    generated_methods INT DEFAULT 0,

    -- AI metadata
    ai_provider VARCHAR(50) NOT NULL,
    ai_model VARCHAR(100) NOT NULL,
    total_tokens_used INT DEFAULT 0,
    estimated_tokens INT,
    estimated_cost_cents INT,
    actual_cost_cents INT,

    -- Error handling
    error_message TEXT,
    retry_count INT DEFAULT 0,

    -- User interaction
    user_cancelled BOOLEAN DEFAULT false,
    user_cancellation_reason TEXT,

    -- Timing
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    estimated_completion_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_authoring_generations_session ON ai_pipeline.authoring_generations(session_id);
CREATE INDEX IF NOT EXISTS idx_authoring_generations_status ON ai_pipeline.authoring_generations(status);
CREATE INDEX IF NOT EXISTS idx_authoring_generations_course ON ai_pipeline.authoring_generations(generated_course_id);
CREATE INDEX IF NOT EXISTS idx_authoring_generations_active ON ai_pipeline.authoring_generations(status, created_at DESC)
    WHERE status IN ('queued', 'initializing', 'generating');

COMMENT ON TABLE ai_pipeline.authoring_generations IS 'Long-running generation jobs for full courses with progress tracking';
COMMENT ON COLUMN ai_pipeline.authoring_generations.current_step IS 'Current step for UI display: "Analyzing Chapter 3/12"';
COMMENT ON COLUMN ai_pipeline.authoring_generations.estimated_completion_at IS 'ETA for UI progress bar';

-- ============================================================================
-- TABLE: authoring_refinements
-- Description: User-requested refinements with AI suggestions
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_pipeline.authoring_refinements (
    refinement_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES ai_pipeline.ai_authoring_sessions(session_id) ON DELETE CASCADE,
    generation_id UUID REFERENCES ai_pipeline.authoring_generations(generation_id) ON DELETE SET NULL,

    -- Target of refinement
    target_type VARCHAR(50) NOT NULL
        CHECK (target_type IN ('course', 'chapter', 'lesson', 'method', 'theory', 'quiz')),
    target_id UUID NOT NULL,

    -- Refinement request
    refinement_type VARCHAR(50) NOT NULL
        CHECK (refinement_type IN ('simplify', 'expand', 'split', 'merge', 'rewrite', 'translate', 'adjust_difficulty', 'add_examples')),
    user_request TEXT NOT NULL,

    -- AI response
    ai_suggestion TEXT,
    ai_actions JSONB DEFAULT '[]',  -- [{"action": "split_chapter", "params": {...}}]

    -- Collaborative discussion (Psychologische UX Extension)
    discussion_thread JSONB DEFAULT '[]',  -- User-KI Dialog über diese Refinement
    ai_learning_note TEXT,  -- Was lernt KI aus User-Entscheidung?

    -- User decision
    user_approved BOOLEAN,
    user_feedback TEXT,
    applied BOOLEAN DEFAULT false,
    applied_at TIMESTAMPTZ,

    -- AI metadata
    ai_provider VARCHAR(50),
    ai_model VARCHAR(100),
    tokens_used INT DEFAULT 0,

    -- Timing
    requested_at TIMESTAMPTZ DEFAULT NOW(),
    responded_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_authoring_refinements_session ON ai_pipeline.authoring_refinements(session_id);
CREATE INDEX IF NOT EXISTS idx_authoring_refinements_generation ON ai_pipeline.authoring_refinements(generation_id);
CREATE INDEX IF NOT EXISTS idx_authoring_refinements_target ON ai_pipeline.authoring_refinements(target_type, target_id);
CREATE INDEX IF NOT EXISTS idx_authoring_refinements_type ON ai_pipeline.authoring_refinements(refinement_type);
CREATE INDEX IF NOT EXISTS idx_authoring_refinements_pending ON ai_pipeline.authoring_refinements(session_id)
    WHERE user_approved IS NULL;

COMMENT ON TABLE ai_pipeline.authoring_refinements IS 'User-requested refinements with AI suggestions and collaborative discussion';
COMMENT ON COLUMN ai_pipeline.authoring_refinements.ai_actions IS 'Structured actions AI will perform: split, merge, rewrite';
COMMENT ON COLUMN ai_pipeline.authoring_refinements.discussion_thread IS 'User-KI dialog about this refinement for learning';

-- ============================================================================
-- TABLE: authoring_user_journey (Psychologische UX Extension)
-- Description: Track user's progress through authoring workflow
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_pipeline.authoring_user_journey (
    journey_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES ai_pipeline.ai_authoring_sessions(session_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,

    -- Current state
    current_phase VARCHAR(50) NOT NULL
        CHECK (current_phase IN ('upload', 'analysis', 'planning', 'generation', 'refinement', 'preview', 'finalize')),
    completed_phases VARCHAR(50)[] DEFAULT '{}',

    -- User guidance
    suggested_next_action TEXT,
    user_experience_level VARCHAR(20) DEFAULT 'beginner'
        CHECK (user_experience_level IN ('beginner', 'intermediate', 'expert')),

    -- Help system
    tips_shown TEXT[] DEFAULT '{}',
    last_tip_shown_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_authoring_journey_session ON ai_pipeline.authoring_user_journey(session_id);
CREATE INDEX IF NOT EXISTS idx_authoring_journey_user ON ai_pipeline.authoring_user_journey(user_id);
CREATE INDEX IF NOT EXISTS idx_authoring_journey_phase ON ai_pipeline.authoring_user_journey(current_phase);

COMMENT ON TABLE ai_pipeline.authoring_user_journey IS 'Track user progress and provide contextual guidance (Progressive Disclosure)';
COMMENT ON COLUMN ai_pipeline.authoring_user_journey.suggested_next_action IS 'Next step suggestion based on current phase';

-- ============================================================================
-- TABLE: ai_decision_explanations (Psychologische UX Extension)
-- Description: AI explains WHY it made certain decisions
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_pipeline.ai_decision_explanations (
    explanation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES ai_pipeline.ai_authoring_sessions(session_id) ON DELETE CASCADE,
    analysis_id UUID REFERENCES ai_pipeline.authoring_analysis(analysis_id) ON DELETE CASCADE,
    generation_id UUID REFERENCES ai_pipeline.authoring_generations(generation_id) ON DELETE CASCADE,

    -- Decision context
    decision_type VARCHAR(50) NOT NULL
        CHECK (decision_type IN ('chapter_split', 'topic_grouping', 'difficulty_assignment', 'method_selection', 'exam_focus')),

    -- AI reasoning
    ai_reasoning TEXT NOT NULL,
    user_friendly_explanation TEXT NOT NULL,
    confidence_score FLOAT CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),

    -- Alternative options
    alternative_options JSONB DEFAULT '[]',  -- [{"option": "...", "pros": [...], "cons": [...]}]

    -- User feedback
    user_accepted BOOLEAN,
    user_selected_alternative INT,  -- Index in alternative_options
    user_feedback TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ai_explanations_session ON ai_pipeline.ai_decision_explanations(session_id);
CREATE INDEX IF NOT EXISTS idx_ai_explanations_type ON ai_pipeline.ai_decision_explanations(decision_type);
CREATE INDEX IF NOT EXISTS idx_ai_explanations_generation ON ai_pipeline.ai_decision_explanations(generation_id);

COMMENT ON TABLE ai_pipeline.ai_decision_explanations IS 'AI transparency: explain decisions and offer alternatives';
COMMENT ON COLUMN ai_pipeline.ai_decision_explanations.alternative_options IS 'What else could AI have done? User can choose alternative';

