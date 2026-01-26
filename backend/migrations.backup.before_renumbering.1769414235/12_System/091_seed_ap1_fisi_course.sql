-- ============================================================================
-- Migration: 091_seed_ap1_fisi_course.sql
-- Description: Seed data for AP1 FISI Pruefungsvorbereitung course
-- Phase: 4 (Seeds - all INSERT statements after table creation)
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-01-25
-- ============================================================================

-- Variablen
\set creator_id 'e4ac9965-e3d2-42b9-9703-3f1c0f4adedc'

-- ============================================================
-- 1. KURS ERSTELLEN
-- ============================================================

INSERT INTO courses (
    course_id,
    creator_user_id,
    course_type,
    title,
    slug,
    description,
    long_description,
    category,
    level,
    language_default,
    duration_hours,
    tags,
    is_published,
    is_public,
    status,
    learning_goals,
    target_audience
) VALUES (
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    :'creator_id',
    'academy',
    'AP1 Pruefungsvorbereitung - FISI Baden-Wuerttemberg',
    'ap1-fisi-bw',
    'Komplette Vorbereitung auf die Abschlusspruefung Teil 1 (AP1) fuer Fachinformatiker Systemintegration. Basierend auf Original-IHK-Pruefungen 2022-2024.',
    E'Dieser Kurs bereitet dich optimal auf die AP1 vor. Er deckt alle pruefungsrelevanten Themen ab:\n\n• IT 1: Unternehmen & Beschaffung (30 Punkte)\n• IT 2: Programmierung (15 Punkte)\n• IT 3: Datenbanken & SQL (15 Punkte)\n• IT 4: Netzwerk & IT-Sicherheit (30 Punkte)\n\nMit Original-Pruefungsaufgaben und 90-Minuten-Simulationen.',
    'IT-Ausbildung',
    'intermediate',
    'de',
    40,
    ARRAY['AP1', 'FISI', 'IHK', 'Fachinformatiker', 'Pruefungsvorbereitung', 'Baden-Wuerttemberg', 'Systemintegration'],
    false,
    true,
    'draft',
    ARRAY[
        'Handelskalkulation sicher beherrschen',
        'Subnetting (IPv4) fehlerfrei berechnen',
        'SQL-Abfragen schreiben und Fehler finden',
        'Schutzbedarfsanalyse durchfuehren',
        'ERM und Relationenmodelle erstellen',
        '90-Minuten-Pruefung unter Zeitdruck bestehen'
    ],
    'Auszubildende zum Fachinformatiker Systemintegration (FISI) in der Pruefungsvorbereitung auf AP1'
) ON CONFLICT DO NOTHING;

-- ============================================================
-- 2. MODULE (CHAPTERS) ERSTELLEN
-- ============================================================

-- Modul 1: Unternehmen & Beschaffung
INSERT INTO chapters (chapter_id, course_id, title, slug, description, order_index, duration_minutes, has_quiz, has_exam)
VALUES (
    '11111111-1111-1111-1111-111111111111',
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    'Modul 1: Unternehmen & Beschaffung',
    'modul-1-beschaffung',
    'Organisationsformen, Rechtsformen, Handelskalkulation, Angebotsvergleich, SLA/ITIL. Ca. 30 Punkte in der Pruefung.',
    0,
    480,
    true,
    true
) ON CONFLICT DO NOTHING;

-- Modul 2: IT-Sicherheit
INSERT INTO chapters (chapter_id, course_id, title, slug, description, order_index, duration_minutes, has_quiz, has_exam)
VALUES (
    '22222222-2222-2222-2222-222222222222',
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    'Modul 2: IT-Sicherheit',
    'modul-2-it-sicherheit',
    'Schutzziele (CIA), Schutzbedarfsanalyse, WLAN-Sicherheit, Bedrohungen & Massnahmen. Ca. 15 Punkte in der Pruefung.',
    1,
    300,
    true,
    true
) ON CONFLICT DO NOTHING;

-- Modul 3: Netzwerktechnik (HAUPTMODUL)
INSERT INTO chapters (chapter_id, course_id, title, slug, description, order_index, duration_minutes, has_quiz, has_exam)
VALUES (
    '33333333-3333-3333-3333-333333333333',
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    'Modul 3: Netzwerktechnik',
    'modul-3-netzwerk',
    'OSI-Modell, IPv4-Subnetting, IPv6, DHCP, DNS, WLAN-Standards, Netzwerkkomponenten. KERNMODUL - ca. 30 Punkte!',
    2,
    720,
    true,
    true
) ON CONFLICT DO NOTHING;

