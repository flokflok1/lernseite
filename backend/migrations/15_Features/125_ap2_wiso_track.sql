-- ============================================================================
-- Migration: 125_ap2_wiso_track.sql
-- Description: WISO-Track für AP2 Mai 2026 (Prüfungstermin 11.05.).
--              Fügt 3 weitere WISO-Topics hinzu (Kaufvertrag, Marktformen,
--              Ausbildungsrecht), dann seeded alle 6 WISO-Topics mit
--              Blurt/Cued/Application-Items.
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-04-18
-- ============================================================================

-- ---------------------------------------------------------------------------
-- 1. Zusätzliche WISO-Topics
-- ---------------------------------------------------------------------------

INSERT INTO assessments.ap2_topics
    (slug, name_de, name_en, bereich, priority, expected_points, exam_count, description)
VALUES
    ('wiso-kaufvertrag',     'Kaufvertrag + Mängelrechte (BGB)',    'Sales Contract Law',    'WISO', 'sehr-hoch', 10, 5, 'Kaufvertragsabschluss, Mangelarten, Gewährleistung vs Garantie'),
    ('wiso-marktformen',     'Marktformen + Wettbewerb',            'Market Forms',          'WISO', 'hoch',       8, 4, 'Polypol, Oligopol, Monopol; vollkommen/unvollkommen; Preisbildung'),
    ('wiso-ausbildungsrecht','Ausbildungs- & Jugendarbeitsschutz',  'Apprenticeship Law',    'WISO', 'hoch',       8, 4, 'BBiG, JArbSchG, Ausbilder-/Azubi-Pflichten, Arbeitszeit, Prüfungen'),
    ('wiso-wirtschaftspolitik','Wirtschaftspolitik + Konjunktur',   'Economic Policy',       'WISO', 'mittel',     6, 3, 'Konjunkturphasen, EZB, Geldpolitik, Inflation, Magisches Viereck')
ON CONFLICT (slug) DO NOTHING;

-- ---------------------------------------------------------------------------
-- 2. WISO-Items seeden
-- ---------------------------------------------------------------------------

WITH topic_lookup AS (
    SELECT slug, topic_id FROM assessments.ap2_topics
)
INSERT INTO assessments.ap2_learning_items
    (topic_id, item_type, prompt, model_answer, expected_answer_structure,
     grading_criteria, points, source_exam, difficulty, estimated_time_sec)
SELECT t.topic_id, v.item_type, v.prompt, v.model_answer,
       v.expected_answer_structure::jsonb,
       v.grading_criteria::jsonb,
       v.points, v.source_exam, v.difficulty, v.estimated_time_sec
FROM (VALUES

-- ===== SOZIALVERSICHERUNG =====
('wiso-sozialversicherung', 'blurt',
 'Schreibe alles was du über die 5 Sozialversicherungszweige in Deutschland weißt: Kranken, Pflege, Renten, Arbeitslosen, Unfall. Wer zahlt, Beitragssätze, Leistungen.',
 'Die 5 Sozialversicherungen (Pflichtversicherungen ab Ausbildungsbeginn):\n\n1. Krankenversicherung (KV): AG + AN je hälftig (ca. 14,6 % + 1,3 % Zusatzbeitrag), Beitrag hälftig. Leistungen: Arzt, Medikamente, Krankenhaus, Krankengeld.\n2. Pflegeversicherung (PV): AG + AN hälftig (3,4 %, für Kinderlose ab 23: + 0,6 %). Leistungen bei Pflegebedürftigkeit (Pflegegrade 1-5).\n3. Rentenversicherung (RV): AG + AN hälftig (18,6 %). Leistungen: Altersrente, Erwerbsminderung, Hinterbliebene. BBG 2026 West 90.600 €, Ost 89.400 €.\n4. Arbeitslosenversicherung (AV): AG + AN hälftig (2,6 %). ALG I bei Arbeitslosigkeit (i.d.R. 60 %/67 %).\n5. Unfallversicherung (UV): nur AG zahlt. Zuständigkeit: Berufsgenossenschaft. Leistungen bei Arbeitsunfällen + Berufskrankheiten.\n\nBemessungsgrundlage: Bruttolohn bis zur Beitragsbemessungsgrenze (BBG). AN-Anteile werden direkt vom Lohn einbehalten.',
 '{"required_concepts": ["Krankenversicherung", "Pflegeversicherung", "Rentenversicherung", "Arbeitslosenversicherung", "Unfallversicherung", "AG + AN hälftig", "Unfall nur AG", "BBG", "Beitragssätze", "Berufsgenossenschaft"]}',
 '[{"criterion": "5 Zweige genannt", "weight": 3, "description": "Alle 5 Versicherungen", "required": true},
   {"criterion": "AG/AN-Aufteilung", "weight": 3, "description": "Wer zahlt jeweils", "required": true},
   {"criterion": "Leistungen", "weight": 2, "description": "Pro Zweig Hauptleistung", "required": true},
   {"criterion": "Beitragssätze", "weight": 2, "description": "Zahlen halbwegs korrekt", "required": false}]',
 10, 'ki-generated', 4, 600),

('wiso-sozialversicherung', 'cued',
 'Welche Sozialversicherung zahlt in Deutschland NUR der Arbeitgeber? Warum?',
 'Nur die Unfallversicherung (UV) wird vollständig vom Arbeitgeber getragen. Grund: Der AG haftet für Arbeitssicherheit am Arbeitsplatz. Zuständig sind die Berufsgenossenschaften (je Branche). Leistungen bei Arbeitsunfällen, Wegeunfällen (Hin-/Rückweg), anerkannten Berufskrankheiten.',
 '{"required_concepts": ["Unfallversicherung", "nur Arbeitgeber", "Berufsgenossenschaft", "Arbeitssicherheit", "Wegeunfall"]}',
 NULL, 2, 'ki-generated', 2, 90),

('wiso-sozialversicherung', 'cued',
 'Azubi Pascal verdient 1.200 € brutto. Berechne seinen AN-Anteil zur Krankenversicherung bei 14,6 % + 1,3 % Zusatzbeitrag (beide AG/AN hälftig).',
 'Gesamtbeitrag KV: 14,6 % + 1,3 % = 15,9 %\nAN-Anteil: 15,9 % / 2 = 7,95 %\n7,95 % von 1.200 € = 95,40 €\n\n→ Pascal zahlt 95,40 € AN-Anteil zur KV.',
 '{"required_concepts": ["15.9 %", "hälftig 7.95 %", "95.40", "1200 × 0.0795"]}',
 NULL, 2, 'ki-generated', 3, 120),

('wiso-sozialversicherung', 'cued',
 'Was bedeutet BBG (Beitragsbemessungsgrenze)? Was ist die Versicherungspflichtgrenze (Jahresarbeitsentgeltgrenze, JAEG)?',
 'BBG (Beitragsbemessungsgrenze): Das maximale Bruttoeinkommen, bis zu dem Beiträge berechnet werden. Einkommen DARÜBER wird nicht mehr verbeitragt.\n- KV/PV: ca. 66.150 € / Jahr (2026)\n- RV/AV (West): ca. 90.600 € / Jahr\n\nJAEG (Versicherungspflichtgrenze): Das Einkommen ab dem AN aus der gesetzlichen KV in die private KV wechseln DÜRFEN. Liegt höher als BBG — ca. 73.800 € / Jahr.',
 '{"required_concepts": ["BBG Maximum Beitrag", "JAEG Wechsel PKV", "höher als BBG", "Jahresentgelt"]}',
 NULL, 3, 'ki-generated', 4, 180),

('wiso-sozialversicherung', 'cued',
 'Nenne 3 Leistungen der gesetzlichen Rentenversicherung (RV).',
 '1. Altersrente (Regelaltersrente, vorzeitig mit Abschlag)\n2. Rente wegen Erwerbsminderung (teilweise/voll)\n3. Hinterbliebenenrente (Witwen/Witwer, Waisenrente)\n(Weitere: Rehabilitationsleistungen, Grundrente)',
 '{"required_concepts": ["Altersrente", "Erwerbsminderung", "Hinterbliebene"]}',
 NULL, 3, 'ki-generated', 3, 120),

