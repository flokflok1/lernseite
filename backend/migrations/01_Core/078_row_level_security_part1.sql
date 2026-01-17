-- =====================================================
-- Migration 078: Row-Level Security (RLS)
-- =====================================================
-- Datum: 2026-01-09
-- Zweck: Aktiviert PostgreSQL Row-Level Security für Multi-Tenancy Isolation
--
-- WICHTIG: Aktiviert RLS auf allen Tabellen mit organisation_id
--
-- NEU:
-- - RLS Policies für automatische Tenant-Isolation
-- - Session-Variable app.current_organisation_id
-- - Admin-Bypass Policies
-- - Helper-Funktionen für RLS-Context
-- =====================================================

-- =====================================================
-- 1. Session-Variable für aktuellen Tenant
-- =====================================================

-- Custom GUC-Variable für aktuellen Tenant
-- Wird von Middleware gesetzt: SET app.current_organisation_id = 'uuid'
-- Kann gelesen werden: current_setting('app.current_organisation_id', true)

COMMENT ON DATABASE current_database() IS
'Uses app.current_organisation_id session variable for RLS';

-- =====================================================
-- 2. Helper-Funktionen
-- =====================================================

-- Funktion: Hole aktuelle Organisation aus Session
CREATE OR REPLACE FUNCTION current_organisation_id()
RETURNS UUID AS $$
BEGIN
    RETURN current_setting('app.current_organisation_id', true)::UUID;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION current_organisation_id IS
'Returns current organisation from session variable (set by middleware)';

-- Funktion: Ist aktueller User Admin?
CREATE OR REPLACE FUNCTION is_admin_user()
RETURNS BOOLEAN AS $$
DECLARE
    v_user_id TEXT;
    v_role_id INTEGER;
BEGIN
    -- Hole user_id aus Session
    v_user_id := current_setting('app.current_user_id', true);

    IF v_user_id IS NULL THEN
        RETURN FALSE;
    END IF;

    -- Prüfe ob User Admin-Rolle hat (role_id = 9)
    SELECT role_id INTO v_role_id
    FROM core.users
    WHERE user_id = v_user_id::UUID
    AND status = 'active';

    RETURN v_role_id = 9;
EXCEPTION
    WHEN OTHERS THEN
        RETURN FALSE;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION is_admin_user IS
'Checks if current user has admin role (bypasses RLS)';

-- Funktion: Prüfe ob User zur Organisation gehört
CREATE OR REPLACE FUNCTION user_belongs_to_organisation(
    p_organisation_id UUID
) RETURNS BOOLEAN AS $$
DECLARE
    v_user_id TEXT;
BEGIN
    v_user_id := current_setting('app.current_user_id', true);

    IF v_user_id IS NULL THEN
        RETURN FALSE;
    END IF;

    RETURN EXISTS (
        SELECT 1
        FROM organisations.organisation_members
        WHERE user_id = v_user_id::UUID
        AND organisation_id = p_organisation_id
        AND status = 'active'
    );
EXCEPTION
    WHEN OTHERS THEN
        RETURN FALSE;
END;
$$ LANGUAGE plpgsql STABLE;

-- =====================================================
-- 3. Aktiviere RLS auf Tabellen
-- =====================================================

-- Courses
ALTER TABLE courses.courses ENABLE ROW LEVEL SECURITY;
ALTER TABLE courses.chapters ENABLE ROW LEVEL SECURITY;
ALTER TABLE courses.lessons ENABLE ROW LEVEL SECURITY;

-- Learning Methods
ALTER TABLE learning_methods.learning_method_instances ENABLE ROW LEVEL SECURITY;

-- Enrollments
ALTER TABLE courses.enrollments ENABLE ROW LEVEL SECURITY;

-- Exams
ALTER TABLE exams.exams ENABLE ROW LEVEL SECURITY;

-- Analytics
ALTER TABLE analytics.events ENABLE ROW LEVEL SECURITY;

-- AI
ALTER TABLE ki.ki_requests ENABLE ROW LEVEL SECURITY;

-- LiveRoom (wenn existiert)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'liveroom' AND table_name = 'rooms') THEN
        EXECUTE 'ALTER TABLE liveroom.rooms ENABLE ROW LEVEL SECURITY';
    END IF;
END $$;

-- =====================================================
-- 4. RLS Policies: Courses
-- =====================================================

