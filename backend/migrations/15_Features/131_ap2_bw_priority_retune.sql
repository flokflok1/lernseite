-- ============================================================================
-- Migration: 131_ap2_bw_priority_retune.sql
-- Description: Priority- und expected_points-Retuning für BW-spezifische
--              Gewichtung. Baden-Württemberg prüft als betriebswirtschaftlich
--              orientiertes Land andere Schwerpunkte als Bayern/NRW:
--              — Kalkulationen (Zuschlag, Handel) sind sehr-hoch statt hoch
--              — Wirtschaftsrecht (Rechtsformen, Vollmachten) sehr-hoch
--              — Aufbauorganisation (Organigramm) sehr-hoch (AP1-2026: 16P!)
--              — Nutzwertanalyse sehr-hoch (Standard-BW-Entscheidungsaufgabe)
--              Quelle: AP1-2026-BW-Analyse + BW-Prüfer-Verband-Statistiken
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-04-18
-- ============================================================================

-- Betriebswirtschaftliche Themen auf sehr-hoch + Points hochziehen
UPDATE assessments.ap2_topics
SET priority = 'sehr-hoch', expected_points = 14
WHERE slug = 'zuschlagskalkulation';

UPDATE assessments.ap2_topics
SET priority = 'sehr-hoch', expected_points = 12
WHERE slug = 'rechtsformen';

UPDATE assessments.ap2_topics
SET priority = 'sehr-hoch', expected_points = 16
WHERE slug = 'organigramm';

UPDATE assessments.ap2_topics
SET priority = 'sehr-hoch', expected_points = 10
WHERE slug = 'vollmachten';

UPDATE assessments.ap2_topics
SET priority = 'sehr-hoch', expected_points = 16
WHERE slug = 'nutzwertanalyse';

-- Schutzbedarf-BSI ist schon hoch, aber Punkte sind korrekt (24)
-- Projektmanagement von hoch → hoch lassen (BW fragt eher Nutzwertanalyse)

-- WISO-Schwerpunkte BW-konform
UPDATE assessments.ap2_topics
SET priority = 'sehr-hoch', expected_points = 12
WHERE slug = 'wiso-ausbildungsrecht';

UPDATE assessments.ap2_topics
SET priority = 'sehr-hoch', expected_points = 10
WHERE slug = 'wiso-marktformen';

UPDATE assessments.ap2_topics
SET priority = 'sehr-hoch', expected_points = 10
WHERE slug = 'wiso-rechtsgeschaeft';

UPDATE assessments.ap2_topics
SET priority = 'hoch', expected_points = 8
WHERE slug = 'wiso-wirtschaftspolitik';

-- Kaufvertrag-Mängelanspruch ist in BW SEHR populär
UPDATE assessments.ap2_topics
SET priority = 'sehr-hoch', expected_points = 10
WHERE slug = 'kaufvertrag';

-- MQTT und andere Rand-Tech bleiben mittel (BW fragt die selten)
-- VPN schon sehr-hoch (korrekt)

COMMIT;
