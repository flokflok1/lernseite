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
    FOR ALL
    USING (
        organisation_id IS NULL
        OR organisation_id = current_organisation_id()
    );

DROP POLICY IF EXISTS admin_bypass_policy ON analytics.events;
CREATE POLICY admin_bypass_policy ON analytics.events
    FOR ALL
    TO PUBLIC
    USING (is_admin_user());

-- =====================================================
-- 11. RLS Policies: KI Requests
-- =====================================================

DROP POLICY IF EXISTS tenant_isolation_policy ON ki.ki_requests;
CREATE POLICY tenant_isolation_policy ON ki.ki_requests
    FOR ALL
    USING (
        organisation_id IS NULL
        OR organisation_id = current_organisation_id()
    );

DROP POLICY IF EXISTS admin_bypass_policy ON ki.ki_requests;
CREATE POLICY admin_bypass_policy ON ki.ki_requests
    FOR ALL
    TO PUBLIC
    USING (is_admin_user());

-- =====================================================
-- 12. RLS Policies: LiveRoom (wenn existiert)
-- =====================================================

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'liveroom' AND table_name = 'rooms') THEN
        -- Tenant Isolation
        EXECUTE '
            DROP POLICY IF EXISTS tenant_isolation_policy ON liveroom.rooms;
            CREATE POLICY tenant_isolation_policy ON liveroom.rooms
                FOR ALL
                USING (
                    organisation_id IS NULL
                    OR organisation_id = current_organisation_id()
                );
        ';

        -- Admin Bypass
        EXECUTE '
            DROP POLICY IF EXISTS admin_bypass_policy ON liveroom.rooms;
            CREATE POLICY admin_bypass_policy ON liveroom.rooms
                FOR ALL
                TO PUBLIC
                USING (is_admin_user());
        ';

        RAISE NOTICE '✅ RLS policies für liveroom.rooms erstellt';
    END IF;
END $$;

-- =====================================================
-- 13. RLS für Organisation-Tabellen selbst
-- =====================================================

-- Organisation Members: User sieht nur Members seiner Org
ALTER TABLE organisations.organisation_members ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS member_isolation_policy ON organisations.organisation_members;
CREATE POLICY member_isolation_policy ON organisations.organisation_members
    FOR ALL
    USING (
        organisation_id = current_organisation_id()
        OR user_id = current_setting('app.current_user_id', true)::UUID  -- Eigenes Membership
        OR is_admin_user()
    );

-- Organisation Stats: Nur eigene Org
ALTER TABLE organisations.organisation_stats ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS stats_isolation_policy ON organisations.organisation_stats;
CREATE POLICY stats_isolation_policy ON organisations.organisation_stats
    FOR ALL
    USING (
        organisation_id = current_organisation_id()
        OR is_admin_user()
    );

-- Custom Domains: Nur eigene Org
ALTER TABLE organisations.custom_domains ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS domain_isolation_policy ON organisations.custom_domains;
CREATE POLICY domain_isolation_policy ON organisations.custom_domains
    FOR ALL
    USING (
        organisation_id = current_organisation_id()
        OR is_admin_user()
    );

-- Branding: Nur eigene Org
ALTER TABLE organisations.branding ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS branding_isolation_policy ON organisations.branding;
CREATE POLICY branding_isolation_policy ON organisations.branding
    FOR ALL
    USING (
        organisation_id = current_organisation_id()
        OR is_admin_user()
    );

-- Feature Flags: Nur eigene Org
ALTER TABLE organisations.feature_flags ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS feature_flags_isolation_policy ON organisations.feature_flags;
CREATE POLICY feature_flags_isolation_policy ON organisations.feature_flags
    FOR ALL
    USING (
        organisation_id = current_organisation_id()
        OR is_admin_user()
    );

-- =====================================================
-- 14. RLS für Organisation-Rollen
-- =====================================================

ALTER TABLE core.organisation_roles ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS org_roles_isolation_policy ON core.organisation_roles;
CREATE POLICY org_roles_isolation_policy ON core.organisation_roles
    FOR ALL
    USING (
        organisation_id = current_organisation_id()
        OR is_admin_user()
    );

-- =====================================================
-- 15. Helper: Set Organisation Context (für Middleware)
-- =====================================================