('wiso-sozialversicherung', 'application',
 'Azubi-Gehalt 1.200 € brutto. Berechne ALLE AN-Anteile zur Sozialversicherung (KV 14,6 % + 1,3 % Zusatz, PV 3,4 %, RV 18,6 %, AV 2,6 %). Pascal ist 20 und kinderlos (+0,6 % PV-Zuschlag für Kinderlose ab 23 entfällt noch nicht). Gib Brutto-Abzug und Nettolohn ohne Steuern an.',
 'AN-Anteile (jeweils hälftig, Unfall fällt als AN-frei weg):\n\nKV: (14,6 + 1,3) / 2 = 7,95 % × 1.200 € = 95,40 €\nPV: 3,4 / 2 = 1,7 % × 1.200 € = 20,40 € (kinderlos <23 kein Zuschlag)\nRV: 18,6 / 2 = 9,3 % × 1.200 € = 111,60 €\nAV: 2,6 / 2 = 1,3 % × 1.200 € = 15,60 €\n\nGesamt AN-Anteil: 95,40 + 20,40 + 111,60 + 15,60 = 243,00 €\n\nNetto ohne Steuern: 1.200 − 243 = 957,00 €\n\n(AG zahlt zusätzlich gleichen Betrag + UV-Beitrag).',
 '{"required_concepts": ["KV 95.40", "PV 20.40", "RV 111.60", "AV 15.60", "243 Gesamt", "957 Netto"]}',
 '[{"criterion": "Alle 4 Beiträge", "weight": 4, "description": "KV/PV/RV/AV korrekt", "required": true},
   {"criterion": "Summe", "weight": 2, "description": "243 €", "required": true},
   {"criterion": "Netto-Berechnung", "weight": 2, "description": "1.200 − 243", "required": true}]',
 8, 'ki-generated', 4, 600),

-- ===== TARIFVERHANDLUNGEN + BETRIEBSRAT =====
('wiso-tarif', 'blurt',
 'Schreibe alles was du über Tarifverhandlungen, Tarifautonomie, Tarifvertragsarten und Betriebsrat / Mitbestimmung weißt.',
 'Tarifautonomie (Art. 9 GG): Gewerkschaften + Arbeitgeberverbände schließen Tarifverträge OHNE staatlichen Eingriff. Friedenspflicht während Laufzeit.\n\nTarifvertrag-Arten:\n- Manteltarifvertrag (MTV): langfristig, regelt Arbeitszeit, Urlaub, Kündigung, Eingruppierung.\n- Lohn-/Gehaltstarifvertrag: kurzfristig (meist 1-2 J), regelt Entgelte.\n- Firmentarifvertrag: nur für ein Unternehmen.\n- Flächentarifvertrag: für Branche + Region.\n\nEskalationsstufen Tarifkonflikt: Verhandlungen → Schlichtung → Urabstimmung (75 %) → Streik / Aussperrung → Schlichtungsspruch / Einigung.\n\nBetriebsrat (BetrVG): Ab 5 AN wählbar. Mitbestimmung in sozialen, personellen, wirtschaftlichen Fragen. § 87 BetrVG (harte Mitbestimmung): Arbeitszeit, Urlaubsplan, Akkord- & Prämienlöhne, Ordnung im Betrieb. Betriebsversammlung (1x/Quartal), Jugend- & Auszubildendenvertretung (JAV) ab 5 Azubis.',
 '{"required_concepts": ["Tarifautonomie", "Art 9 GG", "Manteltarifvertrag", "Lohntarifvertrag", "Flächentarif", "Friedenspflicht", "Schlichtung", "Urabstimmung 75 %", "Streik", "Aussperrung", "Betriebsrat ab 5 AN", "§ 87 BetrVG", "JAV"]}',
 '[{"criterion": "Tarifautonomie + GG", "weight": 2, "description": "Art. 9 erwähnt", "required": true},
   {"criterion": "Tarifarten", "weight": 3, "description": "Mind. 3 Arten", "required": true},
   {"criterion": "Eskalation", "weight": 2, "description": "Schritte bis Streik", "required": true},
   {"criterion": "Betriebsrat", "weight": 2, "description": "Rechte / Schwellenwert", "required": true}]',
 8, 'ki-generated', 4, 480),

('wiso-tarif', 'cued',
 'Was bedeutet "Friedenspflicht" in einem Tarifvertrag?',
 'Während der Laufzeit eines Tarifvertrags dürfen Gewerkschaft + Arbeitgeber KEINE Arbeitskampfmaßnahmen (Streik, Aussperrung) zu den im Vertrag geregelten Themen führen. Die Friedenspflicht endet mit Ablauf der Tarifvertragslaufzeit oder nach Kündigung.',
 '{"required_concepts": ["Laufzeit", "kein Streik", "keine Aussperrung", "geregelte Themen"]}',
 NULL, 2, 'ki-generated', 2, 90),

('wiso-tarif', 'cued',
 'Was sind die Eskalationsstufen eines Tarifkonflikts in richtiger Reihenfolge?',
 '1. Tarifverhandlungen (mehrere Runden)\n2. Scheitern → Schlichtung (freiwillig/verpflichtend je Branche)\n3. Urabstimmung der Gewerkschaftsmitglieder (mind. 75 % Zustimmung nötig)\n4. Streik (Gewerkschaft) und/oder Aussperrung (Arbeitgeber)\n5. Neue Verhandlungen → Einigung oder Schlichterspruch',
 '{"required_concepts": ["Verhandlungen", "Schlichtung", "Urabstimmung 75 %", "Streik", "Aussperrung"]}',
 NULL, 3, 'ki-generated', 3, 120),

('wiso-tarif', 'cued',
 'Ab wie vielen Arbeitnehmern kann ein Betriebsrat gewählt werden? Welche Hauptrechte hat er (nenne 3 Bereiche der Mitbestimmung).',
 'Ab 5 ständig beschäftigten wahlberechtigten AN (davon 3 wählbar) kann ein Betriebsrat gewählt werden (§ 1 BetrVG).\n\n3 Mitbestimmungsbereiche:\n1. Soziale Mitbestimmung (§ 87 BetrVG): Arbeitszeit, Pausen, Urlaubsplan, Akkord- & Prämienlöhne — echtes Mitbestimmungsrecht (ohne BR-Zustimmung nicht durchsetzbar).\n2. Personelle Angelegenheiten: Einstellung, Versetzung, Eingruppierung, Kündigung (BR muss angehört werden).\n3. Wirtschaftliche Angelegenheiten: Bei >20 AN Informationsrecht + Wirtschaftsausschuss, bei Betriebsänderungen Sozialplan.',
 '{"required_concepts": ["5 AN Schwelle", "§ 1 BetrVG", "soziale Mitbestimmung § 87", "personell", "wirtschaftlich"]}',
 NULL, 4, 'ki-generated', 4, 240),

('wiso-tarif', 'cued',
 'Was ist der Unterschied zwischen einem Warnstreik und einem Erzwingungsstreik?',
 'Warnstreik: kurzfristige Arbeitsniederlegung (meist wenige Stunden bis 1 Tag) WÄHREND laufender Tarifverhandlungen, um Druck auszuüben. OHNE Urabstimmung möglich.\n\nErzwingungsstreik: unbefristete Arbeitsniederlegung NACH gescheiterten Verhandlungen und Urabstimmung (75 %). Ziel ist der Abschluss eines Tarifvertrags.',
 '{"required_concepts": ["Warnstreik kurz während", "Erzwingungsstreik unbefristet nach Urabstimmung", "75 %"]}',
 NULL, 2, 'ki-generated', 3, 150),

('wiso-tarif', 'application',
 'Szenario: In deinem Ausbildungsbetrieb (IT-GmbH, 45 AN) gibt es Konflikte über Überstunden und Pausenregelung. Ein Kollege schlägt vor einen Betriebsrat zu gründen. Beschreibe (a) ob die Gründung möglich ist, (b) wie das Prozedere aussieht, (c) welche Rechte der Betriebsrat bei Überstunden-Anordnung hätte.',
 '(a) Gründung möglich: Ja, ab 5 AN möglich (§ 1 BetrVG). Bei 45 AN wäre ein 3-köpfiger Betriebsrat zu wählen (§ 9 BetrVG: 21-50 AN = 3 Mitglieder).\n\n(b) Prozedere zur Gründung:\n1. 3 AN oder eine im Betrieb vertretene Gewerkschaft laden zu einer Betriebsversammlung ein.\n2. Wahlvorstand wird bestellt (3 Personen).\n3. Wahlvorstand schreibt Wahl aus, sammelt Kandidatenvorschläge.\n4. Briefwahl oder Urnenwahl (allgemein, geheim, gleich, unmittelbar).\n5. Wahlvorstand zählt aus → Bekanntmachung des Ergebnisses.\n6. Konstituierende Sitzung des BR: Vorsitzender + Stellvertreter.\n\n(c) Rechte bei Überstunden:\nÜberstunden = Arbeitszeit → § 87 BetrVG soziale Mitbestimmung. Der Arbeitgeber KANN Überstunden nicht einseitig anordnen — der BR muss zustimmen. Ohne BR-Zustimmung sind Überstunden-Anordnungen UNWIRKSAM. Falls keine Einigung: Einigungsstelle entscheidet (§ 76 BetrVG).\n\nÄhnlich bei Pausen: § 87 Abs. 1 Nr. 2 BetrVG (Beginn/Ende der täglichen Arbeitszeit + Pausen).',
 '{"required_concepts": ["5 AN Schwelle", "§ 1 BetrVG", "Wahlvorstand", "geheime Wahl", "§ 87 BetrVG", "Überstunden Mitbestimmung", "Einigungsstelle"]}',
 '[{"criterion": "Möglichkeit bejaht", "weight": 1, "description": "§ 1 BetrVG", "required": true},
   {"criterion": "Wahl-Prozedere", "weight": 3, "description": "Wahlvorstand → Wahl → konstituierende Sitzung", "required": true},
   {"criterion": "Überstunden-Recht", "weight": 4, "description": "§ 87, Zustimmung nötig", "required": true}]',
 8, 'ki-generated', 5, 900),

