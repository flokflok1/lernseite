-- Migration 096: Modify users table for group-based system
-- Beschreibung: Erweiterung der users table mit Spalten für Group-Based RBAC 3.0
-- Datum: 2026-01-22
-- Status: Phase 1 - Database Schema
-- Anmerkung: Alte role-Spalte bleibt für Rollback-Sicherheit

BEGIN;

-- ============================================================================
-- 1. ADD NEW COLUMNS TO USERS TABLE (WITH BACKWARD COMPATIBILITY)
-- ============================================================================

-- Migration status tracking
ALTER TABLE core.users
    ADD COLUMN IF NOT EXISTS groups_override JSONB DEFAULT NULL,  -- Emergency group override
    ADD COLUMN IF NOT EXISTS last_group_sync TIMESTAMP WITH TIME ZONE DEFAULT NULL,  -- When groups were last synced from roles
    ADD COLUMN IF NOT EXISTS migration_roles_to_groups_date TIMESTAMP WITH TIME ZONE DEFAULT NULL;  -- When user was migrated

-- Create indices for new columns
CREATE INDEX IF NOT EXISTS idx_users_migration_roles_to_groups_date
    ON core.users(migration_roles_to_groups_date)
    WHERE migration_roles_to_groups_date IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_users_last_group_sync
    ON core.users(last_group_sync DESC)
    WHERE last_group_sync IS NOT NULL;

-- ============================================================================
-- 2-3. MIGRATION FUNCTIONS REMOVED
-- ============================================================================
-- Note: migrate_user_to_groups() and migrate_all_users_to_groups() functions removed
-- as users table no longer has a role column. System works purely with groups.
-- Users are assigned to groups directly, not migrated from roles.

-- ============================================================================
-- 4. CREATE HELPER FUNCTION: Verify group assignment status
-- ============================================================================
CREATE OR REPLACE FUNCTION verify_user_group_assignment_status()
RETURNS TABLE(
    total_users INT,
    users_in_groups INT,
    assignment_percentage NUMERIC,
    status VARCHAR
)
AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(DISTINCT u.user_id)::INT as total_users,
        COUNT(DISTINCT ug.user_id)::INT as users_in_groups,
        (COUNT(DISTINCT ug.user_id)::NUMERIC / NULLIF(COUNT(DISTINCT u.user_id), 0) * 100)::NUMERIC(5,2) as assignment_percentage,
        CASE
            WHEN COUNT(DISTINCT ug.user_id) = COUNT(DISTINCT u.user_id) THEN 'ALL_ASSIGNED'
            WHEN COUNT(DISTINCT ug.user_id) > 0 THEN 'PARTIAL'
            ELSE 'NONE_ASSIGNED'
        END as status
    FROM core.users u
    LEFT JOIN core.users_groups ug ON u.user_id = ug.user_id AND ug.is_active = TRUE;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 5. CREATE HELPER FUNCTION: Get user's effective permissions
-- ============================================================================
CREATE OR REPLACE FUNCTION get_user_effective_permissions(p_user_id UUID)
RETURNS TABLE(permission_code VARCHAR, display_name VARCHAR, category VARCHAR)
AS $$
    SELECT DISTINCT
        p.code,
        p.display_name,
        p.category
    FROM core.users_groups ug
    JOIN core.group_permissions gp ON ug.group_id = gp.group_id
    JOIN core.permissions p ON gp.permission_id = p.id
    WHERE ug.user_id = p_user_id
        AND ug.is_active = TRUE
        AND ug.left_at IS NULL
    ORDER BY p.code;
$$ LANGUAGE SQL STABLE;

-- ============================================================================
-- 6. CREATE HELPER FUNCTION: Check if user has permission
-- ============================================================================
CREATE OR REPLACE FUNCTION user_has_permission(p_user_id UUID, p_permission_code VARCHAR)
RETURNS BOOLEAN AS $$
DECLARE
    v_count INT;
BEGIN
    SELECT COUNT(*) INTO v_count
    FROM core.users_groups ug
    JOIN core.group_permissions gp ON ug.group_id = gp.group_id
    JOIN core.permissions p ON gp.permission_id = p.id
    WHERE ug.user_id = p_user_id
        AND p.code = p_permission_code
        AND ug.is_active = TRUE
        AND ug.left_at IS NULL;

    RETURN v_count > 0;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- 7. TRIGGER REMOVED - No backward compatibility needed
-- ============================================================================
-- Note: Removed trigger for role-to-groups sync as users table no longer has
-- a role column. System works purely with groups now (no hardcoded dependencies).

-- ============================================================================
-- 8. GRANT PERMISSIONS
-- ============================================================================
-- Note: GRANT statements removed - app_role does not exist
-- Permissions will be inherited from database owner

-- ============================================================================
-- 9. CREATE INITIAL SYSTEM GROUPS (ONE-TIME INITIALIZATION)
-- ============================================================================

-- Check if groups already exist, if not create them
INSERT INTO core.groups (name, slug, description, is_system_group, is_protected, group_type, organisation_id)
VALUES
    ('Owner', 'owner', 'Organization owner with full authority', TRUE, TRUE, 'org_admin', NULL),
    ('System Users', 'system-users', 'Regular system users', TRUE, TRUE, 'custom', NULL),
    ('Premium Members', 'premium-members', 'Premium subscription members', TRUE, TRUE, 'custom', NULL),
    ('Content Creators', 'content-creators', 'Content creators and authors', TRUE, TRUE, 'custom', NULL),
    ('Teachers', 'teachers', 'Teacher/instructor accounts', TRUE, TRUE, 'custom', NULL),
    ('School Admins', 'school-admin', 'School administration accounts', TRUE, TRUE, 'org_admin', NULL),
    ('Company Admins', 'company-admin', 'Company administration accounts', TRUE, TRUE, 'org_admin', NULL),
    ('Content Moderators', 'content-moderators', 'Content moderation team', TRUE, TRUE, 'custom', NULL),
    ('Support Team', 'support-team', 'Support team members', TRUE, TRUE, 'custom', NULL),
    ('System Admin', 'system-admin', 'System administrators with full access', TRUE, TRUE, 'system_admin', NULL)
ON CONFLICT (slug) DO NOTHING;

-- ============================================================================
-- 10. DISPLAY MIGRATION SUMMARY
-- ============================================================================
DO $$
DECLARE
    v_groups_count INT;
    v_group_perms_count INT;
BEGIN
    SELECT COUNT(*) INTO v_groups_count FROM core.groups WHERE is_system_group = TRUE;
    SELECT COUNT(*) INTO v_group_perms_count FROM core.group_permissions;

    RAISE NOTICE '
    ╔════════════════════════════════════════════════════════════════╗
    ║        MIGRATION 096: Group-Based System Initialized           ║
    ╠════════════════════════════════════════════════════════════════╣
    ║ System groups created: %                                       ║
    ║ Group permissions seeded: %                                    ║
    ║ Status: Ready for Phase 2 (Domain Models & Repositories)       ║
    ╚════════════════════════════════════════════════════════════════╝
    ', v_groups_count, v_group_perms_count;
END $$;

COMMIT;
