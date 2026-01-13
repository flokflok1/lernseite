-- ==========================================
-- LernsystemX - Audit Log Schema
-- Phase 20: Security Architecture & Hardening
-- ==========================================
--
-- Based on Dok 31 (Security Architecture)
-- ISO 27001:2013 compliant - Audit Logging
-- DSGVO/GDPR compliant - Activity Tracking
--
-- This migration creates the audit_logs table for security event tracking.
-- Tracks: authentication, authorization, data access, modifications, admin actions
--
-- Run this after initial database setup
-- ==========================================

-- Create audit_logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    -- Primary Key
    log_id BIGSERIAL PRIMARY KEY,

    -- Timestamp
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Event Information
    event_type VARCHAR(50) NOT NULL,  -- e.g., 'login', 'logout', 'create', 'update', 'delete', 'permission_denied'
    event_category VARCHAR(50) NOT NULL,  -- e.g., 'authentication', 'authorization', 'data_access', 'admin_action'
    severity VARCHAR(20) NOT NULL DEFAULT 'info',  -- 'debug', 'info', 'warning', 'error', 'critical'

    -- User Information
    user_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,  -- NULL for anonymous/failed login attempts
    user_email VARCHAR(255),  -- Denormalized for failed logins where user_id is NULL
    user_role VARCHAR(50),

    -- Session & Request Information
    session_id VARCHAR(255),  -- JWT jti or session ID
    ip_address INET,  -- Client IP address
    user_agent TEXT,  -- Browser/client user agent

    -- Resource Information
    resource_type VARCHAR(100),  -- e.g., 'user', 'course', 'organisation', 'subscription'
    resource_id VARCHAR(100),  -- ID of affected resource

    -- Action Details
    action VARCHAR(100) NOT NULL,  -- e.g., 'login_success', 'login_failed', 'user_created', 'permission_denied'
    description TEXT,  -- Human-readable description

    -- Additional Context (JSON)
    metadata JSONB,  -- Additional event-specific data (sanitized, no passwords!)

    -- Result
    success BOOLEAN NOT NULL DEFAULT true,  -- Whether action succeeded
    error_message TEXT,  -- Error message if failed

    -- Retention & Compliance
    retained_until DATE  -- Auto-deletion date based on retention policy
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_audit_logs_event_type ON audit_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_event_category ON audit_logs(event_category);
CREATE INDEX IF NOT EXISTS idx_audit_logs_severity ON audit_logs(severity);
CREATE INDEX IF NOT EXISTS idx_audit_logs_ip_address ON audit_logs(ip_address);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_session_id ON audit_logs(session_id) WHERE session_id IS NOT NULL;

-- Composite index for common queries
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_created ON audit_logs(user_id, created_at DESC) WHERE user_id IS NOT NULL;

-- Partial index for failed events
CREATE INDEX IF NOT EXISTS idx_audit_logs_failures ON audit_logs(created_at DESC, event_type, user_email)
    WHERE success = false;

-- GIN index for JSONB metadata searches
CREATE INDEX IF NOT EXISTS idx_audit_logs_metadata ON audit_logs USING GIN(metadata);

-- Comment on table
COMMENT ON TABLE audit_logs IS 'Security audit log for tracking all security-relevant events';
COMMENT ON COLUMN audit_logs.event_type IS 'Type of event: login, logout, create, update, delete, permission_denied, etc.';
COMMENT ON COLUMN audit_logs.event_category IS 'Category: authentication, authorization, data_access, admin_action, system';
COMMENT ON COLUMN audit_logs.severity IS 'Log level: debug, info, warning, error, critical';
COMMENT ON COLUMN audit_logs.metadata IS 'Additional context (JSON) - MUST be sanitized, no sensitive data!';
COMMENT ON COLUMN audit_logs.retained_until IS 'Auto-deletion date based on AUDIT_LOG_RETENTION_DAYS config';

-- ==========================================
-- RETENTION POLICY FUNCTION
-- ==========================================
-- Automatically set retained_until based on config (365 days default)

CREATE OR REPLACE FUNCTION set_audit_log_retention()
RETURNS TRIGGER AS $$
BEGIN
    -- Set retention date to 365 days from creation (configurable via app)
    NEW.retained_until := (NEW.created_at + INTERVAL '365 days')::DATE;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically set retention date
DROP TRIGGER IF EXISTS trg_set_audit_log_retention ON audit_logs;
CREATE TRIGGER trg_set_audit_log_retention
    BEFORE INSERT ON audit_logs
    FOR EACH ROW
    EXECUTE FUNCTION set_audit_log_retention();

-- ==========================================
-- CLEANUP FUNCTION (Run via cron/Celery)
-- ==========================================
-- Function to delete expired audit logs

CREATE OR REPLACE FUNCTION cleanup_expired_audit_logs()
RETURNS TABLE(deleted_count BIGINT) AS $$
DECLARE
    rows_deleted BIGINT;
BEGIN
    DELETE FROM audit_logs
    WHERE retained_until < CURRENT_DATE;

    GET DIAGNOSTICS rows_deleted = ROW_COUNT;
    RETURN QUERY SELECT rows_deleted;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION cleanup_expired_audit_logs IS 'Delete audit logs past their retention date. Run daily via Celery task.';

-- ==========================================
-- EXAMPLE QUERIES
-- ==========================================

-- Get recent failed login attempts
-- SELECT * FROM audit_logs
-- WHERE event_type = 'login' AND success = false
-- ORDER BY created_at DESC LIMIT 100;

-- Get all actions by a specific user
-- SELECT * FROM audit_logs
-- WHERE user_id = 123
-- ORDER BY created_at DESC;

-- Get permission denied events
-- SELECT * FROM audit_logs
-- WHERE event_type = 'permission_denied'
-- ORDER BY created_at DESC;

-- Get admin actions
-- SELECT * FROM audit_logs
-- WHERE event_category = 'admin_action'
-- ORDER BY created_at DESC;

-- Get failed events by IP
-- SELECT ip_address, COUNT(*) as failure_count, MAX(created_at) as last_failure
-- FROM audit_logs
-- WHERE success = false AND created_at > NOW() - INTERVAL '1 hour'
-- GROUP BY ip_address
-- ORDER BY failure_count DESC;
