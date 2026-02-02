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
-- Note: This session variable is set by the application middleware

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
-- 3. Aktiviere RLS auf Tabellen (Conditionally)
-- =====================================================
-- Note: RLS is only enabled on tables that exist.
-- Tables from other schemas (courses, exams, etc.) will be created later
-- and should have RLS enabled in their respective migrations.

-- Helper function to conditionally enable RLS
CREATE OR REPLACE FUNCTION enable_rls_if_exists(p_schema VARCHAR, p_table VARCHAR) RETURNS VOID AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = p_schema AND table_name = p_table
    ) THEN
        EXECUTE FORMAT('ALTER TABLE %I.%I ENABLE ROW LEVEL SECURITY', p_schema, p_table);
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Enable RLS on core tables (only if they exist)
SELECT enable_rls_if_exists('core', 'users');
SELECT enable_rls_if_exists('core', 'groups');
SELECT enable_rls_if_exists('organisations', 'organisations');

-- Other tables will have RLS enabled in their respective migrations

-- =====================================================
-- 4-9. RLS Policies for Domain Tables
-- =====================================================
-- MOVED: RLS policies for courses, chapters, lessons, learning methods, enrollments, exams,
-- and other domain tables have been moved to their respective domain migrations
-- (02_Content, 03_AI, etc.) to ensure tables exist before policies are created.
--
-- This follows the pattern:
-- - Core RLS infrastructure (helper functions) in 01_Core
-- - Domain-specific RLS policies in their respective migration folders
--
-- Example:
-- - Courses RLS policies → 02_Content/012_learning_progress.sql (or similar)
-- - Exams RLS policies → 02_Content/013_exams.sql
-- - AI RLS policies → 03_AI/XXX_ai_infrastructure.sql

-- RLS Infrastructure for Core Database Complete
COMMIT;