-- ===== RECHTSGESCHÄFTE + KAUFVERTRAGSSTÖRUNGEN =====
('wiso-rechtsgeschaeft', 'blurt',
 'Schreibe alles auf was du über Rechtsgeschäfte weißt: Arten, Geschäftsfähigkeit (beschränkt/voll), Willenserklärungen, Kaufvertragsstörungen (Sachmangel, Verzug, Unmöglichkeit).',
 'Rechtsgeschäft = Handlung die rechtliche Folgen hat, basiert auf Willenserklärungen.\n\nArten:\n- Einseitige RG: eine Willenserklärung (Kündigung, Testament).\n- Mehrseitige RG: mindestens 2 Willenserklärungen (Vertrag).\n\nGeschäftsfähigkeit (§ 104 ff BGB):\n- Geschäftsunfähig: unter 7 Jahre → RG nichtig.\n- Beschränkt geschäftsfähig (7-17): RG nur mit Einwilligung der Eltern wirksam; Ausnahme "Taschengeldparagraph" § 110 BGB (wenn mit eigenen Mitteln bezahlt) + lediglich rechtlich vorteilhaft (§ 107).\n- Voll geschäftsfähig ab 18.\n\nKaufvertragsstörungen:\n- Sachmangel (§ 434 BGB): Ware entspricht nicht der vereinbarten Beschaffenheit / nicht zum gewöhnlichen Gebrauch geeignet.\n- Lieferungsverzug: Lieferung nach Fälligkeit trotz Mahnung (Verbraucher: ab 30 Tage nach Rechnung ohne Mahnung).\n- Unmöglichkeit: Leistung ist objektiv nicht möglich (Ware verbrannt).\n\nMängelrechte (§ 437 BGB): 1. Nacherfüllung (Reparatur oder Ersatzlieferung) → 2. Rücktritt oder Minderung → 3. Schadensersatz.\n\nGewährleistungsfrist: 2 Jahre (Neuware B2C), 1 Jahr (Gebrauchtware möglich). Garantie ist freiwillige Zusatzleistung.',
 '{"required_concepts": ["einseitig mehrseitig", "Geschäftsfähigkeit 7 18", "Taschengeldparagraph", "§ 110 BGB", "Sachmangel § 434", "Verzug", "Mahnung 30 Tage", "Unmöglichkeit", "Mängelrechte Nacherfüllung Rücktritt Minderung Schadensersatz", "Gewährleistung 2 Jahre", "Garantie freiwillig"]}',
 '[{"criterion": "Arten", "weight": 2, "description": "Einseitig/mehrseitig", "required": true},
   {"criterion": "Geschäftsfähigkeit-Stufen", "weight": 3, "description": "Alle 3 mit Altersgrenzen", "required": true},
   {"criterion": "Kaufvertragsstörungen", "weight": 3, "description": "Mind. Sachmangel + Verzug", "required": true},
   {"criterion": "Mängelrechte-Reihenfolge", "weight": 2, "description": "Nacherfüllung zuerst", "required": true}]',
 10, 'ki-generated', 4, 600),

('wiso-rechtsgeschaeft', 'cued',
 'Der 16-jährige Max kauft ohne Elterneinverständnis einen Laptop für 800 € von seinem Taschengeld. Ist das RG wirksam?',
 'Nein — NICHT wirksam (schwebend unwirksam nach § 108 BGB).\n\nBegründung: Max ist beschränkt geschäftsfähig. Ein 800-€-Laptop ist NICHT "lediglich rechtlich vorteilhaft" (§ 107 BGB). Der Taschengeldparagraph § 110 BGB gilt nur, wenn Max mit tatsächlich zur freien Verfügung überlassenen Mitteln bezahlt — 800 € übersteigen üblicherweise das Taschengeld eines 16-Jährigen deutlich.\n\nDer Vertrag wird erst wirksam, wenn die Eltern nachträglich zustimmen (Genehmigung). Verweigern sie, ist er endgültig nichtig — der Kaufpreis muss zurück, der Laptop ebenso.',
 '{"required_concepts": ["beschränkt geschäftsfähig", "§ 108 BGB schwebend unwirksam", "§ 107 nicht vorteilhaft", "§ 110 Taschengeld nicht anwendbar", "Eltern Zustimmung"]}',
 NULL, 4, 'ki-generated', 4, 240),

('wiso-rechtsgeschaeft', 'cued',
 'Welche Mängelrechte stehen dem Käufer bei einem Sachmangel in welcher Reihenfolge zu?',
 'Reihenfolge nach § 437 BGB:\n\n1. Nacherfüllung (Primärrecht): Käufer wählt zwischen Nachbesserung (Reparatur) oder Ersatzlieferung. Der Verkäufer kann ablehnen nur wenn unverhältnismäßig teuer.\n\n2. Bei Scheitern (2 Versuche, Verweigerung, Unzumutbarkeit):\n   a) Rücktritt vom Vertrag — Ware zurück, Geld zurück.\n   b) Minderung des Kaufpreises — Ware behalten, Preis reduziert.\n\n3. Schadensersatz (parallel möglich bei Verschulden des Verkäufers).\n\n4. Aufwendungsersatz (Nachteile die durch den Mangel entstanden sind).',
 '{"required_concepts": ["Nacherfüllung zuerst", "Nachbesserung oder Ersatz", "Rücktritt", "Minderung", "Schadensersatz", "§ 437 BGB"]}',
 NULL, 3, 'ki-generated', 3, 240),

('wiso-rechtsgeschaeft', 'cued',
 'Unterscheide Gewährleistung und Garantie.',
 'Gewährleistung: gesetzliche Pflicht des Verkäufers — bei Sachmangel haftet er. Dauer: 2 Jahre ab Übergabe bei Neuware (§ 438 BGB). Erste 12 Monate Beweislastumkehr — der VK muss beweisen, dass kein Mangel vorlag. Kann bei Gebrauchtware auf 1 Jahr reduziert werden (nicht abdingbar zwischen Unternehmer und Verbraucher).\n\nGarantie: FREIWILLIGE Leistung des Herstellers oder Händlers. Regelt eigene Bedingungen (Dauer, Umfang). Kommt ZUSÄTZLICH zur Gewährleistung — nicht statt.',
 '{"required_concepts": ["Gewährleistung gesetzlich", "2 Jahre", "Beweislastumkehr 12 Monate", "Garantie freiwillig", "zusätzlich nicht statt"]}',
 NULL, 3, 'ki-generated', 3, 180),

('wiso-rechtsgeschaeft', 'cued',
 'Wann kommt der Käufer in Zahlungsverzug?',
 'Zahlungsverzug tritt ein (§ 286 BGB):\n\n1. Nach Mahnung: Fälligkeit erreicht + Mahnung durch den Verkäufer → Verzug ab Zugang der Mahnung.\n\n2. Ohne Mahnung wenn:\n   a) Kalendertermin für Leistung bestimmt ist (Zahlbar bis 15.03.).\n   b) Verbraucher: automatisch 30 Tage nach Zugang der Rechnung, wenn auf der Rechnung auf diese Folge hingewiesen wurde (§ 286 Abs. 3 BGB).\n\nFolgen: Verzugszinsen (B2C 5 %, B2B 9 % über Basiszins), Schadensersatz, ggf. Rücktritt.',
 '{"required_concepts": ["Mahnung", "§ 286 BGB", "Kalendertermin ohne Mahnung", "30 Tage Verbraucher", "Verzugszinsen 5 9 %"]}',
 NULL, 3, 'ki-generated', 4, 180),

