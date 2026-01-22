-- Migration 092: Create groups table
-- Beschreibung: Grundlegende Tabelle für das neue Group-Based RBAC 3.0 System
-- Datum: 2026-01-22
-- Status: Phase 1 - Database Schema

BEGIN;

-- Drop dependent objects if they exist (for idempotency)
DROP TABLE IF EXISTS group_permissions CASCADE;
DROP TABLE IF EXISTS users_groups CASCADE;
DROP TABLE IF EXISTS groups CASCADE;

-- ============================================================================
-- 1. CREATE GROUPS TABLE
-- ============================================================================
CREATE TABLE groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Basic Information
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,

    -- Hierarchical Organization
    organisation_id UUID REFERENCES organisations(id) ON DELETE CASCADE,
    parent_group_id UUID REFERENCES groups(id) ON DELETE SET NULL,

    -- Group Classification
    group_type VARCHAR(50) NOT NULL DEFAULT 'custom',
    is_system_group BOOLEAN DEFAULT FALSE,
    is_protected BOOLEAN DEFAULT FALSE,  -- Protected groups cannot be deleted

    -- Metadata
    metadata JSONB DEFAULT '{}',  -- Flexible storage for group-specific config

    -- Audit Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Constraints
    CONSTRAINT chk_group_type CHECK (group_type IN (
        'department',
        'class',
        'team',
        'org_admin',
        'org_members',
        'system_admin',
        'moderators',
        'support',
        'custom'
    )),

    CONSTRAINT chk_slug_format CHECK (slug ~ '^[a-z0-9-]+$'),
    CONSTRAINT chk_protected_system_groups CHECK (
        is_protected = FALSE OR is_system_group = TRUE
    )
);

-- ============================================================================
-- 2. CREATE INDICES FOR PERFORMANCE
-- ============================================================================
CREATE INDEX idx_groups_organisation_id
    ON groups(organisation_id)
    WHERE organisation_id IS NOT NULL;

CREATE INDEX idx_groups_parent_group_id
    ON groups(parent_group_id)
    WHERE parent_group_id IS NOT NULL;

CREATE INDEX idx_groups_group_type
    ON groups(group_type);

CREATE INDEX idx_groups_is_system_group
    ON groups(is_system_group)
    WHERE is_system_group = TRUE;

CREATE UNIQUE INDEX idx_groups_slug_org
    ON groups(slug, organisation_id)
    WHERE organisation_id IS NOT NULL;

CREATE UNIQUE INDEX idx_groups_slug_system
    ON groups(slug)
    WHERE organisation_id IS NULL AND is_system_group = TRUE;

CREATE INDEX idx_groups_created_at
    ON groups(created_at DESC);

-- ============================================================================
-- 3. ENABLE ROW-LEVEL SECURITY (if RLS is enabled for this table)
-- ============================================================================
ALTER TABLE groups ENABLE ROW LEVEL SECURITY;

-- Create RLS policy for organisation isolation
CREATE POLICY groups_org_isolation ON groups
    USING (
        organisation_id IS NULL  -- System groups
        OR organisation_id = current_setting('app.current_organisation_id')::UUID
    );

-- ============================================================================
-- 4. CREATE TRIGGER FOR updated_at
-- ============================================================================
CREATE TRIGGER trigger_groups_updated_at
    BEFORE UPDATE ON groups
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 5. GRANT PERMISSIONS
-- ============================================================================
GRANT SELECT, INSERT, UPDATE, DELETE ON groups TO app_role;
GRANT SELECT ON groups TO app_readonly;

COMMIT;
