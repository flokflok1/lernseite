-- ============================================================================
-- Migration 051: AI Model Profiles (Globale KI-Profile)
--
-- Globale KI-Profile definieren Sets von Modellen pro Kategorie.
-- Profile werden systemweit verwaltet und können pro Kurs angewendet werden.
--
-- Kategorien: chat, reasoning, image, audio, realtime, embedding
-- Profile: Standard, Qualität, Sparsam, Lokal
--
-- Phase: KI-Studio Pro - Globale KI-Einstellungen
-- ============================================================================

-- AI Model Profiles Table
CREATE TABLE IF NOT EXISTS ai_model_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Eindeutiger Schlüssel für Referenzierung
    key VARCHAR(50) NOT NULL UNIQUE,

    -- Anzeigename und Beschreibung
    name VARCHAR(100) NOT NULL,
    description TEXT,

    -- Modell-IDs pro Kategorie (verweisen auf ai_models.model_id)
    chat_model_id VARCHAR(100),           -- z.B. "gpt-4o"
    reasoning_model_id VARCHAR(100),      -- z.B. "o3", "o1"
    image_model_id VARCHAR(100),          -- z.B. "gpt-image-1", "dall-e-3"
    audio_model_id VARCHAR(100),          -- z.B. "tts-1-hd", "whisper-1"
    realtime_model_id VARCHAR(100),       -- z.B. "gpt-4o-realtime"
    embedding_model_id VARCHAR(100),      -- z.B. "text-embedding-3-large"

    -- Standard-Profil Flag (nur eines kann true sein)
    is_default BOOLEAN DEFAULT FALSE,

    -- Aktiv-Flag
    is_active BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_ai_model_profiles_key ON ai_model_profiles(key);
CREATE INDEX IF NOT EXISTS idx_ai_model_profiles_default ON ai_model_profiles(is_default) WHERE is_default = TRUE;

-- Ensure only one default profile
CREATE UNIQUE INDEX IF NOT EXISTS idx_ai_model_profiles_single_default
    ON ai_model_profiles(is_default) WHERE is_default = TRUE;

-- Updated_at Trigger
CREATE OR REPLACE FUNCTION update_ai_model_profiles_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_ai_model_profiles_updated ON ai_model_profiles;
CREATE TRIGGER trg_ai_model_profiles_updated
    BEFORE UPDATE ON ai_model_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_ai_model_profiles_timestamp();

-- Insert Default Profiles
INSERT INTO ai_model_profiles (key, name, description, chat_model_id, reasoning_model_id, image_model_id, audio_model_id, realtime_model_id, embedding_model_id, is_default) VALUES
(
    'standard',
    'Standard',
    'Ausgewogene Balance zwischen Qualität und Kosten. Empfohlen für die meisten Anwendungsfälle.',
    'gpt-4o-mini',
    'gpt-4o',
    'dall-e-3',
    'tts-1',
    'gpt-4o-realtime-preview',
    'text-embedding-3-small',
    TRUE
),
(
    'quality',
    'Qualität',
    'Beste verfügbare Modelle für höchste Qualität. Höhere Kosten, aber optimale Ergebnisse.',
    'gpt-4o',
    'o3',
    'gpt-image-1',
    'tts-1-hd',
    'gpt-4o-realtime-preview',
    'text-embedding-3-large',
    FALSE
),
(
    'budget',
    'Sparsam',
    'Kostengünstige Modelle für einfache Inhalte. Geringere Qualität, aber niedrige Kosten.',
    'gpt-4o-mini',
    'gpt-4o-mini',
    'dall-e-3',
    'tts-1',
    NULL,
    'text-embedding-3-small',
    FALSE
),
(
    'anthropic',
    'Anthropic Claude',
    'Claude-basierte Generierung für alternative Perspektiven und Stilistik.',
    'claude-3-5-sonnet-20241022',
    'claude-3-5-sonnet-20241022',
    'dall-e-3',
    'tts-1-hd',
    NULL,
    'text-embedding-3-large',
    FALSE
)
ON CONFLICT (key) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    chat_model_id = EXCLUDED.chat_model_id,
    reasoning_model_id = EXCLUDED.reasoning_model_id,
    image_model_id = EXCLUDED.image_model_id,
    audio_model_id = EXCLUDED.audio_model_id,
    realtime_model_id = EXCLUDED.realtime_model_id,
    embedding_model_id = EXCLUDED.embedding_model_id,
    updated_at = NOW();

-- Comment
COMMENT ON TABLE ai_model_profiles IS
'Globale KI-Profile für LernsystemX.

Profile definieren Sets von Modellen pro Kategorie:
- chat_model_id: Modell für Chat/Theorie-Generierung
- reasoning_model_id: Modell für Prüfungen/Reasoning (o3, o1, etc.)
- image_model_id: Modell für Bildgenerierung
- audio_model_id: Modell für TTS/STT
- realtime_model_id: Modell für Realtime-Audio
- embedding_model_id: Modell für Embeddings

WICHTIG: Nur Modell-IDs werden gespeichert. Kategorien/Preise
werden aus der globalen Modelleliste (ai_models) gelesen.

is_default: Nur ein Profil kann Standard sein (für neue Kurse).';

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON ai_model_profiles TO lernsystem;

-- Verify
DO $$
DECLARE
    profile_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO profile_count FROM ai_model_profiles;
    IF profile_count >= 4 THEN
        RAISE NOTICE 'ai_model_profiles: % Profile erstellt', profile_count;
    ELSE
        RAISE WARNING 'ai_model_profiles: Nur % Profile erstellt!', profile_count;
    END IF;
END $$;
