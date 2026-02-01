-- ============================================================================
-- Migration: 084_i18n_core_tables.sql
-- Description: Core i18n tables and views
--              - Content translations table
--              - i18n key management (namespaces, keys, translations)
--              - Community suggestions with voting
--              - Translation requests
--              - AI quality reviews
--              - Moderation queue
--              - Progress views
-- Version: 2.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-01-16
-- ============================================================================
--
-- Part 1 of 5-part i18n system (split from 038_i18n_complete.sql)
-- Other parts: 085 (languages), 086 (sync), 087 (triggers), 088 (namespaces)
--
-- ============================================================================

BEGIN;

-- ============================================================================
-- 0. PREREQUISITES: Extensions and Schema
-- ============================================================================

-- Create UUID extension if not exists
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- NOTE: translations schema is created in 01_Core/000_schemas.sql
-- No schema creation needed here

-- ============================================================================
-- 1. TABLE: translations (Content translations)
-- ============================================================================
CREATE TABLE IF NOT EXISTS translations.translations (
    translation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_type VARCHAR(50) NOT NULL,
    content_id UUID NOT NULL,
    language VARCHAR(10) NOT NULL,
    translated_json JSONB NOT NULL,
    source_language VARCHAR(10),
    translation_provider VARCHAR(50),
    version INTEGER DEFAULT 1,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_translation_content_type CHECK (content_type IN ('course', 'chapter', 'theory', 'method', 'lesson', 'exam', 'notification')),
    CONSTRAINT chk_translation_status CHECK (status IN ('active', 'draft', 'archived', 'deleted')),
    CONSTRAINT chk_translation_version CHECK (version > 0)
);

CREATE INDEX IF NOT EXISTS idx_translations_content ON translations.translations(content_type, content_id);
CREATE INDEX IF NOT EXISTS idx_translations_language ON translations.translations(language);
CREATE INDEX IF NOT EXISTS idx_translations_status ON translations.translations(status);
CREATE INDEX IF NOT EXISTS idx_translations_created_at ON translations.translations(created_at DESC);

COMMENT ON TABLE translations.translations IS 'Stores translations for all translatable content (courses, lessons, etc.)';
COMMENT ON COLUMN translations.translations.translated_json IS 'Full translated content in JSONB format';
COMMENT ON COLUMN translations.translations.translation_provider IS 'e.g., deepl, google_translate, anthropic, manual';

