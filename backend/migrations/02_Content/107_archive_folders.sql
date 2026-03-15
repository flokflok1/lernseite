-- ============================================================================
-- Migration: 107_archive_folders.sql
-- Description: Archive folder hierarchy for exam file explorer
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-03-15
-- ============================================================================

-- ============================================================
-- 1. Folder hierarchy table
-- ============================================================
CREATE TABLE IF NOT EXISTS assessments.archive_folders (
    folder_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_folder_id UUID REFERENCES assessments.archive_folders(folder_id) ON DELETE CASCADE,
    program_id       INTEGER REFERENCES assessments.exam_programs(program_id) ON DELETE CASCADE,
    name             VARCHAR(255) NOT NULL,
    icon             VARCHAR(10),
    position         INTEGER DEFAULT 0,
    metadata         JSONB DEFAULT '{}',
    created_by       UUID REFERENCES core.users(user_id) ON DELETE SET NULL,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    updated_at       TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_archive_folders_parent
    ON assessments.archive_folders(parent_folder_id);
CREATE INDEX IF NOT EXISTS idx_archive_folders_program
    ON assessments.archive_folders(program_id);

-- ============================================================
-- 2. Add folder_id FK to exams
-- ============================================================
ALTER TABLE assessments.exams
    ADD COLUMN IF NOT EXISTS folder_id UUID
    REFERENCES assessments.archive_folders(folder_id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_exams_folder
    ON assessments.exams(folder_id) WHERE folder_id IS NOT NULL;
