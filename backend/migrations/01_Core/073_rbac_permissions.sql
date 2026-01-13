-- ============================================================================
-- Migration: 073_rbac_permissions.sql
-- Version: 1.0.0
-- Description: RBAC Permissions System
-- Author: LernsystemX Migration System
-- Date: 2026-01-02
-- ============================================================================

ALTER TABLE core.permissions
    ADD COLUMN IF NOT EXISTS category VARCHAR(50),
    ADD COLUMN IF NOT EXISTS display_name VARCHAR(100),
    ADD COLUMN IF NOT EXISTS is_system BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS sort_order INTEGER DEFAULT 0;

CREATE INDEX IF NOT EXISTS idx_permissions_category ON core.permissions(category);
CREATE INDEX IF NOT EXISTS idx_permissions_system ON core.permissions(is_system);

-- ============================================================================
-- 2. Custom Roles Support
-- ============================================================================

ALTER TABLE core.roles
    ADD COLUMN IF NOT EXISTS is_builtin BOOLEAN DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS is_administrator BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS created_by UUID REFERENCES core.users(user_id),
    ADD COLUMN IF NOT EXISTS color VARCHAR(20) DEFAULT '#6b7280',
    ADD COLUMN IF NOT EXISTS icon VARCHAR(50) DEFAULT '👤';

-- Ensure is_builtin/is_administrator are NOT NULL
ALTER TABLE core.roles
    ALTER COLUMN is_builtin SET NOT NULL,
    ALTER COLUMN is_administrator SET NOT NULL;

-- Markiere bestehende Rollen als System-Rollen (is_builtin=true)
UPDATE core.roles SET is_builtin = TRUE WHERE role_name IN (
    'free', 'premium', 'creator', 'teacher',
    'school_admin', 'company_admin', 'support', 'moderator', 'admin'
);

-- ============================================================================
-- 3. User Permission Overrides (für spezifische User-Berechtigungen)
-- ============================================================================

CREATE TABLE IF NOT EXISTS core.user_permissions (
    user_id UUID REFERENCES core.users(user_id) ON DELETE CASCADE,
    permission_id INTEGER REFERENCES core.permissions(permission_id) ON DELETE CASCADE,
    granted BOOLEAN DEFAULT TRUE,  -- TRUE = gewährt, FALSE = explizit entzogen
    granted_by UUID REFERENCES core.users(user_id),
    granted_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,  -- NULL = permanent
    reason TEXT,
    PRIMARY KEY (user_id, permission_id)
);

CREATE INDEX IF NOT EXISTS idx_user_perms_user ON core.user_permissions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_perms_expires ON core.user_permissions(expires_at) WHERE expires_at IS NOT NULL;

COMMENT ON TABLE core.user_permissions IS 'User-spezifische Permission-Overrides (zusätzlich zu Rollen-Permissions)';

-- ============================================================================
-- 4. System Permissions erstellen
-- ============================================================================

