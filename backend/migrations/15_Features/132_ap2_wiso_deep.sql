-- ============================================================================
-- Migration: 132_ap2_wiso_deep.sql
-- Description: WISO-Track massiv ausbauen. Alle 7 WISO-Topics bekommen
--              deep Content (Blurt + Cued + Application pro Topic).
--              Pascal hat WISO am 11.05.2026. BW fragt WISO sehr rechtslastig.
--              Deckt ab:
--              — Ausbildungsrecht (BBiG, JArbSchG, Probezeit, Kündigung)
--              — Marktformen (Polypol/Oligopol/Monopol + Preisbildung)
--              — Sozialversicherung (5 Säulen, Beitragssätze 2026, AG/AN-Teil)
--              — Wirtschaftspolitik (Konjunktur, Fiskal/Geldpolitik, EZB)
--              — Tarif (Tarifautonomie, Tarifvertrag, Tarifkonflikt)
--              — Rechtsgeschäft (Willenserklärung, Geschäftsfähigkeit)
--              — Kaufvertrag WISO-Seite (Abschluss, Störungen)
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-04-18
-- ============================================================================

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

-- ============================================================
-- AUSBILDUNGSRECHT
-- ============================================================

('wiso-ausbildungsrecht', 'blurt',
 'Schreibe alles auf, was du zum Ausbildungsrecht weißt: BBiG, JArbSchG, Probezeit, Kündigungsregeln, Pflichten von Azubi und Ausbilder, Vergütung, Urlaub, Arbeitszeit für Minderjährige, Abschlussprüfung, Zeugnis.',
 'BBiG (Berufsbildungsgesetz) — regelt die duale Berufsausbildung. Wichtigste Punkte:
- Schriftlicher Ausbildungsvertrag vor Beginn (§11 BBiG): Inhalt, Dauer, Ausbildungszeit, Probezeit, Vergütung, Urlaubstage, Kündigung.
- Probezeit: 1-4 Monate (§20 BBiG). In der Probezeit kann jederzeit ohne Grund und Frist gekündigt werden.
- Nach Probezeit: Kündigung durch Ausbilder nur aus wichtigem Grund (z.B. wiederholter Diebstahl) schriftlich. Azubi kann mit 4 Wochen Frist bei Berufsaufgabe oder Berufswechsel kündigen.
- Vergütung (§17 BBiG): muss angemessen sein, jährlich steigen. Mindestausbildungsvergütung seit 2020: 1. Jahr 620€ (2024), steigt jährlich.
- Urlaub: gesetzlich mind. 24 Werktage (= 4 Wochen). Für Minderjährige gilt JArbSchG: unter 16 Jahre 30 Werktage, 16-17 27, 17-18 25.

JArbSchG (Jugendarbeitsschutzgesetz) für Azubis unter 18:
- Max. 8h/Tag, 40h/Woche.
- Keine Nachtarbeit (20-6 Uhr).
- Keine Samstags-/Sonntagsarbeit (Ausnahmen: Krankenhaus, Gastronomie).
- Mindestens 12h Ruhezeit zwischen Arbeitstagen.
- 30 min Pause ab 4,5h, 60 min ab 6h.
- Berufsschulzeit zählt zur Arbeitszeit (max. 1 Tag pro Woche muss freigestellt werden).
- Ärztliche Untersuchungen vor Ausbildungsbeginn und nach 1 Jahr Pflicht.

Pflichten Azubi (§13 BBiG): Lernpflicht, Berichtsheft führen, Weisungen befolgen, Betriebsgeheimnisse wahren, Berufsschule besuchen, Prüfungen ablegen.
Pflichten Ausbilder (§14 BBiG): Ausbildungsziel erreichbar machen, kostenlose Ausbildungsmittel, Freistellung für Berufsschule + Prüfungen, Führung des Ausbildungsnachweises ermöglichen, charakterliche Förderung.

Abschluss:
- Zwischenprüfung während Ausbildung (Pflicht, nicht bestanden = kein Ausschlussgrund).
- Abschlussprüfung = gestreckte AP1 (nach ca. 2 Jahren, 20%) + AP2 (Ende, 80%). Bestehen: mind. 50% Gesamt.
- Zeugnis: Ausbildungszeugnis mit Beruf, Dauer, Fähigkeiten (§16 BBiG). Qualifiziert auf Wunsch.
- Nach bestandener Prüfung: Automatische Übernahme endet (Ausbildungsverhältnis), außer Tarifvertrag regelt Übernahme.',
 '{"required_concepts": ["BBiG schriftlicher Vertrag", "Probezeit 1-4 Monate", "Kündigung Probezeit jederzeit", "nach Probezeit nur wichtiger Grund", "Azubi 4 Wochen Frist bei Berufsaufgabe", "angemessene Vergütung jährlich steigend", "24 Werktage Urlaub gesetzlich", "JArbSchG u18 max 8h/40h", "keine Nachtarbeit 20-6", "30 Urlaubstage u16", "Berichtsheft führen", "Zwischenprüfung Abschlussprüfung AP1 AP2", "Zeugnis §16 BBiG"]}',
 '[{"criterion": "BBiG Pflichten + Kündigung", "weight": 3, "description": "Probezeit, Fristen, Azubi-Kündigung", "required": true},
   {"criterion": "JArbSchG Kernpunkte u18", "weight": 3, "description": "Arbeitszeit, Nachtarbeit, Pausen", "required": true},
   {"criterion": "Vergütung + Urlaub", "weight": 2, "description": "jährliche Steigerung, 24 Werktage", "required": true},
   {"criterion": "Pflichten beider Seiten", "weight": 2, "description": "Azubi + Ausbilder", "required": true},
   {"criterion": "Prüfungen + Zeugnis", "weight": 2, "description": "Zwischenprüfung, AP1/AP2, §16", "required": false}]',
 12, 'ki-generated-bw-wiso', 4, 900),

