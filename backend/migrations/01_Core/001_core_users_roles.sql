-- ============================================================================
-- Migration: 001_core_users_roles.sql
-- Version: 1.0.0
-- Description: Database migration
-- Author: LernsystemX Migration System
-- Date: 2026-01-02
-- ============================================================================

BEGIN;

-- ============================================================================
-- PART 1: CREATE POSTGRESQL SCHEMAS
-- ============================================================================
-- Create 12 logical schemas for organizing 195+ tables
-- This MUST be done first before any table creation

CREATE SCHEMA IF NOT EXISTS core;               -- Auth, RBAC, System
CREATE SCHEMA IF NOT EXISTS organisations;      -- Schools, Companies (British spelling)
CREATE SCHEMA IF NOT EXISTS courses;            -- Course Hierarchy
CREATE SCHEMA IF NOT EXISTS learning_methods;   -- 19 Content LMs
CREATE SCHEMA IF NOT EXISTS assessments;        -- Exams, Certificates
CREATE SCHEMA IF NOT EXISTS ai_pipeline;        -- AI Integration
CREATE SCHEMA IF NOT EXISTS liveroom;           -- Real-Time Rooms
CREATE SCHEMA IF NOT EXISTS analytics;          -- Learning Analytics
CREATE SCHEMA IF NOT EXISTS smart_agents;       -- AI Knowledge Caching
CREATE SCHEMA IF NOT EXISTS support_systems;    -- Support, Feedback
CREATE SCHEMA IF NOT EXISTS billing_storage;    -- Payments, Media
CREATE SCHEMA IF NOT EXISTS translations;       -- Multi-Language
CREATE SCHEMA IF NOT EXISTS gamification;       -- XP, Achievements, Skills
CREATE SCHEMA IF NOT EXISTS community;          -- Groups, Peer Review, Portfolios
CREATE SCHEMA IF NOT EXISTS notifications;      -- Notification System
CREATE SCHEMA IF NOT EXISTS storage;            -- File Storage, Media
CREATE SCHEMA IF NOT EXISTS dashboards;         -- Dashboard & Widget System
CREATE SCHEMA IF NOT EXISTS it_environments;    -- IT Sandbox Environments
CREATE SCHEMA IF NOT EXISTS email;              -- Email Queue

-- Set default search path for backwards compatibility
-- Uses current_database() to work with any database name
DO $$
BEGIN
    EXECUTE format('ALTER DATABASE %I SET search_path TO public, core, organisations, courses, learning_methods, assessments, ai_pipeline, liveroom, analytics, smart_agents, support_systems, billing_storage, translations', current_database());
END $$;

COMMENT ON SCHEMA core IS 'Core system tables: users, roles, permissions, audit';
COMMENT ON SCHEMA organisations IS 'Multi-tenant organisation tables';
COMMENT ON SCHEMA courses IS 'Course hierarchy: courses, chapters, lessons';
COMMENT ON SCHEMA learning_methods IS '19 Content-Lernmethoden (lm00-lm18)';
COMMENT ON SCHEMA assessments IS 'Exams, quizzes, certificates';
COMMENT ON SCHEMA ai_pipeline IS 'AI integration: providers, models, prompts, jobs';
COMMENT ON SCHEMA liveroom IS 'Real-time learning rooms with WebRTC';
COMMENT ON SCHEMA analytics IS 'Learning analytics, events, dashboards';
COMMENT ON SCHEMA smart_agents IS 'AI knowledge caching per course';
COMMENT ON SCHEMA support_systems IS 'Notifications, community, gamification';
COMMENT ON SCHEMA billing_storage IS 'Subscriptions, tokens, media storage';
COMMENT ON SCHEMA translations IS 'Multi-language support (20 languages)';

-- ============================================================================
-- PART 2: EXTENSIONS
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- PART 3: CORE SCHEMA TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- TABLE: core.roles
-- Description: System roles (9 predefined roles)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS core.roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    hierarchy_level INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_role_hierarchy CHECK (hierarchy_level BETWEEN 1 AND 9)
);

