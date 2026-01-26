-- ============================================================================
-- 033_refactor_group_constraint_to_fk.sql
--
-- Replace hardcoded CHECK constraint with Foreign Key to learning_method_groups
-- This makes group validation database-driven instead of hardcoded
-- ============================================================================

-- Step 1: Drop the old hardcoded CHECK constraint
ALTER TABLE IF EXISTS learning_methods.learning_method_types
DROP CONSTRAINT IF EXISTS chk_group_code;

-- Step 2: Add Foreign Key constraint to the new groups table
-- This ensures group_code references actual rows in learning_method_groups
ALTER TABLE learning_methods.learning_method_types
ADD CONSTRAINT fk_learning_method_group
    FOREIGN KEY (group_code)
    REFERENCES learning_methods.learning_method_groups(group_code)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- Step 3: Add comment explaining the relationship
COMMENT ON CONSTRAINT fk_learning_method_group 
ON learning_methods.learning_method_types IS 
    'Foreign key to learning_method_groups table - ensures group_code is valid and database-driven';

-- Verify: Count groups and learning methods
-- SELECT COUNT(*) as group_count FROM learning_methods.learning_method_groups;
-- SELECT COUNT(*) as lm_count FROM learning_methods.learning_method_types;
