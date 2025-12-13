-- ============================================================================
-- Migration 067: Feedback System
-- ============================================================================
-- User feedback with AI-powered summarization for admin dashboard
--
-- Features:
-- - Feedback collection (questions, bugs, suggestions, praise)
-- - AI summarization of feedback batches
-- - Context tracking (course, lesson, page)
-- - Anonymous feedback support
-- - Admin dashboard integration
-- ============================================================================

-- ============================================================================
-- 1. FEEDBACK TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_feedback (
    feedback_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- User (optional for anonymous)
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    is_anonymous BOOLEAN DEFAULT FALSE,
    email VARCHAR(255),

    -- Feedback content
    feedback_type VARCHAR(20) NOT NULL CHECK (feedback_type IN ('question', 'bug', 'suggestion', 'praise', 'other')),
    title VARCHAR(255),
    message TEXT NOT NULL,

    -- Context
    context_course_id UUID REFERENCES courses(course_id) ON DELETE SET NULL,
    context_lesson_id UUID,  -- No FK because lessons might be deleted
    context_page VARCHAR(100),
    context_url TEXT,
    context_user_agent TEXT,
    context_data JSONB DEFAULT '{}',

    -- Status tracking
    status VARCHAR(20) DEFAULT 'new' CHECK (status IN ('new', 'read', 'in_progress', 'resolved', 'closed')),
    priority VARCHAR(10) DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    assigned_to UUID REFERENCES users(user_id) ON DELETE SET NULL,

    -- AI Processing
    ai_summary TEXT,
    ai_category VARCHAR(50),
    ai_sentiment VARCHAR(20) CHECK (ai_sentiment IN ('positive', 'neutral', 'negative', 'mixed')),
    ai_tags TEXT[],
    ai_processed_at TIMESTAMPTZ,

    -- Admin response
    admin_response TEXT,
    admin_responded_by UUID REFERENCES users(user_id) ON DELETE SET NULL,
    admin_responded_at TIMESTAMPTZ,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);

-- ============================================================================
-- 2. FEEDBACK SUMMARY BATCHES (for periodic AI summaries)
-- ============================================================================

