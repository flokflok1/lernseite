-- Migration: 070_learning_paths.sql
-- Purpose: AI-generated personalized learning paths (Feature #5)
-- Date: 2026-01-18

BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS learning_paths (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,

    -- Path metadata
    path_name VARCHAR(255) NOT NULL,
    description TEXT,
    target_audience VARCHAR(100),
    estimated_hours DECIMAL(5, 2),
    difficulty_level VARCHAR(20) CHECK (difficulty_level IN ('BEGINNER', 'INTERMEDIATE', 'ADVANCED', 'EXPERT')),

    -- Learning outcomes
    learning_outcomes TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- Configuration
    is_default BOOLEAN DEFAULT FALSE,
    is_published BOOLEAN DEFAULT FALSE,

    -- Tracking
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT fk_course FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_learning_paths_course_id ON learning_paths(course_id);
CREATE INDEX IF NOT EXISTS idx_learning_paths_default ON learning_paths(is_default);
CREATE INDEX IF NOT EXISTS idx_learning_paths_published ON learning_paths(is_published);
CREATE INDEX IF NOT EXISTS idx_learning_paths_difficulty ON learning_paths(difficulty_level);

-- Learning path steps (ordered sequence)
CREATE TABLE IF NOT EXISTS learning_path_steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    path_id UUID NOT NULL REFERENCES learning_paths(id) ON DELETE CASCADE,

    -- Sequence
    step_number INT NOT NULL CHECK (step_number >= 1),

    -- Content
    lesson_id UUID REFERENCES lessons(id) ON DELETE SET NULL,
    recommended_method_id INT REFERENCES learning_method_types(method_type) ON DELETE SET NULL,

    -- Attributes
    estimated_duration_minutes INT CHECK (estimated_duration_minutes >= 0),
    learning_objectives TEXT[] DEFAULT ARRAY[]::TEXT[],
    difficulty_score FLOAT CHECK (difficulty_score >= 0.0 AND difficulty_score <= 100.0),
    complexity_level VARCHAR(20) CHECK (complexity_level IN ('LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH')),

    -- Dependencies (step numbers that must be completed first)
    prerequisite_steps INT[] DEFAULT ARRAY[]::INT[],

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT fk_path FOREIGN KEY (path_id) REFERENCES learning_paths(id) ON DELETE CASCADE,
    CONSTRAINT fk_lesson FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE SET NULL,
    CONSTRAINT unique_path_step UNIQUE(path_id, step_number)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_learning_path_steps_path_id ON learning_path_steps(path_id);
CREATE INDEX IF NOT EXISTS idx_learning_path_steps_lesson_id ON learning_path_steps(lesson_id);
CREATE INDEX IF NOT EXISTS idx_learning_path_steps_complexity ON learning_path_steps(complexity_level);

COMMIT;
