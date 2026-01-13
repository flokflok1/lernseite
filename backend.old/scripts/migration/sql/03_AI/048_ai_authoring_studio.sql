-- ============================================================================
-- Migration: 048_ai_authoring_studio.sql
-- Version: 1.0.0
-- Description: Database migration
-- Author: LernsystemX Migration System
-- Date: 2026-01-02
-- ============================================================================

CREATE TABLE IF NOT EXISTS ai_pipeline.ai_authoring_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES core.users(user_id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses.courses(course_id) ON DELETE CASCADE,
    chapter_id UUID REFERENCES courses.chapters(chapter_id) ON DELETE SET NULL,

    -- Session metadata
    session_name VARCHAR(255),
    status VARCHAR(30) DEFAULT 'draft',

    -- Source content (PDF analysis, manual input, etc.)
    source_type VARCHAR(50) DEFAULT 'manual',
    source_data JSONB DEFAULT '{}',

    -- AI configuration for this session
    ai_config JSONB DEFAULT '{
        "provider": "anthropic",
        "model": "claude-sonnet-4-20250514",
        "temperature": 0.7,
        "max_tokens": 4000
    }',

    -- Generated content storage
    generated_theory JSONB,
    generated_lessons JSONB DEFAULT '[]',
    generated_methods JSONB DEFAULT '[]',

    -- Progress tracking
    current_step VARCHAR(50) DEFAULT 'source_selection',
    steps_completed JSONB DEFAULT '[]',

    -- Timing
    started_at TIMESTAMPTZ DEFAULT NOW(),
    last_activity_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT chk_session_status CHECK (status IN ('draft', 'in_progress', 'review', 'completed', 'cancelled')),
    CONSTRAINT chk_source_type CHECK (source_type IN ('manual', 'pdf', 'url', 'existing_chapter', 'template'))
);

CREATE INDEX IF NOT EXISTS idx_ai_authoring_sessions_user ON ai_pipeline.ai_authoring_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_authoring_sessions_course ON ai_pipeline.ai_authoring_sessions(course_id);
CREATE INDEX IF NOT EXISTS idx_ai_authoring_sessions_chapter ON ai_pipeline.ai_authoring_sessions(chapter_id);
CREATE INDEX IF NOT EXISTS idx_ai_authoring_sessions_status ON ai_pipeline.ai_authoring_sessions(status);
CREATE INDEX IF NOT EXISTS idx_ai_authoring_sessions_activity ON ai_pipeline.ai_authoring_sessions(last_activity_at DESC);

COMMENT ON TABLE ai_pipeline.ai_authoring_sessions IS 'KI-Authoring-Studio sessions for AI-assisted content creation';
COMMENT ON COLUMN ai_pipeline.ai_authoring_sessions.source_data IS 'Source content data (PDF text, URL content, etc.)';
COMMENT ON COLUMN ai_pipeline.ai_authoring_sessions.generated_theory IS 'AI-generated theory content for chapter';
COMMENT ON COLUMN ai_pipeline.ai_authoring_sessions.generated_lessons IS 'Array of AI-generated lesson objects';
COMMENT ON COLUMN ai_pipeline.ai_authoring_sessions.generated_methods IS 'Array of AI-generated learning method objects';

