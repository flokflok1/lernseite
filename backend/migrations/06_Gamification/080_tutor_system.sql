-- ============================================================================
-- Migration: 080_tutor_system.sql
-- Version: 1.0.0
-- Description: Tutor System (Base Infrastructure for AI Tutor)
-- Author: LernsystemX Migration System
-- Date: 2026-01-26
-- Phase: 4 (System Features - Tutor Infrastructure)
-- Dependencies: 000_schemas.sql (support_systems schema)
-- ============================================================================

-- ============================================================================
-- TABLE: support_systems.tutor_configurations
-- Description: Global and per-course tutor settings
-- ============================================================================

CREATE TABLE IF NOT EXISTS support_systems.tutor_configurations (
    config_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Scope
    scope VARCHAR(20) NOT NULL,  -- 'system' or 'course'
    course_id UUID REFERENCES courses.courses(course_id) ON DELETE CASCADE,

    -- Tutor behavior settings
    tutor_name VARCHAR(100) DEFAULT 'Tutor',
    tutor_role VARCHAR(100) DEFAULT 'Intelligent Tutor System',
    personality VARCHAR(50) DEFAULT 'helpful',  -- helpful, socratic, strict, encouraging
    language VARCHAR(10) DEFAULT 'de',

    -- AI Model configuration
    ai_model VARCHAR(100) DEFAULT 'claude-3-opus',
    temperature DECIMAL(3,2) DEFAULT 0.7,
    max_tokens INTEGER DEFAULT 2000,

    -- Features enabled
    explain_theory BOOLEAN DEFAULT TRUE,
    answer_questions BOOLEAN DEFAULT TRUE,
    evaluate_tasks BOOLEAN DEFAULT TRUE,
    provide_hints BOOLEAN DEFAULT TRUE,
    use_tts BOOLEAN DEFAULT TRUE,

    -- TTS Configuration
    tts_enabled BOOLEAN DEFAULT TRUE,
    tts_voice VARCHAR(50) DEFAULT 'default',
    tts_speed DECIMAL(3,2) DEFAULT 1.0,
    tts_provider VARCHAR(50) DEFAULT 'google',  -- google, aws, azure, local

    -- Response settings
    max_explanation_length INTEGER DEFAULT 1000,
    max_hint_length INTEGER DEFAULT 500,
    response_timeout_seconds INTEGER DEFAULT 30,

    -- Context settings
    context_window_size INTEGER DEFAULT 5,  -- How many previous messages to remember
    use_course_knowledge BOOLEAN DEFAULT TRUE,

    -- Feedback settings
    feedback_level VARCHAR(20) DEFAULT 'detailed',  -- minimal, standard, detailed
    show_step_by_step BOOLEAN DEFAULT TRUE,

    -- Advanced
    config JSONB DEFAULT '{}',

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    CONSTRAINT chk_scope CHECK (scope IN ('system', 'course')),
    CONSTRAINT chk_personality CHECK (personality IN ('helpful', 'socratic', 'strict', 'encouraging')),
    CONSTRAINT chk_temperature CHECK (temperature >= 0.0 AND temperature <= 1.0),
    CONSTRAINT chk_feedback_level CHECK (feedback_level IN ('minimal', 'standard', 'detailed'))
);

CREATE INDEX IF NOT EXISTS idx_tutor_config_scope ON support_systems.tutor_configurations(scope);
CREATE INDEX IF NOT EXISTS idx_tutor_config_course ON support_systems.tutor_configurations(course_id);

COMMENT ON TABLE support_systems.tutor_configurations IS 'Global and per-course tutor settings and behavior';

-- ============================================================================
-- TABLE: support_systems.tutor_knowledge_bases
-- Description: Course-specific knowledge bases for the tutor
-- ============================================================================

CREATE TABLE IF NOT EXISTS support_systems.tutor_knowledge_bases (
    kb_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID NOT NULL REFERENCES courses.courses(course_id) ON DELETE CASCADE,

    -- Knowledge base metadata
    name VARCHAR(100) NOT NULL,
    description TEXT,

    -- Content type
    content_type VARCHAR(50) NOT NULL,  -- theory_sheets, textbook_chapters, qna_pairs, examples
    content JSONB NOT NULL,  -- Structured knowledge

    -- Indexing
    is_indexed BOOLEAN DEFAULT FALSE,
    embedding_model VARCHAR(100),  -- For semantic search

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    CONSTRAINT chk_content_type CHECK (content_type IN ('theory_sheets', 'textbook_chapters', 'qna_pairs', 'examples', 'definitions'))
);

CREATE INDEX IF NOT EXISTS idx_tutor_kb_course ON support_systems.tutor_knowledge_bases(course_id);
CREATE INDEX IF NOT EXISTS idx_tutor_kb_type ON support_systems.tutor_knowledge_bases(content_type);

COMMENT ON TABLE support_systems.tutor_knowledge_bases IS 'Course-specific knowledge for tutor context and grounding';

-- ============================================================================
-- TABLE: support_systems.tutor_prompts
-- Description: Templates for tutor interactions (explanations, questions, feedback)
-- ============================================================================

CREATE TABLE IF NOT EXISTS support_systems.tutor_prompts (
    prompt_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Identification
    name VARCHAR(100) NOT NULL,
    purpose VARCHAR(50) NOT NULL,  -- explanation, question, feedback, hint

    -- Prompt content
    system_prompt TEXT NOT NULL,
    user_prompt_template TEXT,
    example_response TEXT,

    -- Customization
    language VARCHAR(10) DEFAULT 'de',
    tone VARCHAR(50) DEFAULT 'friendly',

    -- Templates for variables
    template_variables TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    CONSTRAINT chk_purpose CHECK (purpose IN ('explanation', 'question', 'feedback', 'hint', 'summary'))
);

CREATE INDEX IF NOT EXISTS idx_tutor_prompts_purpose ON support_systems.tutor_prompts(purpose);

COMMENT ON TABLE support_systems.tutor_prompts IS 'Prompt templates for different tutor interaction types';

-- ============================================================================
-- End of Migration: 080_tutor_system.sql
-- ============================================================================
