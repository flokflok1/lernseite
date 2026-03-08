-- ============================================================================
-- Migration: 104_exam_mode_on_courses.sql
-- Description: Adds exam_mode flag and exam_config JSONB to courses for
--              marking auto-generated exam simulation courses.
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-03-08
-- ============================================================================

-- Exam Mode: Pruefungsmodus fuer generierte Pruefungskurse
-- Adds exam_mode flag and exam_config JSONB to courses

ALTER TABLE courses.courses
    ADD COLUMN IF NOT EXISTS exam_mode BOOLEAN DEFAULT FALSE;

ALTER TABLE courses.courses
    ADD COLUMN IF NOT EXISTS exam_config JSONB DEFAULT NULL;

-- Index for quick filtering of exam-mode courses
CREATE INDEX IF NOT EXISTS idx_courses_exam_mode
    ON courses.courses (exam_mode) WHERE exam_mode = TRUE;

COMMENT ON COLUMN courses.courses.exam_mode
    IS 'Whether this course is an exam simulation course';

COMMENT ON COLUMN courses.courses.exam_config
    IS 'Exam configuration: time_limit_minutes, total_points, passing_percentage, source_exam_type, source_region';
