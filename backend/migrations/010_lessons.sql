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
CREATE TABLE IF NOT EXISTS lessons (
    lesson_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chapter_id UUID REFERENCES chapters(chapter_id) ON DELETE CASCADE,
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

CREATE INDEX IF NOT EXISTS idx_lessons_chapter ON lessons(chapter_id);
CREATE INDEX IF NOT EXISTS idx_lessons_order ON lessons(chapter_id, order_index);
CREATE INDEX IF NOT EXISTS idx_lessons_type ON lessons(lesson_type);
CREATE INDEX IF NOT EXISTS idx_lessons_published ON lessons(published) WHERE published = TRUE;
CREATE INDEX IF NOT EXISTS idx_lessons_preview ON lessons(free_preview) WHERE free_preview = TRUE;

COMMENT ON TABLE lessons IS 'Individual lessons within course chapters';
COMMENT ON COLUMN lessons.content IS 'JSONB structure varies by lesson_type';

-- ============================================================================
-- TABLE: lesson_completions
-- Description: Track user completion of lessons
-- ============================================================================
CREATE TABLE IF NOT EXISTS lesson_completions (
    completion_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lesson_id UUID REFERENCES lessons(lesson_id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    completed_at TIMESTAMPTZ DEFAULT NOW(),
    time_spent_seconds INTEGER,
    score DECIMAL(5,2),
    UNIQUE (lesson_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_lesson_completions_lesson ON lesson_completions(lesson_id);
CREATE INDEX IF NOT EXISTS idx_lesson_completions_user ON lesson_completions(user_id, completed_at DESC);
CREATE INDEX IF NOT EXISTS idx_lesson_completions_score ON lesson_completions(score);

COMMENT ON TABLE lesson_completions IS 'User completion tracking for lessons';

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- ============================================================================
CREATE TRIGGER update_lessons_updated_at BEFORE UPDATE ON lessons
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- End of Migration: 010_lessons.sql
-- ============================================================================