('wiso-ausbildungsrecht', 'cued',
 'Ein 17-jähriger Azubi hat einen Ausbildungsvertrag mit 3 Monaten Probezeit unterschrieben. In der zweiten Woche möchte er kündigen. Was gilt?',
 'In der Probezeit (§20 BBiG) kann sowohl der Auszubildende als auch der Ausbildungsbetrieb das Ausbildungsverhältnis JEDERZEIT und OHNE KÜNDIGUNGSFRIST und OHNE Angabe von Gründen kündigen.\n\nFormvorschrift: Schriftlich (§22 Abs. 3 BBiG) — E-Mail/WhatsApp reichen NICHT. Unterschrift erforderlich.\n\nBesonderheit bei Minderjährigen (unter 18):\n- Die Kündigung muss auch der gesetzliche Vertreter (Eltern) unterschreiben bzw. ihr zustimmen.\n- Alternative: Eltern kündigen selbst mit Zustimmung des Jugendlichen.\n\nFolge: Das Ausbildungsverhältnis endet mit Zugang der Kündigung beim Empfänger. Keine Abfindung. Berufsschule informiert.',
 '{"required_concepts": ["Probezeit §20 BBiG", "jederzeit ohne Grund ohne Frist", "schriftlich §22", "Minderjährige Zustimmung Eltern", "Zugang beendet"]}',
 NULL, 5, 'ki-generated-bw-wiso', 3, 360),

('wiso-ausbildungsrecht', 'application',
 'Die „Schnellinger GmbH" bildet drei Azubis aus. Ein 16-jähriger Azubi wird regelmäßig von seinem Ausbilder auch samstags eingesetzt (4h) und muss an einem Werktag bis 21 Uhr arbeiten, um einen Kundenauftrag fertigzustellen. Außerdem verlangt der Ausbilder, dass der Azubi sein Werkzeug selbst kauft.

a) Welche Gesetze sind verletzt? Nennen Sie die konkreten Paragraphen.
b) An wen kann sich der Azubi wenden?
c) Welche Konsequenzen kann das für den Ausbildungsbetrieb haben?',
 'a) Gesetzesverletzungen:

Samstagsarbeit: §16 JArbSchG verbietet Samstagsarbeit für Minderjährige grundsätzlich. Nur Ausnahmen in §16 Abs. 2 zulässig (Gastronomie, Landwirtschaft, Krankenhäuser — IT-Dienstleister gehört NICHT dazu).

Arbeitszeit bis 21 Uhr: §14 JArbSchG verbietet Arbeit nach 20:00 Uhr für Jugendliche (Ausnahmen ab 16 Jahren bis 22 Uhr in bestimmten Branchen wie Gastronomie — IT ist nicht darunter).

Werkzeugkosten: §14 Abs. 1 Nr. 3 BBiG — der Ausbildende muss dem Auszubildenden KOSTENLOS die Ausbildungsmittel (insbesondere Werkzeuge und Werkstoffe) zur Verfügung stellen, die zur Berufsausbildung und zum Ablegen der Prüfungen erforderlich sind.

b) Azubi kann sich wenden an:
1. Ausbildungsberater der zuständigen IHK (primäre Anlaufstelle bei Problemen mit dem Ausbilder).
2. Jugend- und Auszubildendenvertretung (JAV) im Betrieb, falls vorhanden.
3. Betriebsrat.
4. Gewerbeaufsichtsamt (Kontrollbehörde für Arbeitsschutz) — bei systematischen Verstößen.
5. Gewerkschaft (bei Mitgliedschaft).
6. In letzter Instanz: Arbeitsgericht.

c) Konsequenzen für den Betrieb:
1. Bußgelder: Verstöße gegen JArbSchG sind Ordnungswidrigkeiten (§58 JArbSchG), Geldbuße bis zu 15.000 €, bei wiederholten schweren Verstößen sogar Straftat (§59 JArbSchG).
2. Entzug der Ausbildungsberechtigung: Die IHK kann die Eignung des Ausbilders/Betriebs nach §32 BBiG aberkennen.
3. Schadensersatzforderungen: Azubi kann verauslagte Werkzeugkosten zurückfordern.
4. Imageschaden + Probleme bei zukünftigen Ausschreibungen mit öffentlichen Auftraggebern.
5. Aufsichtsmaßnahmen durch Gewerbeaufsichtsamt bis hin zur Betriebsuntersagung für Minderjährigen-Ausbildung.',
 '{"required_concepts": ["§16 JArbSchG keine Samstagsarbeit", "§14 JArbSchG bis 20 Uhr", "§14 BBiG kostenlose Werkzeuge", "IHK Ausbildungsberater", "JAV Betriebsrat", "Gewerbeaufsichtsamt", "§58 JArbSchG Bußgeld bis 15000", "§32 BBiG Entzug Ausbildungsberechtigung"]}',
 '[{"criterion": "3 Verstöße identifiziert", "weight": 3, "description": "Samstag/21h/Werkzeuge", "required": true},
   {"criterion": "Paragraphen genannt", "weight": 3, "description": "JArbSchG + BBiG", "required": true},
   {"criterion": "3+ Anlaufstellen", "weight": 2, "description": "IHK, JAV, Gewerbeaufsicht", "required": true},
   {"criterion": "Konsequenzen konkret", "weight": 3, "description": "Bußgeld, Berechtigung", "required": true},
   {"criterion": "Schadensersatz erwähnt", "weight": 1, "description": "Werkzeugkosten", "required": false}]',
 12, 'ki-generated-bw-wiso', 4, 1200),