CREATE TABLE IF NOT EXISTS feedback_summary_batches (
    batch_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Time period
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,

    -- Stats
    total_feedbacks INTEGER DEFAULT 0,
    questions_count INTEGER DEFAULT 0,
    bugs_count INTEGER DEFAULT 0,
    suggestions_count INTEGER DEFAULT 0,
    praise_count INTEGER DEFAULT 0,
    other_count INTEGER DEFAULT 0,

    -- AI Summary
    ai_executive_summary TEXT,
    ai_key_themes JSONB DEFAULT '[]',  -- [{theme, count, examples}]
    ai_action_items JSONB DEFAULT '[]', -- [{priority, action, related_feedbacks}]
    ai_sentiment_breakdown JSONB DEFAULT '{}', -- {positive: n, neutral: n, negative: n}
    ai_top_courses JSONB DEFAULT '[]',  -- [{course_id, course_name, feedback_count}]

    -- Processing
    processed_at TIMESTAMPTZ,
    processing_tokens INTEGER DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 3. FEEDBACK ATTACHMENTS
-- ============================================================================

CREATE TABLE IF NOT EXISTS feedback_attachments (
    attachment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    feedback_id UUID NOT NULL REFERENCES user_feedback(feedback_id) ON DELETE CASCADE,

    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(100),
    file_size INTEGER,
    file_path TEXT NOT NULL,

    -- Screenshot detection
    is_screenshot BOOLEAN DEFAULT FALSE,
    ai_screenshot_description TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 4. FEEDBACK NOTES (internal team notes)
-- ============================================================================

CREATE TABLE IF NOT EXISTS feedback_notes (
    note_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    feedback_id UUID NOT NULL REFERENCES user_feedback(feedback_id) ON DELETE CASCADE,

    author_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    note_text TEXT NOT NULL,
    is_internal BOOLEAN DEFAULT TRUE,  -- Not shown to user

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 5. INDEXES
-- ============================================================================

-- Main queries
CREATE INDEX IF NOT EXISTS idx_user_feedback_type ON user_feedback(feedback_type);
CREATE INDEX IF NOT EXISTS idx_user_feedback_status ON user_feedback(status);
CREATE INDEX IF NOT EXISTS idx_user_feedback_created ON user_feedback(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_user_feedback_user ON user_feedback(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_user_feedback_course ON user_feedback(context_course_id) WHERE context_course_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_user_feedback_priority ON user_feedback(priority, status);

-- Full text search on feedback
CREATE INDEX IF NOT EXISTS idx_user_feedback_search ON user_feedback
    USING gin(to_tsvector('german', coalesce(title, '') || ' ' || message));

-- Attachments
CREATE INDEX IF NOT EXISTS idx_feedback_attachments_feedback ON feedback_attachments(feedback_id);

-- Notes
CREATE INDEX IF NOT EXISTS idx_feedback_notes_feedback ON feedback_notes(feedback_id);

-- Summary batches
CREATE INDEX IF NOT EXISTS idx_feedback_summary_period ON feedback_summary_batches(period_start, period_end);

-- ============================================================================
-- 6. VIEWS
-- ============================================================================

-- Admin dashboard view with stats
CREATE OR REPLACE VIEW v_feedback_dashboard AS
SELECT
    -- Overall stats
    COUNT(*) AS total_feedbacks,
    COUNT(*) FILTER (WHERE status = 'new') AS new_count,
    COUNT(*) FILTER (WHERE status = 'in_progress') AS in_progress_count,
    COUNT(*) FILTER (WHERE status = 'resolved') AS resolved_count,

    -- By type
    COUNT(*) FILTER (WHERE feedback_type = 'question') AS questions,
    COUNT(*) FILTER (WHERE feedback_type = 'bug') AS bugs,
    COUNT(*) FILTER (WHERE feedback_type = 'suggestion') AS suggestions,
    COUNT(*) FILTER (WHERE feedback_type = 'praise') AS praise,

    -- By priority
    COUNT(*) FILTER (WHERE priority = 'urgent') AS urgent_count,
    COUNT(*) FILTER (WHERE priority = 'high') AS high_priority_count,

    -- Time stats
    COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '24 hours') AS last_24h,
    COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '7 days') AS last_7d,
    COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '30 days') AS last_30d,

    -- Sentiment
    COUNT(*) FILTER (WHERE ai_sentiment = 'positive') AS positive_sentiment,
    COUNT(*) FILTER (WHERE ai_sentiment = 'negative') AS negative_sentiment,

    -- Response rate
    ROUND(
        COUNT(*) FILTER (WHERE admin_response IS NOT NULL)::NUMERIC /
        NULLIF(COUNT(*), 0) * 100, 2
    ) AS response_rate_percent,

    -- Avg resolution time (hours)
    ROUND(
        AVG(EXTRACT(EPOCH FROM (resolved_at - created_at)) / 3600)
        FILTER (WHERE resolved_at IS NOT NULL), 2
    ) AS avg_resolution_hours
FROM user_feedback;

-- ============================================================================
-- 7. FUNCTIONS
-- ============================================================================

-- Auto-update timestamp
CREATE OR REPLACE FUNCTION update_feedback_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trg_feedback_updated
    BEFORE UPDATE ON user_feedback
    FOR EACH ROW
    EXECUTE FUNCTION update_feedback_timestamp();

-- Auto-set resolved_at when status changes to resolved
CREATE OR REPLACE FUNCTION set_feedback_resolved_at()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'resolved' AND OLD.status != 'resolved' THEN
        NEW.resolved_at = NOW();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trg_feedback_resolved
    BEFORE UPDATE ON user_feedback
    FOR EACH ROW
    EXECUTE FUNCTION set_feedback_resolved_at();

-- ============================================================================
-- 8. INITIAL DATA
-- ============================================================================

-- Nothing to seed initially

-- ============================================================================
-- Migration complete
-- ============================================================================
COMMENT ON TABLE user_feedback IS 'User feedback with AI-powered summarization - Migration 067';
