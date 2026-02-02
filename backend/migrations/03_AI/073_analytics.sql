-- Migration: 073_analytics.sql
-- Purpose: Analytics and insights tracking (Feature #8)
-- Date: 2026-01-18

BEGIN TRANSACTION;

-- NOTE: analytics schema is created in 01_Core/000_schemas.sql
-- No schema creation needed here

CREATE TABLE IF NOT EXISTS analytics.ai_editor_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organisation_id UUID NOT NULL REFERENCES organisations.organisations(organisation_id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses.courses(course_id) ON DELETE SET NULL,

    -- Metrics
    metric_type VARCHAR(50) NOT NULL CHECK (metric_type IN (
        'GENERATION_EFFICIENCY',
        'METHOD_EFFECTIVENESS',
        'LEARNING_GAPS',
        'QUALITY_SCORE',
        'TOKEN_USAGE',
        'COST_TRACKING',
        'USER_ENGAGEMENT'
    )),
    metric_value FLOAT NOT NULL,
    metric_data JSONB DEFAULT '{}'::jsonb,

    calculated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT fk_organisation FOREIGN KEY (organisation_id) REFERENCES organisations.organisations(organisation_id) ON DELETE CASCADE,
    CONSTRAINT fk_course FOREIGN KEY (course_id) REFERENCES courses.courses(course_id) ON DELETE SET NULL
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_ai_editor_analytics_organisation_id ON analytics.ai_editor_analytics(organisation_id);
CREATE INDEX IF NOT EXISTS idx_ai_editor_analytics_metric_type ON analytics.ai_editor_analytics(metric_type);
CREATE INDEX IF NOT EXISTS idx_ai_editor_analytics_calculated_at ON analytics.ai_editor_analytics(calculated_at DESC);
CREATE INDEX IF NOT EXISTS idx_ai_editor_analytics_course_id ON analytics.ai_editor_analytics(course_id);

-- AI-generated insights
CREATE TABLE IF NOT EXISTS analytics.ai_editor_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organisation_id UUID NOT NULL REFERENCES organisations.organisations(organisation_id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses.courses(course_id) ON DELETE SET NULL,

    -- Insight
    insight_type VARCHAR(50) NOT NULL CHECK (insight_type IN ('RECOMMENDATION', 'WARNING', 'OPPORTUNITY')),
    insight_text TEXT NOT NULL,
    affected_elements TEXT[] DEFAULT ARRAY[]::TEXT[],

    priority VARCHAR(20) DEFAULT 'MEDIUM' CHECK (priority IN ('LOW', 'MEDIUM', 'HIGH')),
    is_actionable BOOLEAN DEFAULT TRUE,

    -- Generation metadata
    generated_by_ai BOOLEAN DEFAULT TRUE,
    ai_model VARCHAR(50),

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT fk_organisation FOREIGN KEY (organisation_id) REFERENCES organisations.organisations(organisation_id) ON DELETE CASCADE,
    CONSTRAINT fk_course FOREIGN KEY (course_id) REFERENCES courses.courses(course_id) ON DELETE SET NULL
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_ai_editor_insights_organisation_id ON analytics.ai_editor_insights(organisation_id);
CREATE INDEX IF NOT EXISTS idx_ai_editor_insights_insight_type ON analytics.ai_editor_insights(insight_type);
CREATE INDEX IF NOT EXISTS idx_ai_editor_insights_priority ON analytics.ai_editor_insights(priority);
CREATE INDEX IF NOT EXISTS idx_ai_editor_insights_created_at ON analytics.ai_editor_insights(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ai_editor_insights_actionable ON analytics.ai_editor_insights(is_actionable);

COMMIT;
