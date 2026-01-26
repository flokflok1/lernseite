-- ============================================================================
-- 032_create_learning_method_groups.sql
-- 
-- Create master table for learning method groups (A, B, C, etc.)
-- This enables full database-driven group configuration - no hardcoding!
-- ============================================================================

-- Create the groups catalog table
CREATE TABLE IF NOT EXISTS learning_methods.learning_method_groups (
    group_code VARCHAR(1) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    icon VARCHAR(50),
    sort_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CHECK (group_code ~ '^[A-Z]$'),  -- Only uppercase letters
    UNIQUE(sort_order)
);

-- Add comment for clarity
COMMENT ON TABLE learning_methods.learning_method_groups IS 
    'Master catalog of learning method groups. Enables dynamic group configuration without code changes.';

COMMENT ON COLUMN learning_methods.learning_method_groups.group_code IS 
    'Group code (A, B, C, etc.) - primary identifier';

COMMENT ON COLUMN learning_methods.learning_method_groups.name IS 
    'User-friendly group name (e.g., "Erklärend", "Praxis")';

COMMENT ON COLUMN learning_methods.learning_method_groups.icon IS 
    'Unicode emoji or icon for UI display';

COMMENT ON COLUMN learning_methods.learning_method_groups.sort_order IS 
    'Display order in UI and admin panels';

COMMENT ON COLUMN learning_methods.learning_method_groups.is_active IS 
    'Whether this group is currently active (used for soft-delete)';

-- Insert initial data (the 3 core groups)
INSERT INTO learning_methods.learning_method_groups 
    (group_code, name, description, icon, sort_order, is_active)
VALUES
    ('A', 'Erklärend', 'Verständnis & Wissensvermittlung - Theorie und Erklärungen', '📖', 1, TRUE),
    ('B', 'Praxis', 'Anwenden & Trainieren - Übungen und praktische Aufgaben', '✏️', 2, TRUE),
    ('C', 'Prüfung', 'Kompetenznachweis & Bewertung - Prüfungen und Tests', '📝', 3, TRUE)
ON CONFLICT (group_code) DO NOTHING;

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_learning_method_groups_active 
ON learning_methods.learning_method_groups(is_active);

CREATE INDEX IF NOT EXISTS idx_learning_method_groups_sort 
ON learning_methods.learning_method_groups(sort_order);