INSERT INTO core.permissions (permission_key, display_name, description, module, category, is_system, sort_order) VALUES
    -- Users Module
    ('users.view', 'Benutzer anzeigen', 'Benutzer-Liste und Details ansehen', 'users', 'Benutzer', TRUE, 10),
    ('users.create', 'Benutzer erstellen', 'Neue Benutzer anlegen', 'users', 'Benutzer', TRUE, 20),
    ('users.edit', 'Benutzer bearbeiten', 'Benutzer-Daten ändern', 'users', 'Benutzer', TRUE, 30),
    ('users.delete', 'Benutzer löschen', 'Benutzer entfernen', 'users', 'Benutzer', TRUE, 40),
    ('users.roles.assign', 'Rollen zuweisen', 'Benutzer-Rollen ändern', 'users', 'Benutzer', TRUE, 50),
    
    -- Roles Module
    ('roles.view', 'Rollen anzeigen', 'Rollen-Liste ansehen', 'roles', 'Rollen', TRUE, 10),
    ('roles.create', 'Rollen erstellen', 'Neue Rollen anlegen', 'roles', 'Rollen', TRUE, 20),
    ('roles.edit', 'Rollen bearbeiten', 'Rollen-Berechtigungen ändern', 'roles', 'Rollen', TRUE, 30),
    ('roles.delete', 'Rollen löschen', 'Custom Rollen entfernen', 'roles', 'Rollen', TRUE, 40),
    ('roles.permissions.assign', 'Permissions zuweisen', 'Permissions zu Rollen zuweisen', 'roles', 'Rollen', TRUE, 50),
    
    -- Courses Module
    ('courses.view', 'Kurse anzeigen', 'Kurse ansehen', 'courses', 'Kurse', TRUE, 10),
    ('courses.create', 'Kurse erstellen', 'Neue Kurse anlegen', 'courses', 'Kurse', TRUE, 20),
    ('courses.edit', 'Kurse bearbeiten', 'Kurs-Inhalte ändern', 'courses', 'Kurse', TRUE, 30),
    ('courses.delete', 'Kurse löschen', 'Kurse entfernen', 'courses', 'Kurse', TRUE, 40),
    ('courses.publish', 'Kurse veröffentlichen', 'Kurse öffentlich machen', 'courses', 'Kurse', TRUE, 50),
    
    -- i18n Module
    ('i18n.view', 'Übersetzungen anzeigen', 'Übersetzungs-System ansehen', 'i18n', 'Übersetzungen', TRUE, 10),
    ('i18n.suggest', 'Vorschläge einreichen', 'Übersetzungs-Vorschläge machen', 'i18n', 'Übersetzungen', TRUE, 20),
    ('i18n.vote', 'Abstimmen', 'Für Vorschläge abstimmen', 'i18n', 'Übersetzungen', TRUE, 25),
    ('i18n.moderate', 'Moderieren', 'Übersetzungen prüfen und genehmigen', 'i18n', 'Übersetzungen', TRUE, 30),
    ('i18n.edit', 'Übersetzungen bearbeiten', 'Übersetzungen direkt ändern', 'i18n', 'Übersetzungen', TRUE, 40),
    ('i18n.config', 'Einstellungen ändern', 'i18n-Konfiguration anpassen', 'i18n', 'Übersetzungen', TRUE, 50),
    
    -- AI Studio Module
    ('ai.view', 'KI-Studio anzeigen', 'KI-Studio ansehen', 'ai', 'KI-Studio', TRUE, 10),
    ('ai.generate', 'Inhalte generieren', 'KI-Inhalte erstellen', 'ai', 'KI-Studio', TRUE, 20),
    ('ai.models.view', 'Modelle anzeigen', 'KI-Modelle ansehen', 'ai', 'KI-Studio', TRUE, 30),
    ('ai.models.edit', 'Modelle konfigurieren', 'KI-Modell-Einstellungen ändern', 'ai', 'KI-Studio', TRUE, 40),
    
    -- Analytics Module
    ('analytics.view', 'Analytics anzeigen', 'Statistiken ansehen', 'analytics', 'Analytics', TRUE, 10),
    ('analytics.export', 'Daten exportieren', 'Analytics-Daten exportieren', 'analytics', 'Analytics', TRUE, 20),
    
    -- Organisation Module
    ('org.view', 'Organisation anzeigen', 'Org-Dashboard ansehen', 'org', 'Organisation', TRUE, 10),
    ('org.members.manage', 'Mitglieder verwalten', 'Org-Mitglieder hinzufügen/entfernen', 'org', 'Organisation', TRUE, 20),
    ('org.settings', 'Einstellungen ändern', 'Org-Einstellungen anpassen', 'org', 'Organisation', TRUE, 30),
    ('org.billing', 'Abrechnung verwalten', 'Org-Billing und Tokens', 'org', 'Organisation', TRUE, 40),
    
    -- System Module
    ('system.settings', 'System-Einstellungen', 'Globale Einstellungen ändern', 'system', 'System', TRUE, 10),
    ('system.audit', 'Audit-Logs', 'Audit-Logs ansehen', 'system', 'System', TRUE, 20),
    ('system.cache', 'Cache verwalten', 'Cache invalidieren', 'system', 'System', TRUE, 30),
    ('system.maintenance', 'Wartungsmodus', 'System-Wartung durchführen', 'system', 'System', TRUE, 40)
    
ON CONFLICT (permission_key) DO UPDATE SET
    display_name = EXCLUDED.display_name,
    description = EXCLUDED.description,
    module = EXCLUDED.module,
    category = EXCLUDED.category,
    is_system = EXCLUDED.is_system,
    sort_order = EXCLUDED.sort_order;

-- ============================================================================
-- 5. Standard Role-Permission Zuweisungen
-- ============================================================================

-- Helper function zum Zuweisen von Permissions
CREATE OR REPLACE FUNCTION assign_permission_to_role(p_role_name VARCHAR, p_permission_key VARCHAR)
RETURNS VOID AS $$
DECLARE
    v_role_id INTEGER;
    v_permission_id INTEGER;