CREATE INDEX IF NOT EXISTS idx_roles_name ON core.roles(role_name);
CREATE INDEX IF NOT EXISTS idx_roles_hierarchy ON core.roles(hierarchy_level);

COMMENT ON TABLE core.roles IS 'System roles for LSX: free, premium, creator, teacher, school_admin, company_admin, support, moderator, admin';

-- Seed standard roles
INSERT INTO core.roles (role_name, display_name, description, hierarchy_level) VALUES
    ('free', 'Free User', 'Kostenloser Basis-Zugang (11 Methoden)', 1),
    ('premium', 'Premium User', 'Premium-Mitgliedschaft (17 Methoden)', 2),
    ('creator', 'Creator', 'Kurs-Ersteller (Creator Marketplace)', 3),
    ('teacher', 'Lehrer/Dozent', 'Lehrer mit Klassenverwaltung', 4),
    ('school_admin', 'Schul-Administrator', 'Schul-Administrator', 5),
    ('company_admin', 'Unternehmens-Administrator', 'Unternehmens-Administrator', 6),
    ('support', 'Support-Team', 'Support-Mitarbeiter', 7),
    ('moderator', 'Community-Moderator', 'Community-Moderator', 8),
    ('admin', 'System-Administrator', 'System-Administrator (volle Rechte)', 9)
ON CONFLICT (role_name) DO NOTHING;

-- ----------------------------------------------------------------------------
-- TABLE: core.permissions
-- Description: Granular permissions for role-based access control
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS core.permissions (
    permission_id SERIAL PRIMARY KEY,
    permission_key VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    module VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_permissions_key ON core.permissions(permission_key);
CREATE INDEX IF NOT EXISTS idx_permissions_module ON core.permissions(module);

COMMENT ON TABLE core.permissions IS 'Granular permissions for RBAC system';

-- ----------------------------------------------------------------------------
-- TABLE: core.role_permissions
-- Description: Many-to-many relationship between roles and permissions
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS core.role_permissions (
    role_id INTEGER REFERENCES core.roles(role_id) ON DELETE CASCADE,
    permission_id INTEGER REFERENCES core.permissions(permission_id) ON DELETE CASCADE,
    granted_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (role_id, permission_id)
);

CREATE INDEX IF NOT EXISTS idx_role_perms_role ON core.role_permissions(role_id);
CREATE INDEX IF NOT EXISTS idx_role_perms_permission ON core.role_permissions(permission_id);

-- ----------------------------------------------------------------------------
-- TABLE: core.users
-- Description: Core user accounts table
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS core.users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    firstname VARCHAR(100),
    lastname VARCHAR(100),
    role_id INTEGER REFERENCES core.roles(role_id) ON DELETE RESTRICT,
    language VARCHAR(10) DEFAULT 'de',
    timezone VARCHAR(50) DEFAULT 'Europe/Berlin',
    theme_preference VARCHAR(10) DEFAULT 'dark' CHECK (theme_preference IN ('system', 'light', 'dark')),
    avatar_url VARCHAR(500),
    email_verified BOOLEAN DEFAULT FALSE,
    email_verified_at TIMESTAMPTZ,
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    two_factor_secret VARCHAR(255),
    last_login TIMESTAMPTZ,
    last_login_ip INET,
    status VARCHAR(20) DEFAULT 'active',
    banned_until TIMESTAMPTZ,
    creator_verified BOOLEAN DEFAULT FALSE,
    creator_verified_at TIMESTAMPTZ,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_user_status CHECK (status IN ('active', 'inactive', 'suspended', 'banned', 'deleted'))
);