-- Modul 4: Datenbanken
INSERT INTO chapters (chapter_id, course_id, title, slug, description, order_index, duration_minutes, has_quiz, has_exam)
VALUES (
    '44444444-4444-4444-4444-444444444444',
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    'Modul 4: Datenbanken & SQL',
    'modul-4-datenbanken',
    'Datenformate, ERM, Kardinalitaeten, Relationenmodell, SQL (SELECT, INSERT, DELETE, CREATE). Ca. 15 Punkte.',
    3,
    420,
    true,
    true
) ON CONFLICT DO NOTHING;

-- Modul 5: Programmierung
INSERT INTO chapters (chapter_id, course_id, title, slug, description, order_index, duration_minutes, has_quiz, has_exam)
VALUES (
    '55555555-5555-5555-5555-555555555555',
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    'Modul 5: Programmierung',
    'modul-5-programmierung',
    'Kontrollstrukturen, Struktogramme, Pseudocode, Fehler in Code finden. Ca. 15 Punkte.',
    4,
    240,
    true,
    true
) ON CONFLICT DO NOTHING;

-- Modul 6: Pruefungsvorbereitung
INSERT INTO chapters (chapter_id, course_id, title, slug, description, order_index, duration_minutes, has_quiz, has_exam)
VALUES (
    '66666666-6666-6666-6666-666666666666',
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    'Modul 6: Pruefungsvorbereitung',
    'modul-6-pruefung',
    'Zeitmanagement, Original-Pruefungen 2022-2024, Finale Generalprobe unter echten Bedingungen.',
    5,
    360,
    false,
    true
) ON CONFLICT DO NOTHING;

-- ============================================================
-- 3. LEKTIONEN ERSTELLEN
-- ============================================================

-- ============================================================
-- MODUL 1: Unternehmen & Beschaffung (10 Lektionen)
-- ============================================================

INSERT INTO lessons (chapter_id, title, slug, lesson_type, order_index, duration_minutes, content) VALUES
('11111111-1111-1111-1111-111111111111', '1.1 Organisationsformen Einfuehrung', 'organisationsformen-einfuehrung', 'text', 0, 30,
 '{"lm_primary": "LM00", "lm_secondary": null, "topic": "Einlinien-, Mehrlinien-, Matrixorganisation", "pruefungs_relevanz": "mittel"}'),

('11111111-1111-1111-1111-111111111111', '1.2 Organisationsformen Uebung', 'organisationsformen-uebung', 'interactive', 1, 25,
 '{"lm_primary": "LM14", "lm_secondary": "LM22", "topic": "Organigramme zuordnen, MC-Fragen", "pruefungs_relevanz": "mittel"}'),

('11111111-1111-1111-1111-111111111111', '1.3 Rechtsformen im Ueberblick', 'rechtsformen-ueberblick', 'interactive', 2, 30,
 '{"lm_primary": "LM13", "lm_secondary": null, "topic": "GmbH, KG, GbR, Einzelunternehmen - Vor/Nachteile", "pruefungs_relevanz": "mittel"}'),

('11111111-1111-1111-1111-111111111111', '1.4 Rechtsformen Pruefungsaufgaben', 'rechtsformen-pruefung', 'interactive', 3, 35,
 '{"lm_primary": "LM19", "lm_secondary": null, "topic": "Situationsaufgabe: Firmengruendung", "pruefungs_relevanz": "mittel"}'),

('11111111-1111-1111-1111-111111111111', '1.5 Handelskalkulation Theorie', 'handelskalkulation-theorie', 'text', 4, 45,
 '{"lm_primary": "LM00", "lm_secondary": "LM01", "topic": "Bezugs- und Verkaufskalkulation Schema", "pruefungs_relevanz": "SEHR HOCH"}'),

('11111111-1111-1111-1111-111111111111', '1.6 Bezugskalkulation Uebung', 'bezugskalkulation-uebung', 'interactive', 5, 50,
 '{"lm_primary": "LM12", "lm_secondary": null, "topic": "Listeneinkaufspreis -> Bezugspreis rechnen", "pruefungs_relevanz": "SEHR HOCH"}'),

('11111111-1111-1111-1111-111111111111', '1.7 Verkaufskalkulation Uebung', 'verkaufskalkulation-uebung', 'interactive', 6, 50,
 '{"lm_primary": "LM12", "lm_secondary": null, "topic": "Bezugspreis -> Listenverkaufspreis rechnen", "pruefungs_relevanz": "SEHR HOCH"}'),