BEGIN
    SELECT role_id INTO v_role_id FROM core.roles WHERE role_name = p_role_name;
    SELECT permission_id INTO v_permission_id FROM core.permissions WHERE permission_key = p_permission_key;
    
    IF v_role_id IS NOT NULL AND v_permission_id IS NOT NULL THEN
        INSERT INTO core.role_permissions (role_id, permission_id)
        VALUES (v_role_id, v_permission_id)
        ON CONFLICT DO NOTHING;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Free User Permissions
SELECT assign_permission_to_role('free', 'courses.view');
SELECT assign_permission_to_role('free', 'i18n.view');
SELECT assign_permission_to_role('free', 'i18n.suggest');
SELECT assign_permission_to_role('free', 'i18n.vote');

-- Premium User Permissions (+ Free)
SELECT assign_permission_to_role('premium', 'courses.view');
SELECT assign_permission_to_role('premium', 'i18n.view');
SELECT assign_permission_to_role('premium', 'i18n.suggest');
SELECT assign_permission_to_role('premium', 'i18n.vote');
SELECT assign_permission_to_role('premium', 'analytics.view');

-- Creator Permissions (+ Premium)
SELECT assign_permission_to_role('creator', 'courses.view');
SELECT assign_permission_to_role('creator', 'courses.create');
SELECT assign_permission_to_role('creator', 'courses.edit');
SELECT assign_permission_to_role('creator', 'courses.publish');
SELECT assign_permission_to_role('creator', 'i18n.view');
SELECT assign_permission_to_role('creator', 'i18n.suggest');
SELECT assign_permission_to_role('creator', 'i18n.vote');
SELECT assign_permission_to_role('creator', 'analytics.view');
SELECT assign_permission_to_role('creator', 'ai.view');
SELECT assign_permission_to_role('creator', 'ai.generate');

-- Teacher Permissions (+ Creator)
SELECT assign_permission_to_role('teacher', 'courses.view');
SELECT assign_permission_to_role('teacher', 'courses.create');
SELECT assign_permission_to_role('teacher', 'courses.edit');
SELECT assign_permission_to_role('teacher', 'courses.publish');
SELECT assign_permission_to_role('teacher', 'i18n.view');
SELECT assign_permission_to_role('teacher', 'i18n.suggest');
SELECT assign_permission_to_role('teacher', 'i18n.vote');
SELECT assign_permission_to_role('teacher', 'analytics.view');
SELECT assign_permission_to_role('teacher', 'ai.view');
SELECT assign_permission_to_role('teacher', 'ai.generate');
SELECT assign_permission_to_role('teacher', 'org.view');
SELECT assign_permission_to_role('teacher', 'org.members.manage');

-- Moderator Permissions
SELECT assign_permission_to_role('moderator', 'courses.view');
SELECT assign_permission_to_role('moderator', 'i18n.view');
SELECT assign_permission_to_role('moderator', 'i18n.suggest');
SELECT assign_permission_to_role('moderator', 'i18n.vote');
SELECT assign_permission_to_role('moderator', 'i18n.moderate');
SELECT assign_permission_to_role('moderator', 'i18n.edit');
SELECT assign_permission_to_role('moderator', 'analytics.view');

-- Admin Permissions (ALL)
DO $$
DECLARE
    v_admin_role_id INTEGER;
BEGIN
    SELECT role_id INTO v_admin_role_id FROM core.roles WHERE role_name = 'admin';
    
    INSERT INTO core.role_permissions (role_id, permission_id)
    SELECT v_admin_role_id, permission_id FROM core.permissions
    ON CONFLICT DO NOTHING;
END $$;

-- ============================================================================
-- 6. Function: Check User Permission
-- ============================================================================

CREATE OR REPLACE FUNCTION user_has_permission(p_user_id UUID, p_permission_key VARCHAR)
RETURNS BOOLEAN AS $$
DECLARE
    v_has_permission BOOLEAN := FALSE;
    v_role_id INTEGER;
    v_role_name VARCHAR;
