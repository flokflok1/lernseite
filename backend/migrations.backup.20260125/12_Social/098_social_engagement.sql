-- ============================================================================
-- Migration: 098_social_engagement.sql
-- Description: Social Engagement - Likes, Comments, Shares, Bookmarks
--              Feature Flags:
--                - likes_reactions (DISABLED)
--                - comments (ENABLED for courses, extending to posts)
--                - shares (DISABLED)
--                - bookmarks (DISABLED)
--              Compliance: GDPR Art. 17 (right to erasure), DSA Art. 14 (reporting)
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-01-16
-- ============================================================================
-- Previous number: 081 (12_Social) → Renumbered to 098 to resolve duplicates
-- Phase: Social Network Layer - Engagement (Likes, Comments, Shares, Bookmarks)
-- ============================================================================

BEGIN;

-- =====================================================
-- 1. SOCIAL LIKES (Simple Like System)
-- =====================================================

CREATE TABLE IF NOT EXISTS social_likes (
    like_id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id VARCHAR(36) NOT NULL,
    post_id VARCHAR(36) NOT NULL REFERENCES social_posts(post_id) ON DELETE CASCADE,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_user_post_like UNIQUE(user_id, post_id)
);

CREATE INDEX idx_likes_user ON social_likes(user_id);
CREATE INDEX idx_likes_post ON social_likes(post_id);
CREATE INDEX idx_likes_created ON social_likes(created_at DESC);

COMMENT ON TABLE social_likes IS 'Simple likes for posts - Feature flag: likes_reactions';

-- =====================================================
-- 2. SOCIAL REACTIONS (Extended: Love, Haha, Wow, Sad, Angry)
-- =====================================================

CREATE TABLE IF NOT EXISTS social_reactions (
    reaction_id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id VARCHAR(36) NOT NULL,
    post_id VARCHAR(36) NOT NULL REFERENCES social_posts(post_id) ON DELETE CASCADE,

    -- Reaction Type
    reaction_type VARCHAR(20) NOT NULL, -- 'like', 'love', 'haha', 'wow', 'sad', 'angry'

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_user_post_reaction UNIQUE(user_id, post_id),
    CONSTRAINT chk_reaction_type CHECK (reaction_type IN (
        'like', 'love', 'haha', 'wow', 'sad', 'angry', 'thinking', 'celebrate'
    ))
);

CREATE INDEX idx_reactions_user ON social_reactions(user_id);
CREATE INDEX idx_reactions_post ON social_reactions(post_id);
CREATE INDEX idx_reactions_type ON social_reactions(reaction_type);
CREATE INDEX idx_reactions_created ON social_reactions(created_at DESC);

COMMENT ON TABLE social_reactions IS 'Extended reactions (Facebook-style) - Feature flag: likes_reactions';
COMMENT ON COLUMN social_reactions.reaction_type IS 'Reaction emoji: like, love, haha, wow, sad, angry, etc.';

-- =====================================================
-- 3. SOCIAL COMMENTS
-- =====================================================

CREATE TABLE IF NOT EXISTS social_comments (
    comment_id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    post_id VARCHAR(36) NOT NULL REFERENCES social_posts(post_id) ON DELETE CASCADE,
    user_id VARCHAR(36) NOT NULL,

    -- Content
    content TEXT NOT NULL,
    content_language VARCHAR(10) DEFAULT 'de',

    -- Threading (Replies)
    parent_comment_id VARCHAR(36) REFERENCES social_comments(comment_id) ON DELETE CASCADE,
    thread_level INTEGER DEFAULT 0, -- 0 = top-level, 1 = reply, 2 = reply to reply (max 2)

    -- Editing
    is_edited BOOLEAN DEFAULT FALSE,
    edited_at TIMESTAMP,

    -- Moderation
    moderation_status VARCHAR(20) DEFAULT 'pending',
    moderated_by VARCHAR(36),
    moderated_at TIMESTAMP,

    -- Engagement
    likes_count INTEGER DEFAULT 0,
    replies_count INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP, -- Soft delete

    CONSTRAINT chk_comment_thread_level CHECK (thread_level >= 0 AND thread_level <= 2),
    CONSTRAINT chk_comment_moderation CHECK (moderation_status IN (
        'pending', 'approved', 'rejected', 'flagged', 'ai_approved'
    ))
);

