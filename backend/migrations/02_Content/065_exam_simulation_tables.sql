-- ============================================================================
-- Migration 047: KI-Prüfungssimulation Tables
-- ============================================================================
-- Erstellt Tabellen für:
-- 1. user_profiles (erweitert mit Prüfungs-Kontext)
-- 2. user_learning_analytics (Lernfortschritt pro Thema)
-- 3. exam_simulations (KI-generierte Prüfungssimulationen)
-- 4. courses Erweiterungen (profession_tag, exam_level, region)
-- ============================================================================

-- ============================================================================
-- 1. USER_PROFILES - Erweiterte Benutzerprofile mit Prüfungskontext
-- ============================================================================
CREATE TABLE IF NOT EXISTS user_profiles (
    profile_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(user_id) ON DELETE CASCADE,

    -- Berufliche Informationen
    profession VARCHAR(100),              -- z.B. "FISI", "Einzelhandel", "Industriekaufmann"
    profession_detail VARCHAR(255),       -- z.B. "Fachinformatiker Systemintegration"
    training_year INT,                    -- Ausbildungsjahr (1, 2, 3)
    training_start_date DATE,             -- Ausbildungsbeginn
    training_end_date DATE,               -- Voraussichtliches Ausbildungsende

    -- Prüfungsinformationen
    target_exam VARCHAR(50),              -- z.B. "AP1", "AP2", "Abschlussprüfung"
    exam_date DATE,                       -- Geplantes Prüfungsdatum
    exam_attempts INT DEFAULT 0,          -- Bisherige Prüfungsversuche

    -- Regionale Informationen
    region VARCHAR(100),                  -- z.B. "Baden-Württemberg", "Bayern"
    ihk VARCHAR(100),                     -- z.B. "IHK Stuttgart", "IHK München"
    ihk_code VARCHAR(20),                 -- IHK-Kennziffer

    -- KI-erkannte Daten
    detected_profession VARCHAR(100),     -- Automatisch erkannter Beruf
    detected_level VARCHAR(50),           -- Automatisch erkanntes Prüfungslevel
    detected_region VARCHAR(100),         -- Automatisch erkannte Region
    detection_confidence NUMERIC(3,2),    -- Konfidenz der Erkennung (0.00-1.00)

    -- Lernpräferenzen
    preferred_difficulty VARCHAR(20) DEFAULT 'realistic',  -- easy, realistic, hard
    preferred_question_types TEXT[],      -- Bevorzugte Fragetypen
    daily_learning_goal_minutes INT DEFAULT 30,

    -- Metadaten
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indizes für user_profiles
CREATE INDEX IF NOT EXISTS idx_user_profiles_user ON user_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_profiles_profession ON user_profiles(profession);
CREATE INDEX IF NOT EXISTS idx_user_profiles_target_exam ON user_profiles(target_exam);
CREATE INDEX IF NOT EXISTS idx_user_profiles_region ON user_profiles(region);

-- Trigger für updated_at
CREATE OR REPLACE FUNCTION update_user_profiles_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS user_profiles_updated ON user_profiles;
CREATE TRIGGER user_profiles_updated
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_user_profiles_timestamp();


-- ============================================================================
-- 2. USER_LEARNING_ANALYTICS - Lernfortschritt pro Thema
-- ============================================================================
CREATE TABLE IF NOT EXISTS user_learning_analytics (
    analytics_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses(course_id) ON DELETE CASCADE,

    -- Themen-Tracking
    topic VARCHAR(100) NOT NULL,          -- z.B. "Kalkulation", "Netzwerk", "SQL"
    topic_category VARCHAR(100),          -- Übergeordnete Kategorie

    -- Leistungsdaten
    score_avg NUMERIC(5,2) DEFAULT 0,     -- Durchschnittliche Punktzahl (0-100)
    score_best NUMERIC(5,2) DEFAULT 0,    -- Beste Punktzahl
    score_worst NUMERIC(5,2) DEFAULT 0,   -- Schlechteste Punktzahl
    score_trend NUMERIC(5,2) DEFAULT 0,   -- Trend (positiv/negativ)

    -- Übungsstatistiken
    attempts INT DEFAULT 0,               -- Anzahl Versuche
    correct_count INT DEFAULT 0,          -- Richtige Antworten
    incorrect_count INT DEFAULT 0,        -- Falsche Antworten
    skipped_count INT DEFAULT 0,          -- Übersprungene Fragen

    -- Zeitstatistiken
    total_time_seconds INT DEFAULT 0,     -- Gesamtzeit in Sekunden
    avg_time_seconds INT DEFAULT 0,       -- Durchschnittszeit pro Aufgabe
    fastest_time_seconds INT,             -- Schnellste Zeit
    slowest_time_seconds INT,             -- Langsamste Zeit

    -- Fehleranalyse
    common_mistakes JSONB DEFAULT '[]',   -- Häufige Fehler als JSON Array
    weak_subtopics TEXT[],                -- Schwache Unterthemen
    strong_subtopics TEXT[],              -- Starke Unterthemen

    -- Zeitstempel
    first_attempt TIMESTAMP WITH TIME ZONE,
    last_attempt TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Eindeutigkeit: Ein Eintrag pro User + Course + Topic
    UNIQUE(user_id, course_id, topic)
);

-- Indizes für user_learning_analytics
CREATE INDEX IF NOT EXISTS idx_ula_user ON user_learning_analytics(user_id);
CREATE INDEX IF NOT EXISTS idx_ula_course ON user_learning_analytics(course_id);
CREATE INDEX IF NOT EXISTS idx_ula_topic ON user_learning_analytics(topic);
CREATE INDEX IF NOT EXISTS idx_ula_score ON user_learning_analytics(score_avg);
CREATE INDEX IF NOT EXISTS idx_ula_user_course ON user_learning_analytics(user_id, course_id);

-- Trigger für updated_at
DROP TRIGGER IF EXISTS ula_updated ON user_learning_analytics;
CREATE TRIGGER ula_updated
    BEFORE UPDATE ON user_learning_analytics
    FOR EACH ROW
    EXECUTE FUNCTION update_user_profiles_timestamp();


-- ============================================================================
-- 3. EXAM_SIMULATIONS - KI-generierte Prüfungssimulationen
-- ============================================================================
CREATE TABLE IF NOT EXISTS exam_simulations (
    simulation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,

    -- Simulation Metadaten
    title VARCHAR(255),                   -- z.B. "AP1 Simulation - Kalkulation Fokus"
    description TEXT,

    -- Kontext (erkannter Prüfungskontext)
    context_json JSONB NOT NULL DEFAULT '{}',
    -- Struktur:
    -- {
    --   "profession": "FISI",
    --   "exam_level": "AP1",
    --   "region": "Baden-Württemberg",
    --   "ihk_standard": "IHK FISI AP1",
    --   "weak_topics": [...],
    --   "strong_topics": [...],
    --   "recommended_focus": {...},
    --   "detected_files": [...],
    --   "confidence": 0.94
    -- }

    -- Konfiguration (User-Einstellungen)
    config_json JSONB NOT NULL DEFAULT '{}',
    -- Struktur:
    -- {
    --   "mode": "smart" | "manual",
    --   "focus_distribution": { "Kalkulation": 35, "Netzwerk": 30, ... },
    --   "difficulty": "easy" | "realistic" | "hard",
    --   "time_limit_minutes": 90,
    --   "extra_instructions": "...",
    --   "selected_files": ["file-id-1", ...]
    -- }

    -- Ergebnis (generierte Prüfung)
    result_json JSONB,
    -- Struktur:
    -- {
    --   "summary": "...",
    --   "topics_covered": [...],
    --   "total_points": 100,
    --   "questions": [
    --     {
    --       "question_id": "...",
    --       "type": "mc" | "calculation" | "scenario" | "free_text",
    --       "topic": "Kalkulation",
    --       "difficulty": "realistic",
    --       "points": 10,
    --       "question": "...",
    --       "options": [...],           // für MC
    --       "correct_answer": "...",
    --       "explanation": "...",
    --       "ihk_reference": "..."      // IHK Aufgabennummer/Referenz
    --     }
    --   ]
    -- }

    -- Status
    status VARCHAR(20) DEFAULT 'pending',  -- pending, generating, ready, failed
    error_message TEXT,                    -- Fehlermeldung bei failed

    -- Generierungsdetails
    generation_started_at TIMESTAMP WITH TIME ZONE,
    generation_completed_at TIMESTAMP WITH TIME ZONE,
    tokens_used INT DEFAULT 0,
    model_used VARCHAR(100),

    -- Nutzungsstatistiken
    attempt_count INT DEFAULT 0,           -- Wie oft wurde diese Simulation gestartet
    best_score NUMERIC(5,2),               -- Beste erreichte Punktzahl
    avg_score NUMERIC(5,2),                -- Durchschnittliche Punktzahl

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indizes für exam_simulations
CREATE INDEX IF NOT EXISTS idx_examsim_course ON exam_simulations(course_id);
CREATE INDEX IF NOT EXISTS idx_examsim_user ON exam_simulations(user_id);
CREATE INDEX IF NOT EXISTS idx_examsim_status ON exam_simulations(status);
CREATE INDEX IF NOT EXISTS idx_examsim_created ON exam_simulations(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_examsim_context ON exam_simulations USING GIN (context_json);
CREATE INDEX IF NOT EXISTS idx_examsim_config ON exam_simulations USING GIN (config_json);

-- Trigger für updated_at
DROP TRIGGER IF EXISTS examsim_updated ON exam_simulations;
CREATE TRIGGER examsim_updated
    BEFORE UPDATE ON exam_simulations
    FOR EACH ROW
    EXECUTE FUNCTION update_user_profiles_timestamp();


-- ============================================================================
-- 4. EXAM_SIMULATION_ATTEMPTS - Versuche/Durchläufe einer Simulation
-- ============================================================================
CREATE TABLE IF NOT EXISTS exam_simulation_attempts (
    attempt_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    simulation_id UUID NOT NULL REFERENCES exam_simulations(simulation_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,

    -- Versuch-Daten
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    time_spent_seconds INT,

    -- Ergebnisse
    answers_json JSONB DEFAULT '[]',      -- User-Antworten
    score NUMERIC(5,2),                   -- Erreichte Punktzahl
    max_score NUMERIC(5,2),               -- Maximal mögliche Punktzahl
    percentage NUMERIC(5,2),              -- Prozent
    passed BOOLEAN,                       -- Bestanden?

    -- Detaillierte Auswertung
    results_by_topic JSONB DEFAULT '{}',  -- Ergebnisse pro Thema
    feedback_json JSONB,                  -- KI-Feedback

    -- Status
    status VARCHAR(20) DEFAULT 'in_progress',  -- in_progress, completed, abandoned

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indizes für exam_simulation_attempts
CREATE INDEX IF NOT EXISTS idx_esa_simulation ON exam_simulation_attempts(simulation_id);
CREATE INDEX IF NOT EXISTS idx_esa_user ON exam_simulation_attempts(user_id);
CREATE INDEX IF NOT EXISTS idx_esa_status ON exam_simulation_attempts(status);


-- ============================================================================
-- 5. COURSES ERWEITERUNGEN - Prüfungs-spezifische Felder
-- ============================================================================
ALTER TABLE courses
ADD COLUMN IF NOT EXISTS profession_tag VARCHAR(50),
ADD COLUMN IF NOT EXISTS exam_level VARCHAR(50),
ADD COLUMN IF NOT EXISTS exam_region VARCHAR(100),
ADD COLUMN IF NOT EXISTS ihk_standard VARCHAR(100),
ADD COLUMN IF NOT EXISTS detected_exam_type VARCHAR(50),
ADD COLUMN IF NOT EXISTS detected_topics TEXT[],
ADD COLUMN IF NOT EXISTS exam_metadata JSONB DEFAULT '{}';

-- Index für neue Felder
CREATE INDEX IF NOT EXISTS idx_courses_profession ON courses(profession_tag);
CREATE INDEX IF NOT EXISTS idx_courses_exam_level ON courses(exam_level);


-- ============================================================================
-- 6. COURSE_FILES ERWEITERUNGEN - Prüfungsdatei-Markierung
-- ============================================================================
ALTER TABLE course_files
ADD COLUMN IF NOT EXISTS is_exam_relevant BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS exam_topics TEXT[],
ADD COLUMN IF NOT EXISTS content_summary TEXT,
ADD COLUMN IF NOT EXISTS analyzed_at TIMESTAMP WITH TIME ZONE;

-- Index für exam-relevante Dateien
CREATE INDEX IF NOT EXISTS idx_cf_exam_relevant ON course_files(is_exam_relevant) WHERE is_exam_relevant = TRUE;


-- ============================================================================
-- KOMMENTARE
-- ============================================================================
COMMENT ON TABLE user_profiles IS 'Erweiterte Benutzerprofile mit Prüfungs- und Ausbildungskontext';
COMMENT ON TABLE user_learning_analytics IS 'Lernfortschritt und Leistungsdaten pro Thema für adaptive Prüfungsvorbereitung';
COMMENT ON TABLE exam_simulations IS 'KI-generierte Prüfungssimulationen mit Smart/Manual Mode';
COMMENT ON TABLE exam_simulation_attempts IS 'Durchläufe/Versuche von Prüfungssimulationen';

COMMENT ON COLUMN exam_simulations.context_json IS 'Automatisch erkannter Prüfungskontext (Beruf, Level, Region, Schwächen)';
COMMENT ON COLUMN exam_simulations.config_json IS 'User-Konfiguration (Mode, Fokus, Schwierigkeit, Zeitlimit)';
COMMENT ON COLUMN exam_simulations.result_json IS 'Generierte Prüfung mit Summary und Fragen';