-- ============================================================
-- MARKTFORMEN
-- ============================================================

('wiso-marktformen', 'cued',
 'Nennen Sie die drei Grundmarktformen nach der Zahl der Marktteilnehmer. Geben Sie für jede ein Beispiel aus der IT-Branche und beschreiben Sie das typische Preisverhalten.',
 'Grundmarktformen (Schema nach Heinrich von Stackelberg):

1. Polypol (vollkommener Markt / viele Anbieter + viele Nachfrager):
- IT-Beispiel: Kleine Web-Design-Agenturen, Freelancer-Entwickler, Webhosting-Anbieter.
- Preisverhalten: Preis bildet sich durch Angebot und Nachfrage. Einzelner Anbieter hat keine Preissetzungsmacht. Preiskampf häufig.

2. Oligopol (wenige Anbieter + viele Nachfrager):
- IT-Beispiel: Cloud-Anbieter (AWS, Azure, GCP ≈ 65% Marktanteil), Smartphone-Hersteller (Apple, Samsung, Xiaomi), Browser (Chrome, Safari, Firefox).
- Preisverhalten: Strategisches Verhalten — jeder beobachtet die Konkurrenz. Preisabsprachen möglich (kartellrechtlich verboten!). Nicht-Preis-Wettbewerb häufig (Features, Werbung). Preisführer-Muster.

3. Monopol (ein Anbieter + viele Nachfrager):
- IT-Beispiel: Microsoft Windows im Desktop-OS-Bereich (historisch), Betriebssystem iPhone iOS, öffentliche Versorgung wie Deutsche Telekom (früher).
- Preisverhalten: Monopolist kann Preis und Menge eigenständig bestimmen. Hohe Preise, geringe Menge (Monopolrente). Gefahr der Marktmissbrauch → Bundeskartellamt.

Sonderformen:
- Monopson: ein Nachfrager, viele Anbieter (z.B. Staatsbehörde als einziger Käufer).
- Duopol: genau 2 Anbieter (Sonderfall Oligopol).
- Monopolistische Konkurrenz: viele Anbieter mit differenzierten Produkten (z.B. Smartphone-Apps).',
 '{"required_concepts": ["Polypol viele Anbieter Preis durch Angebot-Nachfrage", "Oligopol wenige Anbieter strategisches Verhalten", "Monopol ein Anbieter Preis-Mengen-Macht", "IT-Beispiele AWS Microsoft", "Monopson Duopol Sonderformen", "Bundeskartellamt", "Preisabsprachen verboten"]}',
 NULL, 8, 'ki-generated-bw-wiso', 3, 480),

('wiso-marktformen', 'application',
 'Die „Agrarenergie Müller e. K." betreibt einen kleinen Webshop für Solartechnik-Zubehör. Sie stellt fest, dass drei große Online-Händler zusammen 80% des Marktes kontrollieren.

a) Um welche Marktform handelt es sich?
b) Welche Wettbewerbsstrategien stehen dem Kleinanbieter offen, um trotzdem Marktanteile zu gewinnen?
c) Woran erkennen Sie als Beobachter, ob die drei großen Händler ein illegales Preiskartell bilden?',
 'a) Marktform: Oligopol (bzw. genauer: enges Oligopol, da wenige dominante Anbieter den Großteil des Marktes halten). Die vielen kleinen Anbieter wie Agrarenergie Müller e. K. sind Randanbieter.

b) Wettbewerbsstrategien für den Kleinanbieter (Nicht-Preis-Wettbewerb, da Preiskampf gegen Große aussichtslos):
1. Differenzierung durch Spezialisierung: Nischenprodukte, die die Großen nicht führen (z.B. spezielle Wechselrichter-Adapter).
2. Persönlicher Service / Beratung: telefonische Beratung durch Fachleute, die die Großen nicht bieten.
3. Regionale Bindung: Vor-Ort-Montage-Service, schnelle Lieferung im Umkreis.
4. Bundling: Komplettpakete mit Installation, nicht nur Produktverkauf.
5. Qualitäts- und Garantieversprechen deutlich über gesetzlichem Minimum.
6. Zielgruppen-Marketing: Fachforen, Branchen-Events für Solarteure.
7. Kooperation: Einkaufsgemeinschaft mit anderen Kleinhändlern, um bessere Einkaufskonditionen zu erzielen.