-- ============================================================================
-- TABLE: ai_session_snapshots
-- Description: Undo/Redo snapshots for session state
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_pipeline.ai_session_snapshots (
    snapshot_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES ai_pipeline.ai_authoring_sessions(session_id) ON DELETE CASCADE,

    -- Snapshot content
    snapshot_data JSONB NOT NULL,
    description VARCHAR(255),

    -- Position in history
    sequence_number INTEGER NOT NULL,
    is_current BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ai_session_snapshots_session ON ai_pipeline.ai_session_snapshots(session_id);
CREATE INDEX IF NOT EXISTS idx_ai_session_snapshots_sequence ON ai_pipeline.ai_session_snapshots(session_id, sequence_number);
CREATE INDEX IF NOT EXISTS idx_ai_session_snapshots_current ON ai_pipeline.ai_session_snapshots(session_id) WHERE is_current = TRUE;

COMMENT ON TABLE ai_pipeline.ai_session_snapshots IS 'State snapshots for undo/redo functionality in authoring sessions';
COMMENT ON COLUMN ai_pipeline.ai_session_snapshots.sequence_number IS 'Order number for history navigation';

-- ============================================================================
-- TABLE: ai_generation_variants
-- Description: Multiple AI-generated variants for comparison
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_pipeline.ai_generation_variants (
    variant_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES ai_pipeline.ai_authoring_sessions(session_id) ON DELETE CASCADE,

    -- Variant identification
    variant_type VARCHAR(50) NOT NULL,
    variant_index INTEGER DEFAULT 0,

    -- Content
    content JSONB NOT NULL,

    -- AI generation metadata
    ai_provider VARCHAR(50),
    ai_model VARCHAR(100),
    prompt_used TEXT,
    generation_params JSONB,

    -- User selection
    is_selected BOOLEAN DEFAULT FALSE,
    user_rating INTEGER,
    user_feedback TEXT,

    -- Timing
    generation_started_at TIMESTAMPTZ,
    generation_completed_at TIMESTAMPTZ,
    generation_duration_ms INTEGER,

    created_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT chk_variant_type CHECK (variant_type IN ('theory', 'lesson', 'method', 'quiz', 'summary', 'full_chapter')),
    CONSTRAINT chk_user_rating CHECK (user_rating IS NULL OR (user_rating >= 1 AND user_rating <= 5))
);

CREATE INDEX IF NOT EXISTS idx_ai_generation_variants_session ON ai_pipeline.ai_generation_variants(session_id);
CREATE INDEX IF NOT EXISTS idx_ai_generation_variants_type ON ai_pipeline.ai_generation_variants(variant_type);
CREATE INDEX IF NOT EXISTS idx_ai_generation_variants_selected ON ai_pipeline.ai_generation_variants(session_id) WHERE is_selected = TRUE;

COMMENT ON TABLE ai_pipeline.ai_generation_variants IS 'Multiple AI-generated content variants for user comparison';
COMMENT ON COLUMN ai_pipeline.ai_generation_variants.variant_type IS 'Type of content: theory, lesson, method, quiz, summary, full_chapter';

-- ============================================================================
-- TABLE: ai_studio_analytics
-- Description: Analytics events for KI-Authoring-Studio usage
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_pipeline.ai_studio_analytics (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES ai_pipeline.ai_authoring_sessions(session_id) ON DELETE SET NULL,
    user_id UUID REFERENCES core.users(user_id) ON DELETE SET NULL,

    -- Event details
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB DEFAULT '{}',

    -- AI metrics (if applicable)
    tokens_used INTEGER,
    generation_time_ms INTEGER,
    ai_provider VARCHAR(50),
    ai_model VARCHAR(100),

    -- Context
    step_name VARCHAR(50),
    component_name VARCHAR(100),

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ai_studio_analytics_session ON ai_pipeline.ai_studio_analytics(session_id);
CREATE INDEX IF NOT EXISTS idx_ai_studio_analytics_user ON ai_pipeline.ai_studio_analytics(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_studio_analytics_type ON ai_pipeline.ai_studio_analytics(event_type);
CREATE INDEX IF NOT EXISTS idx_ai_studio_analytics_created ON ai_pipeline.ai_studio_analytics(created_at DESC);

COMMENT ON TABLE ai_pipeline.ai_studio_analytics IS 'Usage analytics for KI-Authoring-Studio';

-- ============================================================================
-- TABLE: pdf_cache
-- Description: Cached PDF analysis results for reuse
-- ============================================================================
CREATE TABLE IF NOT EXISTS storage.pdf_cache (
    cache_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- File identification
    file_hash VARCHAR(64) NOT NULL UNIQUE,
    original_filename VARCHAR(255),
    file_size_bytes BIGINT,
    page_count INTEGER,

    -- Extracted content
    extracted_text TEXT,
    extracted_metadata JSONB DEFAULT '{}',
    structure_analysis JSONB DEFAULT '{}',

    -- Processing info
    extraction_method VARCHAR(50) DEFAULT 'pdfplumber',
    processing_time_ms INTEGER,

    -- Cache management
    access_count INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_pdf_cache_hash ON storage.pdf_cache(file_hash);
CREATE INDEX IF NOT EXISTS idx_pdf_cache_expires ON storage.pdf_cache(expires_at) WHERE expires_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_pdf_cache_accessed ON storage.pdf_cache(last_accessed_at DESC);

COMMENT ON TABLE storage.pdf_cache IS 'Cached PDF extraction results to avoid redundant processing';
COMMENT ON COLUMN storage.pdf_cache.file_hash IS 'SHA-256 hash of file content for deduplication';
COMMENT ON COLUMN storage.pdf_cache.structure_analysis IS 'AI-analyzed structure (headings, sections, key topics)';

-- ============================================================================
-- ALTER TABLE: chapters - Add AI authoring metadata
-- ============================================================================
DO $$
BEGIN
    -- Add ai_generated flag
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'chapters' AND column_name = 'ai_generated') THEN
        ALTER TABLE courses.chapters ADD COLUMN ai_generated BOOLEAN DEFAULT FALSE;
        RAISE NOTICE 'Added column chapters.ai_generated';
    END IF;

    -- Add source session reference
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'chapters' AND column_name = 'ai_session_id') THEN
        ALTER TABLE courses.chapters ADD COLUMN ai_session_id UUID REFERENCES ai_pipeline.ai_authoring_sessions(session_id) ON DELETE SET NULL;
        RAISE NOTICE 'Added column chapters.ai_session_id';
    END IF;

    -- Add generation metadata
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'chapters' AND column_name = 'ai_metadata') THEN
        ALTER TABLE courses.chapters ADD COLUMN ai_metadata JSONB DEFAULT '{}';
        RAISE NOTICE 'Added column chapters.ai_metadata';
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_chapters_ai_generated ON courses.chapters(ai_generated) WHERE ai_generated = TRUE;
CREATE INDEX IF NOT EXISTS idx_chapters_ai_session ON courses.chapters(ai_session_id) WHERE ai_session_id IS NOT NULL;

COMMENT ON COLUMN courses.chapters.ai_generated IS 'Indicates if chapter was created via KI-Authoring-Studio';
COMMENT ON COLUMN courses.chapters.ai_session_id IS 'Reference to the authoring session that created this chapter';
COMMENT ON COLUMN courses.chapters.ai_metadata IS 'AI generation metadata (model used, prompts, timestamps)';

-- ============================================================================
-- TABLE: ai_authoring_templates
-- Description: Reusable templates for AI content generation
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_pipeline.ai_authoring_templates (
    template_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Template identification
    template_name VARCHAR(255) NOT NULL,
    template_key VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50) DEFAULT 'general',

    -- Template content
    description TEXT,
    template_config JSONB NOT NULL,

    -- Usage settings
    is_system BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_by UUID REFERENCES core.users(user_id) ON DELETE SET NULL,

    -- Stats
    usage_count INTEGER DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ai_authoring_templates_key ON ai_pipeline.ai_authoring_templates(template_key);
CREATE INDEX IF NOT EXISTS idx_ai_authoring_templates_category ON ai_pipeline.ai_authoring_templates(category);
CREATE INDEX IF NOT EXISTS idx_ai_authoring_templates_active ON ai_pipeline.ai_authoring_templates(is_active) WHERE is_active = TRUE;

COMMENT ON TABLE ai_pipeline.ai_authoring_templates IS 'Reusable templates for KI-Authoring-Studio workflows';
COMMENT ON COLUMN ai_pipeline.ai_authoring_templates.template_config IS 'Template configuration: steps, default prompts, AI settings';

-- ============================================================================
-- NOTE: Keine Seed-Daten - Authoring Templates werden via Frontend konfiguriert
-- Templates: standard_chapter, quiz_focused, vocabulary_chapter, practical_skills etc.
-- ============================================================================

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- ============================================================================
DROP TRIGGER IF EXISTS update_ai_authoring_sessions_updated_at ON ai_pipeline.ai_authoring_sessions;
CREATE TRIGGER update_ai_authoring_sessions_updated_at BEFORE UPDATE ON ai_pipeline.ai_authoring_sessions
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_ai_authoring_templates_updated_at ON ai_pipeline.ai_authoring_templates;
CREATE TRIGGER update_ai_authoring_templates_updated_at BEFORE UPDATE ON ai_pipeline.ai_authoring_templates
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

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

-- ============================================================================
-- TABLE: authoring_milestones (Psychologische UX Extension)
-- Description: Celebrate user achievements (Gamification)
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_pipeline.authoring_milestones (
    milestone_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES ai_pipeline.ai_authoring_sessions(session_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,

    -- Milestone details
    milestone_type VARCHAR(50) NOT NULL
        CHECK (milestone_type IN ('first_upload', 'first_analysis', 'first_generation', 'first_refinement', 'course_completed', 'multi_file_master', 'exam_pattern_expert')),

    -- Celebration
    achievement_title VARCHAR(255) NOT NULL,
    celebration_message TEXT NOT NULL,
    badge_earned VARCHAR(100),

    -- Stats
    achievement_data JSONB DEFAULT '{}',  -- {"chapters_created": 12, "lessons_created": 47}

    achieved_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_authoring_milestones_session ON ai_pipeline.authoring_milestones(session_id);
CREATE INDEX IF NOT EXISTS idx_authoring_milestones_user ON ai_pipeline.authoring_milestones(user_id);
CREATE INDEX IF NOT EXISTS idx_authoring_milestones_type ON ai_pipeline.authoring_milestones(milestone_type);

COMMENT ON TABLE ai_pipeline.authoring_milestones IS 'User achievements and celebrations for motivation';
COMMENT ON COLUMN ai_pipeline.authoring_milestones.achievement_data IS 'Statistics about this achievement';

-- ============================================================================
-- ALTER EXISTING TABLES: Add new columns for enhanced functionality
-- ============================================================================

-- Extend ai_authoring_sessions for multi-file support
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'ai_authoring_sessions' AND column_name = 'target_audience') THEN
        ALTER TABLE ai_pipeline.ai_authoring_sessions
            ADD COLUMN target_audience JSONB DEFAULT '{}';
        RAISE NOTICE 'Added column ai_authoring_sessions.target_audience';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'ai_authoring_sessions' AND column_name = 'exam_integration') THEN
        ALTER TABLE ai_pipeline.ai_authoring_sessions
            ADD COLUMN exam_integration JSONB DEFAULT '{}';
        RAISE NOTICE 'Added column ai_authoring_sessions.exam_integration';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'ai_authoring_sessions' AND column_name = 'multi_file_support') THEN
        ALTER TABLE ai_pipeline.ai_authoring_sessions
            ADD COLUMN multi_file_support BOOLEAN DEFAULT false;
        RAISE NOTICE 'Added column ai_authoring_sessions.multi_file_support';
    END IF;
