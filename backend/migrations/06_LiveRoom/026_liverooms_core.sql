-- ============================================================================
-- Migration: 026_liverooms_core.sql
-- Version: 1.0.0
-- Description: Database migration
-- Author: LernsystemX Migration System
-- Date: 2026-01-02
-- ============================================================================

CREATE TABLE IF NOT EXISTS liveroom.rooms (
    id SERIAL PRIMARY KEY,
    org_id UUID NOT NULL REFERENCES organisations.organisations(organization_id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses.courses(course_id) ON DELETE SET NULL,
    chapter_id UUID REFERENCES courses.chapters(chapter_id) ON DELETE SET NULL,
    created_by UUID REFERENCES core.users(user_id) ON DELETE SET NULL,
    room_type VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'active',
    max_participants INTEGER DEFAULT 50,
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    duration_minutes INTEGER,
    enable_ai BOOLEAN DEFAULT FALSE,
    enable_recording BOOLEAN DEFAULT FALSE,
    ai_model VARCHAR(50),
    ai_pipeline_version VARCHAR(20),
    access_code VARCHAR(10),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_room_type CHECK (room_type IN ('classroom', 'seminar', 'study', 'exam', 'ai')),
    CONSTRAINT chk_room_status CHECK (status IN ('active', 'closed', 'archived'))
);

CREATE INDEX IF NOT EXISTS idx_rooms_org ON liveroom.rooms(org_id);
CREATE INDEX IF NOT EXISTS idx_rooms_course ON liveroom.rooms(course_id);
CREATE INDEX IF NOT EXISTS idx_rooms_chapter ON liveroom.rooms(chapter_id);
CREATE INDEX IF NOT EXISTS idx_rooms_status ON liveroom.rooms(status);
CREATE INDEX IF NOT EXISTS idx_rooms_created_by ON liveroom.rooms(created_by);
CREATE INDEX IF NOT EXISTS idx_rooms_access_code ON liveroom.rooms(access_code);

COMMENT ON TABLE liveroom.rooms IS 'LiveRoom main table - virtual classrooms, seminars, study rooms';
COMMENT ON COLUMN liveroom.rooms.room_type IS 'classroom, seminar, study, exam, ai';

-- ============================================================================
-- TABLE: room_participants
-- Description: Participants in LiveRooms
-- ============================================================================
CREATE TABLE IF NOT EXISTS liveroom.room_participants (
    id SERIAL PRIMARY KEY,
    room_id INTEGER REFERENCES liveroom.rooms(id) ON DELETE CASCADE,
    user_id UUID REFERENCES core.users(user_id) ON DELETE CASCADE,
    role VARCHAR(20) DEFAULT 'student',
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    left_at TIMESTAMPTZ,
    active BOOLEAN DEFAULT TRUE,
    participation_score DECIMAL(5,2) DEFAULT 0.00,
    CONSTRAINT chk_room_participant_role CHECK (role IN ('host', 'teacher', 'student', 'guest'))
);

CREATE INDEX IF NOT EXISTS idx_room_participants_room ON liveroom.room_participants(room_id);
CREATE INDEX IF NOT EXISTS idx_room_participants_user ON liveroom.room_participants(user_id);
CREATE INDEX IF NOT EXISTS idx_room_participants_active ON liveroom.room_participants(room_id, active);

COMMENT ON TABLE liveroom.room_participants IS 'LiveRoom participants with roles and participation tracking';

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- ============================================================================
DROP TRIGGER IF EXISTS update_rooms_updated_at ON liveroom.rooms;
CREATE TRIGGER update_rooms_updated_at BEFORE UPDATE ON liveroom.rooms
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- TABLE: tutor_agent_configs
-- Description: Tutor configuration per course
-- ============================================================================
CREATE TABLE IF NOT EXISTS liveroom.tutor_agent_configs (
    config_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID REFERENCES courses.courses(course_id) ON DELETE CASCADE,
    enabled BOOLEAN DEFAULT FALSE,
    persona VARCHAR(50) DEFAULT 'friendly',
    personality_traits JSONB DEFAULT '{"strictness": 50, "humor": 50, "patience": 70}',
    custom_persona_name VARCHAR(100),
    custom_persona_description TEXT,
    use_voice BOOLEAN DEFAULT FALSE,
    use_whiteboard BOOLEAN DEFAULT FALSE,
    use_avatar BOOLEAN DEFAULT FALSE,
    use_gestures BOOLEAN DEFAULT FALSE,
    voice_id VARCHAR(100),
    avatar_style VARCHAR(50),
    adaptive_scaffolding BOOLEAN DEFAULT TRUE,
    hint_levels INTEGER DEFAULT 3 CHECK (hint_levels BETWEEN 1 AND 5),
    fading_support BOOLEAN DEFAULT TRUE,
    preferred_strategy VARCHAR(50) DEFAULT 'mixed',
    allow_partial_credit BOOLEAN DEFAULT TRUE,
    auto_generate_tasks BOOLEAN DEFAULT TRUE,
    difficulty_adaptation BOOLEAN DEFAULT TRUE,
    emotional_feedback BOOLEAN DEFAULT TRUE,
    engagement_detection BOOLEAN DEFAULT FALSE,
    frustration_intervention BOOLEAN DEFAULT TRUE,
    xp_rewards BOOLEAN DEFAULT FALSE,
    challenge_mode BOOLEAN DEFAULT FALSE,
    cost_mode VARCHAR(20) DEFAULT 'hybrid',
    rule_based_fallback BOOLEAN DEFAULT TRUE,
    max_ai_tokens_per_session INTEGER DEFAULT 10000,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(course_id)
);

CREATE INDEX IF NOT EXISTS idx_tutor_agent_configs_course ON liveroom.tutor_agent_configs(course_id);
CREATE INDEX IF NOT EXISTS idx_tutor_agent_configs_enabled ON liveroom.tutor_agent_configs(enabled) WHERE enabled = TRUE;

DROP TRIGGER IF EXISTS update_tutor_agent_configs_updated_at ON liveroom.tutor_agent_configs;
CREATE TRIGGER update_tutor_agent_configs_updated_at
    BEFORE UPDATE ON liveroom.tutor_agent_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- TABLE: tutor_interactions
-- Description: Tutor interaction logs
-- ============================================================================
CREATE TABLE IF NOT EXISTS liveroom.tutor_interactions (
    interaction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,
    interaction_type VARCHAR(50) NOT NULL,
    tutor_message TEXT,
    tutor_message_html TEXT,
    modality VARCHAR(20) DEFAULT 'text',
    voice_audio_url TEXT,
    whiteboard_data JSONB,
    user_response TEXT,
    user_response_type VARCHAR(20),
    was_correct BOOLEAN,
    partial_score DECIMAL(5,2),
    feedback_given TEXT,
    related_lm_id INTEGER,
    related_lm_instance_id UUID,
    related_content_ref JSONB,
    ai_model_used VARCHAR(100),
    ai_tokens_input INTEGER DEFAULT 0,
    ai_tokens_output INTEGER DEFAULT 0,
    ai_latency_ms INTEGER,
    response_time_seconds INTEGER,
    engagement_indicator VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tutor_interactions_session ON liveroom.tutor_interactions(session_id);
CREATE INDEX IF NOT EXISTS idx_tutor_interactions_type ON liveroom.tutor_interactions(interaction_type);
CREATE INDEX IF NOT EXISTS idx_tutor_interactions_created ON liveroom.tutor_interactions(created_at DESC);

-- ============================================================================
-- End of Migration: 026_liverooms_core.sql
-- ============================================================================
