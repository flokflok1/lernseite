-- ============================================================================
-- Migration: 079_update_i18n_namespaces.sql
-- Description: Add missing i18n namespaces to match frontend restructure
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-01-16
-- ============================================================================
--
-- Purpose: Add missing namespaces to match frontend restructure
--
-- Frontend Restructure (2026-01-16):
-- - Added aiEditor/ (AI Content Editor)
-- - Added features/ (System features: AI Pricing, Learning Methods, Viewer)
--
-- Mapping to existing namespaces:
-- - aiEditor → replaces/extends ai_studio
-- - features → replaces/extends windows (partial)
--
-- Strategy: Add new namespaces, keep old ones for backward compatibility
-- ============================================================================

BEGIN;

-- =====================================================
-- 1. ADD MISSING NAMESPACES
-- =====================================================

-- aiEditor namespace (AI Content Editor)
INSERT INTO translations.i18n_namespaces (namespace_code, name, description, icon, sort_order)
VALUES
    ('aiEditor', 'KI-Editor', 'AI Content Editor - Authoring, Chat, Content-Generierung, Panels, Settings', '🤖✏️', 85)
ON CONFLICT (namespace_code) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    icon = EXCLUDED.icon,
    sort_order = EXCLUDED.sort_order,
    updated_at = NOW();

-- features namespace (System Features)
INSERT INTO translations.i18n_namespaces (namespace_code, name, description, icon, sort_order)
VALUES
    ('features', 'System-Features', 'System Features - AI Pricing, Learning Methods, Viewer, Shared Features', '⚙️✨', 195)
ON CONFLICT (namespace_code) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    icon = EXCLUDED.icon,
    sort_order = EXCLUDED.sort_order,
    updated_at = NOW();

-- =====================================================
-- 2. UPDATE EXISTING NAMESPACE DESCRIPTIONS (Optional)
-- =====================================================

-- Update ai_studio description to clarify it's deprecated in favor of aiEditor
UPDATE translations.i18n_namespaces
SET
    description = 'KI-Studio (DEPRECATED: Use aiEditor instead) - Legacy AI authoring',
    updated_at = NOW()
WHERE namespace_code = 'ai_studio';

-- Update windows description to clarify partial migration to features
UPDATE translations.i18n_namespaces
SET
    description = 'Fenster/UI (PARTIAL: Some content moved to features) - Legacy window components',
    updated_at = NOW()
WHERE namespace_code = 'windows';

-- =====================================================
-- 3. VERIFICATION
-- =====================================================

-- Verify new namespaces exist
DO $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_count
    FROM translations.i18n_namespaces
    WHERE namespace_code IN ('aiEditor', 'features');

    IF v_count != 2 THEN
        RAISE EXCEPTION 'Failed to add aiEditor and features namespaces (found % instead of 2)', v_count;
    END IF;

    RAISE NOTICE 'Successfully added % namespaces (aiEditor, features)', v_count;
END $$;

-- Show current namespace count
SELECT
    COUNT(*) as total_namespaces,
    COUNT(*) FILTER (WHERE is_active = true) as active_namespaces,
    COUNT(*) FILTER (WHERE namespace_code IN ('aiEditor', 'features')) as new_namespaces
FROM translations.i18n_namespaces;

COMMIT;

-- =====================================================
-- NOTES FOR DEVELOPERS
-- =====================================================
--
-- Frontend Structure (after restructure):
-- locales/de/
--   ├── aiEditor/        → namespace: aiEditor (NEW)
--   ├── features/        → namespace: features (NEW)
--   ├── admin/           → namespace: admin (existing)
--   ├── common/          → namespace: common (existing)
--   ├── courses/         → namespace: courses (existing)
--   └── ... (other existing namespaces)
--
-- Backward Compatibility:
-- - ai_studio → kept for legacy translations (marked deprecated)
-- - windows → kept for legacy translations (marked partial migration)
--
-- Next Steps:
-- 1. Migrate translations from ai_studio → aiEditor (if needed)
-- 2. Migrate translations from windows → features (if needed)
-- 3. Eventually remove deprecated namespaces after full migration
--
-- =====================================================
-- END MIGRATION 079
-- =====================================================
