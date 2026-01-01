-- ============================================================================
-- Migration 049: Course AI Settings
--
-- Kurs-spezifische KI-Modell-Konfiguration.
-- Ermöglicht pro Kurs die Auswahl von Chat-, Exam- und Image-Modellen.
-- Fallback auf System-Defaults wenn nicht konfiguriert.
--
-- Phase: KI-Studio Pro - Kurs-spezifische Einstellungen
-- ============================================================================

-- Course AI Settings Table
CREATE TABLE IF NOT EXISTS course_ai_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,

    -- Model selections (nullable = use system default)
    chat_model VARCHAR(100),           -- z.B. "gpt-4o", "claude-3-5-sonnet"
    exam_model VARCHAR(100),           -- z.B. "o3", "deepseek-reasoner"
    image_model VARCHAR(100),          -- z.B. "gpt-image-1", "dall-e-3"
    tts_model VARCHAR(100),            -- z.B. "tts-1-hd", "nova"

    -- Optional profile name for quick selection
    profile_name VARCHAR(100),         -- z.B. "AP1 FISI Standard", "Mathe Intensiv"

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
    ON course_ai_settings(course_id);

-- Updated_at trigger
CREATE OR REPLACE FUNCTION update_course_ai_settings_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_course_ai_settings_updated ON course_ai_settings;
CREATE TRIGGER trg_course_ai_settings_updated
    BEFORE UPDATE ON course_ai_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_course_ai_settings_timestamp();

-- Comment
COMMENT ON TABLE course_ai_settings IS
'Kurs-spezifische KI-Modell-Konfiguration.

Felder:
- chat_model: Modell für Chat/Theorie-Generierung (z.B. gpt-4o, claude-3-5-sonnet)
- exam_model: Modell für Prüfungen/Reasoning (z.B. o3, deepseek-reasoner)
- image_model: Modell für Bildgenerierung (z.B. gpt-image-1, dall-e-3)
- tts_model: Modell für Text-to-Speech (z.B. tts-1-hd)
- profile_name: Optionaler Name für Schnellauswahl

NULL-Werte bedeuten: System-Default verwenden.
additional_settings: JSONB für zukünftige Erweiterungen.';

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON course_ai_settings TO lernsystem;
