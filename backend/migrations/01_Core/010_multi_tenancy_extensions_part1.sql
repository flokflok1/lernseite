-- =====================================================
-- Migration: 010_multi_tenancy_extensions_part1.sql
-- =====================================================
-- Datum: 2026-01-09
-- Zweck: Erweitert organisations.organisations für echte Multi-Tenancy
-- WICHTIG: Diese Migration ist robust gegen fehlende Tabellen
-- =====================================================

BEGIN;

-- =====================================================
-- 1. Erweitere organisations.organisations (OHNE Abhängigkeiten)
-- =====================================================

-- Füge Billing-Modell-Spalte hinzu
ALTER TABLE organisations.organisations
ADD COLUMN IF NOT EXISTS billing_model VARCHAR(50) DEFAULT 'freemium';

-- Füge Pricing-Spalten hinzu
ALTER TABLE organisations.organisations
ADD COLUMN IF NOT EXISTS price_per_user DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS flatrate_price DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS seat_count INTEGER,
ADD COLUMN IF NOT EXISTS platform_fee_percent INTEGER DEFAULT 25,
ADD COLUMN IF NOT EXISTS subscription_tier VARCHAR(50) DEFAULT 'free';

-- Comments
COMMENT ON COLUMN organisations.organisations.billing_model IS 'Billing-Modelle: per_user, flatrate, seat_based, revenue_share, hybrid, freemium';
COMMENT ON COLUMN organisations.organisations.price_per_user IS 'Preis pro aktiven User/Monat (per_user model)';
COMMENT ON COLUMN organisations.organisations.flatrate_price IS 'Flatrate-Preis/Monat (flatrate model)';
COMMENT ON COLUMN organisations.organisations.seat_count IS 'Anzahl gekaufter Seats (seat_based model)';
COMMENT ON COLUMN organisations.organisations.platform_fee_percent IS 'Platform Fee % (revenue_share model)';
COMMENT ON COLUMN organisations.organisations.subscription_tier IS 'free|pro|enterprise';

-- =====================================================
-- 2. White-Label Branding
-- =====================================================

CREATE TABLE IF NOT EXISTS organisations.branding (
    organisation_id UUID PRIMARY KEY REFERENCES organisations.organisations(organisation_id) ON DELETE CASCADE,

    -- Logos
    logo_url VARCHAR(500),
    logo_dark_url VARCHAR(500),
    favicon_url VARCHAR(500),

    -- Farben
    primary_color VARCHAR(7),
    secondary_color VARCHAR(7),
    accent_color VARCHAR(7),
    text_color VARCHAR(7),
    background_color VARCHAR(7),

    -- Font
    font_family VARCHAR(100),

    -- Status
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_branding_org ON organisations.branding(organisation_id);

COMMENT ON TABLE organisations.branding IS 'White-Label-Branding-Einstellungen pro Organisation';

-- =====================================================
-- 3. Organization Feature Flags
-- =====================================================

CREATE TABLE IF NOT EXISTS organisations.feature_flags (
    organisation_id UUID NOT NULL REFERENCES organisations.organisations(organisation_id) ON DELETE CASCADE,
    feature_code VARCHAR(100) NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (organisation_id, feature_code)
);

CREATE INDEX IF NOT EXISTS idx_feature_flags_org ON organisations.feature_flags(organisation_id);

COMMENT ON TABLE organisations.feature_flags IS 'Organization-specific feature flag configuration';

COMMIT;
