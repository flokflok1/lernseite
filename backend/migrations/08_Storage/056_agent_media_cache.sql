-- ============================================================================
-- Migration: 056_agent_media_cache.sql
-- Description: Agent Media Cache - TTS, Audio, Video, Transcripts
-- Author: Claude Code
-- Date: 2025-12-10
-- ============================================================================
--
-- Erweiterung des Smart Agent Systems um Media Caching:
-- - TTS Audio Responses (vorgelesene Antworten)
-- - Video Erklaerungen (KI-generierte Videos)
-- - Realtime Transcripts (Whisper Transkriptionen)
-- - Lip-Sync Videos (Avatar mit Audio)
--
-- Token-Ersparnis Projektion:
-- - TTS: $0.015/1000 chars -> Bei 1000 gleichen Anfragen: 99% Ersparnis
-- - Whisper: $0.006/min -> Einmalig transkribieren, ewig cachen
-- - Video Gen: Sehr teuer -> Massive Ersparnis durch Wiederverwertung
-- ============================================================================

BEGIN;

-- ============================================================================
-- TABLE: agent_media_cache
-- Description: Cached media assets (audio, video, images)
-- ============================================================================
CREATE TABLE IF NOT EXISTS smart_agents.agent_media_cache (
    media_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES smart_agents.course_agents(agent_id) ON DELETE CASCADE,

    -- Media Identification
    content_hash VARCHAR(64) NOT NULL,  -- SHA256 of source content
    media_type VARCHAR(20) NOT NULL,    -- tts_audio, video, image, transcript

    -- Source Reference
    source_type VARCHAR(30) NOT NULL,   -- answer_text, lesson_content, question
    source_id UUID,                      -- knowledge_id, lesson_id, etc.
    source_text TEXT,                    -- Original text (for TTS/video)

    -- Media Storage
    storage_provider VARCHAR(20) DEFAULT 'local',  -- local, s3, cloudflare
    storage_path TEXT NOT NULL,                     -- File path or URL
    file_size_bytes BIGINT,
    mime_type VARCHAR(50),
    duration_ms INTEGER,                            -- For audio/video

    -- Generation Config
    generation_config JSONB DEFAULT '{}',  -- voice, speed, quality settings
    generation_model VARCHAR(100),          -- tts-1, whisper-1, etc.
    generation_cost DECIMAL(10,6) DEFAULT 0,

    -- Cache Status
    status VARCHAR(20) DEFAULT 'ready',
    quality_tier INTEGER DEFAULT 2,        -- 1=high, 2=medium, 3=low

    -- Usage Stats
    access_count INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMPTZ,

    -- TTL Management
    expires_at TIMESTAMPTZ,
    never_expire BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Composite unique for deduplication
    UNIQUE(agent_id, content_hash, media_type, generation_config),

    CONSTRAINT chk_media_type CHECK (
        media_type IN ('tts_audio', 'video_explanation', 'video_avatar',
                       'transcript', 'image', 'diagram')
    ),
    CONSTRAINT chk_media_status CHECK (
        status IN ('generating', 'ready', 'failed', 'expired')
    ),
    CONSTRAINT chk_storage_provider CHECK (
        storage_provider IN ('local', 's3', 'cloudflare', 'azure')
    )
);

CREATE INDEX idx_agent_media_cache_agent ON smart_agents.agent_media_cache (agent_id);
CREATE INDEX idx_agent_media_cache_hash ON smart_agents.agent_media_cache (content_hash);
CREATE INDEX idx_agent_media_cache_type ON smart_agents.agent_media_cache (media_type);
CREATE INDEX idx_agent_media_cache_source ON smart_agents.agent_media_cache (source_type, source_id);
CREATE INDEX idx_agent_media_cache_expires ON smart_agents.agent_media_cache (expires_at) WHERE expires_at IS NOT NULL;
CREATE INDEX idx_agent_media_cache_access ON smart_agents.agent_media_cache (last_accessed_at DESC);

