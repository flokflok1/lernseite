-- ============================================================================
-- Migration: 031_media_files.sql
-- Description: Media file storage and management
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-01-17
-- ============================================================================

-- ============================================================================
-- TABLE: media_files
-- Description: Uploaded media files (images, videos, documents)
-- ============================================================================
CREATE TABLE IF NOT EXISTS media_files (
    file_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    uploaded_by UUID REFERENCES users(user_id) ON DELETE SET NULL,
    organization_id UUID REFERENCES organizations(organization_id) ON DELETE SET NULL,
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    storage_provider VARCHAR(50) DEFAULT 'local',
    mime_type VARCHAR(100) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    width INTEGER,
    height INTEGER,
    duration_seconds INTEGER,
    file_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'uploaded',
    virus_scanned BOOLEAN DEFAULT FALSE,
    virus_scan_result VARCHAR(20),
    public_url VARCHAR(500),
    cdn_url VARCHAR(500),
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_media_file_type CHECK (file_type IN ('image', 'video', 'audio', 'document', 'archive', 'other')),
    CONSTRAINT chk_media_status CHECK (status IN ('uploaded', 'processing', 'ready', 'failed', 'deleted')),
    CONSTRAINT chk_virus_scan CHECK (virus_scan_result IN ('clean', 'infected', 'suspicious', NULL))
);

CREATE INDEX IF NOT EXISTS idx_media_files_uploader ON media_files(uploaded_by, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_media_files_org ON media_files(organization_id);
CREATE INDEX IF NOT EXISTS idx_media_files_type ON media_files(file_type);
CREATE INDEX IF NOT EXISTS idx_media_files_mime ON media_files(mime_type);
CREATE INDEX IF NOT EXISTS idx_media_files_status ON media_files(status);
CREATE INDEX IF NOT EXISTS idx_media_files_created ON media_files(created_at DESC);

COMMENT ON TABLE media_files IS 'Uploaded media files with metadata and virus scanning';

-- ============================================================================
-- TABLE: media_thumbnails
-- Description: Generated thumbnails for images and videos
-- ============================================================================
CREATE TABLE IF NOT EXISTS media_thumbnails (
    thumbnail_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_id UUID REFERENCES media_files(file_id) ON DELETE CASCADE,
    size_name VARCHAR(50) NOT NULL,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size_bytes BIGINT,
    url VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_thumbnail_size CHECK (size_name IN ('small', 'medium', 'large', 'xlarge', 'custom')),
    UNIQUE (file_id, size_name)
);

CREATE INDEX IF NOT EXISTS idx_media_thumbnails_file ON media_thumbnails(file_id);
CREATE INDEX IF NOT EXISTS idx_media_thumbnails_size ON media_thumbnails(size_name);

COMMENT ON TABLE media_thumbnails IS 'Generated thumbnails for media files';

-- ============================================================================
-- End of Migration: 031_media_files.sql
-- ============================================================================
