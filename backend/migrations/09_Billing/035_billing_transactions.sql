-- ============================================================================
-- Migration: 035_billing_transactions.sql
-- Description: Token wallets and payment transactions
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-01-17
-- ============================================================================

-- ============================================================================
-- TABLE: token_wallets
-- Description: Token balances for users and organizations
-- ============================================================================
CREATE TABLE IF NOT EXISTS token_wallets (
    wallet_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(organization_id) ON DELETE CASCADE,
    balance INTEGER DEFAULT 0,
    total_purchased INTEGER DEFAULT 0,
    total_granted INTEGER DEFAULT 0,
    total_consumed INTEGER DEFAULT 0,
    last_grant_date DATE,
    monthly_grant_amount INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_wallet_target CHECK (
        (user_id IS NOT NULL AND organization_id IS NULL) OR
        (user_id IS NULL AND organization_id IS NOT NULL)
    ),
    UNIQUE (user_id),
    UNIQUE (organization_id)
);

CREATE INDEX IF NOT EXISTS idx_token_wallets_user ON token_wallets(user_id);
CREATE INDEX IF NOT EXISTS idx_token_wallets_org ON token_wallets(organization_id);

COMMENT ON TABLE token_wallets IS 'Token balance management for AI usage';

-- ============================================================================
-- TABLE: token_transactions
-- Description: Token transaction history
-- ============================================================================
CREATE TABLE IF NOT EXISTS token_transactions (
    transaction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wallet_id UUID REFERENCES token_wallets(wallet_id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(organization_id) ON DELETE CASCADE,
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
        (user_id IS NOT NULL AND organization_id IS NULL) OR
        (user_id IS NULL AND organization_id IS NOT NULL)
    )
);

CREATE INDEX IF NOT EXISTS idx_token_transactions_wallet ON token_transactions(wallet_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_token_transactions_user ON token_transactions(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_token_transactions_org ON token_transactions(organization_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_token_transactions_type ON token_transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_token_transactions_reference ON token_transactions(reference_type, reference_id);

COMMENT ON TABLE token_transactions IS 'Token transaction history for AI usage tracking';

-- ============================================================================
-- TABLE: payment_history
-- Description: Payment transaction records
-- ============================================================================
CREATE TABLE IF NOT EXISTS payment_history (
    payment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subscription_id UUID REFERENCES subscriptions(subscription_id) ON DELETE SET NULL,
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(organization_id) ON DELETE CASCADE,
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
        (user_id IS NOT NULL AND organization_id IS NULL) OR
        (user_id IS NULL AND organization_id IS NOT NULL)
    )
);

CREATE INDEX IF NOT EXISTS idx_payment_history_subscription ON payment_history(subscription_id);
CREATE INDEX IF NOT EXISTS idx_payment_history_user ON payment_history(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_payment_history_org ON payment_history(organization_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_payment_history_status ON payment_history(status);
CREATE INDEX IF NOT EXISTS idx_payment_history_stripe_intent ON payment_history(stripe_payment_intent_id);

COMMENT ON TABLE payment_history IS 'Payment transaction history';

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- ============================================================================
CREATE TRIGGER update_token_wallets_updated_at BEFORE UPDATE ON token_wallets
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- End of Migration: 035_billing_transactions.sql
-- ============================================================================
