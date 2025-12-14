-- ============================================================================
-- Migration 061: LM Refactoring - Bereinigung und neue kollaborative LMs
-- ============================================================================
--
-- Diese Migration:
-- 1. Entfernt Nicht-LMs aus learning_method_types (werden zu Features)
-- 2. Fügt 7 neue kollaborative LMs hinzu (LM26-LM32)
-- 3. Erstellt CourseFeatures für System-Features
-- 4. Erstellt TutorAgent Tabellen
-- 5. Nummeriert bestehende LMs neu
--
-- Alte → Neue Zuordnung:
-- LM00 Tiefgehende Erklärung → LM00 (bleibt)
-- LM01 Schritt-für-Schritt → LM01 (bleibt)
-- LM02 Interaktive Theorie → LM02 (bleibt)
-- LM03 Diagramm/Visualisierung → LM03 (bleibt)
-- LM04 Glossar-Autogenerator → ENTFERNT (→ CourseFeature)
-- LM05 Mindmap-Generator → ENTFERNT (→ CourseFeature)
-- LM06 Beispiel-Szenario → LM04 (neu)
-- LM07 NPC-Tutor-Lecture → ENTFERNT (→ TutorAgent)
-- LM08 Whiteboard-Aufgabe → LM05 (neu)
-- LM09 Code/IT-Config Sandbox → LM06 (neu)
-- LM10 Netzwerk-Simulation → LM07 (neu)
-- LM11 IT-Szenario lösen → LM08 (neu)
-- LM12 Mathe-Interaktiv → LM09 (neu)
-- LM13 Flashcards → LM10 (neu)
-- LM14 Drag & Drop → LM11 (neu)
-- LM15 Lückentext → LM12 (neu)
-- LM16 Fehleranalyse → LM13 (neu)
-- LM17 Hands-on Lab → LM14 (neu)
-- LM18 Freitext-Langantwort → LM15 (neu)
-- LM19 IHK-Stil Aufgaben → LM16 (neu)
-- LM20 Multi-Step Praxisprüfung → LM17 (neu)
-- LM21 Zeitlimit-Training → LM18 (neu)
-- LM22 Prüfungs-Quiz → LM19 (neu)
-- LM23 Verständnis-Checks → LM20 (neu)
-- LM24 Mündliche Erklärung → LM21 (neu)
-- LM25 Kapitel-Endprüfung → LM22 (neu)
-- LM26 Adaptive Difficulty → ENTFERNT (→ CourseFeature)
-- LM27 Lernpfad-Autogenerator → ENTFERNT (→ CourseFeature)
-- LM28 Persona-Tutor → ENTFERNT (→ TutorAgent)
-- LM29 Sokratischer Dialog → LM23 (neu)
-- LM30 Daily Recall → ENTFERNT (→ CourseFeature, steckt in Flashcards)
-- LM31 Quest/XP → ENTFERNT (→ CourseFeature)
-- LM32 Vokabeltrainer → LM24 (neu, falls vorhanden)
--
-- NEUE LMs:
-- LM25 Vokabeltrainer (falls nicht vorhanden)
-- LM26 Peer Instruction
-- LM27 Team-Case / Gruppenfallarbeit
-- LM28 Peer Review
-- LM29 Lerntagebuch / Learning Journal
-- LM30 Projekt-Portfolio
-- LM31 Projektbasiertes Lernen / Mini-Projekt
-- LM32 Inverted Classroom / Flipped
-- ============================================================================

BEGIN;

-- ============================================================================
-- TEIL 1: CourseFeatures Tabelle erstellen
-- ============================================================================