('wiso-rechtsgeschaeft', 'application',
 'Du hast einen Laptop für 1.200 € gekauft. Nach 4 Monaten ist der Akku defekt (hält nur noch 30 Minuten statt angegebene 8 Stunden). Du wendest dich an den Verkäufer. Beschreibe: (a) welche Rechte du hast und in welcher Reihenfolge, (b) wer hat die Beweislast, (c) was passiert wenn zweimalige Reparatur scheitert.',
 '(a) Rechte nach § 437 BGB in dieser Reihenfolge:\n\n1. Nacherfüllung (Primärrecht): Ich wähle zwischen Reparatur (Nachbesserung) oder Ersatzlieferung eines neuen Laptops. Der Verkäufer muss eine angemessene Frist bekommen.\n\n2. Falls Nacherfüllung scheitert (i.d.R. nach 2 erfolglosen Versuchen):\n   a) Rücktritt: Laptop zurück, Kaufpreis zurück.\n   b) Minderung: Laptop behalten, Preis wird reduziert.\n\n3. Zusätzlich Schadensersatz bei Verschulden des VK (Laufzeitverkürzung, Leihgerät-Kosten).\n\n(b) Beweislast:\nDer Mangel ist 4 Monate nach Kauf aufgetreten → innerhalb der ersten 12 Monate gilt Beweislastumkehr (§ 477 BGB). Der VERKÄUFER muss beweisen, dass der Mangel bei Übergabe NICHT vorlag (z.B. fahrlässige Beschädigung durch Käufer). Erst ab Monat 13 muss der Käufer den Mangel bei Übergabe beweisen.\n\n(c) Nach zweimaliger gescheiterter Reparatur:\nNacherfüllung gilt als gescheitert → ich kann zwischen Rücktritt und Minderung wählen. Bei Rücktritt: Laptop zurück, 1.200 € zurück (ggf. abzüglich Nutzungsentschädigung, aber seit 2022 bei Kaufmangel kaum noch relevant). Bei Minderung: angemessene Preisreduktion — typisch 20-40 % je nach Restnutzen.',
 '{"required_concepts": ["Nacherfüllung zuerst", "Reparatur oder Ersatz", "Rücktritt oder Minderung", "2 Versuche Regel", "Beweislastumkehr 12 Monate", "§ 477 BGB", "VK muss beweisen"]}',
 '[{"criterion": "Reihenfolge korrekt", "weight": 3, "description": "Nacherfüllung → Rücktritt/Minderung", "required": true},
   {"criterion": "Beweislast", "weight": 3, "description": "12 Monate Umkehr", "required": true},
   {"criterion": "Scheitern nach 2 Versuchen", "weight": 2, "description": "Rücktritt oder Minderung", "required": true}]',
 8, 'ki-generated', 4, 720),

-- ===== KAUFVERTRAG + MÄNGELRECHTE =====
('wiso-kaufvertrag', 'blurt',
 'Schreibe alles was du über den Kaufvertrag weißt: Zustandekommen (Anfrage → Angebot → Annahme), gesetzliche Grundlagen, Inhalt, Pflichten VK + KF, besondere Klauseln (Eigentumsvorbehalt, AGB).',
 'Kaufvertrag (§§ 433 ff BGB) kommt durch 2 übereinstimmende Willenserklärungen zustande: Antrag (Angebot) + Annahme.\n\nTypischer Ablauf:\n1. Anfrage (unverbindliche Bitte um Angebot — NICHT rechtlich bindend).\n2. Angebot / Offerte (bindend, § 145 BGB — wenn "freibleibend", dann nicht bindend).\n3. Bestellung (= Annahme, wenn inhaltsgleich; sonst Gegenangebot).\n4. Auftragsbestätigung (bei Abweichung Gegenangebot, sonst Bestätigung).\n5. Lieferung + Rechnung.\n\nPflichten Verkäufer (§ 433 Abs. 1): Eigentum + Besitz verschaffen, mangelfreie Ware übergeben.\nPflichten Käufer (§ 433 Abs. 2): Kaufpreis zahlen + Ware abnehmen.\n\nBesondere Klauseln:\n- Eigentumsvorbehalt (§ 449): Eigentum geht erst mit vollständiger Bezahlung über.\n- AGB: Allgemeine Geschäftsbedingungen — rechtlich wirksam bei zumutbarer Kenntnisnahme + kein Überraschung.\n- Skonto: % Abzug bei schneller Zahlung.\n- Rabatt: % Nachlass unabhängig vom Zahlungszeitpunkt.\n\nFristen: Annahmefrist (wenn gesetzt → bis dann), sonst "angemessene Zeit" (bei Abwesenden meist 1-2 Wochen).',
 '{"required_concepts": ["2 Willenserklärungen", "§ 433 BGB", "Anfrage unverbindlich", "Angebot bindend § 145", "Annahme Bestellung", "Pflichten VK Eigentum mangelfrei", "Pflichten KF zahlen abnehmen", "Eigentumsvorbehalt § 449", "AGB", "Skonto Rabatt Unterschied"]}',
 '[{"criterion": "2 Willenserklärungen", "weight": 2, "description": "Grundprinzip", "required": true},
   {"criterion": "4-Stufen-Ablauf", "weight": 3, "description": "Anfrage bis Bestätigung", "required": true},
   {"criterion": "Pflichten beidseitig", "weight": 2, "description": "VK + KF", "required": true},
   {"criterion": "Besondere Klauseln", "weight": 3, "description": "Mind. Eigentumsvorbehalt + AGB", "required": false}]',
 10, 'ki-generated', 4, 540),

('wiso-kaufvertrag', 'cued',
 'Ist eine Anfrage rechtlich bindend? Und ein Angebot?',
 'Anfrage: NICHT bindend. Sie ist eine unverbindliche Bitte um ein Angebot. Der Anbieter muss kein Angebot abgeben.\n\nAngebot / Offerte (§ 145 BGB): BINDEND — der Anbietende ist an sein Angebot gebunden, sobald der Empfänger es kennt. Ausnahme: Wenn das Angebot ausdrücklich als "freibleibend" oder "ohne Obligo" gekennzeichnet ist → dann nicht bindend. Auch Waren im Schaufenster sind i.d.R. nur "invitatio ad offerendum" (Aufforderung ein Angebot abzugeben), nicht bindendes Angebot.',
 '{"required_concepts": ["Anfrage unverbindlich", "Angebot bindend", "§ 145 BGB", "freibleibend nicht bindend", "invitatio ad offerendum"]}',
 NULL, 2, 'ki-generated', 3, 120),

('wiso-kaufvertrag', 'cued',
 'Was ist ein Eigentumsvorbehalt und wann wird er häufig eingesetzt?',
 'Eigentumsvorbehalt (§ 449 BGB): Der Verkäufer bleibt EIGENTÜMER der Ware, bis der Kaufpreis vollständig bezahlt ist. Der Käufer erhält nur den Besitz.\n\nEinsatz: Häufig im B2B-Geschäft bei Rechnungskauf, Teilzahlung oder Ratenzahlung. Schützt den Verkäufer — bei Zahlungsausfall kann er die Ware zurückverlangen. Muss ausdrücklich vereinbart werden (z.B. in AGB oder Kaufvertrag).',
 '{"required_concepts": ["§ 449 BGB", "Eigentum bis Zahlung", "Besitz geht über", "Ratenzahlung", "ausdrücklich vereinbaren"]}',
 NULL, 3, 'ki-generated', 3, 150),

('wiso-kaufvertrag', 'cued',
 'Unterscheide einseitigen und zweiseitigen Handelskauf (B2B vs B2C).',
 'B2C (Einseitiger Handelskauf): Unternehmer verkauft an Verbraucher. Besonderheiten: Verbraucherschutz, zwingende 2-Jahres-Gewährleistung bei Neuware, 14-Tage-Widerrufsrecht im Online-Handel, AGB-Kontrolle streng.\n\nB2B (Zweiseitiger Handelskauf, §§ 373 ff HGB): Beide sind Kaufleute. Besonderheiten:\n- Unverzügliche Untersuchungs- und Rügepflicht (§ 377 HGB) — Mängel sofort nach Wareneingang melden, sonst Verlust der Mängelrechte!\n- Kein Widerrufsrecht.\n- Gewährleistung kann vertraglich eingeschränkt werden.\n- Rügeobliegenheit gilt nur für Handelskauf.',
 '{"required_concepts": ["B2C Verbraucher 2 Jahre", "Widerruf 14 Tage", "B2B § 377 HGB", "Untersuchungspflicht", "Rügepflicht unverzüglich"]}',
 NULL, 4, 'ki-generated', 4, 240),

