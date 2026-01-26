-- ============================================================================
-- Migration: 096_social_posts.sql
-- Description: Social Posts System - Instagram-like posts for users
--              Feature Flag: user_posts (DISABLED by default)
--              Compliance: DSA Art. 14 (content management), GDPR Art. 5
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-01-16
-- ============================================================================
-- Previous number: 079 (12_Social) → Renumbered to 096 to resolve duplicates
-- Phase: Social Network Layer - Posts
--
-- Tables created:
-- - social_posts (main posts table)
-- - social_post_media (media attachments)
-- - social_post_mentions (@ mentions)
-- - social_post_visibility (privacy controls)
-- ============================================================================

BEGIN;

-- =====================================================
-- 1. SOCIAL POSTS (Main Table)
-- =====================================================

CREATE TABLE IF NOT EXISTS social_posts (
    post_id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id VARCHAR(36) NOT NULL,

    -- Content
    content TEXT, -- Post text (max 5000 chars enforced in app)
    content_type VARCHAR(50) NOT NULL DEFAULT 'text', -- 'text', 'media', 'course_portfolio', 'achievement'

    -- Metadata
    language_code VARCHAR(10) DEFAULT 'de', -- Detected language (for moderation)
    is_edited BOOLEAN DEFAULT FALSE,
    edited_at TIMESTAMP,

    -- Visibility & Privacy
    visibility VARCHAR(20) DEFAULT 'public', -- 'public', 'followers', 'private', 'unlisted'
    is_pinned BOOLEAN DEFAULT FALSE, -- Pin to profile top

    -- Moderation
    moderation_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'approved', 'rejected', 'flagged'
    moderated_by VARCHAR(36), -- AI or moderator user_id
    moderated_at TIMESTAMP,

    -- Engagement Counters (Denormalized for Performance)
    likes_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    shares_count INTEGER DEFAULT 0,
    views_count INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP, -- Soft delete

    CONSTRAINT chk_post_content_type CHECK (content_type IN (
        'text', 'media', 'course_portfolio', 'achievement', 'poll'
    )),
    CONSTRAINT chk_post_visibility CHECK (visibility IN (
        'public', 'followers', 'private', 'unlisted'
    )),
    CONSTRAINT chk_post_moderation_status CHECK (moderation_status IN (
        'pending', 'approved', 'rejected', 'flagged', 'ai_approved'
    ))
);