BEGIN
    -- 1. Check user-specific override (explicit grant/deny)
    SELECT granted INTO v_has_permission
    FROM core.user_permissions up
    JOIN core.permissions p ON up.permission_id = p.permission_id
    WHERE up.user_id = p_user_id 
      AND p.permission_key = p_permission_key
      AND (up.expires_at IS NULL OR up.expires_at > NOW());
    
    IF FOUND THEN
        RETURN v_has_permission;
    END IF;
    
    -- 2. Check role-based permissions
    SELECT u.role_id, r.role_name INTO v_role_id, v_role_name
    FROM core.users u
    JOIN core.roles r ON u.role_id = r.role_id
    WHERE u.user_id = p_user_id;
    
    -- Admin has all permissions
    IF v_role_name = 'admin' THEN
        RETURN TRUE;
    END IF;
    
    -- 3. Check role permissions
    SELECT TRUE INTO v_has_permission
    FROM core.role_permissions rp
    JOIN core.permissions p ON rp.permission_id = p.permission_id
    WHERE rp.role_id = v_role_id AND p.permission_key = p_permission_key;
    
    RETURN COALESCE(v_has_permission, FALSE);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION user_has_permission IS 'Prüft ob ein User eine bestimmte Permission hat (via Rolle oder Override)';

-- ============================================================================
-- 7. Function: Get User Permissions
-- ============================================================================

CREATE OR REPLACE FUNCTION get_user_permissions(p_user_id UUID)
RETURNS TABLE (
    permission_key VARCHAR,
    display_name VARCHAR,
    module VARCHAR,
    source VARCHAR  -- 'role' or 'user_override'
) AS $$
DECLARE
    v_role_id INTEGER;
    v_role_name VARCHAR;
BEGIN
    -- Get user role
    SELECT u.role_id, r.role_name INTO v_role_id, v_role_name
    FROM core.users u
    JOIN core.roles r ON u.role_id = r.role_id
    WHERE u.user_id = p_user_id;
    
    -- Admin gets all permissions
    IF v_role_name = 'admin' THEN
        RETURN QUERY
        SELECT p.permission_key, p.display_name, p.module, 'role'::VARCHAR as source
        FROM core.permissions p
        ORDER BY p.module, p.sort_order;
        RETURN;
    END IF;
    
    -- Return combined role + user permissions
    RETURN QUERY
    SELECT DISTINCT p.permission_key, p.display_name, p.module,
           CASE WHEN up.user_id IS NOT NULL THEN 'user_override' ELSE 'role' END::VARCHAR as source
    FROM core.permissions p
    LEFT JOIN core.role_permissions rp ON p.permission_id = rp.permission_id AND rp.role_id = v_role_id
    LEFT JOIN core.user_permissions up ON p.permission_id = up.permission_id 
        AND up.user_id = p_user_id 
        AND up.granted = TRUE
        AND (up.expires_at IS NULL OR up.expires_at > NOW())
    WHERE rp.role_id IS NOT NULL OR up.user_id IS NOT NULL
    ORDER BY p.module, p.sort_order;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_user_permissions IS 'Gibt alle Permissions eines Users zurück (Rolle + Overrides)';

-- ============================================================================
-- 8. View: Role Permissions Overview
-- ============================================================================

CREATE OR REPLACE VIEW v_role_permissions AS
SELECT
    r.role_id,
    r.role_name,
    r.display_name as role_display_name,
    r.hierarchy_level,
    r.is_builtin,
    r.is_administrator,
    r.color,
    r.icon,
    p.permission_id,
    p.permission_key,
    p.display_name as permission_display_name,
    p.module,
    p.category
FROM core.roles r
LEFT JOIN core.role_permissions rp ON r.role_id = rp.role_id
LEFT JOIN core.permissions p ON rp.permission_id = p.permission_id
ORDER BY r.hierarchy_level, p.module, p.sort_order;

COMMENT ON VIEW v_role_permissions IS 'Übersicht aller Rollen mit ihren Permissions - Vereinfachte Struktur (is_builtin/is_administrator)';

-- Cleanup helper function
DROP FUNCTION IF EXISTS assign_permission_to_role(VARCHAR, VARCHAR);

-- ============================================================================
-- 9. RBAC 2.0: Owner Role Addition
-- ============================================================================

-- Add owner role (if not exists)
INSERT INTO core.roles (role_name, display_name, description, hierarchy_level, is_system, color, icon)
VALUES ('owner', 'Owner', 'System Owner (höchste Berechtigung)', 10, TRUE, '#ff0000', '👑')
ON CONFLICT (role_name) DO UPDATE SET
    hierarchy_level = 10,
    is_system = TRUE,
    description = 'System Owner (höchste Berechtigung)'
WHERE core.roles.role_name = 'owner';

-- Assign ALL permissions to owner role
DO $$
DECLARE
    v_owner_role_id INTEGER;
