-- ============================================================================
-- Migration: 027_liverooms_chat.sql
-- Description: LiveRoom interaction tables (whiteboard, transcripts, recordings, logs, AI stats)
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-01-17
-- ============================================================================

-- ============================================================================
-- TABLE: room_whiteboards
-- Description: Whiteboard content and AI recognition
-- ============================================================================
CREATE TABLE IF NOT EXISTS room_whiteboards (
    id SERIAL PRIMARY KEY,
    room_id INTEGER REFERENCES rooms(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    content JSONB,
    ai_recognition JSONB,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_room_whiteboards_room ON room_whiteboards(room_id);
CREATE INDEX IF NOT EXISTS idx_room_whiteboards_content ON room_whiteboards USING GIN(content);

COMMENT ON TABLE room_whiteboards IS 'Whiteboard drawings with AI diagram recognition';
COMMENT ON COLUMN room_whiteboards.content IS 'JSONB: pages, elements (paths, text, shapes)';
COMMENT ON COLUMN room_whiteboards.ai_recognition IS 'JSONB: recognized formulas, diagrams, keywords';

-- ============================================================================
-- TABLE: room_transcripts
-- Description: AI-generated transcripts and summaries
-- ============================================================================
CREATE TABLE IF NOT EXISTS room_transcripts (
    id SERIAL PRIMARY KEY,
    room_id INTEGER REFERENCES rooms(id) ON DELETE CASCADE,
    language VARCHAR(10) DEFAULT 'de',
    transcript TEXT,
    summary TEXT,
    keywords TEXT[],
    ai_model VARCHAR(50),
    token_used INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_room_transcripts_room ON room_transcripts(room_id);
CREATE INDEX IF NOT EXISTS idx_room_transcripts_language ON room_transcripts(language);

COMMENT ON TABLE room_transcripts IS 'AI transcripts and summaries of LiveRoom audio';

-- ============================================================================
-- TABLE: room_recordings
-- Description: Video/audio recordings
-- ============================================================================
CREATE TABLE IF NOT EXISTS room_recordings (
    id SERIAL PRIMARY KEY,
    room_id INTEGER REFERENCES rooms(id) ON DELETE CASCADE,
    file_url TEXT NOT NULL,
    duration_seconds INTEGER,
    storage_location VARCHAR(100),
    transcription_id INTEGER REFERENCES room_transcripts(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_room_recordings_room ON room_recordings(room_id);
CREATE INDEX IF NOT EXISTS idx_room_recordings_transcription ON room_recordings(transcription_id);

COMMENT ON TABLE room_recordings IS 'LiveRoom recordings with cloud storage references';

-- ============================================================================
-- TABLE: room_logs
-- Description: Event logs for rooms (moderation, actions)
-- ============================================================================
CREATE TABLE IF NOT EXISTS room_logs (
    id SERIAL PRIMARY KEY,
    room_id INTEGER REFERENCES rooms(id) ON DELETE CASCADE,
    actor_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    details TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_room_logs_room ON room_logs(room_id);
CREATE INDEX IF NOT EXISTS idx_room_logs_timestamp ON room_logs(timestamp);

COMMENT ON TABLE room_logs IS 'LiveRoom event logs: participant actions, moderation, system events';

-- ============================================================================
-- TABLE: room_ai_stats
-- Description: AI usage statistics per room
-- ============================================================================
CREATE TABLE IF NOT EXISTS room_ai_stats (
    id SERIAL PRIMARY KEY,
    room_id INTEGER REFERENCES rooms(id) ON DELETE CASCADE,
    ai_model VARCHAR(50),
    token_input INTEGER DEFAULT 0,
    token_output INTEGER DEFAULT 0,
    cost_usd DECIMAL(8,4) DEFAULT 0.0000,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_room_ai_stats_room ON room_ai_stats(room_id);
CREATE INDEX IF NOT EXISTS idx_room_ai_stats_created ON room_ai_stats(created_at);

COMMENT ON TABLE room_ai_stats IS 'AI token usage and costs per LiveRoom session';

-- ============================================================================
-- End of Migration: 027_liverooms_chat.sql
-- ============================================================================
