-- =====================================================
-- Migration 077: Flexible RBAC System
-- =====================================================
-- Datum: 2026-01-09
-- Zweck: Erweitert bestehendes RBAC-System für organisationsspezifische Rollen
--
-- WICHTIG: Erweitert core.roles, core.permissions, core.role_permissions
-- aus migrations/01_Core/001_core_users_roles.sql
--
-- NEU:
-- - Organisationen können eigene Rollen erstellen
-- - Journey-basierte Permissions (learning, teaching, management)
-- - Rollenvererbung von System-Rollen
-- - Flexible Permission-Kombinationen pro Organisation
-- =====================================================

-- =====================================================
-- 1. Journey-Based Permissions
-- =====================================================

-- Neue Permissions für Journey-Based Architecture
INSERT INTO core.permissions (permission_key, description, module) VALUES
    -- Learning Journey
    ('learning.discovery.browse', 'Browse public courses', 'learning'),
    ('learning.discovery.search', 'Search courses', 'learning'),
    ('learning.enrollment.enroll', 'Enroll in courses', 'learning'),
    ('learning.experience.learn', 'Access learning content', 'learning'),
    ('learning.experience.practice', 'Use practice features', 'learning'),
    ('learning.experience.ai', 'Use AI-powered features', 'learning'),
    ('learning.progress.view', 'View own progress', 'learning'),
    ('learning.profile.manage', 'Manage own profile', 'learning'),

    -- Teaching Journey
    ('teaching.authoring.create', 'Create courses', 'teaching'),
    ('teaching.authoring.edit', 'Edit own courses', 'teaching'),
    ('teaching.authoring.ai', 'Use AI authoring tools', 'teaching'),
    ('teaching.classroom.manage', 'Manage classes', 'teaching'),
    ('teaching.classroom.liveroom', 'Host LiveRooms', 'teaching'),
    ('teaching.publishing.community', 'Publish to community', 'teaching'),
    ('teaching.publishing.marketplace', 'Publish to marketplace', 'teaching'),
    ('teaching.analytics.view', 'View teaching analytics', 'teaching'),

    -- Management Journey
    ('management.organisations.view', 'View organisation', 'management'),
    ('management.organisations.manage', 'Manage organisation', 'management'),
    ('management.users.view', 'View users', 'management'),
    ('management.users.manage', 'Manage users', 'management'),
    ('management.content.view', 'View all content', 'management'),
    ('management.content.manage', 'Manage all content', 'management'),
    ('management.system.configure', 'Configure system', 'management'),
    ('management.analytics.view', 'View all analytics', 'management')
ON CONFLICT (permission_key) DO NOTHING;

-- =====================================================
-- 2. Organisation-Spezifische Rollen
-- =====================================================

CREATE TABLE IF NOT EXISTS core.organisation_roles (
    organisation_role_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organisation_id UUID NOT NULL REFERENCES organisations.organisations(organisation_id) ON DELETE CASCADE,

    -- Rollendetails
    role_code VARCHAR(50) NOT NULL,
    role_name VARCHAR(100) NOT NULL,
    role_description TEXT,

    -- Basis-Rolle (optional)
    base_role_id INTEGER REFERENCES core.roles(role_id),

    -- Journey-Access (JSONB)
    journey_access JSONB DEFAULT '{}',
    -- Beispiel: {"learning": "write", "teaching": "read", "management": "none"}
    -- Werte: none, read, write, admin

    -- Custom Permissions (zusätzlich zu Journey-Access)
    custom_permissions TEXT[] DEFAULT '{}',

    -- Status
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE (organisation_id, role_code)
);

CREATE INDEX idx_org_roles_organisation ON core.organisation_roles(organisation_id);
CREATE INDEX idx_org_roles_base_role ON core.organisation_roles(base_role_id);

COMMENT ON TABLE core.organisation_roles IS
'Custom roles per organisation (extends system roles)';

COMMENT ON COLUMN core.organisation_roles.journey_access IS
'Journey-basierte Permissions: {"learning": "write", "teaching": "admin", "management": "none"}';

