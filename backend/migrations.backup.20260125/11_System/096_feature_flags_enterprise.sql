-- ============================================================================
-- Migration: 096_feature_flags_enterprise.sql
-- Description: Feature Flags System - Enterprise Configurations
--              Role-based fine-grained control and subscription tier limits
--              Advanced progressive rollout planning
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-01-18
-- ============================================================================
-- Part of Feature Flag System (Phase 1: Enterprise Feature Configuration)
--
-- Tables created:
-- - feature_flag_role_mappings (role-based fine-grained control with quotas)
-- - feature_flag_tier_limits (subscription tier-based quotas)
-- - feature_flag_rollout_plans (4-phase progressive rollout planning)
-- - feature_flag_ab_tests (A/B test variant testing)
--
-- Requires: 095_feature_flags_core.sql (feature_flags table)
-- ============================================================================

BEGIN;

-- =====================================================
-- 1. FEATURE ROLE MAPPINGS (Role-based fine-grained control)
-- =====================================================

CREATE TABLE IF NOT EXISTS feature_flag_role_mappings (
    id SERIAL PRIMARY KEY,
    feature_name VARCHAR(100) NOT NULL REFERENCES feature_flags(name) ON DELETE CASCADE,
    role_code VARCHAR(50) NOT NULL,
    is_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    max_usage_per_day INTEGER,
    max_creation_per_month INTEGER,
    priority_level INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_feature_role UNIQUE(feature_name, role_code),
    CONSTRAINT chk_role_code CHECK (role_code IN (
        'admin', 'creator', 'teacher', 'student', 'parent',
        'moderator', 'support', 'company', 'school'
    ))
);

CREATE INDEX idx_feature_role_feature ON feature_flag_role_mappings(feature_name);
CREATE INDEX idx_feature_role_role ON feature_flag_role_mappings(role_code);
CREATE INDEX idx_feature_role_enabled ON feature_flag_role_mappings(is_enabled);
CREATE INDEX idx_feature_role_priority ON feature_flag_role_mappings(priority_level);

COMMENT ON TABLE feature_flag_role_mappings IS 'Role-based access control with per-role quotas';
COMMENT ON COLUMN feature_flag_role_mappings.max_usage_per_day IS 'Daily limit (NULL = unlimited)';
COMMENT ON COLUMN feature_flag_role_mappings.priority_level IS '0=normal, 10=premium, 20=enterprise';

-- =====================================================
-- 2. FEATURE TIER LIMITS (Subscription tier-based quotas)
-- =====================================================

CREATE TABLE IF NOT EXISTS feature_flag_tier_limits (
    id SERIAL PRIMARY KEY,
    feature_name VARCHAR(100) NOT NULL REFERENCES feature_flags(name) ON DELETE CASCADE,
    tier_code VARCHAR(50) NOT NULL,
    is_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    max_concurrent_usage INTEGER,
    max_monthly_quota INTEGER,
    max_per_day INTEGER,
    max_storage_gb DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_feature_tier UNIQUE(feature_name, tier_code),
    CONSTRAINT chk_tier_code CHECK (tier_code IN ('free', 'premium', 'enterprise'))
);

CREATE INDEX idx_feature_tier_feature ON feature_flag_tier_limits(feature_name);
CREATE INDEX idx_feature_tier_tier ON feature_flag_tier_limits(tier_code);
CREATE INDEX idx_feature_tier_enabled ON feature_flag_tier_limits(is_enabled);

COMMENT ON TABLE feature_flag_tier_limits IS 'Tier-based feature limits (free, premium, enterprise)';

-- =====================================================
-- 3. FEATURE ROLLOUT PLANS (4-Phase progressive rollout)
-- =====================================================