c) Indizien für ein illegales Preiskartell:
1. Preisparallelität: Alle drei ändern Preise zeitgleich in gleicher Höhe/Richtung, obwohl Einkaufspreise stabil sind.
2. Identische ungewöhnliche Preisstrukturen (z.B. gleiche krumme Endzahlen, gleiche Rabattstaffeln).
3. Markt-Aufteilung: Drei Händler bedienen unauffällig verschiedene Regionen/Kundensegmente ohne Überschneidung.
4. Absprachen über Werbemaßnahmen, Messeauftritte.
5. Überhöhte Preise bei geringen Kosten-Schwankungen — klassisches Indiz.
6. Austausch sensibler Marktdaten zwischen Wettbewerbern.

Meldung und Rechtsfolgen:
- Bundeskartellamt (BKartA) in Bonn ist zuständig (§19, §20, §1 GWB — Gesetz gegen Wettbewerbsbeschränkungen).
- Geldbußen bis zu 10% des Jahresumsatzes des Unternehmens.
- Kronzeugenregelung: der erste Kartellant, der das Kartell meldet, bekommt häufig Bußgeldnachlass bis 100%.',
 '{"required_concepts": ["Oligopol enges Oligopol", "Nicht-Preis-Wettbewerb", "Differenzierung Nische", "persönlicher Service regional", "Bundling", "Preisparallelität", "identische Preisstrukturen", "Markt-Aufteilung Regionen", "§1 GWB Kartellverbot", "Bundeskartellamt", "10% Umsatz Bußgeld", "Kronzeugenregelung"]}',
 '[{"criterion": "Oligopol korrekt identifiziert", "weight": 1, "description": "eng/ Randanbieter", "required": true},
   {"criterion": "3+ Nicht-Preis-Strategien", "weight": 3, "description": "Differenzierung, Service, Nische", "required": true},
   {"criterion": "3+ Kartell-Indizien", "weight": 3, "description": "Preisparallelität, Aufteilung", "required": true},
   {"criterion": "GWB + Bundeskartellamt", "weight": 2, "description": "Rechtsfolgen", "required": true},
   {"criterion": "Kronzeugenregelung", "weight": 1, "description": "genannt", "required": false}]',
 10, 'ki-generated-bw-wiso', 4, 1200),

-- ============================================================
-- SOZIALVERSICHERUNG
-- ============================================================

('wiso-sozialversicherung', 'blurt',
 'Schreibe alles zur deutschen Sozialversicherung auf: die 5 Säulen, aktuelle Beitragssätze (2026), AG/AN-Anteil, Beitragsbemessungsgrenzen, wer ist pflichtversichert, was sind die Leistungen.',
 'Die 5 Säulen der deutschen Sozialversicherung:

1. Krankenversicherung (KV) — SGB V:
- Beitragssatz 2026: allgemein 14,6% + durchschnittlicher Zusatzbeitrag ~1,7% = ca. 16,3% (je Kasse unterschiedlich).
- Aufteilung: je zur Hälfte AG (ca. 8,15%) und AN (ca. 8,15%).
- Beitragsbemessungsgrenze (BBG) West 2026: ca. 5.362,50 €/Monat.
- Pflichtgrenze (Versicherungspflicht-Grenze): ca. 6.437,50 €/Monat.
- Leistungen: Arztbehandlung, Krankenhaus, Arznei, Rehabilitation, Krankengeld ab 7. Woche.

2. Rentenversicherung (RV) — SGB VI:
- Beitragssatz 2026: 18,6% (stabil seit Jahren).
- Aufteilung: je 9,3% AG und AN.
- BBG West: ca. 7.550 €/Monat.
- Leistungen: Altersrente (Regel-Alter 67), Erwerbsminderungsrente, Hinterbliebenenrente, medizinische Reha, berufliche Reha.

3. Arbeitslosenversicherung (ALV) — SGB III:
- Beitragssatz 2026: 2,6%.
- Aufteilung: je 1,3% AG und AN.
- BBG identisch mit RV: 7.550 €/Monat West.
- Leistungen: Arbeitslosengeld I (60-67% Netto), Qualifizierungsmaßnahmen, Arbeitsvermittlung.

4. Pflegeversicherung (PV) — SGB XI:
- Beitragssatz 2026: 3,4% (ohne Kind) / 3,6% mit Kinderlosen-Zuschlag / ab 2. Kind Ermäßigung.
- Aufteilung: je 1,7% AG und AN. Kinderlose über 23 zahlen Zuschlag 0,6% allein (AN-Teil).
- Besonderheit Sachsen: AG zahlt nur 1,2%, AN 2,2% (weil in Sachsen der Buß- und Bettag Feiertag ist).
- Leistungen: Pflegegeld, Pflegesachleistungen, Pflegegrade 1-5, stationäre Pflege.

5. Unfallversicherung (UV) — SGB VII:
- BESONDERHEIT: AG-Beitrag allein (AN zahlt nichts).
- Beitragssatz: variiert stark nach Gefahrenklasse der Branche (ca. 1-6% der Bruttolohnsumme).
- Träger: Berufsgenossenschaft der jeweiligen Branche.
- Leistungen: Behandlung + Rente bei Arbeitsunfall + Berufskrankheit.

SUMME (ohne UV, ohne Kinderlosen-Zuschlag):
16,3% KV + 18,6% RV + 2,6% ALV + 3,4% PV = 40,9% Gesamtbeitrag. AN trägt ~20,45%.

Pflichtversicherung besteht für alle abhängig Beschäftigten, deren Einkommen unter der Versicherungspflichtgrenze liegt (KV) bzw. generell (RV/ALV/PV).

Midijob-Regelung: 556€-2.000€/Monat = verringerter AN-Beitrag (Gleitzone).
Minijob: bis 556€/Monat = pauschale AG-Beiträge (15% RV + 13% KV + 2% LSt), AN nur 3,6% RV (oder Befreiung).',
 '{"required_concepts": ["5 Säulen KV RV ALV PV UV", "KV 14,6% + Zusatz ~1,7%", "RV 18,6% je 9,3%", "ALV 2,6% je 1,3%", "PV 3,4% je 1,7%", "UV nur Arbeitgeber Berufsgenossenschaft", "BBG RV 7550", "BBG KV 5362", "Pflichtgrenze 6437", "Altersrente 67", "Arbeitslosengeld 60-67%", "Pflegegrade 1-5", "Sachsen Sonderregelung", "Kinderlosen-Zuschlag", "Minijob Midijob"]}',
 '[{"criterion": "Alle 5 Säulen", "weight": 4, "description": "KV RV ALV PV UV", "required": true},
   {"criterion": "Beitragssätze korrekt", "weight": 4, "description": "± 0,5%", "required": true},
   {"criterion": "AG/AN-Aufteilung", "weight": 3, "description": "paritätisch + UV-Sonderfall", "required": true},
   {"criterion": "BBG / Pflichtgrenze", "weight": 2, "description": "RV + KV", "required": true},
   {"criterion": "Leistungen pro Säule", "weight": 3, "description": "mind. 2 pro Säule", "required": false},
   {"criterion": "Sonderformen erwähnt", "weight": 2, "description": "Mini/Midijob, Kinderlose, Sachsen", "required": false}]',
 14, 'ki-generated-bw-wiso', 4, 1200),

