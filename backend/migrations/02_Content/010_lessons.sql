-- ============================================================================
-- Migration: 010_lessons.sql
-- Description: Lessons within chapters
-- Version: 2.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-01-17
-- Updated: 2025-11-27 (Refactoring: modules → chapters)
-- ============================================================================

-- ============================================================================
-- TABLE: lessons
-- Description: Individual lessons within chapters
-- ============================================================================
CREATE TABLE IF NOT EXISTS courses.lessons (
    lesson_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chapter_id UUID REFERENCES courses.chapters(chapter_id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255),
    lesson_type VARCHAR(50) NOT NULL,
    content JSONB,
    duration_minutes INTEGER,
    order_index INTEGER NOT NULL,
    published BOOLEAN DEFAULT FALSE,
    free_preview BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_lesson_type CHECK (lesson_type IN ('text', 'video', 'quiz', 'interactive', 'assignment', 'discussion')),
    UNIQUE (chapter_id, order_index)
);

CREATE INDEX IF NOT EXISTS idx_lessons_chapter ON courses.lessons (chapter_id);
CREATE INDEX IF NOT EXISTS idx_lessons_order ON courses.lessons (chapter_id, order_index);
CREATE INDEX IF NOT EXISTS idx_lessons_type ON courses.lessons (lesson_type);
CREATE INDEX IF NOT EXISTS idx_lessons_published ON courses.lessons (published) WHERE published = TRUE;
CREATE INDEX IF NOT EXISTS idx_lessons_preview ON courses.lessons (free_preview) WHERE free_preview = TRUE;

COMMENT ON TABLE courses.lessons IS 'Individual lessons within course chapters';
COMMENT ON COLUMN courses.lessons.content IS 'JSONB structure varies by lesson_type';

-- ============================================================================
-- TABLE: lesson_completions
-- Description: Track user completion of lessons
-- ============================================================================
CREATE TABLE IF NOT EXISTS courses.lesson_completions (
    completion_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lesson_id UUID REFERENCES courses.lessons(lesson_id) ON DELETE CASCADE,
    user_id UUID REFERENCES core.users(user_id) ON DELETE CASCADE,
    completed_at TIMESTAMPTZ DEFAULT NOW(),
    time_spent_seconds INTEGER,
    score DECIMAL(5,2),
    UNIQUE (lesson_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_lesson_completions_lesson ON courses.lesson_completions (lesson_id);
CREATE INDEX IF NOT EXISTS idx_lesson_completions_user ON courses.lesson_completions (user_id, completed_at DESC);
CREATE INDEX IF NOT EXISTS idx_lesson_completions_score ON courses.lesson_completions (score);

COMMENT ON TABLE courses.lesson_completions IS 'User completion tracking for lessons';

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- ============================================================================
CREATE TRIGGER update_lessons_updated_at BEFORE UPDATE ON courses.lessons
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- TABLE: lesson_theory
-- Description: Theory sheets for lessons
-- ============================================================================
CREATE TABLE IF NOT EXISTS courses.lesson_theory (
    theory_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lesson_id UUID NOT NULL REFERENCES courses.lessons(lesson_id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (lesson_id, order_index)
);

CREATE INDEX IF NOT EXISTS idx_lesson_theory_lesson ON courses.lesson_theory (lesson_id);
CREATE INDEX IF NOT EXISTS idx_lesson_theory_order ON courses.lesson_theory (lesson_id, order_index);

COMMENT ON TABLE courses.lesson_theory IS 'Theory sheets for individual lessons';

-- ============================================================================
-- TABLE: course_publishing
-- Description: Publishing and community submission workflow
-- ============================================================================
CREATE TABLE IF NOT EXISTS courses.course_publishing (
    publish_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID NOT NULL REFERENCES courses.courses(course_id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    submission_date TIMESTAMPTZ,
    moderator_id UUID REFERENCES core.users(user_id) ON DELETE SET NULL,
    moderation_notes TEXT,
    moderation_ai_score NUMERIC(3,2),
    published_date TIMESTAMPTZ,
    visibility VARCHAR(20) DEFAULT 'private',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_publishing_status CHECK (status IN ('draft', 'submitted', 'approved', 'published', 'rejected')),
    CONSTRAINT chk_publishing_visibility CHECK (visibility IN ('private', 'community', 'public')),
    CONSTRAINT chk_ai_score CHECK (moderation_ai_score IS NULL OR (moderation_ai_score >= 0 AND moderation_ai_score <= 1)),
    UNIQUE (course_id)
);

CREATE INDEX IF NOT EXISTS idx_course_publishing_course ON courses.course_publishing (course_id);
CREATE INDEX IF NOT EXISTS idx_course_publishing_status ON courses.course_publishing (status);
CREATE INDEX IF NOT EXISTS idx_course_publishing_moderator ON courses.course_publishing (moderator_id);
CREATE INDEX IF NOT EXISTS idx_course_publishing_date ON courses.course_publishing (submission_date DESC);
CREATE INDEX IF NOT EXISTS idx_course_publishing_visibility ON courses.course_publishing (visibility) WHERE visibility = 'community';

COMMENT ON TABLE courses.course_publishing IS 'Publishing workflow: draft → submitted → approved/rejected → published';
COMMENT ON COLUMN courses.course_publishing.moderation_ai_score IS 'KI-Moderation score: 0.00-1.00 (higher = better)';

-- ============================================================================
-- TABLE: moderation_audit
-- Description: Audit trail for course moderation actions
-- ============================================================================
CREATE TABLE IF NOT EXISTS courses.moderation_audit (
    audit_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID NOT NULL REFERENCES courses.courses(course_id) ON DELETE CASCADE,
    moderator_id UUID REFERENCES core.users(user_id) ON DELETE SET NULL,
    action VARCHAR(50) NOT NULL,
    notes TEXT,
    ai_analysis JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_audit_action CHECK (action IN ('submitted', 'reviewed', 'approved', 'rejected', 'revision_requested', 'ai_analyzed'))
);

CREATE INDEX IF NOT EXISTS idx_moderation_audit_course ON courses.moderation_audit (course_id);
CREATE INDEX IF NOT EXISTS idx_moderation_audit_moderator ON courses.moderation_audit (moderator_id);
CREATE INDEX IF NOT EXISTS idx_moderation_audit_action ON courses.moderation_audit (action);
CREATE INDEX IF NOT EXISTS idx_moderation_audit_date ON courses.moderation_audit (created_at DESC);

COMMENT ON TABLE courses.moderation_audit IS 'Audit trail for all moderation actions and AI analyses';
COMMENT ON COLUMN courses.moderation_audit.ai_analysis IS 'JSONB structure with KI analysis results: {quality, appropriateness, originality, learning_methods, overall_score, issues, recommendations}';

-- ============================================================================
-- Trigger: Update updated_at for chapter_theory
-- ============================================================================
CREATE TRIGGER update_chapter_theory_updated_at BEFORE UPDATE ON courses.chapter_theory
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Trigger: Update updated_at for lesson_theory
-- ============================================================================
CREATE TRIGGER update_lesson_theory_updated_at BEFORE UPDATE ON courses.lesson_theory
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Trigger: Update updated_at for course_publishing
-- ============================================================================
CREATE TRIGGER update_course_publishing_updated_at BEFORE UPDATE ON courses.course_publishing
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- End of Migration: 010_lessons.sql
-- ============================================================================
