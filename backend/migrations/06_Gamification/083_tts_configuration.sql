-- ============================================================================
-- Migration: 083_tts_configuration.sql
-- Version: 1.0.0
-- Description: Text-to-Speech (TTS) System Configuration
-- Author: LernsystemX Migration System
-- Date: 2026-01-26
-- Phase: 4 (System Features - Tutor TTS)
-- ============================================================================

-- ============================================================================
-- TABLE: support_systems.tts_configurations
-- Description: TTS voice and delivery settings per course/user
-- ============================================================================

CREATE TABLE IF NOT EXISTS support_systems.tts_configurations (
    config_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Scope
    scope VARCHAR(20) NOT NULL,  -- 'system', 'course', 'user'
    course_id UUID REFERENCES courses.courses(course_id) ON DELETE CASCADE,
    user_id UUID REFERENCES core.users(user_id) ON DELETE CASCADE,

    -- Provider configuration
    provider VARCHAR(50) NOT NULL DEFAULT 'google',  -- google, aws, azure, local
    provider_config JSONB DEFAULT '{}',  -- Provider-specific settings

    -- Voice selection
    voice_id VARCHAR(100) NOT NULL,
    language VARCHAR(10) DEFAULT 'de',
    accent VARCHAR(50),  -- regional variation

    -- Audio delivery settings
    speed DECIMAL(3,2) DEFAULT 1.0,  -- 0.5 (slow) to 2.0 (fast)
    pitch DECIMAL(3,2) DEFAULT 1.0,  -- 0.5 (low) to 2.0 (high)
    volume DECIMAL(3,2) DEFAULT 1.0,  -- 0.0 (silent) to 1.0 (normal)

    -- Pronunciation & phonetics
    use_phonetic_spelling BOOLEAN DEFAULT FALSE,
    phonetic_rules JSONB DEFAULT '{}',  -- Custom pronunciation rules

    -- Performance settings
    streaming_enabled BOOLEAN DEFAULT TRUE,  -- Stream audio as it's generated?
    cache_audio BOOLEAN DEFAULT TRUE,  -- Cache generated audio?
    max_cache_size_mb INTEGER DEFAULT 500,

    -- Quality settings
    audio_quality VARCHAR(20) DEFAULT 'high',  -- low, medium, high
    sample_rate INTEGER DEFAULT 22050,  -- Hz

    -- Content handling
    skip_punctuation BOOLEAN DEFAULT TRUE,  -- Don't read punctuation?
    convert_numbers_to_words BOOLEAN DEFAULT TRUE,  -- "123" → "one hundred twenty-three"?
    spell_acronyms BOOLEAN DEFAULT TRUE,  -- "USA" → "U S A"?

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    CONSTRAINT chk_scope CHECK (scope IN ('system', 'course', 'user')),
    CONSTRAINT chk_provider CHECK (provider IN ('google', 'aws', 'azure', 'local')),
    CONSTRAINT chk_speed CHECK (speed >= 0.5 AND speed <= 2.0),
    CONSTRAINT chk_pitch CHECK (pitch >= 0.5 AND pitch <= 2.0),
    CONSTRAINT chk_volume CHECK (volume >= 0.0 AND volume <= 1.0),
    CONSTRAINT chk_quality CHECK (audio_quality IN ('low', 'medium', 'high'))
);

CREATE INDEX IF NOT EXISTS idx_tts_config_scope ON support_systems.tts_configurations(scope);
CREATE INDEX IF NOT EXISTS idx_tts_config_course ON support_systems.tts_configurations(course_id);
CREATE INDEX IF NOT EXISTS idx_tts_config_user ON support_systems.tts_configurations(user_id);
CREATE INDEX IF NOT EXISTS idx_tts_config_language ON support_systems.tts_configurations(language);

COMMENT ON TABLE support_systems.tts_configurations IS 'TTS voice and delivery settings (global, course, or user level)';

