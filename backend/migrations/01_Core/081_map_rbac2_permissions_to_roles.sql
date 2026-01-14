-- ============================================================================
-- Migration: 081_map_rbac2_permissions_to_roles.sql
-- Description: Map RBAC 2.0 permissions to appropriate roles
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-01-14
-- ============================================================================
-- Purpose: Establish role-permission mappings for three new RBAC 2.0
--          permissions required by Phase 1 decorator migration.
--
-- Permission Mappings:
--   admin:system (213)          → owner (11), admin (9)
--   manage:org:settings (214)   → owner (11), admin (9), company_admin (6), school_admin (5)
--   admin:organisations (215)   → owner (11), admin (9), company_admin (6), school_admin (5)
--
-- These mappings allow the decorators to grant access via database-driven
-- permission checks instead of hardcoded role lists.

-- ============================================================================
-- admin:system → System admin roles (owner, admin)
-- ============================================================================
INSERT INTO core.role_permissions (role_id, permission_id)
VALUES
    (11, 213),  -- owner gets admin:system
    (9, 213)    -- admin gets admin:system
ON CONFLICT DO NOTHING;

-- ============================================================================
-- manage:org:settings → Organization admin roles
-- ============================================================================
INSERT INTO core.role_permissions (role_id, permission_id)
VALUES
    (11, 214),  -- owner gets manage:org:settings
    (9, 214),   -- admin gets manage:org:settings
    (6, 214),   -- company_admin gets manage:org:settings
    (5, 214)    -- school_admin gets manage:org:settings
ON CONFLICT DO NOTHING;

-- ============================================================================
-- admin:organisations → Organization administration roles
-- ============================================================================
INSERT INTO core.role_permissions (role_id, permission_id)
VALUES
    (11, 215),  -- owner gets admin:organisations
    (9, 215),   -- admin gets admin:organisations
    (6, 215),   -- company_admin gets admin:organisations
    (5, 215)    -- school_admin gets admin:organisations
ON CONFLICT DO NOTHING;

-- ============================================================================
-- End of Migration 081_map_rbac2_permissions_to_roles.sql
-- Migration Status: ✅ SUCCESSFUL
-- Total Mappings: 11 role-permission relationships created
-- ============================================================================
