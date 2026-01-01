-- ============================================================================
-- Migration 068: Umstellung auf 19 Content-Lernmethoden
-- ============================================================================
--
-- Referenz: 02_Lernmethoden.md (Master-Dokument)
--           02a_System-Features.md (System-Features)
--
-- Aktive Content-Lernmethoden (19 Methoden in 3 Gruppen):
-- - Gruppe A (Erklärend): LM00, LM01, LM02, LM03, LM06 - 5 Methoden
-- - Gruppe B (Praxis):    LM08, LM12, LM13, LM14, LM15, LM17 - 6 Methoden
-- - Gruppe C (Prüfung):   LM18-LM25 - 8 Methoden
--
-- System-Features (frühere LMs, jetzt eigenständige Features):
-- - LM04: Sokratischer Dialog → TutorAgent / Pro-Feature
-- - LM05: Mindmap-Generator → CourseFeatures.mindmap
-- - LM07: NPC-Tutor-Lecture → TutorAgent
-- - LM09-LM11, LM16: IT-Sandboxes → System-Feature IT-Umgebungen
-- - LM26-LM32: Kollaborative Methoden → System-Features Kollaboration
--
-- Diese Migration markiert System-Features als inaktiv und aktualisiert
-- die Gruppenzuordnung entsprechend der neuen Struktur.
--
-- WICHTIG: Das Constraint bleibt bei 0-31 für Abwärtskompatibilität mit
-- existierenden Daten. Neue Instanzen sollten nur 19 Content-LMs nutzen.
--
-- ============================================================================

-- ============================================================================
-- 1. System-Features als inaktiv markieren
-- ============================================================================

-- LM04: Sokratischer Dialog (früher Gruppe D, jetzt TutorAgent)
UPDATE learning_method_types
SET active = FALSE,
    description = '[SYSTEM-FEATURE] Sokratischer Dialog - verschoben zu TutorAgent'
WHERE method_number = 4;

-- LM05: Mindmap-Generator (früher Gruppe A, jetzt CourseFeatures)
UPDATE learning_method_types
SET active = FALSE,
    description = '[SYSTEM-FEATURE] Mindmap-Generator - verschoben zu CourseFeatures.mindmap'
WHERE method_number = 5;

-- LM07: NPC-Tutor-Lecture (früher Gruppe A, jetzt TutorAgent)
UPDATE learning_method_types
SET active = FALSE,
    description = '[SYSTEM-FEATURE] NPC-Tutor-Lecture - verschoben zu TutorAgent'
WHERE method_number = 7;

-- LM09-LM11, LM16: IT-Sandboxes (früher Gruppe B/E, jetzt IT-Umgebungen)
UPDATE learning_method_types
SET active = FALSE,
    description = '[SYSTEM-FEATURE] ' || name || ' - verschoben zu System-Feature IT-Umgebungen'
WHERE method_number IN (9, 10, 11, 16);

-- LM26-LM32: Kollaborative Methoden (früher Gruppe D/F, jetzt Kollaboration)
UPDATE learning_method_types
SET active = FALSE,
    description = '[SYSTEM-FEATURE] ' || name || ' - verschoben zu System-Features Kollaboration'
WHERE method_number >= 26 AND method_number <= 32;

-- ============================================================================
-- 2. Gruppenzuordnung für Content-LMs bestätigen
-- ============================================================================

-- Sicherstellen, dass aktive Content-LMs korrekte Gruppe haben
UPDATE learning_method_types
SET group_code = 'A'
WHERE method_number IN (0, 1, 2, 3, 6) AND active = TRUE;

UPDATE learning_method_types
SET group_code = 'B'
WHERE method_number IN (8, 12, 13, 14, 15, 17) AND active = TRUE;

UPDATE learning_method_types
SET group_code = 'C'
WHERE method_number BETWEEN 18 AND 25 AND active = TRUE;

-- ============================================================================
-- 3. Tabellen-Kommentar aktualisieren
-- ============================================================================

COMMENT ON TABLE learning_method_types IS
'Lernmethoden-Typen: 19 Content-Lernmethoden (aktiv) + 14 System-Features (inaktiv).
Aktive Content-LMs:
- Gruppe A (Erklärend): LM00, LM01, LM02, LM03, LM06
- Gruppe B (Praxis): LM08, LM12, LM13, LM14, LM15, LM17
- Gruppe C (Prüfung): LM18-LM25
System-Features (inaktiv, eigenständige Module):
- LM04, LM05, LM07, LM09-LM11, LM16, LM26-LM32
Referenz: 02_Lernmethoden.md, 02a_System-Features.md
Migration 068 - Stand: 2025-12';

-- ============================================================================
-- 4. View für aktive Content-LMs erstellen
-- ============================================================================

CREATE OR REPLACE VIEW v_content_learning_methods AS
SELECT
    type_id,
    method_number,
    name,
    group_code,
    description,
    ki_usage,
    default_prompt_key,
    tier
FROM learning_method_types
WHERE active = TRUE
  AND method_number IN (0, 1, 2, 3, 6, 8, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 23, 24, 25)
ORDER BY method_number;

COMMENT ON VIEW v_content_learning_methods IS
'Aktive Content-Lernmethoden (19 Methoden).
Für neue Lektionen nur diese LMs verwenden.
System-Features (LM04, LM05, LM07, LM09-LM11, LM16, LM26-LM32)
werden über separate Module bereitgestellt.';

-- ============================================================================
-- 5. View für System-Features erstellen
-- ============================================================================

CREATE OR REPLACE VIEW v_system_features AS
SELECT
    type_id,
    method_number,
    name,
    description,
    CASE
        WHEN method_number = 4 THEN 'TutorAgent'
        WHEN method_number = 5 THEN 'CourseFeatures'
        WHEN method_number = 7 THEN 'TutorAgent'
        WHEN method_number IN (9, 10, 11, 16) THEN 'IT-Umgebungen'
        WHEN method_number >= 26 THEN 'Kollaboration'
        ELSE 'Sonstige'
    END AS feature_module,
    ki_usage
FROM learning_method_types
WHERE active = FALSE
  AND method_number IN (4, 5, 7, 9, 10, 11, 16, 26, 27, 28, 29, 30, 31, 32)
ORDER BY method_number;

COMMENT ON VIEW v_system_features IS
'System-Features (frühere LMs). Diese werden über eigenständige Module
bereitgestellt und sind keine Content-Lernmethoden mehr.
Referenz: 02a_System-Features.md';

-- ============================================================================
-- Migration 068 abgeschlossen
-- ============================================================================
