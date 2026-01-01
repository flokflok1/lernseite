-- ============================================================================
-- Migration: 008_courses.sql
-- Description: Core course tables (courses, categories, access)
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-01-17
-- ============================================================================

-- ============================================================================
-- TABLE: course_categories
-- Description: 5-level hierarchical course categorization
-- ============================================================================
CREATE TABLE IF NOT EXISTS course_categories (
    category_id SERIAL PRIMARY KEY,
    parent_id INTEGER REFERENCES course_categories(category_id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    icon VARCHAR(50),
    color VARCHAR(7),
    level INTEGER NOT NULL DEFAULT 1,
    order_index INTEGER DEFAULT 0,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_category_level CHECK (level >= 1 AND level <= 5)
);

CREATE INDEX IF NOT EXISTS idx_course_categories_parent ON course_categories(parent_id);
CREATE INDEX IF NOT EXISTS idx_course_categories_slug ON course_categories(slug);
CREATE INDEX IF NOT EXISTS idx_course_categories_level ON course_categories(level);
CREATE INDEX IF NOT EXISTS idx_course_categories_active ON course_categories(active) WHERE active = TRUE;
CREATE INDEX IF NOT EXISTS idx_course_categories_order ON course_categories(parent_id, order_index);

COMMENT ON TABLE course_categories IS '5-level hierarchical course categorization system';

-- ============================================================================
-- TABLE: courses
-- Description: Core courses table
-- ============================================================================
CREATE TABLE IF NOT EXISTS courses (
    course_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    creator_user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    organization_id UUID REFERENCES organizations(organization_id) ON DELETE SET NULL,
    course_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE,
    description TEXT,
    long_description TEXT,
    category_id INTEGER REFERENCES course_categories(category_id) ON DELETE SET NULL,
    level VARCHAR(50),
    language_default VARCHAR(10) DEFAULT 'de',
    duration_hours INTEGER,
    thumbnail_url VARCHAR(500),
    video_preview_url VARCHAR(500),
    tags TEXT[],
    published BOOLEAN DEFAULT FALSE,
    published_at TIMESTAMPTZ,
    featured BOOLEAN DEFAULT FALSE,
    price DECIMAL(10,2) DEFAULT 0,
    original_price DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'EUR',
    enrollment_count INTEGER DEFAULT 0,
    average_rating DECIMAL(3,2),
    review_count INTEGER DEFAULT 0,
    view_count INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'draft',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_course_type CHECK (course_type IN ('academy', 'creator', 'community', 'organization')),
    CONSTRAINT chk_course_level CHECK (level IN ('beginner', 'intermediate', 'advanced', 'expert')),
    CONSTRAINT chk_course_status CHECK (status IN ('draft', 'review', 'published', 'archived', 'deleted'))
);

CREATE INDEX IF NOT EXISTS idx_courses_creator ON courses(creator_user_id);
CREATE INDEX IF NOT EXISTS idx_courses_org ON courses(organization_id);
CREATE INDEX IF NOT EXISTS idx_courses_type ON courses(course_type);
CREATE INDEX IF NOT EXISTS idx_courses_category ON courses(category_id);
CREATE INDEX IF NOT EXISTS idx_courses_published ON courses(published, published_at DESC);
CREATE INDEX IF NOT EXISTS idx_courses_status ON courses(status);
CREATE INDEX IF NOT EXISTS idx_courses_slug ON courses(slug);
CREATE INDEX IF NOT EXISTS idx_courses_featured ON courses(featured) WHERE featured = TRUE;
CREATE INDEX IF NOT EXISTS idx_courses_language ON courses(language_default);
CREATE INDEX IF NOT EXISTS idx_courses_tags ON courses USING GIN(tags);

COMMENT ON TABLE courses IS 'Core courses table supporting academy, creator, community, and organization courses';

-- ============================================================================
-- TABLE: course_access
-- Description: Course access control and enrollment
-- ============================================================================
CREATE TABLE IF NOT EXISTS course_access (
    access_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID REFERENCES courses(course_id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    access_type VARCHAR(50) NOT NULL,
    granted_by UUID REFERENCES users(user_id) ON DELETE SET NULL,
    granted_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    revoked BOOLEAN DEFAULT FALSE,
    revoked_at TIMESTAMPTZ,
    CONSTRAINT chk_access_type CHECK (access_type IN ('purchased', 'assigned', 'free', 'premium', 'trial', 'gifted')),
    UNIQUE (course_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_course_access_course ON course_access(course_id);
CREATE INDEX IF NOT EXISTS idx_course_access_user ON course_access(user_id);
CREATE INDEX IF NOT EXISTS idx_course_access_type ON course_access(access_type);
CREATE INDEX IF NOT EXISTS idx_course_access_active ON course_access(course_id, user_id) WHERE revoked = FALSE;
CREATE INDEX IF NOT EXISTS idx_course_access_expires ON course_access(expires_at) WHERE revoked = FALSE AND expires_at IS NOT NULL;

COMMENT ON TABLE course_access IS 'Course access control and user enrollments';

-- ============================================================================
-- TABLE: course_reviews
-- Description: Course reviews and ratings
-- ============================================================================
CREATE TABLE IF NOT EXISTS course_reviews (
    review_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID REFERENCES courses(course_id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    rating INTEGER NOT NULL,
    title VARCHAR(255),
    review_text TEXT,
    helpful_count INTEGER DEFAULT 0,
    verified_purchase BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'published',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_review_rating CHECK (rating >= 1 AND rating <= 5),
    CONSTRAINT chk_review_status CHECK (status IN ('pending', 'published', 'hidden', 'flagged')),
    UNIQUE (course_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_course_reviews_course ON course_reviews(course_id, status);
CREATE INDEX IF NOT EXISTS idx_course_reviews_user ON course_reviews(user_id);
CREATE INDEX IF NOT EXISTS idx_course_reviews_rating ON course_reviews(rating);
CREATE INDEX IF NOT EXISTS idx_course_reviews_status ON course_reviews(status);

COMMENT ON TABLE course_reviews IS 'Course reviews and ratings from students';

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- ============================================================================
CREATE TRIGGER update_course_categories_updated_at BEFORE UPDATE ON course_categories
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_courses_updated_at BEFORE UPDATE ON courses
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_course_reviews_updated_at BEFORE UPDATE ON course_reviews
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- End of Migration: 008_courses.sql
-- ============================================================================
