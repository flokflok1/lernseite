-- ============================================================================
-- Migration: 070_system_features.sql
-- Version: 1.0.0
-- Description: System-Features Registry (25 Features - Non-Content Infrastructure)
-- Author: LernsystemX Migration System
-- Date: 2026-01-26
-- Phase: 4 (System Features - Separate from Content-Lernmethoden)
-- Dependencies: 000_schemas.sql (system_features schema)
-- ============================================================================

-- ============================================================================
-- TABLE: system_features.system_features
-- Description: Registry of all 25 System-Features (Tools/Services with Infrastructure)
--
-- System-Features are different from Content-Lernmethoden (LM00-LM11):
-- - Content-LMs: Task formats (Flashcards, Quiz, etc.) - no infrastructure needed
-- - System-Features: Tools/Services with own infrastructure (Math Patterns, Code Sandbox, etc.)
-- ============================================================================

CREATE TABLE IF NOT EXISTS system_features.system_features (
    feature_id SERIAL PRIMARY KEY,
    feature_code VARCHAR(50) UNIQUE NOT NULL,
    feature_name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,

    -- Infrastructure requirements
    requires_infrastructure BOOLEAN DEFAULT FALSE,
    requires_external_service BOOLEAN DEFAULT FALSE,

    -- Configuration
    active BOOLEAN DEFAULT TRUE,
    config JSONB DEFAULT '{}',
    icon VARCHAR(50),

    -- Reference to former LM (if migrated from older structure)
    former_lm_id INTEGER,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    CONSTRAINT chk_feature_code CHECK (feature_code ~ '^[a-z_]+$'),
    CONSTRAINT chk_category CHECK (category IN (
        'interactive_tools',
        'exam_systems',
        'tutor_coaching',
        'gamification',
        'learning_paths',
        'collaboration',
        'it_environments',
        'visualization',
        'meta_features'
    ))
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_system_features_code ON system_features.system_features(feature_code);
CREATE INDEX IF NOT EXISTS idx_system_features_category ON system_features.system_features(category);
CREATE INDEX IF NOT EXISTS idx_system_features_active ON system_features.system_features(active) WHERE active = TRUE;

COMMENT ON TABLE system_features.system_features IS 'Registry of 25 System-Features (Tools/Services separate from Content-Lernmethoden)';
COMMENT ON COLUMN system_features.system_features.feature_code IS 'Unique identifier: math_patterns, whiteboard_engine, code_sandbox, etc.';
COMMENT ON COLUMN system_features.system_features.requires_infrastructure IS 'TRUE if feature needs Container/GPU/WebRTC/etc.';

-- ============================================================================
-- TABLE: system_features.course_system_features
-- Description: Per-course activation of System-Features with override config
-- ============================================================================

CREATE TABLE IF NOT EXISTS system_features.course_system_features (
    mapping_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID REFERENCES courses.courses(course_id) ON DELETE CASCADE,
    feature_id INTEGER REFERENCES system_features.system_features(feature_id) ON DELETE CASCADE,

    -- Feature enabled at course level
    enabled BOOLEAN DEFAULT TRUE,

    -- Course-specific override config
    config_override JSONB DEFAULT '{}',

    -- Timestamps
    enabled_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    UNIQUE(course_id, feature_id)
);

CREATE INDEX IF NOT EXISTS idx_course_system_features_course ON system_features.course_system_features(course_id);
CREATE INDEX IF NOT EXISTS idx_course_system_features_feature ON system_features.course_system_features(feature_id);
CREATE INDEX IF NOT EXISTS idx_course_system_features_enabled ON system_features.course_system_features(enabled) WHERE enabled = TRUE;

COMMENT ON TABLE system_features.course_system_features IS 'Per-course activation and configuration of System-Features';

-- ============================================================================
-- TABLE: system_features.chapter_system_features
-- Description: Per-chapter activation of System-Features with override config
-- ============================================================================

CREATE TABLE IF NOT EXISTS system_features.chapter_system_features (
    mapping_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chapter_id UUID REFERENCES courses.chapters(chapter_id) ON DELETE CASCADE,
    feature_id INTEGER REFERENCES system_features.system_features(feature_id) ON DELETE CASCADE,

    -- Feature enabled at chapter level
    enabled BOOLEAN DEFAULT TRUE,

    -- Chapter-specific override config
    config_override JSONB DEFAULT '{}',

    -- Timestamps
    enabled_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    UNIQUE(chapter_id, feature_id)
);

CREATE INDEX IF NOT EXISTS idx_chapter_system_features_chapter ON support_systems.chapter_system_features(chapter_id);
CREATE INDEX IF NOT EXISTS idx_chapter_system_features_feature ON support_systems.chapter_system_features(feature_id);
CREATE INDEX IF NOT EXISTS idx_chapter_system_features_enabled ON support_systems.chapter_system_features(enabled) WHERE enabled = TRUE;

COMMENT ON TABLE support_systems.chapter_system_features IS 'Per-chapter activation and configuration of System-Features';

-- ============================================================================
-- SYSTEM-FEATURES CATEGORIES (25 Total)
--
-- These are INFRASTRUCTURE FEATURES, not Content-Lernmethoden!
--
-- Kategorien:
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
-- End of Migration: 070_system_features.sql
-- ============================================================================