-- ============================================================================
-- TABLE: agent_tts_cache
-- Description: Specialized TTS audio cache with voice settings
-- ============================================================================
CREATE TABLE IF NOT EXISTS smart_agents.agent_tts_cache (
    tts_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    media_id UUID NOT NULL REFERENCES smart_agents.agent_media_cache(media_id) ON DELETE CASCADE,

    -- Text Source
    text_hash VARCHAR(64) NOT NULL,
    text_content TEXT NOT NULL,
    text_language VARCHAR(5) DEFAULT 'de',
    char_count INTEGER NOT NULL,

    -- Voice Settings
    voice_id VARCHAR(50) NOT NULL,        -- alloy, echo, fable, onyx, nova, shimmer
    voice_provider VARCHAR(30) NOT NULL,  -- openai, elevenlabs, azure
    speech_speed DECIMAL(3,2) DEFAULT 1.0,

    -- Audio Details
    audio_format VARCHAR(10) DEFAULT 'mp3',
    sample_rate INTEGER DEFAULT 24000,
    bitrate INTEGER,

    -- Cost Tracking
    cost_per_char DECIMAL(10,8),
    total_cost DECIMAL(10,6),

    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(text_hash, voice_id, speech_speed, voice_provider)
);

CREATE INDEX idx_agent_tts_text ON smart_agents.agent_tts_cache (text_hash);
CREATE INDEX idx_agent_tts_voice ON smart_agents.agent_tts_cache (voice_id);

-- ============================================================================
-- TABLE: agent_transcript_cache
-- Description: Cached audio/video transcriptions
-- ============================================================================
CREATE TABLE IF NOT EXISTS smart_agents.agent_transcript_cache (
    transcript_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    media_id UUID REFERENCES smart_agents.agent_media_cache(media_id) ON DELETE CASCADE,

    -- Source Audio/Video
    source_file_hash VARCHAR(64) NOT NULL,
    source_file_path TEXT,
    source_duration_ms INTEGER,

    -- Transcript Content
    transcript_text TEXT NOT NULL,
    transcript_language VARCHAR(5),
    detected_language VARCHAR(5),

    -- Segments (for timestamps)
    segments JSONB DEFAULT '[]',  -- [{start: 0, end: 1.5, text: "Hello"}]
    word_timestamps JSONB,        -- Word-level timestamps if available

    -- Quality
    confidence_score DECIMAL(5,4),
    model_used VARCHAR(50),        -- whisper-1, deepgram-nova

    -- Cost
    cost_per_minute DECIMAL(10,6),
    total_cost DECIMAL(10,6),

    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(source_file_hash)
);

CREATE INDEX idx_agent_transcript_hash ON smart_agents.agent_transcript_cache (source_file_hash);
CREATE INDEX idx_agent_transcript_lang ON smart_agents.agent_transcript_cache (transcript_language);

-- Full-text search for transcripts
CREATE INDEX idx_agent_transcript_fts ON smart_agents.agent_transcript_cache USING GIN (to_tsvector('german', transcript_text));

-- ============================================================================
-- TABLE: agent_video_cache
-- Description: Cached video explanations and avatar videos
-- ============================================================================
CREATE TABLE IF NOT EXISTS smart_agents.agent_video_cache (
    video_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    media_id UUID NOT NULL REFERENCES smart_agents.agent_media_cache(media_id) ON DELETE CASCADE,

    -- Video Type
    video_type VARCHAR(30) NOT NULL,  -- explanation, avatar_lipsync, diagram_anim

    -- Source Content
    source_text TEXT,                  -- Script/explanation text
    source_audio_id UUID REFERENCES smart_agents.agent_tts_cache(tts_id),  -- Linked TTS

    -- Avatar Settings (for lip-sync videos)
    avatar_id VARCHAR(50),
    avatar_provider VARCHAR(30),       -- heygen, synthesia, d-id
    avatar_style JSONB DEFAULT '{}',   -- clothing, background, etc.

    -- Video Details
    resolution VARCHAR(20),            -- 720p, 1080p, 4k
    framerate INTEGER DEFAULT 30,
    codec VARCHAR(20) DEFAULT 'h264',

    -- Thumbnail
    thumbnail_path TEXT,

    -- Generation
    render_time_ms INTEGER,
    generation_cost DECIMAL(10,4),

    created_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT chk_video_type CHECK (
        video_type IN ('explanation', 'avatar_lipsync', 'diagram_animation',
                       'whiteboard', 'screen_recording')
    )
);

CREATE INDEX idx_agent_video_type ON smart_agents.agent_video_cache (video_type);
CREATE INDEX idx_agent_video_avatar ON smart_agents.agent_video_cache (avatar_id);

