-- ============================================================================
-- Migration: 023_analytics_events.sql
-- Version: 1.0.0
-- Description: Database migration
-- Author: LernsystemX Migration System
-- Date: 2026-01-02
-- ============================================================================

CREATE TABLE IF NOT EXISTS analytics.analytics_events (
    event_id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES core.users(user_id) ON DELETE CASCADE,
    organisation_id UUID REFERENCES organisations.organisations(organisation_id) ON DELETE SET NULL,
    session_id UUID REFERENCES analytics.analytics_sessions(session_id) ON DELETE SET NULL,
    event_type VARCHAR(100) NOT NULL,
    event_category VARCHAR(50),
    resource_type VARCHAR(100),
    resource_id VARCHAR(255),
    payload JSONB,
    ip_address_hash VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_analytics_event_type CHECK (event_type IN (
        'page_view', 'login', 'logout', 'signup',
        'course_view', 'course_enroll', 'course_complete',
        'chapter_start', 'chapter_complete',
        'lesson_start', 'lesson_complete',
        'method_execute', 'method_complete',
        'exam_start', 'exam_complete',
        'liveroom_join', 'liveroom_leave',
        'ai_request', 'purchase', 'subscription_start'
    ))
);

CREATE INDEX IF NOT EXISTS idx_analytics_events_user ON analytics.analytics_events(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analytics_events_org ON analytics.analytics_events(organisation_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analytics_events_session ON analytics.analytics_events(session_id);
CREATE INDEX IF NOT EXISTS idx_analytics_events_type ON analytics.analytics_events(event_type, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analytics_events_category ON analytics.analytics_events(event_category, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analytics_events_resource ON analytics.analytics_events(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_analytics_events_created ON analytics.analytics_events(created_at DESC);

COMMENT ON TABLE analytics.analytics_events IS 'Granular event tracking for user actions and system events';

-- ============================================================================
-- End of Migration: 023_analytics_events.sql
-- ============================================================================
