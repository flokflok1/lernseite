-- ============================================================================
-- Migration: 013_exams.sql
-- Version: 1.0.0
-- Description: Database migration
-- Author: LernsystemX Migration System
-- Date: 2026-01-02
-- ============================================================================

CREATE TABLE IF NOT EXISTS assessments.exams (
    exam_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID REFERENCES courses.courses(course_id) ON DELETE CASCADE,
    chapter_id UUID REFERENCES courses.chapters(chapter_id) ON DELETE SET NULL,
    created_by UUID REFERENCES core.users(user_id) ON DELETE SET NULL,
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

CREATE INDEX IF NOT EXISTS idx_exams_course ON assessments.exams(course_id);
CREATE INDEX IF NOT EXISTS idx_exams_chapter ON assessments.exams(chapter_id);
CREATE INDEX IF NOT EXISTS idx_exams_type ON assessments.exams(exam_type);
CREATE INDEX IF NOT EXISTS idx_exams_creator ON assessments.exams(created_by);
CREATE INDEX IF NOT EXISTS idx_exams_published ON assessments.exams(published) WHERE published = TRUE;

COMMENT ON TABLE assessments.exams IS 'Exam definitions: simulations, practice tests, real exams';
COMMENT ON COLUMN assessments.exams.settings IS 'JSONB: proctoring, calculator, notes, break times, etc.';

-- ============================================================================
-- TABLE: exam_questions
-- Description: Questions within exams
-- ============================================================================
CREATE TABLE IF NOT EXISTS assessments.exam_questions (
    question_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    exam_id UUID REFERENCES assessments.exams(exam_id) ON DELETE CASCADE,
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

CREATE INDEX IF NOT EXISTS idx_exam_questions_exam ON assessments.exam_questions(exam_id);
CREATE INDEX IF NOT EXISTS idx_exam_questions_type ON assessments.exam_questions(question_type);
CREATE INDEX IF NOT EXISTS idx_exam_questions_order ON assessments.exam_questions(exam_id, order_index);
CREATE INDEX IF NOT EXISTS idx_exam_questions_difficulty ON assessments.exam_questions(difficulty);

COMMENT ON TABLE assessments.exam_questions IS 'Exam questions with various types (MCQ, essay, code, etc.)';
COMMENT ON COLUMN assessments.exam_questions.data IS 'JSONB: question-specific data (options, code template, etc.)';

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- ============================================================================
DROP TRIGGER IF EXISTS update_exams_updated_at ON assessments.exams;
CREATE TRIGGER update_exams_updated_at BEFORE UPDATE ON assessments.exams
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- ExamArchive Extension: Additional columns for real exam archive
-- ============================================================================

ALTER TABLE assessments.exams
ADD COLUMN IF NOT EXISTS semester VARCHAR(50),
ADD COLUMN IF NOT EXISTS year INTEGER,
ADD COLUMN IF NOT EXISTS season VARCHAR(10),
ADD COLUMN IF NOT EXISTS part VARCHAR(10),
ADD COLUMN IF NOT EXISTS region VARCHAR(50),
ADD COLUMN IF NOT EXISTS profession VARCHAR(50),
ADD COLUMN IF NOT EXISTS pdf_path TEXT,
ADD COLUMN IF NOT EXISTS solution_pdf_path TEXT,
ADD COLUMN IF NOT EXISTS analysis_status VARCHAR(20) DEFAULT 'pending',
ADD COLUMN IF NOT EXISTS raw_text TEXT;

CREATE INDEX IF NOT EXISTS idx_exams_exam_type_real ON assessments.exams(exam_type) WHERE exam_type = 'real';
CREATE INDEX IF NOT EXISTS idx_exams_semester ON assessments.exams(semester);
CREATE INDEX IF NOT EXISTS idx_exams_profession ON assessments.exams(profession);
CREATE INDEX IF NOT EXISTS idx_exams_analysis_status ON assessments.exams(analysis_status);

-- ============================================================================
-- ExamArchive Extension: Additional columns for exam_questions
-- ============================================================================

ALTER TABLE assessments.exam_questions
ADD COLUMN IF NOT EXISTS scenario_title VARCHAR(255),
ADD COLUMN IF NOT EXISTS scenario_text TEXT,
ADD COLUMN IF NOT EXISTS question_number VARCHAR(20),
ADD COLUMN IF NOT EXISTS topics TEXT[],
ADD COLUMN IF NOT EXISTS solution_text TEXT;

CREATE INDEX IF NOT EXISTS idx_eq_topics ON assessments.exam_questions USING GIN (topics);

-- ============================================================================
-- TABLE: exam_topic_stats
-- Description: Aggregated topic statistics for exam trainer heatmap
-- ============================================================================

CREATE TABLE IF NOT EXISTS assessments.exam_topic_stats (
    stat_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,
    topic VARCHAR(100) NOT NULL,
    topic_category VARCHAR(100),
    attempts INTEGER DEFAULT 0,
    correct_count INTEGER DEFAULT 0,
    total_points DECIMAL(10,2) DEFAULT 0,
    earned_points DECIMAL(10,2) DEFAULT 0,
    last_attempt_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, topic)
);

CREATE INDEX IF NOT EXISTS idx_ets_user ON assessments.exam_topic_stats(user_id);
CREATE INDEX IF NOT EXISTS idx_ets_topic ON assessments.exam_topic_stats(topic);

COMMENT ON TABLE assessments.exam_topic_stats IS 'Aggregierte Themen-Statistik für Prüfungstrainer-Heatmap';

-- ============================================================================
-- End of Migration: 013_exams.sql
-- ============================================================================