('11111111-1111-1111-1111-111111111111', '1.8 Handelskalkulation IHK-Aufgaben', 'handelskalkulation-ihk', 'interactive', 7, 60,
 '{"lm_primary": "LM19", "lm_secondary": null, "topic": "Original-Pruefungsaufgaben Handelskalkulation", "pruefungs_relevanz": "SEHR HOCH"}'),

('11111111-1111-1111-1111-111111111111', '1.9 SLA & ITIL-Begriffe', 'sla-itil', 'interactive', 8, 30,
 '{"lm_primary": "LM13", "lm_secondary": "LM15", "topic": "Event, Incident, Service Request", "pruefungs_relevanz": "niedrig"}'),

('11111111-1111-1111-1111-111111111111', '1.10 Modul-Pruefung Beschaffung', 'modul-pruefung-beschaffung', 'quiz', 9, 45,
 '{"lm_primary": "LM25", "lm_secondary": null, "topic": "30 Punkte Simulation IT1", "pruefungs_relevanz": "SEHR HOCH"}')
ON CONFLICT DO NOTHING;

-- ============================================================
-- MODUL 2: IT-Sicherheit (7 Lektionen)
-- ============================================================

INSERT INTO lessons (chapter_id, title, slug, lesson_type, order_index, duration_minutes, content) VALUES
('22222222-2222-2222-2222-222222222222', '2.1 Schutzziele (CIA-Triade)', 'schutzziele-cia', 'text', 0, 30,
 '{"lm_primary": "LM00", "lm_secondary": "LM13", "topic": "Vertraulichkeit, Integritaet, Verfuegbarkeit", "pruefungs_relevanz": "HOCH"}'),

('22222222-2222-2222-2222-222222222222', '2.2 Schutzbedarfskategorien', 'schutzbedarfskategorien', 'text', 1, 35,
 '{"lm_primary": "LM00", "lm_secondary": null, "topic": "normal, hoch, sehr hoch + Maximumprinzip", "pruefungs_relevanz": "HOCH"}'),

('22222222-2222-2222-2222-222222222222', '2.3 Schutzbedarfsanalyse Uebung', 'schutzbedarfsanalyse-uebung', 'interactive', 2, 50,
 '{"lm_primary": "LM11", "lm_secondary": null, "topic": "Tabelle ausfuellen mit Begruendung", "pruefungs_relevanz": "HOCH"}'),

('22222222-2222-2222-2222-222222222222', '2.4 Schutzbedarfsanalyse IHK', 'schutzbedarfsanalyse-ihk', 'interactive', 3, 45,
 '{"lm_primary": "LM19", "lm_secondary": null, "topic": "Original-Pruefungsaufgabe nachstellen", "pruefungs_relevanz": "HOCH"}'),

('22222222-2222-2222-2222-222222222222', '2.5 WLAN-Sicherheit', 'wlan-sicherheit', 'interactive', 4, 35,
 '{"lm_primary": "LM14", "lm_secondary": "LM22", "topic": "WEP, WPA2, WPA3 Zuordnung", "pruefungs_relevanz": "mittel"}'),

('22222222-2222-2222-2222-222222222222', '2.6 Bedrohungen & Massnahmen', 'bedrohungen-massnahmen', 'interactive', 5, 40,
 '{"lm_primary": "LM22", "lm_secondary": "LM11", "topic": "Ransomware, Phishing, Firewall, DMZ", "pruefungs_relevanz": "mittel"}'),

('22222222-2222-2222-2222-222222222222', '2.7 Modul-Pruefung IT-Sicherheit', 'modul-pruefung-sicherheit', 'quiz', 6, 30,
 '{"lm_primary": "LM25", "lm_secondary": null, "topic": "15 Punkte Simulation IT2", "pruefungs_relevanz": "HOCH"}')
ON CONFLICT DO NOTHING;

-- ============================================================
-- MODUL 3: Netzwerktechnik (15 Lektionen) - HAUPTMODUL
-- ============================================================

INSERT INTO lessons (chapter_id, title, slug, lesson_type, order_index, duration_minutes, content) VALUES
('33333333-3333-3333-3333-333333333333', '3.1 OSI-Modell Grundlagen', 'osi-modell-grundlagen', 'text', 0, 40,
 '{"lm_primary": "LM00", "lm_secondary": null, "topic": "7 Schichten, Protokolle pro Schicht", "pruefungs_relevanz": "mittel"}'),