COMMENT ON COLUMN core.organisation_roles.custom_permissions IS
'Array of custom permission_keys (e.g. ["learning.discovery.browse", "teaching.authoring.create"])';

-- =====================================================
-- 3. User-Organisation-Role Mapping
-- =====================================================

-- Erweitere organisations.organisation_members (wenn existiert) oder erstelle neue Tabelle
DO $$
BEGIN
    -- Prüfe ob organisation_members existiert
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'organisations'
        AND table_name = 'organisation_members'
    ) THEN
        -- Füge Spalte hinzu
        ALTER TABLE organisations.organisation_members
        ADD COLUMN IF NOT EXISTS organisation_role_id UUID REFERENCES core.organisation_roles(organisation_role_id);

        CREATE INDEX IF NOT EXISTS idx_org_members_role ON organisations.organisation_members(organisation_role_id);
    ELSE
        -- Erstelle neue Tabelle (falls noch nicht vorhanden)
        CREATE TABLE IF NOT EXISTS organisations.organisation_members (
            member_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            organisation_id UUID NOT NULL REFERENCES organisations.organisations(organisation_id) ON DELETE CASCADE,
            user_id UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,

            -- Rolle
            system_role_id INTEGER REFERENCES core.roles(role_id),
            organisation_role_id UUID REFERENCES core.organisation_roles(organisation_role_id),

            -- Status
            status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended')),
            joined_at TIMESTAMPTZ DEFAULT NOW(),
            left_at TIMESTAMPTZ,

            UNIQUE (organisation_id, user_id)
        );

        CREATE INDEX idx_org_members_organisation ON organisations.organisation_members(organisation_id);
        CREATE INDEX idx_org_members_user ON organisations.organisation_members(user_id);
        CREATE INDEX idx_org_members_system_role ON organisations.organisation_members(system_role_id);
        CREATE INDEX idx_org_members_org_role ON organisations.organisation_members(organisation_role_id);

        COMMENT ON TABLE organisations.organisation_members IS
        'Members of organisations with flexible role assignment';
    END IF;
END $$;

-- =====================================================
-- 4. Journey-Access Helper Functions
-- =====================================================

-- Funktion: Hole effektive Journey-Access für User in Organisation
CREATE OR REPLACE FUNCTION get_user_journey_access(
    p_user_id UUID,
    p_organisation_id UUID
) RETURNS JSONB AS $$
DECLARE
    v_journey_access JSONB;
    v_system_role_id INTEGER;
    v_org_role_id UUID;
BEGIN
    -- Hole Rollen des Users in dieser Organisation
    SELECT system_role_id, organisation_role_id
    INTO v_system_role_id, v_org_role_id
    FROM organisations.organisation_members
    WHERE user_id = p_user_id
    AND organisation_id = p_organisation_id
    AND status = 'active';

    -- Wenn Organisation-Role existiert, nutze diese
    IF v_org_role_id IS NOT NULL THEN
        SELECT journey_access INTO v_journey_access
        FROM core.organisation_roles
        WHERE organisation_role_id = v_org_role_id
        AND active = TRUE;

        RETURN COALESCE(v_journey_access, '{}'::jsonb);
    END IF;

    -- Fallback: Hole Journey-Access von System-Rolle
    -- (Später erweitern mit mapping von system roles zu journey access)
    RETURN '{}'::jsonb;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_user_journey_access IS
'Returns journey access for user in organisation (learning/teaching/management)';

-- Funktion: Prüfe ob User Journey-Access hat
CREATE OR REPLACE FUNCTION has_journey_access(
    p_user_id UUID,
    p_organisation_id UUID,
    p_journey VARCHAR(50),
    p_required_level VARCHAR(10)  -- none, read, write, admin
) RETURNS BOOLEAN AS $$
DECLARE
    v_journey_access JSONB;
    v_user_level VARCHAR(10);
