-- ============================================================================
-- Migration: 091_i18n_extend_source_and_namespaces.sql
-- Description: Extend translation_source CHECK constraint + seed namespaces
--              - Add 'llm' as provider-agnostic AI translation source
--              - Seed namespaces matching frontend locale directory structure
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-02-07
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. EXTEND translation_source CHECK constraint to include 'llm'
-- ============================================================================
-- The 'llm' value is provider-agnostic (covers OpenAI, Anthropic, etc.)
-- Existing 'gpt4' kept for backward compatibility
-- ============================================================================

ALTER TABLE translations.i18n_translations
    DROP CONSTRAINT IF EXISTS chk_i18n_translations_source;

ALTER TABLE translations.i18n_translations
    ADD CONSTRAINT chk_i18n_translations_source
    CHECK (translation_source IN ('manual', 'deepl', 'gpt4', 'llm', 'community', 'imported'));

-- ============================================================================
-- 2. SEED namespaces matching frontend locale directory structure
-- ============================================================================
-- Source: frontend/src/infrastructure/i18n/locales/en/
-- Uses ON CONFLICT DO NOTHING to be idempotent
-- ============================================================================

INSERT INTO translations.i18n_namespaces (namespace_code, name, description, icon, sort_order) VALUES
    -- Top-level namespaces
    ('common',    'Common',       'Shared UI elements, buttons, labels',                  NULL, 10),
    ('errors',    'Errors',       'Error messages and validation feedback',                NULL, 20),
    ('dashboard', 'Dashboard',    'Dashboard widgets and overview',                        NULL, 30),
    ('courses',   'Courses',      'Course browsing, content, moderation',                  NULL, 40),
    ('legal',     'Legal',        'Legal pages, privacy policy, terms of service',         NULL, 50),
    ('setup',     'Setup',        'Setup wizard and onboarding',                           NULL, 60),
    ('tutor',     'Tutor',        'AI tutor companion interface',                          NULL, 70),
    -- Panel (admin) namespaces — dot-notation maps to panel/ subdirectory
    ('panel.system',            'Panel: System',            'Admin system settings and audit logs',     NULL, 100),
    ('panel.languages',         'Panel: Languages',         'Language management admin panel',          NULL, 101),
    ('panel.users',             'Panel: Users',             'User management admin panel',              NULL, 102),
    ('panel.ai-settings',       'Panel: AI Settings',       'AI model and provider configuration',      NULL, 103),
    ('panel.analytics',         'Panel: Analytics',         'Analytics dashboard',                      NULL, 104),
    ('panel.feature-flags',     'Panel: Feature Flags',     'Feature flag management',                  NULL, 105),
    ('panel.organisations',     'Panel: Organisations',     'Organisation management',                  NULL, 106),
    ('panel.course-management', 'Panel: Course Management', 'Course administration and moderation',     NULL, 107),
    ('panel.groups',            'Panel: Groups',            'Group and access management',              NULL, 108),
    ('panel.shared',            'Panel: Shared',            'Shared admin panel components',            NULL, 109)
ON CONFLICT (namespace_code) DO NOTHING;

COMMIT;

-- ============================================================================
-- END MIGRATION 091 (i18n Extend Source + Seed Namespaces)
-- ============================================================================
