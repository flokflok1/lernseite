-- ============================================================================
-- Seed Data: System Groups & Group Permissions
-- Description: System groups and permission mappings for RBAC
-- Source: 009_modify_users_for_groups.sql, 035_permissions_registry.sql, 036_group_permissions_mapping.sql
-- Author: LernsystemX Migration System
-- Date: 2026-01-26
-- Phase: 4 (Seed Data)
-- ============================================================================

-- ============================================================================
-- ONLY Owner Group (User controls all other groups!)
-- Description: Only the Owner/Super-Admin group is auto-created.
--              All other groups (Teachers, Admins, etc.) are created by USER
--              through Admin Panel. This gives FULL CONTROL to the user.
-- ============================================================================

INSERT INTO core.groups (name, slug, description, is_system_group, is_protected, group_type, organisation_id)
VALUES
    ('Owner', 'owner', 'Organization owner with full authority (hierarchy_level: 1000)', TRUE, TRUE, 'org_admin', NULL)
ON CONFLICT (slug) DO NOTHING;

-- ============================================================================
-- Owner Group Permissions (Full Access)
-- Description: Only Owner gets system permissions.
--              All other group permissions are configured by USER
--              through Admin Panel or API.
-- ============================================================================

INSERT INTO core.group_permissions (group_id, permission_id, granted_by)
SELECT
    (SELECT id FROM core.groups WHERE slug = 'owner'),
    p.id,
    NULL
FROM core.permissions p
WHERE p.is_system_permission = TRUE
ON CONFLICT (group_id, permission_id) DO NOTHING;

-- ============================================================================
-- Verification
-- ============================================================================

SELECT COUNT(*) as total_system_groups FROM core.groups WHERE is_system_group = TRUE;
SELECT COUNT(*) as total_group_permissions FROM core.group_permissions;
