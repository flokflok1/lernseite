-- =====================================================
-- Migration 076: Multi-Tenancy Extensions
-- =====================================================
-- Datum: 2026-01-09
-- Zweck: Erweitert bestehendes Organisation-System für echte Multi-Tenancy
--
-- WICHTIG: Diese Migration erweitert das bestehende Organisation-System
-- aus migrations/01_Core/003_organisations.sql
--
-- NEU:
-- - organisation_id in ALLEN relevanten Tabellen
-- - Row-Level Security (RLS) für Tenant-Isolation
-- - Erweiterte Billing-Modelle (6 Typen)
-- - Marketplace-Visibility (private/community/marketplace)
-- - Flexible Feature-Flags pro Organisation
-- =====================================================

-- =====================================================
-- 1. Erweitere organisations.organisations
-- =====================================================

-- Füge neue Billing-Modelle hinzu
ALTER TABLE organisations.organisations
ALTER COLUMN billing_model TYPE VARCHAR(50);

COMMENT ON COLUMN organisations.organisations.billing_model IS
'Billing-Modelle: per_user, flatrate, seat_based, revenue_share, hybrid, freemium';

-- Füge neue Felder hinzu
ALTER TABLE organisations.organisations
ADD COLUMN IF NOT EXISTS price_per_user DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS flatrate_price DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS seat_count INTEGER,
ADD COLUMN IF NOT EXISTS platform_fee_percent INTEGER DEFAULT 25,
ADD COLUMN IF NOT EXISTS max_users INTEGER,
ADD COLUMN IF NOT EXISTS max_courses INTEGER,
ADD COLUMN IF NOT EXISTS enabled_features TEXT[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS subscription_tier VARCHAR(50) DEFAULT 'free';

COMMENT ON COLUMN organisations.organisations.price_per_user IS 'Preis pro aktiven User/Monat (per_user model)';
COMMENT ON COLUMN organisations.organisations.flatrate_price IS 'Flatrate-Preis/Monat (flatrate model)';
COMMENT ON COLUMN organisations.organisations.seat_count IS 'Anzahl gekaufter Seats (seat_based model)';
COMMENT ON COLUMN organisations.organisations.platform_fee_percent IS 'Platform Fee % (revenue_share model)';
COMMENT ON COLUMN organisations.organisations.enabled_features IS 'Array von aktivierten Features';
COMMENT ON COLUMN organisations.organisations.subscription_tier IS 'free|pro|enterprise';

-- =====================================================
-- 2. organisation_id zu ALLEN relevanten Tabellen hinzufügen
-- =====================================================

-- Courses
ALTER TABLE courses.courses
ADD COLUMN IF NOT EXISTS organisation_id UUID REFERENCES organisations.organisations(organisation_id);

CREATE INDEX IF NOT EXISTS idx_courses_organisation_id ON courses.courses(organisation_id);

COMMENT ON COLUMN courses.courses.organisation_id IS
'Organisation die diesen Kurs besitzt. NULL = LSX Academy Kurs';

-- Chapters
ALTER TABLE courses.chapters
ADD COLUMN IF NOT EXISTS organisation_id UUID;

CREATE INDEX IF NOT EXISTS idx_chapters_organisation_id ON courses.chapters(organisation_id);

-- Lessons
ALTER TABLE courses.lessons
ADD COLUMN IF NOT EXISTS organisation_id UUID;

CREATE INDEX IF NOT EXISTS idx_lessons_organisation_id ON courses.lessons(organisation_id);

-- Learning Method Instances
ALTER TABLE learning_methods.learning_method_instances
ADD COLUMN IF NOT EXISTS organisation_id UUID;

CREATE INDEX IF NOT EXISTS idx_lm_instances_organisation_id ON learning_methods.learning_method_instances(organisation_id);

-- Enrollments
ALTER TABLE courses.enrollments
ADD COLUMN IF NOT EXISTS organisation_id UUID;

CREATE INDEX IF NOT EXISTS idx_enrollments_organisation_id ON courses.enrollments(organisation_id);

-- Exams
ALTER TABLE exams.exams
ADD COLUMN IF NOT EXISTS organisation_id UUID;

CREATE INDEX IF NOT EXISTS idx_exams_organisation_id ON exams.exams(organisation_id);

-- Analytics Events
ALTER TABLE analytics.events
ADD COLUMN IF NOT EXISTS organisation_id UUID;

CREATE INDEX IF NOT EXISTS idx_analytics_events_organisation_id ON analytics.events(organisation_id);

-- AI Requests
ALTER TABLE ki.ki_requests
ADD COLUMN IF NOT EXISTS organisation_id UUID;

CREATE INDEX IF NOT EXISTS idx_ki_requests_organisation_id ON ki.ki_requests(organisation_id);

-- LiveRoom Sessions (wenn existiert)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'liverooms' AND table_name = 'rooms') THEN
        ALTER TABLE liverooms.rooms ADD COLUMN IF NOT EXISTS organisation_id UUID;
        CREATE INDEX IF NOT EXISTS idx_rooms_organisation_id ON liverooms.rooms(organisation_id);
    END IF;
