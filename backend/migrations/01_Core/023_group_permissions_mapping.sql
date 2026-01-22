-- Migration 095: Create group_permissions mapping table
-- Beschreibung: Junction table für Many-to-Many Beziehung zwischen Groups und Permissions
-- Datum: 2026-01-22
-- Status: Phase 1 - Database Schema

BEGIN;

-- ============================================================================
-- 1. CREATE GROUP_PERMISSIONS JUNCTION TABLE
-- ============================================================================
CREATE TABLE group_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign Keys
    group_id UUID NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,

    -- Audit Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    granted_by UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Unique constraint: Each group can only have a permission once
    CONSTRAINT unique_group_permission UNIQUE(group_id, permission_id)
);

-- ============================================================================
-- 2. CREATE INDICES FOR PERFORMANCE
-- ============================================================================
CREATE INDEX idx_group_permissions_group_id
    ON group_permissions(group_id);

CREATE INDEX idx_group_permissions_permission_id
    ON group_permissions(permission_id);

-- Composite index for common query: "Get all permissions for a group"
CREATE INDEX idx_group_permissions_group_perms
    ON group_permissions(group_id, permission_id);

-- Index for: "Get all groups with a permission"
CREATE INDEX idx_group_permissions_perm_groups
    ON group_permissions(permission_id, group_id);

CREATE INDEX idx_group_permissions_granted_at
    ON group_permissions(granted_at DESC);

-- ============================================================================
-- 3. SEED PERMISSIONS FOR SYSTEM GROUPS
-- ============================================================================

-- Get system group IDs for mapping
WITH system_groups AS (
    SELECT id, slug FROM groups WHERE is_system_group = TRUE
)

-- System Admin Group - All permissions
INSERT INTO group_permissions (group_id, permission_id, granted_by)
SELECT
    (SELECT id FROM system_groups WHERE slug = 'system-admin'),
    p.id,
    NULL
FROM permissions p
WHERE p.is_system_permission = TRUE
ON CONFLICT (group_id, permission_id) DO NOTHING;

-- ============================================================================
-- 4. SEED PERMISSIONS FOR DEFAULT GROUPS
-- ============================================================================

-- Content Creators Group - Can create and edit courses
INSERT INTO group_permissions (group_id, permission_id, granted_by)
SELECT
    (SELECT id FROM groups WHERE slug = 'content-creators' LIMIT 1),
    p.id,
    NULL
FROM permissions p
WHERE p.code IN (
    'courses.create',
    'courses.edit',
    'courses.view',
    'chapters.create',
    'chapters.edit',
    'lessons.create',
    'lessons.edit',
    'learning_methods.create',
    'posts.create',
    'posts.edit',
    'posts.delete',
    'ai.generate',
    'ai.advanced'
)
ON CONFLICT (group_id, permission_id) DO NOTHING;

-- Teachers Group - Can manage courses and students
INSERT INTO group_permissions (group_id, permission_id, granted_by)
SELECT
    (SELECT id FROM groups WHERE slug = 'teachers' LIMIT 1),
    p.id,
    NULL
FROM permissions p
WHERE p.code IN (
    'courses.create',
    'courses.edit',
    'courses.view',
    'chapters.create',
    'chapters.edit',
    'lessons.create',
    'lessons.edit',
    'courses.publish',
    'posts.create',
    'posts.edit',
    'posts.delete',
    'analytics.view',
    'ai.generate',
    'ai.advanced'
)
ON CONFLICT (group_id, permission_id) DO NOTHING;

-- Moderators Group - Can moderate content
INSERT INTO group_permissions (group_id, permission_id, granted_by)
SELECT
    (SELECT id FROM groups WHERE slug = 'content-moderators' LIMIT 1),
    p.id,
    NULL
FROM permissions p
WHERE p.code IN (
    'content.moderate',
    'users.ban',
    'comments.moderate',
    'analytics.view',
    'audit_log.view'
)
ON CONFLICT (group_id, permission_id) DO NOTHING;

