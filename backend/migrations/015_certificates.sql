-- ============================================================================
-- Migration: 015_certificates.sql
-- Description: Certificates and certificate templates
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-01-17
-- ============================================================================

-- ============================================================================
-- TABLE: certificate_templates
-- Description: Certificate design templates
-- ============================================================================
CREATE TABLE IF NOT EXISTS certificate_templates (
    template_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    template_type VARCHAR(50) NOT NULL,
    design_json JSONB NOT NULL,
    background_url VARCHAR(500),
    logo_url VARCHAR(500),
    signature_url VARCHAR(500),
    active BOOLEAN DEFAULT TRUE,
    created_by UUID REFERENCES users(user_id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_template_type CHECK (template_type IN ('course', 'exam', 'skill', 'custom'))
);

CREATE INDEX IF NOT EXISTS idx_certificate_templates_type ON certificate_templates(template_type);
CREATE INDEX IF NOT EXISTS idx_certificate_templates_active ON certificate_templates(active) WHERE active = TRUE;

COMMENT ON TABLE certificate_templates IS 'Certificate design templates';
COMMENT ON COLUMN certificate_templates.design_json IS 'JSONB: layout, fonts, colors, placeholders';

-- ============================================================================
-- TABLE: certificates
-- Description: Issued certificates
-- ============================================================================
CREATE TABLE IF NOT EXISTS certificates (
    certificate_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses(course_id) ON DELETE SET NULL,
    exam_result_id UUID REFERENCES exam_results(result_id) ON DELETE SET NULL,
    template_id UUID REFERENCES certificate_templates(template_id) ON DELETE SET NULL,
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
    issued_by UUID REFERENCES users(user_id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_certificates_user ON certificates(user_id, issued_date DESC);
CREATE INDEX IF NOT EXISTS idx_certificates_course ON certificates(course_id);
CREATE INDEX IF NOT EXISTS idx_certificates_exam ON certificates(exam_result_id);
CREATE INDEX IF NOT EXISTS idx_certificates_number ON certificates(certificate_number);
CREATE INDEX IF NOT EXISTS idx_certificates_verification ON certificates(verification_code);
CREATE INDEX IF NOT EXISTS idx_certificates_revoked ON certificates(revoked) WHERE revoked = FALSE;

COMMENT ON TABLE certificates IS 'Issued certificates for courses, exams, and skills';

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- ============================================================================
CREATE TRIGGER update_certificate_templates_updated_at BEFORE UPDATE ON certificate_templates
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- End of Migration: 015_certificates.sql
-- ============================================================================