-- ============================================================================
-- TABLE: agent_realtime_sessions
-- Description: Track realtime audio/video sessions for caching
-- ============================================================================
CREATE TABLE IF NOT EXISTS smart_agents.agent_realtime_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES smart_agents.course_agents(agent_id) ON DELETE SET NULL,
    user_id UUID REFERENCES core.users(user_id) ON DELETE SET NULL,

    -- Session Info
    session_type VARCHAR(30) NOT NULL,  -- voice_chat, video_tutoring
    started_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    duration_ms INTEGER,

    -- Recording
    recording_path TEXT,
    recording_size_bytes BIGINT,

    -- Transcript
    transcript_id UUID REFERENCES smart_agents.agent_transcript_cache(transcript_id),

    -- AI Interactions
    total_turns INTEGER DEFAULT 0,
    user_audio_duration_ms INTEGER DEFAULT 0,
    agent_audio_duration_ms INTEGER DEFAULT 0,

    -- Cost
    transcription_cost DECIMAL(10,6) DEFAULT 0,
    tts_cost DECIMAL(10,6) DEFAULT 0,
    ai_cost DECIMAL(10,6) DEFAULT 0,
    total_cost DECIMAL(10,6) DEFAULT 0,

    -- Caching Stats
    responses_from_cache INTEGER DEFAULT 0,
    responses_generated INTEGER DEFAULT 0,
    tokens_saved INTEGER DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT chk_session_type CHECK (
        session_type IN ('voice_chat', 'video_tutoring', 'pronunciation',
                         'oral_exam', 'live_qa')
    )
);

CREATE INDEX idx_agent_realtime_agent ON smart_agents.agent_realtime_sessions (agent_id);
CREATE INDEX idx_agent_realtime_user ON smart_agents.agent_realtime_sessions (user_id);
CREATE INDEX idx_agent_realtime_type ON smart_agents.agent_realtime_sessions (session_type);
CREATE INDEX idx_agent_realtime_started ON smart_agents.agent_realtime_sessions (started_at DESC);

-- ============================================================================
-- VIEW: v_agent_media_stats
-- Description: Media cache statistics per agent
-- ============================================================================
CREATE OR REPLACE VIEW v_agent_media_stats AS
SELECT
    ca.agent_id,
    ca.course_id,
    c.title as course_title,

    -- TTS Stats
    COUNT(DISTINCT amc.media_id) FILTER (WHERE amc.media_type = 'tts_audio') as tts_cached,
    SUM(amc.access_count) FILTER (WHERE amc.media_type = 'tts_audio') as tts_accesses,
    SUM(amc.generation_cost) FILTER (WHERE amc.media_type = 'tts_audio') as tts_generation_cost,

    -- Video Stats
    COUNT(DISTINCT amc.media_id) FILTER (WHERE amc.media_type LIKE 'video%') as videos_cached,
    SUM(amc.access_count) FILTER (WHERE amc.media_type LIKE 'video%') as video_accesses,

    -- Transcript Stats
    COUNT(DISTINCT atc.transcript_id) as transcripts_cached,
    SUM(atc.total_cost) as transcription_cost,

    -- Storage
    SUM(amc.file_size_bytes) as total_storage_bytes,

    -- Estimated Savings
    SUM(amc.access_count * amc.generation_cost) - SUM(amc.generation_cost) as estimated_savings

FROM smart_agents.course_agents ca
JOIN courses.courses c ON ca.course_id = c.course_id
LEFT JOIN smart_agents.agent_media_cache amc ON ca.agent_id = amc.agent_id
LEFT JOIN smart_agents.agent_transcript_cache atc ON amc.media_id = atc.media_id
GROUP BY ca.agent_id, ca.course_id, c.title;

-- ============================================================================
-- FUNCTION: get_or_create_tts_cache
-- Description: Check for cached TTS or mark as needing generation
-- ============================================================================
CREATE OR REPLACE FUNCTION get_or_create_tts_cache(
    p_agent_id UUID,
    p_text TEXT,
    p_voice_id VARCHAR(50),
    p_voice_provider VARCHAR(30) DEFAULT 'openai',
    p_speed DECIMAL(3,2) DEFAULT 1.0
) RETURNS TABLE (
    cache_found BOOLEAN,
    media_id UUID,
    storage_path TEXT,
    text_hash VARCHAR(64)
) AS $$
DECLARE
    v_text_hash VARCHAR(64);
    v_media_id UUID;
    v_storage_path TEXT;
