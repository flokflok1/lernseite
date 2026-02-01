-- ============================================================================
-- Migration: 049_flexible_categories.sql
-- Description: Upgrade to flexible unlimited-depth category system
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-01-XX
-- ============================================================================

-- ============================================================================
-- STEP 1: Remove the level limit constraint
-- ============================================================================
ALTER TABLE courses.course_categories DROP CONSTRAINT IF EXISTS chk_category_level;

-- Add new constraint allowing unlimited depth (practical limit 20)
ALTER TABLE courses.course_categories ADD CONSTRAINT chk_category_level
    CHECK (level >= 1 AND level <= 20);

-- ============================================================================
-- STEP 2: Add new columns for performance optimization
-- ============================================================================

-- Path: Full path from root (e.g., "IT/Netzwerk/Cisco/CCNA")
ALTER TABLE courses.course_categories
    ADD COLUMN IF NOT EXISTS path TEXT;

-- Root ID: Quick access to root category
ALTER TABLE courses.course_categories
    ADD COLUMN IF NOT EXISTS root_id INTEGER REFERENCES courses.course_categories(category_id) ON DELETE CASCADE;

-- Depth: Alias for level (renamed for clarity), keeping level for backwards compatibility
-- We use level column that already exists

-- Full path with IDs for queries
ALTER TABLE courses.course_categories
    ADD COLUMN IF NOT EXISTS path_ids INTEGER[];

-- Multilingual names
ALTER TABLE courses.course_categories
    ADD COLUMN IF NOT EXISTS name_en VARCHAR(100);

ALTER TABLE courses.course_categories
    ADD COLUMN IF NOT EXISTS name_es VARCHAR(100);

ALTER TABLE courses.course_categories
    ADD COLUMN IF NOT EXISTS name_fr VARCHAR(100);

-- Course count cache
ALTER TABLE courses.course_categories
    ADD COLUMN IF NOT EXISTS course_count INTEGER DEFAULT 0;

-- Total courses including children
ALTER TABLE courses.course_categories
    ADD COLUMN IF NOT EXISTS total_course_count INTEGER DEFAULT 0;

-- SEO & Metadata
ALTER TABLE courses.course_categories
    ADD COLUMN IF NOT EXISTS meta_title VARCHAR(255);

ALTER TABLE courses.course_categories
    ADD COLUMN IF NOT EXISTS meta_description TEXT;

-- Created/Updated by
ALTER TABLE courses.course_categories
    ADD COLUMN IF NOT EXISTS created_by UUID;

ALTER TABLE courses.course_categories
    ADD COLUMN IF NOT EXISTS updated_by UUID;

-- ============================================================================
-- STEP 3: Create indexes for new columns
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_course_categories_path ON courses.course_categories (path);
CREATE INDEX IF NOT EXISTS idx_course_categories_root ON courses.course_categories (root_id);
CREATE INDEX IF NOT EXISTS idx_course_categories_path_ids ON courses.course_categories USING GIN(path_ids);

-- ============================================================================
-- STEP 4: Function to calculate path and related fields
-- ============================================================================
CREATE OR REPLACE FUNCTION calculate_category_path()
RETURNS TRIGGER AS $$
DECLARE
    parent_path TEXT;
    parent_path_ids INTEGER[];
    parent_root_id INTEGER;
    parent_level INTEGER;
BEGIN
    IF NEW.parent_id IS NULL THEN
        -- Root category
        NEW.path := NEW.name;
        NEW.path_ids := ARRAY[NEW.category_id];
        NEW.root_id := NEW.category_id;
        NEW.level := 1;
    ELSE
        -- Get parent info
        SELECT path, path_ids, root_id, level
        INTO parent_path, parent_path_ids, parent_root_id, parent_level
        FROM courses.course_categories
        WHERE category_id = NEW.parent_id;

        -- Calculate new values
        NEW.path := parent_path || '/' || NEW.name;
        NEW.path_ids := parent_path_ids || NEW.category_id;
        NEW.root_id := parent_root_id;
        NEW.level := parent_level + 1;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- STEP 5: Create trigger for automatic path calculation
