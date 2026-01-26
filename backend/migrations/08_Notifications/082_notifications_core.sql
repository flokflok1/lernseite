-- ============================================================================
-- Migration: 028_notifications_core.sql
-- Version: 1.0.0
-- Description: Database migration
-- Author: LernsystemX Migration System
-- Date: 2026-01-02
-- ============================================================================

CREATE TABLE IF NOT EXISTS support_systems.notifications (
    notification_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES core.users(user_id) ON DELETE CASCADE,
    notification_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    action_url VARCHAR(500),
    icon VARCHAR(100),
    priority VARCHAR(20) DEFAULT 'normal',
    read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMPTZ,
    data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    CONSTRAINT chk_notification_type CHECK (notification_type IN ('system', 'course', 'exam', 'achievement', 'message', 'reminder', 'alert', 'announcement')),
    CONSTRAINT chk_notification_priority CHECK (priority IN ('low', 'normal', 'high', 'urgent'))
);

CREATE INDEX IF NOT EXISTS idx_notifications_user ON support_systems.notifications(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_notifications_type ON support_systems.notifications(notification_type);
CREATE INDEX IF NOT EXISTS idx_notifications_unread ON support_systems.notifications(user_id, read) WHERE read = FALSE;
CREATE INDEX IF NOT EXISTS idx_notifications_expires ON support_systems.notifications(expires_at) WHERE expires_at IS NOT NULL;

COMMENT ON TABLE support_systems.notifications IS 'In-app user notifications';

-- ============================================================================
-- TABLE: notification_preferences
-- Description: User notification preferences
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_systems.notification_preferences (
    preference_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES core.users(user_id) ON DELETE CASCADE,
    notification_type VARCHAR(50) NOT NULL,
    channel VARCHAR(20) NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    frequency VARCHAR(20) DEFAULT 'realtime',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_notif_pref_channel CHECK (channel IN ('email', 'push', 'sms', 'in_app')),
    CONSTRAINT chk_notif_pref_frequency CHECK (frequency IN ('realtime', 'hourly', 'daily', 'weekly', 'never')),
    UNIQUE (user_id, notification_type, channel)
);

CREATE INDEX IF NOT EXISTS idx_notif_prefs_user ON support_systems.notification_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_notif_prefs_type ON support_systems.notification_preferences(notification_type, enabled);

COMMENT ON TABLE support_systems.notification_preferences IS 'User preferences for notification delivery';

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- ============================================================================
DROP TRIGGER IF EXISTS update_notif_prefs_updated_at ON support_systems.notification_preferences;
CREATE TRIGGER update_notif_prefs_updated_at BEFORE UPDATE ON support_systems.notification_preferences
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- End of Migration: 028_notifications_core.sql
-- ============================================================================