CREATE INDEX idx_social_posts_user ON social_posts(user_id);
CREATE INDEX idx_social_posts_created ON social_posts(created_at DESC);
CREATE INDEX idx_social_posts_visibility ON social_posts(visibility);
CREATE INDEX idx_social_posts_moderation ON social_posts(moderation_status);
CREATE INDEX idx_social_posts_deleted ON social_posts(deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_social_posts_pinned ON social_posts(user_id, is_pinned) WHERE is_pinned = TRUE;

COMMENT ON TABLE social_posts IS 'Social posts system (Instagram-like) - Feature flag: user_posts';
COMMENT ON COLUMN social_posts.content_type IS 'Type of post: text, media, course_portfolio, achievement';
COMMENT ON COLUMN social_posts.moderation_status IS 'DSA-compliant moderation status (AI pre-screening)';
COMMENT ON COLUMN social_posts.likes_count IS 'Denormalized counter for performance (updated via triggers)';

-- =====================================================
-- 2. POST MEDIA (Images, Videos, Audio)
-- =====================================================

CREATE TABLE IF NOT EXISTS social_post_media (
    media_id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    post_id VARCHAR(36) NOT NULL REFERENCES social_posts(post_id) ON DELETE CASCADE,

    -- Media Info
    media_type VARCHAR(20) NOT NULL, -- 'image', 'video', 'audio', 'document'
    media_url TEXT NOT NULL,
    thumbnail_url TEXT,

    -- Metadata
    file_size BIGINT, -- in bytes
    mime_type VARCHAR(100),
    width INTEGER,
    height INTEGER,
    duration INTEGER, -- for video/audio in seconds

    -- Alt Text (Accessibility + SEO)
    alt_text TEXT,

    -- Display Order
    display_order INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_media_type CHECK (media_type IN (
        'image', 'video', 'audio', 'document'
    ))
);

CREATE INDEX idx_post_media_post ON social_post_media(post_id);
CREATE INDEX idx_post_media_type ON social_post_media(media_type);
CREATE INDEX idx_post_media_order ON social_post_media(post_id, display_order);

COMMENT ON TABLE social_post_media IS 'Media attachments for social posts (max 10 per post enforced in app)';
COMMENT ON COLUMN social_post_media.alt_text IS 'Accessibility alt text (required for images)';

-- =====================================================
-- 3. POST MENTIONS (@username)
-- =====================================================

CREATE TABLE IF NOT EXISTS social_post_mentions (
    mention_id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    post_id VARCHAR(36) NOT NULL REFERENCES social_posts(post_id) ON DELETE CASCADE,
    mentioned_user_id VARCHAR(36) NOT NULL,

    -- Notification
    notification_sent BOOLEAN DEFAULT FALSE,
    notification_sent_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_post_mention UNIQUE(post_id, mentioned_user_id)
);

CREATE INDEX idx_post_mentions_post ON social_post_mentions(post_id);
CREATE INDEX idx_post_mentions_user ON social_post_mentions(mentioned_user_id);
CREATE INDEX idx_post_mentions_notified ON social_post_mentions(notification_sent);

COMMENT ON TABLE social_post_mentions IS '@mentions in posts - Feature flag: mentions';
COMMENT ON COLUMN social_post_mentions.notification_sent IS 'Real-time notification sent to mentioned user';

-- =====================================================
-- 4. POST HASHTAGS (#tag)
-- =====================================================

CREATE TABLE IF NOT EXISTS social_post_hashtags (
    post_id VARCHAR(36) NOT NULL REFERENCES social_posts(post_id) ON DELETE CASCADE,
    hashtag VARCHAR(100) NOT NULL, -- lowercase, no #

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (post_id, hashtag)
);

CREATE INDEX idx_post_hashtags_tag ON social_post_hashtags(hashtag);
CREATE INDEX idx_post_hashtags_created ON social_post_hashtags(created_at DESC);

COMMENT ON TABLE social_post_hashtags IS 'Hashtags in posts - Feature flag: hashtags';
COMMENT ON COLUMN social_post_hashtags.hashtag IS 'Hashtag without # symbol (lowercase)';

-- =====================================================
-- 5. HASHTAG STATISTICS (Trending)
-- =====================================================

CREATE TABLE IF NOT EXISTS hashtag_stats (
    hashtag VARCHAR(100) PRIMARY KEY,

    -- Counters
    usage_count INTEGER DEFAULT 0,
    usage_count_24h INTEGER DEFAULT 0,
    usage_count_7d INTEGER DEFAULT 0,

    -- Trending
    trending_score NUMERIC(10,2) DEFAULT 0, -- Algorithm score
    is_trending BOOLEAN DEFAULT FALSE,

    -- Timestamps
    first_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_hashtag_stats_trending ON hashtag_stats(trending_score DESC) WHERE is_trending = TRUE;
CREATE INDEX idx_hashtag_stats_usage ON hashtag_stats(usage_count DESC);
CREATE INDEX idx_hashtag_stats_24h ON hashtag_stats(usage_count_24h DESC);

COMMENT ON TABLE hashtag_stats IS 'Hashtag usage statistics for trending discovery - Feature flag: trending_discovery';
COMMENT ON COLUMN hashtag_stats.trending_score IS 'Trending algorithm score (velocity + engagement)';

-- =====================================================
-- 6. POST VISIBILITY SETTINGS (Privacy)
-- =====================================================

CREATE TABLE IF NOT EXISTS social_post_visibility_settings (
    user_id VARCHAR(36) PRIMARY KEY,

    -- Default Visibility
    default_visibility VARCHAR(20) DEFAULT 'public',

    -- Privacy Controls
    allow_mentions BOOLEAN DEFAULT TRUE,
    allow_shares BOOLEAN DEFAULT TRUE,
    allow_comments BOOLEAN DEFAULT TRUE,

    -- Child Safety (COPPA)
    is_minor BOOLEAN DEFAULT FALSE, -- Under 13 (auto-detected)
    parental_consent_required BOOLEAN DEFAULT FALSE,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_default_visibility CHECK (default_visibility IN (
        'public', 'followers', 'private', 'unlisted'
    ))
);

CREATE INDEX idx_post_visibility_minor ON social_post_visibility_settings(is_minor) WHERE is_minor = TRUE;

COMMENT ON TABLE social_post_visibility_settings IS 'User privacy settings for posts (GDPR Art. 25 - Privacy by Design)';
COMMENT ON COLUMN social_post_visibility_settings.is_minor IS 'COPPA compliance - Users under 13 (auto-detected from birthdate)';

-- =====================================================
-- 7. TRIGGERS
-- =====================================================

-- Updated At Trigger
CREATE OR REPLACE FUNCTION update_social_post_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    IF (TG_OP = 'UPDATE' AND OLD.content IS DISTINCT FROM NEW.content) THEN
        NEW.is_edited = TRUE;
        NEW.edited_at = CURRENT_TIMESTAMP;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_social_posts_updated_at
    BEFORE UPDATE ON social_posts
    FOR EACH ROW EXECUTE FUNCTION update_social_post_updated_at();

-- Hashtag Stats Update Trigger
CREATE OR REPLACE FUNCTION update_hashtag_stats()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO hashtag_stats (hashtag, usage_count, usage_count_24h, usage_count_7d, last_used_at)
    VALUES (NEW.hashtag, 1, 1, 1, CURRENT_TIMESTAMP)
    ON CONFLICT (hashtag) DO UPDATE SET
        usage_count = hashtag_stats.usage_count + 1,
        usage_count_24h = hashtag_stats.usage_count_24h + 1,
        usage_count_7d = hashtag_stats.usage_count_7d + 1,
        last_used_at = CURRENT_TIMESTAMP,
        updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_post_hashtags_stats
    AFTER INSERT ON social_post_hashtags
    FOR EACH ROW EXECUTE FUNCTION update_hashtag_stats();

COMMIT;

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Count posts by type
-- SELECT content_type, COUNT(*), SUM(likes_count) as total_likes
-- FROM social_posts
-- WHERE deleted_at IS NULL
-- GROUP BY content_type;

-- Show trending hashtags
-- SELECT hashtag, usage_count_24h, trending_score
-- FROM hashtag_stats
-- WHERE is_trending = TRUE
-- ORDER BY trending_score DESC
-- LIMIT 10;

-- =====================================================
-- END MIGRATION 079
-- =====================================================
