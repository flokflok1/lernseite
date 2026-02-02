-- =====================================================
-- Migration 025: B2B Contact Request Tracking System
-- =====================================================
-- Purpose: Sales pipeline management for B2B customer acquisition
-- Status: Foundation for contact-to-conversion workflow
-- Created: 2026-01-22
-- =====================================================

-- B2B Contact Request Table
-- Tracks business inquiries from initial contact through to organization creation
CREATE TABLE IF NOT EXISTS core.b2b_contact_requests (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Contact Information (Required)
    company_name VARCHAR(200) NOT NULL,
    contact_person VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(30) NOT NULL,

    -- Company Details (Optional but Recommended)
    company_size VARCHAR(20),  -- "1-10", "11-50", "51-200", "200+"
    industry VARCHAR(100),      -- "Schule", "Universität", "Unternehmen", "Sonstiges"
    message TEXT,               -- Customer's inquiry/needs description

    -- Sales Pipeline Status
    status VARCHAR(50) DEFAULT 'new' NOT NULL,
    -- Pipeline stages:
    --   'new'         → Initial submission, awaiting first contact
    --   'contacted'   → Admin reached out to customer
    --   'offer_sent'  → Pricing proposal sent
    --   'negotiating' → Active price/feature negotiation
    --   'converted'   → Organization created, deal closed
    --   'rejected'    → Customer declined or deal lost

    -- Internal Admin Notes
    notes TEXT,  -- Private notes from sales conversations, NOT visible to customer

    -- Pricing & Plan Details (Set during negotiation)
    proposed_plan VARCHAR(50),      -- "startup", "professional", "enterprise", "custom"
    proposed_price DECIMAL(10,2),   -- Custom negotiated pricing in EUR
    currency VARCHAR(3) DEFAULT 'EUR',
    billing_cycle VARCHAR(20),      -- "monthly", "quarterly", "annual"

    -- Link to Created Organization (Post-Conversion)
    organisation_id UUID REFERENCES organisations.organisations(organisation_id),
    -- NULL until conversion, then links to created org for tracking

    -- Admin Assignment
    assigned_to UUID REFERENCES core.users(user_id),  -- Which admin is handling this request

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    contacted_at TIMESTAMP,         -- When admin first contacted customer
    offer_sent_at TIMESTAMP,        -- When pricing offer was sent to customer
    converted_at TIMESTAMP,         -- When organization was successfully created
    rejected_at TIMESTAMP,          -- When deal was lost/customer declined
    last_updated TIMESTAMP DEFAULT NOW() NOT NULL,

    -- Source Tracking (Marketing Attribution)
    source VARCHAR(50) DEFAULT 'website' NOT NULL,  -- 'website', 'referral', 'event', 'direct', 'partner'
    referrer VARCHAR(255),          -- Referring URL or partner name

    -- Additional Flexible Data
    metadata JSONB DEFAULT '{}'::jsonb,  -- For custom fields without schema changes

    -- Constraints
    CONSTRAINT chk_status_valid CHECK (
        status IN ('new', 'contacted', 'offer_sent', 'negotiating', 'converted', 'rejected')
    ),
    CONSTRAINT chk_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT chk_phone_not_empty CHECK (phone <> ''),
    CONSTRAINT chk_price_positive CHECK (proposed_price IS NULL OR proposed_price >= 0)
);

-- =====================================================
-- Indexes for Performance
-- =====================================================

-- Status-based queries (most common filter in admin panel)
CREATE INDEX idx_b2b_requests_status ON core.b2b_contact_requests(status);

-- Recently created requests (admin dashboard)
CREATE INDEX idx_b2b_requests_created ON core.b2b_contact_requests(created_at DESC);

-- Email lookup (duplicate detection, customer search)
CREATE INDEX idx_b2b_requests_email ON core.b2b_contact_requests(email);

-- Organization lookup (find source request after conversion)
CREATE INDEX idx_b2b_requests_org ON core.b2b_contact_requests(organisation_id)
    WHERE organisation_id IS NOT NULL;

-- Company name search (admin search functionality)
CREATE INDEX idx_b2b_requests_company ON core.b2b_contact_requests USING gin(to_tsvector('german', company_name));

-- Assigned admin queries (my requests view)
CREATE INDEX idx_b2b_requests_assigned ON core.b2b_contact_requests(assigned_to)
    WHERE assigned_to IS NOT NULL;

