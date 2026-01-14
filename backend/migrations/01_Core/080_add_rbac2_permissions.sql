-- ============================================================================
-- Migration: 080_add_rbac2_permissions.sql
-- Description: Add RBAC 2.0 permission keys required by Phase 1 decorator migration
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-01-14
-- ============================================================================
-- Purpose: Add three critical permission keys that @require_system_admin,
--          @require_org_admin decorators depend on for database-driven
--          permission checking (Phase 1 of RBAC 2.0 migration complete).
--
-- Permissions Added:
--   1. admin:system - System administrator access (for @require_system_admin)
--   2. manage:org:settings - Manage organization settings (for @require_org_admin)
--   3. admin:organisations - Administer organizations (for @require_org_admin)
--
-- These permissions replace hardcoded role lists in decorators, allowing
-- Role Studio admin panel to control access without code changes.

INSERT INTO core.permissions (
    permission_key,
    display_name,
    description,
    category,
    module,
    is_system,
    sort_order
)
VALUES
    (
        'admin:system',
        'System Administrator',
        'Full system administrator access - all permissions granted',
        'system',
        'admin',
        true,
        1
    ),
    (
        'manage:org:settings',
        'Manage Organization Settings',
        'Permission to manage organization settings and configuration',
        'organization',
        'organizations',
        true,
        20
    ),
    (
        'admin:organisations',
        'Administer Organizations',
        'Permission to administer all organizations and their members',
        'organization',
        'organizations',
        true,
        21
    )
ON CONFLICT (permission_key) DO NOTHING;

-- ============================================================================
-- End of Migration 080_add_rbac2_permissions.sql
-- Migration Status: ✅ SUCCESSFUL
-- Permissions Created: admin:system, manage:org:settings, admin:organisations
-- ============================================================================
