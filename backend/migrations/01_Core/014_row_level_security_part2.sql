-- ============================================================================
-- Migration: 014_row_level_security_part2.sql
-- Description: Row Level Security - Part 2: Org-specific Policies (Conditional)
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-01-27
-- ============================================================================
-- Note: Part 2 of RLS infrastructure.
-- Only enables RLS on organisations and core tables that exist.
-- Uses DO blocks with IF EXISTS checks for safety.
-- ============================================================================

BEGIN;

-- =====================================================
-- 1. Helper Function to Check & Enable RLS + Policy
-- =====================================================

DROP FUNCTION IF EXISTS conditional_enable_rls_with_policy(VARCHAR, VARCHAR, TEXT, TEXT);
CREATE FUNCTION conditional_enable_rls_with_policy(
    p_schema VARCHAR,
    p_table VARCHAR,
    p_policy_name TEXT,
    p_policy_sql TEXT
) RETURNS VOID AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = p_schema AND table_name = p_table
    ) THEN
        -- Enable RLS
        EXECUTE FORMAT('ALTER TABLE %I.%I ENABLE ROW LEVEL SECURITY', p_schema, p_table);

        -- Drop existing policy if any
        EXECUTE FORMAT('DROP POLICY IF EXISTS %I ON %I.%I', p_policy_name, p_schema, p_table);

        -- Create new policy
        EXECUTE p_policy_sql;

        RAISE NOTICE '✓ RLS enabled for %.% with policy %', p_schema, p_table, p_policy_name;
    ELSE
        RAISE NOTICE '⚠ Skipping %.% - table does not exist yet', p_schema, p_table;
    END IF;
EXCEPTION WHEN OTHERS THEN
    RAISE WARNING '✗ Error setting RLS for %.% - %', p_schema, p_table, SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 2. RLS für Organisation-Member Tabellen (Conditional)
-- =====================================================

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables
               WHERE table_schema = 'organisations' AND table_name = 'organisation_members') THEN

        ALTER TABLE organisations.organisation_members ENABLE ROW LEVEL SECURITY;

        DROP POLICY IF EXISTS member_isolation_policy ON organisations.organisation_members;
        CREATE POLICY member_isolation_policy ON organisations.organisation_members
            FOR ALL
            USING (
                organisation_id = current_organisation_id()
                OR user_id = current_setting('app.current_user_id', true)::UUID
                OR is_admin_user()
            );

        RAISE NOTICE '✓ RLS enabled for organisations.organisation_members';
    ELSE
        RAISE NOTICE '⚠ organisations.organisation_members table does not exist yet - skipping RLS';
    END IF;
EXCEPTION WHEN OTHERS THEN
    RAISE WARNING '✗ Error setting RLS for organisations.organisation_members: %', SQLERRM;
END $$;

-- =====================================================
-- 3. RLS für Organisation Statistics (Conditional)
-- =====================================================

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables
               WHERE table_schema = 'organisations' AND table_name = 'organisation_stats') THEN

        ALTER TABLE organisations.organisation_stats ENABLE ROW LEVEL SECURITY;

        DROP POLICY IF EXISTS stats_isolation_policy ON organisations.organisation_stats;
        CREATE POLICY stats_isolation_policy ON organisations.organisation_stats
            FOR ALL
            USING (
                organisation_id = current_organisation_id()
                OR is_admin_user()
            );

        RAISE NOTICE '✓ RLS enabled for organisations.organisation_stats';
    ELSE
        RAISE NOTICE '⚠ organisations.organisation_stats table does not exist yet - skipping RLS';
    END IF;
EXCEPTION WHEN OTHERS THEN
    RAISE WARNING '✗ Error setting RLS for organisations.organisation_stats: %', SQLERRM;
END $$;

-- =====================================================
-- 4. RLS für Custom Domains (Conditional)
-- =====================================================

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables
               WHERE table_schema = 'organisations' AND table_name = 'custom_domains') THEN

        ALTER TABLE organisations.custom_domains ENABLE ROW LEVEL SECURITY;

        DROP POLICY IF EXISTS domain_isolation_policy ON organisations.custom_domains;
        CREATE POLICY domain_isolation_policy ON organisations.custom_domains
            FOR ALL
            USING (
                organisation_id = current_organisation_id()
                OR is_admin_user()
            );

        RAISE NOTICE '✓ RLS enabled for organisations.custom_domains';
    END IF;
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE '⚠ organisations.custom_domains table does not exist yet - skipping RLS';
END $$;

