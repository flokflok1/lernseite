-- =====================================================
-- Migration 080: Social Follow System
-- =====================================================
-- Purpose: Follow/unfollow users, followers list, following list
-- Feature Flag: follow_system (DISABLED by default)
-- Compliance: GDPR Art. 5 (data minimization), Privacy by Design
--
-- Tables:
-- - social_follows (follow relationships)
-- - social_follow_suggestions (AI-powered suggestions)
-- - social_follow_blocks (blocked users)
--
-- Created: 2026-01-10
-- Author: Enterprise Migration
-- =====================================================

BEGIN;

-- =====================================================
-- 1. SOCIAL FOLLOWS (Follow Relationships)
-- =====================================================

CREATE TABLE IF NOT EXISTS social_follows (
    follow_id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,

    follower_user_id VARCHAR(36) NOT NULL, -- Who is following
    followed_user_id VARCHAR(36) NOT NULL, -- Who is being followed

    -- Privacy
    is_approved BOOLEAN DEFAULT TRUE, -- For private accounts (pending follow requests)
    requested_at TIMESTAMP,

    -- Notification
    notification_sent BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_follow_relationship UNIQUE(follower_user_id, followed_user_id),
    CONSTRAINT chk_no_self_follow CHECK (follower_user_id != followed_user_id)
);

CREATE INDEX idx_follows_follower ON social_follows(follower_user_id);
CREATE INDEX idx_follows_followed ON social_follows(followed_user_id);
CREATE INDEX idx_follows_approved ON social_follows(is_approved);
CREATE INDEX idx_follows_created ON social_follows(created_at DESC);

COMMENT ON TABLE social_follows IS 'Follow relationships between users - Feature flag: follow_system';
COMMENT ON COLUMN social_follows.is_approved IS 'For private accounts - follow request must be approved';
COMMENT ON CONSTRAINT chk_no_self_follow ON social_follows IS 'Users cannot follow themselves';

-- =====================================================
-- 2. USER FOLLOW STATS (Denormalized Counters)
-- =====================================================

CREATE TABLE IF NOT EXISTS social_user_stats (
    user_id VARCHAR(36) PRIMARY KEY,

    -- Follow Counts
    followers_count INTEGER DEFAULT 0,
    following_count INTEGER DEFAULT 0,

    -- Post Stats
    posts_count INTEGER DEFAULT 0,
    total_likes_received INTEGER DEFAULT 0,
    total_comments_received INTEGER DEFAULT 0,

    -- Engagement Rate (%)
    engagement_rate NUMERIC(5,2) DEFAULT 0, -- (likes + comments) / followers * 100

    -- Timestamps
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_stats_followers ON social_user_stats(followers_count DESC);
CREATE INDEX idx_user_stats_engagement ON social_user_stats(engagement_rate DESC);

COMMENT ON TABLE social_user_stats IS 'Denormalized user statistics for performance (updated via triggers)';
COMMENT ON COLUMN social_user_stats.engagement_rate IS 'Engagement rate % for ranking/discovery';

-- =====================================================
-- 3. FOLLOW SUGGESTIONS (AI-Powered)
-- =====================================================

CREATE TABLE IF NOT EXISTS social_follow_suggestions (
    suggestion_id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id VARCHAR(36) NOT NULL, -- For whom suggestion is generated
    suggested_user_id VARCHAR(36) NOT NULL,

    -- Suggestion Reason
    reason VARCHAR(50) NOT NULL, -- 'similar_interests', 'mutual_followers', 'popular_creator', 'same_organization'
    confidence_score NUMERIC(3,2), -- 0.00 - 1.00

    -- Status
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'accepted', 'dismissed', 'expired'

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '7 days'),
    dismissed_at TIMESTAMP,

    CONSTRAINT uq_follow_suggestion UNIQUE(user_id, suggested_user_id),
    CONSTRAINT chk_suggestion_reason CHECK (reason IN (
        'similar_interests', 'mutual_followers', 'popular_creator',
        'same_organization', 'same_courses', 'ai_recommended'
    )),
    CONSTRAINT chk_suggestion_status CHECK (status IN (
        'pending', 'accepted', 'dismissed', 'expired'
    ))
);

CREATE INDEX idx_follow_suggestions_user ON social_follow_suggestions(user_id);
CREATE INDEX idx_follow_suggestions_suggested ON social_follow_suggestions(suggested_user_id);
CREATE INDEX idx_follow_suggestions_status ON social_follow_suggestions(status);
CREATE INDEX idx_follow_suggestions_expires ON social_follow_suggestions(expires_at);

COMMENT ON TABLE social_follow_suggestions IS 'AI-powered follow suggestions - Feature flag: follow_system';
COMMENT ON COLUMN social_follow_suggestions.confidence_score IS 'AI confidence score (0-1)';

-- =====================================================
-- 4. BLOCKED USERS (Privacy & Safety)
-- =====================================================