('wiso-sozialversicherung', 'application',
 'Ein kinderloser Arbeitnehmer (35 Jahre alt) hat ein Bruttoeinkommen von 4.800 € monatlich. Berechnen Sie seinen Netto-Sozialversicherungsbeitrag insgesamt. Zusatzbeitrag KV = 1,7% (je zur Hälfte). Angenommen werden für 2026: KV 14,6%, RV 18,6%, ALV 2,6%, PV 3,4% + 0,6% Kinderlosenzuschlag.',
 'Bruttoentgelt: 4.800 €/Monat.
Alle BBG-Grenzen liegen über 4.800 € → voller Betrag bemessungspflichtig.

Beiträge des AN (paritätisch, wenn nicht anders vermerkt):

Krankenversicherung:
- Allgemeiner Beitrag AN: 4.800 × 7,3% = 350,40 €
- Zusatzbeitrag AN-Anteil: 4.800 × 0,85% = 40,80 €
- Summe KV: 391,20 €

Rentenversicherung:
- AN-Anteil: 4.800 × 9,3% = 446,40 €

Arbeitslosenversicherung:
- AN-Anteil: 4.800 × 1,3% = 62,40 €

Pflegeversicherung:
- Grundbeitrag AN-Anteil: 4.800 × 1,7% = 81,60 €
- Kinderlosen-Zuschlag (AN allein): 4.800 × 0,6% = 28,80 €
- Summe PV: 110,40 €

Gesamt-Sozialversicherungsbeitrag AN:
391,20 + 446,40 + 62,40 + 110,40 = 1.010,40 €

Das entspricht 21,05% des Bruttos.

Der Arbeitgeber zahlt zusätzlich:
- KV: 391,20 € (abzgl. Kinderlosenzuschlag, den AN allein trägt)
  genauer: 4.800 × 7,3% + 4.800 × 0,85% = 350,40 + 40,80 = 391,20 €
- RV: 446,40 €
- ALV: 62,40 €
- PV: 81,60 € (nur Grundbeitrag, KEIN Kinderlosenzuschlag)
- UV: z.B. 2% = 96 € (branchenabhängig, AG allein)

AG-Gesamt: ca. 1.077,60 € + UV.',
 '{"required_concepts": ["KV AN 391,20", "RV AN 446,40", "ALV AN 62,40", "PV AN 110,40 mit 28,80 Zuschlag", "Summe 1010,40", "ca 21% Brutto", "Kinderlosenzuschlag AN allein", "AG paritätisch ohne Kinderloszuschlag", "UV AG allein"]}',
 '[{"criterion": "KV korrekt mit Zusatz", "weight": 2, "description": "8,15% AN-Anteil", "required": true},
   {"criterion": "RV 9,3%", "weight": 2, "description": "446,40", "required": true},
   {"criterion": "ALV 1,3%", "weight": 1, "description": "62,40", "required": true},
   {"criterion": "PV mit Zuschlag", "weight": 3, "description": "1,7% + 0,6% Kinderlos allein", "required": true},
   {"criterion": "Summe korrekt", "weight": 1, "description": "ca. 1010 €", "required": true},
   {"criterion": "AG-Seite erwähnt", "weight": 1, "description": "paritätisch + UV", "required": false}]',
 10, 'ki-generated-bw-wiso', 4, 1500),

-- ============================================================
-- WIRTSCHAFTSPOLITIK
-- ============================================================

