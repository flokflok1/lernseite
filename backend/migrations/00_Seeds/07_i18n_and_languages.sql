-- ============================================================================
-- Seed Data: i18n Configuration & Supported Languages
-- Description: Internationalization setup (3 core languages + AI config)
-- Source: 094_i18n_core_tables.sql, 095_i18n_languages_base.sql, 098_i18n_namespaces.sql
-- Author: LernsystemX Migration System
-- Date: 2026-01-26
-- Phase: 4 (Seed Data)
-- ============================================================================

-- ============================================================================
-- AI Moderation Configuration
-- ============================================================================

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
-- Supported Languages (3 Core Languages)
-- ============================================================================

INSERT INTO translations.supported_languages
(language_code, language_name, native_name, flag, is_active, is_rtl, priority, total_keys, translated_keys, completion_percent)
VALUES
    -- Priority 1: German (Primary)
    ('de', 'German', 'Deutsch', '🇩🇪', true, false, 1, 0, 0, 0.00),
    -- Priority 2: Polish (Secondary)
    ('pl', 'Polish', 'Polski', '🇵🇱', true, false, 2, 0, 0, 0.00),
    -- Priority 3: English (Tertiary)
    ('en', 'English', 'English', 'EN', true, false, 3, 0, 0, 0.00)
ON CONFLICT (language_code) DO UPDATE SET
    language_name = EXCLUDED.language_name,
    native_name = EXCLUDED.native_name,
    flag = EXCLUDED.flag,
    is_active = EXCLUDED.is_active,
    is_rtl = EXCLUDED.is_rtl,
    priority = EXCLUDED.priority,
    updated_at = NOW();

-- ============================================================================
-- i18n Namespaces (Organization for translation keys)
-- ============================================================================

INSERT INTO translations.i18n_namespaces (namespace_code, namespace_name, description, is_system) VALUES
    ('common', 'Common Strings', 'Global UI strings (buttons, labels, messages)', TRUE),
    ('errors', 'Error Messages', 'Error codes and messages', TRUE),
    ('validation', 'Validation Messages', 'Form validation and error messages', TRUE),
    ('course_content', 'Course Content', 'Course-related terminology and labels', FALSE),
    ('learning_methods', 'Learning Methods', 'Names and descriptions of learning methods', FALSE),
    ('system_features', 'System Features', 'Feature names and descriptions', FALSE),
    ('admin', 'Admin Interface', 'Admin panel and management UI strings', FALSE),
    ('compliance', 'Compliance', 'GDPR, DSA, NetzDG related strings', FALSE)
ON CONFLICT (namespace_code) DO NOTHING;

-- ============================================================================
-- Core i18n Keys (Multilingual UI strings)
-- ============================================================================

-- Common namespace: essential UI strings
INSERT INTO translations.i18n_keys (namespace_id, key_path, key_description, default_value, is_required, is_translatable) VALUES
    ((SELECT namespace_id FROM translations.i18n_namespaces WHERE namespace_code = 'common'), 'button.save', 'Save button label', 'Save', TRUE, TRUE),
    ((SELECT namespace_id FROM translations.i18n_namespaces WHERE namespace_code = 'common'), 'button.cancel', 'Cancel button label', 'Cancel', TRUE, TRUE),
    ((SELECT namespace_id FROM translations.i18n_namespaces WHERE namespace_code = 'common'), 'button.delete', 'Delete button label', 'Delete', TRUE, TRUE),
    ((SELECT namespace_id FROM translations.i18n_namespaces WHERE namespace_code = 'common'), 'button.edit', 'Edit button label', 'Edit', TRUE, TRUE),
    ((SELECT namespace_id FROM translations.i18n_namespaces WHERE namespace_code = 'common'), 'button.create', 'Create button label', 'Create', TRUE, TRUE),
    ((SELECT namespace_id FROM translations.i18n_namespaces WHERE namespace_code = 'common'), 'button.next', 'Next button label', 'Next', TRUE, TRUE),
    ((SELECT namespace_id FROM translations.i18n_namespaces WHERE namespace_code = 'common'), 'button.previous', 'Previous button label', 'Previous', TRUE, TRUE),
    ((SELECT namespace_id FROM translations.i18n_namespaces WHERE namespace_code = 'common'), 'label.name', 'Name label', 'Name', TRUE, TRUE),
    ((SELECT namespace_id FROM translations.i18n_namespaces WHERE namespace_code = 'common'), 'label.email', 'Email label', 'Email', TRUE, TRUE),
    ((SELECT namespace_id FROM translations.i18n_namespaces WHERE namespace_code = 'common'), 'label.password', 'Password label', 'Password', TRUE, TRUE)
ON CONFLICT (namespace_id, key_path) DO NOTHING;

-- Error namespace
INSERT INTO translations.i18n_keys (namespace_id, key_path, key_description, default_value, is_required, is_translatable) VALUES
    ((SELECT namespace_id FROM translations.i18n_namespaces WHERE namespace_code = 'errors'), 'error.not_found', 'Resource not found error', 'Resource not found', TRUE, TRUE),
    ((SELECT namespace_id FROM translations.i18n_namespaces WHERE namespace_code = 'errors'), 'error.unauthorized', 'Unauthorized access error', 'You are not authorized to perform this action', TRUE, TRUE),
    ((SELECT namespace_id FROM translations.i18n_namespaces WHERE namespace_code = 'errors'), 'error.forbidden', 'Forbidden access error', 'Access to this resource is forbidden', TRUE, TRUE),
    ((SELECT namespace_id FROM translations.i18n_namespaces WHERE namespace_code = 'errors'), 'error.internal_server', 'Internal server error', 'An internal server error occurred', TRUE, TRUE),
    ((SELECT namespace_id FROM translations.i18n_namespaces WHERE namespace_code = 'errors'), 'error.connection_failed', 'Connection error', 'Connection to server failed', TRUE, TRUE)
ON CONFLICT (namespace_id, key_path) DO NOTHING;

-- Verification
SELECT COUNT(*) as total_languages FROM translations.supported_languages;
SELECT COUNT(*) as total_namespaces FROM translations.i18n_namespaces;
SELECT COUNT(*) as total_keys FROM translations.i18n_keys;