-- Support Team Group - Limited admin access
INSERT INTO group_permissions (group_id, permission_id, granted_by)
SELECT
    (SELECT id FROM groups WHERE slug = 'support-team' LIMIT 1),
    p.id,
    NULL
FROM permissions p
WHERE p.code IN (
    'users.manage',
    'analytics.view',
    'audit_log.view',
    'content.moderate'
)
ON CONFLICT (group_id, permission_id) DO NOTHING;

-- Premium Members Group - Advanced features
INSERT INTO group_permissions (group_id, permission_id, granted_by)
SELECT
    (SELECT id FROM groups WHERE slug = 'premium-members' LIMIT 1),
    p.id,
    NULL
FROM permissions p
WHERE p.code IN (
    'ai.generate',
    'ai.advanced',
    'posts.create',
    'posts.edit',
    'posts.delete',
    'comments.create'
)
ON CONFLICT (group_id, permission_id) DO NOTHING;

-- Regular Users Group - Basic permissions
INSERT INTO group_permissions (group_id, permission_id, granted_by)
SELECT
    (SELECT id FROM groups WHERE slug = 'system-users' LIMIT 1),
    p.id,
    NULL
FROM permissions p
WHERE p.code IN (
    'courses.view',
    'profile.edit',
    'password.change',
    'subscriptions.view',
    'posts.create',
    'posts.edit',
    'posts.delete',
    'comments.create',
    'ai.generate'
)
ON CONFLICT (group_id, permission_id) DO NOTHING;

-- ============================================================================
-- 5. CREATE HELPER FUNCTION: Get permissions for a group
-- ============================================================================
CREATE OR REPLACE FUNCTION get_group_permissions(p_group_id UUID)
RETURNS TABLE(permission_code VARCHAR, display_name VARCHAR, category VARCHAR)
AS $$
    SELECT
        p.code,
        p.display_name,
        p.category
    FROM group_permissions gp
    JOIN permissions p ON gp.permission_id = p.id
    WHERE gp.group_id = p_group_id
    ORDER BY p.code;
$$ LANGUAGE SQL STABLE;

-- ============================================================================
-- 6. CREATE HELPER FUNCTION: Get groups with a permission
-- ============================================================================
CREATE OR REPLACE FUNCTION get_groups_with_permission(p_permission_code VARCHAR)
RETURNS TABLE(group_id UUID, group_name VARCHAR, group_type VARCHAR)
AS $$
    SELECT
        g.id,
        g.name,
        g.group_type
    FROM group_permissions gp
    JOIN permissions p ON gp.permission_id = p.id
    JOIN groups g ON gp.group_id = g.id
    WHERE p.code = p_permission_code
    ORDER BY g.name;
$$ LANGUAGE SQL STABLE;

-- ============================================================================
-- 7. CREATE HELPER FUNCTION: Check if group has permission
-- ============================================================================
CREATE OR REPLACE FUNCTION group_has_permission(p_group_id UUID, p_permission_code VARCHAR)
RETURNS BOOLEAN AS $$
DECLARE
    v_count INT;
BEGIN
    SELECT COUNT(*) INTO v_count
    FROM group_permissions gp
    JOIN permissions p ON gp.permission_id = p.id
    WHERE gp.group_id = p_group_id AND p.code = p_permission_code;

    RETURN v_count > 0;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- 8. GRANT PERMISSIONS
-- ============================================================================
GRANT SELECT, INSERT, DELETE ON group_permissions TO app_role;
GRANT SELECT ON group_permissions TO app_readonly;
GRANT EXECUTE ON FUNCTION get_group_permissions TO app_role;
GRANT EXECUTE ON FUNCTION get_groups_with_permission TO app_role;
GRANT EXECUTE ON FUNCTION group_has_permission TO app_role;

COMMIT;
