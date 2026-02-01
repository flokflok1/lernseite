-- ============================================================================
-- Migration: 026_add_frontend_role_to_groups.sql
-- Description: Add frontend_role column to groups table for GBA frontend compatibility
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-01-22
-- ============================================================================

-- Purpose: Map group slugs to frontend-compatible role values for backward compatibility
-- Frontend expects: Free, Premium, Creator, Teacher, School, Company,
--                   Support, Moderator, Admin, school_admin, company_admin, owner

BEGIN;

-- ============================================================================
-- 1. ADD frontend_role COLUMN TO groups TABLE
-- ============================================================================

ALTER TABLE core.groups
    ADD COLUMN IF NOT EXISTS frontend_role VARCHAR(50) DEFAULT 'Free';

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_groups_frontend_role
    ON core.groups(frontend_role);

-- Add comment
COMMENT ON COLUMN core.groups.frontend_role IS
    'Frontend-compatible role value for backward compatibility. Maps to UserRoleEnum in frontend.';

-- ============================================================================
-- 2. UPDATE EXISTING SYSTEM GROUPS WITH FRONTEND ROLES
-- ============================================================================

-- Platform Admin (highest level - system-admin group)
UPDATE core.groups
SET frontend_role = 'Admin'
WHERE slug = 'system-admin';

-- Organization Owners
UPDATE core.groups
SET frontend_role = 'owner'
WHERE slug = 'owner';

-- School Admin
UPDATE core.groups
SET frontend_role = 'school_admin'
WHERE slug = 'school-admin';

-- Company Admin
UPDATE core.groups
SET frontend_role = 'company_admin'
WHERE slug = 'company-admin';

-- Content Creators
UPDATE core.groups
SET frontend_role = 'Creator'
WHERE slug = 'content-creators';

-- Teachers
UPDATE core.groups
SET frontend_role = 'Teacher'
WHERE slug = 'teachers';

-- Content Moderators
UPDATE core.groups
SET frontend_role = 'Moderator'
WHERE slug = 'content-moderators';

-- Support Team
UPDATE core.groups
SET frontend_role = 'Support'
WHERE slug = 'support-team';

-- Premium Members
UPDATE core.groups
SET frontend_role = 'Premium'
WHERE slug = 'premium-members';

-- System Users (Free tier)
UPDATE core.groups
SET frontend_role = 'Free'
WHERE slug = 'system-users';

-- ============================================================================
-- 3. CREATE HELPER FUNCTION: Get frontend role for user
-- ============================================================================

CREATE OR REPLACE FUNCTION get_user_frontend_role(p_user_id UUID)
RETURNS VARCHAR AS $$
DECLARE
    v_frontend_role VARCHAR;
BEGIN
    -- Get frontend_role from user's primary (first joined) active group
    SELECT g.frontend_role INTO v_frontend_role
    FROM core.users_groups ug
    JOIN core.groups g ON ug.group_id = g.id
    WHERE ug.user_id = p_user_id
        AND ug.is_active = TRUE
        AND ug.left_at IS NULL
    ORDER BY ug.joined_at ASC
    LIMIT 1;

    -- Default to 'Free' if no active group found
    RETURN COALESCE(v_frontend_role, 'Free');
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- 4. DISPLAY MIGRATION SUMMARY
-- ============================================================================

DO $$
DECLARE
    v_groups_updated INT;
BEGIN
    SELECT COUNT(*) INTO v_groups_updated
    FROM core.groups
    WHERE frontend_role IS NOT NULL AND frontend_role != 'Free';

    RAISE NOTICE '
    ╔════════════════════════════════════════════════════════════════╗
    ║      MIGRATION 026: Add frontend_role to groups - COMPLETE    ║
    ╠════════════════════════════════════════════════════════════════╣
    ║ Groups updated with frontend_role: %                           ║
    ║ Helper function created: get_user_frontend_role()              ║
    ║ Status: GBA Frontend Compatibility Ready                       ║
    ╚════════════════════════════════════════════════════════════════╝
    ', v_groups_updated;
END $$;

COMMIT;
