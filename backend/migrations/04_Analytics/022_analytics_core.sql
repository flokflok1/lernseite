-- ============================================================================
-- Migration: 022_analytics_core.sql
-- Description: Core analytics tables
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-01-17
-- ============================================================================

-- ============================================================================
-- TABLE: analytics_sessions
-- Description: User session tracking
-- ============================================================================
CREATE TABLE IF NOT EXISTS analytics_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(organization_id) ON DELETE SET NULL,
    session_token VARCHAR(255),
    ip_address_hash VARCHAR(255),
    user_agent TEXT,
    device_type VARCHAR(50),
    browser VARCHAR(100),
    os VARCHAR(100),
    country VARCHAR(2),
    city VARCHAR(100),
    started_at TIMESTAMPTZ DEFAULT NOW(),
    last_activity_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    duration_seconds INTEGER,
    page_views INTEGER DEFAULT 0,
    CONSTRAINT chk_analytics_device CHECK (device_type IN ('desktop', 'mobile', 'tablet', 'unknown'))
);

CREATE INDEX IF NOT EXISTS idx_analytics_sessions_user ON analytics_sessions(user_id, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_analytics_sessions_org ON analytics_sessions(organization_id, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_analytics_sessions_started ON analytics_sessions(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_analytics_sessions_device ON analytics_sessions(device_type);

COMMENT ON TABLE analytics_sessions IS 'User session tracking for analytics';

-- ============================================================================
-- TABLE: analytics_aggregates
-- Description: Pre-aggregated analytics data for fast queries
-- ============================================================================
CREATE TABLE IF NOT EXISTS analytics_aggregates (
    aggregate_id BIGSERIAL PRIMARY KEY,
    metric_type VARCHAR(100) NOT NULL,
    dimension VARCHAR(100),
    dimension_value VARCHAR(255),
    date DATE NOT NULL,
    hour INTEGER,
    value DECIMAL(15,2) NOT NULL,
    count INTEGER DEFAULT 1,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_analytics_hour CHECK (hour IS NULL OR (hour >= 0 AND hour <= 23))
);

CREATE INDEX IF NOT EXISTS idx_analytics_agg_metric ON analytics_aggregates(metric_type, date DESC);
CREATE INDEX IF NOT EXISTS idx_analytics_agg_dimension ON analytics_aggregates(dimension, dimension_value, date DESC);
CREATE INDEX IF NOT EXISTS idx_analytics_agg_date ON analytics_aggregates(date DESC, hour);

COMMENT ON TABLE analytics_aggregates IS 'Pre-aggregated analytics for dashboards (daily/hourly)';

-- ============================================================================
-- End of Migration: 022_analytics_core.sql
-- ============================================================================
