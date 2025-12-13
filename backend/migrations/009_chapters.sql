-- ============================================================================
-- Migration: 009_chapters.sql
-- Description: Course chapters and chapter theory
-- Version: 2.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-01-17
-- Updated: 2025-11-27 (Refactoring: modules → chapters)
-- ============================================================================

-- ============================================================================
-- TABLE: chapters
-- Description: Course chapters (structured learning units)
-- ============================================================================
CREATE TABLE IF NOT EXISTS chapters (
    chapter_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID REFERENCES courses(course_id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255),
    description TEXT,
    order_index INTEGER NOT NULL,
    duration_minutes INTEGER,
    estimated_duration INTEGER,
    prerequisite_chapter_id UUID REFERENCES chapters(chapter_id) ON DELETE SET NULL,
    published BOOLEAN DEFAULT FALSE,
    has_video BOOLEAN DEFAULT FALSE,
    has_quiz BOOLEAN DEFAULT FALSE,
    has_exam BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (course_id, order_index)
);

CREATE INDEX IF NOT EXISTS idx_chapters_course ON chapters(course_id);
CREATE INDEX IF NOT EXISTS idx_chapters_order ON chapters(course_id, order_index);
CREATE INDEX IF NOT EXISTS idx_chapters_published ON chapters(published) WHERE published = TRUE;
CREATE INDEX IF NOT EXISTS idx_chapters_prerequisite ON chapters(prerequisite_chapter_id);
CREATE INDEX IF NOT EXISTS idx_chapters_has_video ON chapters(has_video) WHERE has_video = TRUE;
CREATE INDEX IF NOT EXISTS idx_chapters_has_quiz ON chapters(has_quiz) WHERE has_quiz = TRUE;
CREATE INDEX IF NOT EXISTS idx_chapters_has_exam ON chapters(has_exam) WHERE has_exam = TRUE;

COMMENT ON TABLE chapters IS 'Course chapters containing lessons and learning methods';
COMMENT ON COLUMN chapters.has_video IS 'Indicates if chapter contains video content';
COMMENT ON COLUMN chapters.has_quiz IS 'Indicates if chapter contains quiz/assessment';
COMMENT ON COLUMN chapters.has_exam IS 'Indicates if chapter contains exam/final test';

-- ============================================================================
-- TABLE: chapter_theory
-- Description: Theory content for chapters (JSONB structure)
-- ============================================================================
CREATE TABLE IF NOT EXISTS chapter_theory (
    theory_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chapter_id UUID REFERENCES chapters(chapter_id) ON DELETE CASCADE UNIQUE,
    content JSONB NOT NULL,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chapter_theory_chapter ON chapter_theory(chapter_id);
CREATE INDEX IF NOT EXISTS idx_chapter_theory_content ON chapter_theory USING GIN(content);

COMMENT ON TABLE chapter_theory IS 'Structured theory content for chapters (title, sections, examples, glossary)';
COMMENT ON COLUMN chapter_theory.content IS 'JSONB structure: {title, sections[], examples[], glossary[]}';

-- ============================================================================
-- TABLE: chapter_resources
-- Description: Additional resources attached to chapters
-- ============================================================================
CREATE TABLE IF NOT EXISTS chapter_resources (
    resource_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chapter_id UUID REFERENCES chapters(chapter_id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    url VARCHAR(500),
    file_path VARCHAR(500),
    description TEXT,
    size_bytes BIGINT,
    mime_type VARCHAR(100),
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_chapter_resource_type CHECK (resource_type IN ('pdf', 'video', 'audio', 'document', 'link', 'image', 'code'))
);

CREATE INDEX IF NOT EXISTS idx_chapter_resources_chapter ON chapter_resources(chapter_id);
CREATE INDEX IF NOT EXISTS idx_chapter_resources_type ON chapter_resources(resource_type);
CREATE INDEX IF NOT EXISTS idx_chapter_resources_order ON chapter_resources(chapter_id, order_index);

COMMENT ON TABLE chapter_resources IS 'Additional learning resources for chapters (PDFs, videos, links, etc.)';

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- ============================================================================
CREATE TRIGGER update_chapters_updated_at BEFORE UPDATE ON chapters
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_chapter_theory_updated_at BEFORE UPDATE ON chapter_theory
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- End of Migration: 009_chapters.sql
-- ============================================================================
