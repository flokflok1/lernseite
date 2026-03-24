-- ============================================================================
-- Migration: 106_exam_programs.sql
-- Description: Hierarchical exam programs (Beruf/Zertifizierung) → exam parts
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-03-14
-- ============================================================================

BEGIN;

-- ============================================================
-- 0. Ensure exam_type_registry exists (was never migrated!)
--    Must include framework_id FK added by migration 103.
-- ============================================================
CREATE TABLE IF NOT EXISTS assessments.exam_type_registry (
    exam_type     VARCHAR(50) PRIMARY KEY,
    display_name  JSONB NOT NULL DEFAULT '{}',
    passing_score INTEGER DEFAULT 50,
    parts         JSONB,
    settings      JSONB,
    created_at    TIMESTAMPTZ DEFAULT now(),
    framework_id  INTEGER REFERENCES assessments.curriculum_frameworks(id) ON DELETE SET NULL
);

-- ============================================================
-- 1. Create exam_programs parent table
-- ============================================================
CREATE TABLE IF NOT EXISTS assessments.exam_programs (
    program_id   SERIAL PRIMARY KEY,
    program_key  VARCHAR(50) UNIQUE NOT NULL,
    display_name JSONB NOT NULL,
    program_type VARCHAR(30) NOT NULL
        CHECK (program_type IN ('ausbildung', 'zertifizierung', 'studium', 'custom')),
    provider     VARCHAR(100),
    description  JSONB,
    icon         VARCHAR(10),
    sort_order   INTEGER DEFAULT 0,
    created_at   TIMESTAMPTZ DEFAULT now()
);

-- ============================================================
-- 2. Seed programs
-- ============================================================
INSERT INTO assessments.exam_programs
    (program_key, display_name, program_type, provider, icon, sort_order)
VALUES
    ('fachinformatiker',
     '{"de": "Fachinformatiker", "en": "IT Specialist"}'::jsonb,
     'ausbildung', 'IHK', '🎓', 1),
    ('comptia_aplus',
     '{"de": "CompTIA A+", "en": "CompTIA A+"}'::jsonb,
     'zertifizierung', 'CompTIA', '🏅', 10),
    ('comptia_netplus',
     '{"de": "CompTIA Network+", "en": "CompTIA Network+"}'::jsonb,
     'zertifizierung', 'CompTIA', '🏅', 11),
    ('aws_saa',
     '{"de": "AWS Solutions Architect Associate", "en": "AWS Solutions Architect Associate"}'::jsonb,
     'zertifizierung', 'AWS', '☁️', 20)
ON CONFLICT (program_key) DO NOTHING;

-- ============================================================
-- 3. Add columns to exam_type_registry (idempotent)
-- ============================================================
ALTER TABLE assessments.exam_type_registry
    ADD COLUMN IF NOT EXISTS program_id INTEGER
        REFERENCES assessments.exam_programs(program_id) ON DELETE SET NULL;

ALTER TABLE assessments.exam_type_registry
    ADD COLUMN IF NOT EXISTS applies_to TEXT[] DEFAULT '{}';

ALTER TABLE assessments.exam_type_registry
    ADD COLUMN IF NOT EXISTS sort_order INTEGER DEFAULT 0;

