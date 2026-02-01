-- ============================================================================
-- Migration: 011_multi_tenancy_extensions_part2.sql
-- Description: Multi-Tenancy Extensions - Part 2: Additional Features
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-01-16
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. Row-Level Security (RLS) aktivieren
-- ============================================================================

-- Aktiviere RLS für feature_flags
ALTER TABLE organisations.feature_flags ENABLE ROW LEVEL SECURITY;

COMMENT ON TABLE organisations.feature_flags IS
'Feature-Flags pro Organisation (z.B. ai_enabled, liveroom_enabled)';

-- ============================================================================
-- 2. Auditierung für Organization-Änderungen
-- ============================================================================

CREATE TABLE IF NOT EXISTS organisations.organisation_audit (
    audit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organisation_id UUID NOT NULL REFERENCES organisations.organisations(organisation_id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL,
    changed_by UUID,
    old_values JSONB,
    new_values JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_org_audit_id ON organisations.organisation_audit(organisation_id);
CREATE INDEX IF NOT EXISTS idx_org_audit_action ON organisations.organisation_audit(action);
CREATE INDEX IF NOT EXISTS idx_org_audit_created ON organisations.organisation_audit(created_at DESC);

COMMENT ON TABLE organisations.organisation_audit IS 'Audit trail für Organisation changes';

COMMIT;
