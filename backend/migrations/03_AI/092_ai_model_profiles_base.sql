-- ============================================================================
-- Migration: 092_ai_model_profiles_base.sql
-- Description: AI Model Profiles (Globale KI-Profile)
--              Globale KI-Profile definieren Sets von Modellen pro Kategorie.
--              Profile werden systemweit verwaltet und können pro Kurs angewendet werden.
--              Kategorien: chat, reasoning, image, audio, realtime, embedding
--              Profile: Standard, Qualität, Sparsam, Lokal
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-01-16
-- ============================================================================
-- Previous number: 067 (03_AI) → Renumbered to 092 to resolve duplicates
-- Phase: KI-Studio Pro - Globale KI-Einstellungen

-- AI Model Profiles Table
CREATE TABLE IF NOT EXISTS ai_pipeline.ai_model_profiles (
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
    -- Extended model categories (merged from 077)
    legacy_model_id VARCHAR(100),         -- Legacy/older model for compatibility
    moderation_model_id VARCHAR(100),     -- Content moderation model
    video_model_id VARCHAR(100),          -- Video generation model
    vision_model_id VARCHAR(100),         -- Vision/image understanding model
    transcription_model_id VARCHAR(100),  -- Speech-to-text model
    translation_model_id VARCHAR(100),    -- Translation model

    -- Standard-Profil Flag (nur eines kann true sein)
    is_default BOOLEAN DEFAULT FALSE,

    -- Aktiv-Flag
    is_active BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_ai_model_profiles_key ON ai_pipeline.ai_model_profiles (key);
CREATE INDEX IF NOT EXISTS idx_ai_model_profiles_default ON ai_pipeline.ai_model_profiles (is_default) WHERE is_default = TRUE;

-- Ensure only one default profile
CREATE UNIQUE INDEX IF NOT EXISTS idx_ai_model_profiles_single_default
    ON ai_pipeline.ai_model_profiles (is_default) WHERE is_default = TRUE;

-- Updated_at Trigger
CREATE OR REPLACE FUNCTION update_ai_model_profiles_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_ai_model_profiles_updated ON ai_pipeline.ai_model_profiles ;
CREATE TRIGGER trg_ai_model_profiles_updated
    BEFORE UPDATE ON ai_pipeline.ai_model_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_ai_model_profiles_timestamp();

-- ============================================================================
-- NOTE: Keine Seed-Daten - AI Model Profiles werden via Frontend konfiguriert
-- Profile: Standard, Qualität, Sparsam, Anthropic etc.
-- ============================================================================

-- Comment
COMMENT ON TABLE ai_pipeline.ai_model_profiles IS
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
GRANT SELECT, INSERT, UPDATE, DELETE ON ai_pipeline.ai_model_profiles TO lernsystem;

-- ============================================================================
-- End of schema definition
-- ============================================================================
