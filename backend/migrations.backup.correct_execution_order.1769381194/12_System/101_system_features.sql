-- ============================================================================
-- Migration: 074_system_features.sql
-- Version: 1.0.0
-- Description: System Features - Tools/Services separate from Content-LMs
-- Author: LernsystemX Migration System
-- Date: 2026-01-02
-- Dependencies: 001_core_users_roles.sql, 063_system_features_tables.sql
-- ============================================================================

CREATE TABLE IF NOT EXISTS support_systems.system_features (
    feature_id SERIAL PRIMARY KEY,
    feature_code VARCHAR(50) UNIQUE NOT NULL,
    feature_name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    requires_infrastructure BOOLEAN DEFAULT FALSE,
    requires_external_service BOOLEAN DEFAULT FALSE,
    active BOOLEAN DEFAULT TRUE,
    config JSONB DEFAULT '{}',
    icon VARCHAR(50),
    former_lm_id INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_system_features_code ON support_systems.system_features(feature_code);
CREATE INDEX IF NOT EXISTS idx_system_features_category ON support_systems.system_features(category);
CREATE INDEX IF NOT EXISTS idx_system_features_active ON support_systems.system_features(active) WHERE active = TRUE;

COMMENT ON TABLE support_systems.system_features IS 'System-wide features separated from Content-LMs (Tools, Services, Infrastructure)';
COMMENT ON COLUMN support_systems.system_features.feature_code IS 'Unique identifier (e.g. whiteboard_engine, it_sandbox)';
COMMENT ON COLUMN support_systems.system_features.category IS 'tutor, visualization, gamification, collaboration, it_environments, audio';
COMMENT ON COLUMN support_systems.system_features.former_lm_id IS 'Former LM ID from old numbering (for migration reference)';

-- ============================================================================
-- TABLE: course_system_features
-- Description: Which features are enabled for which course
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_systems.course_system_features (
    mapping_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID REFERENCES courses.courses(course_id) ON DELETE CASCADE,
    feature_id INTEGER REFERENCES support_systems.system_features(feature_id) ON DELETE CASCADE,
    enabled BOOLEAN DEFAULT TRUE,
    config_override JSONB DEFAULT '{}',
    enabled_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (course_id, feature_id)
);

CREATE INDEX IF NOT EXISTS idx_course_features_course ON support_systems.course_system_features(course_id);
CREATE INDEX IF NOT EXISTS idx_course_features_feature ON support_systems.course_system_features(feature_id);
CREATE INDEX IF NOT EXISTS idx_course_features_enabled ON support_systems.course_system_features(enabled) WHERE enabled = TRUE;

COMMENT ON TABLE support_systems.course_system_features IS 'Course-specific feature activation (e.g. enable Whiteboard for Math course)';

-- ============================================================================
-- TABLE: chapter_system_features
-- Description: Chapter-level feature activation (more granular)
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_systems.chapter_system_features (
    mapping_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chapter_id UUID REFERENCES courses.chapters(chapter_id) ON DELETE CASCADE,
    feature_id INTEGER REFERENCES support_systems.system_features(feature_id) ON DELETE CASCADE,
    enabled BOOLEAN DEFAULT TRUE,
    config_override JSONB DEFAULT '{}',
    enabled_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (chapter_id, feature_id)
);

CREATE INDEX IF NOT EXISTS idx_chapter_features_chapter ON support_systems.chapter_system_features(chapter_id);
CREATE INDEX IF NOT EXISTS idx_chapter_features_feature ON support_systems.chapter_system_features(feature_id);

COMMENT ON TABLE support_systems.chapter_system_features IS 'Chapter-specific feature activation (e.g. enable IT-Sandbox only for Docker chapter)';

-- ============================================================================
-- SEED DATA: System Features
-- ============================================================================

INSERT INTO support_systems.system_features (feature_code, feature_name, description, category, requires_infrastructure, requires_external_service, icon, former_lm_id) VALUES
    -- Visualization Features
    ('mindmap_generator', 'Mindmap-Generator', 'Generiert kursweite Mindmaps aus Theorie-Inhalten', 'visualization', FALSE, FALSE, 'sitemap', NULL),

    -- Interactive Tools (früher Content-LMs)
    ('whiteboard_engine', 'Whiteboard-Engine', 'Interaktive Whiteboard-Aufgaben mit KI-Erkennung (Formeln, Diagramme, Keywords)', 'interactive_tools', TRUE, TRUE, 'pencil-ruler', 5),
    ('it_sandbox', 'IT-Sandbox', 'Praktische Übungen in simulierten IT-Umgebungen (Code, Config, Netzwerk, Terminal)', 'it_environments', TRUE, TRUE, 'laptop-code', 10),
    ('speech_to_text', 'Speech-to-Text Engine', 'Sprachaufnahme mit KI-Transkription & Bewertung', 'audio', TRUE, TRUE, 'microphone', 17),

    -- Meta-Features
    ('timer_wrapper', 'Timer/Zeitlimit-Feature', 'Zeitbegrenzung für beliebige Aufgaben (Meta-Feature)', 'meta_features', FALSE, FALSE, 'clock', 14),

    -- Exam & Assessment Systems
    ('ihk_exam_system', 'IHK-Prüfungssystem', 'Prüfungsaufgaben im IHK/Kammer-Format', 'exam_systems', TRUE, TRUE, 'certificate', 10),
    ('practical_exam_engine', 'Praxisprüfungs-Engine', 'Mehrstufige praktische Prüfungsaufgaben', 'exam_systems', TRUE, FALSE, 'clipboard-check', 11),
    ('chapter_completion_system', 'Kapitelabschluss-System', 'Umfassende Kapitelabschluss-Prüfung', 'exam_systems', FALSE, TRUE, 'trophy', 14),

    -- Tutor & Coaching
    ('npc_tutor', 'NPC-/Persona-Tutor', 'KI-basierter Tutor mit verschiedenen Rollen/Personas', 'tutor', FALSE, TRUE, 'user-graduate', NULL),
    ('socratic_dialog', 'Sokratischer Dialog', 'KI-geführter Dialog zur Wissensvermittlung', 'tutor', FALSE, TRUE, 'comments', NULL),
    ('comprehension_checker', 'Verständnis-Checker', 'Mikro-Checks basierend auf Bloom-Taxonomie', 'tutor', FALSE, TRUE, 'check-circle', 13),

    -- Gamification
    ('adaptive_difficulty', 'Adaptive Schwierigkeit', 'Passt Aufgabenschwierigkeit automatisch an Leistungsstand an', 'gamification', FALSE, FALSE, 'chart-line', NULL),
    ('xp_quest_system', 'XP & Quest System', 'Erfahrungspunkte, Level, Achievements, Daily Quests', 'gamification', FALSE, FALSE, 'trophy', NULL),
    ('daily_recall', 'Daily Recall', 'Tägliche Wiederholungslogik (Spaced Repetition)', 'gamification', FALSE, FALSE, 'calendar-check', NULL),

    -- Learning Paths
    ('learning_path_generator', 'Lernpfad-Generator', 'KI-gestützte Lernpfad-Erstellung und -Optimierung', 'learning_paths', FALSE, TRUE, 'route', NULL),

    -- Collaboration
    ('peer_instruction', 'Peer Instruction', 'Peer Instruction Methode (Think-Pair-Share)', 'collaboration', FALSE, FALSE, 'users', 26),
    ('peer_review', 'Peer Review', 'Gegenseitige Bewertung von Lösungen', 'collaboration', FALSE, FALSE, 'users', NULL),
    ('team_case', 'Team-Case', 'Kollaborative Fallbearbeitung', 'collaboration', FALSE, FALSE, 'people-carry', NULL),
    ('learning_journal', 'Lerntagebuch', 'Persönliche Reflexion und Dokumentation', 'collaboration', FALSE, FALSE, 'book', NULL),
    ('project_portfolio', 'Projekt-Portfolio', 'Sammlung eigener Projekte', 'collaboration', FALSE, FALSE, 'folder-open', NULL),
    ('project_based_learning', 'Projektbasiertes Lernen', 'Project-Based Learning Workflows', 'collaboration', FALSE, FALSE, 'tasks', 31),
    ('inverted_classroom', 'Inverted Classroom', 'Flipped Classroom Unterstützung', 'collaboration', FALSE, FALSE, 'chalkboard-teacher', NULL),

    -- IT Environments (specific types)
    ('code_sandbox', 'Code-Sandbox', 'Isolierte Code-Ausführungsumgebung', 'it_environments', TRUE, FALSE, 'code', NULL),
    ('network_simulation', 'Netzwerk-Simulation', 'Virtuelle Netzwerk-Topologien', 'it_environments', TRUE, FALSE, 'network-wired', NULL),
    ('terminal_access', 'Terminal-Zugriff', 'Web-basierter Terminal-Zugang', 'it_environments', TRUE, FALSE, 'terminal', NULL)
ON CONFLICT (feature_code) DO NOTHING;

-- ============================================================================
-- Helper Function: Get Active Features for Course
-- ============================================================================
CREATE OR REPLACE FUNCTION get_course_features(p_course_id UUID)
RETURNS TABLE (
    feature_code VARCHAR,
    feature_name VARCHAR,
    category VARCHAR,
    config JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        sf.feature_code,
        sf.feature_name,
        sf.category,
        COALESCE(csf.config_override, sf.config) as config
    FROM support_systems.system_features sf
    LEFT JOIN support_systems.course_system_features csf
        ON sf.feature_id = csf.feature_id AND csf.course_id = p_course_id
    WHERE sf.active = TRUE
      AND (csf.enabled IS NULL OR csf.enabled = TRUE);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_course_features IS 'Get all active features for a course (including defaults)';

-- ============================================================================
-- Helper Function: Get Active Features for Chapter
-- ============================================================================
CREATE OR REPLACE FUNCTION get_chapter_features(p_chapter_id UUID)
RETURNS TABLE (
    feature_code VARCHAR,
    feature_name VARCHAR,
    category VARCHAR,
    config JSONB
) AS $$
DECLARE
    v_course_id UUID;
BEGIN
    -- Get course_id from chapter
    SELECT course_id INTO v_course_id
    FROM courses.chapters
    WHERE chapter_id = p_chapter_id;

    RETURN QUERY
    SELECT
        sf.feature_code,
        sf.feature_name,
        sf.category,
        COALESCE(
            chsf.config_override,
            csf.config_override,
            sf.config
        ) as config
    FROM support_systems.system_features sf
    LEFT JOIN support_systems.course_system_features csf
        ON sf.feature_id = csf.feature_id AND csf.course_id = v_course_id
    LEFT JOIN support_systems.chapter_system_features chsf
        ON sf.feature_id = chsf.feature_id AND chsf.chapter_id = p_chapter_id
    WHERE sf.active = TRUE
      AND (csf.enabled IS NULL OR csf.enabled = TRUE)
      AND (chsf.enabled IS NULL OR chsf.enabled = TRUE);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_chapter_features IS 'Get all active features for a chapter (inherits from course + chapter-specific)';

-- ============================================================================
-- Triggers
-- ============================================================================
DROP TRIGGER IF EXISTS update_system_features_updated_at ON support_systems.system_features;
CREATE TRIGGER update_system_features_updated_at
    BEFORE UPDATE ON support_systems.system_features
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- End of Migration: 074_system_features.sql
-- ============================================================================