END $$;

COMMENT ON COLUMN ai_pipeline.ai_authoring_sessions.target_audience IS 'Target audience settings: level, background, learning goals';
COMMENT ON COLUMN ai_pipeline.ai_authoring_sessions.exam_integration IS 'Exam integration settings: exam type, years analyzed, focus areas';
COMMENT ON COLUMN ai_pipeline.ai_authoring_sessions.multi_file_support IS 'Session uses multi-file analysis (e.g., 7 years of exams)';

-- Extend ai_session_snapshots for better UX
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'ai_session_snapshots' AND column_name = 'user_friendly_description') THEN
        ALTER TABLE ai_pipeline.ai_session_snapshots
            ADD COLUMN user_friendly_description TEXT;
        RAISE NOTICE 'Added column ai_session_snapshots.user_friendly_description';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'ai_session_snapshots' AND column_name = 'visual_preview_url') THEN
        ALTER TABLE ai_pipeline.ai_session_snapshots
            ADD COLUMN visual_preview_url TEXT;
        RAISE NOTICE 'Added column ai_session_snapshots.visual_preview_url';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'ai_session_snapshots' AND column_name = 'affected_chapters') THEN
        ALTER TABLE ai_pipeline.ai_session_snapshots
            ADD COLUMN affected_chapters INT[] DEFAULT '{}';
        RAISE NOTICE 'Added column ai_session_snapshots.affected_chapters';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'ai_session_snapshots' AND column_name = 'affected_lessons') THEN
        ALTER TABLE ai_pipeline.ai_session_snapshots
            ADD COLUMN affected_lessons INT[] DEFAULT '{}';
        RAISE NOTICE 'Added column ai_session_snapshots.affected_lessons';
    END IF;