('wiso-kaufvertrag', 'cued',
 'Du bestellst als Unternehmer eine Lieferung und stellst beim Wareneingang einen Mangel fest. Was musst du tun um deine Rechte nicht zu verlieren?',
 '§ 377 HGB: Unternehmer im Handelskauf müssen die Ware UNVERZÜGLICH nach Ablieferung untersuchen und offensichtliche Mängel sofort melden ("rügen"). Versteckte Mängel müssen unverzüglich nach Entdeckung gerügt werden.\n\n"Unverzüglich" = ohne schuldhaftes Zögern (Faustregel: 1-2 Werktage). Wird NICHT rechtzeitig gerügt → die Ware gilt als genehmigt, sämtliche Mängelrechte erlöschen.\n\nPraxis: Mangel schriftlich (E-Mail, Fax) mit genauer Beschreibung + Datum melden, Fotos beifügen, Rechnungsnummer angeben.',
 '{"required_concepts": ["§ 377 HGB", "unverzüglich untersuchen", "sofort rügen", "Rechte erlöschen wenn zu spät", "schriftlich"]}',
 NULL, 3, 'ki-generated', 4, 180),

('wiso-kaufvertrag', 'application',
 'Kaufvertrag-Szenario: Du betreibst ein kleines IT-Unternehmen (keine Kleinunternehmerregelung). Du hast 10 Laptops für 9.500 € + MwSt von "TechSupply GmbH" bestellt. Eigentumsvorbehalt wurde vereinbart, Skonto 2 % bei Zahlung innerhalb 10 Tagen, sonst 30 Tage netto. Beschreibe: (a) Gesamtbetrag mit 19 % MwSt und Skontopreis, (b) was passiert bei Mangel an einem Laptop — welche Handlungsschritte musst du einleiten, (c) was bedeutet der Eigentumsvorbehalt für die Laptops wenn du Insolvenz anmeldest.',
 '(a) Gesamtrechnung:\nNetto: 9.500 €\n+ MwSt 19 %: 1.805 €\nBrutto: 11.305 €\n\nMit Skonto 2 % bei Zahlung <= 10 Tage:\nSkontobetrag: 11.305 × 0,02 = 226,10 €\nZahlbetrag: 11.305 − 226,10 = 11.078,90 €\n\n(b) Mangel-Handlung (B2B / HGB):\n1. UNVERZÜGLICH nach Wareneingang untersuchen (§ 377 HGB).\n2. Mangel sofort schriftlich rügen (E-Mail / Fax) — spätestens 1-2 Werktage nach Entdeckung, Beschreibung + Fotos + Rechnungsnummer.\n3. Nacherfüllung einfordern — Reparatur oder Ersatzlieferung (Wahl nach § 439 BGB).\n4. Bei Scheitern: Rücktritt oder Minderung, evtl. Schadensersatz.\n→ Wichtig: Verpasst du die Rügepflicht, verlierst du ALLE Mängelrechte — Ware gilt als genehmigt.\n\n(c) Eigentumsvorbehalt bei Insolvenz:\nSolange die Laptops NICHT vollständig bezahlt sind, bleibt TechSupply GmbH EIGENTÜMER. Im Insolvenzfall kann TechSupply ihre Laptops AUSSONDERN (§ 47 InsO) — sie fallen NICHT in die Insolvenzmasse. Die anderen Gläubiger haben keinen Zugriff auf diese Ware. Das macht den Eigentumsvorbehalt zum stärksten Sicherungsrecht bei Lieferanten-Krediten.',
 '{"required_concepts": ["11305 Brutto", "2 % Skonto 226", "11078.90", "§ 377 HGB", "unverzüglich rügen", "Nacherfüllung", "Eigentumsvorbehalt Insolvenz § 47 InsO", "Aussonderung"]}',
 '[{"criterion": "Brutto-Berechnung", "weight": 2, "description": "11305", "required": true},
   {"criterion": "Skonto-Berechnung", "weight": 2, "description": "226 / 11078.90", "required": true},
   {"criterion": "Mängelrüge-Prozedere", "weight": 3, "description": "§ 377 HGB unverzüglich", "required": true},
   {"criterion": "Eigentumsvorbehalt Insolvenz", "weight": 3, "description": "Aussonderung § 47 InsO", "required": true}]',
 10, 'ki-generated', 5, 900),

-- ===== MARKTFORMEN =====
('wiso-marktformen', 'blurt',
 'Schreibe alles was du über Marktformen, Wettbewerb und Preisbildung weißt. Beziehe ein: Polypol/Oligopol/Monopol, vollkommener Markt, Preisbildung Angebot/Nachfrage, Marktversagen.',
 'Marktformen nach Anzahl der Anbieter/Nachfrager:\n\n| | viele Anbieter | wenige Anbieter | ein Anbieter |\n|---|---|---|---|\n| viele Nachfrager | Polypol | Angebotsoligopol | Angebotsmonopol |\n| wenige Nachfrager | Nachfrageoligopol | zweiseitiges Oligopol | beschränktes Monopol |\n| ein Nachfrager | Nachfragemonopol | beschränktes Monopol | zweiseitiges Monopol |\n\nVollkommener Markt (Modellidealisierung):\n- Viele Anbieter + viele Nachfrager (Polypol).\n- Homogene Güter (gleichartig).\n- Markttransparenz.\n- Keine Präferenzen (räumlich, zeitlich, persönlich).\n- Unendlich schnelle Reaktionsgeschwindigkeit.\n\nUnvollkommener Markt: in der Realität üblich — heterogene Güter, Präferenzen, begrenzte Information.\n\nPreisbildung: Schnittpunkt Angebotskurve (steigt mit Preis) und Nachfragekurve (fällt mit Preis) = Gleichgewichtspreis.\n- Preis zu hoch → Angebotsüberschuss → Preis sinkt.\n- Preis zu niedrig → Nachfrageüberschuss → Preis steigt.\n\nMarktversagen: externe Effekte (Umweltverschmutzung), Informationsasymmetrie, öffentliche Güter (Straßen), Monopolmacht.',
 '{"required_concepts": ["Polypol", "Oligopol", "Monopol", "Angebots vs Nachfrage", "vollkommener Markt", "Homogenität", "Transparenz", "Preisbildung Schnittpunkt", "Gleichgewichtspreis", "Marktversagen"]}',
 '[{"criterion": "3 Grundformen", "weight": 2, "description": "Polypol/Oligopol/Monopol", "required": true},
   {"criterion": "Markt-Matrix", "weight": 3, "description": "Angebots vs Nachfrage-Seite", "required": true},
   {"criterion": "Vollkommener Markt", "weight": 2, "description": "4-5 Voraussetzungen", "required": true},
   {"criterion": "Preisbildung", "weight": 1, "description": "Kurven-Schnittpunkt", "required": false}]',
 8, 'ki-generated', 4, 420),

('wiso-marktformen', 'cued',
 'Nenne die Voraussetzungen des vollkommenen Markts.',
 'Vollkommener Markt (Modellannahme):\n1. Viele Anbieter und viele Nachfrager (Polypol).\n2. Homogene Güter (völlig gleichartig).\n3. Vollständige Markttransparenz (alle Infos bekannt).\n4. Fehlende Präferenzen (keine räumlichen/zeitlichen/persönlichen Vorlieben).\n5. Unendlich schnelle Reaktion auf Preisänderungen.\n\nIn der Realität nie erfüllt — aber nützliches Vergleichsmodell.',
 '{"required_concepts": ["Polypol", "Homogenität", "Transparenz", "keine Präferenzen", "schnelle Reaktion"]}',
 NULL, 3, 'ki-generated', 3, 150),

('wiso-marktformen', 'cued',
 'Was ist ein Oligopol? Nenne ein Beispiel aus der IT-Branche.',
 'Oligopol: Wenige Anbieter beherrschen den Markt — i.d.R. 3-10 große Unternehmen. Sie beobachten sich gegenseitig, Preisänderungen und Angebote werden schnell nachgezogen.\n\nIT-Beispiele:\n- Smartphone-OS (Android, iOS)\n- Cloud-Anbieter (AWS, Azure, GCP)\n- Suchmaschinen-Werbemarkt (Google, Bing)\n- Social-Media-Plattformen (Meta, TikTok, X)\n\nGefahr: Preisabsprachen (Kartelle) — verboten nach Kartellrecht (GWB) und EU-Kartellrecht.',
 '{"required_concepts": ["wenige Anbieter", "3-10", "gegenseitige Beobachtung", "IT-Beispiel", "Kartellgefahr"]}',
 NULL, 3, 'ki-generated', 3, 150),

