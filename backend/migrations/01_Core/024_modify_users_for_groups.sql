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
ALTER TABLE users
    ADD COLUMN IF NOT EXISTS groups_override JSONB DEFAULT NULL,  -- Emergency group override
    ADD COLUMN IF NOT EXISTS last_group_sync TIMESTAMP WITH TIME ZONE DEFAULT NULL,  -- When groups were last synced from roles
    ADD COLUMN IF NOT EXISTS migration_roles_to_groups_date TIMESTAMP WITH TIME ZONE DEFAULT NULL;  -- When user was migrated

-- Create indices for new columns
CREATE INDEX IF NOT EXISTS idx_users_migration_roles_to_groups_date
    ON users(migration_roles_to_groups_date)
    WHERE migration_roles_to_groups_date IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_users_last_group_sync
    ON users(last_group_sync DESC)
    WHERE last_group_sync IS NOT NULL;

-- ============================================================================
-- 2. CREATE HELPER FUNCTION: Migrate single user from role to group
-- ============================================================================
CREATE OR REPLACE FUNCTION migrate_user_to_groups(p_user_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
    v_user_role VARCHAR;
    v_group_id UUID;
    v_member_role VARCHAR;
BEGIN
    -- Get user's current role
    SELECT role INTO v_user_role FROM users WHERE id = p_user_id;

    IF v_user_role IS NULL THEN
        RETURN FALSE;
    END IF;

    -- Determine target group and member role based on current role
    CASE v_user_role
        WHEN 'user' THEN
            SELECT id INTO v_group_id FROM groups WHERE slug = 'system-users' AND is_system_group = TRUE LIMIT 1;
            v_member_role := 'member';
        WHEN 'premium' THEN
            SELECT id INTO v_group_id FROM groups WHERE slug = 'premium-members' AND is_system_group = TRUE LIMIT 1;
            v_member_role := 'member';
        WHEN 'creator' THEN
            SELECT id INTO v_group_id FROM groups WHERE slug = 'content-creators' AND is_system_group = TRUE LIMIT 1;
            v_member_role := 'member';
        WHEN 'teacher' THEN
            SELECT id INTO v_group_id FROM groups WHERE slug = 'teachers' AND is_system_group = TRUE LIMIT 1;
            v_member_role := 'member';
        WHEN 'school_admin' THEN
            SELECT id INTO v_group_id FROM groups WHERE slug = 'school-admin' AND is_system_group = TRUE LIMIT 1;
            v_member_role := 'owner';
        WHEN 'company_admin' THEN
            SELECT id INTO v_group_id FROM groups WHERE slug = 'company-admin' AND is_system_group = TRUE LIMIT 1;
            v_member_role := 'owner';
        WHEN 'moderator' THEN
            SELECT id INTO v_group_id FROM groups WHERE slug = 'content-moderators' AND is_system_group = TRUE LIMIT 1;
            v_member_role := 'moderator';
        WHEN 'support' THEN
            SELECT id INTO v_group_id FROM groups WHERE slug = 'support-team' AND is_system_group = TRUE LIMIT 1;
            v_member_role := 'admin';
        WHEN 'admin', 'superadmin' THEN
            SELECT id INTO v_group_id FROM groups WHERE slug = 'system-admin' AND is_system_group = TRUE LIMIT 1;
            v_member_role := 'owner';
        ELSE
            -- Default: map to system-users
            SELECT id INTO v_group_id FROM groups WHERE slug = 'system-users' AND is_system_group = TRUE LIMIT 1;
            v_member_role := 'member';
    END CASE;

    -- Insert into users_groups if not already present
    INSERT INTO users_groups (user_id, group_id, member_role, joined_at)
    VALUES (p_user_id, v_group_id, v_member_role, COALESCE((SELECT created_at FROM users WHERE id = p_user_id), NOW()))
    ON CONFLICT (user_id, group_id) DO NOTHING;

    -- Update migration tracking
    UPDATE users
    SET
        last_group_sync = NOW(),
        migration_roles_to_groups_date = COALESCE(migration_roles_to_groups_date, NOW())
    WHERE id = p_user_id;

    RETURN TRUE;
EXCEPTION WHEN OTHERS THEN
    RETURN FALSE;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 3. CREATE HELPER FUNCTION: Migrate all users from role to group
-- ============================================================================
CREATE OR REPLACE FUNCTION migrate_all_users_to_groups()
RETURNS TABLE(total_users INT, migrated_count INT, failed_count INT)
AS $$
DECLARE
    v_total INT;
    v_migrated INT := 0;
    v_failed INT := 0;
    v_user_id UUID;
    v_cursor CURSOR FOR SELECT id FROM users WHERE role IS NOT NULL AND migration_roles_to_groups_date IS NULL;
BEGIN
    SELECT COUNT(*) INTO v_total FROM users WHERE role IS NOT NULL;

    OPEN v_cursor;
    LOOP
        FETCH v_cursor INTO v_user_id;
        EXIT WHEN v_cursor%NOTFOUND;

        IF migrate_user_to_groups(v_user_id) THEN
            v_migrated := v_migrated + 1;
        ELSE
            v_failed := v_failed + 1;
        END IF;
    END LOOP;
    CLOSE v_cursor;

    RETURN QUERY SELECT v_total, v_migrated, v_failed;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 4. CREATE HELPER FUNCTION: Verify migration completion
-- ============================================================================
CREATE OR REPLACE FUNCTION verify_user_group_migration_completion()
RETURNS TABLE(
    total_users_with_roles INT,
    users_in_groups INT,
    migration_percentage NUMERIC,
    status VARCHAR
)
AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(DISTINCT u.id)::INT as total_users_with_roles,
        COUNT(DISTINCT ug.user_id)::INT as users_in_groups,
        (COUNT(DISTINCT ug.user_id)::NUMERIC / NULLIF(COUNT(DISTINCT u.id), 0) * 100)::NUMERIC(5,2) as migration_percentage,
        CASE
            WHEN COUNT(DISTINCT ug.user_id) = COUNT(DISTINCT u.id) THEN 'COMPLETE'
            WHEN COUNT(DISTINCT ug.user_id) > 0 THEN 'IN_PROGRESS'
            ELSE 'NOT_STARTED'
        END as status
    FROM users u
    LEFT JOIN users_groups ug ON u.id = ug.user_id AND ug.is_active = TRUE
    WHERE u.role IS NOT NULL;
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
    FROM users_groups ug
    JOIN group_permissions gp ON ug.group_id = gp.group_id
    JOIN permissions p ON gp.permission_id = p.id
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
    FROM users_groups ug
    JOIN group_permissions gp ON ug.group_id = gp.group_id
    JOIN permissions p ON gp.permission_id = p.id
    WHERE ug.user_id = p_user_id
        AND p.code = p_permission_code
        AND ug.is_active = TRUE
        AND ug.left_at IS NULL;

    RETURN v_count > 0;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- 7. CREATE TRIGGER: Auto-sync groups when role changes (backward compatibility)
-- ============================================================================
CREATE OR REPLACE FUNCTION trigger_sync_groups_on_role_change()
RETURNS TRIGGER AS $$
BEGIN
    -- Only trigger if role actually changed
    IF OLD.role != NEW.role THEN
        -- Re-migrate the user to the new role's corresponding group
        PERFORM migrate_user_to_groups(NEW.id);

        -- Log the change
        RAISE NOTICE 'User % role changed from % to %, groups re-synced', NEW.id, OLD.role, NEW.role;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create the trigger (only if it doesn't already exist)
DROP TRIGGER IF EXISTS trigger_user_role_to_groups_sync ON users;
CREATE TRIGGER trigger_user_role_to_groups_sync
    BEFORE UPDATE OF role ON users
    FOR EACH ROW
    WHEN (OLD.role IS DISTINCT FROM NEW.role)
    EXECUTE FUNCTION trigger_sync_groups_on_role_change();

-- ============================================================================
-- 8. GRANT PERMISSIONS
-- ============================================================================
GRANT EXECUTE ON FUNCTION migrate_user_to_groups TO app_role;
GRANT EXECUTE ON FUNCTION migrate_all_users_to_groups TO app_role;
GRANT EXECUTE ON FUNCTION verify_user_group_migration_completion TO app_role;
GRANT EXECUTE ON FUNCTION get_user_effective_permissions TO app_role;
GRANT EXECUTE ON FUNCTION user_has_permission TO app_role;

-- ============================================================================
-- 9. CREATE INITIAL SYSTEM GROUPS (ONE-TIME INITIALIZATION)
-- ============================================================================

-- Check if groups already exist, if not create them
INSERT INTO groups (name, slug, description, is_system_group, is_protected, group_type, organisation_id)
VALUES
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
    SELECT COUNT(*) INTO v_groups_count FROM groups WHERE is_system_group = TRUE;
    SELECT COUNT(*) INTO v_group_perms_count FROM group_permissions;

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
