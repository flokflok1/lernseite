-- ============================================================================
-- Migration: 059_tts_pronunciation.sql
-- Version: 1.0.0
-- Description: TTS Pronunciation System
-- Author: LernsystemX Migration System
-- Date: 2026-01-02
-- ============================================================================

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
-- Initiale deutsche Aussprache-Regeln (Business/Kalkulation)
-- ============================================================================

INSERT INTO translations.tts_pronunciations (original_word, phonetic_spelling, language, category, word_type, source, verified) VALUES
-- Zusammengesetzte Geschäftsbegriffe
('Listeneinkaufspreis', 'Listen Einkaufs Preis', 'de', 'business', 'compound', 'manual', true),
('Zieleinkaufspreis', 'Ziel Einkaufs Preis', 'de', 'business', 'compound', 'manual', true),
('Bareinkaufspreis', 'Bar Einkaufs Preis', 'de', 'business', 'compound', 'manual', true),
('Einstandspreis', 'Einstands Preis', 'de', 'business', 'compound', 'manual', true),
('Verkaufspreis', 'Verkaufs Preis', 'de', 'business', 'compound', 'manual', true),
('Selbstkostenpreis', 'Selbstkosten Preis', 'de', 'business', 'compound', 'manual', true),
('Bezugskalkulation', 'Bezugs Kalkullazion', 'de', 'business', 'compound', 'manual', true),
('Handelskalkulation', 'Handels Kalkullazion', 'de', 'business', 'compound', 'manual', true),
('Verkaufskalkulation', 'Verkaufs Kalkullazion', 'de', 'business', 'compound', 'manual', true),
('Bezugskosten', 'Bezugs Kosten', 'de', 'business', 'compound', 'manual', true),
('Handlungskosten', 'Handlungs Kosten', 'de', 'business', 'compound', 'manual', true),
('Lieferantenrabatt', 'Lieferannten Rabbatt', 'de', 'business', 'compound', 'manual', true),
('Lieferantenskonto', 'Lieferannten Skonnto', 'de', 'business', 'compound', 'manual', true),
('Kundenrabatt', 'Kunden Rabbatt', 'de', 'business', 'compound', 'manual', true),
('Kundenskonto', 'Kunden Skonnto', 'de', 'business', 'compound', 'manual', true),

-- Einzelne Begriffe mit schwieriger Aussprache
('Rabatt', 'Rabbatt', 'de', 'business', 'noun', 'manual', true),
('Skonto', 'Skonnto', 'de', 'business', 'noun', 'manual', true),
('Kalkulation', 'Kalkullazion', 'de', 'business', 'noun', 'manual', true),
('Lieferant', 'Lieferannt', 'de', 'business', 'noun', 'manual', true),
('Lieferanten', 'Lieferannten', 'de', 'business', 'noun', 'manual', true),
('Provision', 'Proviesion', 'de', 'business', 'noun', 'manual', true),
('Marge', 'Marsche', 'de', 'business', 'noun', 'manual', true),
('Gewinnmarge', 'Gewinn Marsche', 'de', 'business', 'compound', 'manual', true),

-- Abkürzungen
('LEP', 'Listen Einkaufs Preis', 'de', 'business', 'abbreviation', 'manual', true),
('ZEP', 'Ziel Einkaufs Preis', 'de', 'business', 'abbreviation', 'manual', true),
('BEP', 'Bar Einkaufs Preis', 'de', 'business', 'abbreviation', 'manual', true),
('VKP', 'Verkaufs Preis', 'de', 'business', 'abbreviation', 'manual', true),
('SKP', 'Selbstkosten Preis', 'de', 'business', 'abbreviation', 'manual', true),
('MwSt', 'Mehrwertsteuer', 'de', 'business', 'abbreviation', 'manual', true),
('USt', 'Umsatzsteuer', 'de', 'business', 'abbreviation', 'manual', true),
('inkl', 'inklusive', 'de', 'general', 'abbreviation', 'manual', true),
('exkl', 'exklusive', 'de', 'general', 'abbreviation', 'manual', true),
('zzgl', 'zuzüglich', 'de', 'general', 'abbreviation', 'manual', true),
('abzgl', 'abzüglich', 'de', 'general', 'abbreviation', 'manual', true),
('Stk', 'Stück', 'de', 'general', 'abbreviation', 'manual', true),
('ca', 'zirka', 'de', 'general', 'abbreviation', 'manual', true),
('bzw', 'beziehungsweise', 'de', 'general', 'abbreviation', 'manual', true),
('z.B.', 'zum Beispiel', 'de', 'general', 'abbreviation', 'manual', true),
('d.h.', 'das heißt', 'de', 'general', 'abbreviation', 'manual', true),
('usw', 'und so weiter', 'de', 'general', 'abbreviation', 'manual', true),

-- IT-Begriffe
('Server', 'Sörver', 'de', 'technical', 'noun', 'manual', true),
('Router', 'Ruuter', 'de', 'technical', 'noun', 'manual', true),
('Switch', 'Suitsch', 'de', 'technical', 'noun', 'manual', true),
('Firewall', 'Feierwall', 'de', 'technical', 'noun', 'manual', true),
('Cloud', 'Klaud', 'de', 'technical', 'noun', 'manual', true),
('Software', 'Softweär', 'de', 'technical', 'noun', 'manual', true),
('Hardware', 'Hardweär', 'de', 'technical', 'noun', 'manual', true),
('Download', 'Daunlohd', 'de', 'technical', 'noun', 'manual', true),
('Upload', 'Aplohd', 'de', 'technical', 'noun', 'manual', true),
('Update', 'Apdäit', 'de', 'technical', 'noun', 'manual', true),
('Backup', 'Bäckapp', 'de', 'technical', 'noun', 'manual', true),
('Interface', 'Interfäis', 'de', 'technical', 'noun', 'manual', true),
('Cache', 'Käsch', 'de', 'technical', 'noun', 'manual', true),
('Browser', 'Brauser', 'de', 'technical', 'noun', 'manual', true),

-- Mathematik
('Prozent', 'Prozent', 'de', 'math', 'noun', 'manual', true),
('Dezimal', 'Deziemahl', 'de', 'math', 'noun', 'manual', true),
('Bruch', 'Bruch', 'de', 'math', 'noun', 'manual', true),
('Quotient', 'Kozient', 'de', 'math', 'noun', 'manual', true),
('Dividend', 'Diviedent', 'de', 'math', 'noun', 'manual', true),
('Divisor', 'Diviesor', 'de', 'math', 'noun', 'manual', true)

ON CONFLICT (original_word, language) DO UPDATE SET
    phonetic_spelling = EXCLUDED.phonetic_spelling,
    updated_at = CURRENT_TIMESTAMP;

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
