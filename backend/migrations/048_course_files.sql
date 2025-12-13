-- ============================================================================
-- Migration: 048_course_files.sql
-- Description: Course files management - link media files to courses
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-01-24
-- ============================================================================

-- ============================================================================
-- TABLE: course_files
-- Description: Links uploaded files to specific courses for management
-- Supports PDF scripts, reference materials, supplementary documents
-- ============================================================================
CREATE TABLE IF NOT EXISTS course_files (
    course_file_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,
    file_id UUID REFERENCES media_files(file_id) ON DELETE SET NULL,

    -- File metadata (stored separately if file_id is null for external files)
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size_bytes BIGINT,
    mime_type VARCHAR(100),

    -- Course file specific fields
    display_name VARCHAR(255),
    description TEXT,
    file_category VARCHAR(50) DEFAULT 'material',
    order_index INTEGER DEFAULT 0,

    -- Access control
    is_public BOOLEAN DEFAULT FALSE,
    requires_enrollment BOOLEAN DEFAULT TRUE,
    download_count INTEGER DEFAULT 0,

    -- AI processing flags
    processed_for_ai BOOLEAN DEFAULT FALSE,
    ai_extracted_text TEXT,
    ai_summary TEXT,

    -- External file support (S3, CDN, etc.)
    storage_path VARCHAR(500),
    external_url VARCHAR(500),

    -- Audit
    uploaded_by UUID REFERENCES users(user_id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT chk_course_file_type CHECK (file_type IN ('pdf', 'docx', 'pptx', 'xlsx', 'txt', 'image', 'video', 'audio', 'archive', 'other')),
    CONSTRAINT chk_course_file_category CHECK (file_category IN ('script', 'material', 'exercise', 'solution', 'reference', 'template', 'other'))
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_course_files_course ON course_files(course_id, order_index);
CREATE INDEX IF NOT EXISTS idx_course_files_media ON course_files(file_id) WHERE file_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_course_files_category ON course_files(file_category);
CREATE INDEX IF NOT EXISTS idx_course_files_uploader ON course_files(uploaded_by);
CREATE INDEX IF NOT EXISTS idx_course_files_public ON course_files(is_public) WHERE is_public = TRUE;
CREATE INDEX IF NOT EXISTS idx_course_files_ai ON course_files(processed_for_ai) WHERE processed_for_ai = FALSE;

COMMENT ON TABLE course_files IS 'Links uploaded files to courses for content management and AI processing';
COMMENT ON COLUMN course_files.file_category IS 'script=Kurs-Skript, material=Begleitmaterial, exercise=Übung, solution=Lösung, reference=Referenz, template=Vorlage';
COMMENT ON COLUMN course_files.processed_for_ai IS 'Flag for AI content extraction pipeline';
COMMENT ON COLUMN course_files.ai_extracted_text IS 'Full text extracted from document for AI indexing';
COMMENT ON COLUMN course_files.ai_summary IS 'AI-generated summary of the document';

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- ============================================================================
CREATE TRIGGER update_course_files_updated_at BEFORE UPDATE ON course_files
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- End of Migration: 048_course_files.sql
-- ============================================================================
