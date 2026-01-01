-- ============================================================================
-- Migration: 013_exams.sql
-- Description: Examination system tables
-- Version: 2.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-01-17
-- Updated: 2025-11-27 (Refactoring: modules → chapters)
-- ============================================================================

-- ============================================================================
-- TABLE: exams
-- Description: Exam definitions (IHK, CompTIA, custom)
-- ============================================================================
CREATE TABLE IF NOT EXISTS exams (
    exam_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID REFERENCES courses(course_id) ON DELETE CASCADE,
    chapter_id UUID REFERENCES chapters(chapter_id) ON DELETE SET NULL,
    created_by UUID REFERENCES users(user_id) ON DELETE SET NULL,
    exam_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    instructions TEXT,
    duration_minutes INTEGER NOT NULL,
    passing_score DECIMAL(5,2) NOT NULL,
    total_points DECIMAL(10,2),
    randomize_questions BOOLEAN DEFAULT FALSE,
    show_results_immediately BOOLEAN DEFAULT TRUE,
    allow_review BOOLEAN DEFAULT TRUE,
    max_attempts INTEGER,
    settings JSONB,
    published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_exam_type CHECK (exam_type IN ('simulation', 'real', 'custom', 'practice', 'quiz'))
);

CREATE INDEX IF NOT EXISTS idx_exams_course ON exams(course_id);
CREATE INDEX IF NOT EXISTS idx_exams_chapter ON exams(chapter_id);
CREATE INDEX IF NOT EXISTS idx_exams_type ON exams(exam_type);
CREATE INDEX IF NOT EXISTS idx_exams_creator ON exams(created_by);
CREATE INDEX IF NOT EXISTS idx_exams_published ON exams(published) WHERE published = TRUE;

COMMENT ON TABLE exams IS 'Exam definitions: simulations, practice tests, real exams';
COMMENT ON COLUMN exams.settings IS 'JSONB: proctoring, calculator, notes, break times, etc.';

-- ============================================================================
-- TABLE: exam_questions
-- Description: Questions within exams
-- ============================================================================
CREATE TABLE IF NOT EXISTS exam_questions (
    question_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    exam_id UUID REFERENCES exams(exam_id) ON DELETE CASCADE,
    question_type VARCHAR(50) NOT NULL,
    question_text TEXT NOT NULL,
    data JSONB NOT NULL,
    solution JSONB,
    points DECIMAL(5,2) DEFAULT 1.0,
    order_index INTEGER,
    difficulty VARCHAR(20),
    time_limit_seconds INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_question_type CHECK (question_type IN ('mcq', 'multiple_choice', 'true_false', 'fill_blank', 'essay', 'code', 'case_study', 'calculation')),
    CONSTRAINT chk_question_difficulty CHECK (difficulty IN ('easy', 'medium', 'hard'))
);

CREATE INDEX IF NOT EXISTS idx_exam_questions_exam ON exam_questions(exam_id);
CREATE INDEX IF NOT EXISTS idx_exam_questions_type ON exam_questions(question_type);
CREATE INDEX IF NOT EXISTS idx_exam_questions_order ON exam_questions(exam_id, order_index);
CREATE INDEX IF NOT EXISTS idx_exam_questions_difficulty ON exam_questions(difficulty);

COMMENT ON TABLE exam_questions IS 'Exam questions with various types (MCQ, essay, code, etc.)';
COMMENT ON COLUMN exam_questions.data IS 'JSONB: question-specific data (options, code template, etc.)';

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- ============================================================================
CREATE TRIGGER update_exams_updated_at BEFORE UPDATE ON exams
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- End of Migration: 013_exams.sql
-- ============================================================================
