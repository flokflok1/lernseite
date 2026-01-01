-- ============================================================================
-- Migration: 037_community_messages.sql
-- Description: Group messaging and discussions
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-01-17
-- ============================================================================

-- ============================================================================
-- TABLE: group_messages
-- Description: Messages within groups
-- ============================================================================
CREATE TABLE IF NOT EXISTS group_messages (
    message_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    group_id UUID REFERENCES groups(group_id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    parent_message_id UUID REFERENCES group_messages(message_id) ON DELETE CASCADE,
    message_text TEXT NOT NULL,
    attachments JSONB,
    edited BOOLEAN DEFAULT FALSE,
    edited_at TIMESTAMPTZ,
    deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_group_messages_group ON group_messages(group_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_group_messages_user ON group_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_group_messages_parent ON group_messages(parent_message_id);
CREATE INDEX IF NOT EXISTS idx_group_messages_deleted ON group_messages(deleted) WHERE deleted = FALSE;

COMMENT ON TABLE group_messages IS 'Messages and discussions within community groups';

-- ============================================================================
-- TABLE: group_discussions
-- Description: Discussion threads in groups
-- ============================================================================
CREATE TABLE IF NOT EXISTS group_discussions (
    discussion_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    group_id UUID REFERENCES groups(group_id) ON DELETE CASCADE,
    created_by UUID REFERENCES users(user_id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    pinned BOOLEAN DEFAULT FALSE,
    locked BOOLEAN DEFAULT FALSE,
    view_count INTEGER DEFAULT 0,
    reply_count INTEGER DEFAULT 0,
    last_activity_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_group_discussions_group ON group_discussions(group_id, last_activity_at DESC);
CREATE INDEX IF NOT EXISTS idx_group_discussions_creator ON group_discussions(created_by);
CREATE INDEX IF NOT EXISTS idx_group_discussions_pinned ON group_discussions(pinned) WHERE pinned = TRUE;

COMMENT ON TABLE group_discussions IS 'Discussion threads within community groups';

-- ============================================================================
-- TABLE: group_posts
-- Description: Posts within discussion threads
-- ============================================================================
CREATE TABLE IF NOT EXISTS group_posts (
    post_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    discussion_id UUID REFERENCES group_discussions(discussion_id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    content TEXT NOT NULL,
    attachments JSONB,
    likes_count INTEGER DEFAULT 0,
    edited BOOLEAN DEFAULT FALSE,
    edited_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_group_posts_discussion ON group_posts(discussion_id, created_at ASC);
CREATE INDEX IF NOT EXISTS idx_group_posts_user ON group_posts(user_id);

COMMENT ON TABLE group_posts IS 'Posts within discussion threads';

-- ============================================================================
-- End of Migration: 037_community_messages.sql
-- ============================================================================