CREATE INDEX idx_comments_post ON social_comments(post_id);
CREATE INDEX idx_comments_user ON social_comments(user_id);
CREATE INDEX idx_comments_parent ON social_comments(parent_comment_id);
CREATE INDEX idx_comments_created ON social_comments(created_at DESC);
CREATE INDEX idx_comments_moderation ON social_comments(moderation_status);
CREATE INDEX idx_comments_deleted ON social_comments(deleted_at) WHERE deleted_at IS NULL;

COMMENT ON TABLE social_comments IS 'Comments on posts with threading - Feature flag: comments';
COMMENT ON COLUMN social_comments.thread_level IS 'Max depth: 2 (comment -> reply -> reply to reply)';
COMMENT ON COLUMN social_comments.moderation_status IS 'DSA Art. 14 - Content moderation status';

-- =====================================================
-- 4. COMMENT LIKES
-- =====================================================

CREATE TABLE IF NOT EXISTS social_comment_likes (
    like_id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id VARCHAR(36) NOT NULL,
    comment_id VARCHAR(36) NOT NULL REFERENCES social_comments(comment_id) ON DELETE CASCADE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_user_comment_like UNIQUE(user_id, comment_id)
);

CREATE INDEX idx_comment_likes_user ON social_comment_likes(user_id);
CREATE INDEX idx_comment_likes_comment ON social_comment_likes(comment_id);

COMMENT ON TABLE social_comment_likes IS 'Likes on comments - Feature flag: likes_reactions';

-- =====================================================
-- 5. SOCIAL SHARES (Repost/Share to Feed)
-- =====================================================

CREATE TABLE IF NOT EXISTS social_shares (
    share_id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id VARCHAR(36) NOT NULL, -- Who shared
    post_id VARCHAR(36) NOT NULL REFERENCES social_posts(post_id) ON DELETE CASCADE,

    -- Share Type
    share_type VARCHAR(20) DEFAULT 'repost', -- 'repost', 'quote', 'external_link'

    -- Quote Share (with comment)
    quote_text TEXT,

    -- Visibility
    visibility VARCHAR(20) DEFAULT 'public',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_share_type CHECK (share_type IN ('repost', 'quote', 'external_link')),
    CONSTRAINT chk_share_visibility CHECK (visibility IN (
        'public', 'followers', 'private'
    ))
);

CREATE INDEX idx_shares_user ON social_shares(user_id);
CREATE INDEX idx_shares_post ON social_shares(post_id);
CREATE INDEX idx_shares_type ON social_shares(share_type);
CREATE INDEX idx_shares_created ON social_shares(created_at DESC);

COMMENT ON TABLE social_shares IS 'Share/repost posts to feed - Feature flag: shares';
COMMENT ON COLUMN social_shares.share_type IS 'repost (simple share), quote (share with comment)';

-- =====================================================
-- 6. SOCIAL BOOKMARKS (Save for Later)
-- =====================================================

CREATE TABLE IF NOT EXISTS social_bookmarks (
    bookmark_id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id VARCHAR(36) NOT NULL,
    post_id VARCHAR(36) NOT NULL REFERENCES social_posts(post_id) ON DELETE CASCADE,

    -- Collections (Folders)
    collection_name VARCHAR(100), -- NULL = default collection

    -- Notes
    notes TEXT, -- Private notes about bookmark

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_user_post_bookmark UNIQUE(user_id, post_id)
);

CREATE INDEX idx_bookmarks_user ON social_bookmarks(user_id);
CREATE INDEX idx_bookmarks_post ON social_bookmarks(post_id);
CREATE INDEX idx_bookmarks_collection ON social_bookmarks(user_id, collection_name);
CREATE INDEX idx_bookmarks_created ON social_bookmarks(created_at DESC);

COMMENT ON TABLE social_bookmarks IS 'Save posts for later (bookmarks) - Feature flag: bookmarks';
COMMENT ON COLUMN social_bookmarks.collection_name IS 'User-defined bookmark collections (folders)';
COMMENT ON COLUMN social_bookmarks.notes IS 'Private notes (GDPR-protected, only visible to owner)';

-- =====================================================
-- 7. BOOKMARK COLLECTIONS
-- =====================================================

CREATE TABLE IF NOT EXISTS social_bookmark_collections (
    collection_id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id VARCHAR(36) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_private BOOLEAN DEFAULT TRUE,

    -- Counts
    bookmarks_count INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_user_collection_name UNIQUE(user_id, name)
);

