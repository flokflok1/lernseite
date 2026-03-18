ALTER TABLE assessments.exam_anlagen
ADD COLUMN IF NOT EXISTS is_generated BOOLEAN NOT NULL DEFAULT false;
COMMENT ON COLUMN assessments.exam_anlagen.is_generated IS 'true = KI-generiert, false = aus PDF';
