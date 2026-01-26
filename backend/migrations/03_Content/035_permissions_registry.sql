-- Migration 094: Create permissions registry table
-- Beschreibung: Zentrale Registry für alle verfügbaren Permissions im System
-- Datum: 2026-01-22
-- Status: Phase 1 - Database Schema

BEGIN;

-- ============================================================================
-- 1. CREATE PERMISSIONS TABLE
-- ============================================================================
CREATE TABLE core.permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Permission Identity
    code VARCHAR(100) UNIQUE NOT NULL,  -- e.g. 'content.courses:read', 'admin.users:write'
    display_name VARCHAR(255) NOT NULL,  -- Human-readable name
    description TEXT,  -- Detailed description

    -- Classification
    permission_type VARCHAR(50) NOT NULL DEFAULT 'general',  -- system, organisation, group, general
    category VARCHAR(100),  -- e.g. 'courses', 'users', 'content', 'system', 'admin'

    -- System Permission Flag
    is_system_permission BOOLEAN DEFAULT FALSE,  -- Cannot be deleted if TRUE

    -- Metadata
    metadata JSONB DEFAULT '{}',  -- Flexible storage for permission-specific config

    -- Audit Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    CONSTRAINT chk_permission_type CHECK (permission_type IN (
        'system',
        'organisation',
        'group',
        'general'
    )),

    CONSTRAINT chk_protected_system_perms CHECK (
        is_system_permission = FALSE OR is_system_permission = TRUE
    ),

    CONSTRAINT chk_code_format CHECK (code ~ '^[a-z0-9._:]+$')
);

-- ============================================================================
-- 2. CREATE INDICES FOR PERFORMANCE
-- ============================================================================
CREATE UNIQUE INDEX idx_permissions_code
    ON core.permissions(code);

CREATE INDEX idx_permissions_category
    ON core.permissions(category);

CREATE INDEX idx_permissions_permission_type
    ON core.permissions(permission_type);

CREATE INDEX idx_permissions_is_system
    ON core.permissions(is_system_permission)
    WHERE is_system_permission = TRUE;

-- ============================================================================
-- 3. Seed Data Relocation Notice
-- ============================================================================
-- The following seed data statements have been moved to dedicated seed files:
-- - System Permissions (14 core GBA permissions) → 00_Seeds/19_system_permissions.sql
--
-- This migration file now contains ONLY structural CREATE statements.

-- ============================================================================
-- 4. CREATE TRIGGER FOR updated_at
-- ============================================================================
DROP TRIGGER IF EXISTS trigger_permissions_updated_at ON core.permissions;
CREATE TRIGGER trigger_permissions_updated_at
    BEFORE UPDATE ON core.permissions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 5. CREATE HELPER FUNCTION: Get permission by code
-- ============================================================================
CREATE OR REPLACE FUNCTION get_permission_by_code(p_code VARCHAR)
RETURNS TABLE(id UUID, display_name VARCHAR, permission_type VARCHAR)
AS $$
    SELECT
        p.id,
        p.display_name,
        p.permission_type
    FROM core.permissions p
    WHERE p.code = p_code;
$$ LANGUAGE SQL STABLE;

-- ============================================================================
-- 6. CREATE HELPER FUNCTION: Get all permissions by category
-- ============================================================================
CREATE OR REPLACE FUNCTION get_permissions_by_category(p_category VARCHAR)
RETURNS TABLE(code VARCHAR, display_name VARCHAR, permission_type VARCHAR)
AS $$
    SELECT
        p.code,
        p.display_name,
        p.permission_type
    FROM core.permissions p
    WHERE p.category = p_category
    ORDER BY p.code;
$$ LANGUAGE SQL STABLE;

-- ============================================================================
-- 7. GRANT PERMISSIONS
-- ============================================================================
-- Note: GRANT statements removed - app_role and app_readonly do not exist
-- Permissions will be inherited from database owner

COMMIT;
