-- ============================================================================
-- Seed Data: Organisation Feature Flags & LSX Academy Setup
-- Description: Feature flags for organisations based on subscription tier,
--              LSX Academy organisation creation, course ownership setup
-- Source: 030_multi_tenancy_extensions_part2.sql
-- Author: LernsystemX Migration System
-- Date: 2026-01-26
-- Phase: 4 (Seed Data)
-- ============================================================================

-- ============================================================================
-- Feature Flags per Organisation (based on subscription tier)
-- ============================================================================
-- Dynamic insertion: Creates feature flag entries for each organisation
-- using subscription tier to determine enabled/disabled state
--
-- Feature codes:
--   - liveroom_enabled: Live classroom/video features
--   - whiteboard_enabled: Interactive whiteboard
--   - exams_enabled: Exam/assessment features
--   - ai_enabled: AI content generation (KI-Studio)
--   - analytics_enabled: Advanced analytics
--   - custom_branding: Custom organisation branding
--   - api_access: API access for integrations
--
-- Tier mapping:
--   - free: FALSE for all features
--   - pro: TRUE for all features
--   - enterprise: TRUE for all features

INSERT INTO organisations.feature_flags (organisation_id, feature_code, enabled)
SELECT
    o.organisation_id,
    unnest(ARRAY[
        'liveroom_enabled',
        'whiteboard_enabled',
        'exams_enabled',
        'ai_enabled',
        'analytics_enabled',
        'custom_branding',
        'api_access'
    ]),
    CASE o.subscription_tier
        WHEN 'free' THEN FALSE
        WHEN 'pro' THEN TRUE
        WHEN 'enterprise' THEN TRUE
        ELSE FALSE
    END
FROM organisations.organisations o
ON CONFLICT (organisation_id, feature_code) DO NOTHING;

-- ============================================================================
-- LSX Academy Organisation Setup
-- ============================================================================
-- Create the default LSX Academy organisation (platform-owned)
-- All system courses and shared content are associated with this organisation
-- organisation_id: 00000000-0000-0000-0000-000000000001 (fixed UUID)

INSERT INTO organisations.organisations (
    organisation_id,
    name,
    org_type,
    billing_model,
    platform_fee_percent,
    subscription_tier,
    active
) VALUES (
    '00000000-0000-0000-0000-000000000001'::UUID,
    'LSX Academy',
    'school',
    'revenue_share',
    0,
    'enterprise',
    TRUE
)
ON CONFLICT (organisation_id) DO NOTHING;

-- ============================================================================
-- Assign Existing Courses to LSX Academy
-- ============================================================================
-- Migrate all courses without organisation_id to LSX Academy
-- Ensures backward compatibility with legacy course records

UPDATE courses.courses
SET organisation_id = '00000000-0000-0000-0000-000000000001'::UUID
WHERE organisation_id IS NULL;

-- ============================================================================
-- Verification
-- ============================================================================

SELECT COUNT(*) as total_feature_flags FROM organisations.feature_flags;
SELECT COUNT(*) as total_organisations FROM organisations.organisations;
