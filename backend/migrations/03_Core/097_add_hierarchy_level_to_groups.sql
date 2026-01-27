-- Version: 1.6.0
-- Description: Add hierarchy_level to groups and functions for Level-Based Authorization (Phase B - GBA)
-- Date: 2026-01-27
-- Purpose: Implement database-driven, level-based authorization system (0-1000 scale) that requires zero code changes when new permission levels are added

BEGIN;

-- ============================================================================
-- 1. ADD HIERARCHY_LEVEL TO GROUPS TABLE (idempotent)
-- ============================================================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'core' AND table_name = 'groups' AND column_name = 'hierarchy_level'
    ) THEN
        ALTER TABLE core.groups
        ADD COLUMN hierarchy_level INTEGER DEFAULT 0 CHECK (hierarchy_level >= 0 AND hierarchy_level <= 1000);
    END IF;
END $$;

COMMENT ON COLUMN core.groups.hierarchy_level IS 'Hierarchical level 0-1000. Higher = more permissions. 1000=Owner, 900=SystemAdmin, 750=Moderator, 500=OrgAdmin, 250=Creator, 100=Premium, 10=Member, 0=Guest';

-- ============================================================================
-- 2. SET HIERARCHY LEVELS FOR SYSTEM GROUPS
-- ============================================================================

-- Owner (1000 - highest)
UPDATE core.groups SET hierarchy_level =1000 WHERE slug = 'owner' AND is_system_group = TRUE;

-- System Admin (900)
UPDATE core.groups SET hierarchy_level =900 WHERE slug = 'system-admin' AND is_system_group = TRUE;

-- Moderators (750)
UPDATE core.groups SET hierarchy_level =750 WHERE slug = 'content-moderators' AND is_system_group = TRUE;

-- Organisation Admin (500)
UPDATE core.groups SET hierarchy_level =500 WHERE slug IN ('org-admin', 'school-admin', 'company-admin') AND is_system_group = FALSE;

-- Teachers/Creators (250)
UPDATE core.groups SET hierarchy_level =250 WHERE slug IN ('teachers', 'content-creators') AND is_system_group = FALSE;

-- Premium Members (100)
UPDATE core.groups SET hierarchy_level =100 WHERE slug = 'premium-members' AND is_system_group = FALSE;

-- Regular Members (10)
UPDATE core.groups SET hierarchy_level =10 WHERE slug = 'system-users' AND is_system_group = FALSE;

-- Support Team (400)
UPDATE core.groups SET hierarchy_level =400 WHERE slug = 'support-team' AND is_system_group = FALSE;

-- ============================================================================
-- 3. ADD HIERARCHY_LEVEL TO USERS_GROUPS JUNCTION TABLE (idempotent)
-- ============================================================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'core' AND table_name = 'users_groups' AND column_name = 'hierarchy_level'
    ) THEN
        ALTER TABLE core.users_groups
        ADD COLUMN hierarchy_level INTEGER DEFAULT 0 CHECK (hierarchy_level >= 0 AND hierarchy_level <= 1000);
    END IF;
END $$;

COMMENT ON COLUMN core.users_groups.hierarchy_level IS 'User-specific level override in group. If set, takes precedence over group default.';

-- ============================================================================
-- 4. CREATE INDEX FOR HIERARCHY_LEVEL QUERIES (idempotent)
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_groups_hierarchy_level
    ON core.groups(hierarchy_level DESC)
    WHERE hierarchy_level > 0;

CREATE INDEX IF NOT EXISTS idx_users_groups_hierarchy_level
    ON core.users_groups(hierarchy_level DESC)
    WHERE hierarchy_level > 0;

-- ============================================================================
-- 5. CREATE FUNCTION: Get user's maximum hierarchy level
-- ============================================================================
DROP FUNCTION IF EXISTS core.get_user_hierarchy_level(UUID);
CREATE FUNCTION core.get_user_hierarchy_level(p_user_id UUID)
RETURNS INTEGER AS $$
DECLARE
    v_max_level INTEGER;
BEGIN
    -- Get the maximum hierarchy level from all user's groups
    -- Use user-specific override if set, otherwise use group default
    SELECT COALESCE(MAX(COALESCE(ug.hierarchy_level, g.hierarchy_level)), 0)
    INTO v_max_level
    FROM core.users_groups ug
    JOIN core.groups g ON ug.group_id = g.id
    WHERE ug.user_id = p_user_id;

    RETURN COALESCE(v_max_level, 0);
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- 6. CREATE FUNCTION: Check if user has minimum hierarchy level
-- ============================================================================
DROP FUNCTION IF EXISTS core.user_has_hierarchy_level(UUID, INTEGER);
CREATE FUNCTION core.user_has_hierarchy_level(p_user_id UUID, p_required_level INTEGER)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN core.get_user_hierarchy_level(p_user_id) >= p_required_level;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- 7. CREATE FUNCTION: Get all groups for user with their effective level
-- ============================================================================
DROP FUNCTION IF EXISTS core.get_user_groups_with_level(UUID);
CREATE FUNCTION core.get_user_groups_with_level(p_user_id UUID)
RETURNS TABLE(
    group_id UUID,
    group_name VARCHAR,
    group_type VARCHAR,
    hierarchy_level INTEGER,
    is_system_group BOOLEAN
) AS $$
    SELECT
        g.id,
        g.name,
        g.group_type,
        COALESCE(ug.hierarchy_level, g.hierarchy_level) AS hierarchy_level,
        g.is_system_group
    FROM core.users_groups ug
    JOIN core.groups g ON ug.group_id = g.id
    WHERE ug.user_id = p_user_id
    ORDER BY hierarchy_level DESC;
$$ LANGUAGE SQL STABLE;

-- ============================================================================
-- 8. COMMIT TRANSACTION
-- ============================================================================
COMMIT;
