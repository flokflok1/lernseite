-- Migration 093: Create users_groups junction table
-- Beschreibung: Junction table für Many-to-Many Beziehung zwischen Usern und Groups
-- Datum: 2026-01-22
-- Status: Phase 1 - Database Schema

BEGIN;

-- ============================================================================
-- 1. CREATE USERS_GROUPS JUNCTION TABLE
-- ============================================================================
CREATE TABLE users_groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign Keys
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    group_id UUID NOT NULL REFERENCES groups(id) ON DELETE CASCADE,

    -- Membership Details
    member_role VARCHAR(50) NOT NULL DEFAULT 'member',  -- member, editor, owner, moderator, admin
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    left_at TIMESTAMP WITH TIME ZONE,  -- Soft delete: NULL = still member, has value = left

    -- Status
    is_active BOOLEAN DEFAULT TRUE,

    -- Audit Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    added_by UUID REFERENCES users(id) ON DELETE SET NULL,

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
    ON users_groups(user_id);

CREATE INDEX idx_users_groups_group_id
    ON users_groups(group_id);

CREATE INDEX idx_users_groups_active
    ON users_groups(is_active)
    WHERE is_active = TRUE;

CREATE INDEX idx_users_groups_member_role
    ON users_groups(member_role);

CREATE INDEX idx_users_groups_joined_at
    ON users_groups(joined_at DESC);

-- Composite index for common queries: "Get all active groups for a user"
CREATE INDEX idx_users_groups_user_active
    ON users_groups(user_id, is_active)
    WHERE is_active = TRUE;

-- Composite index for: "Get all members of a group"
CREATE INDEX idx_users_groups_group_active
    ON users_groups(group_id, is_active)
    WHERE is_active = TRUE;

-- Index for: "Get all group owners"
CREATE INDEX idx_users_groups_owner_role
    ON users_groups(group_id, member_role)
    WHERE member_role IN ('owner', 'admin') AND is_active = TRUE;

-- ============================================================================
-- 3. ENABLE ROW-LEVEL SECURITY
-- ============================================================================
ALTER TABLE users_groups ENABLE ROW LEVEL SECURITY;

-- Users can see their own group memberships
CREATE POLICY users_groups_self_access ON users_groups
    FOR SELECT
    USING (user_id = current_user_id());

-- Only admins can modify group membership
CREATE POLICY users_groups_modify ON users_groups
    FOR INSERT, UPDATE, DELETE
    USING (current_user_is_admin());

-- ============================================================================
-- 4. CREATE TRIGGER FOR updated_at
-- ============================================================================
CREATE TRIGGER trigger_users_groups_updated_at
    BEFORE UPDATE ON users_groups
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
    FROM users_groups ug
    JOIN groups g ON ug.group_id = g.id
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
        u.id,
        u.email,
        ug.member_role,
        ug.joined_at
    FROM users_groups ug
    JOIN users u ON ug.user_id = u.id
    WHERE ug.group_id = p_group_id
        AND ug.is_active = TRUE
        AND ug.left_at IS NULL
    ORDER BY ug.joined_at DESC;
$$ LANGUAGE SQL STABLE;

-- ============================================================================
-- 7. GRANT PERMISSIONS
-- ============================================================================
GRANT SELECT, INSERT, UPDATE, DELETE ON users_groups TO app_role;
GRANT SELECT ON users_groups TO app_readonly;
GRANT EXECUTE ON FUNCTION get_user_active_groups TO app_role;
GRANT EXECUTE ON FUNCTION get_group_members TO app_role;

COMMIT;
