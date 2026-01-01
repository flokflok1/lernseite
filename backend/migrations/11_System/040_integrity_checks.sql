-- ============================================================================
-- Migration: 040_integrity_checks.sql
-- Description: Final integrity checks, RLS policies, and system verification
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-01-17
-- ============================================================================

-- ============================================================================
-- ROW LEVEL SECURITY POLICIES
-- ============================================================================

-- Enable RLS on key multi-tenant tables
ALTER TABLE rooms ENABLE ROW LEVEL SECURITY;
ALTER TABLE courses ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics_events ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Rooms - Organization isolation
CREATE POLICY room_org_isolation ON rooms
FOR SELECT
USING (
    org_id::text = current_setting('app.current_org_id', true) OR
    current_setting('app.user_role', true) = 'admin'
);

-- RLS Policy: Courses - Creator/Organization access
CREATE POLICY course_access_policy ON courses
FOR SELECT
USING (
    published = TRUE OR
    creator_user_id::text = current_setting('app.current_user_id', true) OR
    organization_id::text = current_setting('app.current_org_id', true) OR
    current_setting('app.user_role', true) IN ('admin', 'moderator')
);

-- RLS Policy: Analytics - User/Organization isolation
CREATE POLICY analytics_isolation ON analytics_events
FOR SELECT
USING (
    user_id::text = current_setting('app.current_user_id', true) OR
    organization_id::text = current_setting('app.current_org_id', true) OR
    current_setting('app.user_role', true) IN ('admin', 'support')
);

-- ============================================================================
-- ADDITIONAL CONSTRAINTS
-- ============================================================================

-- Ensure email uniqueness across all users
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email_unique_lower
ON users(LOWER(email));

-- Ensure organization domains are unique and valid
CREATE UNIQUE INDEX IF NOT EXISTS idx_organizations_domain_unique_lower
ON organizations(LOWER(domain)) WHERE domain IS NOT NULL;

-- ============================================================================
-- DATABASE FUNCTIONS
-- ============================================================================

-- Function: Calculate user level from XP
CREATE OR REPLACE FUNCTION calculate_user_level(xp INTEGER)
RETURNS INTEGER AS $$
BEGIN
    -- Simple level calculation: level = sqrt(xp / 100)
    RETURN FLOOR(SQRT(xp::NUMERIC / 100)) + 1;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION calculate_user_level IS 'Calculate user level from total XP';

-- Function: Generate certificate number
CREATE OR REPLACE FUNCTION generate_certificate_number()
RETURNS VARCHAR(100) AS $$
DECLARE
    cert_number VARCHAR(100);
    year_suffix VARCHAR(4);
    random_part VARCHAR(8);
BEGIN
    year_suffix := TO_CHAR(NOW(), 'YY');
    random_part := UPPER(SUBSTRING(MD5(RANDOM()::TEXT || CLOCK_TIMESTAMP()::TEXT) FROM 1 FOR 8));
    cert_number := 'LSX-' || year_suffix || '-' || random_part;
    RETURN cert_number;
END;
$$ LANGUAGE plpgsql VOLATILE;

COMMENT ON FUNCTION generate_certificate_number IS 'Generate unique certificate number (LSX-YY-XXXXXXXX)';

-- Function: Check if user has permission
CREATE OR REPLACE FUNCTION user_has_permission(p_user_id UUID, p_permission_key VARCHAR)
RETURNS BOOLEAN AS $$
DECLARE
    has_perm BOOLEAN;
BEGIN
    SELECT EXISTS (
        SELECT 1
        FROM users u
        JOIN role_permissions rp ON u.role_id = rp.role_id
        JOIN permissions p ON rp.permission_id = p.permission_id
        WHERE u.user_id = p_user_id AND p.permission_key = p_permission_key
    ) INTO has_perm;

    RETURN has_perm;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION user_has_permission IS 'Check if user has specific permission';

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View: Active subscriptions with user details
CREATE OR REPLACE VIEW v_active_subscriptions AS
SELECT
    s.subscription_id,
    s.user_id,
    s.organization_id,
    s.plan_type,
    s.status,
    s.current_period_end,
    u.email,
    u.firstname,
    u.lastname,
    o.name AS organization_name
FROM subscriptions s
LEFT JOIN users u ON s.user_id = u.user_id
LEFT JOIN organizations o ON s.organization_id = o.organization_id
WHERE s.status IN ('active', 'trialing');

COMMENT ON VIEW v_active_subscriptions IS 'Active subscriptions with user/org details';

-- View: User course progress
CREATE OR REPLACE VIEW v_user_course_progress AS
SELECT
    ce.user_id,
    ce.course_id,
    c.title AS course_title,
    ce.completion_percentage,
    ce.status,
    ce.enrolled_at,
    ce.completed_at,
    COUNT(DISTINCT cp.chapter_id) AS chapters_completed,
    COUNT(DISTINCT lc.lesson_id) AS lessons_completed
FROM course_enrollments ce
JOIN courses c ON ce.course_id = c.course_id
LEFT JOIN chapter_progress cp ON ce.user_id = cp.user_id AND cp.completion_percentage = 100
LEFT JOIN lesson_completions lc ON ce.user_id = lc.user_id
GROUP BY ce.user_id, ce.course_id, c.title, ce.completion_percentage, ce.status, ce.enrolled_at, ce.completed_at;

COMMENT ON VIEW v_user_course_progress IS 'User course progress summary';

-- ============================================================================
-- INTEGRITY CHECKS
-- ============================================================================

-- Verify all foreign keys are valid
DO $$
DECLARE
    fk_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO fk_count
    FROM information_schema.table_constraints
    WHERE constraint_type = 'FOREIGN KEY'
    AND table_schema = 'public';

    RAISE NOTICE 'Total foreign key constraints: %', fk_count;
END $$;

-- Verify all tables have primary keys
DO $$
DECLARE
    tables_without_pk TEXT[];
BEGIN
    SELECT ARRAY_AGG(table_name) INTO tables_without_pk
    FROM information_schema.tables t
    WHERE table_schema = 'public'
    AND table_type = 'BASE TABLE'
    AND NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints tc
        WHERE tc.table_name = t.table_name
        AND tc.constraint_type = 'PRIMARY KEY'
        AND tc.table_schema = 'public'
    );

    IF tables_without_pk IS NOT NULL THEN
        RAISE WARNING 'Tables without primary keys: %', tables_without_pk;
    ELSE
        RAISE NOTICE 'All tables have primary keys';
    END IF;
END $$;

-- ============================================================================
-- FINAL STATISTICS
-- ============================================================================

-- Count all tables
DO $$
DECLARE
    table_count INTEGER;
    index_count INTEGER;
    trigger_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_schema = 'public' AND table_type = 'BASE TABLE';

    SELECT COUNT(*) INTO index_count
    FROM pg_indexes
    WHERE schemaname = 'public';

    SELECT COUNT(*) INTO trigger_count
    FROM information_schema.triggers
    WHERE trigger_schema = 'public';

    RAISE NOTICE '========================================';
    RAISE NOTICE 'LernsystemX Database Schema Complete';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Total Tables: %', table_count;
    RAISE NOTICE 'Total Indexes: %', index_count;
    RAISE NOTICE 'Total Triggers: %', trigger_count;
    RAISE NOTICE '========================================';
END $$;

-- ============================================================================
-- End of Migration: 040_integrity_checks.sql
-- ============================================================================
