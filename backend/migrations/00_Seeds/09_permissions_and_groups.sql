-- ============================================================================
-- Seed Data: System Groups & Group Permissions
-- Description: System groups and permission mappings for RBAC
-- Source: 009_modify_users_for_groups.sql, 035_permissions_registry.sql, 036_group_permissions_mapping.sql
-- Author: LernsystemX Migration System
-- Date: 2026-01-26
-- Phase: 4 (Seed Data)
-- ============================================================================

-- ============================================================================
-- System Groups (10 system groups for RBAC)
-- ============================================================================

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
-- Group Permissions Mappings
-- ============================================================================

-- System Admin Group - All permissions
INSERT INTO core.group_permissions (group_id, permission_id, granted_by)
SELECT
    (SELECT id FROM core.groups WHERE slug = 'system-admin'),
    p.id,
    NULL
FROM core.permissions p
WHERE p.is_system_permission = TRUE
ON CONFLICT (group_id, permission_id) DO NOTHING;

-- Content Creators Group - Can create and edit courses
INSERT INTO core.group_permissions (group_id, permission_id, granted_by)
SELECT
    (SELECT id FROM core.groups WHERE slug = 'content-creators' LIMIT 1),
    p.id,
    NULL
FROM core.permissions p
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
INSERT INTO core.group_permissions (group_id, permission_id, granted_by)
SELECT
    (SELECT id FROM core.groups WHERE slug = 'teachers' LIMIT 1),
    p.id,
    NULL
FROM core.permissions p
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
INSERT INTO core.group_permissions (group_id, permission_id, granted_by)
SELECT
    (SELECT id FROM core.groups WHERE slug = 'content-moderators' LIMIT 1),
    p.id,
    NULL
FROM core.permissions p
WHERE p.code IN (
    'content.moderate',
    'users.ban',
    'comments.moderate',
    'analytics.view',
    'audit_log.view'
)
ON CONFLICT (group_id, permission_id) DO NOTHING;

-- Support Team Group - Limited admin access
INSERT INTO core.group_permissions (group_id, permission_id, granted_by)
SELECT
    (SELECT id FROM core.groups WHERE slug = 'support-team' LIMIT 1),
    p.id,
    NULL
FROM core.permissions p
WHERE p.code IN (
    'users.manage',
    'analytics.view',
    'audit_log.view',
    'content.moderate'
)
ON CONFLICT (group_id, permission_id) DO NOTHING;

-- Premium Members Group - Advanced features
INSERT INTO core.group_permissions (group_id, permission_id, granted_by)
SELECT
    (SELECT id FROM core.groups WHERE slug = 'premium-members' LIMIT 1),
    p.id,
    NULL
FROM core.permissions p
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
INSERT INTO core.group_permissions (group_id, permission_id, granted_by)
SELECT
    (SELECT id FROM core.groups WHERE slug = 'system-users' LIMIT 1),
    p.id,
    NULL
FROM core.permissions p
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
-- Verification
-- ============================================================================

SELECT COUNT(*) as total_system_groups FROM core.groups WHERE is_system_group = TRUE;
SELECT COUNT(*) as total_group_permissions FROM core.group_permissions;