BEGIN
    SELECT role_id INTO v_owner_role_id FROM core.roles WHERE role_name = 'owner';

    INSERT INTO core.role_permissions (role_id, permission_id)
    SELECT v_owner_role_id, permission_id FROM core.permissions
    ON CONFLICT DO NOTHING;
END $$;

-- ============================================================================
-- 10. Update Permission Function: Support Owner Role
-- ============================================================================

CREATE OR REPLACE FUNCTION user_has_permission(p_user_id UUID, p_permission_key VARCHAR)
RETURNS BOOLEAN AS $$
DECLARE
    v_has_permission BOOLEAN := FALSE;
    v_role_id INTEGER;
    v_role_name VARCHAR;
BEGIN
    -- 1. Check user-specific override (explicit grant/deny)
    SELECT granted INTO v_has_permission
    FROM core.user_permissions up
    JOIN core.permissions p ON up.permission_id = p.permission_id
    WHERE up.user_id = p_user_id
      AND p.permission_key = p_permission_key
      AND (up.expires_at IS NULL OR up.expires_at > NOW());

    IF FOUND THEN
        RETURN v_has_permission;
    END IF;

    -- 2. Check role-based permissions
    SELECT u.role_id, r.role_name INTO v_role_id, v_role_name
    FROM core.users u
    JOIN core.roles r ON u.role_id = r.role_id
    WHERE u.user_id = p_user_id;

    -- Owner and Admin have all permissions
    IF v_role_name IN ('admin', 'owner') THEN
        RETURN TRUE;
    END IF;

    -- 3. Check role permissions
    SELECT TRUE INTO v_has_permission
    FROM core.role_permissions rp
    JOIN core.permissions p ON rp.permission_id = p.permission_id
    WHERE rp.role_id = v_role_id AND p.permission_key = p_permission_key;

    RETURN COALESCE(v_has_permission, FALSE);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION user_has_permission IS 'Prüft ob ein User eine bestimmte Permission hat (via Rolle oder Override). Owner und Admin erhalten alle Permissions.';

-- ============================================================================
-- 11. Update Get Permissions Function: Support Owner Role
-- ============================================================================

CREATE OR REPLACE FUNCTION get_user_permissions(p_user_id UUID)
RETURNS TABLE (
    permission_key VARCHAR,
    display_name VARCHAR,
    module VARCHAR,
    source VARCHAR  -- 'role' or 'user_override'
) AS $$
DECLARE
    v_role_id INTEGER;
    v_role_name VARCHAR;
BEGIN
    -- Get user role
    SELECT u.role_id, r.role_name INTO v_role_id, v_role_name
    FROM core.users u
    JOIN core.roles r ON u.role_id = r.role_id
    WHERE u.user_id = p_user_id;

    -- Admin and Owner get all permissions
    IF v_role_name IN ('admin', 'owner') THEN
        RETURN QUERY
        SELECT p.permission_key, p.display_name, p.module, 'role'::VARCHAR as source
        FROM core.permissions p
        ORDER BY p.module, p.sort_order;
        RETURN;
    END IF;

    -- Return combined role + user permissions
    RETURN QUERY
    SELECT DISTINCT p.permission_key, p.display_name, p.module,
           CASE WHEN up.user_id IS NOT NULL THEN 'user_override' ELSE 'role' END::VARCHAR as source
    FROM core.permissions p
    LEFT JOIN core.role_permissions rp ON p.permission_id = rp.permission_id AND rp.role_id = v_role_id
    LEFT JOIN core.user_permissions up ON p.permission_id = up.permission_id
        AND up.user_id = p_user_id
        AND up.granted = TRUE
        AND (up.expires_at IS NULL OR up.expires_at > NOW())
    WHERE rp.role_id IS NOT NULL OR up.user_id IS NOT NULL
    ORDER BY p.module, p.sort_order;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_user_permissions IS 'Gibt alle Permissions eines Users zurück (Rolle + Overrides). Owner und Admin bekommen alle Permissions.';

-- Update hierarchy constraint to allow level 10 (for owner)
ALTER TABLE core.roles
DROP CONSTRAINT IF EXISTS chk_role_hierarchy;

ALTER TABLE core.roles
ADD CONSTRAINT chk_role_hierarchy CHECK (hierarchy_level BETWEEN 1 AND 10);

-- ============================================================================
-- 12. Create indexes on new role columns for performance
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_roles_builtin ON core.roles(is_builtin);
CREATE INDEX IF NOT EXISTS idx_roles_administrator ON core.roles(is_administrator);

-- ============================================================================
-- Migration 073 - RBAC 2.0: Complete Role & Permission System
-- ============================================================================
