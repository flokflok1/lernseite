-- ============================================================================
-- Migration: 014_row_level_security_part2.sql
-- Description: Row Level Security - Part 2: Org-specific Policies
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-01-27
-- ============================================================================
-- Note: Part 2 of RLS infrastructure. Only enables RLS on 01_Core tables.
-- Domain-specific RLS policies (courses, exams, etc.) belong in their
-- respective domain migrations.
-- ============================================================================

BEGIN;

-- =====================================================
-- 1. RLS für Organisation-Member Tabellen
-- =====================================================

-- Organisation Members: User sieht nur Members seiner Org
ALTER TABLE IF EXISTS organisations.organisation_members ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS member_isolation_policy ON organisations.organisation_members;
CREATE POLICY member_isolation_policy ON organisations.organisation_members
    FOR ALL
    USING (
        organisation_id = current_organisation_id()
        OR user_id = current_setting('app.current_user_id', true)::UUID  -- Eigenes Membership
        OR is_admin_user()
    );

-- =====================================================
-- 2. RLS für Organisation Settings & Features
-- =====================================================

-- Organisation Stats: Nur eigene Org
ALTER TABLE IF EXISTS organisations.organisation_stats ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS stats_isolation_policy ON organisations.organisation_stats;
CREATE POLICY stats_isolation_policy ON organisations.organisation_stats
    FOR ALL
    USING (
        organisation_id = current_organisation_id()
        OR is_admin_user()
    );

-- Custom Domains: Nur eigene Org
ALTER TABLE IF EXISTS organisations.custom_domains ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS domain_isolation_policy ON organisations.custom_domains;
CREATE POLICY domain_isolation_policy ON organisations.custom_domains
    FOR ALL
    USING (
        organisation_id = current_organisation_id()
        OR is_admin_user()
    );

-- Branding: Nur eigene Org
ALTER TABLE IF EXISTS organisations.branding ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS branding_isolation_policy ON organisations.branding;
CREATE POLICY branding_isolation_policy ON organisations.branding
    FOR ALL
    USING (
        organisation_id = current_organisation_id()
        OR is_admin_user()
    );

-- Feature Flags: Nur eigene Org
ALTER TABLE IF EXISTS organisations.feature_flags ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS feature_flags_isolation_policy ON organisations.feature_flags;
CREATE POLICY feature_flags_isolation_policy ON organisations.feature_flags
    FOR ALL
    USING (
        organisation_id = current_organisation_id()
        OR is_admin_user()
    );

-- =====================================================
-- 3. RLS für Organisation-Rollen (Core Schema)
-- =====================================================

ALTER TABLE IF EXISTS core.organisation_roles ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS org_roles_isolation_policy ON core.organisation_roles;
CREATE POLICY org_roles_isolation_policy ON core.organisation_roles
    FOR ALL
    USING (
        organisation_id = current_organisation_id()
        OR is_admin_user()
    );

-- =====================================================
-- 4. Helper Function: Set Organisation Context (für Middleware)
-- =====================================================

-- Funktion zum Setzen des Tenant-Context
DROP FUNCTION IF EXISTS set_organisation_context(UUID, UUID);
CREATE FUNCTION set_organisation_context(
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
-- 5. Helper Function: Clear Organisation Context
-- =====================================================

DROP FUNCTION IF EXISTS clear_organisation_context();
CREATE FUNCTION clear_organisation_context()
RETURNS VOID AS $$
BEGIN
    PERFORM set_config('app.current_organisation_id', NULL, false);
    PERFORM set_config('app.current_user_id', NULL, false);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION clear_organisation_context IS
'Clears organisation context (called at end of request)';

-- =====================================================
-- 6. View: Current Request Context
-- =====================================================

DROP VIEW IF EXISTS core.current_request_context;
CREATE VIEW core.current_request_context AS
SELECT
    current_organisation_id() AS organisation_id,
    current_setting('app.current_user_id', true)::UUID AS user_id,
    is_admin_user() AS is_admin,
    NOW() AS request_timestamp;

COMMENT ON VIEW core.current_request_context IS
'Shows current request context (organisation, user, admin status)';

-- =====================================================
-- 7. Test Function: Check RLS Status
-- =====================================================

DROP FUNCTION IF EXISTS test_rls();
CREATE FUNCTION test_rls()
RETURNS TABLE (
    table_name TEXT,
    schema_name TEXT,
    rls_enabled BOOLEAN,
    policy_count INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.relname::TEXT,
        n.nspname::TEXT,
        c.relrowsecurity,
        COUNT(p.*)::INTEGER
    FROM pg_class c
    LEFT JOIN pg_namespace n ON n.oid = c.relnamespace
    LEFT JOIN pg_policies p ON p.tablename = c.relname AND p.schemaname = n.nspname
    WHERE n.nspname IN ('organisations', 'core')
    AND c.relkind = 'r'
    AND c.relrowsecurity = TRUE
    GROUP BY c.oid, n.nspname, c.relname, c.relrowsecurity
    ORDER BY n.nspname, c.relname;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION test_rls IS
'Tests RLS configuration for organisations and core schemas';

-- =====================================================
-- 8. Verification & Logging
-- =====================================================

DO $$
DECLARE
    v_rls_tables INTEGER;
    v_policies INTEGER;
BEGIN
    -- Zähle Tabellen mit RLS in organisations und core
    SELECT COUNT(*) INTO v_rls_tables
    FROM pg_class c
    LEFT JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relrowsecurity = TRUE
    AND n.nspname IN ('organisations', 'core');

    -- Zähle Policies
    SELECT COUNT(*) INTO v_policies
    FROM pg_policies
    WHERE schemaname IN ('organisations', 'core');

    RAISE NOTICE '✅ Migration 014: Row-Level Security (Part 2) erfolgreich';
    RAISE NOTICE 'RLS aktiviert auf % Tabellen in organisations + core', v_rls_tables;
    RAISE NOTICE 'RLS Policies erstellt: %', v_policies;
    RAISE NOTICE 'Neue/Erweiterte Functions:';
    RAISE NOTICE '  - set_organisation_context(organisation_id, user_id)';
    RAISE NOTICE '  - clear_organisation_context()';
    RAISE NOTICE '  - test_rls() - check RLS status';
    RAISE NOTICE '';
    RAISE NOTICE '📝 WICHTIG für Backend Middleware:';
    RAISE NOTICE '  1. Am Anfang einer Request: set_organisation_context(org_id)';
    RAISE NOTICE '  2. Session-Variable app.current_organisation_id ist dann gesetzt';
    RAISE NOTICE '  3. Am Ende einer Request: clear_organisation_context()';
    RAISE NOTICE '';
    RAISE NOTICE '⚠️  Domain-Specific RLS Policies (courses, exams, etc.) sind';
    RAISE NOTICE '   in ihren jeweiligen Domain-Migrations definiert.';
END $$;

COMMIT;
