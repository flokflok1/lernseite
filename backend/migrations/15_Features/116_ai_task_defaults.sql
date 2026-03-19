-- Task-specific AI model defaults
-- Each AI task category can have its own default model
CREATE TABLE IF NOT EXISTS ai_pipeline.ai_task_defaults (
    category VARCHAR(50) PRIMARY KEY,
    provider_id INTEGER REFERENCES ai_pipeline.ai_providers(provider_id),
    model_name VARCHAR(100) NOT NULL,
    display_name VARCHAR(200) NOT NULL DEFAULT '',
    description TEXT DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Seed initial categories with sensible defaults
-- All initially point to the current global default
INSERT INTO ai_pipeline.ai_task_defaults (category, provider_id, model_name, display_name, description)
SELECT 'default', p.provider_id, 'gemini-3.1-pro-preview', 'Standard', 'Globaler Fallback für alle Tasks'
FROM ai_pipeline.ai_providers p WHERE p.name = 'google'
ON CONFLICT DO NOTHING;

INSERT INTO ai_pipeline.ai_task_defaults (category, provider_id, model_name, display_name, description)
SELECT 'grading', p.provider_id, 'gemini-3.1-flash-lite-preview', 'Bewertung', 'Freitext-Antworten bewerten'
FROM ai_pipeline.ai_providers p WHERE p.name = 'google'
ON CONFLICT DO NOTHING;

INSERT INTO ai_pipeline.ai_task_defaults (category, provider_id, model_name, display_name, description)
SELECT 'templates', p.provider_id, 'gemini-3.1-flash-lite-preview', 'Vorlagen', 'Lösungsvorlagen generieren'
FROM ai_pipeline.ai_providers p WHERE p.name = 'google'
ON CONFLICT DO NOTHING;

INSERT INTO ai_pipeline.ai_task_defaults (category, provider_id, model_name, display_name, description)
SELECT 'vision', p.provider_id, 'gemini-3.1-pro-preview', 'Analyse (Vision)', 'Prüfungs-PDFs analysieren'
FROM ai_pipeline.ai_providers p WHERE p.name = 'google'
ON CONFLICT DO NOTHING;

INSERT INTO ai_pipeline.ai_task_defaults (category, provider_id, model_name, display_name, description)
SELECT 'content', p.provider_id, 'gemini-3.1-pro-preview', 'Kurs-Erstellung', 'Kurse und Lektionen generieren'
FROM ai_pipeline.ai_providers p WHERE p.name = 'google'
ON CONFLICT DO NOTHING;

INSERT INTO ai_pipeline.ai_task_defaults (category, provider_id, model_name, display_name, description)
SELECT 'tts', p.provider_id, 'tts-1', 'Text-to-Speech', 'Sprachausgabe'
FROM ai_pipeline.ai_providers p WHERE p.name = 'openai'
ON CONFLICT DO NOTHING;

INSERT INTO ai_pipeline.ai_task_defaults (category, provider_id, model_name, display_name, description)
SELECT 'transcription', p.provider_id, 'whisper-1', 'Transkription', 'Sprache-zu-Text'
FROM ai_pipeline.ai_providers p WHERE p.name = 'openai'
ON CONFLICT DO NOTHING;

INSERT INTO ai_pipeline.ai_task_defaults (category, provider_id, model_name, display_name, description)
SELECT 'translation', p.provider_id, 'gemini-2.5-flash', 'Übersetzung', 'i18n-Übersetzungen'
FROM ai_pipeline.ai_providers p WHERE p.name = 'google'
ON CONFLICT DO NOTHING;

INSERT INTO ai_pipeline.ai_task_defaults (category, provider_id, model_name, display_name, description)
SELECT 'tutor', p.provider_id, 'gemini-2.5-flash', 'Tutor', 'NPC Tutor Chat'
FROM ai_pipeline.ai_providers p WHERE p.name = 'google'
ON CONFLICT DO NOTHING;

INSERT INTO ai_pipeline.ai_task_defaults (category, provider_id, model_name, display_name, description)
SELECT 'taxonomy', p.provider_id, 'gemini-3.1-flash-lite-preview', 'Taxonomie', 'Topic-Klassifikation'
FROM ai_pipeline.ai_providers p WHERE p.name = 'google'
ON CONFLICT DO NOTHING;

INSERT INTO ai_pipeline.ai_task_defaults (category, provider_id, model_name, display_name, description)
SELECT 'feedback', p.provider_id, 'gemini-2.5-flash', 'Feedback', 'Dashboard Feedback'
FROM ai_pipeline.ai_providers p WHERE p.name = 'google'
ON CONFLICT DO NOTHING;

COMMENT ON TABLE ai_pipeline.ai_task_defaults IS 'Per-task AI model defaults, configurable via System Settings';