END $$;

-- =====================================================
-- 3. Kurs-Visibility Erweitern
-- =====================================================

-- Erweitere courses.visibility
ALTER TABLE courses.courses
ALTER COLUMN visibility TYPE VARCHAR(50);

COMMENT ON COLUMN courses.courses.visibility IS
'private = nur Organisation, community = global free, marketplace = global paid';

-- =====================================================
-- 4. Kurs-Sharing zwischen Organisationen
-- =====================================================

CREATE TABLE IF NOT EXISTS courses.course_sharing (
    sharing_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID NOT NULL REFERENCES courses.courses(course_id) ON DELETE CASCADE,
    owner_organisation_id UUID NOT NULL REFERENCES organisations.organisations(organisation_id),
    shared_with_organisation_id UUID NOT NULL REFERENCES organisations.organisations(organisation_id),

    -- Sharing-Typ
    access_type VARCHAR(50) NOT NULL DEFAULT 'read', -- read|copy|resell
    revenue_share_percent INTEGER DEFAULT 0,

    -- Preise (wenn resell)
    price DECIMAL(10,2),
    license_type VARCHAR(50), -- one_time|subscription

    -- Status
    active BOOLEAN DEFAULT TRUE,
    shared_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,

    UNIQUE (course_id, shared_with_organisation_id)
);

CREATE INDEX idx_course_sharing_owner ON courses.course_sharing(owner_organisation_id);
CREATE INDEX idx_course_sharing_shared_with ON courses.course_sharing(shared_with_organisation_id);
CREATE INDEX idx_course_sharing_course ON courses.course_sharing(course_id);

COMMENT ON TABLE courses.course_sharing IS
'Ermöglicht Kurs-Sharing zwischen Organisationen (B2B, Community)';

COMMENT ON COLUMN courses.course_sharing.access_type IS
'read = Nur lesen, copy = Kopieren+Anpassen, resell = Verkaufen';

-- =====================================================
-- 5. White-Label Branding (erweitert)
-- =====================================================

