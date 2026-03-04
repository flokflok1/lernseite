-- ============================================================================
-- Migration: 013_exams_archive_extension.sql
-- Description: Standalone extension for exam archive columns (can run on existing DB)
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-03-02
-- ============================================================================

-- ExamArchive: Additional columns for assessments.exams
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

-- ExamArchive: Additional columns for assessments.exam_questions
ALTER TABLE assessments.exam_questions
ADD COLUMN IF NOT EXISTS scenario_title VARCHAR(255),
ADD COLUMN IF NOT EXISTS scenario_text TEXT,
ADD COLUMN IF NOT EXISTS question_number VARCHAR(20),
ADD COLUMN IF NOT EXISTS topics TEXT[],
ADD COLUMN IF NOT EXISTS solution_text TEXT;

CREATE INDEX IF NOT EXISTS idx_eq_topics ON assessments.exam_questions USING GIN (topics);

-- ExamArchive: New table for topic statistics
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
-- End of Migration: 013_exams_archive_extension.sql
-- ============================================================================
