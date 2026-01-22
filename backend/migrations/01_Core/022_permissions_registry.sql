-- Migration 094: Create permissions registry table
-- Beschreibung: Zentrale Registry für alle verfügbaren Permissions im System
-- Datum: 2026-01-22
-- Status: Phase 1 - Database Schema

BEGIN;

-- ============================================================================
-- 1. CREATE PERMISSIONS TABLE
-- ============================================================================
CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Permission Identity
    code VARCHAR(100) UNIQUE NOT NULL,  -- e.g. 'courses.view', 'users.edit', 'admin.access'
    display_name VARCHAR(255) NOT NULL,  -- Human-readable name
    description TEXT,  -- Detailed description

    -- Classification
    permission_type VARCHAR(50) NOT NULL DEFAULT 'general',  -- system, organisation, group, general
    category VARCHAR(100),  -- e.g. 'courses', 'users', 'content', 'system', 'admin'

    -- Compatibility with RBAC 2.0 (Hierarchy Level based)
    required_hierarchy_level SMALLINT DEFAULT 0,  -- 0-10, for compatibility checking

    -- System Permission Flag
    is_system_permission BOOLEAN DEFAULT FALSE,  -- Cannot be deleted if TRUE

    -- Metadata
    metadata JSONB DEFAULT '{}',  -- Flexible storage for permission-specific config

    -- Audit Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    CONSTRAINT chk_permission_type CHECK (permission_type IN (
        'system',
        'organisation',
        'group',
        'general'
    )),

    CONSTRAINT chk_hierarchy_level CHECK (required_hierarchy_level >= 0 AND required_hierarchy_level <= 10),

    CONSTRAINT chk_protected_system_perms CHECK (
        is_system_permission = FALSE OR is_system_permission = TRUE
    ),

    CONSTRAINT chk_code_format CHECK (code ~ '^[a-z0-9._-]+$')
);

-- ============================================================================
-- 2. CREATE INDICES FOR PERFORMANCE
-- ============================================================================
CREATE UNIQUE INDEX idx_permissions_code
    ON permissions(code);

CREATE INDEX idx_permissions_category
    ON permissions(category);

CREATE INDEX idx_permissions_permission_type
    ON permissions(permission_type);

CREATE INDEX idx_permissions_is_system
    ON permissions(is_system_permission)
    WHERE is_system_permission = TRUE;

CREATE INDEX idx_permissions_required_level
    ON permissions(required_hierarchy_level DESC);

