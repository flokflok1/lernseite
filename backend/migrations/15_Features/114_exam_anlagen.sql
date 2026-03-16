-- Migration: Separate exam anlagen (appendices) table
-- Anlagen are extracted by Vision AI and stored as HTML for direct rendering.
-- Replaces the old raw_text-based parsing approach.

CREATE TABLE IF NOT EXISTS assessments.exam_anlagen (
    anlage_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exam_id UUID NOT NULL REFERENCES assessments.exams(exam_id) ON DELETE CASCADE,
    number INTEGER NOT NULL,
    title VARCHAR(500) NOT NULL DEFAULT '',
    content_html TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(exam_id, number)
);

CREATE INDEX IF NOT EXISTS idx_exam_anlagen_exam ON assessments.exam_anlagen(exam_id);

COMMENT ON TABLE assessments.exam_anlagen IS 'Exam appendices (Anlagen) extracted by Vision AI, stored as HTML';
