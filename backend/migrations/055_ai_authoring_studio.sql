-- ============================================================================
-- Migration: 055_ai_authoring_studio.sql
-- Description: KI-Authoring-Studio tables for AI-powered chapter/lesson creation
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-12-02
-- ============================================================================

-- ============================================================================
-- TABLE: ai_authoring_sessions
-- Description: Main sessions for KI-Authoring-Studio workflow
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_authoring_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses(course_id) ON DELETE CASCADE,
    chapter_id UUID REFERENCES chapters(chapter_id) ON DELETE SET NULL,

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

CREATE INDEX IF NOT EXISTS idx_ai_authoring_sessions_user ON ai_authoring_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_authoring_sessions_course ON ai_authoring_sessions(course_id);
CREATE INDEX IF NOT EXISTS idx_ai_authoring_sessions_chapter ON ai_authoring_sessions(chapter_id);
CREATE INDEX IF NOT EXISTS idx_ai_authoring_sessions_status ON ai_authoring_sessions(status);
CREATE INDEX IF NOT EXISTS idx_ai_authoring_sessions_activity ON ai_authoring_sessions(last_activity_at DESC);

COMMENT ON TABLE ai_authoring_sessions IS 'KI-Authoring-Studio sessions for AI-assisted content creation';
COMMENT ON COLUMN ai_authoring_sessions.source_data IS 'Source content data (PDF text, URL content, etc.)';
COMMENT ON COLUMN ai_authoring_sessions.generated_theory IS 'AI-generated theory content for chapter';
COMMENT ON COLUMN ai_authoring_sessions.generated_lessons IS 'Array of AI-generated lesson objects';
COMMENT ON COLUMN ai_authoring_sessions.generated_methods IS 'Array of AI-generated learning method objects';

