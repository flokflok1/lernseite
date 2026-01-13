-- ============================================================================
-- Migration: 038_translations.sql
-- Description: Multi-language translation system (20 languages)
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-01-17
-- ============================================================================

-- ============================================================================
-- TABLE: translations
-- Description: Content translations (courses, chapters, etc.)
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
-- TABLE: translation_cache
-- Description: Translation cache for performance
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
-- TABLE: supported_languages
-- Description: Supported languages configuration
-- ============================================================================
CREATE TABLE IF NOT EXISTS translations.supported_languages (
    language_code VARCHAR(10) PRIMARY KEY,
    language_name VARCHAR(100) NOT NULL,
    native_name VARCHAR(100) NOT NULL,
    flag_emoji VARCHAR(10),
    rtl BOOLEAN DEFAULT FALSE,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_supported_languages_active ON translations.supported_languages (active) WHERE active = TRUE;

COMMENT ON TABLE translations.supported_languages IS 'Supported languages for the platform';

-- ============================================================================
-- Seed Supported Languages (20 languages)
-- ============================================================================
INSERT INTO translations.supported_languages (language_code, language_name, native_name, flag_emoji, active) VALUES
    ('de', 'German', 'Deutsch', '🇩🇪', true),
    ('en', 'English', 'English', '🇬🇧', true),
    ('fr', 'French', 'Français', '🇫🇷', true),
    ('es', 'Spanish', 'Español', '🇪🇸', true),
    ('it', 'Italian', 'Italiano', '🇮🇹', true),
    ('pl', 'Polish', 'Polski', '🇵🇱', true),
    ('nl', 'Dutch', 'Nederlands', '🇳🇱', true),
    ('pt', 'Portuguese', 'Português', '🇵🇹', true),
    ('ru', 'Russian', 'Русский', '🇷🇺', true),
    ('ja', 'Japanese', '日本語', '🇯🇵', true),
    ('zh', 'Chinese', '中文', '🇨🇳', true),
    ('ko', 'Korean', '한국어', '🇰🇷', true),
    ('ar', 'Arabic', 'العربية', '🇸🇦', true),
    ('tr', 'Turkish', 'Türkçe', '🇹🇷', true),
    ('sv', 'Swedish', 'Svenska', '🇸🇪', true),
    ('da', 'Danish', 'Dansk', '🇩🇰', true),
    ('no', 'Norwegian', 'Norsk', '🇳🇴', true),
    ('fi', 'Finnish', 'Suomi', '🇫🇮', true),
    ('cs', 'Czech', 'Čeština', '🇨🇿', true),
    ('uk', 'Ukrainian', 'Українська', '🇺🇦', true)
ON CONFLICT (language_code) DO NOTHING;

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- ============================================================================
CREATE TRIGGER update_translations_updated_at BEFORE UPDATE ON translations.translations
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- End of Migration: 038_translations.sql
-- ============================================================================
