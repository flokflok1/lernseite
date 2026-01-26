-- ============================================================================
-- Migration: 040_system_features_core.sql
-- Version: 1.0.0
-- Description: System-Features Core (25 Infrastructure-Features + Activation)
-- Author: LernsystemX Migration System
-- Date: 2026-01-26
-- Phase: 2 (Infrastructure Layer)
-- Dependencies: 000_schemas.sql (system_features schema)
--
-- ZENTRAL: Dies ist die EINZIGE Datei für System-Features-Strukturen
-- - System-Features (ERWEITERBAR): Tools/Services mit Infrastruktur-Anforderungen
-- - Per-Kurs Aktivierung: course_system_features
-- - Pro-Kapitel Aktivierung: chapter_system_features
--
-- DESIGN-PHILOSOPHIE: ERWEITERBAR, NICHT HARDCODED
-- - Keine Hardcoded Limit von 25 Features
-- - Neue Kategorien können hinzugefügt werden
-- - active Flag erlaubt Disabling ohne Datenverlust
-- - deprecated Flag für künftige Phasierung von Features
--
-- AKTUELL: 25 System-Features
-- ZUKÜNFTIG: Kann bei Bedarf erweitert werden
--
-- NICHT verwechseln mit Content-Lernmethoden (Flashcards, Multiple Choice, Code Challenge, etc.)!
-- Content-Lernmethoden sind in 04_LearningMethods/030_learning_methods_core.sql
-- ============================================================================

-- ============================================================================
-- TABLE: system_features.system_features
-- Description: Registry of all 25 System-Features (Tools/Services)
--
-- System-Features sind INFRASTRUKTUR-TOOLS mit eigenen Servern/APIs:
-- - math_patterns: Math pattern recognition engine
-- - whiteboard_engine: Interactive whiteboard with formula recognition
-- - code_sandbox: Container-based code execution
-- - npc_tutor: AI-powered tutor companion
-- - etc. (25 total)
--
-- Constraint: 25 Features total (nicht unbegrenzt erwerbbar)
-- ============================================================================

CREATE TABLE IF NOT EXISTS system_features.system_features (
    feature_id SERIAL PRIMARY KEY,
    feature_code VARCHAR(50) UNIQUE NOT NULL,
    feature_name VARCHAR(100) NOT NULL,
    description TEXT,

    -- Kategorisierung (ERWEITERBAR - neue Kategorien können hinzugefügt werden)
    category VARCHAR(50) NOT NULL,  -- 'interactive_tools', 'exam_systems', 'tutor_coaching', etc.

    -- Infrastruktur-Anforderungen
    requires_infrastructure BOOLEAN DEFAULT FALSE,  -- Braucht Container/GPU/WebRTC?
    requires_external_service BOOLEAN DEFAULT FALSE,  -- Braucht externe API?

    -- Konfiguration
    active BOOLEAN DEFAULT TRUE,  -- Allows disabling without deleting
    deprecated BOOLEAN DEFAULT FALSE,  -- For future features, mark old ones as deprecated
    config JSONB DEFAULT '{}',
    icon VARCHAR(50),

    -- Hinweis auf migierte LM-IDs (falls aus alteren LMs migriert)
    former_lm_id INTEGER,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- CONSTRAINTS - FLEXIBLE FOR EXTENSIBILITY
    -- Application logic enforces category whitelist, not database constraint
    CONSTRAINT chk_feature_code CHECK (feature_code ~ '^[a-z_]+$'),
    -- Categories can be extended: just add new strings as needed
    CONSTRAINT chk_category_format CHECK (category ~ '^[a-z_]+$'),
    CONSTRAINT chk_active_not_deprecated CHECK (NOT (active = FALSE AND deprecated = TRUE))
);

CREATE INDEX IF NOT EXISTS idx_system_features_code ON system_features.system_features(feature_code);
CREATE INDEX IF NOT EXISTS idx_system_features_category ON system_features.system_features(category);
CREATE INDEX IF NOT EXISTS idx_system_features_active ON system_features.system_features(active) WHERE active = TRUE;

COMMENT ON TABLE system_features.system_features IS '25 System-Features Registry (Infrastructure-Tools/Services, separate from Content-Lernmethoden)';
COMMENT ON COLUMN system_features.system_features.feature_code IS 'Unique identifier: math_patterns, whiteboard_engine, code_sandbox, npc_tutor, etc.';
COMMENT ON COLUMN system_features.system_features.requires_infrastructure IS 'TRUE wenn Feature Container/GPU/WebRTC/etc. braucht';
COMMENT ON COLUMN system_features.system_features.requires_external_service IS 'TRUE wenn externe API/Service erforderlich';

