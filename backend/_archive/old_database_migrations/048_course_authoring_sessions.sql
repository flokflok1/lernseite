-- ============================================================================
-- Migration 048: Course Authoring Sessions
--
-- Persistente Sessions für chat-basiertes Kurs-Authoring.
-- Speichert draft_structure für Kapitel/Lektionen/Methoden bevor finalize.
--
-- Neue Tabelle: course_authoring_sessions
-- ============================================================================

-- Course Authoring Sessions
CREATE TABLE IF NOT EXISTS course_authoring_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,
    created_by UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,

    -- Model/Provider configuration
    model_profile VARCHAR(100) NOT NULL DEFAULT 'anthropic-claude-sonnet',

    -- Draft structure (Kurs-Entwurf mit Kapiteln/Lektionen/Methoden)
    draft_structure JSONB NOT NULL DEFAULT '{
        "chapters": [],
        "meta": {
            "version": 1,
            "last_operation": null
        }
    }'::jsonb,

    -- Chat history (optional, für Replay)
    chat_history JSONB DEFAULT '[]'::jsonb,

    -- Files used in this session
    file_context JSONB DEFAULT '[]'::jsonb,

    -- Session status
    status VARCHAR(20) NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'finalized', 'archived')),

    -- Stats
    total_tokens_used INTEGER DEFAULT 0,
    total_operations INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    finalized_at TIMESTAMP WITH TIME ZONE
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_course_authoring_sessions_course
    ON course_authoring_sessions(course_id);
CREATE INDEX IF NOT EXISTS idx_course_authoring_sessions_user
    ON course_authoring_sessions(created_by);
CREATE INDEX IF NOT EXISTS idx_course_authoring_sessions_status
    ON course_authoring_sessions(status);
CREATE INDEX IF NOT EXISTS idx_course_authoring_sessions_active
    ON course_authoring_sessions(course_id, created_by)
    WHERE status = 'active';

-- Updated_at trigger
CREATE OR REPLACE FUNCTION update_course_authoring_session_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_course_authoring_session_updated ON course_authoring_sessions;
CREATE TRIGGER trg_course_authoring_session_updated
    BEFORE UPDATE ON course_authoring_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_course_authoring_session_timestamp();

-- ============================================================================
-- Lesson Method Types erweitern (falls nicht vorhanden)
-- ============================================================================

-- Neue Lernmethoden-Typen für Tutorials
-- Diese werden als JSONB in learning_method_instances.data gespeichert
-- mit method_type als Diskriminator

COMMENT ON TABLE course_authoring_sessions IS
'Persistente Sessions für chat-basiertes Kurs-Authoring.
draft_structure enthält den Kurs-Entwurf bevor finalize() aufgerufen wird.

Struktur von draft_structure:
{
  "chapters": [
    {
      "id": "temp-uuid",
      "title": "Kapitelname",
      "description": "...",
      "existing_id": null | "real-uuid",
      "lessons": [
        {
          "id": "temp-uuid",
          "title": "Lektionsname",
          "type": "text",
          "existing_id": null | "real-uuid",
          "methods": [
            {
              "id": "temp-uuid",
              "type": "calculator_tutorial|tool_tutorial|step_by_step|theory|quiz",
              "title": "...",
              "content": {...}
            }
          ]
        }
      ]
    }
  ],
  "meta": {
    "version": 1,
    "last_operation": "add_chapter"
  }
}';

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON course_authoring_sessions TO lernsystem;
