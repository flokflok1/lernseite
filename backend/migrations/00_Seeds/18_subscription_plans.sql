-- ============================================================================
-- Seed Data: Subscription Plans
-- Description: Available subscription plan definitions with pricing and features
-- Source: 040_billing_subscriptions.sql
-- Author: LernsystemX Migration System
-- Date: 2026-01-26
-- Phase: 4 (Seed Data)
-- ============================================================================

-- ============================================================================
-- Subscription Plans - 4 Plan Types
-- ============================================================================
-- Seeds the billing_storage.subscription_plans table
-- Defines available subscription plans with features and pricing
--
-- Plan Types:
--   1. free - Free plan with basic features
--   2. premium - Premium individual plan with AI and extended features
--   3. creator - Creator plan with marketplace and revenue sharing
--   4. teacher - Teacher plan with class management and bulk student support
--
-- Features Structure (JSONB):
--   - methods: Number of supported learning methods
--   - ai: AI content generation enabled
--   - max_courses: Maximum courses allowed
--   - marketplace: Course marketplace access (creator+)
--   - revenue_share: Revenue share percentage (creator)
--   - classes: Number of classes (teacher)
--   - students: Number of students per class (teacher)
--
-- Pricing:
--   - price_monthly: Monthly subscription price (EUR)
--   - price_yearly: Yearly subscription price (EUR)
--   - token_monthly_grant: Monthly AI token grant

INSERT INTO billing_storage.subscription_plans (plan_code, name, plan_type, features, price_monthly, price_yearly, token_monthly_grant) VALUES
    ('free', 'Free', 'free', '{"methods": 11, "ai": false, "max_courses": 3}'::jsonb, 0, 0, 0),
    ('premium', 'Premium', 'premium', '{"methods": 17, "ai": true, "max_courses": 999}'::jsonb, 14.99, 143.90, 10000),
    ('creator', 'Creator', 'creator', '{"methods": 21, "ai": true, "marketplace": true, "revenue_share": 0.75}'::jsonb, 29.99, 287.90, 50000),
    ('teacher', 'Lehrer', 'teacher', '{"methods": 21, "ai": true, "classes": 10, "students": 300}'::jsonb, 49.99, 479.90, 100000)
ON CONFLICT (plan_code) DO NOTHING;

-- ============================================================================
-- Verification
-- ============================================================================

SELECT COUNT(*) as total_subscription_plans FROM billing_storage.subscription_plans;
