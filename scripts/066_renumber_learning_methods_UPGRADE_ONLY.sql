-- ============================================================================
-- Migration 066: Renumber Learning Methods (lm00-lm25 → lm00-lm18)
-- ============================================================================
--
-- PURPOSE: Remove gaps in Learning Method numbering for cleaner architecture
--
-- OLD SYSTEM (with gaps):
--   Gruppe A: lm00, lm01, lm02, lm03, lm06
--   Gruppe B: lm08, lm12, lm13, lm14, lm15, lm17
--   Gruppe C: lm18, lm19, lm20, lm21, lm22, lm23, lm24, lm25
--
-- NEW SYSTEM (continuous):
--   Gruppe A: lm00-lm04 (5 methods)
--   Gruppe B: lm05-lm10 (6 methods)
--   Gruppe C: lm11-lm18 (8 methods)
--
-- REASON FOR GAPS: lm04, lm05, lm07, lm09-lm11, lm16 became System-Features
-- ============================================================================

BEGIN;

-- Temporary table to avoid conflicts during renumbering
CREATE TEMP TABLE lm_renumber_map (
    old_type INT,
    new_type INT
);

INSERT INTO lm_renumber_map (old_type, new_type) VALUES
    -- Gruppe A (unchanged except lm06 → lm04)
    (0, 0),   -- lm00 → lm00
    (1, 1),   -- lm01 → lm01
    (2, 2),   -- lm02 → lm02
    (3, 3),   -- lm03 → lm03
    (6, 4),   -- lm06 → lm04
    -- Gruppe B (lm08-lm17 → lm05-lm10)
    (8, 5),   -- lm08 → lm05
    (12, 6),  -- lm12 → lm06
    (13, 7),  -- lm13 → lm07
    (14, 8),  -- lm14 → lm08
    (15, 9),  -- lm15 → lm09
    (17, 10), -- lm17 → lm10
    -- Gruppe C (lm18-lm25 → lm11-lm18)
    (18, 11), -- lm18 → lm11
    (19, 12), -- lm19 → lm12
    (20, 13), -- lm20 → lm13
    (21, 14), -- lm21 → lm14
    (22, 15), -- lm22 → lm15
    (23, 16), -- lm23 → lm16
    (24, 17), -- lm24 → lm17
    (25, 18); -- lm25 → lm18

-- Step 1: Add temporary column to track new values
ALTER TABLE learning_methods.learning_method_types ADD COLUMN new_method_type INT;
ALTER TABLE learning_methods.learning_method_instances ADD COLUMN new_method_type INT;

-- Step 2: Populate new values from mapping
UPDATE learning_methods.learning_method_types AS lmt
SET new_method_type = lrm.new_type
FROM lm_renumber_map AS lrm
WHERE lmt.method_type = lrm.old_type;

UPDATE learning_methods.learning_method_instances AS lmi
SET new_method_type = lrm.new_type
FROM lm_renumber_map AS lrm
WHERE lmi.method_type = lrm.old_type;

-- Step 3: Drop old columns and rename new ones
ALTER TABLE learning_methods.learning_method_types DROP COLUMN method_type;
ALTER TABLE learning_methods.learning_method_types RENAME COLUMN new_method_type TO method_type;

ALTER TABLE learning_methods.learning_method_instances DROP COLUMN method_type;
ALTER TABLE learning_methods.learning_method_instances RENAME COLUMN new_method_type TO method_type;

-- Step 4: Update constraints (if any exist)
-- method_type should be BETWEEN 0 AND 18 now instead of 0 AND 31

-- Step 5: Verify counts
DO $$
DECLARE
    type_count INT;
    instance_count INT;
BEGIN
    SELECT COUNT(*) INTO type_count FROM learning_methods.learning_method_types WHERE method_type BETWEEN 0 AND 18;
    SELECT COUNT(*) INTO instance_count FROM learning_methods.learning_method_instances WHERE method_type BETWEEN 0 AND 18;

    RAISE NOTICE 'Renumbering complete:';
    RAISE NOTICE '  learning_method_types: % rows updated', type_count;
    RAISE NOTICE '  learning_method_instances: % rows updated', instance_count;
END $$;

COMMIT;

-- ============================================================================
-- END Migration 066
-- ============================================================================
