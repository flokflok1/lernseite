-- ============================================================================
-- Migration 071: Chapter Theory Storage
-- ============================================================================
-- Stores KI-generated chapter theory content for user-facing display.
-- Theory is generated once and cached to save tokens.
--
-- Features:
-- - JSONB storage for flexible theory structure (overview, concepts, etc.)
-- - Whiteboard actions for ADHS-friendly visual learning
-- - TTS audio URL for voice playback
-- - Style variants (adhs, detailed, short, exam_focus)
-- ============================================================================

-- Chapter Theory Table
CREATE TABLE IF NOT EXISTS chapter_theory (
    theory_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chapter_id UUID NOT NULL REFERENCES chapters(chapter_id) ON DELETE CASCADE,
    style VARCHAR(20) NOT NULL DEFAULT 'adhs',

    -- Theory content (JSONB for flexible structure)
    theory_data JSONB NOT NULL,
    -- Example structure:
    -- {
    --   "overview": "Short overview text",
    --   "learningGoals": ["Goal 1", "Goal 2"],
    --   "concepts": [{"title": "...", "description": "...", "example": "..."}],
    --   "terms": [{"term": "...", "definition": "...", "example": "..."}],
    --   "examTips": ["Tip 1", "Tip 2"],
    --   "summary": "Summary text",
    --   "whiteboardActions": [
    --     {"type": "write", "content": "...", "position": {"x": 50, "y": 20}, "duration": 1000}
    --   ]
    -- }

    -- TTS Audio
    audio_url VARCHAR(500),
    audio_duration_seconds INTEGER,

    -- Generation metadata
    tokens_used INTEGER DEFAULT 0,
    model_used VARCHAR(50),
    generated_by UUID REFERENCES users(user_id),

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Unique constraint: one theory per chapter per style
    CONSTRAINT uq_chapter_theory_style UNIQUE (chapter_id, style)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_chapter_theory_chapter_id ON chapter_theory(chapter_id);
CREATE INDEX IF NOT EXISTS idx_chapter_theory_style ON chapter_theory(style);

-- GIN index for JSONB queries (e.g., searching within theory content)
CREATE INDEX IF NOT EXISTS idx_chapter_theory_data ON chapter_theory USING GIN (theory_data);

-- Updated timestamp trigger
CREATE OR REPLACE FUNCTION update_chapter_theory_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS chapter_theory_updated ON chapter_theory;
CREATE TRIGGER chapter_theory_updated
    BEFORE UPDATE ON chapter_theory
    FOR EACH ROW
    EXECUTE FUNCTION update_chapter_theory_timestamp();

-- Comment on table
COMMENT ON TABLE chapter_theory IS 'Stores KI-generated chapter theory content for user learning. Generated once per chapter/style combination.';
COMMENT ON COLUMN chapter_theory.theory_data IS 'JSONB containing theory content: overview, learningGoals, concepts, terms, examTips, summary, whiteboardActions';
COMMENT ON COLUMN chapter_theory.style IS 'Theory style: adhs (visual), detailed, short, exam_focus, standard';

-- Grant permissions (adjust as needed)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON chapter_theory TO lernsystem_app;
