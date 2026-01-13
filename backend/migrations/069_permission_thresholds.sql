-- ============================================================================
-- Migration 069: Permission Thresholds System (RBAC 2.0)
-- ============================================================================
-- Description: Flexible permission system with configurable hierarchy thresholds
--              Allows admin panel to control access levels dynamically
-- Date: 2026-01-12
-- Author: Claude (RBAC 2.0 Implementation)
-- ============================================================================

-- Create permission thresholds table
CREATE TABLE IF NOT EXISTS core.permission_thresholds (
    threshold_id SERIAL PRIMARY KEY,
    permission_key VARCHAR(100) UNIQUE NOT NULL,
    min_hierarchy_level INT NOT NULL CHECK (min_hierarchy_level >= 1 AND min_hierarchy_level <= 10),
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Add index for fast lookups
CREATE INDEX IF NOT EXISTS idx_permission_thresholds_key_active
ON core.permission_thresholds(permission_key, is_active);

-- Add updated_at trigger
CREATE OR REPLACE FUNCTION update_permission_threshold_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_permission_threshold_updated_at
    BEFORE UPDATE ON core.permission_thresholds
    FOR EACH ROW
    EXECUTE FUNCTION update_permission_threshold_updated_at();

-- Insert default permission thresholds
INSERT INTO core.permission_thresholds (permission_key, min_hierarchy_level, description) VALUES
-- General resource permissions (admin+ = 8)
('view_any_resource', 8, 'View any resource regardless of ownership (admin, superadmin, owner)'),
('edit_any_resource', 8, 'Edit any resource regardless of ownership (admin, superadmin, owner)'),
('delete_any_resource', 8, 'Delete any resource regardless of ownership (admin, superadmin, owner)'),
('archive_any_resource', 8, 'Archive any resource regardless of ownership (admin, superadmin, owner)'),

-- Course-specific permissions
('courses.view_any', 8, 'View any course including private/draft (admin+)'),
('courses.edit_any', 8, 'Edit any course regardless of creator (admin+)'),
('courses.delete_any', 8, 'Delete any course regardless of creator (admin+)'),
('courses.publish_any', 8, 'Publish any course regardless of creator (admin+)'),
('courses.view_drafts', 6, 'View draft courses in listings (moderator+)'),
('courses.view_stats', 8, 'View statistics for any course (admin+)'),

-- Simulation/Exam permissions
('simulations.view_any', 8, 'View any exam simulation regardless of owner (admin+)'),
('simulations.edit_any', 8, 'Edit any exam simulation regardless of owner (admin+)'),
('simulations.delete_any', 8, 'Delete any exam simulation regardless of owner (admin+)'),

-- Organisation permissions
('organisations.view_any', 8, 'View any organisation details (admin+)'),
('organisations.manage_any', 8, 'Manage any organisation (admin+)'),
('organisations.create', 8, 'Create new organisations (admin+)'),

-- Analytics permissions
('analytics.view_all', 8, 'View all analytics data across organisations (admin+)'),
('analytics.view_org', 5, 'View organisation analytics (org_admin+)'),

-- User management permissions
('users.view_all', 6, 'View all users in system (moderator+)'),
('users.edit_any', 8, 'Edit any user regardless of role (admin+)'),
('users.delete_any', 9, 'Delete any user (superadmin+)'),

-- System permissions
('maintenance.access', 8, 'Access system during maintenance mode (admin+)'),
('system.configure', 9, 'Configure system settings (superadmin+)'),

-- Agent/AI permissions
('agents.manage_any', 8, 'Manage AI agents for any user (admin+)'),
('agents.view_all', 8, 'View all AI agent interactions (admin+)')

ON CONFLICT (permission_key) DO NOTHING;

-- Create audit log table for threshold changes
CREATE TABLE IF NOT EXISTS core.permission_threshold_audit (
    audit_id SERIAL PRIMARY KEY,
    threshold_id INT NOT NULL,
    permission_key VARCHAR(100) NOT NULL,
    old_min_level INT,
    new_min_level INT,
    changed_by_user_id UUID,
    changed_at TIMESTAMP DEFAULT NOW(),
    action VARCHAR(50) NOT NULL, -- 'created', 'updated', 'deleted', 'activated', 'deactivated'
    CONSTRAINT fk_changed_by_user FOREIGN KEY (changed_by_user_id) REFERENCES core.users(user_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_threshold_audit_user ON core.permission_threshold_audit(changed_by_user_id);
CREATE INDEX IF NOT EXISTS idx_threshold_audit_date ON core.permission_threshold_audit(changed_at);

-- Create audit trigger
CREATE OR REPLACE FUNCTION audit_permission_threshold_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'UPDATE') THEN
        IF (OLD.min_hierarchy_level != NEW.min_hierarchy_level) THEN
            INSERT INTO core.permission_threshold_audit
            (threshold_id, permission_key, old_min_level, new_min_level, action)
            VALUES (NEW.threshold_id, NEW.permission_key, OLD.min_hierarchy_level, NEW.min_hierarchy_level, 'updated');
        END IF;

        IF (OLD.is_active != NEW.is_active) THEN
            INSERT INTO core.permission_threshold_audit
            (threshold_id, permission_key, old_min_level, new_min_level, action)
            VALUES (NEW.threshold_id, NEW.permission_key, NEW.min_hierarchy_level, NEW.min_hierarchy_level,
                    CASE WHEN NEW.is_active THEN 'activated' ELSE 'deactivated' END);
        END IF;

        RETURN NEW;
    ELSIF (TG_OP = 'INSERT') THEN
        INSERT INTO core.permission_threshold_audit
        (threshold_id, permission_key, old_min_level, new_min_level, action)
        VALUES (NEW.threshold_id, NEW.permission_key, NULL, NEW.min_hierarchy_level, 'created');
        RETURN NEW;
    ELSIF (TG_OP = 'DELETE') THEN
        INSERT INTO core.permission_threshold_audit
        (threshold_id, permission_key, old_min_level, new_min_level, action)
        VALUES (OLD.threshold_id, OLD.permission_key, OLD.min_hierarchy_level, NULL, 'deleted');
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_permission_thresholds
    AFTER INSERT OR UPDATE OR DELETE ON core.permission_thresholds
    FOR EACH ROW
    EXECUTE FUNCTION audit_permission_threshold_changes();

-- Grant permissions
-- Note: Grant to PUBLIC for read access (application uses connection pooling)
GRANT SELECT ON core.permission_thresholds TO PUBLIC;
GRANT INSERT, UPDATE, DELETE ON core.permission_thresholds TO PUBLIC;
GRANT SELECT, INSERT ON core.permission_threshold_audit TO PUBLIC;
GRANT USAGE, SELECT ON SEQUENCE core.permission_thresholds_threshold_id_seq TO PUBLIC;
GRANT USAGE, SELECT ON SEQUENCE core.permission_threshold_audit_audit_id_seq TO PUBLIC;

-- ============================================================================
-- Verification
-- ============================================================================
DO $$
DECLARE
    threshold_count INT;
BEGIN
    SELECT COUNT(*) INTO threshold_count FROM core.permission_thresholds;
    IF threshold_count = 0 THEN
        RAISE EXCEPTION 'Permission thresholds table is empty - migration failed!';
    END IF;

    RAISE NOTICE 'Migration 069 completed successfully!';
    RAISE NOTICE '  - Permission thresholds table created';
    RAISE NOTICE '  - % default thresholds inserted', threshold_count;
    RAISE NOTICE '  - Audit logging enabled';
END $$;
