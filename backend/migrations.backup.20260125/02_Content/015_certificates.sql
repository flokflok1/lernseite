-- ============================================================================
-- Migration: 015_certificates.sql
-- Version: 1.0.0
-- Description: Database migration
-- Author: LernsystemX Migration System
-- Date: 2026-01-02
-- ============================================================================

CREATE TABLE IF NOT EXISTS assessments.certificate_templates (
    template_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    template_type VARCHAR(50) NOT NULL,
    design_json JSONB NOT NULL,
    background_url VARCHAR(500),
    logo_url VARCHAR(500),
    signature_url VARCHAR(500),
    active BOOLEAN DEFAULT TRUE,
    created_by UUID REFERENCES core.users(user_id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_template_type CHECK (template_type IN ('course', 'exam', 'skill', 'custom'))
);

CREATE INDEX IF NOT EXISTS idx_certificate_templates_type ON assessments.certificate_templates(template_type);
CREATE INDEX IF NOT EXISTS idx_certificate_templates_active ON assessments.certificate_templates(active) WHERE active = TRUE;

COMMENT ON TABLE assessments.certificate_templates IS 'Certificate design templates';
COMMENT ON COLUMN assessments.certificate_templates.design_json IS 'JSONB: layout, fonts, colors, placeholders';

-- ============================================================================
-- TABLE: certificates
-- Description: Issued certificates
-- ============================================================================
CREATE TABLE IF NOT EXISTS assessments.certificates (
    certificate_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES core.users(user_id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses.courses(course_id) ON DELETE SET NULL,
    exam_result_id UUID REFERENCES assessments.exam_results(result_id) ON DELETE SET NULL,
    template_id UUID REFERENCES assessments.certificate_templates(template_id) ON DELETE SET NULL,
    certificate_number VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    issued_date DATE NOT NULL,
    expiry_date DATE,
    verification_code VARCHAR(50) UNIQUE NOT NULL,
    pdf_url VARCHAR(500),
    metadata JSONB,
    revoked BOOLEAN DEFAULT FALSE,
    revoked_at TIMESTAMPTZ,
    revoked_reason TEXT,
    issued_by UUID REFERENCES core.users(user_id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_certificates_user ON assessments.certificates(user_id, issued_date DESC);
CREATE INDEX IF NOT EXISTS idx_certificates_course ON assessments.certificates(course_id);
CREATE INDEX IF NOT EXISTS idx_certificates_exam ON assessments.certificates(exam_result_id);
CREATE INDEX IF NOT EXISTS idx_certificates_number ON assessments.certificates(certificate_number);
CREATE INDEX IF NOT EXISTS idx_certificates_verification ON assessments.certificates(verification_code);
CREATE INDEX IF NOT EXISTS idx_certificates_revoked ON assessments.certificates(revoked) WHERE revoked = FALSE;

COMMENT ON TABLE assessments.certificates IS 'Issued certificates for courses, exams, and skills';

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- ============================================================================
DROP TRIGGER IF EXISTS update_certificate_templates_updated_at ON assessments.certificate_templates;
CREATE TRIGGER update_certificate_templates_updated_at BEFORE UPDATE ON assessments.certificate_templates
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- End of Migration: 015_certificates.sql
-- ============================================================================