('wiso-wirtschaftspolitik', 'cued',
 'Erläutern Sie die vier Konjunkturphasen und nennen Sie je zwei typische Merkmale. Welche wirtschaftspolitischen Instrumente setzt der Staat in einer Rezession ein?',
 'Vier Konjunkturphasen (Konjunkturzyklus):

1. Aufschwung (Expansion):
- Steigende Nachfrage, Investitionen nehmen zu.
- Beschäftigung steigt, Arbeitslosigkeit sinkt.
- Preise beginnen zu steigen, Zinsen moderat.

2. Hochkonjunktur (Boom):
- Vollbeschäftigung, Kapazitäten ausgelastet.
- Inflationsgefahr — Preise + Löhne steigen stark.
- Leitzins wird erhöht (um Überhitzung zu bremsen).

3. Abschwung (Rezession):
- Nachfrage sinkt, Produktion wird zurückgefahren.
- Arbeitslosigkeit steigt, Investitionen werden verschoben.
- Unternehmensinsolvenzen nehmen zu. Offiziell: zwei Quartale in Folge negatives BIP-Wachstum.

4. Tiefphase (Depression):
- Massive Arbeitslosigkeit, Deflationsgefahr.
- Produktion stark eingebrochen, Kapazitäten brachliegend.
- Vertrauenskrise in der Wirtschaft.

Wirtschaftspolitische Instrumente in der Rezession:

Fiskalpolitik (Staat via Bundestag/Ministerium):
- Antizyklische Ausgabenpolitik: Staat investiert (Infrastruktur, Bildung) um Nachfrage zu stützen.
- Steuersenkungen (Einkommen, MwSt temporär) um Kaufkraft zu erhöhen.
- Konjunkturprogramme (z.B. Abwrackprämie 2009, Kurzarbeitergeld in Corona-Krise).
- Erhöhung sozialer Leistungen (Transferzahlungen an Haushalte mit hoher Konsumquote).

Geldpolitik (EZB — Europäische Zentralbank):
- Leitzinssenkung → Kredite werden billiger → Investitionen werden angeregt.
- Quantitative Easing (QE): EZB kauft Staatsanleihen → Geldmenge steigt.
- Mindestreservesatz senken (Banken müssen weniger bei EZB parken).

Zielkonflikte:
- Magisches Viereck: Preisniveaustabilität, hoher Beschäftigungsstand, außenwirtschaftliches Gleichgewicht, stetiges Wachstum.
- Beispiel: Wachstum fördern vs. Inflation vermeiden.',
 '{"required_concepts": ["4 Phasen Aufschwung Boom Rezession Depression", "Merkmale je Phase Beschäftigung Preise", "Fiskalpolitik Staat Konjunkturprogramm Steuern", "Geldpolitik EZB Leitzins QE", "antizyklisch", "magisches Viereck", "zwei Quartale negatives BIP", "Transferzahlungen", "Kurzarbeitergeld Corona-Beispiel"]}',
 NULL, 8, 'ki-generated-bw-wiso', 4, 480),

-- ============================================================
-- TARIF
-- ============================================================

('wiso-tarif', 'cued',
 'Erklären Sie Tarifautonomie, Tarifvertrag, Tarifpartner und den Ablauf eines Tarifkonflikts. Welche Druckmittel haben Arbeitnehmer und Arbeitgeber?',
 'Tarifautonomie (Art. 9 Abs. 3 GG):
Das grundgesetzlich garantierte Recht der Tarifparteien (Gewerkschaften und Arbeitgeberverbände), frei von staatlicher Einflussnahme Tarifverträge abzuschließen.

Tarifvertrag (TVG — Tarifvertragsgesetz):
Schriftlicher Vertrag zwischen Gewerkschaft und Arbeitgeberverband/Einzelarbeitgeber, der Arbeitsbedingungen regelt.

Arten:
- Verbandstarifvertrag (Flächentarif): zwischen Gewerkschaft + Arbeitgeberverband, gilt für ganze Branche.
- Firmentarifvertrag / Haustarifvertrag: direkt zwischen Gewerkschaft + einzelnem Unternehmen (z.B. VW-Haustarif).
- Allgemeinverbindlicher Tarifvertrag: Staat erklärt Tarifvertrag für ganze Branche bindend (z.B. Baugewerbe).

Inhalte:
- Lohn- und Gehaltstarifvertrag: Entgelt, Gruppen, Zulagen.
- Manteltarifvertrag: längerfristig, Regeln zu Urlaub, Arbeitszeit, Kündigung.

Geltung: bindend für Tarifgebundene (Gewerkschaftsmitglieder in AG-Verbandsbetrieb). Für andere über arbeitsvertraglichen Verweis oder betrieblichen Usus.

Tarifpartner:
- Arbeitnehmerseite: Gewerkschaften (IG Metall, ver.di, IG BCE, GEW, Marburger Bund, ...).
- Arbeitgeberseite: Arbeitgeberverbände (Gesamtmetall, BDA, HDE, ...).

Ablauf Tarifkonflikt:
1. Kündigung des alten Tarifvertrags.
2. Forderungspapier der Gewerkschaft (oft 8-12% über mehrere Jahre).
3. Verhandlungen (2-4 Runden).
4. Scheitern → Urabstimmung in der Gewerkschaft (75% für Streik nötig).
5. Streik oder Aussperrung.
6. Schlichtung (unparteiischer Vermittler).
7. Einigung → neuer Tarifvertrag.

Druckmittel AN-Seite:
- Warnstreik (kurz, während Verhandlungen).
- Vollstreik (unbefristet bei Urabstimmung).
- Boykott-Aufrufe, Solidaritätsstreiks (in D rechtlich stark eingeschränkt).

Druckmittel AG-Seite:
- Aussperrung (Arbeitgeber schließt Betrieb, Arbeitnehmer bekommen keinen Lohn) — rechtlich umstritten, nur als Abwehrreaktion.
- Streikbrecher einsetzen (arbeitsrechtlich heikel).
- Betriebsverlagerung androhen.

Friedenspflicht: Während Laufzeit eines Tarifvertrags dürfen keine Streiks geführt werden.',
 '{"required_concepts": ["Tarifautonomie Art 9 GG", "Flächentarif Haustarif allgemeinverbindlich", "Lohntarif Manteltarif", "Gewerkschaft IG Metall verdi", "Arbeitgeberverband Gesamtmetall BDA", "Urabstimmung 75%", "Warnstreik Vollstreik", "Aussperrung AG", "Schlichtung", "Friedenspflicht"]}',
 NULL, 8, 'ki-generated-bw-wiso', 4, 480),

