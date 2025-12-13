-- ============================================================================
-- Migration: 001_core_users_roles.sql
-- Description: Core user management, roles, and permissions tables
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-01-17
-- ============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- TABLE: roles
-- Description: System roles (9 predefined roles)
-- ============================================================================
CREATE TABLE IF NOT EXISTS roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    hierarchy_level INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_role_hierarchy CHECK (hierarchy_level BETWEEN 1 AND 9)
);

CREATE INDEX IF NOT EXISTS idx_roles_name ON roles(role_name);
CREATE INDEX IF NOT EXISTS idx_roles_hierarchy ON roles(hierarchy_level);

COMMENT ON TABLE roles IS 'System roles for LSX: free, premium, creator, teacher, school_admin, company_admin, support, moderator, admin';

-- Seed standard roles
INSERT INTO roles (role_name, display_name, description, hierarchy_level) VALUES
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

-- ============================================================================
-- TABLE: permissions
-- Description: Granular permissions for role-based access control
-- ============================================================================
CREATE TABLE IF NOT EXISTS permissions (
    permission_id SERIAL PRIMARY KEY,
    permission_key VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    module VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_permissions_key ON permissions(permission_key);
CREATE INDEX IF NOT EXISTS idx_permissions_module ON permissions(module);

COMMENT ON TABLE permissions IS 'Granular permissions for RBAC system';

-- ============================================================================
-- TABLE: role_permissions
-- Description: Many-to-many relationship between roles and permissions
-- ============================================================================
CREATE TABLE IF NOT EXISTS role_permissions (
    role_id INTEGER REFERENCES roles(role_id) ON DELETE CASCADE,
    permission_id INTEGER REFERENCES permissions(permission_id) ON DELETE CASCADE,
    granted_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (role_id, permission_id)
);

CREATE INDEX IF NOT EXISTS idx_role_perms_role ON role_permissions(role_id);
CREATE INDEX IF NOT EXISTS idx_role_perms_permission ON role_permissions(permission_id);

-- ============================================================================
-- TABLE: users
-- Description: Core user accounts table
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    firstname VARCHAR(100),
    lastname VARCHAR(100),
    role_id INTEGER REFERENCES roles(role_id) ON DELETE RESTRICT,
    language VARCHAR(10) DEFAULT 'de',
    timezone VARCHAR(50) DEFAULT 'Europe/Berlin',
    avatar_url VARCHAR(500),
    email_verified BOOLEAN DEFAULT FALSE,
    email_verified_at TIMESTAMPTZ,
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    two_factor_secret VARCHAR(255),
    last_login TIMESTAMPTZ,
    last_login_ip INET,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_user_status CHECK (status IN ('active', 'suspended', 'banned', 'deleted'))
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role_id);
CREATE INDEX IF NOT EXISTS idx_users_status ON users(status) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS idx_users_created ON users(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_users_language ON users(language);

COMMENT ON TABLE users IS 'Core user accounts with role-based access';
COMMENT ON COLUMN users.status IS 'User account status: active, suspended, banned, deleted';

-- ============================================================================
-- TABLE: user_sessions
-- Description: Active user sessions for JWT token management
-- ============================================================================
CREATE TABLE IF NOT EXISTS user_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
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

CREATE INDEX IF NOT EXISTS idx_sessions_user ON user_sessions(user_id) WHERE revoked = FALSE;
CREATE INDEX IF NOT EXISTS idx_sessions_jti ON user_sessions(jti);
CREATE INDEX IF NOT EXISTS idx_sessions_expires ON user_sessions(expires_at) WHERE revoked = FALSE;
CREATE INDEX IF NOT EXISTS idx_sessions_revoked ON user_sessions(revoked);

COMMENT ON TABLE user_sessions IS 'Active user sessions and JWT tokens';

-- ============================================================================
-- TABLE: recovery_codes
-- Description: Account recovery codes (one-time use)
-- ============================================================================
CREATE TABLE IF NOT EXISTS recovery_codes (
    code_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    code_hash VARCHAR(255) NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    used_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '1 year')
);

CREATE INDEX IF NOT EXISTS idx_recovery_user ON recovery_codes(user_id);
CREATE INDEX IF NOT EXISTS idx_recovery_used ON recovery_codes(used) WHERE used = FALSE;
CREATE INDEX IF NOT EXISTS idx_recovery_expires ON recovery_codes(expires_at) WHERE used = FALSE;

COMMENT ON TABLE recovery_codes IS 'One-time recovery codes for account access';

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_roles_updated_at BEFORE UPDATE ON roles
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- End of Migration: 001_core_users_roles.sql
-- ============================================================================
