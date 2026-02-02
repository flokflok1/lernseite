-- =====================================================
-- Migration 083: Child Safety System (COPPA + Age-Appropriate Design Code)
-- =====================================================
-- Purpose: Child protection, age verification, parental controls
-- Compliance:
--   - COPPA (USA - Children under 13)
--   - UK Age-Appropriate Design Code
--   - GDPR Art. 8 (Children's Consent)
--   - DSA Child Safety Requirements
--
-- Feature Flag: child_safety_strict (ENABLED - always on)
--
-- Created: 2026-01-10
-- Author: Enterprise Migration
-- =====================================================

BEGIN;

-- =====================================================
-- 1. AGE VERIFICATIONS (COPPA Compliance)
-- =====================================================

CREATE TABLE IF NOT EXISTS compliance.age_verifications (
    verification_id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id VARCHAR(36) NOT NULL UNIQUE,

    -- Age Information
    date_of_birth DATE NOT NULL,
    age_at_verification INTEGER, -- Age when verified
    -- Note: is_minor and is_coppa_protected are computed in application code
    -- (age() function is not IMMUTABLE, can't use GENERATED ALWAYS AS)
    is_minor BOOLEAN,
    is_coppa_protected BOOLEAN, -- USA: Under 13 requires parental consent

    -- Verification Method
    verification_method VARCHAR(50) NOT NULL, -- 'self_declaration', 'id_document', 'credit_card', 'parental_consent'
    verification_status VARCHAR(20) DEFAULT 'pending',

    -- Document Upload (if ID verification)
    document_type VARCHAR(50), -- 'passport', 'id_card', 'drivers_license'
    document_url TEXT, -- Encrypted storage URL
    document_verified_at TIMESTAMP,

    -- Parental Consent (COPPA)
    parental_consent_given BOOLEAN DEFAULT FALSE,
    parental_email VARCHAR(255),
    parental_consent_date TIMESTAMP,
    parental_consent_ip INET,

    -- Re-verification (Every 90 days for minors)
    last_verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    next_verification_due TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_age_verification_method CHECK (verification_method IN (
        'self_declaration', 'id_document', 'credit_card',
        'parental_consent', 'government_database', 'third_party_service'
    )),
    CONSTRAINT chk_age_verification_status CHECK (verification_status IN (
        'pending', 'verified', 'rejected', 'expired', 'needs_revalidation'
    )),
    -- Note: Can't use CURRENT_DATE in CHECK constraint (not IMMUTABLE)
    -- Validation should be done in application code
    CONSTRAINT chk_age_verification_dob CHECK (
        date_of_birth >= '1900-01-01' AND date_of_birth <= '2100-01-01'
    )
);

CREATE INDEX idx_age_verif_user ON compliance.age_verifications(user_id);
CREATE INDEX idx_age_verif_status ON compliance.age_verifications(verification_status);
CREATE INDEX idx_age_verif_minor ON compliance.age_verifications(is_minor) WHERE is_minor = TRUE;
CREATE INDEX idx_age_verif_coppa ON compliance.age_verifications(is_coppa_protected) WHERE is_coppa_protected = TRUE;
-- Index for revalidation due dates (removed CURRENT_TIMESTAMP as it's not IMMUTABLE)
CREATE INDEX idx_age_verif_revalidation ON compliance.age_verifications(next_verification_due, verification_status)
    WHERE verification_status = 'verified';

COMMENT ON TABLE compliance.age_verifications IS 'Age verification system - COPPA & UK Age-Appropriate Design Code';
COMMENT ON COLUMN compliance.age_verifications.is_coppa_protected IS 'COPPA: Children under 13 (USA) - requires parental consent';
COMMENT ON COLUMN compliance.age_verifications.parental_consent_given IS 'COPPA: Verifiable parental consent required';

-- =====================================================
-- 2. PARENTAL CONTROLS (COPPA + UK Code)
-- =====================================================

CREATE TABLE IF NOT EXISTS compliance.parental_controls (
    control_id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    child_user_id VARCHAR(36) NOT NULL UNIQUE,
    parent_user_id VARCHAR(36), -- NULL if parent not a platform user

    -- Parent Contact
    parent_email VARCHAR(255) NOT NULL,
    parent_phone VARCHAR(50),
    parent_verified BOOLEAN DEFAULT FALSE,
    parent_verified_at TIMESTAMP,

    -- Controls Configuration
    allow_social_features BOOLEAN DEFAULT FALSE, -- Posts, comments, follows
    allow_direct_messages BOOLEAN DEFAULT FALSE,
    allow_public_profile BOOLEAN DEFAULT FALSE,
    allow_location_sharing BOOLEAN DEFAULT FALSE,
    allow_third_party_integrations BOOLEAN DEFAULT FALSE,

    -- Content Filtering
    content_filter_level VARCHAR(20) DEFAULT 'strict', -- 'strict', 'moderate', 'off'
    age_rating_limit VARCHAR(10) DEFAULT 'U', -- 'U' (Universal), 'PG', '12', '15', '18'

    -- Screen Time Limits
    daily_time_limit_minutes INTEGER DEFAULT 120, -- 2 hours default
    time_limit_enabled BOOLEAN DEFAULT TRUE,
    quiet_hours_start TIME, -- e.g., '22:00'
    quiet_hours_end TIME, -- e.g., '07:00'

    -- Approval Requirements
    require_content_approval BOOLEAN DEFAULT TRUE, -- Parent must approve posts
    require_follow_approval BOOLEAN DEFAULT TRUE,
    require_purchase_approval BOOLEAN DEFAULT TRUE,

    -- Activity Monitoring
    send_activity_reports BOOLEAN DEFAULT TRUE,
    report_frequency VARCHAR(20) DEFAULT 'weekly', -- 'daily', 'weekly', 'monthly'

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_parent_content_filter CHECK (content_filter_level IN ('strict', 'moderate', 'off')),
    CONSTRAINT chk_parent_age_rating CHECK (age_rating_limit IN ('U', 'PG', '12', '15', '18')),
    CONSTRAINT chk_parent_report_freq CHECK (report_frequency IN ('daily', 'weekly', 'monthly'))
);

CREATE INDEX idx_parental_child ON compliance.parental_controls(child_user_id);
CREATE INDEX idx_parental_parent ON compliance.parental_controls(parent_user_id);
CREATE INDEX idx_parental_verified ON compliance.parental_controls(parent_verified);

COMMENT ON TABLE compliance.parental_controls IS 'Parental control settings - COPPA & UK Age-Appropriate Design Code';
COMMENT ON COLUMN compliance.parental_controls.allow_social_features IS 'COPPA: Social features disabled by default for under 13';
COMMENT ON COLUMN compliance.parental_controls.require_content_approval IS 'UK Code: Parent must approve child content';

-- =====================================================
-- 3. CHILD ACTIVITY LOG (Parent Monitoring)
-- =====================================================

CREATE TABLE IF NOT EXISTS compliance.child_activity_log (
    activity_id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    child_user_id VARCHAR(36) NOT NULL,

    -- Activity Details
    activity_type VARCHAR(50) NOT NULL,
    activity_description TEXT,
    activity_metadata JSONB,

    -- Parental Visibility
    visible_to_parent BOOLEAN DEFAULT TRUE,
    requires_parent_approval BOOLEAN DEFAULT FALSE,
    parent_approved BOOLEAN,
    parent_approved_at TIMESTAMP,
    parent_approval_notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_child_activity_type CHECK (activity_type IN (
        'post_created', 'comment_posted', 'follow_request', 'message_sent',
        'content_purchased', 'profile_updated', 'friend_request', 'location_shared'
    ))
);

CREATE INDEX idx_child_activity_child ON compliance.child_activity_log(child_user_id);
CREATE INDEX idx_child_activity_type ON compliance.child_activity_log(activity_type);
CREATE INDEX idx_child_activity_approval ON compliance.child_activity_log(requires_parent_approval, parent_approved)
    WHERE requires_parent_approval = TRUE;
CREATE INDEX idx_child_activity_created ON compliance.child_activity_log(created_at DESC);

COMMENT ON TABLE compliance.child_activity_log IS 'Child activity log for parent monitoring (privacy-protected)';
COMMENT ON COLUMN compliance.child_activity_log.visible_to_parent IS 'Some activities may be private (e.g., support messages)';

-- =====================================================
-- 4. SCREEN TIME TRACKING (UK Code)
-- =====================================================

CREATE TABLE IF NOT EXISTS compliance.screen_time_sessions (
    session_id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id VARCHAR(36) NOT NULL,

    -- Session Info
    session_start TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    session_end TIMESTAMP,
    duration_minutes INTEGER,

    -- Context
    device_type VARCHAR(50), -- 'mobile', 'desktop', 'tablet'
    user_agent TEXT,

    -- Daily Summary
    session_date DATE NOT NULL DEFAULT CURRENT_DATE,

    CONSTRAINT chk_screen_time_duration CHECK (duration_minutes >= 0 AND duration_minutes <= 1440) -- Max 24h
);

CREATE INDEX idx_screen_time_user ON compliance.screen_time_sessions(user_id);
CREATE INDEX idx_screen_time_date ON compliance.screen_time_sessions(user_id, session_date);
CREATE INDEX idx_screen_time_active ON compliance.screen_time_sessions(user_id, session_end) WHERE session_end IS NULL;

COMMENT ON TABLE compliance.screen_time_sessions IS 'Screen time tracking - UK Age-Appropriate Design Code';
COMMENT ON COLUMN compliance.screen_time_sessions.duration_minutes IS 'Session duration (auto-calculated on session_end)';

-- =====================================================
-- 5. DAILY SCREEN TIME SUMMARY
-- =====================================================

CREATE TABLE IF NOT EXISTS compliance.daily_screen_time (
    summary_id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id VARCHAR(36) NOT NULL,
    summary_date DATE NOT NULL,

    -- Totals
    total_minutes INTEGER DEFAULT 0,
    session_count INTEGER DEFAULT 0,

    -- Limits
    daily_limit_minutes INTEGER,
    limit_exceeded BOOLEAN DEFAULT FALSE,
    limit_exceeded_at TIMESTAMP,

    -- Warnings Sent
    warning_75_percent_sent BOOLEAN DEFAULT FALSE,
    warning_100_percent_sent BOOLEAN DEFAULT FALSE,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_user_screen_time_date UNIQUE(user_id, summary_date)
);

CREATE INDEX idx_daily_screen_user ON compliance.daily_screen_time(user_id);
CREATE INDEX idx_daily_screen_date ON compliance.daily_screen_time(summary_date DESC);
CREATE INDEX idx_daily_screen_exceeded ON compliance.daily_screen_time(limit_exceeded) WHERE limit_exceeded = TRUE;

COMMENT ON TABLE compliance.daily_screen_time IS 'Daily screen time summary with limits (UK Code)';

-- =====================================================
-- 6. GROOMING DETECTION LOGS (AI-Powered Safety)
-- =====================================================

CREATE TABLE IF NOT EXISTS compliance.grooming_detection_logs (
    detection_id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,

    -- Who is involved
    potential_groomer_id VARCHAR(36) NOT NULL, -- Adult user
    potential_victim_id VARCHAR(36) NOT NULL, -- Minor user

    -- Detection Details
    detection_type VARCHAR(50) NOT NULL,
    confidence_score NUMERIC(5,4), -- 0.0000 - 1.0000
    risk_level VARCHAR(20) NOT NULL, -- 'low', 'medium', 'high', 'critical'

    -- Evidence
    message_content_hash TEXT, -- Hashed content (privacy-protected)
    pattern_matched VARCHAR(100), -- Which grooming pattern was detected
    context_metadata JSONB, -- Age gap, conversation history, etc.

    -- Action Taken
    action_taken VARCHAR(50),
    human_review_required BOOLEAN DEFAULT TRUE,
    escalated_to_authorities BOOLEAN DEFAULT FALSE,
    authorities_notified_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_grooming_detection_type CHECK (detection_type IN (
        'age_gap_suspicious', 'sexual_solicitation', 'gift_offering',
        'isolation_attempt', 'secret_keeping', 'trust_building_manipulation',
        'photo_request', 'location_request', 'offline_meeting_request'
    )),
    CONSTRAINT chk_grooming_risk_level CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
    CONSTRAINT chk_grooming_action CHECK (action_taken IN (
        'flagged_for_review', 'message_blocked', 'user_warned',
        'user_suspended', 'contact_blocked', 'authorities_notified', NULL
    ))
);

CREATE INDEX idx_grooming_groomer ON compliance.grooming_detection_logs(potential_groomer_id);
CREATE INDEX idx_grooming_victim ON compliance.grooming_detection_logs(potential_victim_id);
CREATE INDEX idx_grooming_risk ON compliance.grooming_detection_logs(risk_level);
CREATE INDEX idx_grooming_review ON compliance.grooming_detection_logs(human_review_required)
    WHERE human_review_required = TRUE;
CREATE INDEX idx_grooming_created ON compliance.grooming_detection_logs(created_at DESC);

COMMENT ON TABLE compliance.grooming_detection_logs IS 'AI-powered grooming detection (child safety critical)';
COMMENT ON COLUMN compliance.grooming_detection_logs.confidence_score IS 'AI confidence (threshold: 0.7 for flagging)';
COMMENT ON COLUMN compliance.grooming_detection_logs.escalated_to_authorities IS 'Legal requirement to report suspected child abuse';

-- =====================================================
-- 7. TRIGGERS
-- =====================================================

-- Auto-calculate age at verification
CREATE OR REPLACE FUNCTION calculate_age_at_verification()
RETURNS TRIGGER AS $$
BEGIN
    NEW.age_at_verification = EXTRACT(YEAR FROM age(NEW.date_of_birth));

    -- Set next verification due (90 days for minors)
    IF NEW.age_at_verification < 18 THEN
        NEW.next_verification_due = CURRENT_TIMESTAMP + INTERVAL '90 days';
    ELSE
        NEW.next_verification_due = CURRENT_TIMESTAMP + INTERVAL '365 days';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_age_verification_calculate
    BEFORE INSERT OR UPDATE ON compliance.age_verifications
    FOR EACH ROW EXECUTE FUNCTION calculate_age_at_verification();

-- Update screen time duration on session end
CREATE OR REPLACE FUNCTION update_screen_time_duration()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.session_end IS NOT NULL AND OLD.session_end IS NULL THEN
        NEW.duration_minutes = EXTRACT(EPOCH FROM (NEW.session_end - NEW.session_start)) / 60;

        -- Update daily summary
        INSERT INTO compliance.daily_screen_time (user_id, summary_date, total_minutes, session_count)
        VALUES (NEW.user_id, NEW.session_date, NEW.duration_minutes, 1)
        ON CONFLICT (user_id, summary_date) DO UPDATE SET
            total_minutes = daily_screen_time.total_minutes + EXCLUDED.total_minutes,
            session_count = daily_screen_time.session_count + 1,
            updated_at = CURRENT_TIMESTAMP;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_screen_time_update_duration
    BEFORE UPDATE ON compliance.screen_time_sessions
    FOR EACH ROW EXECUTE FUNCTION update_screen_time_duration();

COMMIT;

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Get all COPPA-protected users
-- SELECT u.user_id, u.email, av.date_of_birth, av.parental_consent_given
-- FROM users u
-- JOIN age_verifications av ON av.user_id = u.user_id
-- WHERE av.is_coppa_protected = TRUE;

-- Get users exceeding screen time limits today
-- SELECT user_id, total_minutes, daily_limit_minutes,
--        (total_minutes - daily_limit_minutes) as minutes_over_limit
-- FROM daily_screen_time
-- WHERE summary_date = CURRENT_DATE
--   AND limit_exceeded = TRUE;

-- Get high-risk grooming detections
-- SELECT *
-- FROM grooming_detection_logs
-- WHERE risk_level IN ('high', 'critical')
--   AND created_at > CURRENT_TIMESTAMP - INTERVAL '7 days'
-- ORDER BY created_at DESC;

-- =====================================================
-- END MIGRATION 083
-- =====================================================