-- ============================================================
-- RECHTSGESCHÄFT / WILLENSERKLÄRUNG
-- ============================================================

('wiso-rechtsgeschaeft', 'cued',
 'Erklären Sie die Geschäftsfähigkeit nach BGB (§104-113) mit allen Stufen. Was gilt für 7-jährige, 10-jährige, 14-jährige, 17-jährige, 18-jährige, Personen unter Vormundschaft?',
 'Geschäftsfähigkeit (BGB §104-113) — drei Stufen:

1. Geschäftsunfähig (§104 BGB):
- Kinder unter 7 Jahren.
- Personen in einem dauerhaften Zustand geistiger Störung (z.B. schwere Demenz).
- KONSEQUENZ: Rechtsgeschäfte sind NICHTIG (§105).
- Ausnahme „Taschengeldparagraph" (§110) greift NICHT — gilt nur für beschränkt Geschäftsfähige.

2. Beschränkt geschäftsfähig (§106):
- 7. bis vollendetem 18. Lebensjahr (Minderjährige).
- Willenserklärungen sind grundsätzlich SCHWEBEND UNWIRKSAM bis Einwilligung/Genehmigung der gesetzlichen Vertreter (Eltern).
- AUSNAHMEN:
  a) Lediglich rechtlich vorteilhaft (§107): gilt OHNE Zustimmung (z.B. Geschenk annehmen).
  b) Taschengeldparagraph (§110): Geschäft ist wirksam, wenn Minderjähriger mit seinen Mitteln (Taschengeld) bezahlt und die Leistung bewirkt.
  c) Arbeitsverhältnis (§113): Wenn Eltern Arbeitsaufnahme erlauben, kann Minderjähriger selbstständig ähnliche Verträge abschließen.
- WICHTIG: Einseitige Rechtsgeschäfte (Kündigung!) eines Minderjährigen sind OHNE Zustimmung IMMER unwirksam, auch bei rechtlicher Vorteilhaftigkeit.

3. Voll geschäftsfähig (§2):
- Ab vollendetem 18. Lebensjahr.
- Alle Rechtsgeschäfte wirksam.

Beispiele aus dem Prompt:
- 7-jährige (Tag des 7. Geburtstags): beschränkt geschäftsfähig (§106). Kauf mit Taschengeld wirksam (§110).
- 10-jährige: beschränkt. Kauf iPhone ohne Eltern-Zustimmung schwebend unwirksam, Eltern können verweigern → nichtig.
- 14-jährige: beschränkt. Gleiche Regeln. Ausbildungsvertrag schließen nur mit Eltern-Unterschrift.
- 17-jährige: beschränkt. Kündigung Ausbildungsvertrag braucht Eltern-Zustimmung.
- 18-jährige (ab 00:00 am 18. Geburtstag): voll geschäftsfähig.
- Vormundschaft (nur noch sehr selten, meist ersetzt durch Betreuung): Einschränkung der Geschäftsfähigkeit möglich. Betreuter mit Einwilligungsvorbehalt ist in bestimmten Bereichen beschränkt geschäftsfähig.

Das frühere "Volljährigkeit" ab 21 wurde 1975 auf 18 gesenkt.',
 '{"required_concepts": ["geschäftsunfähig unter 7 §104 nichtig", "beschränkt 7-18 §106 schwebend unwirksam", "§107 lediglich rechtlich vorteilhaft", "§110 Taschengeldparagraph bewirkt", "§113 Arbeitsverhältnis", "voll ab 18", "einseitige Geschäfte Kündigung immer unwirksam", "Betreuung Einwilligungsvorbehalt"]}',
 NULL, 8, 'ki-generated-bw-wiso', 4, 480),

-- ============================================================
-- KAUFVERTRAG (WISO-Seite, ergänzt zum bestehenden kaufvertrag-Topic)
-- ============================================================

