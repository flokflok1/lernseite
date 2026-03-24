-- Migration: Add archive_folder_id to exam_type_registry
-- Links exam types to their default archive folder for automatic file organization

ALTER TABLE assessments.exam_type_registry
ADD COLUMN IF NOT EXISTS archive_folder_id UUID
REFERENCES assessments.archive_folders(folder_id)
ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_exam_type_registry_archive_folder
ON assessments.exam_type_registry(archive_folder_id)
WHERE archive_folder_id IS NOT NULL;