CREATE TABLE IF NOT EXISTS organisations.branding (
    organisation_id UUID PRIMARY KEY REFERENCES organisations.organisations(organisation_id) ON DELETE CASCADE,

    -- Logos
    logo_url VARCHAR(500),
    logo_dark_url VARCHAR(500),
    favicon_url VARCHAR(500),

    -- Farben
    primary_color VARCHAR(7),     -- #1E40AF
    secondary_color VARCHAR(7),   -- #8B5CF6
    accent_color VARCHAR(7),      -- #10B981
    background_color VARCHAR(7),  -- #F3F4F6
    text_color VARCHAR(7),        -- #111827

    -- Fonts
    heading_font VARCHAR(100),    -- 'Inter'
    body_font VARCHAR(100),       -- 'Roboto'

    -- Custom CSS
    custom_css TEXT,

    -- Texte
    platform_name VARCHAR(100),
    tagline VARCHAR(200),
    welcome_message TEXT,

    -- Footer
    footer_text TEXT,
    contact_email VARCHAR(255),
    imprint_url VARCHAR(500),
    privacy_url VARCHAR(500),

    -- Social Links
    social_links JSONB DEFAULT '{}',

    updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE organisations.branding IS
'White-Label Branding-Konfiguration pro Organisation';

COMMENT ON COLUMN organisations.branding.social_links IS
'JSON: {"youtube": "url", "twitter": "url", "instagram": "url"}';

-- =====================================================
-- 6. Domain-Verifikation (erweitert)
-- =====================================================

CREATE TABLE IF NOT EXISTS organisations.custom_domains (
    domain_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organisation_id UUID NOT NULL REFERENCES organisations.organisations(organisation_id) ON DELETE CASCADE,

    domain VARCHAR(255) NOT NULL UNIQUE,

    -- Verifikation
    verification_code VARCHAR(255) NOT NULL,
    verification_method VARCHAR(50) DEFAULT 'cname', -- cname|txt|http
    verified BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMPTZ,

    -- SSL/TLS
    ssl_enabled BOOLEAN DEFAULT FALSE,
    ssl_certificate TEXT,
    ssl_expires_at TIMESTAMPTZ,

    -- Status
    active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_custom_domains_organisation ON organisations.custom_domains(organisation_id);
CREATE INDEX idx_custom_domains_domain ON organisations.custom_domains(domain);

COMMENT ON TABLE organisations.custom_domains IS
'Custom Domains für White-Label (z.B. lernportal.meineschule.de)';

-- =====================================================
-- 7. Organisation-Features Matrix
-- =====================================================

CREATE TABLE IF NOT EXISTS organisations.feature_flags (
    organisation_id UUID REFERENCES organisations.organisations(organisation_id) ON DELETE CASCADE,
    feature_code VARCHAR(100) NOT NULL,
    enabled BOOLEAN DEFAULT FALSE,
    config JSONB DEFAULT '{}',
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (organisation_id, feature_code)
);

CREATE INDEX idx_feature_flags_org ON organisations.feature_flags(organisation_id);

COMMENT ON TABLE organisations.feature_flags IS
'Feature-Flags pro Organisation (z.B. ai_enabled, liveroom_enabled)';

-- Standard-Features einfügen für neue Organisationen
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

-- =====================================================
-- 8. Organisation-Analytics
-- =====================================================

CREATE TABLE IF NOT EXISTS organisations.organisation_stats (
    stat_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organisation_id UUID NOT NULL REFERENCES organisations.organisations(organisation_id) ON DELETE CASCADE,

    -- Zeitraum
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,

    -- User-Statistiken
    active_users_count INTEGER DEFAULT 0,
    new_users_count INTEGER DEFAULT 0,
    total_users_count INTEGER DEFAULT 0,

    -- Kurs-Statistiken
    total_courses INTEGER DEFAULT 0,
    total_enrollments INTEGER DEFAULT 0,
    avg_completion_rate DECIMAL(5,2) DEFAULT 0.00,

    -- Token-Statistiken
    tokens_consumed INTEGER DEFAULT 0,
    tokens_purchased INTEGER DEFAULT 0,

    -- LiveRoom-Statistiken
    liveroom_minutes INTEGER DEFAULT 0,
    liveroom_sessions INTEGER DEFAULT 0,

    -- Prüfungen
    exams_taken INTEGER DEFAULT 0,
    avg_exam_score DECIMAL(5,2) DEFAULT 0.00,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_org_stats_organisation ON organisations.organisation_stats(organisation_id);
CREATE INDEX idx_org_stats_period ON organisations.organisation_stats(period_start, period_end);

COMMENT ON TABLE organisations.organisation_stats IS
'Monatliche Statistiken pro Organisation für Analytics & Billing';

-- =====================================================
-- 9. Helper-Funktionen
-- =====================================================

-- Funktion: Hole aktuelle Organisation eines Users
CREATE OR REPLACE FUNCTION get_user_organisation(p_user_id UUID)
RETURNS UUID AS $$
DECLARE
    v_org_id UUID;
BEGIN
    SELECT organisation_id INTO v_org_id
    FROM core.users
    WHERE user_id = p_user_id
    LIMIT 1;

    RETURN v_org_id;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_user_organisation IS
'Gibt Organisation-ID eines Users zurück';

-- Funktion: Prüfe ob User Zugriff auf Kurs hat
CREATE OR REPLACE FUNCTION can_access_course(
    p_user_id UUID,
    p_course_id UUID
) RETURNS BOOLEAN AS $$
DECLARE
    v_user_org UUID;
    v_course_org UUID;
    v_visibility VARCHAR(50);
    v_is_shared BOOLEAN;
BEGIN
    -- User-Organisation
    v_user_org := get_user_organisation(p_user_id);

    -- Kurs-Organisation und Visibility
    SELECT organisation_id, visibility INTO v_course_org, v_visibility
    FROM courses.courses
    WHERE course_id = p_course_id;

    -- NULL organisation_id = LSX Academy (alle haben Zugriff)
    IF v_course_org IS NULL THEN
        RETURN TRUE;
    END IF;

    -- Private: Nur eigene Organisation
    IF v_visibility = 'private' THEN
        RETURN v_user_org = v_course_org;
    END IF;

    -- Community/Marketplace: Global sichtbar
    IF v_visibility IN ('community', 'marketplace') THEN
        RETURN TRUE;
    END IF;

    -- Prüfe ob Kurs mit User-Organisation geteilt wurde
    SELECT EXISTS(
        SELECT 1 FROM courses.course_sharing
        WHERE course_id = p_course_id
        AND shared_with_organisation_id = v_user_org
        AND active = TRUE
    ) INTO v_is_shared;

    RETURN v_is_shared;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION can_access_course IS
'Prüft ob User Zugriff auf Kurs hat (basierend auf Organisation + Sharing)';

-- =====================================================
-- 10. Update bestehende Daten
-- =====================================================

-- LSX Academy Organisation erstellen (wenn nicht existiert)
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
    'school', -- Nutze existierenden Typ
    'revenue_share',
    0, -- LSX Academy zahlt keine Platform Fee
    'enterprise',
    TRUE
)
ON CONFLICT (organisation_id) DO NOTHING;

-- Alle bestehenden Kurse ohne organisation_id werden LSX Academy zugewiesen
UPDATE courses.courses
SET organisation_id = '00000000-0000-0000-0000-000000000001'::UUID
WHERE organisation_id IS NULL;

-- =====================================================
-- 11. Constraints & Validierung
-- =====================================================

-- Billing Model Check
ALTER TABLE organisations.organisations
DROP CONSTRAINT IF EXISTS chk_billing_model;

ALTER TABLE organisations.organisations
ADD CONSTRAINT chk_billing_model CHECK (
    billing_model IN ('per_user', 'flatrate', 'seat_based', 'revenue_share', 'hybrid', 'freemium')
);

-- Subscription Tier Check
ALTER TABLE organisations.organisations
ADD CONSTRAINT chk_subscription_tier CHECK (
    subscription_tier IN ('free', 'pro', 'enterprise')
);

-- Visibility Check
ALTER TABLE courses.courses
DROP CONSTRAINT IF EXISTS chk_visibility;

ALTER TABLE courses.courses
ADD CONSTRAINT chk_visibility CHECK (
    visibility IN ('private', 'community', 'marketplace', 'public')
);

-- Course Sharing Access Type Check
ALTER TABLE courses.course_sharing
ADD CONSTRAINT chk_access_type CHECK (
    access_type IN ('read', 'copy', 'resell')
);

-- =====================================================
-- 12. Triggers
-- =====================================================

-- Trigger: Setze organisation_id automatisch bei Kurs-Erstellung
CREATE OR REPLACE FUNCTION set_course_organisation()
RETURNS TRIGGER AS $$
BEGIN
    -- Wenn organisation_id nicht gesetzt, vom Creator übernehmen
    IF NEW.organisation_id IS NULL THEN
        NEW.organisation_id := get_user_organisation(NEW.creator_id);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_set_course_organisation
BEFORE INSERT ON courses.courses
FOR EACH ROW
EXECUTE FUNCTION set_course_organisation();

-- Trigger: Update updated_at bei Branding-Änderungen
CREATE OR REPLACE FUNCTION update_branding_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_branding_timestamp
BEFORE UPDATE ON organisations.branding
FOR EACH ROW
EXECUTE FUNCTION update_branding_timestamp();

-- =====================================================
-- ENDE Migration 076
-- =====================================================

-- Verify
DO $$
BEGIN
    RAISE NOTICE '✅ Migration 076: Multi-Tenancy Extensions erfolgreich';
    RAISE NOTICE 'Neue Tabellen:';
    RAISE NOTICE '  - courses.course_sharing';
    RAISE NOTICE '  - organisations.branding';
    RAISE NOTICE '  - organisations.custom_domains';
    RAISE NOTICE '  - organisations.feature_flags';
    RAISE NOTICE '  - organisations.organisation_stats';
    RAISE NOTICE 'Erweiterte Spalten:';
    RAISE NOTICE '  - organisation_id in 10+ Tabellen';
    RAISE NOTICE '  - Erweiterte Billing-Modelle (6 Typen)';
    RAISE NOTICE '  - Erweiterte Visibility (private/community/marketplace)';
END $$;
