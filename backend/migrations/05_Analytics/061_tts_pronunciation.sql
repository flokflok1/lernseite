-- ============================================================================
-- Migration: 061_tts_pronunciation.sql
-- Version: 1.0.0
-- Description: TTS Pronunciation System (CREATE SCHEMA + tables)
-- Author: LernsystemX Migration System
-- Date: 2026-01-02
-- Phase: 3 (Extended Systems - Translations/I18n)
-- ============================================================================

-- Create translations schema (MUST come before all translations.* table creation)

CREATE TABLE IF NOT EXISTS translations.tts_pronunciations (
    pronunciation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Das Originalwort (case-insensitive matching)
    original_word VARCHAR(255) NOT NULL,

    -- Phonetische Schreibweise für bessere Aussprache
    phonetic_spelling VARCHAR(500) NOT NULL,

    -- Sprache (de, en, etc.)
    language VARCHAR(10) NOT NULL DEFAULT 'de',

    -- Kategorie für Gruppierung
    category VARCHAR(100),  -- z.B. 'business', 'math', 'technical', 'names'

    -- Wortart
    word_type VARCHAR(50),  -- 'noun', 'verb', 'abbreviation', 'compound', 'name', 'number'

    -- Quelle der Aussprache
    source VARCHAR(50) NOT NULL DEFAULT 'manual',  -- 'manual', 'ai_generated', 'user_feedback'

    -- Bei AI-generierten: welches Modell
    ai_model VARCHAR(100),

    -- Confidence Score (0-1) für AI-generierte
    confidence DECIMAL(3,2) DEFAULT 1.0,

    -- Wurde von Admin verifiziert?
    verified BOOLEAN DEFAULT FALSE,

    -- Nutzungsstatistik
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP WITH TIME ZONE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES core.users(user_id),

    -- Constraints
    CONSTRAINT unique_word_language UNIQUE (original_word, language)
);

-- Index für schnelle Suche
CREATE INDEX IF NOT EXISTS idx_tts_original_word ON translations.tts_pronunciations(LOWER(original_word));
CREATE INDEX IF NOT EXISTS idx_tts_language ON translations.tts_pronunciations(language);
CREATE INDEX IF NOT EXISTS idx_tts_category ON translations.tts_pronunciations(category);
CREATE INDEX IF NOT EXISTS idx_tts_verified ON translations.tts_pronunciations(verified);

-- ============================================================================
-- Tabelle für KI-Anfragen zur Aussprache (für Tracking)
-- ============================================================================

CREATE TABLE IF NOT EXISTS translations.tts_ai_requests (
    request_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Das angefragte Wort
    word VARCHAR(255) NOT NULL,
    language VARCHAR(10) NOT NULL DEFAULT 'de',

    -- Kontext (optional)
    context TEXT,

    -- KI-Antwort
    ai_response JSONB,
    suggested_spelling VARCHAR(500),

    -- Status
    status VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'completed', 'failed', 'approved', 'rejected'

    -- Wurde in tts_pronunciations übernommen?
    pronunciation_id UUID REFERENCES translations.tts_pronunciations(pronunciation_id),

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP WITH TIME ZONE,

    -- Wer hat angefragt
    requested_by UUID REFERENCES core.users(user_id)
);

CREATE INDEX IF NOT EXISTS idx_tts_ai_word ON translations.tts_ai_requests(LOWER(word));
CREATE INDEX IF NOT EXISTS idx_tts_ai_status ON translations.tts_ai_requests(status);

-- ============================================================================
-- Funktion zum Abrufen der Aussprache
-- ============================================================================

CREATE OR REPLACE FUNCTION get_pronunciation(
    p_word VARCHAR(255),
    p_language VARCHAR(10) DEFAULT 'de'
)
RETURNS VARCHAR(500) AS $$
DECLARE
    v_phonetic VARCHAR(500);
BEGIN
    SELECT phonetic_spelling INTO v_phonetic
    FROM translations.tts_pronunciations
    WHERE LOWER(original_word) = LOWER(p_word)
      AND language = p_language;

    -- Update usage stats
    IF v_phonetic IS NOT NULL THEN
        UPDATE translations.tts_pronunciations
        SET usage_count = usage_count + 1,
            last_used_at = CURRENT_TIMESTAMP
        WHERE LOWER(original_word) = LOWER(p_word)
          AND language = p_language;
    END IF;

    RETURN v_phonetic;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- View für häufig verwendete Aussprachen
-- ============================================================================

CREATE OR REPLACE VIEW v_tts_popular_pronunciations AS
SELECT
    pronunciation_id,
    original_word,
    phonetic_spelling,
    language,
    category,
    usage_count,
    verified
FROM translations.tts_pronunciations
WHERE verified = true
ORDER BY usage_count DESC;

COMMENT ON TABLE translations.tts_pronunciations IS 'Phonetische Korrekturen für Text-to-Speech Systeme';
COMMENT ON TABLE translations.tts_ai_requests IS 'Tracking von KI-Anfragen für neue Aussprachekorrekturen';
