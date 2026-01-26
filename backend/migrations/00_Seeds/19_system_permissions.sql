-- ============================================================================
-- Seed Data: System Permissions
-- Description: Central registry of all available permissions for GBA (Group-Based Architecture)
-- Source: 035_permissions_registry.sql
-- Author: LernsystemX Migration System
-- Date: 2026-01-26
-- Phase: 4 (Seed Data)
-- ============================================================================

-- ============================================================================
-- System Permissions - 14 Core Permissions
-- ============================================================================
-- Seeds the core.permissions table with GBA system permissions
-- Defines all available permissions for group-based authorization
--
-- Permission Categories:
--   1. Admin Permissions (8) - System administration and user management
--   2. Content Permissions (3) - Course and content management
--   3. Moderation Permissions (2) - Content moderation and feedback
--   4. Organization Permissions (1) - Organization analytics
--
-- Permission Format:
--   - code: Unique identifier in format domain.resource:action (e.g., 'admin.users:read')
--   - display_name: Human-readable permission name for UI
--   - description: Detailed description of permission scope
--   - permission_type: general (standard), system (protected), organisation, or group
--   - category: Grouping for admin interface (admin, content, moderation, org)
--   - is_system_permission: TRUE = cannot be deleted, FALSE = can be modified

INSERT INTO core.permissions (code, display_name, description, permission_type, category, is_system_permission) VALUES
    -- Admin Permissions (8)
    ('admin.ai-jobs:read', 'Read AI Jobs', 'View AI job details, history, and status', 'general', 'admin', TRUE),
    ('admin.ai-jobs:write', 'Manage AI Jobs', 'Create, update, cancel, or manage AI jobs', 'general', 'admin', TRUE),
    ('admin.analytics:read', 'View Admin Analytics', 'View system-wide analytics and reports', 'general', 'admin', TRUE),
    ('admin.courses:write', 'Manage Courses (Admin)', 'Create, edit, publish, or delete courses as admin', 'general', 'admin', TRUE),
    ('admin.system:read', 'View System Settings', 'View system configuration, settings, and status', 'general', 'admin', TRUE),
    ('admin.system:write', 'Manage System Settings', 'Modify system configuration and settings', 'general', 'admin', TRUE),
    ('admin.users:read', 'View Users', 'View user accounts, roles, and information', 'general', 'admin', TRUE),
    ('admin.users:write', 'Manage Users', 'Create, edit, or modify user accounts and assignments', 'general', 'admin', TRUE),
    ('admin.users:delete', 'Delete Users', 'Delete or deactivate user accounts', 'general', 'admin', TRUE),

    -- Content Permissions (3)
    ('content.courses:read', 'Read Courses', 'View course details, chapters, and lessons', 'general', 'content', TRUE),
    ('content.courses:write', 'Create/Edit Courses', 'Create, edit, or update courses', 'general', 'content', TRUE),
    ('content.courses:delete', 'Delete Courses', 'Delete courses and associated content', 'general', 'content', TRUE),
    ('content.moderation:moderate', 'Moderate Content', 'Review, approve, or reject user-generated content', 'general', 'content', TRUE),

    -- Moderation Permissions (2)
    ('moderation.feedback:read', 'View Moderation Feedback', 'View feedback on moderated content and decisions', 'general', 'moderation', TRUE),
    ('moderation.feedback:write', 'Create Moderation Feedback', 'Add feedback or notes on moderation decisions', 'general', 'moderation', TRUE),

    -- Organization Permissions (1)
    ('org.analytics:read', 'View Organization Analytics', 'View organization-level analytics and statistics', 'general', 'org', TRUE)

ON CONFLICT (code) DO NOTHING;

-- ============================================================================
-- Verification
-- ============================================================================

SELECT COUNT(*) as total_system_permissions FROM core.permissions;
