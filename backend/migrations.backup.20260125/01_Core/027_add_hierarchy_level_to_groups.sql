-- ============================================================================
-- Migration: 027_add_hierarchy_level_to_groups.sql
-- Description: Add hierarchy_level column to groups table for flexible authorization
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-01-25
-- ============================================================================

-- Purpose: Enable hierarchical group structure where level 1000 is the highest authority
-- This allows up to 999 custom groups below system admin level
-- Hierarchy Level Scale:
--   1000 = Owner/Super Admin (highest)
--   900-999 = System Administrators
--   700-899 = Organization Administrators
--   500-699 = Content Management
--   300-499 = Teachers/Instructors
--   100-299 = Regular Users
--   1-99 = Guest/Limited Access

BEGIN;

-- ============================================================================
-- 1. ADD hierarchy_level COLUMN TO groups TABLE
-- ============================================================================

ALTER TABLE core.groups
    ADD COLUMN IF NOT EXISTS hierarchy_level INT DEFAULT 100
    CONSTRAINT chk_hierarchy_level_range CHECK (hierarchy_level >= 1 AND hierarchy_level <= 1000);

-- Create index for performance (queries by hierarchy level)
CREATE INDEX IF NOT EXISTS idx_groups_hierarchy_level
    ON core.groups(hierarchy_level DESC);

-- Composite index for frequently used queries (org + hierarchy)
CREATE INDEX IF NOT EXISTS idx_groups_org_hierarchy
    ON core.groups(organisation_id, hierarchy_level DESC)
    WHERE organisation_id IS NOT NULL;

-- Add comment
COMMENT ON COLUMN core.groups.hierarchy_level IS
    'Hierarchical level for authorization (1-1000). Higher number = more authority. 1000 = Owner/SuperAdmin (highest). Allows up to 999 custom groups.';

-- ============================================================================
-- 2. UPDATE EXISTING SYSTEM GROUPS WITH HIERARCHY LEVELS
-- ============================================================================

-- System Owner (highest authority - level 1000)
UPDATE core.groups
SET hierarchy_level = 1000
WHERE slug = 'owner'
  AND hierarchy_level != 1000;

-- System Admin (highest system access - level 950)
UPDATE core.groups
SET hierarchy_level = 950
WHERE slug = 'system-admin'
  AND hierarchy_level != 950;

-- Organization Admins (level 800)
UPDATE core.groups
SET hierarchy_level = 800
WHERE slug IN ('school-admin', 'company-admin')
  AND hierarchy_level != 800;

-- Content Management (level 600)
UPDATE core.groups
SET hierarchy_level = 600
WHERE slug IN ('content-creators', 'content-moderators')
  AND hierarchy_level != 600;

-- Teachers (level 400)
UPDATE core.groups
SET hierarchy_level = 400
WHERE slug = 'teachers'
  AND hierarchy_level != 400;

-- Support Team (level 350)
UPDATE core.groups
SET hierarchy_level = 350
WHERE slug = 'support-team'
  AND hierarchy_level != 350;

-- Premium Members (level 250)
UPDATE core.groups
SET hierarchy_level = 250
WHERE slug = 'premium-members'
  AND hierarchy_level != 250;

-- Regular System Users (level 100)
UPDATE core.groups
SET hierarchy_level = 100
WHERE slug = 'system-users'
  AND hierarchy_level != 100;

-- ============================================================================
-- 3. CREATE HELPER FUNCTION: Get user's maximum hierarchy level
-- ============================================================================

CREATE OR REPLACE FUNCTION get_user_max_hierarchy_level(p_user_id UUID)
RETURNS INT AS $$
DECLARE
    v_max_level INT;
BEGIN
    -- Get the highest hierarchy level from all active groups
    SELECT MAX(g.hierarchy_level) INTO v_max_level
    FROM core.users_groups ug
    JOIN core.groups g ON ug.group_id = g.id
    WHERE ug.user_id = p_user_id
        AND ug.is_active = TRUE
        AND ug.left_at IS NULL;

    -- Default to 0 if no active group found
    RETURN COALESCE(v_max_level, 0);
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- 4. CREATE HELPER FUNCTION: Check if user has minimum hierarchy level
-- ============================================================================