-- ============================================================================
-- 2. TABLE: translation_cache (Performance cache)
-- ============================================================================
CREATE TABLE IF NOT EXISTS translations.translation_cache (
    cache_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cache_key VARCHAR(255) NOT NULL UNIQUE,
    content_type VARCHAR(50) NOT NULL,
    content_id UUID NOT NULL,
    language VARCHAR(10) NOT NULL,
    cached_json JSONB NOT NULL,
    ttl_seconds INTEGER DEFAULT 3600,
    expires_at TIMESTAMPTZ,
    hit_count INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_translation_cache_key ON translations.translation_cache(cache_key);
CREATE INDEX IF NOT EXISTS idx_translation_cache_expires ON translations.translation_cache(expires_at);
CREATE INDEX IF NOT EXISTS idx_translation_cache_content ON translations.translation_cache(content_type, content_id, language);

COMMENT ON TABLE translations.translation_cache IS 'High-performance cache for frequently accessed translations';

-- ============================================================================
-- 3. TABLE: supported_languages (20 languages config)
-- ============================================================================
CREATE TABLE IF NOT EXISTS translations.supported_languages (
    language_code VARCHAR(10) PRIMARY KEY,
    language_name VARCHAR(100) NOT NULL,
    native_name VARCHAR(100) NOT NULL,
    flag VARCHAR(10) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    is_rtl BOOLEAN DEFAULT false,
    priority INTEGER DEFAULT 10,
    total_keys INTEGER DEFAULT 0,
    translated_keys INTEGER DEFAULT 0,
    completion_percent DECIMAL(5,2) DEFAULT 0.00,
    last_sync_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_supported_languages_active ON translations.supported_languages(is_active, priority);

COMMENT ON TABLE translations.supported_languages IS 'Configuration for all supported UI languages';
COMMENT ON COLUMN translations.supported_languages.priority IS 'Display order (1=highest, DE=1, PL=2, EN=3)';
COMMENT ON COLUMN translations.supported_languages.completion_percent IS 'Auto-calculated translation progress';

-- ============================================================================
-- 4. TABLE: i18n_namespaces (Translation key namespaces)
-- ============================================================================
CREATE TABLE IF NOT EXISTS translations.i18n_namespaces (
    namespace_code VARCHAR(100) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    icon VARCHAR(10),
    sort_order INTEGER DEFAULT 100,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_i18n_namespaces_active ON translations.i18n_namespaces(is_active, sort_order);

COMMENT ON TABLE translations.i18n_namespaces IS 'Organizes translation keys by functional area (admin, courses, etc.)';
COMMENT ON COLUMN translations.i18n_namespaces.namespace_code IS 'e.g., admin, courses, dashboard, errors';

-- ============================================================================
-- 5. TABLE: i18n_keys (Translatable text keys)
-- ============================================================================
CREATE TABLE IF NOT EXISTS translations.i18n_keys (
    key_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    namespace_code VARCHAR(100) NOT NULL REFERENCES translations.i18n_namespaces(namespace_code) ON DELETE CASCADE,
    key_path VARCHAR(500) NOT NULL,
    default_value TEXT NOT NULL,
    description TEXT,
    context TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_i18n_keys_namespace_path UNIQUE (namespace_code, key_path)
);

CREATE INDEX IF NOT EXISTS idx_i18n_keys_namespace ON translations.i18n_keys(namespace_code);
CREATE INDEX IF NOT EXISTS idx_i18n_keys_path ON translations.i18n_keys(key_path);
CREATE INDEX IF NOT EXISTS idx_i18n_keys_active ON translations.i18n_keys(is_active);

COMMENT ON TABLE translations.i18n_keys IS 'Master list of all translatable UI text keys';
COMMENT ON COLUMN translations.i18n_keys.key_path IS 'Dot-notation path, e.g., admin.users.title';
COMMENT ON COLUMN translations.i18n_keys.default_value IS 'Default text (usually German)';

-- ============================================================================
-- 6. TABLE: i18n_translations (Actual translations)
-- ============================================================================
CREATE TABLE IF NOT EXISTS translations.i18n_translations (
    translation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key_id UUID NOT NULL REFERENCES translations.i18n_keys(key_id) ON DELETE CASCADE,
    language_code VARCHAR(10) NOT NULL REFERENCES translations.supported_languages(language_code) ON DELETE CASCADE,
    translated_value TEXT NOT NULL,
    translation_source VARCHAR(50) DEFAULT 'manual',
    translator_user_id UUID,
    quality_score DECIMAL(3,2),
    is_verified BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_i18n_translations_key_lang UNIQUE (key_id, language_code),
    CONSTRAINT chk_i18n_translations_source CHECK (translation_source IN ('manual', 'deepl', 'gpt4', 'community', 'imported'))
);

CREATE INDEX IF NOT EXISTS idx_i18n_translations_key ON translations.i18n_translations(key_id);
CREATE INDEX IF NOT EXISTS idx_i18n_translations_language ON translations.i18n_translations(language_code);
CREATE INDEX IF NOT EXISTS idx_i18n_translations_verified ON translations.i18n_translations(is_verified, is_active);

COMMENT ON TABLE translations.i18n_translations IS 'Stores actual translated text for each key and language';
COMMENT ON COLUMN translations.i18n_translations.quality_score IS 'AI-calculated quality score (0.00-1.00)';

-- ============================================================================
-- 7. TABLE: i18n_suggestions (Community translation suggestions)
-- ============================================================================
CREATE TABLE IF NOT EXISTS translations.i18n_suggestions (
    suggestion_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key_id UUID NOT NULL REFERENCES translations.i18n_keys(key_id) ON DELETE CASCADE,
    language_code VARCHAR(10) NOT NULL REFERENCES translations.supported_languages(language_code) ON DELETE CASCADE,
    suggested_value TEXT NOT NULL,
    reason TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    upvotes INTEGER DEFAULT 0,
    downvotes INTEGER DEFAULT 0,
    submitted_by_user_id UUID NOT NULL,
    reviewed_by_user_id UUID,
    reviewed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_i18n_suggestions_status CHECK (status IN ('pending', 'approved', 'rejected', 'implemented'))
);

CREATE INDEX IF NOT EXISTS idx_i18n_suggestions_key ON translations.i18n_suggestions(key_id);
CREATE INDEX IF NOT EXISTS idx_i18n_suggestions_status ON translations.i18n_suggestions(status);
CREATE INDEX IF NOT EXISTS idx_i18n_suggestions_user ON translations.i18n_suggestions(submitted_by_user_id);

COMMENT ON TABLE translations.i18n_suggestions IS 'Community-submitted translation improvements';

-- ============================================================================
-- 8. TABLE: i18n_suggestion_votes (Voting system)
-- ============================================================================
CREATE TABLE IF NOT EXISTS translations.i18n_suggestion_votes (
    vote_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    suggestion_id UUID NOT NULL REFERENCES translations.i18n_suggestions(suggestion_id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    vote_type VARCHAR(10) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_i18n_votes_user_suggestion UNIQUE (suggestion_id, user_id),
    CONSTRAINT chk_i18n_votes_type CHECK (vote_type IN ('upvote', 'downvote'))
);

CREATE INDEX IF NOT EXISTS idx_i18n_votes_suggestion ON translations.i18n_suggestion_votes(suggestion_id);
CREATE INDEX IF NOT EXISTS idx_i18n_votes_user ON translations.i18n_suggestion_votes(user_id);

COMMENT ON TABLE translations.i18n_suggestion_votes IS 'User votes on translation suggestions';

-- ============================================================================
-- 9. TABLE: i18n_translation_requests (On-demand requests)
-- ============================================================================
CREATE TABLE IF NOT EXISTS translations.i18n_translation_requests (
    request_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key_id UUID NOT NULL REFERENCES translations.i18n_keys(key_id) ON DELETE CASCADE,
    target_language VARCHAR(10) NOT NULL REFERENCES translations.supported_languages(language_code) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'pending',
    priority VARCHAR(10) DEFAULT 'normal',
    requested_by_user_id UUID NOT NULL,
    assigned_to_user_id UUID,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_i18n_requests_status CHECK (status IN ('pending', 'assigned', 'completed', 'cancelled')),
    CONSTRAINT chk_i18n_requests_priority CHECK (priority IN ('low', 'normal', 'high', 'urgent'))
);

CREATE INDEX IF NOT EXISTS idx_i18n_requests_key ON translations.i18n_translation_requests(key_id);
CREATE INDEX IF NOT EXISTS idx_i18n_requests_status ON translations.i18n_translation_requests(status);
CREATE INDEX IF NOT EXISTS idx_i18n_requests_assigned ON translations.i18n_translation_requests(assigned_to_user_id);

COMMENT ON TABLE translations.i18n_translation_requests IS 'User requests for missing translations';

-- ============================================================================
-- 10. TABLE: i18n_ai_reviews (AI quality reviews)
-- ============================================================================
CREATE TABLE IF NOT EXISTS translations.i18n_ai_reviews (
    review_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    translation_id UUID NOT NULL REFERENCES translations.i18n_translations(translation_id) ON DELETE CASCADE,
    ai_model VARCHAR(50) NOT NULL,
    quality_score DECIMAL(3,2) NOT NULL,
    confidence_score DECIMAL(3,2),
    issues_found JSONB DEFAULT '[]',
    suggestions JSONB DEFAULT '[]',
    reviewed_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_i18n_ai_quality CHECK (quality_score BETWEEN 0.00 AND 1.00),
    CONSTRAINT chk_i18n_ai_confidence CHECK (confidence_score IS NULL OR (confidence_score BETWEEN 0.00 AND 1.00))
);

CREATE INDEX IF NOT EXISTS idx_i18n_ai_reviews_translation ON translations.i18n_ai_reviews(translation_id);
CREATE INDEX IF NOT EXISTS idx_i18n_ai_reviews_model ON translations.i18n_ai_reviews(ai_model);
CREATE INDEX IF NOT EXISTS idx_i18n_ai_reviews_quality ON translations.i18n_ai_reviews(quality_score);

COMMENT ON TABLE translations.i18n_ai_reviews IS 'AI-powered quality reviews (GPT-4, Claude, etc.)';
COMMENT ON COLUMN translations.i18n_ai_reviews.issues_found IS 'Array of detected issues (grammar, context, etc.)';

-- ============================================================================
-- 11. TABLE: i18n_moderation_queue (Moderation workflow)
-- ============================================================================
CREATE TABLE IF NOT EXISTS translations.i18n_moderation_queue (
    queue_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_type VARCHAR(20) NOT NULL,
    content_id UUID NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    priority VARCHAR(10) DEFAULT 'normal',
    flagged_reason TEXT,
    ai_recommendation VARCHAR(20),
    ai_confidence DECIMAL(3,2),
    assigned_to_moderator_id UUID,
    moderator_decision VARCHAR(20),
    moderator_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    reviewed_at TIMESTAMPTZ,
    CONSTRAINT chk_i18n_mod_content_type CHECK (content_type IN ('translation', 'suggestion', 'key')),
    CONSTRAINT chk_i18n_mod_status CHECK (status IN ('pending', 'assigned', 'approved', 'rejected', 'flagged')),
    CONSTRAINT chk_i18n_mod_priority CHECK (priority IN ('low', 'normal', 'high', 'urgent'))
);

CREATE INDEX IF NOT EXISTS idx_i18n_mod_queue_status ON translations.i18n_moderation_queue(status);
CREATE INDEX IF NOT EXISTS idx_i18n_mod_queue_assigned ON translations.i18n_moderation_queue(assigned_to_moderator_id);
CREATE INDEX IF NOT EXISTS idx_i18n_mod_queue_created ON translations.i18n_moderation_queue(created_at DESC);

COMMENT ON TABLE translations.i18n_moderation_queue IS 'Queue for moderating translations and suggestions';

-- ============================================================================
-- 12. TABLE: i18n_ai_config (AI moderation settings)
-- ============================================================================
CREATE TABLE IF NOT EXISTS translations.i18n_ai_config (
    config_key VARCHAR(100) PRIMARY KEY,
    config_value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE translations.i18n_ai_config IS 'Configuration for AI moderation (thresholds, models, etc.)';

-- Insert default AI config
INSERT INTO translations.i18n_ai_config (config_key, config_value, description) VALUES
    ('ai_model_primary', 'gpt-4o', 'Primary AI model for translation quality review'),
    ('ai_model_fallback', 'gpt-5.2', 'Fallback AI model if primary fails'),
    ('quality_threshold_min', '0.70', 'Minimum quality score to pass (0.00-1.00)'),
    ('quality_threshold_warn', '0.85', 'Quality score below this triggers warning'),
    ('confidence_threshold', '0.80', 'Minimum confidence for auto-approval'),
    ('auto_approve_enabled', 'false', 'Auto-approve high-quality translations'),
    ('batch_size', '50', 'Number of translations to review in one batch'),
    ('rate_limit_per_minute', '100', 'Max AI API calls per minute')
ON CONFLICT (config_key) DO NOTHING;

-- ============================================================================
-- 13. VIEWS: Progress and Analytics
-- ============================================================================

-- View: Language Progress
CREATE OR REPLACE VIEW translations.v_i18n_language_progress AS
SELECT
    sl.language_code,
    sl.language_name,
    sl.native_name,
    sl.flag,
    sl.total_keys,
    sl.translated_keys,
    sl.completion_percent,
    COUNT(DISTINCT t.translation_id) FILTER (WHERE t.is_verified) AS verified_count,
    COUNT(DISTINCT s.suggestion_id) FILTER (WHERE s.status = 'pending') AS pending_suggestions,
    sl.last_sync_at,
    sl.updated_at
FROM translations.supported_languages sl
LEFT JOIN translations.i18n_translations t ON sl.language_code = t.language_code AND t.is_active = true
LEFT JOIN translations.i18n_suggestions s ON sl.language_code = s.language_code
WHERE sl.is_active = true
GROUP BY sl.language_code, sl.language_name, sl.native_name, sl.flag,
         sl.total_keys, sl.translated_keys, sl.completion_percent,
         sl.last_sync_at, sl.updated_at
ORDER BY sl.priority;

-- View: Missing Translations
CREATE OR REPLACE VIEW translations.v_i18n_missing_translations AS
SELECT
    k.namespace_code,
    k.key_path,
    k.default_value,
    k.description,
    sl.language_code,
    sl.language_name,
    CASE WHEN t.translation_id IS NULL THEN true ELSE false END AS is_missing
FROM translations.i18n_keys k
CROSS JOIN translations.supported_languages sl
LEFT JOIN translations.i18n_translations t
    ON k.key_id = t.key_id
    AND sl.language_code = t.language_code
    AND t.is_active = true
WHERE k.is_active = true
  AND sl.is_active = true
  AND t.translation_id IS NULL
ORDER BY k.namespace_code, k.key_path, sl.priority;

-- View: Moderation Dashboard
CREATE OR REPLACE VIEW translations.v_i18n_moderation_dashboard AS
SELECT
    mq.queue_id,
    mq.content_type,
    mq.content_id,
    mq.status,
    mq.priority,
    mq.flagged_reason,
    mq.ai_recommendation,
    mq.ai_confidence,
    mq.assigned_to_moderator_id,
    mq.created_at,
    CASE
        WHEN mq.content_type = 'translation' THEN (
            SELECT CONCAT(k.namespace_code, '.', k.key_path)
            FROM translations.i18n_translations t
            JOIN translations.i18n_keys k ON t.key_id = k.key_id
            WHERE t.translation_id = mq.content_id
        )
        WHEN mq.content_type = 'suggestion' THEN (
            SELECT CONCAT(k.namespace_code, '.', k.key_path)
            FROM translations.i18n_suggestions s
            JOIN translations.i18n_keys k ON s.key_id = k.key_id
            WHERE s.suggestion_id = mq.content_id
        )
    END AS key_path
FROM translations.i18n_moderation_queue mq
WHERE mq.status IN ('pending', 'assigned')
ORDER BY
    CASE mq.priority
        WHEN 'urgent' THEN 1
        WHEN 'high' THEN 2
        WHEN 'normal' THEN 3
        WHEN 'low' THEN 4
    END,
    mq.created_at;

COMMIT;

-- ============================================================================
-- END MIGRATION 084 (i18n Core Tables)
-- ============================================================================
