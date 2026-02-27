-- ============================================================================
-- Migration 048: Course Authoring Sessions
--
-- Persistente Sessions für chat-basiertes Kurs-Authoring.
-- Speichert draft_structure für Kapitel/Lektionen/Methoden bevor finalize.
--
-- Neue Tabelle: course_authoring_sessions
-- ============================================================================

-- Course Authoring Sessions
CREATE TABLE IF NOT EXISTS courses.course_authoring_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID NOT NULL REFERENCES courses.courses(course_id) ON DELETE CASCADE,
    created_by UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,

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
        CHECK (status IN ('active', 'finalizing', 'finalized', 'archived')),

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
    ON courses.course_authoring_sessions (course_id);
CREATE INDEX IF NOT EXISTS idx_course_authoring_sessions_user
    ON courses.course_authoring_sessions (created_by);
CREATE INDEX IF NOT EXISTS idx_course_authoring_sessions_status
    ON courses.course_authoring_sessions (status);
CREATE INDEX IF NOT EXISTS idx_course_authoring_sessions_active
    ON courses.course_authoring_sessions (course_id, created_by)
    WHERE status = 'active';

-- Updated_at trigger
CREATE OR REPLACE FUNCTION update_course_authoring_session_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_course_authoring_session_updated ON courses.course_authoring_sessions ;
CREATE TRIGGER trg_course_authoring_session_updated
    BEFORE UPDATE ON courses.course_authoring_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_course_authoring_session_timestamp();

-- ============================================================================
-- Lesson Method Types erweitern (falls nicht vorhanden)
-- ============================================================================

-- Neue Lernmethoden-Typen für Tutorials
-- Diese werden als JSONB in learning_method_instances.data gespeichert
-- mit method_type als Diskriminator

COMMENT ON TABLE courses.course_authoring_sessions IS
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
GRANT SELECT, INSERT, UPDATE, DELETE ON courses.course_authoring_sessions TO lernsystem;

-- ============================================================================
-- EXTENSIONS (2025-01-07): Structured Dialog System & Approval Workflow
-- ============================================================================

