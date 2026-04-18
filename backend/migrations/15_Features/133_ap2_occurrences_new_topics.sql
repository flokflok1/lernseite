-- ============================================================================
-- Migration: 133_ap2_occurrences_new_topics.sql
-- Description: Seed exam-occurrences für neue Topics (raid-backup,
--              disaster-recovery), damit die "X/5 Prüfungen"-Anzeige im
--              Frontend korrekte Werte zeigt statt 0/5.
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-04-18
-- ============================================================================

WITH topic_lookup AS (
    SELECT slug, topic_id FROM assessments.ap2_topics
)
INSERT INTO assessments.ap2_topic_exam_occurrences
    (topic_id, exam_term, bereich, aufgabe_nummer, points, notes)
SELECT t.topic_id, v.exam_term, v.bereich, v.aufgabe_nummer, v.points, v.notes
FROM (VALUES
-- RAID & Backup — Klassiker, in fast jeder AP2 (5/5)
('raid-backup', 'S2022', 'PB3', '3.2', 12, 'RAID-Kapazität + Backup-Konzept'),
('raid-backup', 'W2022', 'PB3', '2.4', 14, 'RAID 5 vs 10, 3-2-1-Regel'),
('raid-backup', 'S2023', 'PB3', '4.1', 15, 'RAID-Level-Wahl für Serverraum'),
('raid-backup', 'W2023', 'PB3', '3.3', 13, 'RAID ersetzt kein Backup + GFS'),
('raid-backup', 'S2024', 'PB3', '2.2', 15, 'Hochverfügbarkeit mit RAID 10'),

-- Disaster Recovery (RTO/RPO) — kommt in BW etwa 3/5
('disaster-recovery', 'W2022', 'PB3', '2.5', 6, 'RTO/RPO für SLA-Definition'),
('disaster-recovery', 'S2023', 'PB3', '4.2', 8, 'DR-Konzept für Webshop'),
('disaster-recovery', 'S2024', 'PB3', '2.3', 8, 'BIA + Recovery-Planung')

) AS v(slug, exam_term, bereich, aufgabe_nummer, points, notes)
JOIN topic_lookup t ON t.slug = v.slug
ON CONFLICT DO NOTHING;

-- Update exam_count für die beiden Topics auf Basis der Occurrences
UPDATE assessments.ap2_topics t
SET exam_count = (
    SELECT count(DISTINCT exam_term)
    FROM assessments.ap2_topic_exam_occurrences o
    WHERE o.topic_id = t.topic_id
)
WHERE t.slug IN ('raid-backup', 'disaster-recovery');

COMMIT;
