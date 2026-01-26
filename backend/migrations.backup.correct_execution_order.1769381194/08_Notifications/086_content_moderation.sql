-- =====================================================
-- Migration 082: Content Moderation System (DSA Compliance)
-- =====================================================
-- Purpose: Content moderation, reporting, Trust & Safety
-- Compliance:
--   - DSA Art. 14 (User Reporting)
--   - DSA Art. 15 (Moderation Transparency)
--   - NetzDG § 3 (24h/7d Response Times)
--   - Child Safety (COPPA, Age-Appropriate Design Code)
--
-- Feature Flags:
--   - ai_moderation (ENABLED - always on)
--   - human_moderation (DISABLED)
--   - community_moderation (DISABLED)
--
-- Created: 2026-01-10
-- Author: Enterprise Migration
-- =====================================================

BEGIN;

-- =====================================================
-- 1. CONTENT REPORTS (User Reporting - DSA Art. 14)
-- =====================================================

CREATE TABLE IF NOT EXISTS content_reports (
    report_id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,

    -- What was reported
    reported_content_type VARCHAR(50) NOT NULL, -- 'post', 'comment', 'user', 'message'
    reported_content_id VARCHAR(36) NOT NULL,

    -- Who reported
    reporter_user_id VARCHAR(36), -- NULL if anonymous report
    reporter_ip_address INET,

    -- Report Details
    report_category VARCHAR(50) NOT NULL,
    report_reason TEXT NOT NULL, -- User-provided description
    additional_context JSONB, -- Screenshots, URLs, etc.

    -- Priority (Auto-calculated based on category)
    priority VARCHAR(20) DEFAULT 'medium', -- 'critical', 'high', 'medium', 'low'

    -- Status
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'reviewing', 'resolved', 'dismissed'
    resolution VARCHAR(20), -- 'content_removed', 'user_warned', 'user_banned', 'no_action'
    resolution_notes TEXT,

    -- Assignment
    assigned_moderator_id VARCHAR(36),
    assigned_at TIMESTAMP,

    -- Timestamps (DSA/NetzDG SLA Tracking)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP,
    resolved_at TIMESTAMP,

    -- SLA Status
    is_offensichtlich_rechtswidrig BOOLEAN DEFAULT FALSE, -- NetzDG: Offensichtlich illegal (24h SLA)
    sla_deadline TIMESTAMP, -- Auto-calculated: 24h or 7d

    CONSTRAINT chk_report_content_type CHECK (reported_content_type IN (
        'post', 'comment', 'user', 'message', 'profile', 'media'
    )),
    CONSTRAINT chk_report_category CHECK (report_category IN (
        -- DSA/NetzDG Categories
        'illegal_content', 'hate_speech', 'violence', 'terrorism',
        'child_abuse', 'harassment', 'bullying', 'spam',
        'misinformation', 'copyright_violation', 'privacy_violation',
        'self_harm', 'suicide', 'nudity', 'sexual_content',
        -- Platform Violations
        'fake_account', 'impersonation', 'scam', 'other'
    )),
    CONSTRAINT chk_report_priority CHECK (priority IN ('critical', 'high', 'medium', 'low')),
    CONSTRAINT chk_report_status CHECK (status IN (
        'pending', 'reviewing', 'escalated', 'resolved', 'dismissed'
    )),
    CONSTRAINT chk_report_resolution CHECK (resolution IN (
        'content_removed', 'content_hidden', 'user_warned', 'user_suspended',
        'user_banned', 'no_action', 'escalated_to_authorities', NULL
    ))
);

CREATE INDEX idx_reports_content ON content_reports(reported_content_type, reported_content_id);
CREATE INDEX idx_reports_reporter ON content_reports(reporter_user_id);
CREATE INDEX idx_reports_status ON content_reports(status);
CREATE INDEX idx_reports_priority ON content_reports(priority);
CREATE INDEX idx_reports_category ON content_reports(report_category);
CREATE INDEX idx_reports_assigned ON content_reports(assigned_moderator_id);
CREATE INDEX idx_reports_sla ON content_reports(sla_deadline) WHERE status = 'pending';
CREATE INDEX idx_reports_created ON content_reports(created_at DESC);

