-- ============================================================================
-- Migration 070: Prompt Templates System
-- ============================================================================
-- Description: Database tables for editable prompt templates
--              Allows admins to customize AI prompts for content generation
--              Supports multiple styles: ADHS, Kurz, Ausfuehrlich, Pruefungsfokus
--
-- Phase: KI-Studio Enhancement
-- Date: 2025-01
-- ============================================================================

-- ============================================================================
-- 1. Prompt Templates Table
-- ============================================================================
-- Stores customizable prompt templates for AI content generation

CREATE TABLE IF NOT EXISTS ai_pipeline.prompt_templates (
    template_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Template identification
    code VARCHAR(100) NOT NULL,              -- Unique code: 'theory_sheet_adhs', 'lesson_steps_short'
    category VARCHAR(50) NOT NULL,           -- 'theory', 'lesson', 'quiz', 'flashcard', 'tutor'
    style VARCHAR(50) NOT NULL DEFAULT 'standard',  -- 'standard', 'adhs', 'short', 'detailed', 'exam_focus'

    -- Display info
    title VARCHAR(255) NOT NULL,             -- "Theorieblatt (ADHS-freundlich)"
    description TEXT,                        -- "Kurze, visuelle Erklaerungen mit Schritt-fuer-Schritt Anleitungen"
    icon VARCHAR(50),                        -- Emoji or icon code

    -- The actual prompt
    system_prompt TEXT NOT NULL,             -- System message for AI
    user_prompt_template TEXT NOT NULL,      -- User message template with {{variables}}

    -- AI Configuration
    model VARCHAR(100) DEFAULT 'gpt-4o-mini',
    provider VARCHAR(50) DEFAULT 'openai',
    temperature DECIMAL(3,2) DEFAULT 0.7,
    max_tokens INTEGER DEFAULT 4000,

    -- Variables definition (JSON)
    -- Example: [{"name": "chapter_title", "required": true, "description": "Kapiteltitel"}]
    variables JSONB DEFAULT '[]'::jsonb,

    -- Output format
    output_format VARCHAR(50) DEFAULT 'json',  -- 'json', 'markdown', 'html', 'text'
    output_schema JSONB,                        -- Expected JSON schema for validation

    -- TTS Settings
    tts_enabled BOOLEAN DEFAULT false,
    tts_voice VARCHAR(50) DEFAULT 'alloy',     -- OpenAI voice: alloy, echo, fable, onyx, nova, shimmer
    tts_model VARCHAR(50) DEFAULT 'tts-1',     -- tts-1 or tts-1-hd
    tts_speed DECIMAL(3,2) DEFAULT 1.0,        -- 0.25 to 4.0

    -- Metadata
    language VARCHAR(10) DEFAULT 'de',
    target_audience VARCHAR(255),              -- "Fachinformatiker Systemintegration"
    difficulty_level VARCHAR(50),              -- "beginner", "intermediate", "advanced", "exam"

    -- Learning method association (optional)
    lm_type INTEGER,                           -- 0-25 Content-LMs, NULL for general templates

    -- Status
    is_active BOOLEAN DEFAULT true,
    is_default BOOLEAN DEFAULT false,          -- Default template for this category+style
    is_system BOOLEAN DEFAULT false,           -- System template (cannot be deleted)

    -- Versioning
    version INTEGER DEFAULT 1,
    parent_template_id UUID REFERENCES ai_pipeline.prompt_templates(template_id),  -- For version history

    -- Audit
    created_by UUID REFERENCES core.users(user_id),
    updated_by UUID REFERENCES core.users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    CONSTRAINT unique_template_code UNIQUE (code),
    CONSTRAINT valid_temperature CHECK (temperature >= 0 AND temperature <= 2),
    CONSTRAINT valid_tts_speed CHECK (tts_speed >= 0.25 AND tts_speed <= 4.0),
    CONSTRAINT valid_lm_type CHECK (lm_type IS NULL OR (lm_type >= 0 AND lm_type <= 32))
);

-- Indexes
CREATE INDEX idx_prompt_templates_category ON ai_pipeline.prompt_templates (category);
CREATE INDEX idx_prompt_templates_style ON ai_pipeline.prompt_templates (style);
CREATE INDEX idx_prompt_templates_category_style ON ai_pipeline.prompt_templates (category, style);
CREATE INDEX idx_prompt_templates_lm_type ON ai_pipeline.prompt_templates (lm_type) WHERE lm_type IS NOT NULL;
CREATE INDEX idx_prompt_templates_active ON ai_pipeline.prompt_templates (is_active) WHERE is_active = true;
CREATE INDEX idx_prompt_templates_default ON ai_pipeline.prompt_templates (category, style, is_default) WHERE is_default = true;