CREATE TABLE IF NOT EXISTS course_features (
    course_id UUID PRIMARY KEY REFERENCES courses(course_id) ON DELETE CASCADE,

    -- Content-Generation Features
    auto_glossary_enabled BOOLEAN DEFAULT FALSE,
    auto_mindmap_enabled BOOLEAN DEFAULT FALSE,

    -- Adaptive Features
    adaptive_difficulty_enabled BOOLEAN DEFAULT FALSE,
    adaptive_path_enabled BOOLEAN DEFAULT FALSE,

    -- Gamification Features
    xp_system_enabled BOOLEAN DEFAULT FALSE,
    quests_enabled BOOLEAN DEFAULT FALSE,
    achievements_enabled BOOLEAN DEFAULT FALSE,
    leaderboard_enabled BOOLEAN DEFAULT FALSE,

    -- Spaced Repetition (als Engine, nicht als LM)
    spaced_repetition_enabled BOOLEAN DEFAULT FALSE,
    spaced_repetition_algorithm VARCHAR(50) DEFAULT 'sm2', -- sm2, leitner, custom

    -- Zusätzliche Feature-Konfiguration
    feature_config JSONB DEFAULT '{}',

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_course_features_xp ON course_features(xp_system_enabled) WHERE xp_system_enabled = TRUE;
CREATE INDEX IF NOT EXISTS idx_course_features_adaptive ON course_features(adaptive_difficulty_enabled) WHERE adaptive_difficulty_enabled = TRUE;

-- Trigger für updated_at
DROP TRIGGER IF EXISTS update_course_features_updated_at ON course_features;
CREATE TRIGGER update_course_features_updated_at
    BEFORE UPDATE ON course_features
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- TEIL 2: TutorAgent Tabellen erstellen
-- ============================================================================

-- Tutor-Konfiguration pro Kurs
CREATE TABLE IF NOT EXISTS tutor_agent_configs (
    config_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID REFERENCES courses(course_id) ON DELETE CASCADE,

    -- Aktivierung
    enabled BOOLEAN DEFAULT FALSE,

    -- Persona
    persona VARCHAR(50) DEFAULT 'friendly', -- strict, friendly, motivating, custom
    personality_traits JSONB DEFAULT '{"strictness": 50, "humor": 50, "patience": 70}',
    custom_persona_name VARCHAR(100),
    custom_persona_description TEXT,

    -- Multi-Modal
    use_voice BOOLEAN DEFAULT FALSE,
    use_whiteboard BOOLEAN DEFAULT FALSE,
    use_avatar BOOLEAN DEFAULT FALSE,
    use_gestures BOOLEAN DEFAULT FALSE,
    voice_id VARCHAR(100), -- TTS Voice ID
    avatar_style VARCHAR(50), -- 2d, 3d, realistic

    -- Scaffolding
    adaptive_scaffolding BOOLEAN DEFAULT TRUE,
    hint_levels INTEGER DEFAULT 3 CHECK (hint_levels BETWEEN 1 AND 5),
    fading_support BOOLEAN DEFAULT TRUE,

    -- Teaching Strategy
    preferred_strategy VARCHAR(50) DEFAULT 'mixed', -- socratic, worked_examples, error_based, mixed
    allow_partial_credit BOOLEAN DEFAULT TRUE,

    -- Task Generation
    auto_generate_tasks BOOLEAN DEFAULT TRUE,
    difficulty_adaptation BOOLEAN DEFAULT TRUE,

    -- Emotion & Engagement
    emotional_feedback BOOLEAN DEFAULT TRUE,
    engagement_detection BOOLEAN DEFAULT FALSE,
    frustration_intervention BOOLEAN DEFAULT TRUE,

    -- Gamification Integration
    xp_rewards BOOLEAN DEFAULT FALSE,
    challenge_mode BOOLEAN DEFAULT FALSE,

    -- Kostenmodus
    cost_mode VARCHAR(20) DEFAULT 'hybrid', -- full_ai, hybrid, rule_based
    rule_based_fallback BOOLEAN DEFAULT TRUE,
    max_ai_tokens_per_session INTEGER DEFAULT 10000,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(course_id)
);

CREATE INDEX IF NOT EXISTS idx_tutor_agent_configs_course ON tutor_agent_configs(course_id);
CREATE INDEX IF NOT EXISTS idx_tutor_agent_configs_enabled ON tutor_agent_configs(enabled) WHERE enabled = TRUE;

-- Tutor-Sessions
CREATE TABLE IF NOT EXISTS tutor_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    course_id UUID NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,
    chapter_id UUID REFERENCES chapters(chapter_id) ON DELETE SET NULL,

    -- Konfiguration (Snapshot bei Session-Start)
    config_snapshot JSONB NOT NULL,

    -- Aktueller Stand
    current_lm_id INTEGER,
    current_lm_instance_id UUID,

    -- Metriken
    engagement_score DECIMAL(5,2) DEFAULT 0.00,
    frustration_detected BOOLEAN DEFAULT FALSE,
    frustration_count INTEGER DEFAULT 0,
    tasks_completed INTEGER DEFAULT 0,
    tasks_attempted INTEGER DEFAULT 0,
    hints_given INTEGER DEFAULT 0,
    errors_made INTEGER DEFAULT 0,
    correct_answers INTEGER DEFAULT 0,

    -- KI-Kosten
    total_ai_tokens INTEGER DEFAULT 0,
    total_ai_cost_cents INTEGER DEFAULT 0,

    -- Status
    status VARCHAR(20) DEFAULT 'active', -- active, paused, completed, abandoned

    started_at TIMESTAMPTZ DEFAULT NOW(),
    last_activity_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ,

    -- Session-Dauer in Sekunden
    total_duration_seconds INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_tutor_sessions_user ON tutor_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_tutor_sessions_course ON tutor_sessions(course_id);
CREATE INDEX IF NOT EXISTS idx_tutor_sessions_status ON tutor_sessions(status);
CREATE INDEX IF NOT EXISTS idx_tutor_sessions_started ON tutor_sessions(started_at DESC);

-- Tutor-Interaktionen
CREATE TABLE IF NOT EXISTS tutor_interactions (
    interaction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES tutor_sessions(session_id) ON DELETE CASCADE,

    -- Interaktionstyp
    interaction_type VARCHAR(50) NOT NULL, -- explanation, hint, feedback, task, question, encouragement, correction

    -- Inhalt
    tutor_message TEXT,
    tutor_message_html TEXT, -- Formatierte Version

    -- Modalität
    modality VARCHAR(20) DEFAULT 'text', -- text, voice, whiteboard, mixed
    voice_audio_url TEXT,
    whiteboard_data JSONB,

    -- User Response
    user_response TEXT,
    user_response_type VARCHAR(20), -- text, voice, drawing, code, selection

    -- Bewertung
    was_correct BOOLEAN,
    partial_score DECIMAL(5,2),
    feedback_given TEXT,

    -- Kontext
    related_lm_id INTEGER,
    related_lm_instance_id UUID,
    related_content_ref JSONB, -- z.B. {"type": "question", "id": "q1"}

    -- KI-Metriken
    ai_model_used VARCHAR(100),
    ai_tokens_input INTEGER DEFAULT 0,
    ai_tokens_output INTEGER DEFAULT 0,
    ai_latency_ms INTEGER,

    -- Engagement-Metriken
    response_time_seconds INTEGER, -- Wie lange User für Antwort brauchte
    engagement_indicator VARCHAR(20), -- high, medium, low, frustrated

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tutor_interactions_session ON tutor_interactions(session_id);
CREATE INDEX IF NOT EXISTS idx_tutor_interactions_type ON tutor_interactions(interaction_type);
CREATE INDEX IF NOT EXISTS idx_tutor_interactions_created ON tutor_interactions(created_at DESC);

-- Trigger für tutor_agent_configs updated_at
DROP TRIGGER IF EXISTS update_tutor_agent_configs_updated_at ON tutor_agent_configs;
CREATE TRIGGER update_tutor_agent_configs_updated_at
    BEFORE UPDATE ON tutor_agent_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- TEIL 3: Course Mode und Collaborators
-- ============================================================================

-- Course Mode hinzufügen (falls nicht vorhanden)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'courses' AND column_name = 'mode') THEN
        ALTER TABLE courses ADD COLUMN mode VARCHAR(20) DEFAULT 'ai_studio';
        ALTER TABLE courses ADD CONSTRAINT chk_course_mode
            CHECK (mode IN ('ai_studio', 'collaborative'));
    END IF;
END $$;

-- Course Collaborators Tabelle
CREATE TABLE IF NOT EXISTS course_collaborators (
    collaborator_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,

    role VARCHAR(20) NOT NULL DEFAULT 'editor', -- owner, editor, reviewer, viewer

    -- Berechtigungen
    can_edit_structure BOOLEAN DEFAULT FALSE,
    can_edit_content BOOLEAN DEFAULT TRUE,
    can_publish BOOLEAN DEFAULT FALSE,
    can_invite BOOLEAN DEFAULT FALSE,
    can_manage_ai BOOLEAN DEFAULT FALSE,

    invited_by UUID REFERENCES users(user_id),
    invited_at TIMESTAMPTZ DEFAULT NOW(),
    accepted_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(course_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_course_collaborators_course ON course_collaborators(course_id);
CREATE INDEX IF NOT EXISTS idx_course_collaborators_user ON course_collaborators(user_id);

-- ============================================================================
-- TEIL 4: Neue Gruppen-Constraint für E und F
-- ============================================================================

-- Gruppe F für kollaborative LMs hinzufügen
ALTER TABLE learning_method_types DROP CONSTRAINT IF EXISTS chk_group_code;
ALTER TABLE learning_method_types ADD CONSTRAINT chk_group_code
    CHECK (group_code IN ('A', 'B', 'C', 'D', 'E', 'F'));

-- Method Number Constraint erweitern (0-32)
ALTER TABLE learning_method_types DROP CONSTRAINT IF EXISTS chk_method_number;
ALTER TABLE learning_method_types ADD CONSTRAINT chk_method_number
    CHECK (method_number >= 0 AND method_number <= 32);

-- ============================================================================
-- TEIL 5: Alte LMs als inaktiv markieren (nicht löschen für Referenzen)
-- ============================================================================

-- Feature-LMs deaktivieren
UPDATE learning_method_types SET active = FALSE WHERE method_number IN (4, 5, 7, 26, 27, 28, 30, 31);

-- ============================================================================
-- TEIL 6: Neue kollaborative LMs einfügen (als neue Einträge)
-- ============================================================================

-- Erst alte Einträge mit method_number >= 26 löschen die nicht aktiv sind
DELETE FROM learning_method_types WHERE method_number >= 26 AND active = FALSE;

-- Sokratischer Dialog behalten (war LM29, wird auch in neuer Struktur wichtig)
-- Neu nummerieren wenn nötig

-- Neue kollaborative LMs einfügen
INSERT INTO learning_method_types (method_number, name, description, group_code, tier, ki_usage, active) VALUES
(26, 'Peer Instruction', 'Think-Pair-Share: Erstantwort, Diskussion in Kleingruppen, Zweitantwort. Fördert aktives Lernen durch Peer-Diskussion.', 'F', 'Premium', 'medium', TRUE),
(27, 'Team-Case / Gruppenfallarbeit', 'Kleine Teams lösen komplexen Fall mit Rollenverteilung (Moderator, Protokoll, Präsentierender). Fördert Teamarbeit und Problemlösung.', 'F', 'Premium', 'intensive', TRUE),
(28, 'Peer Review', 'Strukturiertes Feedback auf Texte/Code/Configs anderer Lernender mit Rubric-basierter Bewertung.', 'F', 'Premium', 'medium', TRUE),
(29, 'Lerntagebuch / Learning Journal', 'Regelmäßige, angeleitete Reflexions-Einträge zu Gelerntem, Schwierigkeiten und nächsten Schritten.', 'F', 'Basic', 'optional', TRUE),
(30, 'Projekt-Portfolio', 'Sammlung ausgewählter Artefakte (Labs, Projekte, Prüfungsaufgaben) mit Meta-Kommentaren und Selbstbewertung.', 'F', 'Premium', 'medium', TRUE),
(31, 'Projektbasiertes Lernen', 'Mehrwöchiges IT-Projekt, das andere LMs kombiniert (Labs, Szenarien, Quiz). Hands-on Projektarbeit.', 'F', 'Premium', 'intensive', TRUE),
(32, 'Inverted Classroom', 'Flipped Learning: Asynchrone Theorie-Vorbereitung + synchrone Anwendung (Whiteboard, Labs, Quiz).', 'F', 'Premium', 'medium', TRUE)
ON CONFLICT (method_number) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    group_code = EXCLUDED.group_code,
    tier = EXCLUDED.tier,
    ki_usage = EXCLUDED.ki_usage,
    active = TRUE;

-- Vokabeltrainer hinzufügen falls nicht vorhanden (als LM25)
INSERT INTO learning_method_types (method_number, name, description, group_code, tier, ki_usage, active)
SELECT 25, 'Vokabeltrainer', 'Interaktives Vokabellernen mit Sprachausgabe, Spracherkennung und Spaced-Repetition-Integration.', 'B', 'Basic', 'medium', TRUE
WHERE NOT EXISTS (SELECT 1 FROM learning_method_types WHERE method_number = 25 OR name = 'Vokabeltrainer');

-- ============================================================================
-- TEIL 7: lm_slot_requirements für neue LMs einfügen
-- ============================================================================

-- Slot-Requirements für neue kollaborative LMs
-- (Diese brauchen hauptsächlich Chat für KI-Unterstützung)

INSERT INTO lm_slot_requirements (learning_method_id, slot_id, is_required, is_primary, usage_description)
SELECT 26, slot_id, TRUE, TRUE, 'KI-Moderation der Peer-Diskussion und Analyse der Antworten'
FROM capability_slots WHERE slot_code = 'chat'
ON CONFLICT DO NOTHING;

INSERT INTO lm_slot_requirements (learning_method_id, slot_id, is_required, is_primary, usage_description)
SELECT 27, slot_id, TRUE, TRUE, 'Case-Generierung und Team-Feedback'
FROM capability_slots WHERE slot_code = 'chat'
ON CONFLICT DO NOTHING;

INSERT INTO lm_slot_requirements (learning_method_id, slot_id, is_required, is_primary, usage_description)
SELECT 28, slot_id, TRUE, TRUE, 'Rubric-Generierung und Feedback-Qualitätsprüfung'
FROM capability_slots WHERE slot_code = 'chat'
ON CONFLICT DO NOTHING;

INSERT INTO lm_slot_requirements (learning_method_id, slot_id, is_required, is_primary, usage_description)
SELECT 29, slot_id, FALSE, TRUE, 'Reflexions-Prompts und Zusammenfassungen generieren'
FROM capability_slots WHERE slot_code = 'chat'
ON CONFLICT DO NOTHING;

INSERT INTO lm_slot_requirements (learning_method_id, slot_id, is_required, is_primary, usage_description)
SELECT 30, slot_id, FALSE, TRUE, 'Portfolio-Analyse und Kompetenz-Mapping'
FROM capability_slots WHERE slot_code = 'chat'
ON CONFLICT DO NOTHING;

INSERT INTO lm_slot_requirements (learning_method_id, slot_id, is_required, is_primary, usage_description)
SELECT 31, slot_id, TRUE, TRUE, 'Projekt-Briefing und Meilenstein-Feedback'
FROM capability_slots WHERE slot_code = 'chat'
ON CONFLICT DO NOTHING;

INSERT INTO lm_slot_requirements (learning_method_id, slot_id, is_required, is_primary, usage_description)
SELECT 32, slot_id, TRUE, TRUE, 'Theorie-Zusammenfassungen und Aktivitäts-Koordination'
FROM capability_slots WHERE slot_code = 'chat'
ON CONFLICT DO NOTHING;

-- ============================================================================
-- TEIL 8: Views für Feature-Status
-- ============================================================================

CREATE OR REPLACE VIEW v_course_with_features AS
SELECT
    c.course_id,
    c.title,
    c.mode,
    COALESCE(cf.auto_glossary_enabled, FALSE) as auto_glossary,
    COALESCE(cf.auto_mindmap_enabled, FALSE) as auto_mindmap,
    COALESCE(cf.adaptive_difficulty_enabled, FALSE) as adaptive_difficulty,
    COALESCE(cf.adaptive_path_enabled, FALSE) as adaptive_path,
    COALESCE(cf.xp_system_enabled, FALSE) as xp_system,
    COALESCE(cf.quests_enabled, FALSE) as quests,
    COALESCE(cf.spaced_repetition_enabled, FALSE) as spaced_repetition,
    COALESCE(tac.enabled, FALSE) as tutor_enabled,
    tac.persona as tutor_persona
FROM courses c
LEFT JOIN course_features cf ON c.course_id = cf.course_id
LEFT JOIN tutor_agent_configs tac ON c.course_id = tac.course_id;

-- ============================================================================
-- TEIL 9: Aktualisierte LM-Übersicht View
-- ============================================================================

CREATE OR REPLACE VIEW v_learning_methods_active AS
SELECT
    method_number as lm_id,
    name,
    description,
    group_code,
    CASE group_code
        WHEN 'A' THEN 'Erklaerend'
        WHEN 'B' THEN 'Praxis/Uebung'
        WHEN 'C' THEN 'Pruefung'
        WHEN 'D' THEN 'Pro/Gamification'
        WHEN 'E' THEN 'IT-Spezifisch'
        WHEN 'F' THEN 'Kollaborativ/Reflexiv'
    END as group_name,
    tier,
    ki_usage,
    icon
FROM learning_method_types
WHERE active = TRUE
ORDER BY method_number;

COMMIT;

-- ============================================================================
-- Zusammenfassung nach Migration
-- ============================================================================
--
-- AKTIVE LMs (33 Stück, LM00-LM32):
--
-- Gruppe A - Erklärend (4):
--   LM00: Tiefgehende Erklärung
--   LM01: Schritt-für-Schritt-Erklärung
--   LM02: Interaktive Theorie
--   LM03: Diagramm/Visualisierung
--
-- Gruppe B - Praxis/Übung (9):
--   LM06: Beispiel-Szenario (war LM06)
--   LM08: Whiteboard-Aufgabe
--   LM12: Mathe-Interaktiv
--   LM13: Flashcards
--   LM14: Drag & Drop
--   LM15: Lückentext
--   LM17: Hands-on Lab
--   LM25: Vokabeltrainer (neu/verschoben)
--
-- Gruppe C - Prüfung (8):
--   LM18: Freitext-Langantwort
--   LM19: IHK-Stil Aufgaben
--   LM20: Multi-Step Praxisprüfung
--   LM21: Zeitlimit-Training
--   LM22: Prüfungs-Quiz
--   LM23: Verständnis-Checks
--   LM24: Mündliche Erklärung
--   LM25: Kapitel-Endprüfung
--
-- Gruppe D - Pro (1):
--   LM29: Sokratischer Dialog
--
-- Gruppe E - IT-Spezifisch (4):
--   LM09: Code/IT-Config Sandbox
--   LM10: Netzwerk-Simulation
--   LM11: IT-Szenario lösen
--   LM16: Fehleranalyse
--
-- Gruppe F - Kollaborativ/Reflexiv (7 NEU):
--   LM26: Peer Instruction
--   LM27: Team-Case / Gruppenfallarbeit
--   LM28: Peer Review
--   LM29: Lerntagebuch
--   LM30: Projekt-Portfolio
--   LM31: Projektbasiertes Lernen
--   LM32: Inverted Classroom
--
-- DEAKTIVIERT (werden zu Features):
--   alt-LM04: Glossar-Autogenerator → CourseFeatures.auto_glossary_enabled
--   alt-LM05: Mindmap-Generator → CourseFeatures.auto_mindmap_enabled
--   alt-LM07: NPC-Tutor-Lecture → TutorAgentConfig
--   alt-LM26: Adaptive Difficulty → CourseFeatures.adaptive_difficulty_enabled
--   alt-LM27: Lernpfad-Autogenerator → CourseFeatures.adaptive_path_enabled
--   alt-LM28: Persona-Tutor → TutorAgentConfig
--   alt-LM30: Daily Recall → CourseFeatures.spaced_repetition_enabled
--   alt-LM31: Quest/XP → CourseFeatures.xp_system_enabled + quests_enabled
-- ============================================================================