COMMENT ON TABLE content_reports IS 'User reports - DSA Art. 14 + NetzDG § 3';
COMMENT ON COLUMN content_reports.is_offensichtlich_rechtswidrig IS 'NetzDG: Obviously illegal content (24h SLA requirement)';
COMMENT ON COLUMN content_reports.sla_deadline IS 'SLA deadline: 24h for obviously illegal, 7d for complex';

-- =====================================================
-- 2. MODERATION ACTIONS (Transparency - DSA Art. 15)
-- =====================================================

CREATE TABLE IF NOT EXISTS moderation_actions (
    action_id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,

    -- What was moderated
    content_type VARCHAR(50) NOT NULL,
    content_id VARCHAR(36) NOT NULL,
    content_owner_id VARCHAR(36), -- User who created content

    -- Action Details
    action_type VARCHAR(50) NOT NULL,
    reason TEXT NOT NULL, -- Must be provided (DSA Transparency requirement)
    internal_notes TEXT, -- Private moderator notes

    -- Who took action
    moderator_type VARCHAR(20) DEFAULT 'ai', -- 'ai', 'human', 'automated_system'
    moderator_id VARCHAR(36), -- NULL if AI

    -- Related Report
    related_report_id VARCHAR(36) REFERENCES content_reports(report_id),

    -- User Notification
    user_notified BOOLEAN DEFAULT FALSE,
    notification_sent_at TIMESTAMP,

    -- Appeal
    is_appealable BOOLEAN DEFAULT TRUE,
    appeal_deadline TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_action_content_type CHECK (content_type IN (
        'post', 'comment', 'user', 'message', 'profile', 'media'
    )),
    CONSTRAINT chk_action_type CHECK (action_type IN (
        -- Content Actions
        'content_removed', 'content_hidden', 'content_flagged', 'content_age_restricted',
        -- User Actions
        'user_warned', 'user_suspended', 'user_banned', 'user_restricted',
        -- Other
        'appeal_granted', 'appeal_denied', 'no_action_taken'
    )),
    CONSTRAINT chk_moderator_type CHECK (moderator_type IN ('ai', 'human', 'automated_system'))
);

