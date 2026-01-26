-- Rollback Script: Remove group-based system
-- Beschreibung: Notfalls-Rollback für das komplette Group-Based RBAC 3.0 System
-- Datum: 2026-01-22
-- Status: Phase 1 - Database Schema (Emergency Rollback)
-- Verwendung: NUR im Notfall verwenden, wenn die Migration fehlgeschlagen ist

BEGIN;

-- ============================================================================
-- 1. DROP TRIGGERS
-- ============================================================================
DROP TRIGGER IF EXISTS trigger_user_role_to_groups_sync ON users CASCADE;
DROP TRIGGER IF EXISTS trigger_users_groups_updated_at ON users_groups CASCADE;
DROP TRIGGER IF EXISTS trigger_groups_updated_at ON groups CASCADE;
DROP TRIGGER IF EXISTS trigger_permissions_updated_at ON permissions CASCADE;

-- ============================================================================
-- 2. DROP HELPER FUNCTIONS (in reverse order of dependency)
-- ============================================================================
DROP FUNCTION IF EXISTS user_has_permission(UUID, VARCHAR) CASCADE;
DROP FUNCTION IF EXISTS get_user_effective_permissions(UUID) CASCADE;
DROP FUNCTION IF EXISTS verify_user_group_migration_completion() CASCADE;
DROP FUNCTION IF EXISTS migrate_all_users_to_groups() CASCADE;
DROP FUNCTION IF EXISTS migrate_user_to_groups(UUID) CASCADE;
DROP FUNCTION IF EXISTS group_has_permission(UUID, VARCHAR) CASCADE;
DROP FUNCTION IF EXISTS get_groups_with_permission(VARCHAR) CASCADE;
DROP FUNCTION IF EXISTS get_group_permissions(UUID) CASCADE;
DROP FUNCTION IF EXISTS get_permissions_by_category(VARCHAR) CASCADE;
DROP FUNCTION IF EXISTS get_permission_by_code(VARCHAR) CASCADE;
DROP FUNCTION IF EXISTS get_group_members(UUID) CASCADE;
DROP FUNCTION IF EXISTS get_user_active_groups(UUID) CASCADE;

-- ============================================================================
-- 3. DROP POLICIES (Row-Level Security)
-- ============================================================================
DROP POLICY IF EXISTS users_groups_modify ON users_groups CASCADE;
DROP POLICY IF EXISTS users_groups_self_access ON users_groups CASCADE;
DROP POLICY IF EXISTS groups_org_isolation ON groups CASCADE;

-- ============================================================================
-- 4. DROP TABLES (in reverse order of dependency)
-- ============================================================================
DROP TABLE IF EXISTS group_permissions CASCADE;
DROP TABLE IF EXISTS users_groups CASCADE;
DROP TABLE IF EXISTS permissions CASCADE;
DROP TABLE IF EXISTS groups CASCADE;

-- ============================================================================
-- 5. REMOVE NEW COLUMNS FROM USERS TABLE
-- ============================================================================
ALTER TABLE users
    DROP COLUMN IF EXISTS groups_override,
    DROP COLUMN IF EXISTS last_group_sync,
    DROP COLUMN IF EXISTS migration_roles_to_groups_date;

-- ============================================================================
-- 6. DROP INDICES (if any remain)
-- ============================================================================
DROP INDEX IF EXISTS idx_users_migration_roles_to_groups_date CASCADE;
DROP INDEX IF EXISTS idx_users_last_group_sync CASCADE;

-- ============================================================================
-- 7. RESTORE PERMISSIONS (grant back to old roles system)
-- ============================================================================
-- This assumes the old role-based system is still in place
-- No specific action needed as old tables/functions remain

-- ============================================================================
-- 8. DISPLAY ROLLBACK STATUS
-- ============================================================================
DO $$
BEGIN
    RAISE NOTICE '
    ╔════════════════════════════════════════════════════════════════╗
    ║        ROLLBACK: Group-Based System Removed                    ║
    ╠════════════════════════════════════════════════════════════════╣
    ║ ✓ All group-based tables dropped                               ║
    ║ ✓ All helper functions removed                                 ║
    ║ ✓ All row-level security policies removed                      ║
    ║ ✓ New columns from users table removed                         ║
    ║ ✓ System reverted to role-based access control                 ║
    ║                                                                 ║
    ║ Status: OLD SYSTEM ACTIVE (role-based RBAC)                    ║
    ╚════════════════════════════════════════════════════════════════╝
    ';
END $$;

COMMIT;
