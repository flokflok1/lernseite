-- ============================================================================
-- Migration: 090_role_feature_assignments.sql
-- Description: Create role_feature_assignments table for dynamic feature assignment to roles
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-01-16
-- ============================================================================
-- Previous number: 068 (Root) → Renumbered to 090 to resolve duplicates

-- Purpose:
-- This migration creates the role_feature_assignments table which enables:
-- 1. Dynamic assignment of system features to roles via Admin Panel
-- 2. Custom role creation with feature-specific permissions
-- 3. Role templates (Parent, Enterprise Admin, Auditor, etc.)
-- 4. Fine-grained control over which roles can access which system features
--
-- Relationship: core.roles ← role_feature_assignments → support_systems.system_features

-- Create role_feature_assignments table
CREATE TABLE IF NOT EXISTS core.role_feature_assignments (
    assignment_id SERIAL PRIMARY KEY,
    role_id INTEGER NOT NULL REFERENCES core.roles(role_id) ON DELETE CASCADE,
    feature_id INTEGER NOT NULL REFERENCES support_systems.system_features(feature_id) ON DELETE CASCADE,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES core.users(user_id),
    UNIQUE(role_id, feature_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_role_feature_role
ON core.role_feature_assignments(role_id);

CREATE INDEX IF NOT EXISTS idx_role_feature_feature
ON core.role_feature_assignments(feature_id);

CREATE INDEX IF NOT EXISTS idx_role_feature_enabled
ON core.role_feature_assignments(enabled)
WHERE enabled = TRUE;

-- Add comments
COMMENT ON TABLE core.role_feature_assignments IS
'Maps roles to system features - enables dynamic feature assignment for custom roles';

COMMENT ON COLUMN core.role_feature_assignments.role_id IS
'Reference to role (core.roles)';

COMMENT ON COLUMN core.role_feature_assignments.feature_id IS
'Reference to system feature (support_systems.system_features)';

COMMENT ON COLUMN core.role_feature_assignments.enabled IS
'Whether this feature is enabled for this role';

COMMENT ON COLUMN core.role_feature_assignments.created_by IS
'User who created this assignment (typically Owner-Admin)';

-- Add audit logging trigger
CREATE OR REPLACE FUNCTION core.log_role_feature_change()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        -- Log feature assignment
        INSERT INTO core.audit_logs (
            user_id,
            event_type,
            event_category,
            severity,
            action,
            resource_type,
            resource_id,
            metadata,
            success
        ) VALUES (
            NEW.created_by,
            'role_feature_assigned',
            'authorization',
            'info',
            'ROLE_FEATURE_ASSIGNED',
            'role_feature_assignment',
            NEW.assignment_id::VARCHAR,
            jsonb_build_object(
                'role_id', NEW.role_id,
                'feature_id', NEW.feature_id,
                'enabled', NEW.enabled,
                'created_by', NEW.created_by
            ),
            TRUE
        );
    ELSIF TG_OP = 'UPDATE' THEN
        -- Log feature change
        IF NEW.enabled != OLD.enabled THEN
            INSERT INTO core.audit_logs (
                user_id,
                event_type,
                event_category,
                severity,
                action,
                resource_type,
                resource_id,
                metadata,
                success
            ) VALUES (
                NEW.created_by,
                'role_feature_toggled',
                'authorization',
                'info',
                'ROLE_FEATURE_TOGGLED',
                'role_feature_assignment',
                NEW.assignment_id::VARCHAR,
                jsonb_build_object(
                    'role_id', NEW.role_id,
                    'feature_id', NEW.feature_id,
                    'enabled', NEW.enabled,
                    'previous_enabled', OLD.enabled,
                    'modified_by', NEW.created_by
                ),
                TRUE
            );
        END IF;
    ELSIF TG_OP = 'DELETE' THEN
        -- Log feature removal
        INSERT INTO core.audit_logs (
            user_id,
            event_type,
            event_category,
            severity,
            action,
            resource_type,
            resource_id,
            metadata,
            success
        ) VALUES (
            OLD.created_by,
            'role_feature_removed',
            'authorization',
            'info',
            'ROLE_FEATURE_REMOVED',
            'role_feature_assignment',
            OLD.assignment_id::VARCHAR,
            jsonb_build_object(
                'role_id', OLD.role_id,
                'feature_id', OLD.feature_id,
                'removed_by', OLD.created_by
            ),
            TRUE
        );
    END IF;

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Create trigger
DROP TRIGGER IF EXISTS role_feature_audit_trigger ON core.role_feature_assignments;
CREATE TRIGGER role_feature_audit_trigger
AFTER INSERT OR UPDATE OR DELETE ON core.role_feature_assignments
FOR EACH ROW
EXECUTE FUNCTION core.log_role_feature_change();

-- ============================================================================
-- Seed Default Role-Feature Assignments
-- ============================================================================

-- Admin role gets all features
INSERT INTO core.role_feature_assignments (role_id, feature_id, enabled)
SELECT
    r.role_id,
    f.feature_id,
    TRUE
FROM core.roles r
CROSS JOIN support_systems.system_features f
WHERE r.role_name = 'admin'
ON CONFLICT (role_id, feature_id) DO NOTHING;

-- Premium role gets premium features
INSERT INTO core.role_feature_assignments (role_id, feature_id, enabled)
SELECT
    r.role_id,
    f.feature_id,
    TRUE
FROM core.roles r
CROSS JOIN support_systems.system_features f
WHERE r.role_name = 'premium'
  AND f.category IN ('interactive_tools', 'visualization', 'audio')
ON CONFLICT (role_id, feature_id) DO NOTHING;

-- Teacher role gets educational features
INSERT INTO core.role_feature_assignments (role_id, feature_id, enabled)
SELECT
    r.role_id,
    f.feature_id,
    TRUE
FROM core.roles r
CROSS JOIN support_systems.system_features f
WHERE r.role_name = 'teacher'
  AND f.category IN ('exam_systems', 'interactive_tools', 'collaboration', 'tutor')
ON CONFLICT (role_id, feature_id) DO NOTHING;

-- ============================================================================
-- End Migration
-- ============================================================================
