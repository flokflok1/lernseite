-- ============================================================================
-- Migration 068: Course AI Settings
--
-- Kurs-spezifische KI-Modell-Konfiguration.
-- Ermöglicht pro Kurs die Auswahl von Chat-, Exam- und Image-Modellen.
-- Fallback auf System-Defaults wenn nicht konfiguriert.
--
-- Phase: KI-Studio Pro - Kurs-spezifische Einstellungen
-- ============================================================================

-- Course AI Settings Table
CREATE TABLE IF NOT EXISTS courses.course_ai_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID NOT NULL REFERENCES courses.courses(course_id) ON DELETE CASCADE,

    -- Profile reference (merged from 076)
    profile_key VARCHAR(50) REFERENCES ai_pipeline.ai_model_profiles(key) ON DELETE SET NULL,

    -- Model selections (nullable = use system default)
    chat_model_id VARCHAR(100),        -- z.B. "gpt-4o", "claude-3-5-sonnet"
    reasoning_model_id VARCHAR(100),   -- z.B. "o3", "deepseek-reasoner" (was exam_model)
    image_model_id VARCHAR(100),       -- z.B. "gpt-image-1", "dall-e-3"
    audio_model_id VARCHAR(100),       -- z.B. "tts-1-hd", "nova" (was tts_model)
    realtime_model_id VARCHAR(100),    -- z.B. "gpt-4o-realtime"
    embedding_model_id VARCHAR(100),   -- z.B. "text-embedding-3-large"

    -- Additional settings as JSONB for extensibility
    additional_settings JSONB DEFAULT '{}'::jsonb,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Each course has only one settings entry
    CONSTRAINT unique_course_ai_settings UNIQUE (course_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_course_ai_settings_course
    ON courses.course_ai_settings (course_id);
CREATE INDEX IF NOT EXISTS idx_course_ai_settings_profile_key
    ON courses.course_ai_settings (profile_key);

-- Updated_at trigger
CREATE OR REPLACE FUNCTION update_course_ai_settings_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_course_ai_settings_updated ON courses.course_ai_settings ;
CREATE TRIGGER trg_course_ai_settings_updated
    BEFORE UPDATE ON courses.course_ai_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_course_ai_settings_timestamp();

-- Comment
COMMENT ON TABLE courses.course_ai_settings IS
'Kurs-spezifische KI-Modell-Konfiguration.

Felder:
- profile_key: Referenz auf ai_model_profiles.key
- chat_model_id: Modell für Chat/Theorie-Generierung
- reasoning_model_id: Modell für Prüfungen/Reasoning (o3, o1, etc.)
- image_model_id: Modell für Bildgenerierung
- audio_model_id: Modell für TTS/STT
- realtime_model_id: Modell für Realtime-Audio
- embedding_model_id: Modell für Embeddings

NULL-Werte bedeuten: System-Default verwenden.
Beim Anwenden eines Profils werden alle Model-IDs überschrieben.';

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON courses.course_ai_settings TO lernsystem;