ALTER TABLE assessments.exam_type_registry
    ADD COLUMN IF NOT EXISTS archive_folder_id UUID
        REFERENCES assessments.archive_folders(folder_id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_exam_type_registry_program
    ON assessments.exam_type_registry(program_id);

CREATE INDEX IF NOT EXISTS idx_exam_type_registry_archive_folder
    ON assessments.exam_type_registry(archive_folder_id)
    WHERE archive_folder_id IS NOT NULL;

-- ============================================================
-- 4. Insert NEW exam types with new keys (idempotent)
--    Fresh install: creates all types. Existing: adds new ones.
-- ============================================================
INSERT INTO assessments.exam_type_registry
    (exam_type, display_name, passing_score, program_id, applies_to, sort_order)
VALUES
    ('FI_AP1',
     '{"de": "AP1 (gemeinsam)", "en": "AP1 (shared)"}'::jsonb,
     50,
     (SELECT program_id FROM assessments.exam_programs WHERE program_key = 'fachinformatiker'),
     '{FISI,FIAE}', 1),
    ('FI_AP2_FISI',
     '{"de": "AP2 Systemintegration", "en": "AP2 System Integration"}'::jsonb,
     50,
     (SELECT program_id FROM assessments.exam_programs WHERE program_key = 'fachinformatiker'),
     '{FISI}', 2),
    ('FI_AP2_FIAE',
     '{"de": "AP2 Anwendungsentwicklung", "en": "AP2 Application Development"}'::jsonb,
     50,
     (SELECT program_id FROM assessments.exam_programs WHERE program_key = 'fachinformatiker'),
     '{FIAE}', 3),
    ('AWS_SAA_C03',
     '{"de": "SAA-C03", "en": "SAA-C03"}'::jsonb,
     72,
     (SELECT program_id FROM assessments.exam_programs WHERE program_key = 'aws_saa'),
     '{}', 1),
    ('COMPTIA_APLUS_CORE1',
     '{"de": "Core 1 (220-1101)", "en": "Core 1 (220-1101)"}'::jsonb,
     70,
     (SELECT program_id FROM assessments.exam_programs WHERE program_key = 'comptia_aplus'),
     '{}', 1),
    ('COMPTIA_NETPLUS_N10',
     '{"de": "N10-009", "en": "N10-009"}'::jsonb,
     70,
     (SELECT program_id FROM assessments.exam_programs WHERE program_key = 'comptia_netplus'),
     '{}', 1)
ON CONFLICT (exam_type) DO UPDATE SET
    program_id = EXCLUDED.program_id,
    applies_to = EXCLUDED.applies_to,
    sort_order = EXCLUDED.sort_order;

-- ============================================================
-- 5. Migrate FK references from old keys → new keys
--    (On fresh install: 0 rows affected — safe)
-- ============================================================

-- IHK_FISI_AP1 → FI_AP1
UPDATE assessments.exam_sessions
    SET exam_type_key = 'FI_AP1' WHERE exam_type_key = 'IHK_FISI_AP1';
UPDATE assessments.exams
    SET exam_type_key = 'FI_AP1' WHERE exam_type_key = 'IHK_FISI_AP1';
UPDATE assessments.exam_topic_taxonomy
    SET exam_type = 'FI_AP1' WHERE exam_type = 'IHK_FISI_AP1';
UPDATE assessments.exam_topic_global_stats
    SET exam_type = 'FI_AP1' WHERE exam_type = 'IHK_FISI_AP1';
UPDATE assessments.exam_topic_clusters
    SET exam_type_key = 'FI_AP1' WHERE exam_type_key = 'IHK_FISI_AP1';
UPDATE core.user_exam_goals
    SET exam_type = 'FI_AP1' WHERE exam_type = 'IHK_FISI_AP1';

-- IHK_FISI_AP2 → FI_AP2_FISI
UPDATE assessments.exam_sessions
    SET exam_type_key = 'FI_AP2_FISI' WHERE exam_type_key = 'IHK_FISI_AP2';
UPDATE assessments.exams
    SET exam_type_key = 'FI_AP2_FISI' WHERE exam_type_key = 'IHK_FISI_AP2';
UPDATE assessments.exam_topic_taxonomy
    SET exam_type = 'FI_AP2_FISI' WHERE exam_type = 'IHK_FISI_AP2';
UPDATE assessments.exam_topic_clusters
    SET exam_type_key = 'FI_AP2_FISI' WHERE exam_type_key = 'IHK_FISI_AP2';

-- IHK_FIAE → FI_AP1 (AP1 is shared)
UPDATE assessments.exam_sessions
    SET exam_type_key = 'FI_AP1' WHERE exam_type_key = 'IHK_FIAE';
UPDATE assessments.exams
    SET exam_type_key = 'FI_AP1' WHERE exam_type_key = 'IHK_FIAE';
UPDATE assessments.exam_topic_taxonomy
    SET exam_type = 'FI_AP1' WHERE exam_type = 'IHK_FIAE';
UPDATE assessments.exam_topic_clusters
    SET exam_type_key = 'FI_AP1' WHERE exam_type_key = 'IHK_FIAE';
UPDATE core.user_exam_goals
    SET exam_type = 'FI_AP1' WHERE exam_type = 'IHK_FIAE';

-- Also catch IHK_FISI (used in migration 100 backfill)
UPDATE assessments.exam_sessions
    SET exam_type_key = 'FI_AP1' WHERE exam_type_key = 'IHK_FISI';
UPDATE assessments.exams
    SET exam_type_key = 'FI_AP1' WHERE exam_type_key = 'IHK_FISI';

-- ============================================================
-- 6. Remove old keys (only affects existing installs)
-- ============================================================
DELETE FROM assessments.exam_type_registry
    WHERE exam_type IN ('IHK_FISI_AP1', 'IHK_FISI_AP2', 'IHK_FIAE',
                         'IHK_FISI', 'AWS_SAA', 'CompTIA_A+', 'CompTIA_Net+');

COMMIT;