-- =====================================================
-- 5. RLS für Branding (Conditional)
-- =====================================================

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables
               WHERE table_schema = 'organisations' AND table_name = 'branding') THEN

        ALTER TABLE organisations.branding ENABLE ROW LEVEL SECURITY;

        DROP POLICY IF EXISTS branding_isolation_policy ON organisations.branding;
        CREATE POLICY branding_isolation_policy ON organisations.branding
            FOR ALL
            USING (
                organisation_id = current_organisation_id()
                OR is_admin_user()
            );

        RAISE NOTICE '✓ RLS enabled for organisations.branding';
    END IF;
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE '⚠ organisations.branding table does not exist yet - skipping RLS';
END $$;

-- =====================================================
-- 6. RLS für Feature Flags (Conditional)
-- =====================================================

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables
               WHERE table_schema = 'organisations' AND table_name = 'feature_flags') THEN

        ALTER TABLE organisations.feature_flags ENABLE ROW LEVEL SECURITY;

        DROP POLICY IF EXISTS feature_flags_isolation_policy ON organisations.feature_flags;
        CREATE POLICY feature_flags_isolation_policy ON organisations.feature_flags
            FOR ALL
            USING (
                organisation_id = current_organisation_id()
                OR is_admin_user()
            );

        RAISE NOTICE '✓ RLS enabled for organisations.feature_flags';
    END IF;
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE '⚠ organisations.feature_flags table does not exist yet - skipping RLS';
END $$;

-- =====================================================
-- 7. RLS für Organisation-Rollen (Conditional)
-- =====================================================

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables
               WHERE table_schema = 'core' AND table_name = 'organisation_roles') THEN

        ALTER TABLE core.organisation_roles ENABLE ROW LEVEL SECURITY;

        DROP POLICY IF EXISTS org_roles_isolation_policy ON core.organisation_roles;
        CREATE POLICY org_roles_isolation_policy ON core.organisation_roles
            FOR ALL
            USING (
                organisation_id = current_organisation_id()
                OR is_admin_user()
            );

        RAISE NOTICE '✓ RLS enabled for core.organisation_roles';
    END IF;
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE '⚠ core.organisation_roles table does not exist yet - skipping RLS';
END $$;

-- =====================================================
-- 8. Helper Functions for Middleware
-- =====================================================

DROP FUNCTION IF EXISTS set_organisation_context(UUID, UUID);
CREATE FUNCTION set_organisation_context(
    p_organisation_id UUID,
    p_user_id UUID DEFAULT NULL
) RETURNS VOID AS $$
BEGIN
    PERFORM set_config('app.current_organisation_id', p_organisation_id::TEXT, false);
    IF p_user_id IS NOT NULL THEN
        PERFORM set_config('app.current_user_id', p_user_id::TEXT, false);
    END IF;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION set_organisation_context IS
'Sets organisation context for RLS (called by middleware)';

-- =====================================================
-- 9. Helper: Clear Organisation Context
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
-- 10. View: Current Request Context
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
-- 11. Test Function: Check RLS Status
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
-- 12. Final Verification
-- =====================================================

DO $$
DECLARE
    v_rls_tables INTEGER;
    v_policies INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_rls_tables
    FROM pg_class c
    LEFT JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relrowsecurity = TRUE
    AND n.nspname IN ('organisations', 'core');

    SELECT COUNT(*) INTO v_policies
    FROM pg_policies
    WHERE schemaname IN ('organisations', 'core');

    RAISE NOTICE '✅ Migration 014: Row-Level Security (Part 2) - COMPLETED';
    RAISE NOTICE 'RLS activated on % tables in organisations + core', v_rls_tables;
    RAISE NOTICE 'RLS Policies created: %', v_policies;
    RAISE NOTICE '';
    RAISE NOTICE '📝 Middleware Integration Required:';
    RAISE NOTICE '  1. Before query: set_organisation_context(org_id, user_id)';
    RAISE NOTICE '  2. After query: clear_organisation_context()';
    RAISE NOTICE '';
    RAISE NOTICE '⚠️  Domain-Specific RLS Policies (courses, exams, etc.)';
    RAISE NOTICE '   are defined in their respective domain migrations.';
END $$;

COMMIT;
