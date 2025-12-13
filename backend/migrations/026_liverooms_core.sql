-- ============================================================================
-- Migration: 026_liverooms_core.sql
-- Description: LiveRoom core tables (based on 14_DB-Struktur.md Section 14)
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-01-17
-- ============================================================================

-- ============================================================================
-- TABLE: rooms
-- Description: LiveRoom main table (NOT liverooms - see doc Section 14.2)
-- ============================================================================
CREATE TABLE IF NOT EXISTS rooms (
    id SERIAL PRIMARY KEY,
    org_id UUID NOT NULL REFERENCES organizations(organization_id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses(course_id) ON DELETE SET NULL,
    chapter_id UUID REFERENCES chapters(chapter_id) ON DELETE SET NULL,
    created_by UUID REFERENCES users(user_id) ON DELETE SET NULL,
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

CREATE INDEX IF NOT EXISTS idx_rooms_org ON rooms(org_id);
CREATE INDEX IF NOT EXISTS idx_rooms_course ON rooms(course_id);
CREATE INDEX IF NOT EXISTS idx_rooms_chapter ON rooms(chapter_id);
CREATE INDEX IF NOT EXISTS idx_rooms_status ON rooms(status);
CREATE INDEX IF NOT EXISTS idx_rooms_created_by ON rooms(created_by);
CREATE INDEX IF NOT EXISTS idx_rooms_access_code ON rooms(access_code);

COMMENT ON TABLE rooms IS 'LiveRoom main table - virtual classrooms, seminars, study rooms';
COMMENT ON COLUMN rooms.room_type IS 'classroom, seminar, study, exam, ai';

-- ============================================================================
-- TABLE: room_participants
-- Description: Participants in LiveRooms
-- ============================================================================
CREATE TABLE IF NOT EXISTS room_participants (
    id SERIAL PRIMARY KEY,
    room_id INTEGER REFERENCES rooms(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    role VARCHAR(20) DEFAULT 'student',
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    left_at TIMESTAMPTZ,
    active BOOLEAN DEFAULT TRUE,
    participation_score DECIMAL(5,2) DEFAULT 0.00,
    CONSTRAINT chk_room_participant_role CHECK (role IN ('host', 'teacher', 'student', 'guest'))
);

CREATE INDEX IF NOT EXISTS idx_room_participants_room ON room_participants(room_id);
CREATE INDEX IF NOT EXISTS idx_room_participants_user ON room_participants(user_id);
CREATE INDEX IF NOT EXISTS idx_room_participants_active ON room_participants(room_id, active);

COMMENT ON TABLE room_participants IS 'LiveRoom participants with roles and participation tracking';

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- ============================================================================
CREATE TRIGGER update_rooms_updated_at BEFORE UPDATE ON rooms
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- End of Migration: 026_liverooms_core.sql
-- ============================================================================
