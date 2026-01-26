-- ============================================================================
-- Migration: 076_multi_tenancy_extensions_part2.sql
-- Description: Multi-Tenancy Extensions - Part 2: Additional Features
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-01-16
-- ============================================================================
-- Note: Split from original 076_multi_tenancy_extensions.sql (510 lines)
--       Part 2 of 2
-- ============================================================================

-- ============================================================================
-- Seed Data Relocation Notice
-- ============================================================================
-- The following seed data statements have been moved to dedicated seed files:
-- - Feature flags per organisation → 00_Seeds/14_organisation_feature_flags.sql
-- - LSX Academy organisation creation → 00_Seeds/14_organisation_feature_flags.sql
-- - Course ownership migration → 00_Seeds/14_organisation_feature_flags.sql
--
-- This migration file now contains ONLY structural CREATE statements.

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
-- 10. Constraints & Validierung
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
-- 11. Triggers
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