END $$;

COMMENT ON COLUMN ai_pipeline.ai_session_snapshots.user_friendly_description IS 'Human-readable snapshot description: "Kapitel 3 wurde aufgeteilt"';
COMMENT ON COLUMN ai_pipeline.ai_session_snapshots.visual_preview_url IS 'Optional visual preview for snapshot (thumbnail)';

-- ============================================================================
-- Triggers for updated_at timestamps
-- ============================================================================
DROP TRIGGER IF EXISTS update_authoring_generations_updated_at ON ai_pipeline.authoring_generations;
CREATE TRIGGER update_authoring_generations_updated_at BEFORE UPDATE ON ai_pipeline.authoring_generations
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_authoring_journey_updated_at ON ai_pipeline.authoring_user_journey;
CREATE TRIGGER update_authoring_journey_updated_at BEFORE UPDATE ON ai_pipeline.authoring_user_journey
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- EDIT MODE EXTENSIONS (2025-01-07): Support für bestehende Kurse bearbeiten
-- ============================================================================

-- Extend ai_authoring_sessions for edit mode support
DO $$
BEGIN
    -- Session Type (new_course, edit_existing, extend_existing)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'ai_authoring_sessions' AND column_name = 'session_type') THEN
        ALTER TABLE ai_pipeline.ai_authoring_sessions
            ADD COLUMN session_type VARCHAR(50) DEFAULT 'new_course'
                CHECK (session_type IN ('new_course', 'edit_existing', 'extend_existing'));
        RAISE NOTICE 'Added column ai_authoring_sessions.session_type';
    END IF;

    -- Original course data (when loading existing course)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'ai_authoring_sessions' AND column_name = 'original_course_data') THEN
        ALTER TABLE ai_pipeline.ai_authoring_sessions
            ADD COLUMN original_course_data JSONB DEFAULT '{}';
        RAISE NOTICE 'Added column ai_authoring_sessions.original_course_data';
    END IF;

    -- When was course loaded? (for conflict detection)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'ai_authoring_sessions' AND column_name = 'course_loaded_at') THEN
        ALTER TABLE ai_pipeline.ai_authoring_sessions
            ADD COLUMN course_loaded_at TIMESTAMPTZ;
        RAISE NOTICE 'Added column ai_authoring_sessions.course_loaded_at';
    END IF;

    -- Course version at load time (for optimistic locking)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'ai_authoring_sessions' AND column_name = 'course_version_at_load') THEN
        ALTER TABLE ai_pipeline.ai_authoring_sessions
            ADD COLUMN course_version_at_load INTEGER;
        RAISE NOTICE 'Added column ai_authoring_sessions.course_version_at_load';
    END IF;