('wiso-marktformen', 'cued',
 'Der Preis einer Ware liegt AKTUELL über dem Gleichgewichtspreis. Was passiert langfristig, und warum?',
 'Preis > Gleichgewichtspreis → Angebotsüberschuss:\n\n1. Anbieter produzieren mehr als Nachfrage abnimmt → Lagerbestände steigen.\n2. Anbieter senken Preise um Absatz zu fördern → Preis sinkt.\n3. Gleichzeitig springt die Nachfrage an (bei niedrigerem Preis wollen mehr kaufen).\n4. Angebot und Nachfrage nähern sich bis zum Gleichgewichtspreis → Markt ist wieder im Gleichgewicht.\n\nDas wirkt automatisch durch die Preisbildung — ohne Eingriff.',
 '{"required_concepts": ["Angebotsüberschuss", "Preis sinkt", "Nachfrage steigt bei tieferem Preis", "Gleichgewicht erreicht"]}',
 NULL, 3, 'ki-generated', 3, 150),

('wiso-marktformen', 'application',
 'Du bist Geschäftsführer eines kleinen Software-Startups. Ihr entwickelt eine Branchen-Software. Der Markt hat 5 Konkurrenten. Analysiere: (a) in welcher Marktform ihr operiert, (b) welche Chancen und Risiken das bedeutet, (c) wie ihr euch als Kleinanbieter strategisch aufstellen solltet.',
 '(a) Marktform: Angebotsoligopol (wenige Anbieter, viele potenzielle Kunden = Unternehmen der Branche).\n\n(b) Chancen + Risiken:\nChancen:\n- Weniger Preiskampf als im Polypol, Margen oft höher.\n- Differenzierung durch Nischenfeatures möglich.\n- Kunden haben begrenzte Auswahl → Bindung nach Kauf hoch (Wechselkosten).\n\nRisiken:\n- Konkurrenten reagieren schnell auf Preis-/Feature-Änderungen.\n- Bei Preisabsprachen der Großen → Markteintritt schwer.\n- Marktführer kann durch Akquisition drohen (Startup-Killing).\n- Kunden fordern Interoperabilität / Datenmigration (Lock-In ist negativ bewertet).\n\n(c) Strategische Positionierung als Kleinanbieter:\n1. Nischenstrategie: Spezialisierung auf einen Segment, den die Großen nicht bedienen (z.B. Handwerksbetriebe 5-20 MA).\n2. Servicequalität: persönliche Betreuung, deutschsprachiger Support, DSGVO-konform gehostet.\n3. Agile Entwicklung: schnellere Features-Zyklen als große Konkurrenten.\n4. Preistransparenz: klare Preise ohne versteckte Kosten — wirkt vertrauensbildend.\n5. Partnerschaften: Integrationen mit DATEV, Lexware etc. statt alles selbst bauen.\n6. Kundenreferenzen aufbauen: Case Studies, Testimonials.',
 '{"required_concepts": ["Angebotsoligopol", "Chancen Differenzierung", "Risiken Reaktionsgeschwindigkeit", "Nischenstrategie", "Service als Differenzierung"]}',
 '[{"criterion": "Marktform identifiziert", "weight": 2, "description": "Oligopol", "required": true},
   {"criterion": "Chancen + Risiken", "weight": 3, "description": "Je 2-3 Aspekte", "required": true},
   {"criterion": "Strategie-Empfehlungen", "weight": 3, "description": "Mind. 3 konkrete Maßnahmen", "required": true}]',
 8, 'ki-generated', 4, 600),

-- ===== AUSBILDUNGSRECHT =====
('wiso-ausbildungsrecht', 'blurt',
 'Schreibe alles was du über Ausbildungsrecht weißt: BBiG (Berufsbildungsgesetz), JArbSchG (Jugendarbeitsschutzgesetz), Pflichten Azubi/Ausbilder, Abschlussprüfung, Probezeit, Kündigung.',
 'BBiG (Berufsbildungsgesetz) + HwO regeln die Berufsausbildung.\n\nAusbildungsvertrag (§ 10 BBiG): schriftlich (Beweis), Inhalt: Dauer, Inhalt, Vergütung, Arbeitszeit, Urlaub, Probezeit (1-4 Monate). Eintragung in Lehrlingsrolle (IHK/HWK).\n\nPflichten Ausbilder (§ 14):\n1. Vermitteln aller Fähigkeiten/Kenntnisse.\n2. Freistellen für Berufsschule + Prüfungen.\n3. Ausbildungsmittel kostenlos stellen.\n4. Zeugnis am Ende.\n5. Wohlwollen zeigen, nicht abträglich beschäftigen.\n\nPflichten Azubi (§ 13):\n1. Lernen (Sorgfaltspflicht).\n2. Weisungen befolgen.\n3. Berufsschule + Prüfungen besuchen.\n4. Betriebliche Ordnung beachten.\n5. Schweigepflicht.\n\nJArbSchG (gilt für unter 18):\n- Max 8 h/Tag, 40 h/Woche.\n- 12 h Nachtruhe (20-6 Uhr verboten bis 16, bis 23 Uhr bis 18).\n- 30 Urlaubstage minimum (bis 16), 27 (bis 17), 25 (bis 18).\n- Berufsschultag wird auf Arbeitszeit angerechnet (bei > 5 Std. frei).\n\nProbezeit: 1-4 Monate (§ 20 BBiG). Während Probezeit kann JEDERZEIT fristlos ohne Grund gekündigt werden.\n\nKündigung nach Probezeit:\n- Durch Azubi: mit 4 Wochen Frist aus wichtigem Grund ODER bei Berufsaufgabe / -wechsel.\n- Durch Ausbilder: nur aus wichtigem Grund (§ 22 BBiG).\n\nAbschlussprüfung: AP Teil 1 (Mitte Ausbildung) + Teil 2 (Ende). Bei Nichtbestehen 2 Wiederholungen möglich (§ 37 BBiG).',
 '{"required_concepts": ["BBiG", "JArbSchG", "schriftlicher Ausbildungsvertrag", "Lehrlingsrolle", "Probezeit 1-4 Monate", "Ausbilderpflichten", "Azubipflichten", "Urlaub minderjährig", "Kündigung § 22", "Wiederholungsprüfungen"]}',
 '[{"criterion": "BBiG + JArbSchG genannt", "weight": 2, "description": "Beide Gesetze", "required": true},
   {"criterion": "Pflichten beidseitig", "weight": 3, "description": "Ausbilder + Azubi je 2-3", "required": true},
   {"criterion": "Probezeit + Kündigung", "weight": 2, "description": "Dauer + Regel", "required": true},
   {"criterion": "JArbSchG-Regeln", "weight": 2, "description": "Arbeitszeit/Urlaub minderjährig", "required": false}]',
 8, 'ki-generated', 4, 480),

('wiso-ausbildungsrecht', 'cued',
 'Wie lange darf die Probezeit in einem Ausbildungsvertrag höchstens sein?',
 '§ 20 BBiG: Die Probezeit muss MINDESTENS 1 Monat und DARF HÖCHSTENS 4 Monate betragen. Während der Probezeit kann das Ausbildungsverhältnis von BEIDEN Seiten jederzeit ohne Einhaltung einer Kündigungsfrist gekündigt werden — ohne Angabe eines Grundes.',
 '{"required_concepts": ["§ 20 BBiG", "1 bis 4 Monate", "jederzeit kündbar", "ohne Grund"]}',
 NULL, 2, 'ki-generated', 2, 90),

('wiso-ausbildungsrecht', 'cued',
 'Du bist 16-jähriger Azubi. Dein Chef möchte dich bis 22 Uhr arbeiten lassen. Ist das zulässig? Was sagt das Gesetz?',
 'NEIN, nicht zulässig.\n\n§ 14 JArbSchG (Nachtruhe): Jugendliche unter 16 dürfen nur von 6 bis 20 Uhr beschäftigt werden. Zwischen 16 und 18 grundsätzlich nur von 6 bis 20 Uhr, aber mit Ausnahmen: im Gaststättengewerbe bis 22 Uhr, Schichtbetrieb bis 23 Uhr, Bäckereien ab 4 Uhr — alles mit entsprechender Ruhezeit danach.\n\nZusätzlich § 8 JArbSchG: maximal 8 Stunden täglich / 40 Stunden wöchentlich.\n\nFür einen normalen IT-Ausbildungsbetrieb: Arbeitszeit endet um 20 Uhr. Der Chef darf dich also NICHT bis 22 Uhr arbeiten lassen — das wäre eine Ordnungswidrigkeit (Bußgeld bis 15.000 €).',
 '{"required_concepts": ["JArbSchG", "§ 14 Nachtruhe", "§ 8 8 Std 40 h", "bis 20 Uhr Regel", "Ausnahmen Branche"]}',
 NULL, 3, 'ki-generated', 3, 180),

