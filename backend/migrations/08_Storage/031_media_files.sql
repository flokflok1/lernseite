-- ============================================================================
-- Migration: 031_media_files.sql
-- Version: 1.0.0
-- Description: Database migration
-- Author: LernsystemX Migration System
-- Date: 2026-01-02
-- ============================================================================

CREATE TABLE IF NOT EXISTS billing_storage.media_files (
    file_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    uploaded_by UUID REFERENCES core.users(user_id) ON DELETE SET NULL,
    organisation_id UUID REFERENCES organisations.organisations(organisation_id) ON DELETE SET NULL,
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

CREATE INDEX IF NOT EXISTS idx_media_files_uploader ON billing_storage.media_files(uploaded_by, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_media_files_org ON billing_storage.media_files(organisation_id);
CREATE INDEX IF NOT EXISTS idx_media_files_type ON billing_storage.media_files(file_type);
CREATE INDEX IF NOT EXISTS idx_media_files_mime ON billing_storage.media_files(mime_type);
CREATE INDEX IF NOT EXISTS idx_media_files_status ON billing_storage.media_files(status);
CREATE INDEX IF NOT EXISTS idx_media_files_created ON billing_storage.media_files(created_at DESC);

COMMENT ON TABLE billing_storage.media_files IS 'Uploaded media files with metadata and virus scanning';

-- ============================================================================
-- TABLE: media_thumbnails
-- Description: Generated thumbnails for images and videos
-- ============================================================================
CREATE TABLE IF NOT EXISTS storage.media_thumbnails (
    thumbnail_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_id UUID REFERENCES billing_storage.media_files(file_id) ON DELETE CASCADE,
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

CREATE INDEX IF NOT EXISTS idx_media_thumbnails_file ON storage.media_thumbnails(file_id);
CREATE INDEX IF NOT EXISTS idx_media_thumbnails_size ON storage.media_thumbnails(size_name);

COMMENT ON TABLE storage.media_thumbnails IS 'Generated thumbnails for media files';

-- ============================================================================
-- EXTENSION: Storage Packages & Virus Scanning (2026-01-09)
-- ============================================================================

-- =====================================================
-- 1. Storage Packages (Tiered Storage Limits)
-- =====================================================

CREATE TABLE IF NOT EXISTS storage.storage_packages (
    package_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    package_code VARCHAR(50) NOT NULL UNIQUE,
    package_name VARCHAR(100) NOT NULL,
    storage_limit_mb BIGINT,  -- NULL = unlimited
    file_size_limit_mb INTEGER NOT NULL,
    price_monthly DECIMAL(10,2),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_storage_packages_code ON storage.storage_packages(package_code);

COMMENT ON TABLE storage.storage_packages IS
'Storage packages with tiered limits (Starter/Basic/Pro/Enterprise/Unlimited)';

-- Seed Standard Packages
INSERT INTO storage.storage_packages
(package_code, package_name, storage_limit_mb, file_size_limit_mb, price_monthly) VALUES
('starter', 'Starter (500 MB)', 500, 10, 0.00),
('basic', 'Basic (2 GB)', 2048, 25, 9.99),
('pro', 'Pro (10 GB)', 10240, 100, 29.99),
('enterprise', 'Enterprise (50 GB)', 51200, 500, 99.99),
('unlimited', 'Unlimited', NULL, 1000, 299.99)
ON CONFLICT (package_code) DO NOTHING;

-- =====================================================
-- 2. Organisation Storage Tracking
-- =====================================================

CREATE TABLE IF NOT EXISTS storage.organisation_storage (
    organisation_id UUID PRIMARY KEY REFERENCES organisations.organisations(organisation_id) ON DELETE CASCADE,
    storage_package_id UUID REFERENCES storage.storage_packages(package_id),

    -- Usage Tracking
    storage_used_mb BIGINT DEFAULT 0,
    file_count INTEGER DEFAULT 0,

    -- Limits
    storage_limit_mb BIGINT,  -- NULL = unlimited
    file_size_limit_mb INTEGER DEFAULT 10,

    -- Billing
    overage_mb BIGINT DEFAULT 0,
    overage_charges DECIMAL(10,2) DEFAULT 0.00,

    last_calculated_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_org_storage_package ON storage.organisation_storage(storage_package_id);
CREATE INDEX idx_org_storage_usage ON storage.organisation_storage(storage_used_mb DESC);

COMMENT ON TABLE storage.organisation_storage IS
'Per-organisation storage usage and limits';

-- =====================================================
-- 3. Add Storage Limits to Organisations
-- =====================================================

ALTER TABLE organisations.organisations
ADD COLUMN IF NOT EXISTS storage_limit_mb BIGINT,
ADD COLUMN IF NOT EXISTS file_size_limit_mb INTEGER DEFAULT 10,
ADD COLUMN IF NOT EXISTS storage_package VARCHAR(50) DEFAULT 'starter';

CREATE INDEX IF NOT EXISTS idx_organisations_storage_package
ON organisations.organisations(storage_package);

COMMENT ON COLUMN organisations.organisations.storage_limit_mb IS
'Total storage limit in MB (NULL = unlimited)';

COMMENT ON COLUMN organisations.organisations.file_size_limit_mb IS
'Maximum file size per upload in MB';

-- =====================================================
-- 4. Virus Scan Queue (Async Processing)
-- =====================================================

CREATE TABLE IF NOT EXISTS storage.virus_scan_queue (
    scan_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id UUID NOT NULL REFERENCES billing_storage.media_files(file_id) ON DELETE CASCADE,

    -- Scan Status
    status VARCHAR(50) DEFAULT 'pending',  -- pending|scanning|completed|failed
    scan_engine VARCHAR(50) DEFAULT 'clamav',

    -- Priority
    priority INTEGER DEFAULT 5,  -- 1=highest, 10=lowest

    -- Results
    scan_result VARCHAR(50),  -- clean|infected|suspicious|error
    threat_names TEXT[],
    scan_details JSONB,

    -- Timing
    queued_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,

    -- Retry Logic
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    last_error TEXT,

    CONSTRAINT chk_scan_status CHECK (status IN ('pending', 'scanning', 'completed', 'failed')),
    CONSTRAINT chk_scan_result CHECK (scan_result IN ('clean', 'infected', 'suspicious', 'error', NULL))
);

CREATE INDEX idx_virus_scan_status ON storage.virus_scan_queue(status, priority);
CREATE INDEX idx_virus_scan_file ON storage.virus_scan_queue(file_id);
CREATE INDEX idx_virus_scan_queued ON storage.virus_scan_queue(queued_at);

COMMENT ON TABLE storage.virus_scan_queue IS
'Async virus scan queue for uploaded files (ClamAV integration)';

-- =====================================================
-- 5. Quarantine Log (Security Audit)
-- =====================================================

CREATE TABLE IF NOT EXISTS storage.quarantine_log (
    quarantine_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id UUID NOT NULL REFERENCES billing_storage.media_files(file_id) ON DELETE CASCADE,

    -- Detection
    threat_name VARCHAR(255) NOT NULL,
    scan_engine VARCHAR(50) DEFAULT 'clamav',
    detected_at TIMESTAMPTZ DEFAULT NOW(),

    -- File Info
    original_filename VARCHAR(255) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    uploaded_by UUID REFERENCES core.users(user_id),
    organisation_id UUID REFERENCES organisations.organisations(organisation_id),

    -- Actions
    action_taken VARCHAR(50) DEFAULT 'quarantined',  -- quarantined|deleted|allowed
    reviewed_by UUID REFERENCES core.users(user_id),
    reviewed_at TIMESTAMPTZ,
    review_notes TEXT,

    -- Metadata
    scan_details JSONB,
    file_hash VARCHAR(64),

    CONSTRAINT chk_quarantine_action CHECK (action_taken IN ('quarantined', 'deleted', 'allowed', 'false_positive'))
);

CREATE INDEX idx_quarantine_file ON storage.quarantine_log(file_id);
CREATE INDEX idx_quarantine_org ON storage.quarantine_log(organisation_id);
CREATE INDEX idx_quarantine_date ON storage.quarantine_log(detected_at DESC);
CREATE INDEX idx_quarantine_action ON storage.quarantine_log(action_taken);

COMMENT ON TABLE storage.quarantine_log IS
'Audit log for infected/quarantined files (security compliance)';

-- =====================================================
-- 6. Helper Functions
-- =====================================================

-- Function: Check if organisation has storage available
CREATE OR REPLACE FUNCTION check_storage_available(
    p_organisation_id UUID,
    p_file_size_mb DECIMAL
) RETURNS BOOLEAN AS $$
DECLARE
    v_storage_limit BIGINT;
    v_storage_used BIGINT;
    v_file_size_limit INTEGER;
BEGIN
    -- Get limits
    SELECT storage_limit_mb, storage_used_mb, file_size_limit_mb
    INTO v_storage_limit, v_storage_used, v_file_size_limit
    FROM storage.organisation_storage
    WHERE organisation_id = p_organisation_id;

    -- If no record, check organisations table
    IF v_storage_limit IS NULL THEN
        SELECT storage_limit_mb, file_size_limit_mb
        INTO v_storage_limit, v_file_size_limit
        FROM organisations.organisations
        WHERE organisation_id = p_organisation_id;
    END IF;

    -- NULL = unlimited
    IF v_storage_limit IS NULL THEN
        RETURN TRUE;
    END IF;

    -- Check file size limit
    IF p_file_size_mb > v_file_size_limit THEN
        RETURN FALSE;
    END IF;

    -- Check total storage limit
    IF (v_storage_used + p_file_size_mb) > v_storage_limit THEN
        RETURN FALSE;
    END IF;

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION check_storage_available IS
'Checks if organisation has enough storage quota for upload';

-- Function: Queue file for virus scan
CREATE OR REPLACE FUNCTION queue_virus_scan(
    p_file_id UUID,
    p_priority INTEGER DEFAULT 5
) RETURNS UUID AS $$
DECLARE
    v_scan_id UUID;
BEGIN
    INSERT INTO storage.virus_scan_queue (file_id, priority)
    VALUES (p_file_id, p_priority)
    RETURNING scan_id INTO v_scan_id;

    RETURN v_scan_id;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION queue_virus_scan IS
'Queues a file for async virus scanning';

-- Function: Mark file as infected and quarantine
CREATE OR REPLACE FUNCTION mark_file_infected(
    p_file_id UUID,
    p_threat_name VARCHAR,
    p_scan_engine VARCHAR DEFAULT 'clamav'
) RETURNS VOID AS $$
DECLARE
    v_file RECORD;
BEGIN
    -- Get file details
    SELECT * INTO v_file
    FROM billing_storage.media_files
    WHERE file_id = p_file_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'File not found: %', p_file_id;
    END IF;

    -- Update file status
    UPDATE billing_storage.media_files
    SET virus_scanned = TRUE,
        virus_scan_result = 'infected',
        status = 'deleted'  -- Prevent access
    WHERE file_id = p_file_id;

    -- Log to quarantine
    INSERT INTO storage.quarantine_log (
        file_id, threat_name, scan_engine,
        original_filename, file_size_bytes,
        uploaded_by, organisation_id
    ) VALUES (
        p_file_id, p_threat_name, p_scan_engine,
        v_file.original_filename, v_file.file_size_bytes,
        v_file.uploaded_by, v_file.organisation_id
    );

    RAISE NOTICE 'File quarantined: % (Threat: %)', v_file.original_filename, p_threat_name;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION mark_file_infected IS
'Marks file as infected and moves to quarantine';

-- =====================================================
-- 7. Triggers
-- =====================================================

-- Trigger: Auto-queue virus scan on file upload
CREATE OR REPLACE FUNCTION trigger_auto_virus_scan()
RETURNS TRIGGER AS $$
BEGIN
    -- Queue for scan if not already scanned
    IF NEW.virus_scanned = FALSE THEN
        PERFORM queue_virus_scan(NEW.file_id);
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_media_file_virus_scan ON billing_storage.media_files;
CREATE TRIGGER trigger_media_file_virus_scan
AFTER INSERT ON billing_storage.media_files
FOR EACH ROW
EXECUTE FUNCTION trigger_auto_virus_scan();

-- Trigger: Update organisation storage usage
CREATE OR REPLACE FUNCTION update_organisation_storage()
RETURNS TRIGGER AS $$
DECLARE
    v_org_id UUID;
BEGIN
    -- Get organisation_id
    IF TG_OP = 'INSERT' THEN
        v_org_id := NEW.organisation_id;
    ELSIF TG_OP = 'DELETE' THEN
        v_org_id := OLD.organisation_id;
    END IF;

    IF v_org_id IS NULL THEN
        RETURN NEW;
    END IF;

    -- Update usage
    INSERT INTO storage.organisation_storage (organisation_id, storage_used_mb, file_count)
    SELECT
        organisation_id,
        COALESCE(SUM(file_size_bytes) / 1024 / 1024, 0) AS storage_used_mb,
        COUNT(*) AS file_count
    FROM billing_storage.media_files
    WHERE organisation_id = v_org_id
    AND status != 'deleted'
    GROUP BY organisation_id
    ON CONFLICT (organisation_id) DO UPDATE
    SET storage_used_mb = EXCLUDED.storage_used_mb,
        file_count = EXCLUDED.file_count,
        updated_at = NOW();

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_org_storage_insert ON billing_storage.media_files;
CREATE TRIGGER trigger_update_org_storage_insert
AFTER INSERT ON billing_storage.media_files
FOR EACH ROW
EXECUTE FUNCTION update_organisation_storage();

DROP TRIGGER IF EXISTS trigger_update_org_storage_delete ON billing_storage.media_files;
CREATE TRIGGER trigger_update_org_storage_delete
AFTER DELETE ON billing_storage.media_files
FOR EACH ROW
EXECUTE FUNCTION update_organisation_storage();

-- =====================================================
-- 8. Row-Level Security für Storage
-- =====================================================

ALTER TABLE billing_storage.media_files ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS tenant_isolation_policy ON billing_storage.media_files;
CREATE POLICY tenant_isolation_policy ON billing_storage.media_files
    FOR ALL
    USING (
        organisation_id IS NULL  -- System files
        OR organisation_id = current_organisation_id()  -- Own org
        OR uploaded_by = current_setting('app.current_user_id', true)::UUID  -- Own files
    );

DROP POLICY IF EXISTS admin_bypass_policy ON billing_storage.media_files;
CREATE POLICY admin_bypass_policy ON billing_storage.media_files
    FOR ALL
    TO PUBLIC
    USING (is_admin_user());

COMMENT ON POLICY tenant_isolation_policy ON billing_storage.media_files IS
'Users see only files from their organisation or their own uploads';

-- =====================================================
-- ENDE EXTENSION
-- =====================================================

-- Verify Extension
DO $$
BEGIN
    RAISE NOTICE '✅ Migration 031 Extended: Storage Packages & Virus Scanning';
    RAISE NOTICE 'Neue Tabellen:';
    RAISE NOTICE '  - storage.storage_packages (5 packages)';
    RAISE NOTICE '  - storage.organisation_storage';
    RAISE NOTICE '  - storage.virus_scan_queue';
    RAISE NOTICE '  - storage.quarantine_log';
    RAISE NOTICE 'Neue Functions:';
    RAISE NOTICE '  - check_storage_available()';
    RAISE NOTICE '  - queue_virus_scan()';
    RAISE NOTICE '  - mark_file_infected()';
    RAISE NOTICE 'Triggers:';
    RAISE NOTICE '  - Auto virus scan on upload';
    RAISE NOTICE '  - Auto storage usage tracking';
END $$;

-- =====================================================
-- AI PDF Cache (MOVED FROM 03_AI/048_consolidated.sql)
-- Description: Cached PDF analysis results for reuse
-- NOTE: This table was originally in 03_AI migration but moved here
--       because storage schema wasn't available yet (forward reference)
-- =====================================================

CREATE TABLE IF NOT EXISTS storage.pdf_cache (
    cache_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- File identification
    file_hash VARCHAR(64) NOT NULL UNIQUE,
    original_filename VARCHAR(255),
    file_size_bytes BIGINT,
    page_count INTEGER,

    -- Extracted content
    extracted_text TEXT,
    extracted_metadata JSONB DEFAULT '{}',
    structure_analysis JSONB DEFAULT '{}',

    -- Processing info
    extraction_method VARCHAR(50) DEFAULT 'pdfplumber',
    processing_time_ms INTEGER,

    -- Cache management
    access_count INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_pdf_cache_hash ON storage.pdf_cache(file_hash);
CREATE INDEX IF NOT EXISTS idx_pdf_cache_expires ON storage.pdf_cache(expires_at) WHERE expires_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_pdf_cache_accessed ON storage.pdf_cache(last_accessed_at DESC);

COMMENT ON TABLE storage.pdf_cache IS 'Cached PDF extraction results to avoid redundant processing';
COMMENT ON COLUMN storage.pdf_cache.file_hash IS 'SHA-256 hash of file content for deduplication';
COMMENT ON COLUMN storage.pdf_cache.structure_analysis IS 'AI-analyzed structure (headings, sections, key topics)';

-- ============================================================================
-- End of Migration: 031_media_files.sql
-- ============================================================================
