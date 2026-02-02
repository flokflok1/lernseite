-- ============================================================================
-- Migration: 019_ai_prompts.sql
-- Version: 1.0.0
-- Description: Database migration
-- Author: LernsystemX Migration System
-- Date: 2026-01-02
-- ============================================================================

CREATE TABLE IF NOT EXISTS ai_pipeline.ai_prompts (
    prompt_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prompt_key VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    use_case VARCHAR(100),
    current_version INTEGER DEFAULT 1,
    active BOOLEAN DEFAULT TRUE,
    created_by UUID REFERENCES core.users(user_id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_prompt_category CHECK (category IN ('chapter_generation', 'method_generation', 'exam_generation', 'translation', 'summarization', 'analysis', 'tutoring', 'feedback'))
);

CREATE INDEX IF NOT EXISTS idx_ai_prompts_key ON ai_pipeline.ai_prompts(prompt_key);
CREATE INDEX IF NOT EXISTS idx_ai_prompts_category ON ai_pipeline.ai_prompts(category);
CREATE INDEX IF NOT EXISTS idx_ai_prompts_active ON ai_pipeline.ai_prompts(active) WHERE active = TRUE;

COMMENT ON TABLE ai_pipeline.ai_prompts IS 'AI prompt template registry';

-- ============================================================================
-- TABLE: ai_prompt_versions
-- Description: Versioned prompt templates
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_pipeline.ai_prompt_versions (
    version_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prompt_id UUID REFERENCES ai_pipeline.ai_prompts(prompt_id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    template TEXT NOT NULL,
    variables JSONB,
    system_message TEXT,
    temperature DECIMAL(3,2) DEFAULT 0.7,
    max_tokens INTEGER DEFAULT 2000,
    preferred_model_id INTEGER REFERENCES ai_pipeline.ai_models(model_id) ON DELETE SET NULL,
    tags TEXT[],
    changelog TEXT,
    performance_metrics JSONB,
    active BOOLEAN DEFAULT TRUE,
    created_by UUID REFERENCES core.users(user_id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_prompt_temperature CHECK (temperature >= 0 AND temperature <= 2),
    UNIQUE (prompt_id, version_number)
);

CREATE INDEX IF NOT EXISTS idx_prompt_versions_prompt ON ai_pipeline.ai_prompt_versions(prompt_id, version_number DESC);
CREATE INDEX IF NOT EXISTS idx_prompt_versions_model ON ai_pipeline.ai_prompt_versions(preferred_model_id);
CREATE INDEX IF NOT EXISTS idx_prompt_versions_active ON ai_pipeline.ai_prompt_versions(active) WHERE active = TRUE;

COMMENT ON TABLE ai_pipeline.ai_prompt_versions IS 'Versioned AI prompt templates with A/B testing support';
COMMENT ON COLUMN ai_pipeline.ai_prompt_versions.variables IS 'JSONB array of variable names used in template';

-- ============================================================================
-- TABLE: ai_prompt_learning_method_mapping
-- Description: Maps learning methods to AI prompts
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_pipeline.ai_prompt_learning_method_mapping (
    mapping_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    method_type INTEGER NOT NULL REFERENCES learning_methods.learning_method_types(method_type) ON DELETE RESTRICT,
    prompt_id UUID REFERENCES ai_pipeline.ai_prompts(prompt_id) ON DELETE CASCADE,
    priority INTEGER DEFAULT 0,
    UNIQUE (method_type, prompt_id)
);

CREATE INDEX IF NOT EXISTS idx_prompt_mapping_method ON ai_pipeline.ai_prompt_learning_method_mapping(method_type);
CREATE INDEX IF NOT EXISTS idx_prompt_mapping_prompt ON ai_pipeline.ai_prompt_learning_method_mapping(prompt_id);

COMMENT ON TABLE ai_pipeline.ai_prompt_learning_method_mapping IS 'Maps 19 Content-Lernmethoden to AI prompts';

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- ============================================================================
DROP TRIGGER IF EXISTS update_ai_prompts_updated_at ON ai_pipeline.ai_prompts;
CREATE TRIGGER update_ai_prompts_updated_at BEFORE UPDATE ON ai_pipeline.ai_prompts
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- End of Migration: 019_ai_prompts.sql
-- ============================================================================