BEGIN
    -- Hole Journey-Access
    v_journey_access := get_user_journey_access(p_user_id, p_organisation_id);

    -- Hole Level für Journey
    v_user_level := v_journey_access->>p_journey;

    -- Prüfe Level-Hierarchie
    -- none < read < write < admin
    IF v_user_level IS NULL OR v_user_level = 'none' THEN
        RETURN FALSE;
    END IF;

    IF p_required_level = 'read' THEN
        RETURN v_user_level IN ('read', 'write', 'admin');
    ELSIF p_required_level = 'write' THEN
        RETURN v_user_level IN ('write', 'admin');
    ELSIF p_required_level = 'admin' THEN
        RETURN v_user_level = 'admin';
    END IF;

    RETURN FALSE;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION has_journey_access IS
'Checks if user has required journey access level in organisation';

-- =====================================================
-- 5. Standard Organisation-Rollen Templates
-- =====================================================

-- Funktion: Erstelle Standard-Rollen für neue Organisation
CREATE OR REPLACE FUNCTION create_standard_organisation_roles(
    p_organisation_id UUID,
    p_org_type VARCHAR(50)
) RETURNS VOID AS $$
BEGIN
    -- School-Rollen
    IF p_org_type = 'school' THEN
        INSERT INTO core.organisation_roles (organisation_id, role_code, role_name, role_description, base_role_id, journey_access) VALUES
            (p_organisation_id, 'student', 'Schüler', 'Schüler mit Lernzugriff', 1, '{"learning": "write", "teaching": "none", "management": "none"}'::jsonb),
            (p_organisation_id, 'teacher', 'Lehrer', 'Lehrer mit Klassen-Verwaltung', 4, '{"learning": "write", "teaching": "write", "management": "read"}'::jsonb),
            (p_organisation_id, 'school_admin', 'Schulleiter', 'Schulleiter mit voller Kontrolle', 5, '{"learning": "admin", "teaching": "admin", "management": "admin"}'::jsonb)
        ON CONFLICT (organisation_id, role_code) DO NOTHING;

    -- Company-Rollen
    ELSIF p_org_type = 'company' THEN
        INSERT INTO core.organisation_roles (organisation_id, role_code, role_name, role_description, base_role_id, journey_access) VALUES
            (p_organisation_id, 'employee', 'Mitarbeiter', 'Mitarbeiter mit Lernzugriff', 1, '{"learning": "write", "teaching": "none", "management": "none"}'::jsonb),
            (p_organisation_id, 'trainer', 'Ausbilder', 'Ausbilder mit Kurs-Verwaltung', 4, '{"learning": "write", "teaching": "write", "management": "read"}'::jsonb),
            (p_organisation_id, 'company_admin', 'Administrator', 'Administrator mit voller Kontrolle', 6, '{"learning": "admin", "teaching": "admin", "management": "admin"}'::jsonb)
        ON CONFLICT (organisation_id, role_code) DO NOTHING;

    -- Teacher Team-Rollen
    ELSIF p_org_type = 'teacher_team' THEN
        INSERT INTO core.organisation_roles (organisation_id, role_code, role_name, role_description, base_role_id, journey_access) VALUES
            (p_organisation_id, 'team_member', 'Team-Mitglied', 'Team-Mitglied mit Lernzugriff', 4, '{"learning": "write", "teaching": "read", "management": "none"}'::jsonb),
            (p_organisation_id, 'team_lead', 'Team-Lead', 'Team-Lead mit Verwaltungsrechten', 4, '{"learning": "write", "teaching": "write", "management": "write"}'::jsonb)
        ON CONFLICT (organisation_id, role_code) DO NOTHING;

    -- Creator Team-Rollen
    ELSIF p_org_type = 'creator_team' THEN
        INSERT INTO core.organisation_roles (organisation_id, role_code, role_name, role_description, base_role_id, journey_access) VALUES
            (p_organisation_id, 'creator', 'Creator', 'Creator mit Kurs-Erstellung', 3, '{"learning": "write", "teaching": "write", "management": "read"}'::jsonb),
            (p_organisation_id, 'creator_lead', 'Lead Creator', 'Lead Creator mit Team-Verwaltung', 3, '{"learning": "write", "teaching": "admin", "management": "write"}'::jsonb)
        ON CONFLICT (organisation_id, role_code) DO NOTHING;
    END IF;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION create_standard_organisation_roles IS