('33333333-3333-3333-3333-333333333333', '3.2 OSI-Modell Uebung', 'osi-modell-uebung', 'interactive', 1, 30,
 '{"lm_primary": "LM14", "lm_secondary": null, "topic": "Schichten zuordnen, MAC/IP einordnen", "pruefungs_relevanz": "mittel"}'),

('33333333-3333-3333-3333-333333333333', '3.3 IPv4-Adressierung Basics', 'ipv4-basics', 'text', 2, 40,
 '{"lm_primary": "LM00", "lm_secondary": "LM03", "topic": "Aufbau, Klassen, private/oeffentliche Adressen", "pruefungs_relevanz": "HOCH"}'),

('33333333-3333-3333-3333-333333333333', '3.4 Subnetting Theorie', 'subnetting-theorie', 'text', 3, 50,
 '{"lm_primary": "LM00", "lm_secondary": null, "topic": "CIDR, Subnetzmaske, binaere Rechnung", "pruefungs_relevanz": "SEHR HOCH"}'),

('33333333-3333-3333-3333-333333333333', '3.5 Subnetting: Netzwerkadresse', 'subnetting-netzwerkadresse', 'interactive', 4, 50,
 '{"lm_primary": "LM12", "lm_secondary": null, "topic": "Netzwerkadresse berechnen mit Feedback", "pruefungs_relevanz": "SEHR HOCH"}'),

('33333333-3333-3333-3333-333333333333', '3.6 Subnetting: Broadcast & Hosts', 'subnetting-broadcast-hosts', 'interactive', 5, 50,
 '{"lm_primary": "LM12", "lm_secondary": null, "topic": "Broadcastadresse, Hostbereich berechnen", "pruefungs_relevanz": "SEHR HOCH"}'),

('33333333-3333-3333-3333-333333333333', '3.7 Subnetting: CIDR-Notation', 'subnetting-cidr', 'interactive', 6, 45,
 '{"lm_primary": "LM12", "lm_secondary": "LM10", "topic": "/24, /25, /26 etc. anwenden", "pruefungs_relevanz": "SEHR HOCH"}'),

('33333333-3333-3333-3333-333333333333', '3.8 Subnetting IHK-Aufgaben', 'subnetting-ihk', 'interactive', 7, 60,
 '{"lm_primary": "LM19", "lm_secondary": null, "topic": "Original-Pruefungsaufgaben Subnetting", "pruefungs_relevanz": "SEHR HOCH"}'),

('33333333-3333-3333-3333-333333333333', '3.9 IPv6-Grundlagen', 'ipv6-grundlagen', 'text', 8, 35,
 '{"lm_primary": "LM00", "lm_secondary": "LM13", "topic": "Adressaufbau, Kuerzungsregeln", "pruefungs_relevanz": "mittel"}'),

('33333333-3333-3333-3333-333333333333', '3.10 IPv6-Adresstypen', 'ipv6-adresstypen', 'interactive', 9, 30,
 '{"lm_primary": "LM14", "lm_secondary": "LM22", "topic": "Global, Link-Local, Temporary", "pruefungs_relevanz": "mittel"}'),

('33333333-3333-3333-3333-333333333333', '3.11 DHCP (DORA-Prozess)', 'dhcp-dora', 'interactive', 10, 40,
 '{"lm_primary": "LM14", "lm_secondary": "LM00", "topic": "Discover -> Offer -> Request -> Acknowledge", "pruefungs_relevanz": "mittel"}'),

('33333333-3333-3333-3333-333333333333', '3.12 DNS-Grundlagen', 'dns-grundlagen', 'text', 11, 25,
 '{"lm_primary": "LM00", "lm_secondary": "LM15", "topic": "Namensaufloesung erklaeren", "pruefungs_relevanz": "niedrig"}'),

('33333333-3333-3333-3333-333333333333', '3.13 WLAN-Standards (802.11)', 'wlan-standards', 'interactive', 12, 35,
 '{"lm_primary": "LM13", "lm_secondary": "LM22", "topic": "a/b/g/n/ac/ax, 2.4/5 GHz Eigenschaften", "pruefungs_relevanz": "mittel"}'),

('33333333-3333-3333-3333-333333333333', '3.14 Netzwerkplaene & Komponenten', 'netzwerkplaene-komponenten', 'interactive', 13, 45,
 '{"lm_primary": "LM10", "lm_secondary": "LM03", "topic": "Router, Switch, AP, Firewall, PoE", "pruefungs_relevanz": "mittel"}'),

