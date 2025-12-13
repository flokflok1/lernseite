-- ============================================================================
-- Migration: 003_organisations.sql
-- Description: Organizations (schools and companies) core tables
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-01-17
-- ============================================================================

-- ============================================================================
-- TABLE: organizations
-- Description: Schools and companies using LSX
-- ============================================================================
CREATE TABLE IF NOT EXISTS organizations (
    organization_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    domain VARCHAR(255) UNIQUE,
    logo_url VARCHAR(500),
    billing_email VARCHAR(255),
    phone VARCHAR(50),
    address_street VARCHAR(255),
    address_city VARCHAR(100),
    address_state VARCHAR(100),
    address_country VARCHAR(2) DEFAULT 'DE',
    address_postal_code VARCHAR(20),
    tax_id VARCHAR(50),
    token_pool DECIMAL(15,2) DEFAULT 0,
    token_pool_limit DECIMAL(15,2),
    billing_rate DECIMAL(10,2),
    max_users INTEGER DEFAULT 100,
    max_courses INTEGER,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_org_type CHECK (type IN ('school', 'company')),
    CONSTRAINT chk_org_status CHECK (status IN ('active', 'suspended', 'trial', 'expired'))
);

CREATE INDEX IF NOT EXISTS idx_organizations_type ON organizations(type);
CREATE INDEX IF NOT EXISTS idx_organizations_domain ON organizations(domain) WHERE domain IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_organizations_status ON organizations(status) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS idx_organizations_name ON organizations(name);

COMMENT ON TABLE organizations IS 'Schools and companies with LSX subscriptions';
COMMENT ON COLUMN organizations.token_pool IS 'Available AI tokens for the organization';

-- ============================================================================
-- TABLE: organization_members
-- Description: Users belonging to organizations with their roles
-- ============================================================================
CREATE TABLE IF NOT EXISTS organization_members (
    org_member_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(organization_id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    role_in_org VARCHAR(50) NOT NULL,
    department VARCHAR(100),
    title VARCHAR(100),
    employee_id VARCHAR(50),
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    left_at TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'active',
    CONSTRAINT chk_org_member_role CHECK (role_in_org IN ('admin', 'teacher', 'manager', 'staff', 'employee', 'student')),
    CONSTRAINT chk_org_member_status CHECK (status IN ('active', 'inactive', 'suspended')),
    UNIQUE (organization_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_org_members_org ON organization_members(organization_id, status);
CREATE INDEX IF NOT EXISTS idx_org_members_user ON organization_members(user_id);
CREATE INDEX IF NOT EXISTS idx_org_members_role ON organization_members(role_in_org);
CREATE INDEX IF NOT EXISTS idx_org_members_status ON organization_members(status) WHERE status = 'active';

COMMENT ON TABLE organization_members IS 'Membership relationship between users and organizations';

-- ============================================================================
-- TABLE: organization_classes
-- Description: Classes/groups within organizations
-- ============================================================================
CREATE TABLE IF NOT EXISTS organization_classes (
    class_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(organization_id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    class_code VARCHAR(20) UNIQUE,
    teacher_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    max_students INTEGER DEFAULT 30,
    academic_year VARCHAR(20),
    semester VARCHAR(20),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_class_status CHECK (status IN ('active', 'archived', 'completed'))
);

CREATE INDEX IF NOT EXISTS idx_org_classes_org ON organization_classes(organization_id);
CREATE INDEX IF NOT EXISTS idx_org_classes_teacher ON organization_classes(teacher_id);
CREATE INDEX IF NOT EXISTS idx_org_classes_code ON organization_classes(class_code);
CREATE INDEX IF NOT EXISTS idx_org_classes_status ON organization_classes(status) WHERE status = 'active';

COMMENT ON TABLE organization_classes IS 'Classes/groups for schools and training programs';

-- ============================================================================
-- TABLE: class_enrollments
-- Description: Students enrolled in classes
-- ============================================================================
CREATE TABLE IF NOT EXISTS class_enrollments (
    enrollment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    class_id UUID REFERENCES organization_classes(class_id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    enrolled_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'active',
    CONSTRAINT chk_class_enrollment_status CHECK (status IN ('active', 'completed', 'dropped', 'withdrawn')),
    UNIQUE (class_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_class_enrollments_class ON class_enrollments(class_id, status);
CREATE INDEX IF NOT EXISTS idx_class_enrollments_user ON class_enrollments(user_id);
CREATE INDEX IF NOT EXISTS idx_class_enrollments_status ON class_enrollments(status) WHERE status = 'active';

COMMENT ON TABLE class_enrollments IS 'Student enrollment in organization classes';

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- ============================================================================
CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_org_classes_updated_at BEFORE UPDATE ON organization_classes
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- End of Migration: 003_organisations.sql
-- ============================================================================