-- Composite index for admin panel filters (status + date)
CREATE INDEX idx_b2b_requests_status_date ON core.b2b_contact_requests(status, created_at DESC);

-- =====================================================
-- Auto-Update Timestamp Trigger
-- =====================================================

CREATE OR REPLACE FUNCTION update_b2b_request_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_b2b_request_update
    BEFORE UPDATE ON core.b2b_contact_requests
    FOR EACH ROW
    EXECUTE FUNCTION update_b2b_request_timestamp();

-- =====================================================
-- Auto-Set Conversion Timestamp Trigger
-- =====================================================

CREATE OR REPLACE FUNCTION set_b2b_conversion_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    -- If status changed to 'converted' and converted_at is NULL, set it
    IF NEW.status = 'converted' AND OLD.status <> 'converted' AND NEW.converted_at IS NULL THEN
        NEW.converted_at = NOW();
    END IF;

    -- If status changed to 'rejected' and rejected_at is NULL, set it
    IF NEW.status = 'rejected' AND OLD.status <> 'rejected' AND NEW.rejected_at IS NULL THEN
        NEW.rejected_at = NOW();
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_b2b_conversion_timestamp
    BEFORE UPDATE ON core.b2b_contact_requests
    FOR EACH ROW
    WHEN (NEW.status IS DISTINCT FROM OLD.status)
    EXECUTE FUNCTION set_b2b_conversion_timestamp();

-- =====================================================
-- Comments for Documentation
-- =====================================================

COMMENT ON TABLE core.b2b_contact_requests IS
'B2B sales pipeline tracking from initial contact through to organization creation. Used for managing business customer acquisition with custom pricing negotiation.';

COMMENT ON COLUMN core.b2b_contact_requests.status IS
'Pipeline stage: new (submitted) → contacted (admin reached out) → offer_sent (proposal sent) → negotiating (active discussion) → converted (org created) | rejected (deal lost)';

COMMENT ON COLUMN core.b2b_contact_requests.notes IS
'Internal admin notes from sales conversations - NOT visible to customer. Used for documenting negotiation details, customer needs, and follow-up actions.';

COMMENT ON COLUMN core.b2b_contact_requests.proposed_plan IS
'Plan tier proposed to customer during negotiation: startup (small teams), professional (mid-size), enterprise (large orgs), custom (fully bespoke)';

COMMENT ON COLUMN core.b2b_contact_requests.proposed_price IS
'Custom negotiated monthly price in EUR. NULL if standard pricing applies. Set during offer_sent stage.';

COMMENT ON COLUMN core.b2b_contact_requests.organisation_id IS
'Links to created organization after successful conversion. NULL until status=converted. Used to trace organization back to original contact request.';

COMMENT ON COLUMN core.b2b_contact_requests.assigned_to IS
'Admin/sales rep handling this request. Used for workload distribution and accountability.';

COMMENT ON COLUMN core.b2b_contact_requests.metadata IS
'Flexible JSONB field for additional custom data without schema changes. Example: {"demo_requested": true, "preferred_contact_time": "morning", "features_of_interest": ["liveroom", "ai_tutor"]}';

-- =====================================================
-- Sample Data (Development/Testing)
-- =====================================================

-- Only insert sample data in development environment
DO $$
BEGIN
    IF current_setting('server_version_num')::int < 140000
       OR EXISTS (SELECT 1 FROM pg_settings WHERE name = 'application_name' AND setting LIKE '%dev%')
    THEN
        INSERT INTO core.b2b_contact_requests (
            company_name, contact_person, email, phone, company_size, industry, message, status
        ) VALUES
            (
                'Musterschule GmbH',
                'Max Mustermann',
                'max.mustermann@musterschule.de',
                '+49 30 12345678',
                '51-200',
                'Schule',
                'Wir suchen eine Lernplattform für 150 Schüler. Interesse an Live-Unterricht und KI-Tutor.',
                'new'
            ),
            (
                'TechCorp AG',
                'Anna Schmidt',
                'anna.schmidt@techcorp.de',
                '+49 89 98765432',
                '200+',
                'Unternehmen',
                'Enterprise Learning Management System für IT-Weiterbildung. Budget: 5000€/Monat.',
                'contacted'
            )
        ON CONFLICT DO NOTHING;
    END IF;
END $$;

-- =====================================================
-- Migration Complete
-- =====================================================

-- Verify table creation
SELECT
    'core.b2b_contact_requests table created successfully' AS status,
    COUNT(*) AS sample_records
FROM core.b2b_contact_requests;
