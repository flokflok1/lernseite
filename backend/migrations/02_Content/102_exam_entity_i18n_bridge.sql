-- Migration: Bridge exam entity display_names into the i18n system
-- Seeds exam types and regions as i18n keys so they appear on the Languages page
-- and are automatically included in the i18n bundle API.

-- 1. Create 'exams' namespace
INSERT INTO translations.i18n_namespaces (namespace_code, name, description)
VALUES ('exams', 'Exams', 'Exam types and regions')
ON CONFLICT (namespace_code) DO NOTHING;

-- 2. Exam Types as i18n keys (key pattern: exams.types.<exam_type>)
INSERT INTO translations.i18n_keys (namespace_code, key_path, default_value)
SELECT 'exams', 'exams.types.' || exam_type, display_name->>'de'
FROM assessments.exam_type_registry
ON CONFLICT (namespace_code, key_path)
  DO UPDATE SET default_value = EXCLUDED.default_value;

-- 3. Exam Regions as i18n keys (key pattern: exams.regions.<region_code>)
INSERT INTO translations.i18n_keys (namespace_code, key_path, default_value)
SELECT 'exams', 'exams.regions.' || region_code, display_name->>'de'
FROM assessments.exam_regions
ON CONFLICT (namespace_code, key_path)
  DO UPDATE SET default_value = EXCLUDED.default_value;

-- 4. Seed translations for all active languages (Exam Types)
INSERT INTO translations.i18n_translations (key_id, language_code, translated_value, translation_source)
SELECT k.key_id, lang.code, r.display_name->>lang.code, 'imported'
FROM assessments.exam_type_registry r
JOIN translations.i18n_keys k
  ON k.key_path = 'exams.types.' || r.exam_type AND k.namespace_code = 'exams'
CROSS JOIN (
  SELECT language_code AS code
  FROM translations.supported_languages
  WHERE is_active = true
) lang
WHERE r.display_name->>lang.code IS NOT NULL
ON CONFLICT (key_id, language_code)
  DO UPDATE SET translated_value = EXCLUDED.translated_value;

-- 5. Seed translations for all active languages (Exam Regions)
INSERT INTO translations.i18n_translations (key_id, language_code, translated_value, translation_source)
SELECT k.key_id, lang.code, r.display_name->>lang.code, 'imported'
FROM assessments.exam_regions r
JOIN translations.i18n_keys k
  ON k.key_path = 'exams.regions.' || r.region_code AND k.namespace_code = 'exams'
CROSS JOIN (
  SELECT language_code AS code
  FROM translations.supported_languages
  WHERE is_active = true
) lang
WHERE r.display_name->>lang.code IS NOT NULL
ON CONFLICT (key_id, language_code)
  DO UPDATE SET translated_value = EXCLUDED.translated_value;