-- ============================================================================
-- TABLE: support_systems.tts_voice_profiles
-- Description: Available TTS voices per language/provider
-- ============================================================================

CREATE TABLE IF NOT EXISTS support_systems.tts_voice_profiles (
    voice_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Identification
    provider_voice_id VARCHAR(100) NOT NULL,
    provider VARCHAR(50) NOT NULL,  -- google, aws, azure, local
    voice_name VARCHAR(100) NOT NULL,
    language VARCHAR(10) NOT NULL,

    -- Voice characteristics
    gender VARCHAR(20),  -- male, female, neutral
    age_impression VARCHAR(20),  -- child, young_adult, adult, senior
    accent_description VARCHAR(100),
    use_case VARCHAR(50),  -- tutoring, entertainment, professional, etc.

    -- Quality metrics
    naturalness_score DECIMAL(3,2),  -- 1-10
    clarity_score DECIMAL(3,2),  -- 1-10
    recommended_for_teaching BOOLEAN DEFAULT TRUE,

    -- Availability
    is_available BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE,

    -- Audio characteristics
    sample_audio_url VARCHAR(500),  -- URL to sample audio

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    CONSTRAINT chk_provider CHECK (provider IN ('google', 'aws', 'azure', 'local')),
    CONSTRAINT chk_gender CHECK (gender IN ('male', 'female', 'neutral')),
    UNIQUE(provider_voice_id, provider, language)
);

CREATE INDEX IF NOT EXISTS idx_tts_voice_profiles_language ON support_systems.tts_voice_profiles(language);
CREATE INDEX IF NOT EXISTS idx_tts_voice_profiles_provider ON support_systems.tts_voice_profiles(provider);
CREATE INDEX IF NOT EXISTS idx_tts_voice_profiles_available ON support_systems.tts_voice_profiles(is_available) WHERE is_available = TRUE;

COMMENT ON TABLE support_systems.tts_voice_profiles IS 'Catalog of available TTS voices from different providers';

-- ============================================================================
-- TABLE: support_systems.pronunciation_rules
-- Description: Custom pronunciation rules for specific words/acronyms
-- ============================================================================

CREATE TABLE IF NOT EXISTS support_systems.pronunciation_rules (
    rule_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    language VARCHAR(10) NOT NULL,

    -- What to match
    pattern VARCHAR(255) NOT NULL,
    pattern_type VARCHAR(50) DEFAULT 'literal',  -- literal, regex, phonetic
    case_sensitive BOOLEAN DEFAULT FALSE,

    -- How to pronounce
    phonetic_spelling VARCHAR(500) NOT NULL,
    pronunciation_hint TEXT,

    -- Category (for organization)
    category VARCHAR(50),  -- acronym, technical_term, place_name, person_name, etc.

    -- Priority (lower = applied first)
    priority INTEGER DEFAULT 100,

    -- Active?
    is_active BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    CONSTRAINT chk_pattern_type CHECK (pattern_type IN ('literal', 'regex', 'phonetic')),
    UNIQUE(language, pattern, pattern_type)
);

