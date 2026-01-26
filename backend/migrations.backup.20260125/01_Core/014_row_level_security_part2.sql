-- ============================================================================
-- Migration: 078_row_level_security_part2.sql
-- Description: Row Level Security - Part 2: Additional Policies
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-01-16
-- ============================================================================
-- Note: Split from original 078_row_level_security.sql (525 lines)
--       Part 2 of 2
-- ============================================================================

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
