-- ============================================================================
-- Migration: 088_i18n_namespaces.sql
-- Description: i18n Namespace Updates (Frontend Restructure 2026-01-16)
--              - Add aiEditor namespace (AI Content Editor)
--              - Add features namespace (System Features)
--              - Mark deprecated: ai_studio → aiEditor
--              - Mark partial: windows → features (some content moved)
--
-- Version: 2.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-01-16
-- ============================================================================
--
-- Part 5 of 5-part i18n system (split from 038_i18n_complete.sql)
-- Other parts: 084 (core), 085 (languages), 086 (sync), 087 (triggers)
--
-- NAMESPACE ARCHITECTURE:
-- This migration updates the i18n namespace structure to match the frontend
-- folder reorganization from 2026-01-16. Key changes:
--
-- NEW NAMESPACES:
-- - aiEditor: Replaces ai_studio namespace for AI content authoring
--             Contains: Authoring, Chat, Content-Generierung, Panels, Settings
-- - features: New namespace for System Features
--             Contains: AI Pricing, Learning Methods, Viewer, Shared Features
--
-- DEPRECATED NAMESPACES:
-- - ai_studio: Marked DEPRECATED → Use aiEditor instead
-- - windows: Marked PARTIAL → Some content moved to features
--
-- This ensures translation keys align with the new frontend component structure
-- and provides clear migration paths for deprecated namespaces.
--
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. ADD NEW NAMESPACES
-- ============================================================================
-- Purpose: Add aiEditor and features namespaces to match frontend structure
-- ============================================================================

-- Add aiEditor namespace (AI Content Editor)
INSERT INTO translations.i18n_namespaces (namespace_code, name, description, icon, sort_order)
VALUES
    ('aiEditor', 'KI-Editor', 'AI Content Editor - Authoring, Chat, Content-Generierung, Panels, Settings', '🤖✏️', 85)
ON CONFLICT (namespace_code) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    icon = EXCLUDED.icon,
    sort_order = EXCLUDED.sort_order,
    updated_at = NOW();

COMMENT ON COLUMN translations.i18n_namespaces.namespace_code IS
'Namespace identifier (e.g., aiEditor replaces ai_studio)';

-- Add features namespace (System Features)
INSERT INTO translations.i18n_namespaces (namespace_code, name, description, icon, sort_order)
VALUES
    ('features', 'System-Features', 'System Features - AI Pricing, Learning Methods, Viewer, Shared Features', '⚙️✨', 195)
ON CONFLICT (namespace_code) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    icon = EXCLUDED.icon,
    sort_order = EXCLUDED.sort_order,
    updated_at = NOW();

-- ============================================================================
-- 2. MARK DEPRECATED NAMESPACES
-- ============================================================================
-- Purpose: Update deprecated namespaces with migration instructions
-- Note: Existing keys remain functional but new keys should use new namespaces
-- ============================================================================

-- Mark ai_studio as DEPRECATED (use aiEditor instead)
UPDATE translations.i18n_namespaces
SET
    description = 'KI-Studio (DEPRECATED: Use aiEditor instead) - Legacy AI authoring',
    updated_at = NOW()
WHERE namespace_code = 'ai_studio';

-- Mark windows as PARTIAL (some content moved to features)
UPDATE translations.i18n_namespaces
SET
    description = 'Fenster/UI (PARTIAL: Some content moved to features) - Legacy window components',
    updated_at = NOW()
WHERE namespace_code = 'windows';

-- ============================================================================
-- NAMESPACE MIGRATION NOTES
-- ============================================================================
--
-- MIGRATION PATH FOR DEPRECATED NAMESPACES:
--
-- 1. ai_studio → aiEditor:
--    - Old keys: ai_studio.authoring.* remain functional
--    - New keys: Use aiEditor.authoring.* instead
--    - Timeline: Gradual migration, no immediate breaking change
--
-- 2. windows → features (PARTIAL):
--    - System feature keys: Moved to features.*
--    - UI component keys: Remain in windows.*
--    - Timeline: Ongoing, frontend determines split
--
-- EXISTING NAMESPACES (unchanged):
--   - admin (Admin-Panel)
--   - courses (Kurse & Lernmethoden)
--   - common (Allgemeine UI-Elemente)
--   - auth (Authentifizierung)
--   - errors (Fehlermeldungen)
--   - dashboard (Dashboard & Widgets)
--   - analytics (Analytics-Dashboard)
--   - learningMethods (Lernmethoden-Editor)
--   - gamification (Gamification-System)
--   - liveroom (LiveRoom-System)
--   - messaging (Nachrichten-System)
--   - community (Community-Features)
--   - compliance (Compliance & Moderation)
--   - billing (Abrechnungs-System)
--   - categories (Kategorien)
--
-- ============================================================================

COMMIT;

-- ============================================================================
-- END MIGRATION 088 (i18n Namespaces - Frontend Restructure 2026-01-16)
-- ============================================================================
--
-- SPLIT COMPLETE: 5-PART i18n SYSTEM
--
-- Original: 038_i18n_complete.sql (945 lines)
--
-- Split into:
--   084_i18n_core_tables.sql (543 lines) - Core tables, views, AI config
--   085_i18n_languages_base.sql (101 lines) - 3 core languages (DE, PL, EN)
--   086_i18n_sync_system.sql (239 lines) - Frontend ↔ Database sync
--   087_i18n_progress_triggers.sql (148 lines) - Auto-update progress
--   088_i18n_namespaces.sql (THIS FILE) - Namespace updates
--
-- Total: 5 focused, maintainable migration files in 11_System/i18n/ subdirectory
--
-- ============================================================================
