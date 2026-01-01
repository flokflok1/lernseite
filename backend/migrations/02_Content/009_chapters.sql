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
-- Description: KI-generated theory content for chapters
-- Features: JSONB storage, TTS audio, style variants (adhs, detailed, etc.)
-- ============================================================================
CREATE TABLE IF NOT EXISTS chapter_theory (
    theory_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chapter_id UUID NOT NULL REFERENCES chapters(chapter_id) ON DELETE CASCADE,
    style VARCHAR(20) NOT NULL DEFAULT 'adhs',

    -- Theory content (JSONB for flexible structure)
    -- Structure: {overview, learningGoals[], concepts[], terms[], examTips[], summary, whiteboardActions[]}
    theory_data JSONB NOT NULL,

    -- TTS Audio
    audio_url VARCHAR(500),
    audio_duration_seconds INTEGER,

    -- Generation metadata
    tokens_used INTEGER DEFAULT 0,
    model_used VARCHAR(50),
    generated_by UUID REFERENCES users(user_id),

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Unique constraint: one theory per chapter per style
    CONSTRAINT uq_chapter_theory_style UNIQUE (chapter_id, style)
);

CREATE INDEX IF NOT EXISTS idx_chapter_theory_chapter_id ON chapter_theory(chapter_id);
CREATE INDEX IF NOT EXISTS idx_chapter_theory_style ON chapter_theory(style);
CREATE INDEX IF NOT EXISTS idx_chapter_theory_data ON chapter_theory USING GIN (theory_data);

COMMENT ON TABLE chapter_theory IS 'KI-generated chapter theory content. One per chapter/style combination.';
COMMENT ON COLUMN chapter_theory.theory_data IS 'JSONB: overview, learningGoals, concepts, terms, examTips, summary, whiteboardActions';
COMMENT ON COLUMN chapter_theory.style IS 'Theory style: adhs (visual), detailed, short, exam_focus, standard';

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
-- Triggers: Update updated_at timestamps
-- ============================================================================
CREATE TRIGGER update_chapters_updated_at BEFORE UPDATE ON chapters
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE OR REPLACE FUNCTION update_chapter_theory_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS chapter_theory_updated ON chapter_theory;
CREATE TRIGGER chapter_theory_updated
    BEFORE UPDATE ON chapter_theory
    FOR EACH ROW
    EXECUTE FUNCTION update_chapter_theory_timestamp();

-- ============================================================================
-- End of Migration: 009_chapters.sql
-- ============================================================================
