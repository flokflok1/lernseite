-- ============================================================================
-- 034_add_tier_to_learning_method_groups.sql
--
-- Add `tier` column to learning_method_groups table.
-- This enables database-driven tier assignment per group (no hardcoding!).
--
-- Business Logic:
-- - Groups A, B → basic tier (explanatory and practice)
-- - Group C → premium tier (assessment/exams)
-- - Allows future groups to have any tier configuration
-- ============================================================================

-- Add tier column to groups table
ALTER TABLE IF EXISTS learning_methods.learning_method_groups
ADD COLUMN IF NOT EXISTS tier VARCHAR(50) DEFAULT 'basic' NOT NULL;

-- Add constraint to ensure valid tiers
ALTER TABLE IF EXISTS learning_methods.learning_method_groups
ADD CONSTRAINT chk_group_tier CHECK (tier IN ('basic', 'premium', 'enterprise'));

-- Update existing groups with correct tiers (database-driven, not hardcoded!)
UPDATE learning_methods.learning_method_groups
SET tier = CASE
    WHEN group_code IN ('A', 'B') THEN 'basic'
    WHEN group_code = 'C' THEN 'premium'
    ELSE 'basic'
END
WHERE tier = 'basic';  -- Only update defaults (not explicitly set tiers)

-- Add comment
COMMENT ON COLUMN learning_methods.learning_method_groups.tier IS
    'Tier level for this group (basic, premium, enterprise) - enables dynamic tier assignment per group';

-- Create index for tier lookups
CREATE INDEX IF NOT EXISTS idx_learning_method_groups_tier
ON learning_methods.learning_method_groups(tier);