('wiso-ausbildungsrecht', 'cued',
 'Nenne 3 Pflichten des Ausbilders und 3 Pflichten des Azubis.',
 'Ausbilder-Pflichten (§ 14 BBiG):\n1. Vermittlung der für die Berufsausübung erforderlichen Fertigkeiten, Kenntnisse, Fähigkeiten.\n2. Kostenlose Bereitstellung von Ausbildungsmitteln (Werkzeug, Bücher).\n3. Freistellung für Berufsschule + Prüfungen.\n(Weiter: Ausstellung Zeugnis, Fürsorgepflicht)\n\nAzubi-Pflichten (§ 13 BBiG):\n1. Lern- und Ausbildungspflicht (sich bemühen, alle geforderten Fertigkeiten zu erlernen).\n2. Berufsschulpflicht (regelmäßige Teilnahme).\n3. Weisungsbefolgung.\n(Weiter: Sorgfalt, Schweigepflicht, Berichtsheftführung)',
 '{"required_concepts": ["§ 14 Ausbilder", "§ 13 Azubi", "Vermittlung", "Ausbildungsmittel", "Freistellung Berufsschule", "Lernpflicht", "Weisungsbefolgung"]}',
 NULL, 3, 'ki-generated', 3, 180),

('wiso-ausbildungsrecht', 'cued',
 'Wie oft darf ein Azubi die IHK-Abschlussprüfung wiederholen?',
 'Bei Nichtbestehen der Abschlussprüfung kann die Prüfung ZWEIMAL wiederholt werden (§ 37 Abs. 1 BBiG). Das Ausbildungsverhältnis verlängert sich auf Verlangen des Azubis automatisch bis zum nächsten Prüfungstermin, maximal um 1 Jahr (§ 21 Abs. 3 BBiG).\n\nFalls auch die 2. Wiederholung scheitert, kann man den Beruf nur noch durch "externe Prüfung" (nach mind. 4,5 Jahren Berufserfahrung) nachholen.',
 '{"required_concepts": ["§ 37 BBiG", "2 Wiederholungen", "§ 21 Verlängerung 1 Jahr", "externe Prüfung"]}',
 NULL, 2, 'ki-generated', 3, 120),

('wiso-ausbildungsrecht', 'application',
 'Szenario: Du bist 17, Azubi im 2. Lehrjahr (2,5 Jahre Ausbildung insgesamt). Dein Ausbilder lässt dich oft Reinigungsarbeiten im Büro erledigen statt Fachaufgaben. Du bekommst 950 € Vergütung. Beschreibe: (a) ob das zulässig ist, (b) welche Rechte du hast und wen du kontaktieren kannst, (c) was passiert wenn du AP1 (kommt nächstes Jahr) nicht bestehst.',
 '(a) Zulässigkeit:\n§ 14 Abs. 2 BBiG: "Dem Auszubildenden dürfen nur Aufgaben übertragen werden, die dem Ausbildungszweck dienen und seinen körperlichen Kräften angemessen sind."\n\nReinigungsarbeiten → NICHT dem Ausbildungszweck dienend (außer es wäre Reinigungskraft-Ausbildung). Gelegentliches Aufräumen OK, systematisches Reinigen statt Fachaufgaben ist rechtlich unzulässig. Dein Ausbilder verletzt seine Ausbildungspflicht.\n\n(b) Rechte + Ansprechpartner:\n1. Gespräch mit Ausbilder / Ausbildungsleiter — schriftliche Aufzeichnungen.\n2. Berufsschullehrer / Vertrauenslehrer einbeziehen.\n3. JAV (Jugend- und Auszubildendenvertretung) falls vorhanden — vertritt Azubi-Interessen.\n4. Betriebsrat — kann intervenieren.\n5. IHK Ausbildungsberatung — kostenlos, neutral, kann mit dem Ausbilder sprechen (mein Favorit).\n6. Bei fortgesetzter Verletzung: schriftliche Abmahnung, dann fristlose Kündigung aus wichtigem Grund (§ 22 BBiG) möglich.\n\nZum Gehalt: 950 € im 2. Lehrjahr IT-Ausbildung ist im üblichen Rahmen (Mindestausbildungsvergütung 2026 bei IT ca. 649 € im 1. Lehrjahr).\n\n(c) Bei Nichtbestehen AP1:\nAP1 zählt bereits als Teil der Abschlussprüfung (gestreckte Prüfung) mit 20-25 % Gewichtung. Bestehen ist KEINE Voraussetzung um AP2 machen zu können, aber das Ergebnis wird in die Gesamtnote einberechnet.\n\nBei schlechtem AP1 → Hauptfokus liegt darauf, in AP2 genug zu kompensieren (mind. 50 % Gesamtergebnis). Bei Durchfall insgesamt: 2 Wiederholungen möglich (§ 37 BBiG), Ausbildungsverhältnis kann auf Verlangen bis zum nächsten Prüfungstermin verlängert werden (max. 1 Jahr, § 21 Abs. 3 BBiG).',
 '{"required_concepts": ["§ 14 BBiG Ausbildungszweck", "ausbildungsfremde Tätigkeiten unzulässig", "IHK Ausbildungsberatung", "JAV Betriebsrat", "§ 22 Kündigung", "AP1 gestreckte Prüfung Gewichtung", "2 Wiederholungen", "§ 21 Verlängerung"]}',
 '[{"criterion": "Reinigung unzulässig", "weight": 2, "description": "§ 14 BBiG", "required": true},
   {"criterion": "Ansprechpartner", "weight": 3, "description": "Mind. 3 Stellen inkl. IHK", "required": true},
   {"criterion": "AP1-Bedeutung", "weight": 2, "description": "gestreckte Prüfung, Wiederholung", "required": true}]',
 8, 'ki-generated', 5, 900),

-- ===== WIRTSCHAFTSPOLITIK + KONJUNKTUR =====
('wiso-wirtschaftspolitik', 'blurt',
 'Schreibe alles was du über Konjunkturphasen, EZB-Geldpolitik und das magische Viereck der Wirtschaftspolitik weißt.',
 'Konjunkturzyklus (4 Phasen):\n1. Aufschwung (Expansion): BIP steigt, Nachfrage wächst, Arbeitslosigkeit sinkt, moderate Inflation, steigende Zinsen.\n2. Hochkonjunktur (Boom): BIP auf Höchststand, Vollbeschäftigung, steigende Löhne, Inflation beschleunigt, Investitionen hoch.\n3. Abschwung (Rezession): BIP sinkt, Nachfrage geht zurück, Arbeitslosigkeit steigt, Inflation nimmt ab.\n4. Tiefstand (Depression): BIP am niedrigsten, hohe Arbeitslosigkeit, Deflation möglich, Staatsinterventionen.\n\nEZB (Europäische Zentralbank) — Geldpolitik:\n- Hauptziel: Preisstabilität (Zielinflation ~2 % pro Jahr).\n- Instrumente: Leitzins (Hauptrefinanzierungssatz), Mindestreservesätze, Offenmarktgeschäfte, QE/Anleihenkäufe.\n- Expansive Politik: niedriger Leitzins → günstigere Kredite → mehr Nachfrage → Wachstum (bei Rezession).\n- Restriktive Politik: hoher Leitzins → teurere Kredite → weniger Nachfrage → Inflation gebremst (bei Überhitzung).\n\nMagisches Viereck (Stabilitätsgesetz 1967):\n1. Preisniveau-Stabilität (geringe Inflation).\n2. Hoher Beschäftigungsstand.\n3. Außenwirtschaftliches Gleichgewicht (ausgeglichene Handelsbilanz).\n4. Stetiges und angemessenes Wirtschaftswachstum.\n\n"Magisch" weil alle 4 gleichzeitig schwer zu erreichen sind — Zielkonflikte (z.B. hohe Beschäftigung treibt oft Inflation).\n\nMagisches Sechseck erweitert um: gerechte Einkommens-/Vermögensverteilung, Umweltschutz.',
 '{"required_concepts": ["Aufschwung Hochkonjunktur Abschwung Tiefstand", "BIP", "EZB Leitzins", "expansiv restriktiv", "magisches Viereck 4 Ziele", "Preisstabilität 2 %", "Zielkonflikt"]}',
 '[{"criterion": "4 Konjunkturphasen", "weight": 2, "description": "Benannt + charakterisiert", "required": true},
   {"criterion": "EZB-Rolle + Instrumente", "weight": 3, "description": "Leitzins + Wirkung", "required": true},
   {"criterion": "Magisches Viereck", "weight": 3, "description": "Alle 4 Ziele", "required": true}]',
 6, 'ki-generated', 4, 420),

