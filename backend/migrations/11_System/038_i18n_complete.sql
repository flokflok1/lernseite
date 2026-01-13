-- ============================================================================
-- Migration: 038_i18n_complete.sql
-- Description: Complete internationalization (i18n) system
--              - Content translations (seed data for 3 primary languages)
--              - i18n key management with namespaces
--              - Community translation suggestions with voting
--              - AI-powered moderation and quality review
--              - Primary languages: DE, PL, EN (matching frontend locales)
-- Version: 2.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-01-13
-- ============================================================================
--
-- CONSOLIDATION NOTE:
-- This migration combines:
--   - Original 038_translations.sql (basic tables + 20 language seed)
--   - Original 072_i18n_system.sql (advanced i18n system + AI moderation)
--
-- Reason: Both migrations modify translations.supported_languages table
-- Per Migration Rules: Related schema changes must be in single file
-- Old migrations 038, 072, 077 should be marked @deprecated after this runs
--
-- ============================================================================

-- ============================================================================
-- 0. PREREQUISITES: Extensions and Schema
-- ============================================================================

-- Create UUID extension if not exists
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create translations schema if not exists
CREATE SCHEMA IF NOT EXISTS translations;

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
    CONSTRAINT chk_translation_status CHECK (status IN ('active', 'draft', 'outdated', 'deleted')),
    UNIQUE (content_type, content_id, language)
);

CREATE INDEX IF NOT EXISTS idx_translations_content ON translations.translations (content_type, content_id);
CREATE INDEX IF NOT EXISTS idx_translations_language ON translations.translations (language);
CREATE INDEX IF NOT EXISTS idx_translations_status ON translations.translations (status) WHERE status = 'active';

COMMENT ON TABLE translations.translations IS 'Multi-language translations for all content (20 languages via DeepL)';
COMMENT ON COLUMN translations.translations.translated_json IS 'JSONB: translated fields (title, description, content, etc.)';

-- ============================================================================
-- 2. TABLE: translation_cache (Performance cache)
-- ============================================================================
CREATE TABLE IF NOT EXISTS translations.translation_cache (
    cache_id BIGSERIAL PRIMARY KEY,
    source_text_hash VARCHAR(64) NOT NULL,
    source_language VARCHAR(10) NOT NULL,
    target_language VARCHAR(10) NOT NULL,
    translated_text TEXT NOT NULL,
    provider VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (source_text_hash, source_language, target_language)
);

CREATE INDEX IF NOT EXISTS idx_translation_cache_hash ON translations.translation_cache (source_text_hash, target_language);
CREATE INDEX IF NOT EXISTS idx_translation_cache_languages ON translations.translation_cache (source_language, target_language);

COMMENT ON TABLE translations.translation_cache IS 'Translation cache to avoid redundant API calls';