'Creates standard organisation-specific roles based on org_type';

-- =====================================================
-- 6. Trigger: Erstelle Standard-Rollen bei Org-Erstellung
-- =====================================================

CREATE OR REPLACE FUNCTION trigger_create_org_roles()
RETURNS TRIGGER AS $$
BEGIN
    -- Erstelle Standard-Rollen für neue Organisation
    PERFORM create_standard_organisation_roles(NEW.organisation_id, NEW.org_type);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_org_create_roles ON organisations.organisations;

CREATE TRIGGER trigger_org_create_roles
AFTER INSERT ON organisations.organisations
FOR EACH ROW
EXECUTE FUNCTION trigger_create_org_roles();

-- =====================================================
-- 7. Permission Resolution View
-- =====================================================

-- View: Effektive Permissions eines Users
CREATE OR REPLACE VIEW core.user_effective_permissions AS
SELECT
    u.user_id,
    om.organisation_id,
    o.org_type,
    COALESCE(org_r.role_code, sr.role_name) AS effective_role_code,
    COALESCE(org_r.role_name, sr.display_name) AS effective_role_name,
    COALESCE(org_r.journey_access, '{}'::jsonb) AS journey_access,
    sr.hierarchy_level AS system_hierarchy_level,
    om.status AS member_status
FROM core.users u
LEFT JOIN organisations.organisation_members om ON u.user_id = om.user_id
LEFT JOIN organisations.organisations o ON om.organisation_id = o.organisation_id
LEFT JOIN core.organisation_roles org_r ON om.organisation_role_id = org_r.organisation_role_id
LEFT JOIN core.roles sr ON COALESCE(om.system_role_id, u.role_id) = sr.role_id
WHERE om.status = 'active' OR om.status IS NULL;

COMMENT ON VIEW core.user_effective_permissions IS
'Shows effective permissions for all users across organisations';

-- =====================================================
-- 8. Validierungs-Constraints
-- =====================================================

-- Journey-Access muss gültige Struktur haben
ALTER TABLE core.organisation_roles
ADD CONSTRAINT chk_journey_access_structure CHECK (
    journey_access ?& ARRAY['learning', 'teaching', 'management']
);

-- Journey-Access Levels müssen gültig sein
CREATE OR REPLACE FUNCTION validate_journey_access_levels()
RETURNS TRIGGER AS $$
DECLARE
    v_key TEXT;
    v_value TEXT;
BEGIN
    -- Prüfe alle Keys in journey_access
    FOR v_key, v_value IN SELECT * FROM jsonb_each_text(NEW.journey_access)
    LOOP
        IF v_value NOT IN ('none', 'read', 'write', 'admin') THEN
            RAISE EXCEPTION 'Invalid journey access level: % (must be none/read/write/admin)', v_value;
        END IF;
    END LOOP;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_validate_journey_access ON core.organisation_roles;

CREATE TRIGGER trigger_validate_journey_access
BEFORE INSERT OR UPDATE ON core.organisation_roles
FOR EACH ROW
EXECUTE FUNCTION validate_journey_access_levels();

-- =====================================================
-- 9. Update bestehende Organisationen
-- =====================================================

-- Erstelle Standard-Rollen für bestehende Organisationen
DO $$
DECLARE
    v_org RECORD;
BEGIN
    FOR v_org IN SELECT organisation_id, org_type FROM organisations.organisations
    LOOP
        PERFORM create_standard_organisation_roles(v_org.organisation_id, v_org.org_type);
    END LOOP;

    RAISE NOTICE '✅ Standard-Rollen für % Organisationen erstellt', (SELECT COUNT(*) FROM organisations.organisations);
END $$;

-- =====================================================
-- 10. System-Role zu Journey-Access Mapping (Fallback)
-- =====================================================