CREATE INDEX idx_actions_content ON moderation_actions(content_type, content_id);
CREATE INDEX idx_actions_owner ON moderation_actions(content_owner_id);
CREATE INDEX idx_actions_type ON moderation_actions(action_type);
CREATE INDEX idx_actions_moderator ON moderation_actions(moderator_type, moderator_id);
CREATE INDEX idx_actions_report ON moderation_actions(related_report_id);
-- Index for appealable actions (removed CURRENT_TIMESTAMP as it's not IMMUTABLE)
CREATE INDEX idx_actions_appealable ON moderation_actions(is_appealable, appeal_deadline)
    WHERE is_appealable = TRUE;
CREATE INDEX idx_actions_created ON moderation_actions(created_at DESC);

COMMENT ON TABLE moderation_actions IS 'Moderation actions log - DSA Art. 15 Transparency requirement';
COMMENT ON COLUMN moderation_actions.reason IS 'REQUIRED - User-facing reason for action (DSA compliance)';
COMMENT ON COLUMN moderation_actions.is_appealable IS 'DSA: Users have right to appeal moderation decisions';

-- =====================================================
-- 3. USER VIOLATIONS (Trust & Safety)
-- =====================================================

CREATE TABLE IF NOT EXISTS user_violations (
    violation_id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id VARCHAR(36) NOT NULL,

    -- Violation Details
    violation_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL, -- 'minor', 'moderate', 'severe', 'critical'

    -- Context
    related_content_type VARCHAR(50),
    related_content_id VARCHAR(36),
    related_report_id VARCHAR(36) REFERENCES content_reports(report_id),

    -- Action Taken
    action_taken VARCHAR(50),
    action_details TEXT,

    -- Points System (3 strikes = ban)
    violation_points INTEGER DEFAULT 1,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP, -- Violations may expire (e.g., after 90 days for minor ones)

    CONSTRAINT chk_violation_type CHECK (violation_type IN (
        'hate_speech', 'harassment', 'spam', 'illegal_content',
        'child_safety', 'violence', 'misinformation', 'copyright',
        'terms_of_service', 'community_guidelines', 'repeat_offender'
    )),
    CONSTRAINT chk_violation_severity CHECK (severity IN ('minor', 'moderate', 'severe', 'critical')),
    CONSTRAINT chk_violation_points CHECK (violation_points >= 0 AND violation_points <= 10)
);

CREATE INDEX idx_violations_user ON user_violations(user_id);
CREATE INDEX idx_violations_type ON user_violations(violation_type);
CREATE INDEX idx_violations_severity ON user_violations(severity);
CREATE INDEX idx_violations_created ON user_violations(created_at DESC);
-- Index for active violations (removed CURRENT_TIMESTAMP as it's not IMMUTABLE)
CREATE INDEX idx_violations_active ON user_violations(user_id, expires_at);

COMMENT ON TABLE user_violations IS 'User violations log - Trust & Safety 3-strike system';
COMMENT ON COLUMN user_violations.violation_points IS 'Points: 1-2 (minor), 3-5 (moderate), 6-8 (severe), 9-10 (critical)';
COMMENT ON COLUMN user_violations.expires_at IS 'Violations expire after 90d (minor), 180d (moderate), never (severe/critical)';

-- =====================================================
-- 4. AI MODERATION LOGS (Audit Trail)
-- =====================================================

CREATE TABLE IF NOT EXISTS ai_moderation_logs (
    log_id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,

    -- What was scanned
    content_type VARCHAR(50) NOT NULL,
    content_id VARCHAR(36) NOT NULL,
    content_preview TEXT, -- First 200 chars for reference

    -- AI Detection
    detection_type VARCHAR(50) NOT NULL, -- 'text_toxicity', 'image_nsfw', 'spam', 'hate_speech', etc.
    confidence_score NUMERIC(5,4), -- 0.0000 - 1.0000
    is_flagged BOOLEAN DEFAULT FALSE,

    -- AI Model Info
    model_name VARCHAR(100), -- e.g., 'openai-moderation', 'anthropic-claude', 'custom-hate-speech-v2'
    model_version VARCHAR(50),

    -- Decision
    auto_action_taken VARCHAR(50), -- 'approved', 'flagged_for_review', 'auto_removed'
    human_review_required BOOLEAN DEFAULT FALSE,

    -- Response Time (Performance Metrics)
    processing_time_ms INTEGER,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_ai_detection_type CHECK (detection_type IN (
        'text_toxicity', 'hate_speech', 'violence', 'sexual_content',
        'child_safety', 'spam', 'bot_detection', 'deepfake',
        'image_nsfw', 'image_violence', 'image_child_safety',
        'video_analysis', 'audio_analysis'
    )),
    CONSTRAINT chk_ai_auto_action CHECK (auto_action_taken IN (
        'approved', 'flagged_for_review', 'auto_removed', 'escalated'
    ))
);

CREATE INDEX idx_ai_logs_content ON ai_moderation_logs(content_type, content_id);
CREATE INDEX idx_ai_logs_detection ON ai_moderation_logs(detection_type);
CREATE INDEX idx_ai_logs_flagged ON ai_moderation_logs(is_flagged);
CREATE INDEX idx_ai_logs_review_required ON ai_moderation_logs(human_review_required)
    WHERE human_review_required = TRUE;
CREATE INDEX idx_ai_logs_created ON ai_moderation_logs(created_at DESC);

COMMENT ON TABLE ai_moderation_logs IS 'AI moderation audit log - DSA Art. 24 (Algorithm Transparency)';
COMMENT ON COLUMN ai_moderation_logs.confidence_score IS 'AI confidence: 0-1 (threshold usually 0.7-0.8)';
COMMENT ON COLUMN ai_moderation_logs.processing_time_ms IS 'Performance metric for AI response time';

-- =====================================================
-- 5. MODERATION QUEUE (Human Review)
-- =====================================================

CREATE TABLE IF NOT EXISTS moderation_queue (
    queue_id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,

    -- Content to review
    content_type VARCHAR(50) NOT NULL,
    content_id VARCHAR(36) NOT NULL,

    -- Source
    source VARCHAR(50) NOT NULL, -- 'user_report', 'ai_flagged', 'automated_filter', 'audit'
    related_report_id VARCHAR(36) REFERENCES content_reports(report_id),
    related_ai_log_id VARCHAR(36) REFERENCES ai_moderation_logs(log_id),

    -- Priority Queue
    priority VARCHAR(20) DEFAULT 'normal', -- 'urgent', 'high', 'normal', 'low'
    sla_deadline TIMESTAMP,

    -- Assignment
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'in_review', 'completed'
    assigned_moderator_id VARCHAR(36),
    assigned_at TIMESTAMP,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,

    CONSTRAINT chk_queue_source CHECK (source IN (
        'user_report', 'ai_flagged', 'automated_filter', 'audit', 'pattern_detection'
    )),
    CONSTRAINT chk_queue_priority CHECK (priority IN ('urgent', 'high', 'normal', 'low')),
    CONSTRAINT chk_queue_status CHECK (status IN ('pending', 'in_review', 'completed', 'escalated'))
);

CREATE INDEX idx_queue_status ON moderation_queue(status);
CREATE INDEX idx_queue_priority ON moderation_queue(priority, created_at);
CREATE INDEX idx_queue_assigned ON moderation_queue(assigned_moderator_id);
CREATE INDEX idx_queue_sla ON moderation_queue(sla_deadline) WHERE status != 'completed';
CREATE INDEX idx_queue_content ON moderation_queue(content_type, content_id);

COMMENT ON TABLE moderation_queue IS 'Human moderation queue - Feature flag: human_moderation';
COMMENT ON COLUMN moderation_queue.sla_deadline IS 'SLA deadline for review (24h urgent, 7d normal)';

-- =====================================================
-- 6. TRIGGERS - Auto-calculate SLA Deadlines
-- =====================================================

CREATE OR REPLACE FUNCTION calculate_report_sla()
RETURNS TRIGGER AS $$
BEGIN
    -- NetzDG: Offensichtlich rechtswidrig = 24h, Otherwise = 7d
    IF NEW.is_offensichtlich_rechtswidrig = TRUE OR NEW.priority = 'critical' THEN
        NEW.sla_deadline = NEW.created_at + INTERVAL '24 hours';
    ELSIF NEW.priority = 'high' THEN
        NEW.sla_deadline = NEW.created_at + INTERVAL '48 hours';
    ELSE
        NEW.sla_deadline = NEW.created_at + INTERVAL '7 days';
    END IF;

    -- Auto-set priority based on category
    IF NEW.report_category IN ('child_abuse', 'terrorism', 'violence') THEN
        NEW.priority = 'critical';
        NEW.is_offensichtlich_rechtswidrig = TRUE;
    ELSIF NEW.report_category IN ('hate_speech', 'harassment', 'illegal_content') THEN
        NEW.priority = 'high';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_reports_calculate_sla
    BEFORE INSERT ON content_reports
    FOR EACH ROW EXECUTE FUNCTION calculate_report_sla();

COMMIT;

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Get overdue reports (SLA breach)
-- SELECT report_id, report_category, priority, sla_deadline,
--        EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - sla_deadline))/3600 as hours_overdue
-- FROM content_reports
-- WHERE status IN ('pending', 'reviewing')
--   AND sla_deadline < CURRENT_TIMESTAMP
-- ORDER BY sla_deadline ASC;

-- Get AI moderation stats
-- SELECT detection_type, COUNT(*) as total,
--        SUM(CASE WHEN is_flagged THEN 1 ELSE 0 END) as flagged,
--        AVG(confidence_score) as avg_confidence,
--        AVG(processing_time_ms) as avg_processing_ms
-- FROM ai_moderation_logs
-- WHERE created_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'
-- GROUP BY detection_type;

-- =====================================================
-- END MIGRATION 082
-- =====================================================
