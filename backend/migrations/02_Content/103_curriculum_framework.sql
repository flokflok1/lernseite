-- ============================================================================
-- Migration: 103_curriculum_framework.sql
-- Description: Curriculum framework tables for mapping training plans
--              (Ausbildungsrahmenplan) to exam topics and questions.
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-03-08
-- ============================================================================

-- 1. curriculum_frameworks — Container for a training plan
CREATE TABLE IF NOT EXISTS assessments.curriculum_frameworks (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(255) NOT NULL,
    framework_type  VARCHAR(50) NOT NULL DEFAULT 'custom',
    source_document VARCHAR(500),
    version         VARCHAR(50),
    valid_from      DATE,
    valid_until     DATE,
    metadata        JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_framework_type CHECK (
        framework_type IN ('ihk_ausbildung', 'hochschule', 'zertifizierung', 'custom')
    )
);

COMMENT ON TABLE assessments.curriculum_frameworks
    IS 'Container for a training/curriculum plan (e.g. IHK Ausbildungsrahmenplan)';

-- 2. curriculum_sections — Sections (e.g. Abschnitt A, B)
CREATE TABLE IF NOT EXISTS assessments.curriculum_sections (
    id            SERIAL PRIMARY KEY,
    framework_id  INT NOT NULL
        REFERENCES assessments.curriculum_frameworks(id) ON DELETE CASCADE,
    section_code  VARCHAR(10) NOT NULL,
    display_name  JSONB NOT NULL DEFAULT '{}',
    description   JSONB NOT NULL DEFAULT '{}',
    order_index   INT NOT NULL DEFAULT 0,
    applies_to    TEXT[],

    CONSTRAINT uq_section_code UNIQUE (framework_id, section_code)
);

COMMENT ON TABLE assessments.curriculum_sections
    IS 'Top-level sections within a curriculum framework (e.g. Abschnitt A, B)';

-- 3. curriculum_positions — Training positions within a section
CREATE TABLE IF NOT EXISTS assessments.curriculum_positions (
    id              SERIAL PRIMARY KEY,
    section_id      INT NOT NULL
        REFERENCES assessments.curriculum_sections(id) ON DELETE CASCADE,
    position_number VARCHAR(10) NOT NULL,
    display_name    JSONB NOT NULL DEFAULT '{}',
    description     JSONB NOT NULL DEFAULT '{}',
    order_index     INT NOT NULL DEFAULT 0,
    training_period VARCHAR(20),

    CONSTRAINT uq_position_number UNIQUE (section_id, position_number)
);

COMMENT ON TABLE assessments.curriculum_positions
    IS 'Numbered training positions within a curriculum section';

-- 4. curriculum_objectives — Learning objectives (a, b, c...)
CREATE TABLE IF NOT EXISTS assessments.curriculum_objectives (
    id               SERIAL PRIMARY KEY,
    position_id      INT NOT NULL
        REFERENCES assessments.curriculum_positions(id) ON DELETE CASCADE,
    objective_code   VARCHAR(10) NOT NULL,
    description      JSONB NOT NULL DEFAULT '{}',
    order_index      INT NOT NULL DEFAULT 0,
    competency_level VARCHAR(20),

    CONSTRAINT chk_competency_level CHECK (
        competency_level IS NULL
        OR competency_level IN ('kennen', 'anwenden', 'beherrschen')
    ),
    CONSTRAINT uq_objective_code UNIQUE (position_id, objective_code)
);

COMMENT ON TABLE assessments.curriculum_objectives
    IS 'Individual learning objectives within a training position';

-- 5. curriculum_topic_mapping — Objective <-> Topic Taxonomy
CREATE TABLE IF NOT EXISTS assessments.curriculum_topic_mapping (
    id                      SERIAL PRIMARY KEY,
    curriculum_objective_id INT NOT NULL
        REFERENCES assessments.curriculum_objectives(id) ON DELETE CASCADE,
    topic_id                UUID NOT NULL
        REFERENCES assessments.exam_topic_taxonomy(topic_id) ON DELETE CASCADE,
    confidence              FLOAT NOT NULL DEFAULT 0.0,
    mapped_by               VARCHAR(10) NOT NULL DEFAULT 'ai',
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_mapped_by CHECK (mapped_by IN ('ai', 'admin')),
    CONSTRAINT uq_objective_topic UNIQUE (curriculum_objective_id, topic_id)
);

COMMENT ON TABLE assessments.curriculum_topic_mapping
    IS 'Maps curriculum objectives to exam topic taxonomy nodes';

-- 6. exam_question_curriculum_tags — Question <-> Objective
CREATE TABLE IF NOT EXISTS assessments.exam_question_curriculum_tags (
    id                      SERIAL PRIMARY KEY,
    question_id             UUID NOT NULL
        REFERENCES assessments.exam_questions(question_id) ON DELETE CASCADE,
    curriculum_objective_id INT NOT NULL
        REFERENCES assessments.curriculum_objectives(id) ON DELETE CASCADE,
    confidence              FLOAT NOT NULL DEFAULT 0.0,
    tagged_by               VARCHAR(10) NOT NULL DEFAULT 'ai',
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_tagged_by CHECK (tagged_by IN ('ai', 'admin')),
    CONSTRAINT uq_question_objective UNIQUE (question_id, curriculum_objective_id)
);

COMMENT ON TABLE assessments.exam_question_curriculum_tags
    IS 'Tags exam questions with curriculum objectives for coverage analysis';

-- 7. ALTER exam_type_registry — add framework_id FK
ALTER TABLE assessments.exam_type_registry
    ADD COLUMN IF NOT EXISTS framework_id INT
        REFERENCES assessments.curriculum_frameworks(id) ON DELETE SET NULL;

-- 8. Indexes on all FK columns for query performance
CREATE INDEX IF NOT EXISTS idx_curriculum_sections_framework
    ON assessments.curriculum_sections(framework_id);

CREATE INDEX IF NOT EXISTS idx_curriculum_positions_section
    ON assessments.curriculum_positions(section_id);

CREATE INDEX IF NOT EXISTS idx_curriculum_objectives_position
    ON assessments.curriculum_objectives(position_id);

CREATE INDEX IF NOT EXISTS idx_curriculum_topic_mapping_objective
    ON assessments.curriculum_topic_mapping(curriculum_objective_id);

CREATE INDEX IF NOT EXISTS idx_curriculum_topic_mapping_topic
    ON assessments.curriculum_topic_mapping(topic_id);

CREATE INDEX IF NOT EXISTS idx_exam_question_curriculum_tags_question
    ON assessments.exam_question_curriculum_tags(question_id);

CREATE INDEX IF NOT EXISTS idx_exam_question_curriculum_tags_objective
    ON assessments.exam_question_curriculum_tags(curriculum_objective_id);

CREATE INDEX IF NOT EXISTS idx_exam_type_registry_framework
    ON assessments.exam_type_registry(framework_id);
