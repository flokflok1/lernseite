-- ============================================================================
-- Migration: 036_community_core.sql
-- Description: Community groups and resources
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-01-17
-- ============================================================================

-- ============================================================================
-- TABLE: groups
-- Description: Community groups and teams
-- ============================================================================
CREATE TABLE IF NOT EXISTS groups (
    group_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    organization_id UUID REFERENCES organizations(organization_id) ON DELETE CASCADE,
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

CREATE INDEX IF NOT EXISTS idx_groups_owner ON groups(owner_user_id);
CREATE INDEX IF NOT EXISTS idx_groups_org ON groups(organization_id);
CREATE INDEX IF NOT EXISTS idx_groups_type ON groups(group_type);
CREATE INDEX IF NOT EXISTS idx_groups_private ON groups(is_private);

COMMENT ON TABLE groups IS 'Community study groups and teams';

-- ============================================================================
-- TABLE: group_members
-- Description: Group membership
-- ============================================================================
CREATE TABLE IF NOT EXISTS group_members (
    member_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    group_id UUID REFERENCES groups(group_id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'member',
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    left_at TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'active',
    CONSTRAINT chk_group_member_role CHECK (role IN ('owner', 'admin', 'moderator', 'member')),
    CONSTRAINT chk_group_member_status CHECK (status IN ('active', 'inactive', 'banned')),
    UNIQUE (group_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_group_members_group ON group_members(group_id, status);
CREATE INDEX IF NOT EXISTS idx_group_members_user ON group_members(user_id);
CREATE INDEX IF NOT EXISTS idx_group_members_role ON group_members(role);

COMMENT ON TABLE group_members IS 'Group membership with roles';

-- ============================================================================
-- TABLE: group_resources
-- Description: Shared resources within groups
-- ============================================================================
CREATE TABLE IF NOT EXISTS group_resources (
    resource_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    group_id UUID REFERENCES groups(group_id) ON DELETE CASCADE,
    shared_by UUID REFERENCES users(user_id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    data JSONB NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_group_resource_type CHECK (resource_type IN ('file', 'link', 'course_copy', 'note', 'quiz', 'flashcard_set'))
);

CREATE INDEX IF NOT EXISTS idx_group_resources_group ON group_resources(group_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_group_resources_type ON group_resources(resource_type);
CREATE INDEX IF NOT EXISTS idx_group_resources_shared_by ON group_resources(shared_by);

COMMENT ON TABLE group_resources IS 'Resources shared within community groups';

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- ============================================================================
CREATE TRIGGER update_groups_updated_at BEFORE UPDATE ON groups
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- End of Migration: 036_community_core.sql
-- ============================================================================