CREATE INDEX IF NOT EXISTS idx_users_email ON core.users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON core.users(role_id);
CREATE INDEX IF NOT EXISTS idx_users_status ON core.users(status) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS idx_users_created ON core.users(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_users_language ON core.users(language);

COMMENT ON TABLE core.users IS 'Core user accounts with role-based access';
COMMENT ON COLUMN core.users.status IS 'User account status: active, inactive, suspended, banned, deleted';
COMMENT ON COLUMN core.users.theme_preference IS 'UI theme preference: system, light, dark';

-- ----------------------------------------------------------------------------
-- TABLE: core.user_sessions
-- Description: Active user sessions for JWT token management
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS core.user_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES core.users(user_id) ON DELETE CASCADE,
    jti VARCHAR(255) UNIQUE NOT NULL,
    refresh_token_hash VARCHAR(255),
    ip_address INET,
    user_agent TEXT,
    device_info JSONB,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked BOOLEAN DEFAULT FALSE,
    revoked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sessions_user ON core.user_sessions(user_id) WHERE revoked = FALSE;
CREATE INDEX IF NOT EXISTS idx_sessions_jti ON core.user_sessions(jti);
CREATE INDEX IF NOT EXISTS idx_sessions_expires ON core.user_sessions(expires_at) WHERE revoked = FALSE;
CREATE INDEX IF NOT EXISTS idx_sessions_revoked ON core.user_sessions(revoked);

COMMENT ON TABLE core.user_sessions IS 'Active user sessions and JWT tokens';

-- ----------------------------------------------------------------------------
-- TABLE: core.user_preferences
-- Description: User-specific preferences and settings
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS core.user_preferences (
    preference_id SERIAL PRIMARY KEY,
    user_id UUID UNIQUE REFERENCES core.users(user_id) ON DELETE CASCADE,
    notifications_enabled BOOLEAN DEFAULT TRUE,
    email_notifications BOOLEAN DEFAULT TRUE,
    marketing_emails BOOLEAN DEFAULT FALSE,
    data_sharing BOOLEAN DEFAULT FALSE,
    accessibility_settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_prefs_user ON core.user_preferences(user_id);

COMMENT ON TABLE core.user_preferences IS 'User-specific preferences and settings';

-- ----------------------------------------------------------------------------
-- TABLE: core.audit_logs
-- Note: Full audit_logs table definition moved to 006_audit_logging.sql
-- This ensures proper organization_id foreign key after organizations table exists
-- ----------------------------------------------------------------------------

-- ----------------------------------------------------------------------------
-- TABLE: core.system_settings
-- Note: Full system_settings table definition moved to 007_system_settings.sql
-- This ensures proper schema consistency across migrations
-- ----------------------------------------------------------------------------

-- ============================================================================
-- VERIFICATION
-- ============================================================================

DO $$
DECLARE
    schema_count INT;
    table_count INT;
BEGIN
    -- Count schemas created
    SELECT COUNT(*) INTO schema_count
    FROM information_schema.schemata
    WHERE schema_name IN (
        'core', 'organisations', 'courses', 'learning_methods',
        'assessments', 'ai_pipeline', 'liveroom', 'analytics',
        'smart_agents', 'support_systems', 'billing_storage', 'translations'
    );

    -- Count core tables created
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_schema = 'core';

    RAISE NOTICE '======================================';
    RAISE NOTICE 'Migration 001 Complete:';
    RAISE NOTICE '======================================';
    RAISE NOTICE '  PostgreSQL Schemas: %', schema_count;
    RAISE NOTICE '  Core Tables Created: %', table_count;
    RAISE NOTICE '======================================';

    IF schema_count = 12 THEN
        RAISE NOTICE '✓ All 12 schemas created successfully';
    ELSE
        RAISE WARNING '⚠ Only % of 12 schemas created', schema_count;
    END IF;

    IF table_count >= 7 THEN
        RAISE NOTICE '✓ Core tables created successfully';
    ELSE
        RAISE WARNING '⚠ Only % core tables created', table_count;
    END IF;
END $$;

COMMIT;

-- ============================================================================
-- END Migration 001
-- ============================================================================