-- Policy: User sieht nur Kurse seiner Organisation
DROP POLICY IF EXISTS tenant_isolation_policy ON courses.courses;
CREATE POLICY tenant_isolation_policy ON courses.courses
    FOR ALL
    USING (
        organisation_id IS NULL  -- LSX Academy Kurse (alle sehen)
        OR organisation_id = current_organisation_id()  -- Eigene Organisation
        OR EXISTS (  -- Oder Kurs ist mit User-Org geteilt
            SELECT 1 FROM courses.course_sharing cs
            WHERE cs.course_id = courses.courses.course_id
            AND cs.shared_with_organisation_id = current_organisation_id()
            AND cs.active = TRUE
        )
        OR visibility IN ('community', 'marketplace')  -- Oder global sichtbar
    );

-- Policy: Admin sieht alles
DROP POLICY IF EXISTS admin_bypass_policy ON courses.courses;
CREATE POLICY admin_bypass_policy ON courses.courses
    FOR ALL
    TO PUBLIC
    USING (is_admin_user());

COMMENT ON POLICY tenant_isolation_policy ON courses.courses IS
'Users only see courses from their organisation, shared courses, or public courses';

COMMENT ON POLICY admin_bypass_policy ON courses.courses IS
'Admins bypass RLS and see all courses';

-- =====================================================
-- 5. RLS Policies: Chapters
-- =====================================================

DROP POLICY IF EXISTS tenant_isolation_policy ON courses.chapters;
CREATE POLICY tenant_isolation_policy ON courses.chapters
    FOR ALL
    USING (
        organisation_id IS NULL
        OR organisation_id = current_organisation_id()
    );

DROP POLICY IF EXISTS admin_bypass_policy ON courses.chapters;
CREATE POLICY admin_bypass_policy ON courses.chapters
    FOR ALL
    TO PUBLIC
    USING (is_admin_user());

-- =====================================================
-- 6. RLS Policies: Lessons
-- =====================================================

DROP POLICY IF EXISTS tenant_isolation_policy ON courses.lessons;
CREATE POLICY tenant_isolation_policy ON courses.lessons
    FOR ALL
    USING (
        organisation_id IS NULL
        OR organisation_id = current_organisation_id()
    );

DROP POLICY IF EXISTS admin_bypass_policy ON courses.lessons;
CREATE POLICY admin_bypass_policy ON courses.lessons
    FOR ALL
    TO PUBLIC
    USING (is_admin_user());

-- =====================================================
-- 7. RLS Policies: Learning Method Instances
-- =====================================================

DROP POLICY IF EXISTS tenant_isolation_policy ON learning_methods.learning_method_instances;
CREATE POLICY tenant_isolation_policy ON learning_methods.learning_method_instances
    FOR ALL
    USING (
        organisation_id IS NULL
        OR organisation_id = current_organisation_id()
    );

DROP POLICY IF EXISTS admin_bypass_policy ON learning_methods.learning_method_instances;
CREATE POLICY admin_bypass_policy ON learning_methods.learning_method_instances
    FOR ALL
    TO PUBLIC
    USING (is_admin_user());

-- =====================================================
-- 8. RLS Policies: Enrollments
-- =====================================================

DROP POLICY IF EXISTS tenant_isolation_policy ON courses.enrollments;
CREATE POLICY tenant_isolation_policy ON courses.enrollments
    FOR ALL
    USING (
        organisation_id IS NULL
        OR organisation_id = current_organisation_id()
        OR user_id = current_setting('app.current_user_id', true)::UUID  -- User sieht eigene Enrollments
    );

DROP POLICY IF EXISTS admin_bypass_policy ON courses.enrollments;
CREATE POLICY admin_bypass_policy ON courses.enrollments
    FOR ALL
    TO PUBLIC
    USING (is_admin_user());

-- =====================================================
-- 9. RLS Policies: Exams
-- =====================================================

DROP POLICY IF EXISTS tenant_isolation_policy ON exams.exams;
CREATE POLICY tenant_isolation_policy ON exams.exams
    FOR ALL
    USING (
        organisation_id IS NULL
        OR organisation_id = current_organisation_id()
    );

DROP POLICY IF EXISTS admin_bypass_policy ON exams.exams;
CREATE POLICY admin_bypass_policy ON exams.exams
    FOR ALL
    TO PUBLIC
    USING (is_admin_user());

-- =====================================================
-- 10. RLS Policies: Analytics Events
-- =====================================================

DROP POLICY IF EXISTS tenant_isolation_policy ON analytics.events;
CREATE POLICY tenant_isolation_policy ON analytics.events