CREATE INDEX idx_collections_user ON social_bookmark_collections(user_id);
CREATE INDEX idx_collections_private ON social_bookmark_collections(is_private);

COMMENT ON TABLE social_bookmark_collections IS 'User-defined bookmark collections (folders)';

-- =====================================================
-- 8. TRIGGERS - Update Counters
-- =====================================================

-- Update post likes count
CREATE OR REPLACE FUNCTION update_post_likes_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE social_posts
        SET likes_count = likes_count + 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE post_id = NEW.post_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE social_posts
        SET likes_count = GREATEST(likes_count - 1, 0),
            updated_at = CURRENT_TIMESTAMP
        WHERE post_id = OLD.post_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_likes_update_post_count
    AFTER INSERT OR DELETE ON social_likes
    FOR EACH ROW EXECUTE FUNCTION update_post_likes_count();

-- Update post comments count
CREATE OR REPLACE FUNCTION update_post_comments_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' AND NEW.parent_comment_id IS NULL AND NEW.deleted_at IS NULL THEN
        -- Top-level comment added
        UPDATE social_posts
        SET comments_count = comments_count + 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE post_id = NEW.post_id;
    ELSIF TG_OP = 'DELETE' AND OLD.parent_comment_id IS NULL THEN
        -- Top-level comment deleted
        UPDATE social_posts
        SET comments_count = GREATEST(comments_count - 1, 0),
            updated_at = CURRENT_TIMESTAMP
        WHERE post_id = OLD.post_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_comments_update_post_count
    AFTER INSERT OR DELETE ON social_comments
    FOR EACH ROW EXECUTE FUNCTION update_post_comments_count();

-- Update comment replies count
CREATE OR REPLACE FUNCTION update_comment_replies_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' AND NEW.parent_comment_id IS NOT NULL AND NEW.deleted_at IS NULL THEN
        -- Reply added
        UPDATE social_comments
        SET replies_count = replies_count + 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE comment_id = NEW.parent_comment_id;
    ELSIF TG_OP = 'DELETE' AND OLD.parent_comment_id IS NOT NULL THEN
        -- Reply deleted
        UPDATE social_comments
        SET replies_count = GREATEST(replies_count - 1, 0),
            updated_at = CURRENT_TIMESTAMP
        WHERE comment_id = OLD.parent_comment_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_comments_update_replies_count
    AFTER INSERT OR DELETE ON social_comments
    FOR EACH ROW EXECUTE FUNCTION update_comment_replies_count();

-- Update post shares count
CREATE OR REPLACE FUNCTION update_post_shares_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE social_posts
        SET shares_count = shares_count + 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE post_id = NEW.post_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE social_posts
        SET shares_count = GREATEST(shares_count - 1, 0),
            updated_at = CURRENT_TIMESTAMP
        WHERE post_id = OLD.post_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_shares_update_post_count
    AFTER INSERT OR DELETE ON social_shares
    FOR EACH ROW EXECUTE FUNCTION update_post_shares_count();

-- Update comment likes count
CREATE OR REPLACE FUNCTION update_comment_likes_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE social_comments
        SET likes_count = likes_count + 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE comment_id = NEW.comment_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE social_comments
        SET likes_count = GREATEST(likes_count - 1, 0),
            updated_at = CURRENT_TIMESTAMP
        WHERE comment_id = OLD.comment_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_comment_likes_update_count
    AFTER INSERT OR DELETE ON social_comment_likes
    FOR EACH ROW EXECUTE FUNCTION update_comment_likes_count();

COMMIT;

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Get most liked posts
-- SELECT p.post_id, p.content, p.likes_count, p.comments_count, p.shares_count
-- FROM social_posts p
-- WHERE p.deleted_at IS NULL
--   AND p.moderation_status = 'approved'
-- ORDER BY p.likes_count DESC
-- LIMIT 20;

-- Get top commenters
-- SELECT user_id, COUNT(*) as comment_count
-- FROM social_comments
-- WHERE deleted_at IS NULL
--   AND moderation_status IN ('approved', 'ai_approved')
-- GROUP BY user_id
-- ORDER BY comment_count DESC
-- LIMIT 20;

-- =====================================================
-- END MIGRATION 081
-- =====================================================
