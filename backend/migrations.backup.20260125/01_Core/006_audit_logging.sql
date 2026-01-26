-- ============================================================================
-- Migration: 006_audit_logging.sql
-- Version: 1.0.0
-- Description: Database migration
-- Author: LernsystemX Migration System
-- Date: 2026-01-02
-- ============================================================================

-- Drop old versions of tables if they exist (e.g., from old Migration 001 without organization_id)
DROP TABLE IF EXISTS core.audit_logs CASCADE;
DROP TABLE IF EXISTS core.data_access_logs CASCADE;
DROP TABLE IF EXISTS core.change_history CASCADE;

CREATE TABLE IF NOT EXISTS core.audit_logs (
    log_id BIGSERIAL PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    user_id UUID REFERENCES core.users(user_id) ON DELETE SET NULL,
    organization_id UUID REFERENCES organisations.organisations(organization_id) ON DELETE SET NULL,
    resource_type VARCHAR(100),
    resource_id VARCHAR(255),
    action VARCHAR(50) NOT NULL,
    severity VARCHAR(20) DEFAULT 'info',
    ip_address INET,
    user_agent TEXT,
    changes JSONB,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    -- Extended fields (merged from 043)
    event_category VARCHAR(50),
    user_email VARCHAR(255),
    user_role VARCHAR(50),
    session_id VARCHAR(255),
    description TEXT,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    -- No action constraint (allows admin.* actions)
    CONSTRAINT chk_audit_severity CHECK (severity IN ('debug', 'info', 'warning', 'error', 'critical'))
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON core.audit_logs(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_org ON core.audit_logs(organization_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_event ON core.audit_logs(event_type, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource ON core.audit_logs(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON core.audit_logs(action, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_severity ON core.audit_logs(severity, created_at DESC) WHERE severity IN ('error', 'critical');
CREATE INDEX IF NOT EXISTS idx_audit_logs_time ON core.audit_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_event_category ON core.audit_logs(event_category, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_email ON core.audit_logs(user_email, created_at DESC) WHERE user_email IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_audit_logs_session ON core.audit_logs(session_id) WHERE session_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_audit_logs_success ON core.audit_logs(success, created_at DESC) WHERE success = FALSE;

COMMENT ON TABLE core.audit_logs IS 'Comprehensive audit trail for compliance and security monitoring';

-- ============================================================================
-- TABLE: data_access_logs
-- Description: GDPR-compliant data access logging
-- ============================================================================
CREATE TABLE IF NOT EXISTS core.data_access_logs (
    access_id BIGSERIAL PRIMARY KEY,
    accessed_by UUID REFERENCES core.users(user_id) ON DELETE SET NULL,
    accessed_user_id UUID REFERENCES core.users(user_id) ON DELETE CASCADE,
    access_type VARCHAR(50) NOT NULL,
    data_category VARCHAR(100),
    purpose VARCHAR(255),
    ip_address INET,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_data_access_type CHECK (access_type IN ('view', 'export', 'modification', 'deletion', 'anonymization'))
);

CREATE INDEX IF NOT EXISTS idx_data_access_by ON core.data_access_logs(accessed_by, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_data_access_user ON core.data_access_logs(accessed_user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_data_access_type ON core.data_access_logs(access_type);
CREATE INDEX IF NOT EXISTS idx_data_access_time ON core.data_access_logs(created_at DESC);

COMMENT ON TABLE core.data_access_logs IS 'GDPR-compliant logging of personal data access';

-- ============================================================================
-- TABLE: change_history
-- Description: Detailed change tracking for important entities
-- ============================================================================
CREATE TABLE IF NOT EXISTS core.change_history (
    change_id BIGSERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id VARCHAR(255) NOT NULL,
    operation VARCHAR(20) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    changed_by UUID REFERENCES core.users(user_id) ON DELETE SET NULL,
    changed_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_change_operation CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE'))
);

CREATE INDEX IF NOT EXISTS idx_change_history_table ON core.change_history(table_name, record_id);
CREATE INDEX IF NOT EXISTS idx_change_history_user ON core.change_history(changed_by, changed_at DESC);
CREATE INDEX IF NOT EXISTS idx_change_history_operation ON core.change_history(operation, changed_at DESC);
CREATE INDEX IF NOT EXISTS idx_change_history_time ON core.change_history(changed_at DESC);

COMMENT ON TABLE core.change_history IS 'Detailed change tracking for version control and audit';

-- ============================================================================
-- End of Migration: 006_audit_logging.sql
-- ============================================================================
