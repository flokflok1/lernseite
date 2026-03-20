-- ============================================================================
-- Migration: 108_program_types_enrollments.sql
-- Description: Dynamic program types + user enrollments + course linking
-- ============================================================================
BEGIN;

-- 1. program_types — replaces hardcoded CHECK constraint
CREATE TABLE IF NOT EXISTS assessments.program_types (
    type_key     VARCHAR(50) PRIMARY KEY,
    display_name JSONB NOT NULL,
    icon         VARCHAR(10),
    sort_order   INTEGER DEFAULT 0,
    created_at   TIMESTAMPTZ DEFAULT now()
);

INSERT INTO assessments.program_types (type_key, display_name, icon, sort_order)
VALUES
    ('ausbildung',     '{"de":"Ausbildung","en":"Apprenticeship","pl":"Szkolenie"}'::jsonb, NULL, 1),
    ('zertifizierung', '{"de":"Zertifizierung","en":"Certification","pl":"Certyfikacja"}'::jsonb, NULL, 2),
    ('studium',        '{"de":"Studium","en":"Studies","pl":"Studia"}'::jsonb, NULL, 3),
    ('custom',         '{"de":"Sonstige","en":"Other","pl":"Inne"}'::jsonb, NULL, 99)
ON CONFLICT (type_key) DO NOTHING;

-- Replace CHECK constraint with FK
ALTER TABLE assessments.exam_programs
    DROP CONSTRAINT IF EXISTS exam_programs_program_type_check;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_exam_programs_program_type'
    ) THEN
        ALTER TABLE assessments.exam_programs
            ADD CONSTRAINT fk_exam_programs_program_type
            FOREIGN KEY (program_type) REFERENCES assessments.program_types(type_key)
            ON UPDATE CASCADE;
    END IF;
END $$;

-- 2. user_program_enrollments
CREATE TABLE IF NOT EXISTS assessments.user_program_enrollments (
    user_id     UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,
    program_id  INTEGER NOT NULL REFERENCES assessments.exam_programs(program_id) ON DELETE CASCADE,
    enrolled_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (user_id, program_id)
);

CREATE INDEX IF NOT EXISTS idx_user_program_enrollments_user
    ON assessments.user_program_enrollments(user_id);

-- 3. course_id on exam_type_registry (link exam part to learning course)
ALTER TABLE assessments.exam_type_registry
    ADD COLUMN IF NOT EXISTS course_id UUID
    REFERENCES courses.courses(course_id) ON DELETE SET NULL;

-- 4. Auto-enroll existing users who have exam attempts
INSERT INTO assessments.user_program_enrollments (user_id, program_id)
SELECT DISTINCT
    ea.user_id,
    ep.program_id
FROM assessments.exam_attempts ea
JOIN assessments.exams e ON e.exam_id = ea.exam_id
JOIN assessments.exam_type_registry etr ON etr.exam_type = e.exam_type_key
JOIN assessments.exam_programs ep ON ep.program_id = etr.program_id
WHERE ep.program_id IS NOT NULL
ON CONFLICT DO NOTHING;

COMMIT;
