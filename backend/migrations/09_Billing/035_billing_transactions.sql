-- ============================================================================
-- Migration: 035_billing_transactions.sql
-- Version: 1.0.0
-- Description: Database migration
-- Author: LernsystemX Migration System
-- Date: 2026-01-02
-- ============================================================================

CREATE TABLE IF NOT EXISTS billing_storage.token_wallets (
    wallet_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES core.users(user_id) ON DELETE CASCADE,
    organisation_id UUID REFERENCES organisations.organisations(organisation_id) ON DELETE CASCADE,
    balance INTEGER DEFAULT 0,
    total_purchased INTEGER DEFAULT 0,
    total_granted INTEGER DEFAULT 0,
    total_consumed INTEGER DEFAULT 0,
    last_grant_date DATE,
    monthly_grant_amount INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_wallet_target CHECK (
        (user_id IS NOT NULL AND organisation_id IS NULL) OR
        (user_id IS NULL AND organisation_id IS NOT NULL)
    ),
    UNIQUE (user_id),
    UNIQUE (organisation_id)
);

CREATE INDEX IF NOT EXISTS idx_token_wallets_user ON billing_storage.token_wallets(user_id);
CREATE INDEX IF NOT EXISTS idx_token_wallets_org ON billing_storage.token_wallets(organisation_id);

COMMENT ON TABLE billing_storage.token_wallets IS 'Token balance management for AI usage';

-- ============================================================================
-- TABLE: token_transactions
-- Description: Token transaction history
-- ============================================================================
CREATE TABLE IF NOT EXISTS billing_storage.token_transactions (
    transaction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wallet_id UUID REFERENCES billing_storage.token_wallets(wallet_id) ON DELETE CASCADE,
    user_id UUID REFERENCES core.users(user_id) ON DELETE CASCADE,
    organisation_id UUID REFERENCES organisations.organisations(organisation_id) ON DELETE CASCADE,
    transaction_type VARCHAR(50) NOT NULL,
    amount INTEGER NOT NULL,
    balance_after INTEGER NOT NULL,
    description TEXT,
    reference_type VARCHAR(50),
    reference_id UUID,
    ai_module VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_token_transaction_type CHECK (transaction_type IN ('grant', 'purchase', 'consumption', 'refund', 'adjustment', 'monthly_grant')),
    CONSTRAINT chk_token_target CHECK (
        (user_id IS NOT NULL AND organisation_id IS NULL) OR
        (user_id IS NULL AND organisation_id IS NOT NULL)
    )
);

CREATE INDEX IF NOT EXISTS idx_token_transactions_wallet ON billing_storage.token_transactions(wallet_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_token_transactions_user ON billing_storage.token_transactions(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_token_transactions_org ON billing_storage.token_transactions(organisation_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_token_transactions_type ON billing_storage.token_transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_token_transactions_reference ON billing_storage.token_transactions(reference_type, reference_id);

COMMENT ON TABLE billing_storage.token_transactions IS 'Token transaction history for AI usage tracking';

-- ============================================================================
-- TABLE: payment_history
-- Description: Payment transaction records
-- ============================================================================
CREATE TABLE IF NOT EXISTS billing_storage.payment_history (
    payment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subscription_id UUID REFERENCES billing_storage.subscriptions(subscription_id) ON DELETE SET NULL,
    user_id UUID REFERENCES core.users(user_id) ON DELETE CASCADE,
    organisation_id UUID REFERENCES organisations.organisations(organisation_id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'EUR',
    status VARCHAR(50) NOT NULL,
    payment_method VARCHAR(50),
    stripe_payment_intent_id VARCHAR(255),
    stripe_invoice_id VARCHAR(255),
    description TEXT,
    metadata JSONB,
    paid_at TIMESTAMPTZ,
    failed_at TIMESTAMPTZ,
    refunded_at TIMESTAMPTZ,
    refund_amount DECIMAL(10,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_payment_status CHECK (status IN ('pending', 'processing', 'succeeded', 'failed', 'refunded', 'partially_refunded')),
    CONSTRAINT chk_payment_target CHECK (
        (user_id IS NOT NULL AND organisation_id IS NULL) OR
        (user_id IS NULL AND organisation_id IS NOT NULL)
    )
);

CREATE INDEX IF NOT EXISTS idx_payment_history_subscription ON billing_storage.payment_history(subscription_id);
CREATE INDEX IF NOT EXISTS idx_payment_history_user ON billing_storage.payment_history(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_payment_history_org ON billing_storage.payment_history(organisation_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_payment_history_status ON billing_storage.payment_history(status);
CREATE INDEX IF NOT EXISTS idx_payment_history_stripe_intent ON billing_storage.payment_history(stripe_payment_intent_id);

COMMENT ON TABLE billing_storage.payment_history IS 'Payment transaction history';

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- ============================================================================
DROP TRIGGER IF EXISTS update_token_wallets_updated_at ON billing_storage.token_wallets;
CREATE TRIGGER update_token_wallets_updated_at BEFORE UPDATE ON billing_storage.token_wallets
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- End of Migration: 035_billing_transactions.sql
-- ============================================================================
