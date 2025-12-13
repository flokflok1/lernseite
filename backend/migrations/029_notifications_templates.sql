-- ============================================================================
-- Migration: 029_notifications_templates.sql
-- Description: Notification templates and channels
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-01-17
-- ============================================================================

-- ============================================================================
-- TABLE: notification_templates
-- Description: Reusable notification templates
-- ============================================================================
CREATE TABLE IF NOT EXISTS notification_templates (
    template_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_key VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    notification_type VARCHAR(50) NOT NULL,
    subject_template TEXT,
    body_template TEXT NOT NULL,
    html_template TEXT,
    variables JSONB,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_notif_templates_key ON notification_templates(template_key);
CREATE INDEX IF NOT EXISTS idx_notif_templates_type ON notification_templates(notification_type);
CREATE INDEX IF NOT EXISTS idx_notif_templates_active ON notification_templates(active) WHERE active = TRUE;

COMMENT ON TABLE notification_templates IS 'Reusable templates for email, push, SMS notifications';
COMMENT ON COLUMN notification_templates.variables IS 'JSONB array of variable names used in templates';

-- ============================================================================
-- TABLE: notification_channels
-- Description: Notification delivery channels configuration
-- ============================================================================
CREATE TABLE IF NOT EXISTS notification_channels (
    channel_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    channel_type VARCHAR(20) NOT NULL,
    name VARCHAR(255) NOT NULL,
    provider VARCHAR(100),
    config JSONB NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_notif_channel_type CHECK (channel_type IN ('email', 'sms', 'push', 'webhook', 'slack', 'teams')),
    UNIQUE (channel_type, name)
);

CREATE INDEX IF NOT EXISTS idx_notif_channels_type ON notification_channels(channel_type);
CREATE INDEX IF NOT EXISTS idx_notif_channels_active ON notification_channels(active, priority DESC);

COMMENT ON TABLE notification_channels IS 'Notification delivery channel configurations';

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- ============================================================================
CREATE TRIGGER update_notif_templates_updated_at BEFORE UPDATE ON notification_templates
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_notif_channels_updated_at BEFORE UPDATE ON notification_channels
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- End of Migration: 029_notifications_templates.sql
-- ============================================================================