END $$;

COMMENT ON COLUMN ai_pipeline.ai_authoring_sessions.session_type IS 'Session mode: new_course (from scratch), edit_existing (modify course), extend_existing (add chapters)';
COMMENT ON COLUMN ai_pipeline.ai_authoring_sessions.original_course_data IS 'Original course state when loaded (full snapshot for diff & conflict detection)';
COMMENT ON COLUMN ai_pipeline.ai_authoring_sessions.course_loaded_at IS 'Timestamp when course was loaded into session (conflict detection)';
COMMENT ON COLUMN ai_pipeline.ai_authoring_sessions.course_version_at_load IS 'Course version number at load time (optimistic locking)';

-- ============================================================================
-- TABLE: authoring_changes
-- Description: Track all changes made during authoring session (edit mode)
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_pipeline.authoring_changes (
    change_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES ai_pipeline.ai_authoring_sessions(session_id) ON DELETE CASCADE,

    -- Change type & target
    change_type VARCHAR(50) NOT NULL
        CHECK (change_type IN (
            'chapter_added', 'chapter_edited', 'chapter_deleted', 'chapter_reordered',
            'lesson_added', 'lesson_edited', 'lesson_deleted', 'lesson_reordered',
            'method_added', 'method_edited', 'method_deleted',
            'course_meta_edited', 'course_settings_edited'
        )),

    -- Entity reference
    entity_type VARCHAR(50) NOT NULL
        CHECK (entity_type IN ('course', 'chapter', 'lesson', 'method')),
    entity_id UUID,  -- NULL for new entities (not yet in DB)
    temp_id VARCHAR(100),  -- Temporary ID in draft_structure before finalization

    -- Change details
    before_data JSONB,  -- State before change (NULL for additions)
    after_data JSONB,   -- State after change (NULL for deletions)
    diff JSONB DEFAULT '{}',  -- Structured diff for UI display

    -- User context
    user_action TEXT,  -- Human-readable: "Kapitel 3 umbenannt in 'Advanced Topics'"
    changed_by UUID REFERENCES core.users(user_id) ON DELETE SET NULL,

    -- Sequencing (for undo/redo)
    sequence_number INT NOT NULL,
    is_reverted BOOLEAN DEFAULT false,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_authoring_changes_session ON ai_pipeline.authoring_changes(session_id, sequence_number);
CREATE INDEX IF NOT EXISTS idx_authoring_changes_type ON ai_pipeline.authoring_changes(change_type);
CREATE INDEX IF NOT EXISTS idx_authoring_changes_entity ON ai_pipeline.authoring_changes(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_authoring_changes_not_reverted ON ai_pipeline.authoring_changes(session_id)
    WHERE is_reverted = false;

COMMENT ON TABLE ai_pipeline.authoring_changes IS 'Detailed change tracking for edit mode (enables undo/redo, conflict detection, changelog)';
COMMENT ON COLUMN ai_pipeline.authoring_changes.before_data IS 'Complete entity state before change (NULL for additions)';
COMMENT ON COLUMN ai_pipeline.authoring_changes.after_data IS 'Complete entity state after change (NULL for deletions)';
COMMENT ON COLUMN ai_pipeline.authoring_changes.diff IS 'Structured diff for UI: {"title": {"old": "...", "new": "..."}}';
COMMENT ON COLUMN ai_pipeline.authoring_changes.sequence_number IS 'Sequential order for undo/redo functionality';

-- ============================================================================
-- TABLE: authoring_finalization
-- Description: Merge strategy, conflict resolution, and finalization results
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_pipeline.authoring_finalization (
    finalization_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES ai_pipeline.ai_authoring_sessions(session_id) ON DELETE CASCADE,

    -- Finalization strategy
    merge_strategy VARCHAR(50) NOT NULL DEFAULT 'safe_merge'
        CHECK (merge_strategy IN ('safe_merge', 'force_overwrite', 'create_new_version', 'interactive')),

    -- Pre-flight checks
    has_conflicts BOOLEAN DEFAULT false,
    conflicts JSONB DEFAULT '[]',  -- [{"type": "concurrent_edit", "entity": "chapter-123", ...}]
    conflict_resolution JSONB DEFAULT '{}',  -- {"chapter-123": "use_mine"}

    -- What was applied?
    changes_applied JSONB DEFAULT '[]',  -- [{"change_id": "...", "status": "applied"}]
    changes_skipped JSONB DEFAULT '[]',  -- [{"change_id": "...", "reason": "conflict"}]

    -- Results (IDs of affected entities)
    created_course_id UUID REFERENCES courses.courses(course_id) ON DELETE SET NULL,
    created_chapter_ids UUID[] DEFAULT '{}',
    created_lesson_ids UUID[] DEFAULT '{}',
    created_method_ids UUID[] DEFAULT '{}',
    updated_chapter_ids UUID[] DEFAULT '{}',
    updated_lesson_ids UUID[] DEFAULT '{}',
    updated_method_ids UUID[] DEFAULT '{}',
    deleted_chapter_ids UUID[] DEFAULT '{}',
    deleted_lesson_ids UUID[] DEFAULT '{}',
    deleted_method_ids UUID[] DEFAULT '{}',

    -- Statistics
    total_changes INT DEFAULT 0,
    successful_changes INT DEFAULT 0,
    failed_changes INT DEFAULT 0,

    -- Rollback support
    rollback_data JSONB,  -- Snapshot for rollback if needed
    rollback_at TIMESTAMPTZ,

    -- Status
    status VARCHAR(50) DEFAULT 'pending'
        CHECK (status IN ('pending', 'pre_check', 'in_progress', 'completed', 'failed', 'rolled_back', 'partially_completed')),
    error_message TEXT,
    warnings JSONB DEFAULT '[]',

    -- Timing
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_finalization_session ON ai_pipeline.authoring_finalization(session_id);
CREATE INDEX IF NOT EXISTS idx_finalization_course ON ai_pipeline.authoring_finalization(created_course_id);
CREATE INDEX IF NOT EXISTS idx_finalization_status ON ai_pipeline.authoring_finalization(status);
CREATE INDEX IF NOT EXISTS idx_finalization_conflicts ON ai_pipeline.authoring_finalization(has_conflicts)
    WHERE has_conflicts = true;

COMMENT ON TABLE ai_pipeline.authoring_finalization IS 'Finalization process: merge changes back to DB with conflict detection & resolution';
COMMENT ON COLUMN ai_pipeline.authoring_finalization.merge_strategy IS 'safe_merge: detect conflicts, force_overwrite: ignore conflicts, create_new_version: create course copy, interactive: ask user';
COMMENT ON COLUMN ai_pipeline.authoring_finalization.conflicts IS 'Detected conflicts: concurrent edits, deleted entities, validation errors';
COMMENT ON COLUMN ai_pipeline.authoring_finalization.conflict_resolution IS 'User decisions for each conflict: use_mine, use_theirs, merge_both';
COMMENT ON COLUMN ai_pipeline.authoring_finalization.rollback_data IS 'DB snapshot before finalization (for rollback if something fails)';

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON ai_pipeline.authoring_changes TO lernsystem;
GRANT SELECT, INSERT, UPDATE, DELETE ON ai_pipeline.authoring_finalization TO lernsystem;

-- ============================================================================
-- End of Migration: 055_ai_authoring_studio.sql
-- ============================================================================
