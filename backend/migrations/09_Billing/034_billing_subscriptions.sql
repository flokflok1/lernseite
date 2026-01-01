-- ============================================================================
-- Migration: 034_billing_subscriptions.sql
-- Description: Subscription plans, upgrades, and lifecycle
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-01-17
-- ============================================================================

-- ============================================================================
-- TABLE: subscription_plans
-- Description: Available subscription plan definitions
-- ============================================================================
CREATE TABLE IF NOT EXISTS subscription_plans (
    plan_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plan_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    plan_type VARCHAR(50) NOT NULL,
    features JSONB NOT NULL,
    price_monthly DECIMAL(10,2) NOT NULL,
    price_yearly DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'EUR',
    token_monthly_grant INTEGER DEFAULT 0,
    active BOOLEAN DEFAULT TRUE,
    stripe_product_id VARCHAR(255),
    stripe_price_monthly_id VARCHAR(255),
    stripe_price_yearly_id VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_plan_type CHECK (plan_type IN ('free', 'premium', 'creator', 'teacher', 'school', 'company'))
);

CREATE INDEX IF NOT EXISTS idx_subscription_plans_code ON subscription_plans(plan_code);
CREATE INDEX IF NOT EXISTS idx_subscription_plans_type ON subscription_plans(plan_type);
CREATE INDEX IF NOT EXISTS idx_subscription_plans_active ON subscription_plans(active) WHERE active = TRUE;

COMMENT ON TABLE subscription_plans IS 'Subscription plan definitions with pricing and features';

-- ============================================================================
-- TABLE: subscription_changes
-- Description: History of subscription upgrades/downgrades
-- ============================================================================
CREATE TABLE IF NOT EXISTS subscription_changes (
    change_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subscription_id UUID REFERENCES subscriptions(subscription_id) ON DELETE CASCADE,
    change_type VARCHAR(50) NOT NULL,
    from_plan VARCHAR(50),
    to_plan VARCHAR(50),
    effective_date DATE NOT NULL,
    proration_amount DECIMAL(10,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_subscription_change_type CHECK (change_type IN ('upgrade', 'downgrade', 'cancel', 'reactivate', 'trial_start', 'trial_end'))
);

CREATE INDEX IF NOT EXISTS idx_subscription_changes_sub ON subscription_changes(subscription_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_subscription_changes_type ON subscription_changes(change_type);
CREATE INDEX IF NOT EXISTS idx_subscription_changes_effective ON subscription_changes(effective_date);

COMMENT ON TABLE subscription_changes IS 'History of subscription plan changes';

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- ============================================================================
CREATE TRIGGER update_subscription_plans_updated_at BEFORE UPDATE ON subscription_plans
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Seed Subscription Plans
-- ============================================================================
INSERT INTO subscription_plans (plan_code, name, plan_type, features, price_monthly, price_yearly, token_monthly_grant) VALUES
    ('free', 'Free', 'free', '{"methods": 11, "ai": false, "max_courses": 3}'::jsonb, 0, 0, 0),
    ('premium', 'Premium', 'premium', '{"methods": 17, "ai": true, "max_courses": 999}'::jsonb, 14.99, 143.90, 10000),
    ('creator', 'Creator', 'creator', '{"methods": 21, "ai": true, "marketplace": true, "revenue_share": 0.75}'::jsonb, 29.99, 287.90, 50000),
    ('teacher', 'Lehrer', 'teacher', '{"methods": 21, "ai": true, "classes": 10, "students": 300}'::jsonb, 49.99, 479.90, 100000)
ON CONFLICT (plan_code) DO NOTHING;

-- ============================================================================
-- ALTER TABLE: subscriptions
-- Description: Add plan_id foreign key to link with subscription_plans
-- ============================================================================
-- Add plan_id column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'subscriptions' AND column_name = 'plan_id'
    ) THEN
        ALTER TABLE subscriptions ADD COLUMN plan_id UUID;
    END IF;
END$$;

-- Update existing subscriptions to link with subscription_plans based on plan_type
UPDATE subscriptions s
SET plan_id = sp.plan_id
FROM subscription_plans sp
WHERE s.plan_type = sp.plan_type
  AND s.plan_id IS NULL;

-- Add foreign key constraint if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_subscriptions_plan_id'
          AND table_name = 'subscriptions'
    ) THEN
        ALTER TABLE subscriptions
        ADD CONSTRAINT fk_subscriptions_plan_id
        FOREIGN KEY (plan_id) REFERENCES subscription_plans(plan_id) ON DELETE SET NULL;
    END IF;
END$$;

-- Create index on plan_id if it doesn't exist
CREATE INDEX IF NOT EXISTS idx_subscriptions_plan_id ON subscriptions(plan_id);

COMMENT ON COLUMN subscriptions.plan_id IS 'Foreign key reference to subscription_plans table';

-- ============================================================================
-- End of Migration: 034_billing_subscriptions.sql
-- ============================================================================
