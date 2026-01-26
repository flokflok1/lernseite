-- Migration: 071_interactive_scenarios.sql
-- Purpose: Interactive simulations, case studies, branching narratives (Feature #9)
-- Date: 2026-01-18

BEGIN TRANSACTION;

-- Note: ai_pipeline schema created in migration 021_ai_providers.sql
CREATE TABLE IF NOT EXISTS ai_pipeline.interactive_scenarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lesson_id UUID NOT NULL REFERENCES courses.lessons(lesson_id) ON DELETE CASCADE,

    -- Type
    scenario_type VARCHAR(50) NOT NULL CHECK (scenario_type IN ('SIMULATION', 'CASE_STUDY', 'BRANCHING_NARRATIVE', 'DECISION_TREE')),

    -- Content
    root_content TEXT NOT NULL,
    choice_tree JSONB NOT NULL DEFAULT '{}'::jsonb,

    -- Generation
    generated_by_ai BOOLEAN DEFAULT TRUE,
    ai_model VARCHAR(50),

    -- Tracking
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT fk_lesson FOREIGN KEY (lesson_id) REFERENCES courses.lessons(lesson_id) ON DELETE CASCADE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_interactive_scenarios_lesson_id ON ai_pipeline.interactive_scenarios(lesson_id);
CREATE INDEX IF NOT EXISTS idx_interactive_scenarios_type ON ai_pipeline.interactive_scenarios(scenario_type);
CREATE INDEX IF NOT EXISTS idx_interactive_scenarios_created_at ON ai_pipeline.interactive_scenarios(created_at DESC);

-- User interactions with scenarios
CREATE TABLE IF NOT EXISTS ai_pipeline.scenario_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id UUID NOT NULL REFERENCES ai_pipeline.interactive_scenarios(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,

    -- Interaction data
    current_path TEXT[] DEFAULT ARRAY[]::TEXT[],
    completion_percentage INT DEFAULT 0 CHECK (completion_percentage >= 0 AND completion_percentage <= 100),
    learning_outcomes_achieved TEXT[] DEFAULT ARRAY[]::TEXT[],

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP,

    -- Constraints
    CONSTRAINT fk_scenario FOREIGN KEY (scenario_id) REFERENCES ai_pipeline.interactive_scenarios(id) ON DELETE CASCADE,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES core.users(user_id) ON DELETE CASCADE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_scenario_interactions_scenario_user ON ai_pipeline.scenario_interactions(scenario_id, user_id);
CREATE INDEX IF NOT EXISTS idx_scenario_interactions_user_id ON ai_pipeline.scenario_interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_scenario_interactions_completion_percentage ON ai_pipeline.scenario_interactions(completion_percentage);

COMMIT;
