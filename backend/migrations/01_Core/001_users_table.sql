-- ============================================================================
-- Migration: 001_users_table.sql
-- Version: 1.0.0
-- Description: Create core users table for Group-Based Authorization (GBA) System
-- Author: LernsystemX Migration System
-- Date: 2026-01-27
-- Dependencies: 000_functions (PostgreSQL extensions), 000_schemas (core schema)
-- ============================================================================
-- IMPORTANT: This migration creates the base users table.
-- It runs FIRST (after schemas and functions) before other core migrations.
-- ============================================================================

BEGIN;

-- ============================================================================
-- TABLE: core.users (Base table for all user accounts)
-- ============================================================================
CREATE TABLE IF NOT EXISTS core.users (
    -- Primary Key
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Basic Information
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(100) NOT NULL UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    avatar_url TEXT,

    -- Password & Authentication
    password_hash VARCHAR(255) NOT NULL,
    email_verified BOOLEAN DEFAULT FALSE,
    email_verified_at TIMESTAMP WITH TIME ZONE,
    two_factor_enabled BOOLEAN DEFAULT FALSE,

    -- Account Status
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    deactivated_at TIMESTAMP WITH TIME ZONE,

    -- Preferences & Settings
    preferred_language VARCHAR(5) DEFAULT 'de',
    timezone VARCHAR(50) DEFAULT 'Europe/Berlin',
    theme VARCHAR(20) DEFAULT 'light',
    notifications_enabled BOOLEAN DEFAULT TRUE,

    -- Multi-Tenancy (Organization Assignment)
    -- FK will be added in 004_organisation_settings.sql after organisations table is created
    organisation_id UUID,

    -- Account Metadata
    metadata JSONB DEFAULT '{}',
    settings JSONB DEFAULT '{}',

    -- Audit Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE,
    last_login_ip INET,

    -- GBA System Fields (Group-Based Authorization 3.0)
    groups_override JSONB DEFAULT NULL,                          -- Emergency group override
    last_group_sync TIMESTAMP WITH TIME ZONE DEFAULT NULL,       -- When groups were last synced
    migration_roles_to_groups_date TIMESTAMP WITH TIME ZONE DEFAULT NULL,  -- Migration timestamp

    -- Constraints
    CONSTRAINT chk_email_format CHECK (email ~ '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
    CONSTRAINT chk_username_format CHECK (username ~ '^[a-zA-Z0-9_-]{3,50}$'),
    CONSTRAINT chk_not_active_and_deleted CHECK (NOT (is_active AND is_deleted)),
    CONSTRAINT chk_not_verified_and_deleted CHECK (NOT (email_verified AND is_deleted))
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================
CREATE INDEX idx_users_email ON core.users(email);
CREATE INDEX idx_users_username ON core.users(username);
CREATE INDEX idx_users_organisation_id ON core.users(organisation_id) WHERE organisation_id IS NOT NULL;
CREATE INDEX idx_users_is_active ON core.users(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_users_created_at ON core.users(created_at DESC);
CREATE INDEX idx_users_last_login_at ON core.users(last_login_at DESC) WHERE last_login_at IS NOT NULL;
CREATE INDEX idx_users_email_verified ON core.users(email_verified) WHERE email_verified = FALSE;
CREATE INDEX idx_users_is_deleted ON core.users(is_deleted) WHERE is_deleted = FALSE;
CREATE INDEX idx_users_migration_roles_to_groups_date ON core.users(migration_roles_to_groups_date) WHERE migration_roles_to_groups_date IS NOT NULL;
CREATE INDEX idx_users_last_group_sync ON core.users(last_group_sync DESC) WHERE last_group_sync IS NOT NULL;

-- ============================================================================
-- COMMENTS & DOCUMENTATION
-- ============================================================================
COMMENT ON TABLE core.users IS 'Core domain users table - Base table for all user accounts in GBA System';
COMMENT ON COLUMN core.users.user_id IS 'Unique user identifier (UUID)';
COMMENT ON COLUMN core.users.email IS 'User email address (unique, required)';
COMMENT ON COLUMN core.users.username IS 'Username for login (unique, required)';
COMMENT ON COLUMN core.users.password_hash IS 'Bcrypt hashed password';
COMMENT ON COLUMN core.users.is_active IS 'Whether user account is active';
COMMENT ON COLUMN core.users.organisation_id IS 'Organization the user belongs to (multi-tenancy)';
COMMENT ON COLUMN core.users.groups_override IS 'Emergency group override for special cases (JSONB)';
COMMENT ON COLUMN core.users.last_group_sync IS 'Timestamp when groups were last synced';

COMMIT;
