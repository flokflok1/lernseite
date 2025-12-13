-- ============================================================================
-- Migration: 016_certificates_progress.sql
-- Description: Certificate progress and skill tracking
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-01-17
-- ============================================================================

-- ============================================================================
-- TABLE: certificate_requirements
-- Description: Requirements for earning certificates
-- ============================================================================
CREATE TABLE IF NOT EXISTS certificate_requirements (
    requirement_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID REFERENCES courses(course_id) ON DELETE CASCADE,
    requirement_type VARCHAR(50) NOT NULL,
    requirement_data JSONB NOT NULL,
    description TEXT,
    order_index INTEGER DEFAULT 0,
    CONSTRAINT chk_cert_requirement_type CHECK (requirement_type IN ('course_completion', 'exam_pass', 'min_score', 'all_chapters', 'specific_lessons', 'time_spent'))
);

CREATE INDEX IF NOT EXISTS idx_cert_requirements_course ON certificate_requirements(course_id);
CREATE INDEX IF NOT EXISTS idx_cert_requirements_type ON certificate_requirements(requirement_type);

COMMENT ON TABLE certificate_requirements IS 'Requirements users must meet to earn certificates';

-- ============================================================================
-- TABLE: user_skills
-- Description: Skills earned by users
-- ============================================================================
CREATE TABLE IF NOT EXISTS user_skills (
    skill_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    skill_name VARCHAR(255) NOT NULL,
    skill_category VARCHAR(100),
    proficiency_level VARCHAR(20),
    verified BOOLEAN DEFAULT FALSE,
    verified_by UUID REFERENCES users(user_id) ON DELETE SET NULL,
    evidence_url VARCHAR(500),
    earned_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_skill_proficiency CHECK (proficiency_level IN ('beginner', 'intermediate', 'advanced', 'expert'))
);

CREATE INDEX IF NOT EXISTS idx_user_skills_user ON user_skills(user_id);
CREATE INDEX IF NOT EXISTS idx_user_skills_category ON user_skills(skill_category);
CREATE INDEX IF NOT EXISTS idx_user_skills_verified ON user_skills(verified) WHERE verified = TRUE;

COMMENT ON TABLE user_skills IS 'Skills and competencies earned by users';

-- ============================================================================
-- TABLE: skill_endorsements
-- Description: Endorsements of user skills by others
-- ============================================================================
CREATE TABLE IF NOT EXISTS skill_endorsements (
    endorsement_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    skill_id UUID REFERENCES user_skills(skill_id) ON DELETE CASCADE,
    endorsed_by UUID REFERENCES users(user_id) ON DELETE CASCADE,
    comment TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (skill_id, endorsed_by)
);

CREATE INDEX IF NOT EXISTS idx_skill_endorsements_skill ON skill_endorsements(skill_id);
CREATE INDEX IF NOT EXISTS idx_skill_endorsements_user ON skill_endorsements(endorsed_by);

COMMENT ON TABLE skill_endorsements IS 'Peer endorsements of user skills';

-- ============================================================================
-- End of Migration: 016_certificates_progress.sql
-- ============================================================================
