-- ============================================================================
-- Migration: 032_storage_versions.sql
-- Description: File and content versioning
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-01-17
-- ============================================================================

-- ============================================================================
-- TABLE: file_versions
-- Description: Version history for files
-- ============================================================================
CREATE TABLE IF NOT EXISTS file_versions (
    version_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_id UUID REFERENCES media_files(file_id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    checksum VARCHAR(64),
    uploaded_by UUID REFERENCES users(user_id) ON DELETE SET NULL,
    change_description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (file_id, version_number)
);

CREATE INDEX IF NOT EXISTS idx_file_versions_file ON file_versions(file_id, version_number DESC);
CREATE INDEX IF NOT EXISTS idx_file_versions_uploader ON file_versions(uploaded_by);
CREATE INDEX IF NOT EXISTS idx_file_versions_created ON file_versions(created_at DESC);

COMMENT ON TABLE file_versions IS 'Version history for uploaded files';

-- ============================================================================
-- TABLE: content_versions
-- Description: Version history for editable content
-- ============================================================================
CREATE TABLE IF NOT EXISTS content_versions (
    version_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_type VARCHAR(50) NOT NULL,
    content_id UUID NOT NULL,
    version_number INTEGER NOT NULL,
    content_data JSONB NOT NULL,
    changed_by UUID REFERENCES users(user_id) ON DELETE SET NULL,
    change_summary TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_content_type CHECK (content_type IN ('course', 'module', 'lesson', 'theory', 'method', 'exam')),
    UNIQUE (content_type, content_id, version_number)
);

CREATE INDEX IF NOT EXISTS idx_content_versions_content ON content_versions(content_type, content_id, version_number DESC);
CREATE INDEX IF NOT EXISTS idx_content_versions_user ON content_versions(changed_by);
CREATE INDEX IF NOT EXISTS idx_content_versions_created ON content_versions(created_at DESC);

COMMENT ON TABLE content_versions IS 'Version control for course content and learning materials';

-- ============================================================================
-- End of Migration: 032_storage_versions.sql
-- ============================================================================