('wiso-kaufvertrag', 'application',
 'Ein Azubi (17 Jahre) kauft am Samstag einen Gaming-Laptop für 1.500 € in einem Elektronikmarkt mit seinem Taschengeld (150 €). Die restlichen 1.350 € werden als 12-Monats-Ratenkredit finanziert, den der Azubi im Laden direkt unterschreibt. Zu Hause sind die Eltern entsetzt.

a) Ist der Kaufvertrag wirksam?
b) Welche rechtlichen Möglichkeiten haben die Eltern?
c) Was ändert sich, wenn der Azubi bereits 18 Jahre alt wäre?',
 'a) Wirksamkeit:

Der Azubi ist beschränkt geschäftsfähig (§106 BGB).

Barzahlung mit Taschengeld (150 €):
Ein Teilgeschäft über 150 € aus Taschengeld wäre nach §110 BGB (Taschengeldparagraph) wirksam gewesen. Aber der gesamte Kaufvertrag ist 1.500 €, nicht 150 €.

Ratenkredit (1.350 €):
Der Ratenkreditvertrag ist ein DAUERSCHULDVERHÄLTNIS und wirtschaftlich NACHTEILHAFT (§107) — monatliche Raten mit Zinsen über 12 Monate sind keine Taschengeld-Finanzierung und die Leistung wird erst in Zukunft bewirkt. §110 greift nicht.

Damit ist der Kredit schwebend unwirksam (§108 BGB) bis zur Genehmigung der Eltern.

Folge: Der Kaufvertrag insgesamt ist schwebend unwirksam. Denn Kauf + Finanzierung sind ein "verbundenes Geschäft" — ohne Kredit würde der Azubi den Kauf nicht abschließen können.

b) Rechtliche Möglichkeiten der Eltern:
1. Verweigerung der Genehmigung (§108 BGB) → Vertrag wird endgültig nichtig. Elektronikmarkt muss das Geld zurückzahlen und bekommt den Laptop zurück.
2. Der Elektronikmarkt kann die Eltern zur Erklärung auffordern. Wenn sie nicht innerhalb von 2 Wochen genehmigen, gilt das als Verweigerung (§108 Abs. 2).
3. Stellvertreter-Argument: Die Eltern könnten alternativ nachträglich genehmigen, wenn sie den Kauf für sinnvoll halten.

c) Mit 18 Jahren wäre der Azubi voll geschäftsfähig (§2 BGB).
- Kaufvertrag ist wirksam, unabhängig von Zustimmung Dritter.
- Ratenkredit wäre ebenfalls wirksam.
- Verbraucherschutz: Ratenkredite über 200 € unterliegen dem Verbraucherkreditgesetz / §§491 ff. BGB → 14-tägiges Widerrufsrecht.
- Darüber hinaus greift bei stationärem Handel KEIN generelles Widerrufsrecht (anders als bei Online-Käufen: §312g BGB mit 14 Tagen Widerrufsrecht).

Zusammenfassung: Wegen der Minderjährigkeit ist die Situation für den Azubi glücklicherweise lösbar — seine Eltern können das Geschäft zu Fall bringen. Wäre er 18, würde er an den Vertrag gebunden bleiben und lediglich per Widerruf (14 Tage bei Kredit) zurücktreten können.',
 '{"required_concepts": ["§106 beschränkt geschäftsfähig", "§110 Taschengeld nur bei kompletter Bewirkung", "Ratenkredit dauernd schwebend unwirksam §108", "verbundenes Geschäft", "Eltern verweigern Genehmigung", "§108 Abs. 2 zwei Wochen Frist", "mit 18 voll geschäftsfähig §2", "Verbraucherkreditgesetz §491 ff", "14 Tage Widerruf Kredit", "kein Widerruf bei stationärem Handel außer Online"]}',
 '[{"criterion": "Beschränkte Geschäftsfähigkeit korrekt", "weight": 2, "description": "§106", "required": true},
   {"criterion": "Taschengeldparagraph greift nicht", "weight": 3, "description": "§110 Grenzen erkannt", "required": true},
   {"criterion": "Schwebende Unwirksamkeit", "weight": 3, "description": "§108 Kredit", "required": true},
   {"criterion": "2-Wochen-Frist der Eltern", "weight": 1, "description": "§108 Abs. 2", "required": false},
   {"criterion": "Mit 18: Widerruf 14 Tage", "weight": 2, "description": "Verbraucherkreditgesetz", "required": true},
   {"criterion": "Kein Widerruf stationär", "weight": 1, "description": "Unterscheidung", "required": false}]',
 10, 'ki-generated-bw-wiso', 5, 1500)

) AS v(slug, item_type, prompt, model_answer,
       expected_answer_structure, grading_criteria, points, source_exam, difficulty, estimated_time_sec)
JOIN topic_lookup t ON t.slug = v.slug;

-- WISO-Topics nach Wichtigkeit + Erwartungsumfang anpassen
UPDATE assessments.ap2_topics SET expected_points = 14 WHERE slug = 'wiso-sozialversicherung';
UPDATE assessments.ap2_topics SET expected_points = 12 WHERE slug = 'wiso-ausbildungsrecht';
UPDATE assessments.ap2_topics SET expected_points = 10 WHERE slug = 'wiso-marktformen';
UPDATE assessments.ap2_topics SET expected_points = 10 WHERE slug = 'wiso-kaufvertrag';

COMMIT;