-- ============================================================================
-- 3. SEED SYSTEM PERMISSIONS (RBAC 3.0)
-- ============================================================================
INSERT INTO permissions (code, display_name, description, permission_type, category, required_hierarchy_level, is_system_permission) VALUES
    -- System Admin Permissions
    ('admin.access', 'Admin Panel Access', 'Full access to admin panel', 'system', 'admin', 10, TRUE),
    ('system.manage', 'System Management', 'Manage system settings and configuration', 'system', 'system', 10, TRUE),
    ('users.manage', 'Manage Users', 'Create, edit, delete users', 'system', 'users', 10, TRUE),
    ('roles.manage', 'Manage Roles', 'Manage user roles and permissions', 'system', 'system', 10, TRUE),
    ('groups.manage', 'Manage Groups', 'Create and manage user groups', 'system', 'system', 9, TRUE),
    ('organisations.manage', 'Manage Organisations', 'Create and manage organisations', 'system', 'system', 10, TRUE),

    -- Content Management Permissions
    ('courses.create', 'Create Courses', 'Create new courses', 'general', 'courses', 3, TRUE),
    ('courses.edit', 'Edit Courses', 'Edit existing courses', 'general', 'courses', 3, TRUE),
    ('courses.delete', 'Delete Courses', 'Delete courses', 'general', 'courses', 5, TRUE),
    ('courses.publish', 'Publish Courses', 'Publish courses', 'general', 'courses', 5, TRUE),
    ('courses.view', 'View Courses', 'View all courses', 'general', 'courses', 1, TRUE),

    -- Chapter & Lesson Management
    ('chapters.create', 'Create Chapters', 'Create course chapters', 'general', 'chapters', 3, TRUE),
    ('chapters.edit', 'Edit Chapters', 'Edit chapters', 'general', 'chapters', 3, TRUE),
    ('chapters.delete', 'Delete Chapters', 'Delete chapters', 'general', 'chapters', 5, TRUE),
    ('lessons.create', 'Create Lessons', 'Create lessons', 'general', 'lessons', 2, TRUE),
    ('lessons.edit', 'Edit Lessons', 'Edit lessons', 'general', 'lessons', 2, TRUE),
    ('lessons.delete', 'Delete Lessons', 'Delete lessons', 'general', 'lessons', 5, TRUE),

    -- Learning Methods
    ('learning_methods.create', 'Create Learning Methods', 'Create custom learning methods', 'general', 'learning_methods', 5, TRUE),
    ('learning_methods.edit', 'Edit Learning Methods', 'Edit learning methods', 'general', 'learning_methods', 5, TRUE),
    ('learning_methods.delete', 'Delete Learning Methods', 'Delete learning methods', 'general', 'learning_methods', 5, TRUE),

    -- Moderation & Compliance
    ('content.moderate', 'Moderate Content', 'Moderate user-generated content', 'system', 'moderation', 7, TRUE),
    ('users.ban', 'Ban Users', 'Ban users from the system', 'system', 'moderation', 8, TRUE),
    ('analytics.view', 'View Analytics', 'View system analytics', 'system', 'analytics', 5, TRUE),
    ('audit_log.view', 'View Audit Logs', 'View audit logs', 'system', 'audit', 8, TRUE),

    -- User Permissions
    ('profile.edit', 'Edit Own Profile', 'Edit own profile information', 'general', 'profile', 1, TRUE),
    ('password.change', 'Change Password', 'Change own password', 'general', 'security', 1, TRUE),
    ('subscriptions.view', 'View Subscriptions', 'View subscription information', 'general', 'billing', 1, TRUE),

    -- Social Features
    ('posts.create', 'Create Posts', 'Create social posts', 'general', 'social', 1, TRUE),
    ('posts.edit', 'Edit Posts', 'Edit own posts', 'general', 'social', 1, TRUE),
    ('posts.delete', 'Delete Posts', 'Delete own posts', 'general', 'social', 1, TRUE),
    ('comments.create', 'Create Comments', 'Create comments on posts', 'general', 'social', 1, TRUE),
    ('comments.moderate', 'Moderate Comments', 'Moderate social comments', 'system', 'moderation', 6, TRUE),

    -- AI Features
    ('ai.generate', 'Use AI Generation', 'Use AI content generation', 'general', 'ai', 2, TRUE),
    ('ai.advanced', 'Advanced AI Features', 'Use advanced AI features', 'general', 'ai', 5, TRUE);

-- ============================================================================
-- 4. CREATE TRIGGER FOR updated_at
-- ============================================================================
CREATE TRIGGER trigger_permissions_updated_at
    BEFORE UPDATE ON permissions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 5. CREATE HELPER FUNCTION: Get permission by code
-- ============================================================================
CREATE OR REPLACE FUNCTION get_permission_by_code(p_code VARCHAR)
RETURNS TABLE(id UUID, display_name VARCHAR, permission_type VARCHAR, required_level SMALLINT)
AS $$
    SELECT
        permissions.id,
        permissions.display_name,
        permissions.permission_type,
        permissions.required_hierarchy_level
    FROM permissions
    WHERE permissions.code = p_code;
$$ LANGUAGE SQL STABLE;

-- ============================================================================
-- 6. CREATE HELPER FUNCTION: Get all permissions by category
-- ============================================================================
CREATE OR REPLACE FUNCTION get_permissions_by_category(p_category VARCHAR)
RETURNS TABLE(code VARCHAR, display_name VARCHAR, permission_type VARCHAR)
AS $$
    SELECT
        permissions.code,
        permissions.display_name,
        permissions.permission_type
    FROM permissions
    WHERE permissions.category = p_category
    ORDER BY permissions.code;
$$ LANGUAGE SQL STABLE;

-- ============================================================================
-- 7. GRANT PERMISSIONS
-- ============================================================================
GRANT SELECT ON permissions TO app_role;
GRANT SELECT ON permissions TO app_readonly;
GRANT INSERT, UPDATE ON permissions TO app_role;
GRANT EXECUTE ON FUNCTION get_permission_by_code TO app_role;
GRANT EXECUTE ON FUNCTION get_permissions_by_category TO app_role;

COMMIT;
