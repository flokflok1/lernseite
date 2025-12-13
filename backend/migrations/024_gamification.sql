-- ============================================================================
-- Migration: 024_gamification.sql
-- Description: Gamification system (XP, levels, leaderboards)
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-01-17
-- ============================================================================

-- ============================================================================
-- TABLE: user_xp
-- Description: User experience points and levels
-- ============================================================================
CREATE TABLE IF NOT EXISTS user_xp (
    xp_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE UNIQUE,
    total_xp INTEGER DEFAULT 0,
    current_level INTEGER DEFAULT 1,
    xp_to_next_level INTEGER DEFAULT 100,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_xp_user ON user_xp(user_id);
CREATE INDEX IF NOT EXISTS idx_user_xp_level ON user_xp(current_level DESC, total_xp DESC);

COMMENT ON TABLE user_xp IS 'User experience points and leveling system';

-- ============================================================================
-- TABLE: xp_transactions
-- Description: XP earning/spending history
-- ============================================================================
CREATE TABLE IF NOT EXISTS xp_transactions (
    transaction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    amount INTEGER NOT NULL,
    reason VARCHAR(255) NOT NULL,
    source_type VARCHAR(50),
    source_id VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_xp_transactions_user ON xp_transactions(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_xp_transactions_source ON xp_transactions(source_type, source_id);

COMMENT ON TABLE xp_transactions IS 'History of XP gains and expenditures';

-- ============================================================================
-- TABLE: leaderboards
-- Description: Leaderboard definitions
-- ============================================================================
CREATE TABLE IF NOT EXISTS leaderboards (
    leaderboard_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    leaderboard_type VARCHAR(50) NOT NULL,
    scope VARCHAR(50) DEFAULT 'global',
    organization_id UUID REFERENCES organizations(organization_id) ON DELETE CASCADE,
    time_period VARCHAR(20),
    metric VARCHAR(100) NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_leaderboard_type CHECK (leaderboard_type IN ('xp', 'courses_completed', 'streak', 'exam_score', 'ai_usage', 'custom')),
    CONSTRAINT chk_leaderboard_scope CHECK (scope IN ('global', 'organization', 'class', 'course')),
    CONSTRAINT chk_leaderboard_period CHECK (time_period IN ('daily', 'weekly', 'monthly', 'all_time', NULL))
);

CREATE INDEX IF NOT EXISTS idx_leaderboards_type ON leaderboards(leaderboard_type);
CREATE INDEX IF NOT EXISTS idx_leaderboards_scope ON leaderboards(scope, organization_id);
CREATE INDEX IF NOT EXISTS idx_leaderboards_active ON leaderboards(active) WHERE active = TRUE;

COMMENT ON TABLE leaderboards IS 'Leaderboard definitions for competitive learning';

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- ============================================================================
CREATE TRIGGER update_user_xp_updated_at BEFORE UPDATE ON user_xp
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- End of Migration: 024_gamification.sql
-- ============================================================================