-- Funktion zum Setzen des Tenant-Context
CREATE OR REPLACE FUNCTION set_organisation_context(
    p_organisation_id UUID,
    p_user_id UUID DEFAULT NULL
) RETURNS VOID AS $$
BEGIN
    -- Setze Organisation
    PERFORM set_config('app.current_organisation_id', p_organisation_id::TEXT, false);

    -- Setze User (optional)
    IF p_user_id IS NOT NULL THEN
        PERFORM set_config('app.current_user_id', p_user_id::TEXT, false);
    END IF;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION set_organisation_context IS
'Sets organisation context for RLS (called by middleware)';

-- =====================================================
-- 16. Helper: Clear Organisation Context
-- =====================================================

CREATE OR REPLACE FUNCTION clear_organisation_context()
RETURNS VOID AS $$
BEGIN
    PERFORM set_config('app.current_organisation_id', NULL, false);
    PERFORM set_config('app.current_user_id', NULL, false);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION clear_organisation_context IS
'Clears organisation context (called at end of request)';

-- =====================================================
-- 17. Middleware Helper View
-- =====================================================

-- View: Current Request Context
CREATE OR REPLACE VIEW core.current_request_context AS
SELECT
    current_organisation_id() AS organisation_id,
    current_setting('app.current_user_id', true)::UUID AS user_id,
    is_admin_user() AS is_admin,
    NOW() AS request_timestamp;

COMMENT ON VIEW core.current_request_context IS
'Shows current request context (organisation, user, admin status)';

-- =====================================================
-- 18. Testing Functions
-- =====================================================

-- Funktion: Test RLS
CREATE OR REPLACE FUNCTION test_rls()
RETURNS TABLE (
    table_name TEXT,
    rls_enabled BOOLEAN,
    policy_count INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.relname::TEXT AS table_name,
        c.relrowsecurity AS rls_enabled,
        COUNT(p.*)::INTEGER AS policy_count
    FROM pg_class c
    LEFT JOIN pg_policies p ON p.tablename = c.relname
    WHERE c.relnamespace IN (
        SELECT oid FROM pg_namespace
        WHERE nspname IN ('courses', 'learning_methods', 'exams', 'analytics', 'ki', 'organisations', 'core')
    )
    AND c.relkind = 'r'
    AND c.relrowsecurity = TRUE
    GROUP BY c.relname, c.relrowsecurity
    ORDER BY c.relname;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION test_rls IS
'Tests RLS configuration (lists all tables with RLS enabled)';

-- =====================================================
-- ENDE Migration 078
-- =====================================================

-- Verify
DO $$
DECLARE
    v_rls_tables INTEGER;
    v_policies INTEGER;
BEGIN
    -- Zähle Tabellen mit RLS
    SELECT COUNT(*) INTO v_rls_tables
    FROM pg_class c
    WHERE c.relrowsecurity = TRUE
    AND c.relnamespace IN (
        SELECT oid FROM pg_namespace
        WHERE nspname IN ('courses', 'learning_methods', 'exams', 'analytics', 'ki', 'organisations', 'core')
    );

    -- Zähle Policies
    SELECT COUNT(*) INTO v_policies
    FROM pg_policies
    WHERE schemaname IN ('courses', 'learning_methods', 'exams', 'analytics', 'ki', 'organisations', 'core');

    RAISE NOTICE '✅ Migration 078: Row-Level Security erfolgreich';
    RAISE NOTICE 'RLS aktiviert auf % Tabellen', v_rls_tables;
    RAISE NOTICE 'RLS Policies erstellt: %', v_policies;
    RAISE NOTICE 'Neue Functions:';
    RAISE NOTICE '  - current_organisation_id()';
    RAISE NOTICE '  - is_admin_user()';
    RAISE NOTICE '  - set_organisation_context()';
    RAISE NOTICE '  - clear_organisation_context()';
    RAISE NOTICE '  - test_rls()';
    RAISE NOTICE '';
    RAISE NOTICE '📝 WICHTIG für Backend:';
    RAISE NOTICE '  - Middleware muss set_organisation_context() aufrufen';
    RAISE NOTICE '  - Session-Variable app.current_organisation_id setzen';
    RAISE NOTICE '  - Am Ende jeder Request: clear_organisation_context()';
END $$;

-- Test-Output
SELECT * FROM test_rls();
