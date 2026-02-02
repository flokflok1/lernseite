-- ============================================================================
-- Migration: 012_learning_progress.sql
-- Version: 1.0.0
-- Description: Learning progress and achievement tracking
-- Author: LernsystemX Migration System
-- Date: 2026-01-02
-- ============================================================================

BEGIN;

-- NOTE: gamification schema is created in 01_Core/000_schemas.sql
-- No schema creation needed here

-- ============================================================================
-- TABLE: course_enrollments
-- Description: User enrollment and progress in courses
-- ============================================================================
CREATE TABLE IF NOT EXISTS courses.course_enrollments (
    enrollment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID REFERENCES courses.courses(course_id) ON DELETE CASCADE,
    user_id UUID REFERENCES core.users(user_id) ON DELETE CASCADE,
    enrolled_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    completion_percentage DECIMAL(5,2) DEFAULT 0,
    last_accessed_at TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'active',
    CONSTRAINT chk_enrollment_status CHECK (status IN ('active', 'completed', 'paused', 'dropped')),
    UNIQUE (course_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_course_enrollments_course ON courses.course_enrollments(course_id, status);
CREATE INDEX IF NOT EXISTS idx_course_enrollments_user ON courses.course_enrollments(user_id, status);
CREATE INDEX IF NOT EXISTS idx_course_enrollments_status ON courses.course_enrollments(status);
CREATE INDEX IF NOT EXISTS idx_course_enrollments_accessed ON courses.course_enrollments(last_accessed_at DESC);

COMMENT ON TABLE courses.course_enrollments IS 'User enrollment and progress in courses';

-- ============================================================================
-- TABLE: chapter_progress
-- Description: User progress through chapters
-- ============================================================================
CREATE TABLE IF NOT EXISTS courses.chapter_progress (
    progress_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chapter_id UUID REFERENCES courses.chapters(chapter_id) ON DELETE CASCADE,
    user_id UUID REFERENCES core.users(user_id) ON DELETE CASCADE,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    completion_percentage DECIMAL(5,2) DEFAULT 0,
    time_spent_seconds INTEGER DEFAULT 0,
    last_position JSONB,
    UNIQUE (chapter_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_chapter_progress_chapter ON courses.chapter_progress(chapter_id);
CREATE INDEX IF NOT EXISTS idx_chapter_progress_user ON courses.chapter_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_chapter_progress_completion ON courses.chapter_progress(completion_percentage);

COMMENT ON TABLE courses.chapter_progress IS 'User progress tracking for individual chapters';

-- ============================================================================
-- TABLE: learning_streaks
-- Description: Daily learning streaks for gamification
-- ============================================================================
CREATE TABLE IF NOT EXISTS learning_methods.learning_streaks (
    streak_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES core.users(user_id) ON DELETE CASCADE UNIQUE,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_activity_date DATE,
    total_learning_days INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_learning_streaks_user ON learning_methods.learning_streaks(user_id);
CREATE INDEX IF NOT EXISTS idx_learning_streaks_current ON learning_methods.learning_streaks(current_streak DESC);
CREATE INDEX IF NOT EXISTS idx_learning_streaks_longest ON learning_methods.learning_streaks(longest_streak DESC);

COMMENT ON TABLE learning_methods.learning_streaks IS 'Daily learning streaks for motivation and gamification';

-- ============================================================================
-- TABLE: user_achievements
-- Description: Achievement tracking for users
-- ============================================================================
CREATE TABLE IF NOT EXISTS gamification.user_achievements (
    achievement_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES core.users(user_id) ON DELETE CASCADE,
    achievement_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    icon VARCHAR(100),
    points INTEGER DEFAULT 0,
    metadata JSONB,
    earned_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_achievements_user ON gamification.user_achievements(user_id, earned_at DESC);
CREATE INDEX IF NOT EXISTS idx_user_achievements_type ON gamification.user_achievements(achievement_type);
CREATE INDEX IF NOT EXISTS idx_user_achievements_points ON gamification.user_achievements(points DESC);

COMMENT ON TABLE gamification.user_achievements IS 'User achievements and milestones';

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- ============================================================================
DROP TRIGGER IF EXISTS update_learning_streaks_updated_at ON learning_methods.learning_streaks;
CREATE TRIGGER update_learning_streaks_updated_at BEFORE UPDATE ON learning_methods.learning_streaks
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMIT;
