-- ============================================================================
-- Migration: 097_feature_flags_advanced.sql
-- Description: Feature Flags System - Advanced Infrastructure
--              Cache tracking, enhanced auditing, configuration snapshots
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-01-18
-- ============================================================================
-- Part of Feature Flag System (Phase 2: Advanced Infrastructure)
--
-- Tables created:
-- - feature_flag_cache_status (cache invalidation tracking)
-- - feature_flag_audit_log_enhanced (enhanced audit with impact tracking)
-- - feature_flag_config_snapshots (configuration snapshots for rollback)
--
-- Requires: 095_feature_flags_core.sql (feature_flags table)
--           096_feature_flags_enterprise.sql (role/tier/rollout/ab_test tables)
-- ============================================================================

BEGIN;

-- =====================================================
-- 1. FEATURE CONFIGURATION CACHE TRACKING
-- =====================================================

CREATE TABLE IF NOT EXISTS feature_flag_cache_status (
    feature_name VARCHAR(100) PRIMARY KEY REFERENCES feature_flags(name) ON DELETE CASCADE,
    last_config_change TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cache_invalidated_at TIMESTAMP,
    cache_ttl_seconds INTEGER DEFAULT 300,
    requires_redis_pubsub BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_cache_status_invalidated ON feature_flag_cache_status(cache_invalidated_at);
CREATE INDEX idx_cache_status_requires_pubsub ON feature_flag_cache_status(requires_redis_pubsub) WHERE requires_redis_pubsub = TRUE;

COMMENT ON TABLE feature_flag_cache_status IS 'Track cache invalidation for Redis Pub/Sub events';

-- =====================================================
-- 2. ENHANCED AUDIT LOG WITH IMPACT TRACKING
-- =====================================================

CREATE TABLE IF NOT EXISTS feature_flag_audit_log_enhanced (
    id SERIAL PRIMARY KEY,
    feature_name VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    changed_field VARCHAR(100),
    old_value TEXT,
    new_value TEXT,
    change_details JSONB,
    user_id VARCHAR(36),
    user_email VARCHAR(255),
    organization_id VARCHAR(36),
    ip_address INET,
    user_agent TEXT,
    estimated_affected_users INTEGER,
    estimated_affected_organizations INTEGER,
    rollback_possible BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_action CHECK (action IN (
        'feature_created', 'feature_enabled', 'feature_disabled',
        'role_permission_added', 'role_permission_removed', 'role_quota_updated',
        'tier_limit_added', 'tier_limit_removed', 'tier_limit_updated',
        'org_override_added', 'org_override_removed', 'org_override_updated',
        'rollout_started', 'rollout_paused', 'rollout_completed', 'rollout_rolled_back',
        'rollout_phase_advanced', 'rollout_percentage_adjusted',
        'ab_test_started', 'ab_test_ended', 'ab_test_winner_announced',
        'segment_enabled', 'segment_disabled', 'segment_updated',
        'user_override_added', 'user_override_removed'
    ))
);

CREATE INDEX idx_audit_enhanced_feature ON feature_flag_audit_log_enhanced(feature_name);
CREATE INDEX idx_audit_enhanced_action ON feature_flag_audit_log_enhanced(action);
CREATE INDEX idx_audit_enhanced_user ON feature_flag_audit_log_enhanced(user_id);
CREATE INDEX idx_audit_enhanced_created ON feature_flag_audit_log_enhanced(created_at DESC);
CREATE INDEX idx_audit_enhanced_org ON feature_flag_audit_log_enhanced(organization_id);

COMMENT ON TABLE feature_flag_audit_log_enhanced IS 'Enhanced audit log with impact tracking for compliance';

-- =====================================================
-- 3. FEATURE CONFIGURATION SNAPSHOTS (For rollback)
-- =====================================================

CREATE TABLE IF NOT EXISTS feature_flag_config_snapshots (
    id SERIAL PRIMARY KEY,
    feature_name VARCHAR(100) NOT NULL REFERENCES feature_flags(name) ON DELETE CASCADE,
    snapshot_type VARCHAR(20) NOT NULL,
    feature_config JSONB NOT NULL,
    role_mappings JSONB,
    tier_limits JSONB,
    org_overrides JSONB,
    rollout_plan JSONB,
    ab_tests JSONB,
    created_by VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reason TEXT,

    CONSTRAINT chk_snapshot_type CHECK (snapshot_type IN ('pre_change', 'post_change', 'rollback'))
);

CREATE INDEX idx_snapshot_feature ON feature_flag_config_snapshots(feature_name);
CREATE INDEX idx_snapshot_created ON feature_flag_config_snapshots(created_at DESC);
CREATE INDEX idx_snapshot_type ON feature_flag_config_snapshots(snapshot_type);

COMMENT ON TABLE feature_flag_config_snapshots IS 'Configuration snapshots for rollback capability';

-- =====================================================
-- 4. CACHE INVALIDATION TRIGGERS
-- =====================================================

CREATE OR REPLACE FUNCTION invalidate_feature_cache()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO feature_flag_cache_status (feature_name, last_config_change, cache_invalidated_at)
    VALUES (NEW.feature_name, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    ON CONFLICT (feature_name) DO UPDATE SET
        last_config_change = CURRENT_TIMESTAMP,
        cache_invalidated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_invalidate_cache_on_role_mapping
    AFTER INSERT OR UPDATE OR DELETE ON feature_flag_role_mappings
    FOR EACH ROW EXECUTE FUNCTION invalidate_feature_cache();

CREATE TRIGGER trg_invalidate_cache_on_tier_limits
    AFTER INSERT OR UPDATE OR DELETE ON feature_flag_tier_limits
    FOR EACH ROW EXECUTE FUNCTION invalidate_feature_cache();

CREATE TRIGGER trg_invalidate_cache_on_rollout
    AFTER INSERT OR UPDATE OR DELETE ON feature_flag_rollout_plans
    FOR EACH ROW EXECUTE FUNCTION invalidate_feature_cache();

CREATE TRIGGER trg_invalidate_cache_on_ab_test
    AFTER INSERT OR UPDATE OR DELETE ON feature_flag_ab_tests
    FOR EACH ROW EXECUTE FUNCTION invalidate_feature_cache();

COMMIT;

-- ============================================================================
-- END MIGRATION 097_FEATURE_FLAGS_ADVANCED
-- ============================================================================
