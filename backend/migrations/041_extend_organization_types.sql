-- ============================================================================
-- Migration: Extend Organization Types
-- Version: 041
-- Description: Add academy, creator_org, community, and system types to organizations
-- Author: Setup Wizard Fix
-- Date: 2025-11-18
-- ============================================================================

-- Drop existing constraint
ALTER TABLE organizations
DROP CONSTRAINT IF EXISTS chk_org_type;

-- Add new constraint with all organization types
ALTER TABLE organizations
ADD CONSTRAINT chk_org_type CHECK (
    type IN ('school', 'company', 'academy', 'creator_org', 'community', 'system')
);

-- Add comment
COMMENT ON CONSTRAINT chk_org_type ON organizations IS
'Valid organization types: school, company, academy, creator_org, community, system';