CREATE INDEX IF NOT EXISTS idx_pronunciation_rules_language ON support_systems.pronunciation_rules(language);
CREATE INDEX IF NOT EXISTS idx_pronunciation_rules_category ON support_systems.pronunciation_rules(category);
CREATE INDEX IF NOT EXISTS idx_pronunciation_rules_active ON support_systems.pronunciation_rules(is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_pronunciation_rules_priority ON support_systems.pronunciation_rules(priority ASC);

COMMENT ON TABLE support_systems.pronunciation_rules IS 'Custom pronunciation for words/acronyms (e.g., "USA" → "United States of America")';

-- ============================================================================
-- TABLE: support_systems.tts_synthesis_logs
-- Description: Log of generated TTS audio (for caching and analytics)
-- ============================================================================

CREATE TABLE IF NOT EXISTS support_systems.tts_synthesis_logs (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- What was synthesized
    input_text TEXT NOT NULL,
    output_audio_url VARCHAR(500),
    audio_duration_seconds DECIMAL(8,2),

    -- Configuration used
    voice_id UUID REFERENCES support_systems.tts_voice_profiles(voice_id) ON DELETE SET NULL,
    tts_config_id UUID REFERENCES support_systems.tts_configurations(config_id) ON DELETE SET NULL,

    -- Synthesis details
    provider VARCHAR(50),
    model_used VARCHAR(100),
    synthesis_time_ms INTEGER,

    -- Quality
    was_successful BOOLEAN DEFAULT TRUE,
    error_message TEXT,

    -- Usage
    times_used INTEGER DEFAULT 0,
    last_used_at TIMESTAMPTZ,

    -- Cache metadata
    is_cached BOOLEAN DEFAULT FALSE,
    cache_key VARCHAR(255),
    cache_size_kb INTEGER,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ  -- For cache expiration

);

CREATE INDEX IF NOT EXISTS idx_tts_logs_voice ON support_systems.tts_synthesis_logs(voice_id);
CREATE INDEX IF NOT EXISTS idx_tts_logs_created ON support_systems.tts_synthesis_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_tts_logs_cache_key ON support_systems.tts_synthesis_logs(cache_key);
CREATE INDEX IF NOT EXISTS idx_tts_logs_success ON support_systems.tts_synthesis_logs(was_successful);

COMMENT ON TABLE support_systems.tts_synthesis_logs IS 'Log of TTS synthesis operations (for caching, analytics, debugging)';

-- ============================================================================
-- TABLE: support_systems.tts_user_preferences
-- Description: Per-user TTS preferences
-- ============================================================================

CREATE TABLE IF NOT EXISTS support_systems.tts_user_preferences (
    pref_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,

    -- Voice preferences
    preferred_voice_id UUID REFERENCES support_systems.tts_voice_profiles(voice_id),
    preferred_language VARCHAR(10),

    -- Speed/pitch preferences
    preferred_speed DECIMAL(3,2) DEFAULT 1.0,
    preferred_pitch DECIMAL(3,2) DEFAULT 1.0,

    -- Accessibility
    use_tts_by_default BOOLEAN DEFAULT TRUE,
    auto_read_theory_sheets BOOLEAN DEFAULT FALSE,
    auto_read_instructions BOOLEAN DEFAULT TRUE,

    -- High contrast / other preferences
    additional_preferences JSONB DEFAULT '{}',

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    UNIQUE(user_id)
);

CREATE INDEX IF NOT EXISTS idx_tts_user_pref_user ON support_systems.tts_user_preferences(user_id);

COMMENT ON TABLE support_systems.tts_user_preferences IS 'Per-user TTS preferences (voice, speed, auto-read settings)';

-- ============================================================================
-- Function: get_tts_config()
-- Description: Get effective TTS configuration (respects hierarchy: user > course > system)
-- ============================================================================

CREATE OR REPLACE FUNCTION get_tts_config(p_user_id UUID, p_course_id UUID)
RETURNS TABLE (
    provider VARCHAR,
    voice_id VARCHAR,
    language VARCHAR,
    speed DECIMAL,
    pitch DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COALESCE(uc.provider, cc.provider, sc.provider) as provider,
        COALESCE(uc.voice_id, cc.voice_id, sc.voice_id) as voice_id,
        COALESCE(uc.language, cc.language, sc.language) as language,
        COALESCE(uc.speed, cc.speed, sc.speed) as speed,
        COALESCE(uc.pitch, cc.pitch, sc.pitch) as pitch
    FROM
        support_systems.tts_configurations sc  -- system-level
        LEFT JOIN support_systems.tts_configurations cc
            ON cc.scope = 'course' AND cc.course_id = p_course_id
        LEFT JOIN support_systems.tts_configurations uc
            ON uc.scope = 'user' AND uc.user_id = p_user_id
    WHERE sc.scope = 'system'
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- End of Migration: 083_tts_configuration.sql
-- ============================================================================