-- Mapping-Tabelle für System-Rollen zu Journey-Access
CREATE TABLE IF NOT EXISTS core.system_role_journey_mapping (
    role_id INTEGER PRIMARY KEY REFERENCES core.roles(role_id) ON DELETE CASCADE,
    journey_access JSONB NOT NULL DEFAULT '{}'::jsonb
);

-- Standard-Mappings
INSERT INTO core.system_role_journey_mapping (role_id, journey_access) VALUES
    (1, '{"learning": "write", "teaching": "none", "management": "none"}'::jsonb),  -- free
    (2, '{"learning": "write", "teaching": "none", "management": "none"}'::jsonb),  -- premium
    (3, '{"learning": "write", "teaching": "write", "management": "read"}'::jsonb), -- creator
    (4, '{"learning": "write", "teaching": "write", "management": "read"}'::jsonb), -- teacher
    (5, '{"learning": "admin", "teaching": "admin", "management": "admin"}'::jsonb), -- school_admin
    (6, '{"learning": "admin", "teaching": "admin", "management": "admin"}'::jsonb), -- company_admin
    (7, '{"learning": "admin", "teaching": "read", "management": "read"}'::jsonb),  -- support
    (8, '{"learning": "admin", "teaching": "read", "management": "read"}'::jsonb),  -- moderator
    (9, '{"learning": "admin", "teaching": "admin", "management": "admin"}'::jsonb) -- admin
ON CONFLICT (role_id) DO NOTHING;

-- Update get_user_journey_access Funktion mit Fallback
CREATE OR REPLACE FUNCTION get_user_journey_access(
    p_user_id UUID,
    p_organisation_id UUID
) RETURNS JSONB AS $$
DECLARE
    v_journey_access JSONB;
    v_system_role_id INTEGER;
    v_org_role_id UUID;
BEGIN
    -- Hole Rollen des Users in dieser Organisation
    SELECT system_role_id, organisation_role_id
    INTO v_system_role_id, v_org_role_id
    FROM organisations.organisation_members
    WHERE user_id = p_user_id
    AND organisation_id = p_organisation_id
    AND status = 'active';

    -- Wenn Organisation-Role existiert, nutze diese
    IF v_org_role_id IS NOT NULL THEN
        SELECT journey_access INTO v_journey_access
        FROM core.organisation_roles
        WHERE organisation_role_id = v_org_role_id
        AND active = TRUE;

        RETURN COALESCE(v_journey_access, '{}'::jsonb);
    END IF;

    -- Fallback: Hole Journey-Access von System-Rolle
    IF v_system_role_id IS NOT NULL THEN
        SELECT journey_access INTO v_journey_access
        FROM core.system_role_journey_mapping
        WHERE role_id = v_system_role_id;

        RETURN COALESCE(v_journey_access, '{}'::jsonb);
    END IF;

    -- Letzter Fallback: User-Rolle
    SELECT m.journey_access INTO v_journey_access
    FROM core.users u
    JOIN core.system_role_journey_mapping m ON u.role_id = m.role_id
    WHERE u.user_id = p_user_id;

    RETURN COALESCE(v_journey_access, '{}'::jsonb);
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- ENDE Migration 077
-- =====================================================

-- Verify
DO $$
DECLARE
    v_org_roles_count INTEGER;
    v_permissions_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_org_roles_count FROM core.organisation_roles;
    SELECT COUNT(*) INTO v_permissions_count FROM core.permissions WHERE module IN ('learning', 'teaching', 'management');

    RAISE NOTICE '✅ Migration 077: Flexible RBAC System erfolgreich';
    RAISE NOTICE 'Neue Tabellen:';
    RAISE NOTICE '  - core.organisation_roles';
    RAISE NOTICE '  - core.system_role_journey_mapping';
    RAISE NOTICE 'Neue Functions:';
    RAISE NOTICE '  - get_user_journey_access()';
    RAISE NOTICE '  - has_journey_access()';
    RAISE NOTICE '  - create_standard_organisation_roles()';
    RAISE NOTICE 'Neue Permissions: % (learning/teaching/management)', v_permissions_count;
    RAISE NOTICE 'Organisation-Rollen erstellt: %', v_org_roles_count;
END $$;
