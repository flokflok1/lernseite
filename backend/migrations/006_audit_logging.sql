-- ============================================================================
-- Migration: 006_audit_logging.sql
-- Description: Comprehensive audit logging system
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-01-17
-- ============================================================================

-- ============================================================================
-- TABLE: audit_logs
-- Description: General audit trail for all system operations
-- ============================================================================
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id BIGSERIAL PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    organization_id UUID REFERENCES organizations(organization_id) ON DELETE SET NULL,
    resource_type VARCHAR(100),
    resource_id VARCHAR(255),
    action VARCHAR(50) NOT NULL,
    severity VARCHAR(20) DEFAULT 'info',
    ip_address INET,
    user_agent TEXT,
    changes JSONB,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_audit_action CHECK (action IN ('create', 'read', 'update', 'delete', 'login', 'logout', 'access_denied')),
    CONSTRAINT chk_audit_severity CHECK (severity IN ('debug', 'info', 'warning', 'error', 'critical'))
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_org ON audit_logs(organization_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_event ON audit_logs(event_type, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_severity ON audit_logs(severity, created_at DESC) WHERE severity IN ('error', 'critical');
CREATE INDEX IF NOT EXISTS idx_audit_logs_time ON audit_logs(created_at DESC);

COMMENT ON TABLE audit_logs IS 'Comprehensive audit trail for compliance and security monitoring';

-- ============================================================================
-- TABLE: data_access_logs
-- Description: GDPR-compliant data access logging
-- ============================================================================
CREATE TABLE IF NOT EXISTS data_access_logs (
    access_id BIGSERIAL PRIMARY KEY,
    accessed_by UUID REFERENCES users(user_id) ON DELETE SET NULL,
    accessed_user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    access_type VARCHAR(50) NOT NULL,
    data_category VARCHAR(100),
    purpose VARCHAR(255),
    ip_address INET,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_data_access_type CHECK (access_type IN ('view', 'export', 'modification', 'deletion', 'anonymization'))
);

CREATE INDEX IF NOT EXISTS idx_data_access_by ON data_access_logs(accessed_by, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_data_access_user ON data_access_logs(accessed_user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_data_access_type ON data_access_logs(access_type);
CREATE INDEX IF NOT EXISTS idx_data_access_time ON data_access_logs(created_at DESC);

COMMENT ON TABLE data_access_logs IS 'GDPR-compliant logging of personal data access';

-- ============================================================================
-- TABLE: change_history
-- Description: Detailed change tracking for important entities
-- ============================================================================
CREATE TABLE IF NOT EXISTS change_history (
    change_id BIGSERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id VARCHAR(255) NOT NULL,
    operation VARCHAR(20) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    changed_by UUID REFERENCES users(user_id) ON DELETE SET NULL,
    changed_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_change_operation CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE'))
);

CREATE INDEX IF NOT EXISTS idx_change_history_table ON change_history(table_name, record_id);
CREATE INDEX IF NOT EXISTS idx_change_history_user ON change_history(changed_by, changed_at DESC);
CREATE INDEX IF NOT EXISTS idx_change_history_operation ON change_history(operation, changed_at DESC);
CREATE INDEX IF NOT EXISTS idx_change_history_time ON change_history(changed_at DESC);

COMMENT ON TABLE change_history IS 'Detailed change tracking for version control and audit';

-- ============================================================================
-- End of Migration: 006_audit_logging.sql
-- ============================================================================