CREATE OR REPLACE FUNCTION user_has_hierarchy_level(p_user_id UUID, p_required_level INT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN get_user_max_hierarchy_level(p_user_id) >= p_required_level;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- 5. CREATE HELPER FUNCTION: Get user's highest authority group
-- ============================================================================

CREATE OR REPLACE FUNCTION get_user_highest_authority_group(p_user_id UUID)
RETURNS TABLE(
    group_id UUID,
    group_name VARCHAR,
    hierarchy_level INT,
    frontend_role VARCHAR
)
AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT ON (g.hierarchy_level DESC)
        g.id,
        g.name,
        g.hierarchy_level,
        COALESCE(g.frontend_role, 'Free')
    FROM core.users_groups ug
    JOIN core.groups g ON ug.group_id = g.id
    WHERE ug.user_id = p_user_id
        AND ug.is_active = TRUE
        AND ug.left_at IS NULL
    ORDER BY g.hierarchy_level DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- 6. CREATE HELPER FUNCTION: Validate hierarchy before assignment
-- ============================================================================

CREATE OR REPLACE FUNCTION validate_hierarchy_assignment(
    p_admin_user_id UUID,
    p_target_group_hierarchy INT
)
RETURNS TABLE(is_valid BOOLEAN, reason VARCHAR) AS $$
DECLARE
    v_admin_level INT;
BEGIN
    -- Get admin's maximum hierarchy level
    v_admin_level := get_user_max_hierarchy_level(p_admin_user_id);

    -- Admin can only assign to groups with lower or equal hierarchy level
    IF v_admin_level IS NULL OR v_admin_level = 0 THEN
        RETURN QUERY SELECT FALSE, 'User has no group assignment'::VARCHAR;
    ELSIF v_admin_level < p_target_group_hierarchy THEN
        RETURN QUERY SELECT FALSE, format('Admin level %s cannot assign to level %s', v_admin_level, p_target_group_hierarchy)::VARCHAR;
    ELSE
        RETURN QUERY SELECT TRUE, 'Assignment valid'::VARCHAR;
    END IF;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- 7. CREATE AUDIT FUNCTION: Log hierarchy changes
-- ============================================================================

CREATE OR REPLACE FUNCTION audit_hierarchy_assignment(
    p_user_id UUID,
    p_group_id UUID,
    p_group_hierarchy INT,
    p_admin_id UUID,
    p_action VARCHAR
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO audit_logs (
        event_type,
        user_id,
        action,
        severity,
        metadata,
        created_at
    )
    VALUES (
        'hierarchy_assignment',
        p_admin_id,
        p_action,
        'medium',
        jsonb_build_object(
            'target_user_id', p_user_id,
            'group_id', p_group_id,
            'group_hierarchy_level', p_group_hierarchy,
            'admin_hierarchy_level', get_user_max_hierarchy_level(p_admin_id),
            'timestamp', NOW()
        ),
        NOW()
    );
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 8. CREATE DISPLAY MIGRATION SUMMARY
-- ============================================================================

DO $$
DECLARE
    v_groups_with_hierarchy INT;
BEGIN
    SELECT COUNT(*) INTO v_groups_with_hierarchy
    FROM core.groups
    WHERE hierarchy_level IS NOT NULL;

    RAISE NOTICE '
    ╔════════════════════════════════════════════════════════════════╗
    ║   MIGRATION 027: Add Hierarchical Authorization - COMPLETE    ║
    ╠════════════════════════════════════════════════════════════════╣
    ║ Groups updated with hierarchy_level: %                         ║
    ║ Helper functions created: 4 new functions                      ║
    ║ - get_user_max_hierarchy_level()                               ║
    ║ - user_has_hierarchy_level()                                   ║
    ║ - get_user_highest_authority_group()                           ║
    ║ - validate_hierarchy_assignment()                              ║
    ║ - audit_hierarchy_assignment()                                 ║
    ║                                                                ║
    ║ Hierarchy Scale (1-1000):                                      ║
    ║   1000 = Owner/Super Admin (highest)                           ║
    ║   950  = System Admin                                          ║
    ║   800  = Organization Admin                                    ║
    ║   600  = Content Management                                    ║
    ║   400  = Teachers                                              ║
    ║   350  = Support Team                                          ║
    ║   250  = Premium Members                                       ║
    ║   100  = Regular Users                                         ║
    ║   1-99 = Guest/Limited Access                                  ║
    ║                                                                ║
    ║ Status: Ready for flexible group creation (up to 999 custom)  ║
    ╚════════════════════════════════════════════════════════════════╝
    ', v_groups_with_hierarchy;
END $$;

COMMIT;
