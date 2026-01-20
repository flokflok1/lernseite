-- Migration: 074_material_recommendations.sql
-- Purpose: External material recommendations and integrations (Feature #6)
-- Date: 2026-01-18

BEGIN TRANSACTION;

-- Ensure ai_pipeline schema exists
CREATE SCHEMA IF NOT EXISTS ai_pipeline;

CREATE TABLE IF NOT EXISTS ai_pipeline.material_resources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lesson_id UUID REFERENCES courses.lessons(lesson_id) ON DELETE SET NULL,
    session_id UUID REFERENCES ai_pipeline.ai_editor_sessions(id) ON DELETE SET NULL,

    -- Resource metadata
    resource_type VARCHAR(50) NOT NULL CHECK (resource_type IN ('IMAGE', 'VIDEO', 'CODE_EXAMPLE', 'DATASET', 'ARTICLE')),
    resource_url TEXT NOT NULL,
    resource_title VARCHAR(255),
    resource_description TEXT,

    -- Source
    source VARCHAR(50) NOT NULL CHECK (source IN ('UNSPLASH', 'YOUTUBE', 'GITHUB', 'KAGGLE', 'GENERATED')),
    source_id VARCHAR(255),

    -- Licensing
    license_type VARCHAR(50) CHECK (license_type IN ('CC0', 'CC_BY', 'CC_BY_SA', 'CC_BY_ND', 'CC_BY_NC', 'CC_BY_NC_SA', 'CC_BY_NC_ND', 'CUSTOM')),
    license_url TEXT,
    attribution_required BOOLEAN DEFAULT FALSE,
    attribution_text TEXT,

    -- QA
    quality_score FLOAT CHECK (quality_score >= 0.0 AND quality_score <= 1.0),
    is_approved BOOLEAN DEFAULT FALSE,
    approved_by UUID REFERENCES core.users(user_id) ON DELETE SET NULL,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT fk_lesson FOREIGN KEY (lesson_id) REFERENCES courses.lessons(lesson_id) ON DELETE SET NULL,
    CONSTRAINT fk_session FOREIGN KEY (session_id) REFERENCES ai_pipeline.ai_editor_sessions(id) ON DELETE SET NULL,
    CONSTRAINT fk_approved_by FOREIGN KEY (approved_by) REFERENCES core.users(user_id) ON DELETE SET NULL
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_material_resources_lesson_id ON ai_pipeline.material_resources(lesson_id);
CREATE INDEX IF NOT EXISTS idx_material_resources_session_id ON ai_pipeline.material_resources(session_id);
CREATE INDEX IF NOT EXISTS idx_material_resources_type ON ai_pipeline.material_resources(resource_type);
CREATE INDEX IF NOT EXISTS idx_material_resources_source ON ai_pipeline.material_resources(source);
CREATE INDEX IF NOT EXISTS idx_material_resources_approved ON ai_pipeline.material_resources(is_approved);
CREATE INDEX IF NOT EXISTS idx_material_resources_quality_score ON ai_pipeline.material_resources(quality_score DESC);

-- Material usage tracking
CREATE TABLE IF NOT EXISTS ai_pipeline.material_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    material_id UUID NOT NULL REFERENCES ai_pipeline.material_resources(id) ON DELETE CASCADE,
    lesson_id UUID NOT NULL REFERENCES courses.lessons(lesson_id) ON DELETE CASCADE,
    user_id UUID REFERENCES core.users(user_id) ON DELETE SET NULL,

    -- Usage data
    view_count INT DEFAULT 0,
    download_count INT DEFAULT 0,
    rating FLOAT CHECK (rating >= 0.0 AND rating <= 5.0),
    feedback_text TEXT,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT fk_material FOREIGN KEY (material_id) REFERENCES ai_pipeline.material_resources(id) ON DELETE CASCADE,
    CONSTRAINT fk_lesson FOREIGN KEY (lesson_id) REFERENCES courses.lessons(lesson_id) ON DELETE CASCADE,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES core.users(user_id) ON DELETE SET NULL
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_material_usage_material_id ON ai_pipeline.material_usage(material_id);
CREATE INDEX IF NOT EXISTS idx_material_usage_lesson_id ON ai_pipeline.material_usage(lesson_id);
CREATE INDEX IF NOT EXISTS idx_material_usage_user_id ON ai_pipeline.material_usage(user_id);
CREATE INDEX IF NOT EXISTS idx_material_usage_rating ON ai_pipeline.material_usage(rating DESC);

COMMIT;
