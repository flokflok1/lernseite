-- ============================================================================
-- Migration: 025_badges.sql
-- Description: Badges and achievements system
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-01-17
-- ============================================================================

-- ============================================================================
-- TABLE: badges
-- Description: Badge definitions
-- ============================================================================
CREATE TABLE IF NOT EXISTS badges (
    badge_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    icon_url VARCHAR(500),
    badge_type VARCHAR(50) NOT NULL,
    tier VARCHAR(20),
    points INTEGER DEFAULT 0,
    requirements JSONB NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_badge_type CHECK (badge_type IN ('achievement', 'milestone', 'special', 'seasonal', 'community')),
    CONSTRAINT chk_badge_tier CHECK (tier IN ('bronze', 'silver', 'gold', 'platinum', 'diamond', NULL))
);

CREATE INDEX IF NOT EXISTS idx_badges_type ON badges(badge_type);
CREATE INDEX IF NOT EXISTS idx_badges_tier ON badges(tier);
CREATE INDEX IF NOT EXISTS idx_badges_active ON badges(active) WHERE active = TRUE;

COMMENT ON TABLE badges IS 'Badge definitions for achievements and milestones';
COMMENT ON COLUMN badges.requirements IS 'JSONB criteria for earning badge';

-- ============================================================================
-- TABLE: user_badges
-- Description: Badges earned by users
-- ============================================================================
CREATE TABLE IF NOT EXISTS user_badges (
    user_badge_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    badge_id UUID REFERENCES badges(badge_id) ON DELETE CASCADE,
    earned_at TIMESTAMPTZ DEFAULT NOW(),
    progress JSONB,
    UNIQUE (user_id, badge_id)
);

CREATE INDEX IF NOT EXISTS idx_user_badges_user ON user_badges(user_id, earned_at DESC);
CREATE INDEX IF NOT EXISTS idx_user_badges_badge ON user_badges(badge_id);

COMMENT ON TABLE user_badges IS 'Badges earned by users';

-- ============================================================================
-- End of Migration: 025_badges.sql
-- ============================================================================
