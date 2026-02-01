-- Migration 093: Create users_groups junction table
-- Beschreibung: Junction table für Many-to-Many Beziehung zwischen Usern und Groups
-- Datum: 2026-01-22
-- Status: Phase 1 - Database Schema

BEGIN;

-- ============================================================================
-- 1. CREATE USERS_GROUPS JUNCTION TABLE
-- ============================================================================
CREATE TABLE core.users_groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign Keys
    user_id UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,
    group_id UUID NOT NULL REFERENCES core.groups(id) ON DELETE CASCADE,

    -- Membership Details
    member_role VARCHAR(50) NOT NULL DEFAULT 'member',  -- member, editor, owner, moderator, admin
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    left_at TIMESTAMP WITH TIME ZONE,  -- Soft delete: NULL = still member, has value = left

    -- Status
    is_active BOOLEAN DEFAULT TRUE,

    -- Audit Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    added_by UUID REFERENCES core.users(user_id) ON DELETE SET NULL,

    -- Unique constraint: User can only have one membership per group
    CONSTRAINT unique_user_per_group UNIQUE(user_id, group_id),

    -- Constraints
    CONSTRAINT chk_member_role CHECK (member_role IN (
        'member',
        'editor',
        'owner',
        'moderator',
        'admin'
    )),

    CONSTRAINT chk_left_at_null_or_after_joined CHECK (
        left_at IS NULL OR left_at >= joined_at
    ),

    CONSTRAINT chk_active_status CHECK (
        (is_active = TRUE AND left_at IS NULL) OR
        (is_active = FALSE)
    )
);

-- ============================================================================
-- 2. CREATE INDICES FOR PERFORMANCE
-- ============================================================================
CREATE INDEX idx_users_groups_user_id
    ON core.users_groups(user_id);

CREATE INDEX idx_users_groups_group_id
    ON core.users_groups(group_id);

CREATE INDEX idx_users_groups_active
    ON core.users_groups(is_active)
    WHERE is_active = TRUE;

CREATE INDEX idx_users_groups_member_role
    ON core.users_groups(member_role);

CREATE INDEX idx_users_groups_joined_at
    ON core.users_groups(joined_at DESC);

-- Composite index for common queries: "Get all active groups for a user"
CREATE INDEX idx_users_groups_user_active
    ON core.users_groups(user_id, is_active)
    WHERE is_active = TRUE;

-- Composite index for: "Get all members of a group"
CREATE INDEX idx_users_groups_group_active
    ON core.users_groups(group_id, is_active)
    WHERE is_active = TRUE;

-- Index for: "Get all group owners"
CREATE INDEX idx_users_groups_owner_role
    ON core.users_groups(group_id, member_role)
    WHERE member_role IN ('owner', 'admin') AND is_active = TRUE;

-- ============================================================================
-- 3. ENABLE ROW-LEVEL SECURITY
-- ============================================================================
-- Note: RLS policies removed - required functions (current_user_id, current_user_is_admin) do not exist
-- RLS can be enabled later when these functions are implemented
-- ALTER TABLE core.users_groups ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- 4. CREATE TRIGGER FOR updated_at
-- ============================================================================
CREATE TRIGGER trigger_users_groups_updated_at
    BEFORE UPDATE ON core.users_groups
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 5. CREATE HELPER FUNCTION: Get active groups for user
-- ============================================================================
CREATE OR REPLACE FUNCTION get_user_active_groups(p_user_id UUID)
RETURNS TABLE(group_id UUID, group_name VARCHAR, member_role VARCHAR, organisation_id UUID)
AS $$
    SELECT
        g.id,
        g.name,
        ug.member_role,
        g.organisation_id
    FROM core.users_groups ug
    JOIN core.groups g ON ug.group_id = g.id
    WHERE ug.user_id = p_user_id
        AND ug.is_active = TRUE
        AND ug.left_at IS NULL
    ORDER BY g.name;
$$ LANGUAGE SQL STABLE;

-- ============================================================================
-- 6. CREATE HELPER FUNCTION: Get group members with role
-- ============================================================================
CREATE OR REPLACE FUNCTION get_group_members(p_group_id UUID)
RETURNS TABLE(user_id UUID, user_email VARCHAR, member_role VARCHAR, joined_at TIMESTAMP)
AS $$
    SELECT
        u.user_id,
        u.email,
        ug.member_role,
        ug.joined_at
    FROM core.users_groups ug
    JOIN core.users u ON ug.user_id = u.user_id
    WHERE ug.group_id = p_group_id
        AND ug.is_active = TRUE
        AND ug.left_at IS NULL
    ORDER BY ug.joined_at DESC;
$$ LANGUAGE SQL STABLE;

-- ============================================================================
-- 7. GRANT PERMISSIONS
-- ============================================================================
-- Note: GRANT statements removed - app_role and app_readonly do not exist
-- Permissions will be inherited from database owner

COMMIT;