-- ============================================================================
-- 3. TABLE: supported_languages (Language configuration - 20 languages)
-- ============================================================================
CREATE TABLE IF NOT EXISTS translations.supported_languages (
    language_code VARCHAR(10) PRIMARY KEY,
    language_name VARCHAR(100) NOT NULL,
    native_name VARCHAR(100) NOT NULL,
    flag_emoji VARCHAR(10),
    rtl BOOLEAN DEFAULT FALSE,
    is_primary BOOLEAN DEFAULT FALSE,
    priority INTEGER DEFAULT 100,
    fallback_language VARCHAR(10),
    auto_translate BOOLEAN DEFAULT TRUE,
    community_editable BOOLEAN DEFAULT TRUE,
    completion_percent DECIMAL(5,2) DEFAULT 0,
    total_keys INTEGER DEFAULT 0,
    translated_keys INTEGER DEFAULT 0,
    community_contributions INTEGER DEFAULT 0,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_supported_languages_active ON translations.supported_languages (active) WHERE active = TRUE;
CREATE INDEX IF NOT EXISTS idx_supported_languages_primary ON translations.supported_languages (is_primary) WHERE is_primary = TRUE;
CREATE INDEX IF NOT EXISTS idx_supported_languages_priority ON translations.supported_languages (priority);

COMMENT ON TABLE translations.supported_languages IS 'Supported languages for the platform (3 primary languages: DE, PL, EN matching frontend locales)';

-- ============================================================================
-- SEED: Supported Languages (3 primary languages: DE, PL, EN)
-- ============================================================================
INSERT INTO translations.supported_languages
    (language_code, language_name, native_name, flag_emoji, active, is_primary, priority, fallback_language, auto_translate, community_editable)
VALUES
    ('de', 'German', 'Deutsch', '🇩🇪', true, true, 1, NULL, false, true),
    ('pl', 'Polish', 'Polski', '🇵🇱', true, true, 2, 'de', false, true),
    ('en', 'English', 'English', '🇬🇧', true, true, 3, 'de', false, true)
ON CONFLICT (language_code) DO UPDATE SET
    language_name = EXCLUDED.language_name,
    native_name = EXCLUDED.native_name,
    flag_emoji = EXCLUDED.flag_emoji,
    is_primary = EXCLUDED.is_primary,
    priority = EXCLUDED.priority,
    fallback_language = EXCLUDED.fallback_language,
    auto_translate = EXCLUDED.auto_translate,
    community_editable = EXCLUDED.community_editable,
    active = EXCLUDED.active,
    updated_at = NOW();

-- ============================================================================
-- 4. TABLE: i18n_namespaces (Translation key namespaces)
-- ============================================================================
CREATE TABLE IF NOT EXISTS translations.i18n_namespaces (
    namespace_id SERIAL PRIMARY KEY,
    namespace_code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    icon VARCHAR(50),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_i18n_namespaces_code ON translations.i18n_namespaces (namespace_code);
CREATE INDEX IF NOT EXISTS idx_i18n_namespaces_active ON translations.i18n_namespaces (is_active) WHERE is_active = TRUE;

COMMENT ON TABLE translations.i18n_namespaces IS 'Namespaces for i18n-Keys (common, auth, dashboard, admin, courses, errors, emails, etc.)';

-- ============================================================================
-- SEED: Standard Namespaces
-- ============================================================================
INSERT INTO translations.i18n_namespaces (namespace_code, name, description, icon, sort_order)
VALUES
    ('admin', 'Administration', 'Admin-Panel, Einstellungen', '⚙️', 80),
    ('common', 'Allgemein', 'Allgemeine UI-Elemente (Buttons, Labels, etc.)', '🔤', 10),
    ('courses', 'Kurse', 'Kurs-Übersicht, Kurs-Details, Lektionen', '📚', 50),
    ('dashboard', 'Dashboard', 'Dashboard-Widgets und Übersichten', '📊', 40),
    ('errors', 'Fehler', 'Fehlermeldungen, Validierung', '⚠️', 140),
    ('legal', 'Rechtliches', 'Datenschutz, Impressum, Nutzungsbedingungen', '⚖️', 175),
    ('setup', 'Setup', 'Setup-Wizard, Initialisierung', '🔧', 180),
    ('tutor', 'Tutor', 'KI-Tutor, Assistenzen', '🎓', 185),
    ('windows', 'Fenster/UI', 'Lernmethoden, AI-Studio, Viewer Windows', '🪟', 190),
    ('auth', 'Authentifizierung', 'Login, Registrierung, Passwort-Reset', '🔐', 20),
    ('navigation', 'Navigation', 'Menüs, Breadcrumbs, Links', '🧭', 30),
    ('player', 'Lern-Player', 'Lernmethoden-Player, Quiz, Übungen', '▶️', 60),
    ('editor', 'Editor', 'Kurs-Editor, Content-Erstellung', '✏️', 70),
    ('ai_studio', 'KI-Studio', 'KI-Authoring, Chat, Generierung', '🤖', 90),
    ('profile', 'Profil', 'Benutzer-Profil, Einstellungen', '👤', 100),
    ('org', 'Organisation', 'Schul-/Unternehmens-Verwaltung', '🏢', 110),
    ('notifications', 'Benachrichtigungen', 'System-Benachrichtigungen, Alerts', '🔔', 120),
    ('emails', 'E-Mails', 'E-Mail-Templates', '📧', 130),
    ('tooltips', 'Tooltips', 'Hilfetexte, Erklärungen', '💡', 150),
    ('dates', 'Datum/Zeit', 'Datumsformate, Zeitangaben', '📅', 160),
    ('numbers', 'Zahlen', 'Zahlenformate, Währung', '🔢', 170)
ON CONFLICT (namespace_code) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    icon = EXCLUDED.icon,
    sort_order = EXCLUDED.sort_order,
    updated_at = NOW();

-- ============================================================================
-- 5. TABLE: i18n_keys (Translatable text keys)
-- ============================================================================
CREATE TABLE IF NOT EXISTS translations.i18n_keys (
    key_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    namespace_id INTEGER NOT NULL REFERENCES translations.i18n_namespaces(namespace_id) ON DELETE CASCADE,
    key_path VARCHAR(255) NOT NULL,
    context TEXT,
    screenshot_url VARCHAR(500),
    placeholders JSONB DEFAULT '[]',
    is_plural BOOLEAN DEFAULT FALSE,
    max_length INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES core.users(user_id),
    UNIQUE (namespace_id, key_path)
);

CREATE INDEX IF NOT EXISTS idx_i18n_keys_namespace ON translations.i18n_keys (namespace_id);
CREATE INDEX IF NOT EXISTS idx_i18n_keys_path ON translations.i18n_keys (key_path);
CREATE INDEX IF NOT EXISTS idx_i18n_keys_plural ON translations.i18n_keys (is_plural) WHERE is_plural = TRUE;

COMMENT ON TABLE translations.i18n_keys IS 'All translatable text keys with context for translators';

-- ============================================================================
-- 6. TABLE: i18n_translations (Actual translations)
-- ============================================================================
CREATE TABLE IF NOT EXISTS translations.i18n_translations (
    translation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key_id UUID NOT NULL REFERENCES translations.i18n_keys(key_id) ON DELETE CASCADE,
    language_code VARCHAR(10) NOT NULL REFERENCES translations.supported_languages(language_code),
    value TEXT NOT NULL,
    plural_forms JSONB,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    source VARCHAR(50) NOT NULL DEFAULT 'manual',
    is_verified BOOLEAN DEFAULT FALSE,
    verified_by UUID REFERENCES core.users(user_id),
    verified_at TIMESTAMPTZ,
    machine_confidence DECIMAL(3,2),
    version INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES core.users(user_id),
    UNIQUE (key_id, language_code),
    CONSTRAINT chk_translation_status CHECK (status IN ('draft', 'active', 'needs_review', 'outdated')),
    CONSTRAINT chk_translation_source CHECK (source IN ('manual', 'deepl', 'google', 'community', 'ai', 'import'))
);

CREATE INDEX IF NOT EXISTS idx_i18n_translations_key ON translations.i18n_translations (key_id);
CREATE INDEX IF NOT EXISTS idx_i18n_translations_lang ON translations.i18n_translations (language_code);
CREATE INDEX IF NOT EXISTS idx_i18n_translations_status ON translations.i18n_translations (status);
CREATE INDEX IF NOT EXISTS idx_i18n_translations_unverified ON translations.i18n_translations (is_verified) WHERE is_verified = FALSE;

COMMENT ON TABLE translations.i18n_translations IS 'Translations for all keys in all languages';

-- ============================================================================
-- 7. TABLE: i18n_suggestions (Community translation suggestions)
-- ============================================================================
CREATE TABLE IF NOT EXISTS translations.i18n_suggestions (
    suggestion_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    translation_id UUID REFERENCES translations.i18n_translations(translation_id) ON DELETE CASCADE,
    key_id UUID REFERENCES translations.i18n_keys(key_id) ON DELETE CASCADE,
    language_code VARCHAR(10) NOT NULL REFERENCES translations.supported_languages(language_code),
    suggested_value TEXT NOT NULL,
    suggested_plural_forms JSONB,
    reason TEXT,
    suggested_by UUID NOT NULL REFERENCES core.users(user_id),
    suggested_at TIMESTAMPTZ DEFAULT NOW(),
    votes_up INTEGER DEFAULT 0,
    votes_down INTEGER DEFAULT 0,
    vote_score INTEGER GENERATED ALWAYS AS (votes_up - votes_down) STORED,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    reviewed_by UUID REFERENCES core.users(user_id),
    reviewed_at TIMESTAMPTZ,
    review_comment TEXT,
    CONSTRAINT chk_suggestion_status CHECK (status IN ('pending', 'approved', 'rejected', 'duplicate')),
    CONSTRAINT chk_suggestion_ref CHECK (translation_id IS NOT NULL OR key_id IS NOT NULL)
);

CREATE INDEX IF NOT EXISTS idx_i18n_suggestions_translation ON translations.i18n_suggestions (translation_id);
CREATE INDEX IF NOT EXISTS idx_i18n_suggestions_key ON translations.i18n_suggestions (key_id);
CREATE INDEX IF NOT EXISTS idx_i18n_suggestions_status ON translations.i18n_suggestions (status);
CREATE INDEX IF NOT EXISTS idx_i18n_suggestions_score ON translations.i18n_suggestions (vote_score DESC);
CREATE INDEX IF NOT EXISTS idx_i18n_suggestions_user ON translations.i18n_suggestions (suggested_by);

COMMENT ON TABLE translations.i18n_suggestions IS 'Community translation suggestions with voting system';

-- ============================================================================
-- 8. TABLE: i18n_suggestion_votes (Voting on suggestions)
-- ============================================================================
CREATE TABLE IF NOT EXISTS translations.i18n_suggestion_votes (
    vote_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    suggestion_id UUID NOT NULL REFERENCES translations.i18n_suggestions(suggestion_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,
    vote_type VARCHAR(10) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (suggestion_id, user_id),
    CONSTRAINT chk_vote_type CHECK (vote_type IN ('up', 'down'))
);

CREATE INDEX IF NOT EXISTS idx_i18n_votes_suggestion ON translations.i18n_suggestion_votes (suggestion_id);
CREATE INDEX IF NOT EXISTS idx_i18n_votes_user ON translations.i18n_suggestion_votes (user_id);

-- ============================================================================
-- 9. TABLE: i18n_translation_requests (On-demand translation requests)
-- ============================================================================
CREATE TABLE IF NOT EXISTS translations.i18n_translation_requests (
    request_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    target_language VARCHAR(10) NOT NULL REFERENCES translations.supported_languages(language_code),
    scope VARCHAR(20) NOT NULL DEFAULT 'full',
    namespace_id INTEGER REFERENCES translations.i18n_namespaces(namespace_id),
    key_id UUID REFERENCES translations.i18n_keys(key_id),
    requested_by UUID REFERENCES core.users(user_id),
    requested_at TIMESTAMPTZ DEFAULT NOW(),
    request_count INTEGER DEFAULT 1,
    priority INTEGER DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    keys_total INTEGER,
    keys_completed INTEGER DEFAULT 0,
    error_message TEXT,
    CONSTRAINT chk_request_status CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')),
    CONSTRAINT chk_request_scope CHECK (scope IN ('full', 'namespace', 'key'))
);

CREATE INDEX IF NOT EXISTS idx_i18n_requests_lang ON translations.i18n_translation_requests (target_language);
CREATE INDEX IF NOT EXISTS idx_i18n_requests_status ON translations.i18n_translation_requests (status);
CREATE INDEX IF NOT EXISTS idx_i18n_requests_priority ON translations.i18n_translation_requests (priority DESC);

COMMENT ON TABLE translations.i18n_translation_requests IS 'On-demand translation requests for new languages';

-- ============================================================================
-- 10. TABLE: i18n_ai_reviews (AI quality reviews for translations)
-- ============================================================================
CREATE TABLE IF NOT EXISTS translations.i18n_ai_reviews (
    review_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    translation_id UUID REFERENCES translations.i18n_translations(translation_id) ON DELETE CASCADE,
    suggestion_id UUID REFERENCES translations.i18n_suggestions(suggestion_id) ON DELETE CASCADE,
    ai_model VARCHAR(100) NOT NULL,
    ai_provider VARCHAR(50) NOT NULL,
    quality_score DECIMAL(3,2),
    accuracy_score DECIMAL(3,2),
    fluency_score DECIMAL(3,2),
    consistency_score DECIMAL(3,2),
    recommendation VARCHAR(20) NOT NULL,
    ai_suggestion TEXT,
    ai_explanation TEXT,
    issues JSONB DEFAULT '[]',
    tokens_used INTEGER,
    cost_eur DECIMAL(10,6),
    reviewed_at TIMESTAMPTZ DEFAULT NOW(),
    response_time_ms INTEGER,
    CONSTRAINT chk_ai_recommendation CHECK (recommendation IN ('approve', 'reject', 'needs_review', 'improve')),
    CONSTRAINT chk_review_ref CHECK (translation_id IS NOT NULL OR suggestion_id IS NOT NULL)
);

CREATE INDEX IF NOT EXISTS idx_ai_reviews_translation ON translations.i18n_ai_reviews (translation_id);
CREATE INDEX IF NOT EXISTS idx_ai_reviews_suggestion ON translations.i18n_ai_reviews (suggestion_id);
CREATE INDEX IF NOT EXISTS idx_ai_reviews_recommendation ON translations.i18n_ai_reviews (recommendation);
CREATE INDEX IF NOT EXISTS idx_ai_reviews_model ON translations.i18n_ai_reviews (ai_model);

COMMENT ON TABLE translations.i18n_ai_reviews IS 'AI moderation for translations and community suggestions';

-- ============================================================================
-- 11. TABLE: i18n_moderation_queue (Moderation workflow queue)
-- ============================================================================
CREATE TABLE IF NOT EXISTS translations.i18n_moderation_queue (
    queue_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    item_type VARCHAR(20) NOT NULL,
    translation_id UUID REFERENCES translations.i18n_translations(translation_id) ON DELETE CASCADE,
    suggestion_id UUID REFERENCES translations.i18n_suggestions(suggestion_id) ON DELETE CASCADE,
    priority INTEGER DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    moderation_type VARCHAR(20),
    ai_review_id UUID REFERENCES translations.i18n_ai_reviews(review_id),
    assigned_to UUID REFERENCES core.users(user_id),
    human_decision VARCHAR(20),
    human_comment TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    ai_reviewed_at TIMESTAMPTZ,
    human_reviewed_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    CONSTRAINT chk_queue_item_type CHECK (item_type IN ('translation', 'suggestion')),
    CONSTRAINT chk_queue_status CHECK (status IN ('pending', 'ai_reviewing', 'awaiting_human', 'completed', 'skipped')),
    CONSTRAINT chk_moderation_type CHECK (moderation_type IN ('ai', 'human', 'ai_then_human'))
);

CREATE INDEX IF NOT EXISTS idx_moderation_queue_status ON translations.i18n_moderation_queue (status);
CREATE INDEX IF NOT EXISTS idx_moderation_queue_priority ON translations.i18n_moderation_queue (priority DESC, created_at);
CREATE INDEX IF NOT EXISTS idx_moderation_queue_assigned ON translations.i18n_moderation_queue (assigned_to) WHERE assigned_to IS NOT NULL;

COMMENT ON TABLE translations.i18n_moderation_queue IS 'Queue for AI and human moderation of translations';

-- ============================================================================
-- 12. TABLE: i18n_ai_config (AI moderation configuration)
-- ============================================================================
CREATE TABLE IF NOT EXISTS translations.i18n_ai_config (
    config_id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    updated_by UUID REFERENCES core.users(user_id)
);

-- ============================================================================
-- SEED: AI Moderation Configuration
-- ============================================================================
INSERT INTO translations.i18n_ai_config (config_key, config_value, description) VALUES
    ('moderation_model', '"gpt-4o"', 'Standard model for moderation'),
    ('auto_approve_threshold', '0.95', 'Auto-approve above this score'),
    ('auto_reject_threshold', '0.3', 'Auto-reject below this score'),
    ('human_review_threshold', '0.7', 'Human review between reject and approve'),
    ('moderation_prompt', '{
        "system": "Du bist ein Übersetzungs-Moderator für eine Lernplattform. Prüfe Übersetzungen auf Qualität, Genauigkeit und Konsistenz.",
        "criteria": [
            "Grammatik und Rechtschreibung",
            "Fachliche Korrektheit",
            "Natürlicher Sprachfluss",
            "Konsistenz mit Fachbegriffen",
            "Passender Ton für Lernplattform"
        ]
    }', 'Prompt template for AI moderation'),
    ('batch_size', '50', 'Translations per batch review'),
    ('enabled_languages', '["de", "pl", "en"]', 'Languages enabled for AI moderation')
ON CONFLICT (config_key) DO UPDATE SET
    config_value = EXCLUDED.config_value,
    updated_at = NOW();

-- ============================================================================
-- 13. TRIGGERS: updated_at timestamp maintenance
-- ============================================================================
DROP TRIGGER IF EXISTS update_translations_updated_at ON translations.translations;
CREATE TRIGGER update_translations_updated_at BEFORE UPDATE ON translations.translations
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_i18n_namespaces_updated_at ON translations.i18n_namespaces;
CREATE TRIGGER update_i18n_namespaces_updated_at BEFORE UPDATE ON translations.i18n_namespaces
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_i18n_keys_updated_at ON translations.i18n_keys;
CREATE TRIGGER update_i18n_keys_updated_at BEFORE UPDATE ON translations.i18n_keys
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_i18n_translations_updated_at ON translations.i18n_translations;
CREATE TRIGGER update_i18n_translations_updated_at BEFORE UPDATE ON translations.i18n_translations
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 14. TRIGGER: Vote counter updates
-- ============================================================================
DROP TRIGGER IF EXISTS trigger_suggestion_votes ON translations.i18n_suggestion_votes;
DROP FUNCTION IF EXISTS update_suggestion_vote_counts();

CREATE OR REPLACE FUNCTION update_suggestion_vote_counts()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        IF NEW.vote_type = 'up' THEN
            UPDATE translations.i18n_suggestions SET votes_up = votes_up + 1 WHERE suggestion_id = NEW.suggestion_id;
        ELSE
            UPDATE translations.i18n_suggestions SET votes_down = votes_down + 1 WHERE suggestion_id = NEW.suggestion_id;
        END IF;
    ELSIF TG_OP = 'DELETE' THEN
        IF OLD.vote_type = 'up' THEN
            UPDATE translations.i18n_suggestions SET votes_up = votes_up - 1 WHERE suggestion_id = OLD.suggestion_id;
        ELSE
            UPDATE translations.i18n_suggestions SET votes_down = votes_down - 1 WHERE suggestion_id = OLD.suggestion_id;
        END IF;
    ELSIF TG_OP = 'UPDATE' THEN
        IF OLD.vote_type = 'up' THEN
            UPDATE translations.i18n_suggestions SET votes_up = votes_up - 1 WHERE suggestion_id = OLD.suggestion_id;
        ELSE
            UPDATE translations.i18n_suggestions SET votes_down = votes_down - 1 WHERE suggestion_id = OLD.suggestion_id;
        END IF;
        IF NEW.vote_type = 'up' THEN
            UPDATE translations.i18n_suggestions SET votes_up = votes_up + 1 WHERE suggestion_id = NEW.suggestion_id;
        ELSE
            UPDATE translations.i18n_suggestions SET votes_down = votes_down + 1 WHERE suggestion_id = NEW.suggestion_id;
        END IF;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_suggestion_votes
    AFTER INSERT OR UPDATE OR DELETE ON translations.i18n_suggestion_votes
    FOR EACH ROW EXECUTE FUNCTION update_suggestion_vote_counts();

-- ============================================================================
-- 15. VIEWS: Translation progress & analytics
-- ============================================================================
CREATE OR REPLACE VIEW v_i18n_language_progress AS
SELECT
    sl.language_code,
    sl.language_name,
    sl.native_name,
    sl.flag_emoji,
    sl.is_primary,
    sl.priority,
    sl.fallback_language,
    sl.active,
    COUNT(DISTINCT ik.key_id) AS total_keys,
    COUNT(DISTINCT it.key_id) AS translated_keys,
    CASE
        WHEN COUNT(DISTINCT ik.key_id) > 0
        THEN ROUND((COUNT(DISTINCT it.key_id)::DECIMAL / COUNT(DISTINCT ik.key_id) * 100), 2)
        ELSE 0
    END AS completion_percent,
    COUNT(DISTINCT CASE WHEN it.is_verified THEN it.key_id END) AS verified_keys,
    COUNT(DISTINCT isug.suggestion_id) FILTER (WHERE isug.status = 'pending') AS pending_suggestions
FROM translations.supported_languages sl
CROSS JOIN translations.i18n_keys ik
LEFT JOIN translations.i18n_translations it ON ik.key_id = it.key_id AND sl.language_code = it.language_code
LEFT JOIN translations.i18n_suggestions isug ON it.translation_id = isug.translation_id
GROUP BY sl.language_code, sl.language_name, sl.native_name, sl.flag_emoji,
         sl.is_primary, sl.priority, sl.fallback_language, sl.active
ORDER BY sl.priority, sl.language_name;

COMMENT ON VIEW v_i18n_language_progress IS 'Translation progress per language with statistics';

CREATE OR REPLACE VIEW v_i18n_missing_translations AS
SELECT
    sl.language_code,
    sl.language_name,
    ns.namespace_code,
    ik.key_id,
    ik.key_path,
    ik.context,
    de_trans.value AS german_value
FROM translations.supported_languages sl
CROSS JOIN translations.i18n_keys ik
JOIN translations.i18n_namespaces ns ON ik.namespace_id = ns.namespace_id
LEFT JOIN translations.i18n_translations it ON ik.key_id = it.key_id AND sl.language_code = it.language_code
LEFT JOIN translations.i18n_translations de_trans ON ik.key_id = de_trans.key_id AND de_trans.language_code = 'de'
WHERE sl.active = TRUE
  AND it.translation_id IS NULL
ORDER BY sl.priority, ns.sort_order, ik.key_path;

COMMENT ON VIEW v_i18n_missing_translations IS 'All missing translations with German reference text';

CREATE OR REPLACE VIEW v_i18n_moderation_dashboard AS
SELECT
    sl.language_code,
    sl.language_name,
    sl.flag_emoji,
    COUNT(DISTINCT mq.queue_id) FILTER (WHERE mq.status = 'pending') AS pending_count,
    COUNT(DISTINCT mq.queue_id) FILTER (WHERE mq.status = 'ai_reviewing') AS ai_reviewing_count,
    COUNT(DISTINCT mq.queue_id) FILTER (WHERE mq.status = 'awaiting_human') AS awaiting_human_count,
    COUNT(DISTINCT isug.suggestion_id) FILTER (WHERE isug.status = 'pending') AS pending_suggestions,
    COUNT(DISTINCT ar.review_id) FILTER (WHERE ar.reviewed_at > NOW() - INTERVAL '24 hours') AS ai_reviews_24h,
    AVG(ar.quality_score) FILTER (WHERE ar.reviewed_at > NOW() - INTERVAL '7 days') AS avg_quality_7d
FROM translations.supported_languages sl
LEFT JOIN translations.i18n_translations it ON sl.language_code = it.language_code
LEFT JOIN translations.i18n_moderation_queue mq ON it.translation_id = mq.translation_id
LEFT JOIN translations.i18n_suggestions isug ON it.translation_id = isug.translation_id
LEFT JOIN translations.i18n_ai_reviews ar ON it.translation_id = ar.translation_id
WHERE sl.active = TRUE
GROUP BY sl.language_code, sl.language_name, sl.flag_emoji
ORDER BY pending_count DESC;

COMMENT ON VIEW v_i18n_moderation_dashboard IS 'Dashboard for translation moderation with AI statistics';

-- ============================================================================
-- 16. FUNCTION: Get translation bundle for language
-- ============================================================================
CREATE OR REPLACE FUNCTION get_i18n_bundle(
    p_language_code VARCHAR(10),
    p_namespace_code VARCHAR(50) DEFAULT NULL
)
RETURNS JSONB AS $$
DECLARE
    v_result JSONB := '{}';
    v_fallback VARCHAR(10);
BEGIN
    SELECT fallback_language INTO v_fallback
    FROM translations.supported_languages
    WHERE language_code = p_language_code;

    SELECT jsonb_object_agg(
        ns.namespace_code || '.' || ik.key_path,
        COALESCE(it.value, fb.value, ik.key_path)
    ) INTO v_result
    FROM translations.i18n_keys ik
    JOIN translations.i18n_namespaces ns ON ik.namespace_id = ns.namespace_id
    LEFT JOIN translations.i18n_translations it ON ik.key_id = it.key_id AND it.language_code = p_language_code
    LEFT JOIN translations.i18n_translations fb ON ik.key_id = fb.key_id AND fb.language_code = v_fallback
    WHERE (p_namespace_code IS NULL OR ns.namespace_code = p_namespace_code)
      AND ns.is_active = TRUE;

    RETURN COALESCE(v_result, '{}');
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_i18n_bundle IS 'Returns all translations for a language as JSONB (with fallback)';

-- ============================================================================
-- Migration 038 (Complete i18n System) - Final Status
-- ============================================================================
-- CONSOLIDATED FROM:
--   - Original 038_translations.sql (basic tables + 20 language seed)
--   - Original 072_i18n_system.sql (advanced i18n + AI moderation)
--
-- TABLES CREATED:
--   - translations.translations (content translations, 20 languages)
--   - translations.translation_cache (performance cache)
--   - translations.supported_languages (20 languages config)
--   - translations.i18n_namespaces (translation key namespaces - 17 default)
--   - translations.i18n_keys (translatable text keys)
--   - translations.i18n_translations (actual translations)
--   - translations.i18n_suggestions (community suggestions with voting)
--   - translations.i18n_suggestion_votes (voting system)
--   - translations.i18n_translation_requests (on-demand requests)
--   - translations.i18n_ai_reviews (AI quality reviews)
--   - translations.i18n_moderation_queue (moderation workflow)
--   - translations.i18n_ai_config (AI moderation settings)
--
-- VIEWS CREATED:
--   - v_i18n_language_progress (translation progress per language)
--   - v_i18n_missing_translations (missing translations report)
--   - v_i18n_moderation_dashboard (moderation analytics)
--
-- PRIMARY LANGUAGES: DE (priority 1), PL (priority 2), EN (priority 3)
-- OTHER LANGUAGES: 17 additional languages with fallback to DE
-- AI MODERATION: GPT-4o/GPT-5.2 for automatic quality review
--
-- FIXES APPLIED:
--   - English flag: 🇬🇧 → EN (text, not emoji - for better visibility)
--   - Consolidated migrations 038 + 072 into single 038_i18n_complete.sql
--
-- ============================================================================
