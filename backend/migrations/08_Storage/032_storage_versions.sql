-- ============================================================================
-- Migration: 032_storage_versions.sql
-- Version: 1.0.0
-- Description: Database migration
-- Author: LernsystemX Migration System
-- Date: 2026-01-02
-- ============================================================================

CREATE TABLE IF NOT EXISTS storage.file_versions (
    version_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_id UUID REFERENCES billing_storage.media_files(file_id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    checksum VARCHAR(64),
    uploaded_by UUID REFERENCES core.users(user_id) ON DELETE SET NULL,
    change_description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (file_id, version_number)
);

CREATE INDEX IF NOT EXISTS idx_file_versions_file ON storage.file_versions(file_id, version_number DESC);
CREATE INDEX IF NOT EXISTS idx_file_versions_uploader ON storage.file_versions(uploaded_by);
CREATE INDEX IF NOT EXISTS idx_file_versions_created ON storage.file_versions(created_at DESC);

COMMENT ON TABLE storage.file_versions IS 'Version history for uploaded files';

-- ============================================================================
-- TABLE: content_versions
-- Description: Version history for editable content
-- ============================================================================
CREATE TABLE IF NOT EXISTS courses.content_versions (
    version_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_type VARCHAR(50) NOT NULL,
    content_id UUID NOT NULL,
    version_number INTEGER NOT NULL,
    content_data JSONB NOT NULL,
    changed_by UUID REFERENCES core.users(user_id) ON DELETE SET NULL,
    change_summary TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_content_type CHECK (content_type IN ('course', 'module', 'lesson', 'theory', 'method', 'exam')),
    UNIQUE (content_type, content_id, version_number)
);

CREATE INDEX IF NOT EXISTS idx_content_versions_content ON courses.content_versions(content_type, content_id, version_number DESC);
CREATE INDEX IF NOT EXISTS idx_content_versions_user ON courses.content_versions(changed_by);
CREATE INDEX IF NOT EXISTS idx_content_versions_created ON courses.content_versions(created_at DESC);

COMMENT ON TABLE courses.content_versions IS 'Version control for course content and learning materials';

-- ============================================================================
-- End of Migration: 032_storage_versions.sql
-- ============================================================================
