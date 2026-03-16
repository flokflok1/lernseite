-- Migration: Add chapter_type to distinguish learning chapters from simulation chapters
ALTER TABLE courses.chapters
ADD COLUMN IF NOT EXISTS chapter_type VARCHAR(20) NOT NULL DEFAULT 'learning';

UPDATE courses.chapters
SET chapter_type = 'simulation'
WHERE title LIKE 'Simulation:%';

ALTER TABLE courses.chapters
ADD CONSTRAINT chk_chapter_type
CHECK (chapter_type IN ('learning', 'simulation', 'assessment'));

COMMENT ON COLUMN courses.chapters.chapter_type IS 'Type: learning (default), simulation (exam simulation), assessment (end-of-chapter test)';