-- ============================================================================
-- TABLE: system_features.course_system_features
-- Description: Per-Kurs Aktivierung von System-Features mit Config-Override
--
-- Ermöglicht:
-- - Pro Kurs selective Aktivierung (nicht alle 25 Features pro Kurs)
-- - Course-spezifische Konfiguration (z.B. andere Tutor-Personality)
-- - Feature-Preise können pro Kurs überschrieben werden
-- ============================================================================

CREATE TABLE IF NOT EXISTS system_features.course_system_features (
    mapping_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID REFERENCES courses.courses(course_id) ON DELETE CASCADE,
    feature_id INTEGER REFERENCES system_features.system_features(feature_id) ON DELETE CASCADE,

    -- Feature-Aktivierung auf Kurs-Ebene
    enabled BOOLEAN DEFAULT TRUE,

    -- Kurs-spezifische Config-Overrides
    config_override JSONB DEFAULT '{}',

    -- Timestamps
    enabled_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- CONSTRAINTS
    UNIQUE(course_id, feature_id)
);

CREATE INDEX IF NOT EXISTS idx_course_system_features_course ON system_features.course_system_features(course_id);
CREATE INDEX IF NOT EXISTS idx_course_system_features_feature ON system_features.course_system_features(feature_id);
CREATE INDEX IF NOT EXISTS idx_course_system_features_enabled ON system_features.course_system_features(enabled) WHERE enabled = TRUE;

COMMENT ON TABLE system_features.course_system_features IS 'Per-Kurs Aktivierung und Konfiguration von System-Features';

-- ============================================================================
-- TABLE: system_features.chapter_system_features
-- Description: Pro-Kapitel Aktivierung von System-Features mit Config-Override
--
-- Ermöglicht:
-- - Noch feiner-granulare Steuerung auf Kapitel-Ebene
-- - Beispiel: Code Sandbox nur in "Python Kapitel", nicht in "Theory Kapitel"
-- - Chapter-spezifische Config (z.B. andere Whitelisted Libraries)
-- ============================================================================

CREATE TABLE IF NOT EXISTS system_features.chapter_system_features (
    mapping_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chapter_id UUID REFERENCES courses.chapters(chapter_id) ON DELETE CASCADE,
    feature_id INTEGER REFERENCES system_features.system_features(feature_id) ON DELETE CASCADE,

    -- Feature-Aktivierung auf Kapitel-Ebene
    enabled BOOLEAN DEFAULT TRUE,

    -- Kapitel-spezifische Config-Overrides
    config_override JSONB DEFAULT '{}',

    -- Timestamps
    enabled_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- CONSTRAINTS
    UNIQUE(chapter_id, feature_id)
);

CREATE INDEX IF NOT EXISTS idx_chapter_system_features_chapter ON system_features.chapter_system_features(chapter_id);
CREATE INDEX IF NOT EXISTS idx_chapter_system_features_feature ON system_features.chapter_system_features(feature_id);
CREATE INDEX IF NOT EXISTS idx_chapter_system_features_enabled ON system_features.chapter_system_features(enabled) WHERE enabled = TRUE;

COMMENT ON TABLE system_features.chapter_system_features IS 'Pro-Kapitel Aktivierung und Konfiguration von System-Features';

-- ============================================================================
-- SYSTEM-FEATURES CATEGORIES (25 Total)
--
-- Diese sind INFRASTRUKTUR-FEATURES, nicht Content-Lernmethoden!
--
-- Kategorien (9):
-- 1. Interactive Tools (3): math_patterns, whiteboard_engine, speech_to_text
-- 2. Exam Systems (4): ihk_exam_system, practical_exam_engine, comprehension_checker, chapter_completion
-- 3. Tutor & Coaching (2): npc_tutor, socratic_dialog
-- 4. Gamification (3): adaptive_difficulty, xp_quest_system, daily_recall
-- 5. Learning Paths (1): learning_path_generator
-- 6. Collaboration (7): peer_instruction, team_case, peer_review, learning_journal, project_portfolio, project_based_learning, inverted_classroom
-- 7. IT Environments (3): code_sandbox, network_simulation, terminal_access
-- 8. Visualization (1): mindmap_generator
-- 9. Meta Features (1): timer_wrapper
--
-- Total: 25 System-Features
-- ============================================================================

-- ============================================================================
-- End of Migration: 040_system_features_core.sql
-- ============================================================================
