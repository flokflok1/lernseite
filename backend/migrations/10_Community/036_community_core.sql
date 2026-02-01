-- ============================================================================
-- Migration: 036_community_core.sql
-- Version: 1.0.0
-- Description: Database migration
-- Author: LernsystemX Migration System
-- Date: 2026-01-02
-- ============================================================================

CREATE TABLE IF NOT EXISTS support_systems.groups (
    group_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_user_id UUID REFERENCES core.users(user_id) ON DELETE SET NULL,
    organisation_id UUID REFERENCES organisations.organisations(organisation_id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    group_type VARCHAR(50) NOT NULL,
    is_private BOOLEAN DEFAULT FALSE,
    max_members INTEGER,
    avatar_url VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_group_type CHECK (group_type IN ('study', 'project', 'course', 'interest', 'organization'))
);

CREATE INDEX IF NOT EXISTS idx_groups_owner ON support_systems.groups(owner_user_id);
CREATE INDEX IF NOT EXISTS idx_groups_org ON support_systems.groups(organisation_id);
CREATE INDEX IF NOT EXISTS idx_groups_type ON support_systems.groups(group_type);
CREATE INDEX IF NOT EXISTS idx_groups_private ON support_systems.groups(is_private);

COMMENT ON TABLE support_systems.groups IS 'Community study groups and teams';

-- ============================================================================
-- TABLE: group_members
-- Description: Group membership
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_systems.group_members (
    member_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    group_id UUID REFERENCES support_systems.groups(group_id) ON DELETE CASCADE,
    user_id UUID REFERENCES core.users(user_id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'member',
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    left_at TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'active',
    CONSTRAINT chk_group_member_role CHECK (role IN ('owner', 'admin', 'moderator', 'member')),
    CONSTRAINT chk_group_member_status CHECK (status IN ('active', 'inactive', 'banned')),
    UNIQUE (group_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_group_members_group ON support_systems.group_members(group_id, status);
CREATE INDEX IF NOT EXISTS idx_group_members_user ON support_systems.group_members(user_id);
CREATE INDEX IF NOT EXISTS idx_group_members_role ON support_systems.group_members(role);

COMMENT ON TABLE support_systems.group_members IS 'Group membership with roles';

-- ============================================================================
-- TABLE: group_resources
-- Description: Shared resources within groups
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_systems.group_resources (
    resource_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    group_id UUID REFERENCES support_systems.groups(group_id) ON DELETE CASCADE,
    shared_by UUID REFERENCES core.users(user_id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    data JSONB NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_group_resource_type CHECK (resource_type IN ('file', 'link', 'course_copy', 'note', 'quiz', 'flashcard_set'))
);

CREATE INDEX IF NOT EXISTS idx_group_resources_group ON support_systems.group_resources(group_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_group_resources_type ON support_systems.group_resources(resource_type);
CREATE INDEX IF NOT EXISTS idx_group_resources_shared_by ON support_systems.group_resources(shared_by);

COMMENT ON TABLE support_systems.group_resources IS 'Resources shared within community groups';

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- ============================================================================
DROP TRIGGER IF EXISTS update_groups_updated_at ON support_systems.groups;
CREATE TRIGGER update_groups_updated_at BEFORE UPDATE ON support_systems.groups
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- End of Migration: 036_community_core.sql
-- ============================================================================