-- ============================================================================
-- 2. Prompt Template Usage Tracking
-- ============================================================================
-- Tracks usage statistics for each template

CREATE TABLE IF NOT EXISTS ai_pipeline.prompt_template_usage (
    usage_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES ai_pipeline.prompt_templates(template_id) ON DELETE CASCADE,
    user_id UUID REFERENCES core.users(user_id),

    -- What was generated
    content_type VARCHAR(50) NOT NULL,         -- 'chapter_theory', 'lesson_steps', 'quiz'
    content_id UUID,                            -- Reference to generated content

    -- AI Response metrics
    tokens_input INTEGER,
    tokens_output INTEGER,
    tokens_total INTEGER,
    cost_eur DECIMAL(10,6),
    response_time_ms INTEGER,

    -- TTS metrics (if generated)
    tts_generated BOOLEAN DEFAULT false,
    tts_duration_seconds DECIMAL(10,2),
    tts_cost_eur DECIMAL(10,6),
    tts_audio_url TEXT,

    -- Quality feedback
    user_rating INTEGER CHECK (user_rating >= 1 AND user_rating <= 5),
    user_feedback TEXT,

    -- Context
    context_data JSONB,                        -- Variables used

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_prompt_usage_template ON ai_pipeline.prompt_template_usage (template_id);
CREATE INDEX idx_prompt_usage_user ON ai_pipeline.prompt_template_usage (user_id);
CREATE INDEX idx_prompt_usage_created ON ai_pipeline.prompt_template_usage (created_at);

-- ============================================================================
-- 3. Insert Default Prompt Templates
-- ============================================================================
-- MOVED TO: 00_Seeds/13_prompt_templates.sql
--
-- Default templates created via seed file:
-- - theory_sheet_adhs (ADHS-freundlich)
-- - theory_sheet_detailed (Ausfuehrlich)
-- - theory_sheet_short (Kurz & Knapp)
-- - theory_sheet_exam (Pruefungsfokus)
-- - lesson_steps_adhs (Lektions-Erklaerung)

-- ============================================================================
-- 4. Generated Content with TTS
-- ============================================================================
-- Stores generated content and associated TTS audio

CREATE TABLE IF NOT EXISTS ai_pipeline.generated_theory_sheets (
    sheet_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- References
    chapter_id UUID REFERENCES courses.chapters(chapter_id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses.courses(course_id) ON DELETE CASCADE,
    template_id UUID REFERENCES ai_pipeline.prompt_templates(template_id),

    -- Content
    style VARCHAR(50) NOT NULL,                -- Which style was used
    content JSONB NOT NULL,                    -- The generated JSON content
    content_html TEXT,                         -- Rendered HTML version
    content_markdown TEXT,                     -- Markdown version

    -- TTS Audio
    has_audio BOOLEAN DEFAULT false,
    audio_url TEXT,                            -- URL to audio file
    audio_duration_seconds DECIMAL(10,2),
    audio_voice VARCHAR(50),
    audio_generated_at TIMESTAMP WITH TIME ZONE,

    -- Generation info
    tokens_used INTEGER,
    cost_eur DECIMAL(10,6),
    generation_time_ms INTEGER,

    -- Status
    is_published BOOLEAN DEFAULT false,

    -- Audit
    created_by UUID REFERENCES core.users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_theory_sheets_chapter ON ai_pipeline.generated_theory_sheets (chapter_id);
CREATE INDEX idx_theory_sheets_course ON ai_pipeline.generated_theory_sheets (course_id);
CREATE INDEX idx_theory_sheets_style ON ai_pipeline.generated_theory_sheets (style);
CREATE INDEX idx_theory_sheets_has_audio ON ai_pipeline.generated_theory_sheets (has_audio) WHERE has_audio = true;

-- ============================================================================
-- 5. Update Trigger
-- ============================================================================

CREATE OR REPLACE FUNCTION update_prompt_templates_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_prompt_templates_updated
    BEFORE UPDATE ON ai_pipeline.prompt_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_prompt_templates_timestamp();

CREATE TRIGGER trigger_theory_sheets_updated
    BEFORE UPDATE ON ai_pipeline.generated_theory_sheets
    FOR EACH ROW
    EXECUTE FUNCTION update_prompt_templates_timestamp();

-- ============================================================================
-- Migration complete
-- ============================================================================
-- New tables: prompt_templates, prompt_template_usage, generated_theory_sheets
-- Default templates: 4 theory styles (ADHS, detailed, short, exam_focus)
--                   1 lesson steps style (ADHS)
