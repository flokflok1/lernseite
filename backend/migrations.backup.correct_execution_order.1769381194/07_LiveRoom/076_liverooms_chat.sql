-- ============================================================================
-- Migration: 027_liverooms_chat.sql
-- Version: 1.0.0
-- Description: Database migration
-- Author: LernsystemX Migration System
-- Date: 2026-01-02
-- ============================================================================

CREATE TABLE IF NOT EXISTS liveroom.room_whiteboards (
    id SERIAL PRIMARY KEY,
    room_id INTEGER REFERENCES liveroom.rooms(id) ON DELETE CASCADE,
    user_id UUID REFERENCES core.users(user_id) ON DELETE SET NULL,
    content JSONB,
    ai_recognition JSONB,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_room_whiteboards_room ON liveroom.room_whiteboards(room_id);
CREATE INDEX IF NOT EXISTS idx_room_whiteboards_content ON liveroom.room_whiteboards USING GIN(content);

COMMENT ON TABLE liveroom.room_whiteboards IS 'Whiteboard drawings with AI diagram recognition';
COMMENT ON COLUMN liveroom.room_whiteboards.content IS 'JSONB: pages, elements (paths, text, shapes)';
COMMENT ON COLUMN liveroom.room_whiteboards.ai_recognition IS 'JSONB: recognized formulas, diagrams, keywords';

-- ============================================================================
-- TABLE: room_transcripts
-- Description: AI-generated transcripts and summaries
-- ============================================================================
CREATE TABLE IF NOT EXISTS liveroom.room_transcripts (
    id SERIAL PRIMARY KEY,
    room_id INTEGER REFERENCES liveroom.rooms(id) ON DELETE CASCADE,
    language VARCHAR(10) DEFAULT 'de',
    transcript TEXT,
    summary TEXT,
    keywords TEXT[],
    ai_model VARCHAR(50),
    token_used INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_room_transcripts_room ON liveroom.room_transcripts(room_id);
CREATE INDEX IF NOT EXISTS idx_room_transcripts_language ON liveroom.room_transcripts(language);

COMMENT ON TABLE liveroom.room_transcripts IS 'AI transcripts and summaries of LiveRoom audio';

-- ============================================================================
-- TABLE: room_recordings
-- Description: Video/audio recordings
-- ============================================================================
CREATE TABLE IF NOT EXISTS liveroom.room_recordings (
    id SERIAL PRIMARY KEY,
    room_id INTEGER REFERENCES liveroom.rooms(id) ON DELETE CASCADE,
    file_url TEXT NOT NULL,
    duration_seconds INTEGER,
    storage_location VARCHAR(100),
    transcription_id INTEGER REFERENCES liveroom.room_transcripts(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_room_recordings_room ON liveroom.room_recordings(room_id);
CREATE INDEX IF NOT EXISTS idx_room_recordings_transcription ON liveroom.room_recordings(transcription_id);

COMMENT ON TABLE liveroom.room_recordings IS 'LiveRoom recordings with cloud storage references';

-- ============================================================================
-- TABLE: room_logs
-- Description: Event logs for rooms (moderation, actions)
-- ============================================================================
CREATE TABLE IF NOT EXISTS liveroom.room_logs (
    id SERIAL PRIMARY KEY,
    room_id INTEGER REFERENCES liveroom.rooms(id) ON DELETE CASCADE,
    actor_id UUID REFERENCES core.users(user_id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    details TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_room_logs_room ON liveroom.room_logs(room_id);
CREATE INDEX IF NOT EXISTS idx_room_logs_timestamp ON liveroom.room_logs(timestamp);

COMMENT ON TABLE liveroom.room_logs IS 'LiveRoom event logs: participant actions, moderation, system events';

-- ============================================================================
-- TABLE: room_ai_stats
-- Description: AI usage statistics per room
-- ============================================================================
CREATE TABLE IF NOT EXISTS liveroom.room_ai_stats (
    id SERIAL PRIMARY KEY,
    room_id INTEGER REFERENCES liveroom.rooms(id) ON DELETE CASCADE,
    ai_model VARCHAR(50),
    token_input INTEGER DEFAULT 0,
    token_output INTEGER DEFAULT 0,
    cost_usd DECIMAL(8,4) DEFAULT 0.0000,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_room_ai_stats_room ON liveroom.room_ai_stats(room_id);
CREATE INDEX IF NOT EXISTS idx_room_ai_stats_created ON liveroom.room_ai_stats(created_at);

COMMENT ON TABLE liveroom.room_ai_stats IS 'AI token usage and costs per LiveRoom session';

-- ============================================================================
-- End of Migration: 027_liverooms_chat.sql
-- ============================================================================
