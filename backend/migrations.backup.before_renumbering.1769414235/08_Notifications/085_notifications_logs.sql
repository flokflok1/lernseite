-- ============================================================================
-- Migration: 030_notifications_logs.sql
-- Version: 1.0.0
-- Description: Database migration
-- Author: LernsystemX Migration System
-- Date: 2026-01-02
-- ============================================================================

CREATE TABLE IF NOT EXISTS notifications.notification_logs (
    log_id BIGSERIAL PRIMARY KEY,
    notification_id UUID REFERENCES support_systems.notifications(notification_id) ON DELETE CASCADE,
    user_id UUID REFERENCES core.users(user_id) ON DELETE CASCADE,
    channel_type VARCHAR(20) NOT NULL,
    template_id UUID REFERENCES notifications.notification_templates(template_id) ON DELETE SET NULL,
    status VARCHAR(20) NOT NULL,
    recipient VARCHAR(255),
    subject TEXT,
    sent_at TIMESTAMPTZ DEFAULT NOW(),
    delivered_at TIMESTAMPTZ,
    opened_at TIMESTAMPTZ,
    clicked_at TIMESTAMPTZ,
    failed_at TIMESTAMPTZ,
    error_message TEXT,
    provider_message_id VARCHAR(255),
    metadata JSONB,
    CONSTRAINT chk_notif_log_channel CHECK (channel_type IN ('email', 'sms', 'push', 'webhook')),
    CONSTRAINT chk_notif_log_status CHECK (status IN ('queued', 'sent', 'delivered', 'opened', 'clicked', 'failed', 'bounced'))
);

CREATE INDEX IF NOT EXISTS idx_notif_logs_notification ON notifications.notification_logs(notification_id);
CREATE INDEX IF NOT EXISTS idx_notif_logs_user ON notifications.notification_logs(user_id, sent_at DESC);
CREATE INDEX IF NOT EXISTS idx_notif_logs_channel ON notifications.notification_logs(channel_type, status);
CREATE INDEX IF NOT EXISTS idx_notif_logs_status ON notifications.notification_logs(status, sent_at DESC);
CREATE INDEX IF NOT EXISTS idx_notif_logs_sent ON notifications.notification_logs(sent_at DESC);

COMMENT ON TABLE notifications.notification_logs IS 'Notification delivery tracking and analytics';

-- ============================================================================
-- TABLE: email_queue
-- Description: Email delivery queue
-- ============================================================================
CREATE TABLE IF NOT EXISTS email.email_queue (
    queue_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    to_email VARCHAR(255) NOT NULL,
    from_email VARCHAR(255),
    from_name VARCHAR(255),
    subject VARCHAR(500) NOT NULL,
    body_text TEXT,
    body_html TEXT,
    template_id UUID REFERENCES notifications.notification_templates(template_id) ON DELETE SET NULL,
    template_data JSONB,
    priority INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'queued',
    scheduled_for TIMESTAMPTZ,
    sent_at TIMESTAMPTZ,
    failed_at TIMESTAMPTZ,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_email_queue_status CHECK (status IN ('queued', 'sending', 'sent', 'failed', 'cancelled'))
);

CREATE INDEX IF NOT EXISTS idx_email_queue_status ON email.email_queue(status, priority DESC, created_at ASC);
CREATE INDEX IF NOT EXISTS idx_email_queue_scheduled ON email.email_queue(scheduled_for) WHERE status = 'queued';
CREATE INDEX IF NOT EXISTS idx_email_queue_to ON email.email_queue(to_email);

COMMENT ON TABLE email.email_queue IS 'Email delivery queue with retry logic';

-- ============================================================================
-- End of Migration: 030_notifications_logs.sql
-- ============================================================================