CREATE TABLE IF NOT EXISTS social_blocks (
    block_id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    blocker_user_id VARCHAR(36) NOT NULL, -- Who blocked
    blocked_user_id VARCHAR(36) NOT NULL, -- Who is blocked

    -- Reason
    reason VARCHAR(50), -- 'harassment', 'spam', 'inappropriate_content', 'other'
    notes TEXT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_block_relationship UNIQUE(blocker_user_id, blocked_user_id),
    CONSTRAINT chk_no_self_block CHECK (blocker_user_id != blocked_user_id),
    CONSTRAINT chk_block_reason CHECK (reason IN (
        'harassment', 'spam', 'inappropriate_content', 'other', NULL
    ))
);

CREATE INDEX idx_blocks_blocker ON social_blocks(blocker_user_id);
CREATE INDEX idx_blocks_blocked ON social_blocks(blocked_user_id);
CREATE INDEX idx_blocks_reason ON social_blocks(reason);

COMMENT ON TABLE social_blocks IS 'Blocked users (privacy & safety) - GDPR Art. 25 Privacy by Design';
COMMENT ON COLUMN social_blocks.reason IS 'Reason for blocking (optional, for Trust & Safety analytics)';

-- =====================================================
-- 5. MUTED USERS (Hide content without blocking)
-- =====================================================

CREATE TABLE IF NOT EXISTS social_mutes (
    mute_id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    muter_user_id VARCHAR(36) NOT NULL, -- Who muted
    muted_user_id VARCHAR(36) NOT NULL, -- Who is muted

    -- Duration
    muted_until TIMESTAMP, -- NULL = permanent

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_mute_relationship UNIQUE(muter_user_id, muted_user_id),
    CONSTRAINT chk_no_self_mute CHECK (muter_user_id != muted_user_id)
);

CREATE INDEX idx_mutes_muter ON social_mutes(muter_user_id);
CREATE INDEX idx_mutes_muted ON social_mutes(muted_user_id);
CREATE INDEX idx_mutes_until ON social_mutes(muted_until);

COMMENT ON TABLE social_mutes IS 'Muted users (hide content without blocking) - Less aggressive than blocking';
COMMENT ON COLUMN social_mutes.muted_until IS 'NULL = permanent mute, otherwise temporary';

-- =====================================================
-- 6. TRIGGERS - Update Follow Counts
-- =====================================================

-- Initialize user stats
CREATE OR REPLACE FUNCTION init_user_stats()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO social_user_stats (user_id)
    VALUES (NEW.follower_user_id), (NEW.followed_user_id)
    ON CONFLICT (user_id) DO NOTHING;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_follows_init_stats
    BEFORE INSERT ON social_follows
    FOR EACH ROW EXECUTE FUNCTION init_user_stats();

-- Update follower counts
CREATE OR REPLACE FUNCTION update_follow_counts()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' AND NEW.is_approved = TRUE THEN
        -- Increment follower count for followed user
        UPDATE social_user_stats
        SET followers_count = followers_count + 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = NEW.followed_user_id;

        -- Increment following count for follower
        UPDATE social_user_stats
        SET following_count = following_count + 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = NEW.follower_user_id;

    ELSIF TG_OP = 'DELETE' THEN
        -- Decrement counts
        UPDATE social_user_stats
        SET followers_count = GREATEST(followers_count - 1, 0),
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = OLD.followed_user_id;

        UPDATE social_user_stats
        SET following_count = GREATEST(following_count - 1, 0),
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = OLD.follower_user_id;

    ELSIF TG_OP = 'UPDATE' AND OLD.is_approved = FALSE AND NEW.is_approved = TRUE THEN
        -- Follow request approved - increment counts
        UPDATE social_user_stats
        SET followers_count = followers_count + 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = NEW.followed_user_id;

        UPDATE social_user_stats
        SET following_count = following_count + 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = NEW.follower_user_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_follows_update_counts
    AFTER INSERT OR DELETE OR UPDATE ON social_follows
    FOR EACH ROW EXECUTE FUNCTION update_follow_counts();

-- Auto-unfollow when blocked
CREATE OR REPLACE FUNCTION auto_unfollow_on_block()
RETURNS TRIGGER AS $$
BEGIN
    -- Delete any existing follow relationships
    DELETE FROM social_follows
    WHERE (follower_user_id = NEW.blocker_user_id AND followed_user_id = NEW.blocked_user_id)
       OR (follower_user_id = NEW.blocked_user_id AND followed_user_id = NEW.blocker_user_id);

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_blocks_auto_unfollow
    AFTER INSERT ON social_blocks
    FOR EACH ROW EXECUTE FUNCTION auto_unfollow_on_block();

COMMIT;

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Get top followed users
-- SELECT u.user_id, u.username, s.followers_count, s.posts_count, s.engagement_rate
-- FROM social_user_stats s
-- JOIN users u ON u.user_id = s.user_id
-- WHERE s.followers_count > 0
-- ORDER BY s.followers_count DESC
-- LIMIT 20;

-- Get follow suggestions for user
-- SELECT fs.suggested_user_id, fs.reason, fs.confidence_score
-- FROM social_follow_suggestions fs
-- WHERE fs.user_id = 'USER_ID'
--   AND fs.status = 'pending'
--   AND fs.expires_at > CURRENT_TIMESTAMP
-- ORDER BY fs.confidence_score DESC;

-- =====================================================
-- END MIGRATION 080
-- =====================================================
