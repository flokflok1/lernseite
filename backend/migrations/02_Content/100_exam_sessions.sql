-- 100_exam_sessions.sql
-- Hierarchische Gruppierung: exam_type -> region -> session -> exams
-- + Community-Upload Spalten auf exams

-- ============================================================
-- 1. Regions-Referenz
-- ============================================================
CREATE TABLE IF NOT EXISTS assessments.exam_regions (
    region_code  VARCHAR(50) PRIMARY KEY,
    display_name JSONB NOT NULL DEFAULT '{}'
);

INSERT INTO assessments.exam_regions (region_code, display_name) VALUES
    ('alle', '{"de": "Alle Bundesländer", "en": "All States", "pl": "Wszystkie"}'),
    ('bw', '{"de": "Baden-Württemberg", "en": "Baden-Württemberg", "pl": "Badenia-Wirtembergia"}'),
    ('bayern', '{"de": "Bayern", "en": "Bavaria", "pl": "Bawaria"}'),
    ('nrw', '{"de": "Nordrhein-Westfalen", "en": "North Rhine-Westphalia", "pl": "Nadrenia Północna-Westfalia"}'),
    ('hessen', '{"de": "Hessen", "en": "Hesse", "pl": "Hesja"}'),
    ('niedersachsen', '{"de": "Niedersachsen", "en": "Lower Saxony", "pl": "Dolna Saksonia"}'),
    ('sachsen', '{"de": "Sachsen", "en": "Saxony", "pl": "Saksonia"}'),
    ('berlin', '{"de": "Berlin", "en": "Berlin", "pl": "Berlin"}')
ON CONFLICT DO NOTHING;

-- ============================================================
-- 2. Sessions-Tabelle
-- ============================================================
CREATE TABLE IF NOT EXISTS assessments.exam_sessions (
    session_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exam_type_key VARCHAR(50) NOT NULL
        REFERENCES assessments.exam_type_registry(exam_type),
    region        VARCHAR(50) NOT NULL DEFAULT 'alle'
        REFERENCES assessments.exam_regions(region_code),
    year          INTEGER NOT NULL,
    season        VARCHAR(10) NOT NULL CHECK (season IN ('sommer', 'winter')),
    tags          TEXT[] DEFAULT '{}',
    notes         TEXT,
    created_by    UUID REFERENCES core.users(user_id) ON DELETE SET NULL,
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    updated_at    TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (exam_type_key, region, year, season)
);

CREATE INDEX IF NOT EXISTS idx_exam_sessions_type
    ON assessments.exam_sessions(exam_type_key);
CREATE INDEX IF NOT EXISTS idx_exam_sessions_year
    ON assessments.exam_sessions(year DESC);

-- ============================================================
-- 3. FK session_id auf exams
-- ============================================================
ALTER TABLE assessments.exams
    ADD COLUMN IF NOT EXISTS session_id UUID
    REFERENCES assessments.exam_sessions(session_id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_exams_session
    ON assessments.exams(session_id) WHERE session_id IS NOT NULL;

-- ============================================================
-- 4. Community-Upload Spalten auf exams
-- ============================================================
ALTER TABLE assessments.exams
    ADD COLUMN IF NOT EXISTS uploaded_by UUID
    REFERENCES core.users(user_id) ON DELETE SET NULL;

ALTER TABLE assessments.exams
    ADD COLUMN IF NOT EXISTS upload_source VARCHAR(20)
    DEFAULT 'admin';

ALTER TABLE assessments.exams
    ADD COLUMN IF NOT EXISTS moderation_notes TEXT;

-- ============================================================
-- 5. Backfill: exam_type_key setzen
-- ============================================================
UPDATE assessments.exams SET exam_type_key = 'IHK_FISI'
WHERE profession ILIKE '%fisi%' AND exam_type_key IS NULL;

UPDATE assessments.exams SET exam_type_key = 'IHK_FIAE'
WHERE profession ILIKE '%fiae%' AND exam_type_key IS NULL;

-- Fallback: alle ohne Key -> FISI
UPDATE assessments.exams SET exam_type_key = 'IHK_FISI'
WHERE exam_type = 'real' AND exam_type_key IS NULL;

-- ============================================================
-- 6. Backfill: Sessions aus bestehenden Exams erstellen
-- ============================================================
INSERT INTO assessments.exam_sessions (exam_type_key, region, year, season)
SELECT DISTINCT
    COALESCE(e.exam_type_key, 'IHK_FISI'),
    COALESCE(NULLIF(LOWER(e.region), ''), 'alle'),
    e.year,
    LOWER(e.season)
FROM assessments.exams e
WHERE e.year IS NOT NULL
  AND e.season IS NOT NULL
  AND e.exam_type = 'real'
  AND e.session_id IS NULL
ON CONFLICT (exam_type_key, region, year, season) DO NOTHING;

-- ============================================================
-- 7. Backfill: Exams mit Sessions verknuepfen
-- ============================================================
UPDATE assessments.exams e
SET session_id = s.session_id
FROM assessments.exam_sessions s
WHERE COALESCE(e.exam_type_key, 'IHK_FISI') = s.exam_type_key
  AND COALESCE(NULLIF(LOWER(e.region), ''), 'alle') = s.region
  AND e.year = s.year
  AND LOWER(e.season) = s.season
  AND e.session_id IS NULL;