BEGIN
    -- Generate hash
    v_text_hash := encode(sha256(p_text::bytea), 'hex');

    -- Check for existing cache
    SELECT amc.media_id, amc.storage_path
    INTO v_media_id, v_storage_path
    FROM smart_agents.agent_tts_cache atc
    JOIN smart_agents.agent_media_cache amc ON atc.media_id = amc.media_id
    WHERE atc.text_hash = v_text_hash
      AND atc.voice_id = p_voice_id
      AND atc.voice_provider = p_voice_provider
      AND atc.speech_speed = p_speed
      AND amc.status = 'ready'
      AND (amc.expires_at IS NULL OR amc.expires_at > NOW());

    IF v_media_id IS NOT NULL THEN
        -- Update access stats
        UPDATE smart_agents.agent_media_cache
        SET access_count = access_count + 1,
            last_accessed_at = NOW()
        WHERE media_id = v_media_id;

        RETURN QUERY SELECT TRUE, v_media_id, v_storage_path, v_text_hash;
    ELSE
        RETURN QUERY SELECT FALSE, NULL::UUID, NULL::TEXT, v_text_hash;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- FUNCTION: get_or_create_transcript_cache
-- Description: Check for cached transcript
-- ============================================================================
CREATE OR REPLACE FUNCTION get_or_create_transcript_cache(
    p_file_hash VARCHAR(64)
) RETURNS TABLE (
    cache_found BOOLEAN,
    transcript_id UUID,
    transcript_text TEXT,
    segments JSONB
) AS $$
DECLARE
    v_transcript_id UUID;
    v_text TEXT;
    v_segments JSONB;
BEGIN
    SELECT atc.transcript_id, atc.transcript_text, atc.segments
    INTO v_transcript_id, v_text, v_segments
    FROM smart_agents.agent_transcript_cache atc
    WHERE atc.source_file_hash = p_file_hash;

    IF v_transcript_id IS NOT NULL THEN
        -- Update access stats
        UPDATE smart_agents.agent_media_cache amc
        SET access_count = access_count + 1,
            last_accessed_at = NOW()
        FROM smart_agents.agent_transcript_cache atc
        WHERE atc.transcript_id = v_transcript_id
          AND amc.media_id = atc.media_id;

        RETURN QUERY SELECT TRUE, v_transcript_id, v_text, v_segments;
    ELSE
        RETURN QUERY SELECT FALSE, NULL::UUID, NULL::TEXT, NULL::JSONB;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Extend agent_knowledge_base for media references
-- ============================================================================
ALTER TABLE smart_agents.agent_knowledge_base ADD COLUMN IF NOT EXISTS tts_media_id UUID REFERENCES smart_agents.agent_media_cache(media_id);
ALTER TABLE smart_agents.agent_knowledge_base ADD COLUMN IF NOT EXISTS video_media_id UUID REFERENCES smart_agents.agent_media_cache(media_id);
ALTER TABLE smart_agents.agent_knowledge_base ADD COLUMN IF NOT EXISTS has_audio BOOLEAN DEFAULT FALSE;
ALTER TABLE smart_agents.agent_knowledge_base ADD COLUMN IF NOT EXISTS has_video BOOLEAN DEFAULT FALSE;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Update timestamp trigger for agent_media_cache
DROP TRIGGER IF EXISTS update_agent_media_cache_updated_at ON smart_agents.agent_media_cache ;
CREATE TRIGGER update_agent_media_cache_updated_at
    BEFORE UPDATE ON smart_agents.agent_media_cache
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMIT;

-- ============================================================================
-- Post-migration verification
-- ============================================================================
DO $$
BEGIN
    RAISE NOTICE 'Migration 066_agent_media_cache.sql completed successfully';
    RAISE NOTICE 'Created tables: agent_media_cache, agent_tts_cache, agent_transcript_cache, agent_video_cache, agent_realtime_sessions';
    RAISE NOTICE 'Created view: v_agent_media_stats';
    RAISE NOTICE 'Created functions: get_or_create_tts_cache, get_or_create_transcript_cache';
END $$;
