-- ============================================================================
-- Migration 052: Extend Course AI Settings
--
-- Erweitert course_ai_settings um:
-- - profile_key: Referenz auf ai_model_profiles
-- - reasoning_model_id: Für Prüfungen/Reasoning
-- - audio_model_id: Für TTS/STT
-- - realtime_model_id: Für Realtime-Audio
-- - embedding_model_id: Für Embeddings
--
-- Benennt exam_model → reasoning_model_id um (konsistent mit Profilen).
-- Benennt tts_model → audio_model_id um (konsistent mit Profilen).
--
-- Phase: KI-Studio Pro - Kurs-spezifische Einstellungen
-- ============================================================================

-- 1. Neue Spalten hinzufügen
ALTER TABLE course_ai_settings
    ADD COLUMN IF NOT EXISTS profile_key VARCHAR(50),
    ADD COLUMN IF NOT EXISTS reasoning_model_id VARCHAR(100),
    ADD COLUMN IF NOT EXISTS audio_model_id VARCHAR(100),
    ADD COLUMN IF NOT EXISTS realtime_model_id VARCHAR(100),
    ADD COLUMN IF NOT EXISTS embedding_model_id VARCHAR(100);

-- 2. Daten migrieren: exam_model → reasoning_model_id
UPDATE course_ai_settings
SET reasoning_model_id = exam_model
WHERE exam_model IS NOT NULL AND reasoning_model_id IS NULL;

-- 3. Daten migrieren: tts_model → audio_model_id
UPDATE course_ai_settings
SET audio_model_id = tts_model
WHERE tts_model IS NOT NULL AND audio_model_id IS NULL;

-- 4. chat_model → chat_model_id umbenennen für Konsistenz
ALTER TABLE course_ai_settings
    RENAME COLUMN chat_model TO chat_model_id;

-- 5. image_model → image_model_id umbenennen für Konsistenz
ALTER TABLE course_ai_settings
    RENAME COLUMN image_model TO image_model_id;

-- 6. profile_name → profile_key umbenennen (wird jetzt für FK verwendet)
-- Zuerst alte Daten in profile_key migrieren falls vorhanden
UPDATE course_ai_settings
SET profile_key = LOWER(REPLACE(profile_name, ' ', '_'))
WHERE profile_name IS NOT NULL AND profile_key IS NULL;

-- 7. Alte Spalten entfernen (exam_model, tts_model)
ALTER TABLE course_ai_settings
    DROP COLUMN IF EXISTS exam_model,
    DROP COLUMN IF EXISTS tts_model,
    DROP COLUMN IF EXISTS profile_name;

-- 8. Foreign Key zu ai_model_profiles hinzufügen
-- (ON DELETE SET NULL: Wenn Profil gelöscht wird, bleibt Kurs-Setting erhalten)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_course_ai_settings_profile'
    ) THEN
        ALTER TABLE course_ai_settings
            ADD CONSTRAINT fk_course_ai_settings_profile
            FOREIGN KEY (profile_key) REFERENCES ai_model_profiles(key)
            ON DELETE SET NULL;
    END IF;
END $$;

-- 9. Index für profile_key
CREATE INDEX IF NOT EXISTS idx_course_ai_settings_profile_key
    ON course_ai_settings(profile_key);

-- 10. Kommentar aktualisieren
COMMENT ON TABLE course_ai_settings IS
'Kurs-spezifische KI-Modell-Konfiguration.

Felder (alle nullable = System-Default verwenden):
- profile_key: Referenz auf ai_model_profiles.key
- chat_model_id: Modell für Chat/Theorie-Generierung
- reasoning_model_id: Modell für Prüfungen/Reasoning (o3, o1, etc.)
- image_model_id: Modell für Bildgenerierung
- audio_model_id: Modell für TTS/STT
- realtime_model_id: Modell für Realtime-Audio
- embedding_model_id: Modell für Embeddings

Beim Anwenden eines Profils werden alle Model-IDs überschrieben
und profile_key gesetzt. Änderungen an einzelnen Modellen
überschreiben das Profil.';

-- Verify
DO $$
DECLARE
    col_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO col_count
    FROM information_schema.columns
    WHERE table_name = 'course_ai_settings'
    AND column_name IN ('profile_key', 'chat_model_id', 'reasoning_model_id',
                        'image_model_id', 'audio_model_id', 'realtime_model_id',
                        'embedding_model_id');

    IF col_count = 7 THEN
        RAISE NOTICE 'course_ai_settings: Alle 7 Model-Spalten vorhanden';
    ELSE
        RAISE WARNING 'course_ai_settings: Nur % von 7 Model-Spalten!', col_count;
    END IF;
END $$;