-- ============================================================================
-- TABLE: ai_session_snapshots
-- Description: Undo/Redo snapshots for session state
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_session_snapshots (
    snapshot_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES ai_authoring_sessions(session_id) ON DELETE CASCADE,

    -- Snapshot content
    snapshot_data JSONB NOT NULL,
    description VARCHAR(255),

    -- Position in history
    sequence_number INTEGER NOT NULL,
    is_current BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ai_session_snapshots_session ON ai_session_snapshots(session_id);
CREATE INDEX IF NOT EXISTS idx_ai_session_snapshots_sequence ON ai_session_snapshots(session_id, sequence_number);
CREATE INDEX IF NOT EXISTS idx_ai_session_snapshots_current ON ai_session_snapshots(session_id) WHERE is_current = TRUE;

COMMENT ON TABLE ai_session_snapshots IS 'State snapshots for undo/redo functionality in authoring sessions';
COMMENT ON COLUMN ai_session_snapshots.sequence_number IS 'Order number for history navigation';

-- ============================================================================
-- TABLE: ai_generation_variants
-- Description: Multiple AI-generated variants for comparison
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_generation_variants (
    variant_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES ai_authoring_sessions(session_id) ON DELETE CASCADE,

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

CREATE INDEX IF NOT EXISTS idx_ai_generation_variants_session ON ai_generation_variants(session_id);
CREATE INDEX IF NOT EXISTS idx_ai_generation_variants_type ON ai_generation_variants(variant_type);
CREATE INDEX IF NOT EXISTS idx_ai_generation_variants_selected ON ai_generation_variants(session_id) WHERE is_selected = TRUE;

COMMENT ON TABLE ai_generation_variants IS 'Multiple AI-generated content variants for user comparison';
COMMENT ON COLUMN ai_generation_variants.variant_type IS 'Type of content: theory, lesson, method, quiz, summary, full_chapter';

-- ============================================================================
-- TABLE: ai_studio_analytics
-- Description: Analytics events for KI-Authoring-Studio usage
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_studio_analytics (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES ai_authoring_sessions(session_id) ON DELETE SET NULL,
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,

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

CREATE INDEX IF NOT EXISTS idx_ai_studio_analytics_session ON ai_studio_analytics(session_id);
CREATE INDEX IF NOT EXISTS idx_ai_studio_analytics_user ON ai_studio_analytics(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_studio_analytics_type ON ai_studio_analytics(event_type);
CREATE INDEX IF NOT EXISTS idx_ai_studio_analytics_created ON ai_studio_analytics(created_at DESC);

COMMENT ON TABLE ai_studio_analytics IS 'Usage analytics for KI-Authoring-Studio';

-- ============================================================================
-- TABLE: pdf_cache
-- Description: Cached PDF analysis results for reuse
-- ============================================================================
CREATE TABLE IF NOT EXISTS pdf_cache (
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

CREATE INDEX IF NOT EXISTS idx_pdf_cache_hash ON pdf_cache(file_hash);
CREATE INDEX IF NOT EXISTS idx_pdf_cache_expires ON pdf_cache(expires_at) WHERE expires_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_pdf_cache_accessed ON pdf_cache(last_accessed_at DESC);

COMMENT ON TABLE pdf_cache IS 'Cached PDF extraction results to avoid redundant processing';
COMMENT ON COLUMN pdf_cache.file_hash IS 'SHA-256 hash of file content for deduplication';
COMMENT ON COLUMN pdf_cache.structure_analysis IS 'AI-analyzed structure (headings, sections, key topics)';

-- ============================================================================
-- ALTER TABLE: chapters - Add AI authoring metadata
-- ============================================================================
DO $$
BEGIN
    -- Add ai_generated flag
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'chapters' AND column_name = 'ai_generated') THEN
        ALTER TABLE chapters ADD COLUMN ai_generated BOOLEAN DEFAULT FALSE;
        RAISE NOTICE 'Added column chapters.ai_generated';
    END IF;

    -- Add source session reference
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'chapters' AND column_name = 'ai_session_id') THEN
        ALTER TABLE chapters ADD COLUMN ai_session_id UUID REFERENCES ai_authoring_sessions(session_id) ON DELETE SET NULL;
        RAISE NOTICE 'Added column chapters.ai_session_id';
    END IF;

    -- Add generation metadata
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'chapters' AND column_name = 'ai_metadata') THEN
        ALTER TABLE chapters ADD COLUMN ai_metadata JSONB DEFAULT '{}';
        RAISE NOTICE 'Added column chapters.ai_metadata';
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_chapters_ai_generated ON chapters(ai_generated) WHERE ai_generated = TRUE;
CREATE INDEX IF NOT EXISTS idx_chapters_ai_session ON chapters(ai_session_id) WHERE ai_session_id IS NOT NULL;

COMMENT ON COLUMN chapters.ai_generated IS 'Indicates if chapter was created via KI-Authoring-Studio';
COMMENT ON COLUMN chapters.ai_session_id IS 'Reference to the authoring session that created this chapter';
COMMENT ON COLUMN chapters.ai_metadata IS 'AI generation metadata (model used, prompts, timestamps)';

-- ============================================================================
-- TABLE: ai_authoring_templates
-- Description: Reusable templates for AI content generation
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_authoring_templates (
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
    created_by UUID REFERENCES users(user_id) ON DELETE SET NULL,

    -- Stats
    usage_count INTEGER DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ai_authoring_templates_key ON ai_authoring_templates(template_key);
CREATE INDEX IF NOT EXISTS idx_ai_authoring_templates_category ON ai_authoring_templates(category);
CREATE INDEX IF NOT EXISTS idx_ai_authoring_templates_active ON ai_authoring_templates(is_active) WHERE is_active = TRUE;

COMMENT ON TABLE ai_authoring_templates IS 'Reusable templates for KI-Authoring-Studio workflows';
COMMENT ON COLUMN ai_authoring_templates.template_config IS 'Template configuration: steps, default prompts, AI settings';

-- ============================================================================
-- Insert default templates
-- ============================================================================
INSERT INTO ai_authoring_templates (template_key, template_name, category, description, is_system, template_config)
VALUES
    ('standard_chapter', 'Standard-Kapitel', 'chapter', 'Standardvorlage für Kapitel mit Theorie und Lernmethoden', TRUE, '{
        "steps": ["source_selection", "theory_generation", "lesson_generation", "method_generation", "review"],
        "default_methods": [0, 1, 2, 4],
        "theory_sections": ["introduction", "main_content", "examples", "summary"],
        "ai_settings": {
            "temperature": 0.7,
            "style": "educational"
        }
    }'),
    ('quiz_focused', 'Quiz-Fokus', 'chapter', 'Kapitel mit Schwerpunkt auf Prüfungsvorbereitung', TRUE, '{
        "steps": ["source_selection", "theory_generation", "quiz_generation", "review"],
        "default_methods": [1, 4, 8, 13],
        "quiz_count": 10,
        "ai_settings": {
            "temperature": 0.5,
            "style": "assessment"
        }
    }'),
    ('vocabulary_chapter', 'Vokabel-Kapitel', 'language', 'Sprachkapitel mit Vokabeltrainer', TRUE, '{
        "steps": ["source_selection", "vocabulary_extraction", "method_generation", "review"],
        "default_methods": [32, 1, 2],
        "language_pair": true,
        "ai_settings": {
            "temperature": 0.6,
            "style": "language_learning"
        }
    }'),
    ('practical_skills', 'Praxis-Kapitel', 'practical', 'Kapitel mit praktischen Übungen und Fallstudien', TRUE, '{
        "steps": ["source_selection", "theory_generation", "case_study_generation", "method_generation", "review"],
        "default_methods": [3, 6, 9, 14],
        "include_case_studies": true,
        "ai_settings": {
            "temperature": 0.8,
            "style": "practical"
        }
    }')
ON CONFLICT (template_key) DO NOTHING;

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- ============================================================================
CREATE TRIGGER update_ai_authoring_sessions_updated_at BEFORE UPDATE ON ai_authoring_sessions
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ai_authoring_templates_updated_at BEFORE UPDATE ON ai_authoring_templates
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- End of Migration: 055_ai_authoring_studio.sql
-- ============================================================================