('wiso-wirtschaftspolitik', 'cued',
 'Was passiert mit der Wirtschaft wenn die EZB den Leitzins senkt?',
 'Leitzinssenkung → expansive Geldpolitik:\n\n1. Banken refinanzieren sich günstiger → Kredite werden billiger.\n2. Unternehmen investieren mehr (günstigere Finanzierung).\n3. Konsumenten nehmen Kredite auf (Auto, Haus), sparen weniger.\n4. Gesamtnachfrage steigt → Produktion und Beschäftigung steigen.\n5. Inflation steigt tendenziell (mehr Nachfrage bei gleichem Angebot).\n6. Wechselkurs sinkt (weniger Kapitalzuflüsse) → Export günstiger, Import teurer.\n\nEingesetzt bei Konjunkturabschwüngen oder zu niedriger Inflation. Beispiel: EZB hat 2012-2022 den Leitzins auf 0 % gesenkt um die Wirtschaft anzukurbeln.',
 '{"required_concepts": ["günstigere Kredite", "mehr Investitionen Konsum", "Nachfrage steigt", "Inflation steigt", "Wechselkurs sinkt", "expansive Politik"]}',
 NULL, 3, 'ki-generated', 3, 180),

('wiso-wirtschaftspolitik', 'cued',
 'Was ist das magische Viereck und warum heißt es "magisch"?',
 '4 wirtschaftspolitische Hauptziele (§ 1 Stabilitäts- und Wachstumsgesetz 1967):\n\n1. Preisniveau-Stabilität (Inflation unter 2 %).\n2. Hoher Beschäftigungsstand (niedrige Arbeitslosigkeit).\n3. Außenwirtschaftliches Gleichgewicht (ausgeglichene Handelsbilanz).\n4. Stetiges und angemessenes Wirtschaftswachstum.\n\n"Magisch" weil die 4 Ziele sich teilweise widersprechen (Zielkonflikte):\n- Hohe Beschäftigung → oft steigende Löhne → höhere Inflation.\n- Starkes Wachstum → oft höhere Importe → Handelsbilanzdefizit.\n\nAlle 4 gleichzeitig zu erreichen ist praktisch "magisch" — gelingt selten.',
 '{"required_concepts": ["4 Ziele Preisstabilität Beschäftigung Außenhandel Wachstum", "Zielkonflikte", "Stabilitätsgesetz 1967"]}',
 NULL, 3, 'ki-generated', 3, 180),

('wiso-wirtschaftspolitik', 'cued',
 'Deutschland hat aktuell hohe Inflation (5 %) und sinkende Wirtschaftsleistung. In welcher Konjunkturphase befindet sich das Land und was ist der Fachbegriff dafür?',
 'Hohe Inflation + sinkendes BIP = STAGFLATION (aus "Stagnation" + "Inflation"). Klassischer Konjunkturzyklus geht davon aus: Inflation steigt im Aufschwung/Boom, sinkt in Rezession. Stagflation ist atypisch: beide Probleme gleichzeitig.\n\nUrsachen: Angebotsschocks (Öl-Krise 1970er, Energie-Krise 2022, Corona-Lieferketten). Die klassischen Instrumente versagen:\n- Zinssenkung (gegen Rezession) → verstärkt Inflation.\n- Zinserhöhung (gegen Inflation) → verstärkt Rezession.\n\nRichtige Antwort: Abschwung / Rezession, aber ungewöhnliche Form = Stagflation.',
 '{"required_concepts": ["Stagflation", "Angebotsschock", "Zielkonflikt Geldpolitik", "atypisch"]}',
 NULL, 3, 'ki-generated', 4, 180),

('wiso-wirtschaftspolitik', 'cued',
 'Welche Konjunkturindikatoren kennst du? Nenne 3 und erkläre kurz was sie zeigen.',
 '1. Bruttoinlandsprodukt (BIP): Wert aller produzierten Waren + Dienstleistungen. Zeigt Wirtschaftsleistung. Wird vierteljährlich veröffentlicht.\n2. Arbeitslosenquote: Anteil der Arbeitslosen an Erwerbspersonen. Sinkt im Aufschwung, steigt im Abschwung — zeitverzögerter Indikator.\n3. Inflationsrate (HVPI / VPI): Preisanstieg gegenüber Vorjahr. EZB-Ziel: 2 %.\n4. Geschäftsklima-Index (ifo-Index): Umfrage bei Unternehmen — zeigt Stimmung und Erwartungen.\n5. Auftragseingang Industrie: Vorlaufindikator — zeigt Zukunftserwartungen.\n6. Einkaufsmanager-Index (PMI): > 50 = Expansion, < 50 = Kontraktion.',
 '{"required_concepts": ["BIP", "Arbeitslosenquote", "Inflationsrate", "ifo-Index", "PMI"]}',
 NULL, 3, 'ki-generated', 3, 180),

('wiso-wirtschaftspolitik', 'application',
 'Deutschland befindet sich am Übergang von Hochkonjunktur in Rezession. BIP-Wachstum sinkt von 2,5 % auf 0,3 %, Inflation hoch bei 4 %, Arbeitslosigkeit beginnt zu steigen. Die Bundesregierung muss reagieren. Beschreibe: (a) Was kann die EZB tun, und welcher Zielkonflikt besteht? (b) Welche Fiskalpolitischen Maßnahmen könnte die Bundesregierung ergreifen? (c) Was passiert mit Steuereinnahmen und Staatsausgaben in dieser Phase?',
 '(a) EZB-Geldpolitik — Zielkonflikt:\nDilemma: Inflation bekämpfen (Zinsen rauf) VS Rezession bekämpfen (Zinsen runter).\nAktueller EZB-Fokus liegt auf Preisstabilität (2-%-Ziel) → also Zinserhöhung trotz schwacher Konjunktur. Dadurch wird Inflation gebremst, aber Rezession verstärkt.\nKonsequenz: Kredite werden teurer, Investitionen sinken, Unternehmensinsolvenzen steigen.\n\n(b) Fiskalpolitik (Bundesregierung) — expansive Maßnahmen:\n1. Konjunkturpakete: Staatliche Investitionen in Infrastruktur (Straßen, Digitalisierung), erzeugt Nachfrage.\n2. Steuersenkungen: mehr verfügbares Einkommen → mehr Konsum.\n3. Kurzarbeitergeld ausweiten: verhindert Massenentlassungen.\n4. Unternehmens-Zuschüsse: Energiekostenbremse, Liquiditätshilfen.\n5. Sozialtransfers erhöhen: Kindergeld, Wohngeld.\n\nFinanzierung: Staatsverschuldung steigt (ausnahmsweise von Schuldenbremse befreit bei Notlage).\n\n(c) Staatshaushalt in Rezession:\nSteuereinnahmen sinken AUTOMATISCH:\n- Einkommenssteuer: weniger Einkommen → weniger Steuern.\n- Körperschaftsteuer / Gewerbesteuer: Unternehmen machen weniger Gewinn.\n- Mehrwertsteuer: weniger Konsum.\n\nStaatsausgaben steigen AUTOMATISCH:\n- Arbeitslosengeld: mehr Empfänger.\n- Sozialhilfe: mehr Bedürftige.\n- Konjunkturprogramme: zusätzlich aktive Ausgaben.\n\nNetto: Staatsdefizit steigt stark ("automatische Stabilisatoren"). Schuldenbremse wird ggf. ausgesetzt (Notfall-Klausel). Beispiel: 2020 Corona-Krise → Deutschland 130 Mrd. € Defizit.',
 '{"required_concepts": ["EZB Zielkonflikt Inflation Rezession", "expansive Fiskalpolitik", "Konjunkturpaket Steuersenkung Kurzarbeit", "Einnahmen sinken", "Ausgaben steigen", "automatische Stabilisatoren", "Schuldenbremse"]}',
 '[{"criterion": "EZB-Dilemma", "weight": 3, "description": "Zielkonflikt benannt", "required": true},
   {"criterion": "Fiskalpolitische Maßnahmen", "weight": 3, "description": "Mind. 3 konkrete", "required": true},
   {"criterion": "Haushalt-Logik", "weight": 3, "description": "Einnahmen/Ausgaben Dynamik", "required": true}]',
 8, 'ki-generated', 5, 900)

) AS v(slug, item_type, prompt, model_answer, expected_answer_structure,
       grading_criteria, points, source_exam, difficulty, estimated_time_sec)
JOIN topic_lookup t ON t.slug = v.slug
ON CONFLICT DO NOTHING;