CREATE TABLE IF NOT EXISTS feature_flag_rollout_plans (
    id SERIAL PRIMARY KEY,
    feature_name VARCHAR(100) NOT NULL REFERENCES feature_flags(name) ON DELETE CASCADE,
    plan_name VARCHAR(255) NOT NULL,
    phase_1_percentage INTEGER DEFAULT 5,
    phase_1_duration_hours INTEGER DEFAULT 12,
    phase_1_start_at TIMESTAMP,
    phase_2_percentage INTEGER DEFAULT 25,
    phase_2_duration_hours INTEGER DEFAULT 24,
    phase_2_start_at TIMESTAMP,
    phase_3_percentage INTEGER DEFAULT 50,
    phase_3_duration_hours INTEGER DEFAULT 48,
    phase_3_start_at TIMESTAMP,
    phase_4_start_at TIMESTAMP,
    current_phase INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'planned',
    target_roles TEXT[],
    target_tiers TEXT[],
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(36),

    CONSTRAINT uq_feature_rollout UNIQUE(feature_name),
    CONSTRAINT chk_rollout_status CHECK (status IN ('planned', 'active', 'paused', 'completed', 'rolled_back')),
    CONSTRAINT chk_current_phase CHECK (current_phase >= 0 AND current_phase <= 5)
);

CREATE INDEX idx_rollout_feature ON feature_flag_rollout_plans(feature_name);
CREATE INDEX idx_rollout_status ON feature_flag_rollout_plans(status);
CREATE INDEX idx_rollout_active ON feature_flag_rollout_plans(status) WHERE status = 'active';

COMMENT ON TABLE feature_flag_rollout_plans IS '4-phase progressive rollout (canary → early → wider → full)';

-- =====================================================
-- 4. FEATURE A/B TESTS (Variant testing)
-- =====================================================

CREATE TABLE IF NOT EXISTS feature_flag_ab_tests (
    id SERIAL PRIMARY KEY,
    feature_name VARCHAR(100) NOT NULL REFERENCES feature_flags(name) ON DELETE CASCADE,
    test_name VARCHAR(255) NOT NULL,
    variant_a_name VARCHAR(100) NOT NULL,
    variant_a_percentage INTEGER NOT NULL DEFAULT 50,
    variant_a_config JSONB,
    variant_b_name VARCHAR(100) NOT NULL,
    variant_b_percentage INTEGER NOT NULL DEFAULT 50,
    variant_b_config JSONB,
    target_roles TEXT[],
    target_tiers TEXT[],
    metrics_to_track TEXT[],
    started_at TIMESTAMP,
    planned_duration_days INTEGER DEFAULT 14,
    ended_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'planned',
    winner VARCHAR(1),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(36),

    CONSTRAINT chk_ab_percentages CHECK (variant_a_percentage + variant_b_percentage = 100),
    CONSTRAINT chk_ab_status CHECK (status IN ('planned', 'active', 'paused', 'completed')),
    CONSTRAINT chk_ab_winner CHECK (winner IS NULL OR winner IN ('A', 'B'))
);

CREATE INDEX idx_ab_feature ON feature_flag_ab_tests(feature_name);
CREATE INDEX idx_ab_status ON feature_flag_ab_tests(status);
CREATE INDEX idx_ab_active ON feature_flag_ab_tests(status) WHERE status = 'active';

COMMENT ON TABLE feature_flag_ab_tests IS 'A/B test configuration for feature variants';

-- =====================================================
-- 5. UPDATED_AT TRIGGER FUNCTION FOR ENTERPRISE TABLES
-- =====================================================

CREATE OR REPLACE FUNCTION update_feature_config_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_feature_role_mappings_updated_at
    BEFORE UPDATE ON feature_flag_role_mappings
    FOR EACH ROW EXECUTE FUNCTION update_feature_config_timestamp();

CREATE TRIGGER trg_feature_tier_limits_updated_at
    BEFORE UPDATE ON feature_flag_tier_limits
    FOR EACH ROW EXECUTE FUNCTION update_feature_config_timestamp();

CREATE TRIGGER trg_feature_rollout_plans_updated_at
    BEFORE UPDATE ON feature_flag_rollout_plans
    FOR EACH ROW EXECUTE FUNCTION update_feature_config_timestamp();

CREATE TRIGGER trg_feature_ab_tests_updated_at
    BEFORE UPDATE ON feature_flag_ab_tests
    FOR EACH ROW EXECUTE FUNCTION update_feature_config_timestamp();

COMMIT;

-- ============================================================================
-- END MIGRATION 096_FEATURE_FLAGS_ENTERPRISE
-- ============================================================================
