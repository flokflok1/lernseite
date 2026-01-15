-- ============================================================================
-- Migration: 079_role_studio_modes.sql
-- Description: Create role_studio_modes table for dynamic role-based studio mode configuration
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-01-14
-- ============================================================================
-- Purpose: Enable flexible, database-driven role-to-studio-mode-to-permission
--          mappings. Replaces hardcoded role logic with database configuration
--          that Owner-Admin can manage via Admin Panel without code changes.

-- Create role_studio_modes table
CREATE TABLE IF NOT EXISTS core.role_studio_modes (
    role_code VARCHAR(50) PRIMARY KEY,
    display_name VARCHAR(100) NOT NULL,
    studio_mode VARCHAR(50) NOT NULL,
    requires_organization BOOLEAN DEFAULT FALSE,
    permissions JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Constraints
    CONSTRAINT chk_studio_mode_valid CHECK (studio_mode IN ('admin', 'moderator', 'org_admin', 'org_member', 'teacher', 'user', 'guest'))
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_role_studio_modes_active ON core.role_studio_modes(is_active);
CREATE INDEX IF NOT EXISTS idx_role_studio_modes_studio_mode ON core.role_studio_modes(studio_mode);
CREATE INDEX IF NOT EXISTS idx_role_studio_modes_requires_org ON core.role_studio_modes(requires_organization);

-- Add comments
COMMENT ON TABLE core.role_studio_modes IS 'Role-to-studio-mode-to-permission mapping - central configuration for all role behaviors';
COMMENT ON COLUMN core.role_studio_modes.role_code IS 'Unique role identifier (e.g., admin, moderator, teacher, user)';
COMMENT ON COLUMN core.role_studio_modes.display_name IS 'Human-readable role name for UI display';
COMMENT ON COLUMN core.role_studio_modes.studio_mode IS 'Which studio mode this role gets: admin, moderator, org_admin, org_member, teacher, user, guest';
COMMENT ON COLUMN core.role_studio_modes.requires_organization IS 'Whether this role must belong to an organization (school, company)';
COMMENT ON COLUMN core.role_studio_modes.permissions IS 'JSON object storing permission flags: {can_create_course: true, can_publish: true, can_moderate: false, ...}';
COMMENT ON COLUMN core.role_studio_modes.is_active IS 'Whether this role is currently enabled in the system';

-- Seed initial standard roles (THE ONLY HARDCODED ELEMENT - executed in Setup Wizard)
INSERT INTO core.role_studio_modes
    (role_code, display_name, studio_mode, requires_organization, permissions, is_active, description)
VALUES
    -- System Admin - full access
    ('admin', 'System Administrator', 'admin', FALSE,
        '{"can_create_course": true, "can_publish": true, "can_moderate": true, "can_view_analytics": true, "can_export_data": true, "can_manage_users": true, "can_manage_roles": true, "can_manage_organizations": true, "can_configure_ai": true, "can_manage_subscriptions": true}'::jsonb,
        TRUE, 'System-wide administrator with complete control'),

    -- Content Moderator - review and approve content
    ('moderator', 'Content Moderator', 'moderator', FALSE,
        '{"can_create_course": false, "can_publish": false, "can_moderate": true, "can_view_analytics": true, "can_export_data": false, "can_manage_users": false, "can_manage_roles": false, "can_manage_organizations": false, "can_configure_ai": false, "can_manage_subscriptions": false}'::jsonb,
        TRUE, 'Reviews and approves course content'),

    -- Organization Admin - manages organization's courses and members
    ('org_admin', 'Organization Administrator', 'org_admin', TRUE,
        '{"can_create_course": true, "can_publish": false, "can_moderate": false, "can_view_analytics": true, "can_export_data": true, "can_manage_users": true, "can_manage_roles": false, "can_manage_organizations": false, "can_configure_ai": false, "can_manage_subscriptions": false}'::jsonb,
        TRUE, 'Manages organization (school, company) courses and members'),

    -- Organization Member - teacher or instructor
    ('org_member', 'Organization Member', 'org_member', TRUE,
        '{"can_create_course": true, "can_publish": false, "can_moderate": false, "can_view_analytics": true, "can_export_data": false, "can_manage_users": false, "can_manage_roles": false, "can_manage_organizations": false, "can_configure_ai": false, "can_manage_subscriptions": false}'::jsonb,
        TRUE, 'Organization member (teacher, instructor)'),

    -- Teacher - creates and manages courses
    ('teacher', 'Teacher', 'teacher', FALSE,
        '{"can_create_course": true, "can_publish": false, "can_moderate": false, "can_view_analytics": true, "can_export_data": false, "can_manage_users": false, "can_manage_roles": false, "can_manage_organizations": false, "can_configure_ai": false, "can_manage_subscriptions": false}'::jsonb,
        TRUE, 'Creates and manages courses'),

    -- Regular User - uses system, enrolls in courses
    ('user', 'Student/User', 'user', FALSE,
        '{"can_create_course": false, "can_publish": false, "can_moderate": false, "can_view_analytics": false, "can_export_data": false, "can_manage_users": false, "can_manage_roles": false, "can_manage_organizations": false, "can_configure_ai": false, "can_manage_subscriptions": false}'::jsonb,
        TRUE, 'Regular user - enrolls in courses and learns'),

    -- Guest - limited access user
    ('guest', 'Guest User', 'guest', FALSE,
        '{"can_create_course": false, "can_publish": false, "can_moderate": false, "can_view_analytics": false, "can_export_data": false, "can_manage_users": false, "can_manage_roles": false, "can_manage_organizations": false, "can_configure_ai": false, "can_manage_subscriptions": false}'::jsonb,
        TRUE, 'Guest user - limited access')
ON CONFLICT (role_code) DO NOTHING;

-- Create audit/history table for tracking role changes
CREATE TABLE IF NOT EXISTS core.role_studio_modes_history (
    history_id BIGSERIAL PRIMARY KEY,
    role_code VARCHAR(50) NOT NULL REFERENCES core.role_studio_modes(role_code),
    previous_display_name VARCHAR(100),
    new_display_name VARCHAR(100),
    previous_studio_mode VARCHAR(50),
    new_studio_mode VARCHAR(50),
    previous_permissions JSONB,
    new_permissions JSONB,
    changed_by UUID, -- user_id who made the change
    change_reason TEXT,
    changed_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT fk_changed_by FOREIGN KEY (changed_by) REFERENCES core.users(user_id)
);

CREATE INDEX IF NOT EXISTS idx_role_studio_modes_history_role ON core.role_studio_modes_history(role_code);
CREATE INDEX IF NOT EXISTS idx_role_studio_modes_history_changed_at ON core.role_studio_modes_history(changed_at DESC);
CREATE INDEX IF NOT EXISTS idx_role_studio_modes_history_changed_by ON core.role_studio_modes_history(changed_by);

COMMENT ON TABLE core.role_studio_modes_history IS 'Audit trail for all role configuration changes made by Owner-Admin';
COMMENT ON COLUMN core.role_studio_modes_history.change_reason IS 'Owner-Admin reason for the change (for compliance/audit)';
