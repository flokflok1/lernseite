-- ============================================================================
-- Migration: 033_billing_core.sql
-- Version: 1.0.0
-- Description: Database migration
-- Author: LernsystemX Migration System
-- Date: 2026-01-02
-- ============================================================================

CREATE TABLE IF NOT EXISTS billing_storage.subscriptions (
    subscription_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES core.users(user_id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organisations.organisations(organization_id) ON DELETE CASCADE,
    plan_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    billing_cycle VARCHAR(20) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'EUR',
    stripe_subscription_id VARCHAR(255),
    stripe_customer_id VARCHAR(255),
    current_period_start TIMESTAMPTZ NOT NULL,
    current_period_end TIMESTAMPTZ NOT NULL,
    trial_start TIMESTAMPTZ,
    trial_end TIMESTAMPTZ,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    cancelled_at TIMESTAMPTZ,
    cancellation_reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_subscription_plan CHECK (plan_type IN ('free', 'premium', 'creator', 'teacher', 'school', 'company')),
    CONSTRAINT chk_subscription_status CHECK (status IN ('active', 'past_due', 'canceled', 'unpaid', 'trialing', 'incomplete', 'incomplete_expired')),
    CONSTRAINT chk_billing_cycle CHECK (billing_cycle IN ('monthly', 'yearly')),
    CONSTRAINT chk_subscription_target CHECK (
        (user_id IS NOT NULL AND organization_id IS NULL) OR
        (user_id IS NULL AND organization_id IS NOT NULL)
    )
);

CREATE INDEX IF NOT EXISTS idx_subscriptions_user ON billing_storage.subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_org ON billing_storage.subscriptions(organization_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON billing_storage.subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_plan ON billing_storage.subscriptions(plan_type);
CREATE INDEX IF NOT EXISTS idx_subscriptions_stripe_sub ON billing_storage.subscriptions(stripe_subscription_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_stripe_customer ON billing_storage.subscriptions(stripe_customer_id);

COMMENT ON TABLE billing_storage.subscriptions IS 'User and organization subscription plans';

-- ============================================================================
-- TABLE: payment_methods
-- Description: Saved payment methods
-- ============================================================================
CREATE TABLE IF NOT EXISTS billing_storage.payment_methods (
    payment_method_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES core.users(user_id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organisations.organisations(organization_id) ON DELETE CASCADE,
    stripe_payment_method_id VARCHAR(255) NOT NULL,
    payment_type VARCHAR(50) NOT NULL,
    card_brand VARCHAR(50),
    card_last4 VARCHAR(4),
    card_exp_month INTEGER,
    card_exp_year INTEGER,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_payment_type CHECK (payment_type IN ('card', 'sepa_debit', 'paypal', 'invoice')),
    CONSTRAINT chk_payment_target CHECK (
        (user_id IS NOT NULL AND organization_id IS NULL) OR
        (user_id IS NULL AND organization_id IS NOT NULL)
    )
);

CREATE INDEX IF NOT EXISTS idx_payment_methods_user ON billing_storage.payment_methods(user_id);
CREATE INDEX IF NOT EXISTS idx_payment_methods_org ON billing_storage.payment_methods(organization_id);
CREATE INDEX IF NOT EXISTS idx_payment_methods_stripe ON billing_storage.payment_methods(stripe_payment_method_id);

COMMENT ON TABLE billing_storage.payment_methods IS 'Saved payment methods for users and organizations';

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- ============================================================================
DROP TRIGGER IF EXISTS update_subscriptions_updated_at ON billing_storage.subscriptions;
CREATE TRIGGER update_subscriptions_updated_at BEFORE UPDATE ON billing_storage.subscriptions
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- End of Migration: 033_billing_core.sql
-- ============================================================================
