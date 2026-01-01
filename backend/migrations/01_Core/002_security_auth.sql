-- ============================================================================
-- Migration: 002_security_auth.sql
-- Description: Security and authentication tables (login attempts, 2FA, etc.)
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-01-17
-- ============================================================================

-- ============================================================================
-- TABLE: login_attempts
-- Description: Track login attempts for brute force protection
-- ============================================================================
CREATE TABLE IF NOT EXISTS login_attempts (
    attempt_id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    ip_address INET NOT NULL,
    user_agent TEXT,
    success BOOLEAN DEFAULT FALSE,
    failure_reason VARCHAR(100),
    attempted_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_login_attempts_email ON login_attempts(email, attempted_at DESC);
CREATE INDEX IF NOT EXISTS idx_login_attempts_ip ON login_attempts(ip_address, attempted_at DESC);
CREATE INDEX IF NOT EXISTS idx_login_attempts_time ON login_attempts(attempted_at DESC);
CREATE INDEX IF NOT EXISTS idx_login_attempts_failed ON login_attempts(success) WHERE success = FALSE;

COMMENT ON TABLE login_attempts IS 'Login attempt tracking for security monitoring and brute force protection';

-- ============================================================================
-- TABLE: two_factor_backups
-- Description: Backup codes for 2FA recovery
-- ============================================================================
CREATE TABLE IF NOT EXISTS two_factor_backups (
    backup_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    code_hash VARCHAR(255) NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    used_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_2fa_backups_user ON two_factor_backups(user_id);
CREATE INDEX IF NOT EXISTS idx_2fa_backups_unused ON two_factor_backups(user_id, used) WHERE used = FALSE;

COMMENT ON TABLE two_factor_backups IS 'Backup codes for 2FA recovery (typically 10 codes per user)';

-- ============================================================================
-- TABLE: password_reset_tokens
-- Description: Temporary tokens for password reset
-- ============================================================================
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    token_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    used_at TIMESTAMPTZ,
    ip_address INET,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_reset_tokens_user ON password_reset_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_reset_tokens_expires ON password_reset_tokens(expires_at) WHERE used = FALSE;
CREATE INDEX IF NOT EXISTS idx_reset_tokens_hash ON password_reset_tokens(token_hash) WHERE used = FALSE;

COMMENT ON TABLE password_reset_tokens IS 'Temporary tokens for password reset (15-minute expiry)';

-- ============================================================================
-- TABLE: email_verification_tokens
-- Description: Tokens for email verification
-- ============================================================================
CREATE TABLE IF NOT EXISTS email_verification_tokens (
    token_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    verified BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_email_verify_user ON email_verification_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_email_verify_hash ON email_verification_tokens(token_hash) WHERE verified = FALSE;
CREATE INDEX IF NOT EXISTS idx_email_verify_expires ON email_verification_tokens(expires_at) WHERE verified = FALSE;

COMMENT ON TABLE email_verification_tokens IS 'Email verification tokens (24-hour expiry)';

-- ============================================================================
-- TABLE: security_audit_logs
-- Description: Security-specific audit trail
-- ============================================================================
CREATE TABLE IF NOT EXISTS security_audit_logs (
    log_id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    event_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    ip_address INET,
    user_agent TEXT,
    details JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_severity CHECK (severity IN ('info', 'warning', 'error', 'critical'))
);

CREATE INDEX IF NOT EXISTS idx_security_audit_user ON security_audit_logs(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_security_audit_type ON security_audit_logs(event_type, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_security_audit_severity ON security_audit_logs(severity, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_security_audit_time ON security_audit_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_security_audit_ip ON security_audit_logs(ip_address, created_at DESC);

COMMENT ON TABLE security_audit_logs IS 'Security-specific audit trail for sensitive operations';

-- ============================================================================
-- TABLE: blocked_ips
-- Description: IP addresses blocked due to suspicious activity
-- ============================================================================
CREATE TABLE IF NOT EXISTS blocked_ips (
    block_id BIGSERIAL PRIMARY KEY,
    ip_address INET UNIQUE NOT NULL,
    reason TEXT,
    blocked_by UUID REFERENCES users(user_id) ON DELETE SET NULL,
    blocked_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    permanent BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_blocked_ips_address ON blocked_ips(ip_address);
CREATE INDEX IF NOT EXISTS idx_blocked_ips_expires ON blocked_ips(expires_at) WHERE permanent = FALSE;
CREATE INDEX IF NOT EXISTS idx_blocked_ips_permanent ON blocked_ips(permanent);

COMMENT ON TABLE blocked_ips IS 'IP addresses blocked due to brute force attempts or suspicious activity';

-- ============================================================================
-- End of Migration: 002_security_auth.sql
-- ============================================================================