('33333333-3333-3333-3333-333333333333', '3.15 Modul-Pruefung Netzwerk', 'modul-pruefung-netzwerk', 'quiz', 14, 45,
 '{"lm_primary": "LM25", "lm_secondary": null, "topic": "30 Punkte Simulation IT3+IT4", "pruefungs_relevanz": "SEHR HOCH"}')
ON CONFLICT DO NOTHING;

-- ============================================================
-- MODUL 4: Datenbanken (10 Lektionen)
-- ============================================================

INSERT INTO lessons (chapter_id, title, slug, lesson_type, order_index, duration_minutes, content) VALUES
('44444444-4444-4444-4444-444444444444', '4.1 Datenformate Ueberblick', 'datenformate-ueberblick', 'interactive', 0, 25,
 '{"lm_primary": "LM14", "lm_secondary": "LM22", "topic": "CSV, XML, JSON unterscheiden", "pruefungs_relevanz": "niedrig"}'),

('44444444-4444-4444-4444-444444444444', '4.2 ERM-Grundlagen', 'erm-grundlagen', 'text', 1, 40,
 '{"lm_primary": "LM00", "lm_secondary": "LM03", "topic": "Entitaeten, Attribute, Beziehungen", "pruefungs_relevanz": "HOCH"}'),

('44444444-4444-4444-4444-444444444444', '4.3 Kardinalitaeten', 'kardinalitaeten', 'interactive', 2, 30,
 '{"lm_primary": "LM14", "lm_secondary": null, "topic": "1:1, 1:n, m:n zuordnen", "pruefungs_relevanz": "HOCH"}'),

('44444444-4444-4444-4444-444444444444', '4.4 ERM erstellen & erweitern', 'erm-erstellen', 'interactive', 3, 45,
 '{"lm_primary": "LM19", "lm_secondary": null, "topic": "Kardinalitaeten einzeichnen - IHK-Stil", "pruefungs_relevanz": "HOCH"}'),

('44444444-4444-4444-4444-444444444444', '4.5 Relationenmodell', 'relationenmodell', 'interactive', 4, 40,
 '{"lm_primary": "LM19", "lm_secondary": "LM00", "topic": "Schema aus ERM ableiten", "pruefungs_relevanz": "HOCH"}'),

('44444444-4444-4444-4444-444444444444', '4.6 SQL-Grundlagen (SELECT)', 'sql-select', 'interactive', 5, 50,
 '{"lm_primary": "LM09", "lm_secondary": null, "topic": "SELECT, WHERE, ORDER BY", "pruefungs_relevanz": "HOCH"}'),

('44444444-4444-4444-4444-444444444444', '4.7 SQL erweitert', 'sql-erweitert', 'interactive', 6, 45,
 '{"lm_primary": "LM09", "lm_secondary": null, "topic": "INSERT, DELETE, CREATE TABLE", "pruefungs_relevanz": "mittel"}'),

('44444444-4444-4444-4444-444444444444', '4.8 SQL Aggregatfunktionen', 'sql-aggregat', 'interactive', 7, 40,
 '{"lm_primary": "LM09", "lm_secondary": null, "topic": "COUNT, SUM, AVG, GROUP BY", "pruefungs_relevanz": "mittel"}'),

('44444444-4444-4444-4444-444444444444', '4.9 SQL-Fehleranalyse', 'sql-fehleranalyse', 'interactive', 8, 45,
 '{"lm_primary": "LM16", "lm_secondary": null, "topic": "Syntaxfehler finden und korrigieren", "pruefungs_relevanz": "HOCH"}'),

('44444444-4444-4444-4444-444444444444', '4.10 Modul-Pruefung Datenbank', 'modul-pruefung-datenbank', 'quiz', 9, 35,
 '{"lm_primary": "LM25", "lm_secondary": null, "topic": "15 Punkte Simulation IT3", "pruefungs_relevanz": "HOCH"}')
ON CONFLICT DO NOTHING;

-- ============================================================
-- MODUL 5: Programmierung (6 Lektionen)
-- ============================================================

INSERT INTO lessons (chapter_id, title, slug, lesson_type, order_index, duration_minutes, content) VALUES
('55555555-5555-5555-5555-555555555555', '5.1 Kontrollstrukturen Theorie', 'kontrollstrukturen-theorie', 'text', 0, 35,
 '{"lm_primary": "LM00", "lm_secondary": null, "topic": "Schleifen (for, while), if/else", "pruefungs_relevanz": "mittel"}'),