-- ============================================================================
-- TABLE: authoring_dialog_messages
-- Description: Structured chat history instead of flat JSONB array
-- ============================================================================
CREATE TABLE IF NOT EXISTS courses.authoring_dialog_messages (
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES courses.course_authoring_sessions(session_id) ON DELETE CASCADE,

    -- Message ordering
    message_index INT NOT NULL,

    -- Message content
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,

    -- Structured data (for special messages)
    structured_data JSONB DEFAULT '{}',  -- {"action": "add_chapter", "params": {...}}

    -- AI metadata (only for assistant messages)
    ai_provider VARCHAR(50),
    ai_model VARCHAR(100),
    tokens_used INT DEFAULT 0,

    -- Context
    phase VARCHAR(50),  -- 'upload', 'analysis', 'planning', 'generation', 'refinement'
    references_chapter_id UUID,
    references_lesson_id UUID,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_authoring_dialog_session ON courses.authoring_dialog_messages(session_id, message_index);
CREATE INDEX IF NOT EXISTS idx_authoring_dialog_role ON courses.authoring_dialog_messages(role);
CREATE INDEX IF NOT EXISTS idx_authoring_dialog_phase ON courses.authoring_dialog_messages(phase);

COMMENT ON TABLE courses.authoring_dialog_messages IS 'Structured chat history for course authoring sessions (better than JSONB)';
COMMENT ON COLUMN courses.authoring_dialog_messages.message_index IS 'Sequential order of messages in conversation';
COMMENT ON COLUMN courses.authoring_dialog_messages.structured_data IS 'Structured data for special messages (actions, decisions, etc.)';
COMMENT ON COLUMN courses.authoring_dialog_messages.phase IS 'Workflow phase when message was sent';

-- ============================================================================
-- TABLE: authoring_plan_versions
-- Description: Versioned curriculum plans with approval tracking
-- ============================================================================
CREATE TABLE IF NOT EXISTS courses.authoring_plan_versions (
    version_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES courses.course_authoring_sessions(session_id) ON DELETE CASCADE,

    -- Version info
    version_number INT NOT NULL,
    is_current BOOLEAN DEFAULT false,

    -- Plan content
    plan_structure JSONB NOT NULL,  -- Full curriculum structure

    -- Changes from previous version
    change_summary TEXT,
    changes_detail JSONB DEFAULT '[]',  -- [{"type": "chapter_added", "data": {...}}]

    -- Approval workflow
    approval_status VARCHAR(50) DEFAULT 'draft'
        CHECK (approval_status IN ('draft', 'pending_review', 'approved', 'rejected', 'in_revision')),
    submitted_for_approval_at TIMESTAMPTZ,
    approved_by UUID REFERENCES core.users(user_id) ON DELETE SET NULL,
    approved_at TIMESTAMPTZ,
    rejection_reason TEXT,

    -- Quality metrics
    estimated_total_lessons INT,
    estimated_total_hours FLOAT,
    completeness_score FLOAT CHECK (completeness_score IS NULL OR (completeness_score >= 0.0 AND completeness_score <= 1.0)),

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_plan_versions_session ON courses.authoring_plan_versions(session_id, version_number);
CREATE INDEX IF NOT EXISTS idx_plan_versions_current ON courses.authoring_plan_versions(session_id) WHERE is_current = TRUE;
CREATE INDEX IF NOT EXISTS idx_plan_versions_status ON courses.authoring_plan_versions(approval_status);

COMMENT ON TABLE courses.authoring_plan_versions IS 'Versioned curriculum plans with approval workflow';
COMMENT ON COLUMN courses.authoring_plan_versions.is_current IS 'Currently active version for this session';
COMMENT ON COLUMN courses.authoring_plan_versions.changes_detail IS 'Detailed changelog from previous version';

-- ============================================================================
-- ALTER EXISTING TABLE: Add approval workflow to sessions
-- ============================================================================
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'course_authoring_sessions' AND column_name = 'plan_version') THEN
        ALTER TABLE courses.course_authoring_sessions
            ADD COLUMN plan_version INTEGER DEFAULT 1;
        RAISE NOTICE 'Added column course_authoring_sessions.plan_version';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'course_authoring_sessions' AND column_name = 'approval_status') THEN
        ALTER TABLE courses.course_authoring_sessions
            ADD COLUMN approval_status VARCHAR(50) DEFAULT 'draft'
                CHECK (approval_status IN ('draft', 'pending_review', 'approved', 'rejected', 'in_revision'));
        RAISE NOTICE 'Added column course_authoring_sessions.approval_status';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'course_authoring_sessions' AND column_name = 'approved_by') THEN
        ALTER TABLE courses.course_authoring_sessions
            ADD COLUMN approved_by UUID REFERENCES core.users(user_id) ON DELETE SET NULL;
        RAISE NOTICE 'Added column course_authoring_sessions.approved_by';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'course_authoring_sessions' AND column_name = 'approved_at') THEN
        ALTER TABLE courses.course_authoring_sessions
            ADD COLUMN approved_at TIMESTAMPTZ;
        RAISE NOTICE 'Added column course_authoring_sessions.approved_at';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'course_authoring_sessions' AND column_name = 'rejection_reason') THEN
        ALTER TABLE courses.course_authoring_sessions
            ADD COLUMN rejection_reason TEXT;
        RAISE NOTICE 'Added column course_authoring_sessions.rejection_reason';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'course_authoring_sessions' AND column_name = 'current_phase') THEN
        ALTER TABLE courses.course_authoring_sessions
            ADD COLUMN current_phase VARCHAR(50) DEFAULT 'upload'
                CHECK (current_phase IN ('upload', 'analysis', 'planning', 'generation', 'refinement', 'preview', 'finalize'));
        RAISE NOTICE 'Added column course_authoring_sessions.current_phase';
    END IF;
END $$;

COMMENT ON COLUMN courses.course_authoring_sessions.plan_version IS 'Current plan version number (increments with each major change)';
COMMENT ON COLUMN courses.course_authoring_sessions.approval_status IS 'Approval workflow status for course plan';
COMMENT ON COLUMN courses.course_authoring_sessions.approved_by IS 'User who approved the plan (for organizational workflows)';
COMMENT ON COLUMN courses.course_authoring_sessions.current_phase IS 'Current workflow phase for Progressive Disclosure';

-- ============================================================================
-- Grant permissions for new tables
-- ============================================================================
GRANT SELECT, INSERT, UPDATE, DELETE ON courses.authoring_dialog_messages TO lernsystem;
GRANT SELECT, INSERT, UPDATE, DELETE ON courses.authoring_plan_versions TO lernsystem;