-- ============================================================================
DROP TRIGGER IF EXISTS trigger_calculate_category_path ON courses.course_categories;

CREATE TRIGGER trigger_calculate_category_path
    BEFORE INSERT OR UPDATE OF parent_id, name ON courses.course_categories
    FOR EACH ROW
    EXECUTE FUNCTION calculate_category_path();

-- ============================================================================
-- STEP 6: Function to update paths when category is moved
-- ============================================================================
CREATE OR REPLACE FUNCTION update_children_paths()
RETURNS TRIGGER AS $$
BEGIN
    -- Update all children recursively when parent path changes
    IF OLD.path IS DISTINCT FROM NEW.path THEN
        UPDATE courses.course_categories
        SET path = NEW.path || '/' || name,
            root_id = NEW.root_id,
            path_ids = NEW.path_ids || category_id,
            level = NEW.level + 1,
            updated_at = NOW()
        WHERE parent_id = NEW.category_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_children_paths ON courses.course_categories;

CREATE TRIGGER trigger_update_children_paths
    AFTER UPDATE OF path ON courses.course_categories
    FOR EACH ROW
    EXECUTE FUNCTION update_children_paths();

-- ============================================================================
-- STEP 7: Function to update course counts
-- ============================================================================
CREATE OR REPLACE FUNCTION update_category_course_counts()
RETURNS TRIGGER AS $$
BEGIN
    -- Update direct course count
    UPDATE courses.course_categories cc
    SET course_count = (
        SELECT COUNT(*) FROM courses.courses c
        WHERE c.category_id = cc.category_id
    )
    WHERE cc.category_id IN (OLD.category_id, NEW.category_id);

    -- Update total course count (including children) - recursive
    WITH RECURSIVE category_tree AS (
        SELECT category_id, parent_id, category_id as root_cat
        FROM courses.course_categories
        WHERE category_id IN (OLD.category_id, NEW.category_id)

        UNION ALL

        SELECT cc.category_id, cc.parent_id, ct.root_cat
        FROM courses.course_categories cc
        JOIN category_tree ct ON cc.parent_id = ct.category_id
    )
    UPDATE courses.course_categories cc
    SET total_course_count = (
        SELECT COUNT(*) FROM courses.courses c
        JOIN category_tree ct ON c.category_id = ct.category_id
        WHERE ct.root_cat = cc.category_id
    )
    WHERE cc.category_id IN (
        SELECT DISTINCT root_cat FROM category_tree
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger on courses table
DROP TRIGGER IF EXISTS trigger_update_category_counts ON courses.courses;

CREATE TRIGGER trigger_update_category_counts
    AFTER INSERT OR UPDATE OF category_id OR DELETE ON courses.courses
    FOR EACH ROW
    EXECUTE FUNCTION update_category_course_counts();

-- ============================================================================
-- STEP 8: Update existing categories with path information
-- ============================================================================
-- First, update root categories
UPDATE courses.course_categories
SET path = name,
    path_ids = ARRAY[category_id],
    root_id = category_id
WHERE parent_id IS NULL;

-- Then recursively update children (run multiple times for deep hierarchies)
DO $$
DECLARE
    rows_updated INTEGER := 1;
    iteration INTEGER := 0;
BEGIN
    WHILE rows_updated > 0 AND iteration < 20 LOOP
        WITH parent_info AS (
            SELECT
                c.category_id,
                p.path || '/' || c.name as new_path,
                p.path_ids || c.category_id as new_path_ids,
                p.root_id as new_root_id,
                p.level + 1 as new_level
            FROM courses.course_categories c
            JOIN courses.course_categories p ON c.parent_id = p.category_id
            WHERE c.path IS NULL AND p.path IS NOT NULL
        )
        UPDATE courses.course_categories c
        SET path = pi.new_path,
            path_ids = pi.new_path_ids,
            root_id = pi.new_root_id,
            level = pi.new_level
        FROM parent_info pi
        WHERE c.category_id = pi.category_id;

        GET DIAGNOSTICS rows_updated = ROW_COUNT;
        iteration := iteration + 1;
    END LOOP;
END $$;

-- ============================================================================
-- STEP 9: Update course counts for all categories
-- ============================================================================
UPDATE courses.course_categories cc
SET course_count = (
    SELECT COUNT(*) FROM courses.courses c
    WHERE c.category_id = cc.category_id
);

-- ============================================================================
-- STEP 10: Helper function to get category breadcrumbs
-- ============================================================================
CREATE OR REPLACE FUNCTION get_category_breadcrumbs(p_category_id INTEGER)
RETURNS TABLE (
    category_id INTEGER,
    name VARCHAR(100),
    slug VARCHAR(100),
    level INTEGER
) AS $$
BEGIN
    RETURN QUERY
    WITH RECURSIVE breadcrumbs AS (
        SELECT cc.category_id, cc.name, cc.slug, cc.level, cc.parent_id
        FROM courses.course_categories cc
        WHERE cc.category_id = p_category_id

        UNION ALL

        SELECT cc.category_id, cc.name, cc.slug, cc.level, cc.parent_id
        FROM courses.course_categories cc
        JOIN breadcrumbs b ON cc.category_id = b.parent_id
    )
    SELECT b.category_id, b.name, b.slug, b.level
    FROM breadcrumbs b
    ORDER BY b.level ASC;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- STEP 11: Helper function to get category children
-- ============================================================================
CREATE OR REPLACE FUNCTION get_category_children(p_category_id INTEGER, p_direct_only BOOLEAN DEFAULT FALSE)
RETURNS TABLE (
    category_id INTEGER,
    name VARCHAR(100),
    slug VARCHAR(100),
    level INTEGER,
    parent_id INTEGER,
    course_count INTEGER
) AS $$
BEGIN
    IF p_direct_only THEN
        RETURN QUERY
        SELECT cc.category_id, cc.name, cc.slug, cc.level, cc.parent_id, cc.course_count
        FROM courses.course_categories cc
        WHERE cc.parent_id = p_category_id AND cc.active = TRUE
        ORDER BY cc.order_index, cc.name;
    ELSE
        RETURN QUERY
        WITH RECURSIVE children AS (
            SELECT cc.category_id, cc.name, cc.slug, cc.level, cc.parent_id, cc.course_count
            FROM courses.course_categories cc
            WHERE cc.parent_id = p_category_id AND cc.active = TRUE

            UNION ALL

            SELECT cc.category_id, cc.name, cc.slug, cc.level, cc.parent_id, cc.course_count
            FROM courses.course_categories cc
            JOIN children c ON cc.parent_id = c.category_id
            WHERE cc.active = TRUE
        )
        SELECT * FROM children
        ORDER BY level, name;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- STEP 12: View for category tree
-- ============================================================================
CREATE OR REPLACE VIEW v_category_tree AS
SELECT
    cc.category_id,
    cc.parent_id,
    cc.name,
    cc.slug,
    cc.description,
    cc.icon,
    cc.color,
    cc.level,
    cc.path,
    cc.path_ids,
    cc.root_id,
    cc.order_index,
    cc.active,
    cc.course_count,
    cc.total_course_count,
    cc.name_en,
    cc.created_at,
    cc.updated_at,
    -- Computed: indent for display
    repeat('  ', cc.level - 1) || cc.name as indented_name,
    -- Computed: has children
    EXISTS(SELECT 1 FROM courses.course_categories child WHERE child.parent_id = cc.category_id) as has_children
FROM courses.course_categories cc
ORDER BY cc.path;

COMMENT ON VIEW v_category_tree IS 'Hierarchical view of all categories with computed fields';

-- ============================================================================
-- End of Migration: 049_flexible_categories.sql
-- ============================================================================