('55555555-5555-5555-5555-555555555555', '5.2 Kontrollstrukturen Uebung', 'kontrollstrukturen-uebung', 'interactive', 1, 45,
 '{"lm_primary": "LM09", "lm_secondary": null, "topic": "Schleifen implementieren", "pruefungs_relevanz": "mittel"}'),

('55555555-5555-5555-5555-555555555555', '5.3 Struktogramme (Nassi-Shneiderman)', 'struktogramme', 'interactive', 2, 35,
 '{"lm_primary": "LM14", "lm_secondary": "LM03", "topic": "Symbole verstehen, zuordnen", "pruefungs_relevanz": "mittel"}'),

('55555555-5555-5555-5555-555555555555', '5.4 Pseudocode & Implementierung', 'pseudocode-implementierung', 'interactive', 3, 45,
 '{"lm_primary": "LM09", "lm_secondary": null, "topic": "Struktogramm -> Code umsetzen", "pruefungs_relevanz": "mittel"}'),

('55555555-5555-5555-5555-555555555555', '5.5 Fehler in Code finden', 'code-fehler-finden', 'interactive', 4, 40,
 '{"lm_primary": "LM16", "lm_secondary": null, "topic": "Logik- und Syntaxfehler erkennen", "pruefungs_relevanz": "HOCH"}'),

('55555555-5555-5555-5555-555555555555', '5.6 Modul-Pruefung Programmierung', 'modul-pruefung-programmierung', 'quiz', 5, 30,
 '{"lm_primary": "LM25", "lm_secondary": null, "topic": "15 Punkte Simulation IT2", "pruefungs_relevanz": "mittel"}')
ON CONFLICT DO NOTHING;

-- ============================================================
-- MODUL 6: Pruefungsvorbereitung (5 Lektionen)
-- ============================================================

INSERT INTO lessons (chapter_id, title, slug, lesson_type, order_index, duration_minutes, content) VALUES
('66666666-6666-6666-6666-666666666666', '6.1 Zeitmanagement-Strategie', 'zeitmanagement-strategie', 'text', 0, 30,
 '{"lm_primary": "LM00", "lm_secondary": "LM22", "topic": "90 Min optimal aufteilen", "pruefungs_relevanz": "HOCH"}'),

('66666666-6666-6666-6666-666666666666', '6.2 Original-Pruefung 2022', 'original-pruefung-2022', 'interactive', 1, 90,
 '{"lm_primary": "LM21", "lm_secondary": "LM19", "topic": "Vollstaendige AP1 2022 unter Zeitdruck", "pruefungs_relevanz": "SEHR HOCH"}'),

('66666666-6666-6666-6666-666666666666', '6.3 Original-Pruefung 2023', 'original-pruefung-2023', 'interactive', 2, 90,
 '{"lm_primary": "LM21", "lm_secondary": "LM19", "topic": "Vollstaendige AP1 2023 unter Zeitdruck", "pruefungs_relevanz": "SEHR HOCH"}'),

('66666666-6666-6666-6666-666666666666', '6.4 Original-Pruefung 2024', 'original-pruefung-2024', 'interactive', 3, 90,
 '{"lm_primary": "LM21", "lm_secondary": "LM19", "topic": "Vollstaendige AP1 2024 (4 Aufgaben neu!)", "pruefungs_relevanz": "SEHR HOCH"}'),

('66666666-6666-6666-6666-666666666666', '6.5 Finale Generalprobe', 'finale-generalprobe', 'quiz', 4, 90,
 '{"lm_primary": "LM21", "lm_secondary": "LM25", "topic": "Abschlusspruefung des Kurses - 90 Min", "pruefungs_relevanz": "SEHR HOCH"}')
ON CONFLICT DO NOTHING;

-- ============================================================
-- ZUSAMMENFASSUNG
-- ============================================================
-- Kurs: AP1 Pruefungsvorbereitung - FISI Baden-Wuerttemberg
-- Module: 6
-- Lektionen: 53
-- Gesamtdauer: ~40 Stunden
-- ============================================================

SELECT 'Kurs-Grundgeruest erfolgreich erstellt!' AS status;
SELECT
    (SELECT COUNT(*) FROM chapters WHERE course_id = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890') AS module_count,
    (SELECT COUNT(*) FROM lessons WHERE chapter_id IN (
        SELECT chapter_id FROM chapters WHERE course_id = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
    )) AS lesson_count;
