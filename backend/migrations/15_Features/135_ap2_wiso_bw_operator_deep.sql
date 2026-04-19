-- ============================================================================
-- Migration: 135_ap2_wiso_bw_operator_deep.sql
-- Description: Für ALLE 15 WISO-Topics einen neuen Multi-Step-Blurt im
--              BW-Prüfungsstil (Szenario-Firma + Teilaufgaben mit
--              IHK-Operatoren + Punkten je Teilaufgabe).
--              Plus zusätzliche Items für die 8 dünnen neuen Topics
--              (bisher nur 1-3 Items).
--
--              BW-WiSo ist FREITEXT (nicht MC wie Bayern). Prüfer fragt mit
--              Operatoren: Nennen Sie, Beschreiben Sie, Berechnen Sie,
--              Begründen Sie, Erläutern Sie, Vergleichen Sie, Bewerten Sie.
--              Aufgaben haben typisch 4-6 Teilaufgaben mit 1-6P je Teil.
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
-- 1. SOZIALVERSICHERUNG — BW-Operator-Blurt
-- ============================================================

('wiso-sozialversicherung', 'application',
 'Frau Anna Müller, 28 Jahre alt, kinderlos, arbeitet als Fachinformatikerin bei der Schnellinger GmbH. Ihr Bruttogehalt beträgt 4.200 EUR monatlich.

a) Nennen Sie die fünf Säulen der deutschen Sozialversicherung mit den gesetzlichen Grundlagen. (5P)
b) Beschreiben Sie, wie sich die Beitragslast zwischen Arbeitgeber und Arbeitnehmer grundsätzlich aufteilt. (2P)
c) Erläutern Sie die zwei Ausnahmen vom paritätischen Prinzip: Unfallversicherung und Kinderlosenzuschlag in der Pflegeversicherung. (3P)
d) Berechnen Sie den AN-Anteil zur Pflegeversicherung (2026: 1,7 % paritätisch + 0,6 % Kinderlosenzuschlag allein vom AN). (2P)
e) Begründen Sie, warum Arbeitslosen- und Rentenversicherung eine gemeinsame Beitragsbemessungsgrenze haben. (2P)',
 'a) Fünf Säulen:
1. Gesetzliche Krankenversicherung — SGB V
2. Gesetzliche Rentenversicherung — SGB VI
3. Gesetzliche Arbeitslosenversicherung — SGB III
4. Gesetzliche Pflegeversicherung — SGB XI
5. Gesetzliche Unfallversicherung — SGB VII

b) Grundsatz Paritätisch: Arbeitgeber und Arbeitnehmer tragen Beiträge je zur Hälfte (KV 7,3 + 7,3 %; RV 9,3 + 9,3 %; ALV 1,3 + 1,3 %; PV 1,7 + 1,7 %).

c) Ausnahmen:
- Unfallversicherung: AG trägt 100 % (AN zahlt nichts). Grund: UV ist Haftpflichtersatz für den AG — er würde sonst bei Arbeitsunfällen direkt haften.
- Kinderlosenzuschlag PV: Kinderlose AN ab 23 Jahren zahlen 0,6 % Zuschlag ALLEIN (nicht paritätisch). Grund: Demografischer Ausgleich — wer keine Kinder hat, zahlt mehr ins System ein.

d) PV-Berechnung Frau Müller:
Paritätischer Anteil AN: 4.200 × 1,7 % = 71,40 EUR
Kinderlosenzuschlag AN:  4.200 × 0,6 % = 25,20 EUR
Gesamt AN-Anteil PV:     96,60 EUR

e) BBG gemeinsam RV+ALV (2026: 7.550 EUR/Monat West): Historisch gewachsen, weil beide Leistungen einkommensbezogen sind (ALG I = 60/67 % Netto, Rente aus Entgeltpunkten). Deshalb muss die Bemessungsgrundlage einheitlich sein. KV und PV haben eine eigene, niedrigere BBG (2026: 5.362,50 EUR), weil das Leistungsvolumen pauschaler ist.',
 '{"required_concepts": ["5 Säulen KV RV ALV PV UV", "SGB V VI III XI VII", "paritätisch je 50%", "UV allein AG Haftpflichtersatz", "Kinderlosenzuschlag 0,6% AN", "PV Berechnung 71,40 + 25,20 = 96,60", "BBG RV/ALV identisch 7550"]}',
 '[{"criterion": "5 Säulen + SGB-Nummern", "weight": 3, "description": "alle 5 korrekt", "required": true},
   {"criterion": "Paritätisch erklärt", "weight": 1, "description": "50/50", "required": true},
   {"criterion": "UV + Kinderlos-Zuschlag", "weight": 3, "description": "beide Ausnahmen mit Grund", "required": true},
   {"criterion": "PV-Berechnung", "weight": 2, "description": "71,40 + 25,20 = 96,60", "required": true},
   {"criterion": "BBG-Begründung", "weight": 2, "description": "Einkommensbezug", "required": false}]',
 14, 'bw-stil-schnellinger-2026', 4, 1800),

-- ============================================================
-- 2. AUSBILDUNGSRECHT — BW-Operator-Blurt
-- ============================================================

('wiso-ausbildungsrecht', 'application',
 'Tim, 17 Jahre, beginnt am 01.09.2025 seine Ausbildung zum Fachinformatiker für Systemintegration bei der Agrarenergie Müller e. K. Der Ausbildungsvertrag sieht 3 Monate Probezeit, 28 Werktage Urlaub und folgende Vergütung vor: 1. Jahr 1.020 EUR, 2. Jahr 1.100 EUR, 3. Jahr 1.200 EUR, 4. Jahr 1.300 EUR.

a) Nennen Sie vier Pflichtbestandteile eines Ausbildungsvertrags nach §11 BBiG. (4P)
b) Beschreiben Sie, wie sich die Probezeit rechtlich von der Zeit nach der Probezeit unterscheidet bezüglich Kündigung. (4P)
c) Tim möchte im zweiten Ausbildungsjahr den Beruf wechseln. Erläutern Sie seine Kündigungsmöglichkeit nach §22 BBiG. (3P)
d) Begründen Sie, warum Tim als Minderjähriger den Vertrag nicht allein unterschreiben darf und welche Gesetze das regeln. (3P)
e) Bewerten Sie, ob die Urlaubsregelung von 28 Werktagen mit dem Jugendarbeitsschutzgesetz (JArbSchG §19) vereinbar ist. (2P)',
 'a) Pflichtbestandteile nach §11 BBiG (mindestens 4 nennen):
1. Art, sachliche und zeitliche Gliederung sowie Ziel der Ausbildung.
2. Beginn und Dauer der Ausbildung.
3. Ausbildungsstätte(n).
4. Dauer der regelmäßigen täglichen Ausbildungszeit.
5. Dauer der Probezeit.
6. Zahlung und Höhe der Vergütung.
7. Dauer des Urlaubs.
8. Voraussetzungen, unter denen der Vertrag gekündigt werden kann.
(Weitere zulässig: Hinweis auf Tarifverträge, Formvorschriften — §11 Abs. 3 BBiG).

b) Kündigung in der Probezeit (§22 Abs. 1 BBiG):
Jederzeit, ohne Grund, ohne Frist durch beide Seiten möglich. Schriftform Pflicht (§22 Abs. 3).

Kündigung NACH der Probezeit:
- AG: nur aus WICHTIGEM Grund fristlos (z.B. wiederholter Diebstahl). Schriftform + Begründung.
- AN: mit WICHTIGEM Grund fristlos ODER mit 4 Wochen Frist bei Aufgabe/Wechsel der Berufsausbildung.

c) Tims Kündigungsmöglichkeit für Berufswechsel (§22 Abs. 2 Nr. 2 BBiG):
Tim kann mit einer Kündigungsfrist von 4 Wochen schriftlich kündigen, wenn er die Berufsausbildung aufgeben oder sich für eine andere Berufstätigkeit ausbilden lassen will. Kein wichtiger Grund erforderlich — es reicht die Absicht. Als Minderjähriger braucht er die Zustimmung seiner Eltern (siehe d).

d) Minderjährigkeit (§2 BGB, §107 BGB):
Tim ist mit 17 Jahren beschränkt geschäftsfähig (§106 BGB). Willenserklärungen, die nicht lediglich rechtlich vorteilhaft sind (§107) — und ein Ausbildungsvertrag bindet in Pflichten — brauchen die Einwilligung der gesetzlichen Vertreter (Eltern) nach §107 BGB. Ohne Zustimmung ist der Vertrag schwebend unwirksam (§108 BGB) bis zur Genehmigung. Bei Kündigung gilt dasselbe: Eltern müssen mit-unterschreiben.

e) Urlaubsregelung 28 Werktage:
JArbSchG §19 Mindest-Urlaub: Zum 01.01. des Kalenderjahres 17 Jahre → mind. 25 Werktage. Die 28 Werktage übersteigen das Minimum → **Regelung ist zulässig**. Das Günstigkeitsprinzip greift: Vertragliche Regelungen dürfen vom Gesetz abweichen, wenn sie für den AN günstiger sind.',
 '{"required_concepts": ["§11 BBiG Pflichtbestandteile", "Art Dauer Ziel Ausbildungszeit Probezeit Vergütung Urlaub Kündigung", "§22 Probezeit jederzeit schriftlich", "§22 Abs 2 Nr 2 vier Wochen Berufswechsel", "§106 §107 §108 BGB beschränkt geschäftsfähig", "schwebend unwirksam", "§19 JArbSchG 25 Werktage", "Günstigkeitsprinzip"]}',
 '[{"criterion": "4 Pflichtbestandteile §11", "weight": 3, "description": "mind. 4 korrekt", "required": true},
   {"criterion": "Probezeit vs. danach Kündigung", "weight": 3, "description": "Unterschied klar", "required": true},
   {"criterion": "§22 Abs 2 Nr 2 Berufswechsel", "weight": 2, "description": "4 Wochen Frist", "required": true},
   {"criterion": "Minderjährigkeit BGB", "weight": 3, "description": "§106/107/108", "required": true},
   {"criterion": "JArbSchG-Prüfung", "weight": 2, "description": "25 + Günstigkeit", "required": true}]',
 16, 'bw-stil-agrarenergie-2026', 5, 2100),

-- ============================================================
-- 3. ARBEITSSCHUTZ & UNFALL — BW-Operator-Blurt (neues Topic)
-- ============================================================

('wiso-arbeitsschutz-unfall', 'application',
 'Die Schnellinger GmbH beschäftigt einen 17-jährigen Auszubildenden (Lisa) und mehrere volljährige Mitarbeiter. Im Serverraum passiert ein Unfall: Ein Mitarbeiter erleidet beim Einstecken eines Netzkabels einen Stromschlag mit leichten Brandwunden.

a) Nennen Sie die drei gesetzlichen Mindestgrenzen der täglichen Arbeitszeit für Lisa nach JArbSchG. (3P)
b) Beschreiben Sie drei konkrete Sicherheitskennzeichen nach ASR A1.3, die im Serverraum sichtbar angebracht sein sollten, mit Farbe und Form. (3P)
c) Erläutern Sie, welche Pflichten der Arbeitgeber bei einem Arbeitsunfall hat (Erste Hilfe, Meldung, Dokumentation). (4P)
d) Begründen Sie, wer bei einem Arbeitsunfall der zuständige Unfallversicherungsträger ist und wer die Kosten trägt. (3P)
e) Berechnen Sie, wie viel Urlaub Lisa laut JArbSchG §19 mindestens zusteht, wenn sie zum 01.01. des Jahres 17 Jahre alt ist. (2P)',
 'a) Drei JArbSchG-Grenzen Arbeitszeit (für unter 18):
1. Höchstarbeitszeit: 8 Stunden pro Tag und 40 Stunden pro Woche (§8 JArbSchG).
2. Keine Nachtarbeit zwischen 20:00 und 6:00 Uhr (§14 JArbSchG) — Ausnahmen ab 16 Jahren in Gastronomie etc.
3. Mindestens 12 Stunden ununterbrochene Freizeit zwischen zwei Arbeitstagen (§13 JArbSchG). Pausen: 30 min ab 4,5h, 60 min ab 6h (§11 JArbSchG).

b) Drei Sicherheitskennzeichen für Serverraum nach ASR A1.3:
1. Warnung vor elektrischer Spannung (W012): gelb-schwarzes Dreieck mit Blitzsymbol.
2. Rettungsweg / Notausgang (E002): grün-weißes Rechteck mit Laufsymbol und Pfeil.
3. Feuerlöscher (F001): rot-weißes Rechteck mit Löscher-Symbol.
(Alternativ: Verbot „Kein Wasser zum Löschen" P011; Gebot „Augenschutz benutzen" M004.)

c) Arbeitgeberpflichten bei Arbeitsunfall:
1. Erste Hilfe: Ersthelfer sofort hinzuziehen, ggf. Rettungsdienst alarmieren (112). Betriebsverbandbuch führen.
2. Meldung an BG: Unfälle mit Arbeitsausfall > 3 Tage MÜSSEN binnen 3 Tagen der Berufsgenossenschaft gemeldet werden (Unfallanzeige, §193 SGB VII).
3. Dokumentation: Verbandbuch (mind. 5 Jahre), ggf. Anzeige bei Gewerbeaufsichtsamt bei schweren Unfällen.
4. Gefährdungsbeurteilung überprüfen + Maßnahmen anpassen (§§5, 6 ArbSchG).

d) Zuständiger UV-Träger + Kosten:
Der Unfall fällt in die Zuständigkeit der BRANCHENspezifischen Berufsgenossenschaft (für IT: BGHW — Berufsgenossenschaft Handel und Warenlogistik, oder VBG — Verwaltungs-BG je nach Einstufung). Beiträge zahlt ausschließlich der Arbeitgeber (§150 SGB VII). Bei Arbeitsunfall: BG übernimmt alle Behandlungs-, Reha- und Rentenkosten — der AN zahlt nichts, auch keine KV-Zuzahlung.

e) Urlaub Lisa (17 Jahre zum 01.01.):
Nach JArbSchG §19: Mindesturlaub 27 Werktage.
(Unter 16 → 30; unter 17 → 27; unter 18 → 25. Stichtag 01.01.)',
 '{"required_concepts": ["8h/40h Woche", "20-6 Uhr keine Nachtarbeit", "12h Ruhezeit", "Warnung Gebot Rettung Brandschutz Kennzeichen", "gelb dreieck rot rechteckig grün", "Erste Hilfe", "BG Meldung 3 Tage §193 SGB VII", "Verbandbuch 5 Jahre", "AG trägt UV-Beiträge", "27 Werktage"]}',
 '[{"criterion": "3 Arbeitszeit-Grenzen", "weight": 3, "description": "8h, Nachtarbeit, Ruhezeit", "required": true},
   {"criterion": "3 Kennzeichen Farbe+Form", "weight": 3, "description": "mit Symbol", "required": true},
   {"criterion": "AG-Pflichten BG-Meldung", "weight": 4, "description": "3 Tage §193", "required": true},
   {"criterion": "UV-Träger BG", "weight": 3, "description": "Branche-BG + AG trägt", "required": true},
   {"criterion": "Urlaub 27", "weight": 2, "description": "JArbSchG §19", "required": true}]',
 15, 'bw-stil-schnellinger-2026', 4, 1800),

-- ============================================================
-- 4. BETRIEBSRAT & JAV — BW-Operator-Blurt
-- ============================================================

('wiso-betriebsrat-jav', 'application',
 'In der Schnellinger GmbH (45 Mitarbeiter, davon 4 Auszubildende) soll erstmalig ein Betriebsrat gewählt werden. Die Geschäftsführung plant zusätzlich die Einführung einer Video-Überwachung im Serverraum. Einem langjährigen Mitarbeiter (12 Jahre Betriebszugehörigkeit) soll betriebsbedingt gekündigt werden.

a) Nennen Sie die gesetzliche Grundlage für die Bildung eines Betriebsrats und ab welcher Mitarbeiterzahl. (2P)
b) Unterscheiden Sie aktives und passives Wahlrecht zum Betriebsrat. (3P)
c) Erläutern Sie, ob und warum die Geschäftsführung bei der Video-Überwachung den Betriebsrat einbeziehen muss. (4P)
d) Beschreiben Sie das Verfahren der Betriebsratsanhörung nach §102 BetrVG bei der geplanten Kündigung. Welche Rechtsfolge hat eine unterlassene Anhörung? (4P)
e) Begründen Sie, warum zusätzlich eine Jugend- und Auszubildendenvertretung (JAV) gewählt werden muss. (2P)',
 'a) Gesetzliche Grundlage: Betriebsverfassungsgesetz (BetrVG) §1. Betriebsrat kann in allen Betrieben mit mindestens **5 wahlberechtigten** Arbeitnehmern gewählt werden, von denen 3 wählbar sein müssen.

b) Wahlrechte (BetrVG §§7, 8):
Aktives Wahlrecht (wählen dürfen):
- Mindestalter 16 Jahre (seit Reform 2021).
- Betriebszugehörigkeit am Wahltag.
- Leiharbeitnehmer nach 3 Monaten Einsatzdauer.

Passives Wahlrecht (gewählt werden dürfen):
- Mindestalter 18 Jahre.
- Mindestens 6 Monate ununterbrochen im Betrieb oder Konzern.
- Leiharbeitnehmer NICHT wählbar.

c) Video-Überwachung — Mitbestimmung §87 Abs. 1 Nr. 6 BetrVG:
Technische Einrichtungen, die zur Überwachung von Verhalten oder Leistung der Arbeitnehmer geeignet sind, unterliegen der **erzwingbaren Mitbestimmung**. Der Betriebsrat muss VOR Einführung zustimmen (kein bloßes Anhörungsrecht). Ohne Einigung: Einigungsstelle entscheidet. Grund: Persönlichkeitsrecht der Arbeitnehmer, Schutz vor Leistungs-/Verhaltenskontrolle.

d) §102 BetrVG Kündigungsanhörung:
Verfahren:
1. AG teilt BR schriftlich Kündigungsabsicht mit (Gründe, Person, Sozialdaten).
2. BR hat 1 Woche Zeit zur Stellungnahme (ordentl. Kündigung) bzw. 3 Tage (außerordentl.).
3. BR kann zustimmen, schweigen (= Zustimmung), Bedenken äußern oder widersprechen.
4. Widerspruch bei ordentlicher Kündigung nur aus §102 Abs. 3 Nr. 1-5 BetrVG möglich (z.B. Sozialauswahl nicht beachtet, Weiterbeschäftigungsmöglichkeit).

Rechtsfolge bei fehlender Anhörung: Kündigung ist **unwirksam** (§102 Abs. 1 Satz 3 BetrVG) — auch wenn sachlich begründet.

e) JAV-Pflicht:
§60 BetrVG: In Betrieben mit mindestens fünf jugendlichen Arbeitnehmern unter 18 Jahren ODER Auszubildenden unter 25 Jahren ist eine JAV zu wählen. Die 4 Auszubildenden müssten noch mindestens 1 weitere jugendliche/auszubildende Person umfassen — **erst dann besteht Wahlpflicht**. Mit 4 Azubis allein reicht nicht für JAV-Pflicht (Grenze ist 5).',
 '{"required_concepts": ["BetrVG §1 ab 5 wahlberechtigte", "aktiv 16 Jahre", "passiv 18 Jahre + 6 Monate", "§87 Abs 1 Nr 6 Videoüberwachung erzwingbar", "Einigungsstelle", "§102 BetrVG Anhörung 1 Woche", "fehlende Anhörung Kündigung unwirksam", "§60 BetrVG JAV ab 5 Jugendliche"]}',
 '[{"criterion": "BetrVG §1 + 5 MA", "weight": 2, "description": "Schwelle genannt", "required": true},
   {"criterion": "Wahlrechte unterschieden", "weight": 3, "description": "Alter + Dauer", "required": true},
   {"criterion": "Mitbestimmung §87 Video", "weight": 4, "description": "erzwingbar + Einigungsstelle", "required": true},
   {"criterion": "§102 Anhörung + Folge", "weight": 4, "description": "unwirksam ohne Anhörung", "required": true},
   {"criterion": "JAV-Pflicht § 60 korrekt", "weight": 2, "description": "ab 5 Jugendliche", "required": false}]',
 15, 'bw-stil-schnellinger-betriebsrat', 4, 1800),

-- ============================================================
-- 5. RECHTSFORMEN — BW-Operator-Blurt
-- ============================================================

('wiso-rechtsformen-unternehmen', 'application',
 'Drei Freunde wollen ein IT-Systemhaus gründen. Frau Becker möchte 60.000 EUR einbringen, Herr Huber 30.000 EUR, Frau Klein 10.000 EUR. Frau Klein will nur beschränkt mit ihrer Einlage haften, die anderen wollen aktiv mitarbeiten.

a) Nennen Sie drei Rechtsformen, die grundsätzlich in Frage kommen, und ordnen Sie sie in Personen- vs. Kapitalgesellschaften ein. (3P)
b) Beschreiben Sie die Haftung bei einer GmbH und einer KG im Vergleich. (4P)
c) Erläutern Sie, welche Rechtsform am besten zur Situation der drei Gründer passt, und begründen Sie Ihre Empfehlung. (4P)
d) Berechnen Sie die Gewinnverteilung, wenn die Gründer eine GmbH gründen (Stammkapital 100.000 EUR, Einlagen wie angegeben) und im ersten Jahr einen Gewinn von 90.000 EUR ohne vertragliche Sonderregelung erzielen. (4P)
e) Begründen Sie, warum eine GmbH zwingend ins Handelsregister eingetragen werden muss und welche Abteilung dafür vorgesehen ist. (2P)',
 'a) Mögliche Rechtsformen:
- Personengesellschaften: GbR (BGB), OHG (HGB), KG (HGB).
- Kapitalgesellschaften: GmbH (GmbHG), UG haftungsbeschränkt (Mini-GmbH), AG (AktG).
In dieser Situation realistisch: KG (wegen beschränkter Haftung von Frau Klein als Kommanditistin), GmbH (alle beschränkt haftend), UG (geringes Stammkapital).

b) Haftungsvergleich:
GmbH:
- Haftung nur mit dem Gesellschaftsvermögen, nicht mit dem Privatvermögen der Gesellschafter (§13 Abs. 2 GmbHG).
- Stammeinlagen müssen aber eingezahlt werden; wenn nicht voll eingezahlt, haftet der Gesellschafter bis zur vollen Einlage.

KG:
- Komplementär: haftet UNBESCHRÄNKT mit Privatvermögen, persönlich und solidarisch.
- Kommanditist: haftet NUR bis zur Höhe seiner Einlage (§171 HGB). Nach vollständiger Einzahlung besteht keine weitere Haftung.
- Mischform: flexibel, aber Komplementär trägt volles Risiko.

c) Empfehlung + Begründung:
Frau Becker und Herr Huber wollen aktiv mitarbeiten (Geschäftsführung), Frau Klein nur beschränkt haften.
**Option 1 — GmbH**: Alle drei haften beschränkt, Becker und Huber können als Geschäftsführer bestellt werden, Klein bleibt passiver Gesellschafter. Benötigt 25.000 EUR Stammkapital (hier deutlich übererfüllt mit 100.000 EUR).
**Option 2 — KG**: Becker und Huber werden Komplementäre (haften voll), Klein Kommanditistin. Günstiger in Gründung, aber Becker + Huber tragen volles Privatrisiko — in der IT-Branche mit Kundenhaftung problematisch.
**Empfehlung: GmbH** — schützt alle drei privatrechtlich, passt zur Einlage von 100.000 EUR (= 4× Mindest-Stammkapital), signalisiert Seriosität gegenüber Kunden (B2B-IT).

d) Gewinnverteilung GmbH bei fehlender Regelung:
Gesetzlich §29 Abs. 3 GmbHG: Verteilung nach Verhältnis der Stammeinlagen.
Gesamt-Einlage: 60.000 + 30.000 + 10.000 = 100.000 EUR.
- Frau Becker: 60.000/100.000 × 90.000 = **54.000 EUR**
- Herr Huber: 30.000/100.000 × 90.000 = **27.000 EUR**
- Frau Klein: 10.000/100.000 × 90.000 = **9.000 EUR**
Kontrolle: 54 + 27 + 9 = 90 ✓

e) HR-Eintragung GmbH:
Pflicht nach §7 GmbHG + §8 HGB. Eintragung erfolgt in Abteilung **B des Handelsregisters** beim zuständigen Amtsgericht. Abteilung A ist für Personengesellschaften (Einzelunternehmer e.K., OHG, KG), Abteilung B für Kapitalgesellschaften (GmbH, AG, KGaA). Eintragung ist konstitutiv — GmbH entsteht erst mit Eintragung (§11 GmbHG). Davor nur "GmbH i. Gr." (in Gründung) mit Handelndenhaftung.',
 '{"required_concepts": ["Personen vs Kapital", "GmbH Haftung Gesellschaftsvermögen", "KG Komplementär voll Kommanditist Einlage", "§171 HGB", "Empfehlung GmbH für alle drei", "§29 GmbHG Stammeinlagen-Verhältnis", "Becker 54000 Huber 27000 Klein 9000", "HR Abt B Kapital Abt A Personen", "konstitutiv §11 GmbHG"]}',
 '[{"criterion": "3 Rechtsformen mit Einordnung", "weight": 3, "description": "Personen vs Kapital", "required": true},
   {"criterion": "Haftungsvergleich GmbH/KG", "weight": 4, "description": "Komplementär/Kommanditist", "required": true},
   {"criterion": "GmbH empfohlen + begründet", "weight": 4, "description": "mit Argumenten", "required": true},
   {"criterion": "Gewinnverteilung 54/27/9", "weight": 4, "description": "alle drei korrekt", "required": true},
   {"criterion": "HR Abt B", "weight": 2, "description": "Abteilung korrekt", "required": true}]',
 17, 'bw-stil-it-systemhaus', 5, 2400),

-- ============================================================
-- 6. KAUFVERTRAG & MÄNGEL — BW-Operator-Blurt
-- ============================================================

('wiso-kaufvertrag', 'application',
 'Die Agrarenergie Müller e. K. bestellt bei einem Großhändler 10 Server à 2.500 EUR. Nach Lieferung stellen sie fest: 2 Server funktionieren nicht, 1 Server wurde gar nicht geliefert. Der Großhändler verweigert zunächst jede Leistung.

a) Nennen Sie die zwei Willenserklärungen, die den Kaufvertrag zwischen Käufer und Verkäufer zustande kommen lassen. (2P)
b) Unterscheiden Sie die drei Arten der Kaufvertragsstörung und ordnen Sie den Fall ein. (4P)
c) Beschreiben Sie die Rangfolge der Gewährleistungsrechte des Käufers nach §437 BGB. (4P)
d) Erläutern Sie den Unterschied zwischen Gewährleistung und Garantie. (3P)
e) Berechnen Sie, um welchen Betrag sich der Rechnungsbetrag reduziert, wenn der Käufer die nicht gelieferten Server nicht annimmt und die 2 defekten vom Verkäufer zurückgenommen werden, und begründen Sie die Rechtsgrundlage. (3P)',
 'a) Zwei Willenserklärungen: **Angebot** (Antrag, §145 BGB) + **Annahme** (§147 BGB). Beide müssen übereinstimmen (= Konsens / essentialia negotii: Ware, Preis, Vertragspartner). Kaufvertrag kommt zustande sobald Annahme zugeht (§130 BGB bei Abwesenden).

b) Drei Kaufvertragsstörungen:
1. **Schlechtleistung (Mangel)** — Ware weist einen Sachmangel (§434) oder Rechtsmangel (§435) auf.
2. **Nichtleistung** — Verkäufer liefert gar nicht (Unmöglichkeit §275 oder Verzug §286).
3. **Leistungsverzug** — Lieferung nach Frist.

Im Fall:
- 2 defekte Server = SCHLECHTLEISTUNG (Sachmangel).
- 1 nicht gelieferter Server = NICHTLEISTUNG (Teil-Unmöglichkeit oder Verzug je nach Sachlage).

c) Gewährleistungsrechte §437 BGB (Rangfolge):
1. **Nacherfüllung** (§439) — Vorrang! Käufer wählt zwischen: a) Nachbesserung (Reparatur) oder b) Nachlieferung (neue mangelfreie Ware).
2. **Rücktritt** (§323, §440) — nur wenn Nacherfüllung fehlschlägt, unzumutbar ist oder verweigert wird. Rückabwicklung beider Seiten.
3. **Minderung** (§441) — statt Rücktritt: Kaufpreis wird proportional zum Mindestwert reduziert.
4. **Schadensersatz** (§280 + §437 Nr. 3) — neben oder statt Leistung; z.B. Folgeschäden.
5. Ersatz vergeblicher Aufwendungen (§284).

Wichtig: Nacherfüllung hat IMMER Vorrang. Käufer muss dem Verkäufer Nachfrist setzen.

d) Gewährleistung vs. Garantie:
**Gewährleistung** = gesetzliche Rechte des Käufers bei Mängeln (BGB §§434 ff.). Verjährung: 2 Jahre bei Neuware, 1 Jahr bei Gebrauchtware (B2B oft weiter verkürzt). Nicht verzichtbar bei Neuware gegen Verbraucher.
**Garantie** = freiwillige Zusatzzusage des Herstellers oder Verkäufers. Inhalt und Dauer frei bestimmbar (z.B. „3 Jahre Herstellergarantie ab Kauf"). Zusätzlich zur Gewährleistung — ersetzt sie nicht.

Merke: Gewährleistung = Gesetz (muss); Garantie = freiwillig (kann).

e) Reduktion des Rechnungsbetrags:
10 Server × 2.500 EUR = 25.000 EUR Gesamtrechnung.
- 1 Server nicht geliefert: 2.500 EUR entfällt (Nichtleistung → Käufer muss nicht zahlen was er nicht bekommen hat, §326 Abs. 1 BGB).
- 2 defekte Server zurückgenommen: 2 × 2.500 = 5.000 EUR entfallen (Rücktritt §437 Nr. 2 + §323 BGB — Rückabwicklung).
Reduktion gesamt: **7.500 EUR**. Neuer Rechnungsbetrag: 17.500 EUR für die 7 funktionierenden Server.

Rechtsgrundlage Kombination: §437 Nr. 2 BGB (Rücktritt) + §326 Abs. 1 (Befreiung von Gegenleistung bei Unmöglichkeit) + §323 BGB (Rücktritt bei nicht/schlecht erbrachter Leistung).',
 '{"required_concepts": ["Angebot Annahme §145 §147", "Schlechtleistung Nichtleistung Verzug", "§434 Sachmangel", "§437 Rangfolge Nacherfüllung Rücktritt Minderung Schadensersatz", "Nacherfüllung Vorrang", "Gewährleistung Gesetz 2 Jahre", "Garantie freiwillig Hersteller", "§326 Befreiung Gegenleistung", "7500 EUR Reduktion"]}',
 '[{"criterion": "Angebot + Annahme", "weight": 2, "description": "mit §", "required": true},
   {"criterion": "3 Störungen + Einordnung", "weight": 4, "description": "Schlecht-/Nicht-/Verzug", "required": true},
   {"criterion": "§437 Rangfolge 4 Rechte", "weight": 4, "description": "Nacherfüllung Vorrang", "required": true},
   {"criterion": "Gewährleistung vs Garantie", "weight": 3, "description": "Gesetz vs freiwillig", "required": true},
   {"criterion": "Berechnung 7500", "weight": 3, "description": "mit Rechtsgrundlage", "required": true}]',
 16, 'bw-stil-agrarenergie-kauf', 5, 2100),

-- ============================================================
-- 7. MARKTFORMEN — BW-Operator-Blurt
-- ============================================================

('wiso-marktformen', 'application',
 'Die Bundesrepublik Deutschland hat genau einen Anbieter für Passkarten und -papiere (die Bundesdruckerei). Für Notebooks gibt es drei große Hersteller (Dell, HP, Lenovo), die 70 % des Marktes kontrollieren. Für Brötchen existieren viele Bäckereien und viele Kunden in jeder Stadt.

a) Ordnen Sie jedem der drei Märkte die passende Marktform zu und nennen Sie das jeweilige Preisbildungsverhalten. (6P)
b) Beschreiben Sie, welche Art von Konkurrenz im Oligopol typisch ist und warum offene Preisabsprachen verboten sind. (3P)
c) Erläutern Sie das Gesetz, das in Deutschland die Wettbewerbsordnung regelt, und nennen Sie die zuständige Behörde. (3P)
d) Begründen Sie, warum ein staatliches Monopol bei sicherheitsrelevanten Dokumenten wirtschaftspolitisch gerechtfertigt sein kann. (3P)
e) Bewerten Sie, welche Strategien ein kleiner Notebook-Händler wählen kann, um im Oligopol zu überleben. (3P)',
 'a) Zuordnung Marktformen (nach Stackelberg-Schema):

Bundesdruckerei / Passkarten:
- Marktform: **Angebotsmonopol** (1 Anbieter, viele Nachfrager).
- Preisbildung: Anbieter kann Preis und Menge frei bestimmen (Monopolrente). Staatlich reguliert bei Daseinsvorsorge.

Notebook-Markt:
- Marktform: **Enges Oligopol** (wenige große Anbieter dominieren).
- Preisbildung: Strategisches Verhalten, Preisführerschaft, Nicht-Preis-Wettbewerb (Features, Design, Marketing). Preiskartelle wären verboten.

Brötchen-Markt:
- Marktform: **Polypol** (vollkommener Markt, viele Anbieter + viele Nachfrager).
- Preisbildung: Marktpreis bildet sich durch Angebot und Nachfrage. Einzelner Bäcker hat keine Preissetzungsmacht.

b) Oligopolistische Konkurrenz:
Typisch ist **strategisches Verhalten** — jeder Anbieter beobachtet die Konkurrenz genau. Da Preissenkungen nachgezogen werden (Preiskriege), weichen Anbieter oft auf **Nicht-Preis-Wettbewerb** aus: Marken-Image, Design, Features, Werbung, Kundenservice, Innovation. Offene Preisabsprachen sind nach **§1 GWB** (Gesetz gegen Wettbewerbsbeschränkungen) und Art. 101 AEUV verboten. Grund: Sie schaden dem Verbraucher durch überhöhte Preise und mindern Innovation.

c) Gesetzliche Grundlage:
**Gesetz gegen Wettbewerbsbeschränkungen (GWB)**, zuletzt novelliert 2023 (GWB-Digitalisierungsgesetz). Verbotstatbestände: Kartelle (§1), Missbrauch marktbeherrschender Stellung (§19), Fusionskontrolle (§§35 ff.).
Zuständige Behörde: **Bundeskartellamt (BKartA)** in Bonn. Sanktionen: Bußgeld bis 10 % des Jahresumsatzes, Freigabe/Untersagung von Fusionen.
EU-Ebene: Europäische Kommission (DG Competition).

d) Begründung staatliches Monopol:
1. Sicherheit: Passkarten und Personaldokumente müssen fälschungssicher sein — einheitliche Standards, Chip-Technologie, Zertifikate. Ein Monopol sichert Qualitätsstandard und verhindert Wettbewerb über Sicherheitsabstriche.
2. Daseinsvorsorge: Staatliche Hoheitsaufgabe, nicht marktfähig.
3. Skaleneffekte: Hoher Fixkostenanteil (Druckmaschinen, Zertifizierung) macht Wettbewerb ineffizient.
4. Missbrauchsschutz: Staat kann durch eigene Kontrolle Preismissbrauch vermeiden.

e) Strategien Kleinhändler im Oligopol:
1. **Nischen-Spezialisierung**: z.B. Gaming-Notebooks, Linux-Notebooks, refurbished Business-Geräte.
2. **Service-Differenzierung**: Vor-Ort-Support, 24h-Reparatur, persönliche Beratung.
3. **B2B-Fokus**: Geschäftskunden bedienen, maßgeschneiderte Konfigurationen.
4. **Geografische Bindung**: lokale Kundennähe, Reparatur- und Recycling-Service.
5. **Einkaufsgemeinschaft**: Kooperationen mit anderen Kleinhändlern für bessere Einkaufspreise.
6. **Online-Nischenshops** mit Content-Marketing (Testberichte, Fachblogs).
7. **Bundling**: Komplett-Pakete mit Software, Schulung, Service.
Verzicht auf reinen Preiskampf — dort gewinnt der Große mit Skaleneffekten.',
 '{"required_concepts": ["Monopol 1 Anbieter", "Oligopol wenige dominant", "Polypol viele Anbieter", "strategisches Verhalten", "Nicht-Preis-Wettbewerb", "§1 GWB Kartellverbot", "Bundeskartellamt", "10% Umsatz Bußgeld", "Sicherheit + Daseinsvorsorge + Skaleneffekte", "Nischen Service B2B Einkaufsgemeinschaft"]}',
 '[{"criterion": "3 Marktformen + Preisverhalten", "weight": 6, "description": "Monopol/Oligopol/Polypol", "required": true},
   {"criterion": "Oligopol-Konkurrenz + §1 GWB", "weight": 3, "description": "Nicht-Preis + Kartell-Verbot", "required": true},
   {"criterion": "GWB + BKartA + EU", "weight": 3, "description": "Institutionen", "required": true},
   {"criterion": "Monopol-Rechtfertigung", "weight": 3, "description": "Sicherheit/Daseinsvorsorge", "required": true},
   {"criterion": "3+ Nischenstrategien", "weight": 3, "description": "Differenzierung", "required": true}]',
 18, 'bw-stil-markt-analyse', 5, 2400),

-- ============================================================
-- 8. RECHTSGESCHÄFT & GESCHÄFTSFÄHIGKEIT — BW-Operator-Blurt
-- ============================================================

('wiso-rechtsgeschaeft', 'application',
 'Der 10-jährige Luis kauft mit seinem gesparten Taschengeld (80 EUR) ein Videospiel für 65 EUR. Sein 16-jähriger Bruder Kevin schließt in einem Elektromarkt einen 24-Monats-Handyvertrag (Grundgebühr 30 EUR/Monat) ab. Die 19-jährige Schwester Lara kauft einen Gebrauchtwagen für 8.000 EUR auf Ratenzahlung.

a) Ordnen Sie Luis, Kevin und Lara der jeweiligen Stufe der Geschäftsfähigkeit nach BGB zu. (3P)
b) Erläutern Sie den Taschengeldparagraphen §110 BGB und prüfen Sie Luis Kauf darauf. (4P)
c) Beschreiben Sie den Zustand „schwebende Unwirksamkeit" und prüfen Sie Kevins Handyvertrag. (4P)
d) Begründen Sie, ob Lara ein gesetzliches Widerrufsrecht bei ihrem Ratenkauf hat. (3P)
e) Beschreiben Sie die drei Arten von Rechtsgeschäften nach der Anzahl der Willenserklärungen (einseitig, mehrseitig, Vertrag) und ordnen Sie je ein Beispiel aus dem Fall zu. (3P)',
 'a) Geschäftsfähigkeitsstufen (BGB §§104-113):
- **Luis (10 Jahre)**: beschränkt geschäftsfähig (§106 BGB, 7. bis vollendetes 18. Lebensjahr).
- **Kevin (16 Jahre)**: beschränkt geschäftsfähig (§106 BGB).
- **Lara (19 Jahre)**: voll geschäftsfähig (§2 BGB, ab vollendetem 18. Lebensjahr).

b) Taschengeldparagraph §110 BGB:
Inhalt: Ein von dem Minderjährigen ohne Zustimmung des gesetzlichen Vertreters geschlossener Vertrag gilt als von Anfang an wirksam, wenn der Minderjährige die vertragsmäßige Leistung mit Mitteln bewirkt, die ihm zu diesem Zweck oder zur freien Verfügung von den gesetzlichen Vertretern oder mit deren Zustimmung von einem Dritten überlassen worden sind.

Voraussetzungen:
1. Beschränkt geschäftsfähiger Minderjähriger.
2. Mittel wurden zur freien Verfügung oder zu diesem Zweck überlassen.
3. Leistung wurde **vollständig bewirkt** (nicht auf Kredit / Raten).

Prüfung Luis: Taschengeld 80 EUR = zur freien Verfügung. Kauf 65 EUR < 80 EUR. Sofortige Bezahlung aus eigenen Mitteln = vollständige Bewirkung. **Kauf ist wirksam** nach §110 BGB — keine Elternzustimmung nötig.

c) Schwebende Unwirksamkeit (§108 BGB):
Wenn ein beschränkt Geschäftsfähiger einen Vertrag ohne Einwilligung abschließt, ist dieser Vertrag schwebend unwirksam. Das bedeutet: der Vertrag ist noch nicht wirksam, aber auch noch nicht endgültig nichtig. Er kann durch Genehmigung der gesetzlichen Vertreter nachträglich wirksam werden (§108 Abs. 1). Der Vertragspartner kann die Eltern auffordern, sich binnen 2 Wochen zu erklären (§108 Abs. 2). Genehmigen sie nicht → Vertrag ist endgültig nichtig.

Prüfung Kevin: Handyvertrag 24 Monate × 30 EUR = 720 EUR zukünftige Zahlungspflicht. Das ist nicht lediglich rechtlich vorteilhaft (§107) und nicht mit Taschengeld voll bewirkbar (§110 greift nicht, weil Leistung über 2 Jahre gestreckt). Ohne Elternzustimmung → **schwebend unwirksam**. Eltern müssen genehmigen oder verweigern.

d) Lara Ratenkauf Widerrufsrecht:
Lara ist volljährig → Vertrag ist grundsätzlich wirksam.
Widerrufsrecht:
- **Ratenkauf/Verbraucherdarlehen**: §495 + §355 BGB — 14 Tage Widerruf ab Vertragsschluss + vollständige Widerrufsbelehrung.
- Bei fehlender/fehlerhafter Widerrufsbelehrung verlängert sich die Frist.
- Widerrufsrecht gilt nur gegenüber Unternehmer, nicht bei Kauf von Privat zu Privat.

Wenn der Gebrauchtwagen bei einem gewerblichen Händler gekauft wurde **mit Finanzierung** → 14 Tage Widerruf. Bei Privatkauf ohne Finanzierung → kein Widerrufsrecht.

Wichtig: Widerrufsrecht ist nicht zu verwechseln mit dem „Recht auf 2 Wochen Umtausch" — ein solches allgemeines Rückgaberecht gibt es im deutschen Recht NUR bei Fernabsatz (Online / Versand §312g) und NICHT im stationären Handel!

e) Drei Arten Rechtsgeschäfte:
1. **Einseitiges Rechtsgeschäft**: nur EINE Willenserklärung nötig. Beispiel: Kündigung, Testament, Ausschlagung einer Erbschaft. Aus dem Fall: Keine direkte Entsprechung. (Wenn eines der Eltern Kevins Vertrag NICHT genehmigt — das wäre einseitig.)
2. **Mehrseitiges Rechtsgeschäft / Vertrag**: mindestens ZWEI übereinstimmende Willenserklärungen (Angebot + Annahme). Beispiel: Kauf, Miete, Dienst. Aus dem Fall: Luis Videospielkauf, Kevins Handyvertrag, Laras Gebrauchtwagenkauf.
3. **Beschlüsse**: mehrere parallele Willenserklärungen zum selben Zweck (Vereinsbeschluss, GmbH-Gesellschafterbeschluss). Aus dem Fall: keine Entsprechung.',
 '{"required_concepts": ["§104 geschäftsunfähig", "§106 beschränkt 7-18", "§2 voll ab 18", "§110 Taschengeld Leistung bewirkt", "Luis Kauf wirksam", "§108 schwebend unwirksam", "2 Wochen Aufforderungsfrist", "Kevin Handyvertrag schwebend", "§495 §355 14 Tage Widerruf Ratenkauf", "einseitig/Vertrag/Beschluss"]}',
 '[{"criterion": "3 Stufen zugeordnet", "weight": 3, "description": "Luis/Kevin/Lara", "required": true},
   {"criterion": "§110 Prüfung Luis", "weight": 4, "description": "Bewirkungs-Kriterium", "required": true},
   {"criterion": "Schwebende Unwirksamkeit Kevin", "weight": 4, "description": "§108 mit 2-Wo-Frist", "required": true},
   {"criterion": "Widerrufsrecht differenziert", "weight": 3, "description": "nur bei Unternehmer + Finanzierung", "required": true},
   {"criterion": "3 Arten Rechtsgeschäfte", "weight": 3, "description": "einseitig/Vertrag/Beschluss", "required": false}]',
 17, 'bw-stil-geschaeftsfaehigkeit', 5, 2100),

-- ============================================================
-- 9. BGB §622 KÜNDIGUNGSFRIST — BW-Operator-Blurt
-- ============================================================

('wiso-bgb-kuendigung-frist', 'application',
 'Die Schnellinger GmbH möchte vier Mitarbeitern ordentlich kündigen. Auszug BGB §622 (Grundkündigungsfrist 4 Wochen zum 15. oder Monatsende; verlängert bei AG-Kündigung je nach Dauer):
- 2 Jahre → 1 Monat zum Monatsende
- 5 Jahre → 2 Monate zum Monatsende
- 8 Jahre → 3 Monate zum Monatsende
- 10 Jahre → 4 Monate zum Monatsende
- 12 Jahre → 5 Monate zum Monatsende
- 15 Jahre → 6 Monate zum Monatsende

Mitarbeiter (alle sollen im Februar 2026 die Kündigung erhalten):
- Herr A: Betriebszugehörigkeit 6 Jahre
- Frau B: Betriebszugehörigkeit 13 Jahre
- Herr C: Betriebszugehörigkeit 2 Monate (noch in Probezeit von 6 Monaten)
- Frau D: Betriebszugehörigkeit 22 Jahre (neue Stufe: 7 Monate zum Monatsende)

a) Nennen Sie die Formvorschrift für eine wirksame Kündigung und benennen Sie den Paragraphen. (2P)
b) Berechnen Sie für jeden Mitarbeiter das früheste Beendigungsdatum bei Zugang der Kündigung am 15.02.2026. (8P)
c) Beschreiben Sie drei Gruppen von Arbeitnehmern mit besonderem Kündigungsschutz. (3P)
d) Erläutern Sie, was unter einer Sozialauswahl bei betriebsbedingter Kündigung zu verstehen ist und welche vier Kriterien dabei eine Rolle spielen. (4P)
e) Begründen Sie, warum §622 BGB nur Mindestfristen enthält und wovon längere Fristen abweichen können. (3P)',
 'a) Formvorschrift:
Kündigung bedarf der **schriftlichen Form** (§623 BGB). Das heißt: eigenhändige Unterschrift auf Papier. E-Mail, SMS, WhatsApp, Fax reichen nicht. Auch elektronische Form nach §126a BGB ist ausgeschlossen. Verstoß gegen §623 → Kündigung nichtig.

b) Kündigungsdatum-Berechnung (Zugang 15.02.2026):

Herr A (6 Jahre) → Stufe "5 Jahre", Frist **2 Monate zum Monatsende**.
2 Monate ab 15.02. → April. Nächstes Monatsende: **30.04.2026**.

Frau B (13 Jahre) → Stufe "12 Jahre", Frist **5 Monate zum Monatsende**.
5 Monate ab 15.02. → Juli. Nächstes Monatsende: **31.07.2026**.

Herr C (Probezeit): §622 Abs. 3 → Probezeit-Frist **2 Wochen** (ohne 15./Monatsende-Bindung). Zugang 15.02. + 2 Wochen = **01.03.2026** (Mittwoch wäre der 28.02. → Ende Frist 01.03.).
Präzise: 15.02. + 14 Tage = 01.03.2026.

Frau D (22 Jahre) → Stufe "20 Jahre", Frist **7 Monate zum Monatsende**.
7 Monate ab 15.02. → September. Nächstes Monatsende: **30.09.2026**.

c) Drei Gruppen mit besonderem Kündigungsschutz:
1. **Schwangere und Mütter** (§17 MuSchG): Kündigungsverbot während Schwangerschaft und bis 4 Monate nach Entbindung. Ausnahme: Zustimmung der Obersten Landesbehörde für Arbeitsschutz.
2. **Schwerbehinderte** (§168 SGB IX): Zustimmung des Integrationsamts erforderlich vor jeder Kündigung.
3. **Betriebsratsmitglieder** (§15 KSchG): außerordentliche Kündigung nur mit Zustimmung des Betriebsrats (§103 BetrVG) — ordentliche Kündigung faktisch ausgeschlossen.
4. Weitere: Elternzeit (§18 BEEG), Pflegezeit, Auszubildende nach Probezeit (§22 BBiG — wichtiger Grund nötig).

d) Sozialauswahl (§1 Abs. 3 KSchG):
Bei betriebsbedingter Kündigung muss der AG unter den vergleichbaren Arbeitnehmern eine Sozialauswahl treffen: der sozial am wenigsten schutzwürdige wird zuerst gekündigt. Gesetzlich vorgeschriebene Kriterien:
1. **Dauer der Betriebszugehörigkeit** (je länger, desto schutzwürdiger).
2. **Lebensalter** (je älter, desto schwerer wieder Arbeit zu finden).
3. **Unterhaltspflichten** (Kinder, unterhaltsberechtigter Partner).
4. **Schwerbehinderung** (erhöhter Schutz).

Fehlende/falsche Sozialauswahl = Kündigung unwirksam (Kündigungsschutzklage binnen 3 Wochen § 4 KSchG).

e) §622 als Mindestfrist:
§622 BGB definiert die **gesetzlichen Mindest-Kündigungsfristen**. Das heißt:
- **Tarifvertrag** kann LÄNGERE (günstigere) Fristen für AN vereinbaren → gilt dann statt §622.
- **Individueller Arbeitsvertrag** darf ebenfalls LÄNGERE Fristen enthalten, aber NICHT KÜRZERE bei Arbeitgeberkündigung (Günstigkeitsprinzip — Schutzcharakter).
- **Individueller Arbeitsvertrag** kann für AN-Kündigung KÜRZERE Fristen festlegen (dem AN muss Raum für berufliche Mobilität bleiben).
- In KLEINEREN Betrieben (bis 20 MA) sind kürzere Fristen zulässig (§622 Abs. 5).

Grund: §622 schützt das ältere und länger beschäftigte Arbeitnehmer vor plötzlichem Einkommensverlust — je länger man drin ist, desto mehr Zeit für Jobsuche. Moderne Rechtsprechung hat die frühere Unterscheidung Arbeiter/Angestellte abgeschafft.',
 '{"required_concepts": ["§623 schriftlich", "Herr A 30.04.", "Frau B 31.07.", "Herr C 01.03. Probezeit 2 Wochen", "Frau D 30.09.", "MuSchG Schwangere", "SGB IX Schwerbehinderte", "BetrVG §15 Betriebsräte", "4 Sozialauswahl-Kriterien", "Tarif verlängert", "Günstigkeitsprinzip"]}',
 '[{"criterion": "§623 Schriftform", "weight": 2, "description": "mit §", "required": true},
   {"criterion": "4 Datumsberechnungen", "weight": 8, "description": "alle korrekt", "required": true},
   {"criterion": "3 Sonderkündigungsschutz", "weight": 3, "description": "Schwanger/Behinderung/BR", "required": true},
   {"criterion": "4 Sozialauswahl-Kriterien", "weight": 4, "description": "Dauer/Alter/Unterhalt/SB", "required": true},
   {"criterion": "Mindestfrist-Begründung", "weight": 3, "description": "Tarif/Vertrag günstiger", "required": true}]',
 20, 'bw-stil-schnellinger-kuendigung', 5, 2700),

-- ============================================================
-- 10. RECHNUNGSWESEN — BW-Operator-Blurt
-- ============================================================

('wiso-rechnungswesen-kennzahlen', 'application',
 'Die Schnellinger GmbH hat im Geschäftsjahr 2025 folgende Eckdaten:
- Umsatz: 5.400.000 EUR (Vorjahr 2024: 5.000.000 EUR)
- Mitarbeiter: 45 (Vorjahr: 40)
- Nominaler Tariflohnabschluss: +3,5 %
- Durchschnittliche Inflation 2025: +4,2 %

a) Nennen Sie das Ökonomische Prinzip und unterscheiden Sie Maximal- und Minimalprinzip mit je einem Beispiel aus einem Unternehmen. (4P)
b) Berechnen Sie den Umsatz pro Mitarbeiter für beide Jahre und die prozentuale Veränderung. Runden Sie auf zwei Nachkommastellen. (4P)
c) Bewerten Sie den Tariflohnabschluss 2025 aus Sicht des Arbeitnehmers — nominal versus real. (3P)
d) Beschreiben Sie drei Kennzahlen, die typischerweise in der Betriebswirtschaftslehre zur Beurteilung der Produktivität eines Unternehmens herangezogen werden. (3P)
e) Erläutern Sie den Unterschied zwischen Umsatz, Gewinn und Cashflow. (3P)',
 'a) Ökonomisches Prinzip:
Grundsatz des rationalen Wirtschaftens — Knappheit der Mittel zwingt zur optimalen Verwendung.

**Maximalprinzip**: Mit einem GEGEBENEN Aufwand einen MAXIMALEN Ertrag erzielen.
Beispiel: Ein Unternehmen hat ein fixes IT-Budget von 100.000 EUR und versucht damit die bestmögliche Server-Ausstattung zu bekommen. Eingesetztes Kapital ist fix, Nutzen wird maximiert.

**Minimalprinzip**: Einen GEGEBENEN Ertrag mit MINIMALEM Aufwand erreichen.
Beispiel: Ein Kunde fordert einen Server mit 64 GB RAM und 8 TB Storage. Das Unternehmen sucht die günstigste Variante, die diese Spezifikation erfüllt. Ziel ist fix, Kosten werden minimiert.

Merkregel: Maximum bei fixem Input → Output maximieren. Minimum bei fixem Output → Input minimieren. NICHT gleichzeitig maximieren und minimieren (= Idealprinzip, aber ökonomisch unsinnig).

b) Umsatz pro Mitarbeiter:
2024: 5.000.000 / 40 = **125.000,00 EUR pro MA**
2025: 5.400.000 / 45 = **120.000,00 EUR pro MA**

Veränderung: (120.000 − 125.000) / 125.000 × 100 = −5.000/125.000 × 100 = **−4,00 %**.

Bewertung: Obwohl der Umsatz absolut stieg (+8 %), ist der Umsatz pro Mitarbeiter gesunken, weil die Mitarbeiterzahl schneller wuchs (+12,5 %) als der Umsatz. Die **Arbeitsproduktivität ist gesunken**.

c) Nominal vs. Real Tariflohn 2025:
Nominal: +3,5 % (mehr Geld in EUR).
Real ≈ Nominal − Inflation = 3,5 % − 4,2 % = **−0,7 %**.

Bewertung: Aus Arbeitnehmersicht ist das **faktisch eine Lohnsenkung**. Der AN bekommt zwar 3,5 % mehr Geld, kann damit aber 0,7 % weniger kaufen als im Vorjahr — die Kaufkraft sinkt. Das ist häufig Auslöser für harte Tarifauseinandersetzungen mit Forderungen oberhalb der Inflationsrate.

d) Drei Produktivitätskennzahlen:
1. **Arbeitsproduktivität** = Umsatz / Anzahl Mitarbeiter (oder Output / Arbeitsstunden). Misst Leistung pro Kopf.
2. **Kapitalproduktivität** = Umsatz / eingesetztes Kapital. Misst wie effizient das Eigen-/Fremdkapital in Umsatz umgesetzt wird.
3. **Umsatzrentabilität** = Gewinn / Umsatz × 100. Zeigt, welcher Anteil des Umsatzes als Gewinn verbleibt.
Weitere: Materialproduktivität (Output/Materialeinsatz), Eigenkapitalrentabilität (Gewinn/EK), ROI.

e) Umsatz vs. Gewinn vs. Cashflow:
**Umsatz**: Summe aller Erlöse aus Warenverkäufen und Dienstleistungen vor Kosten. Entspricht dem, was das Unternehmen brutto durch Verkauf einnimmt.
Beispiel: 5.400.000 EUR Umsatz bedeutet, dass für diesen Wert Produkte verkauft wurden.

**Gewinn**: Umsatz minus Aufwendungen (Personal, Material, Abschreibungen, Steuern). Zeigt, was rechnerisch am Ende übrigbleibt.
Beispiel: 5.400.000 Umsatz − 5.000.000 Kosten = 400.000 EUR Gewinn.

**Cashflow**: Tatsächlicher Geldzufluss minus Geldabfluss in einer Periode. Unterscheidet sich vom Gewinn, weil: a) Abschreibungen reduzieren Gewinn aber keinen Cashflow, b) Forderungen erhöhen Gewinn, aber erst bei Zahlung den Cashflow, c) Investitionen reduzieren Cashflow aber nicht direkt den Gewinn.
Wichtiger Indikator für Liquidität und Zahlungsfähigkeit.

Merksatz: "Gewinn ist Meinung, Cashflow ist Wahrheit."',
 '{"required_concepts": ["Maximalprinzip fixer Input max Output", "Minimalprinzip fixer Output min Input", "125000 und 120000 pro MA", "-4,00% Veränderung", "Real = Nominal - Inflation", "-0,7% Reallohn", "Arbeitsproduktivität Kapitalproduktivität Umsatzrentabilität", "Umsatz brutto Gewinn nach Kosten Cashflow tatsächlich"]}',
 '[{"criterion": "Max/Min-Prinzip mit Beispielen", "weight": 4, "description": "beide korrekt unterschieden", "required": true},
   {"criterion": "Umsatz/MA beide Jahre + %", "weight": 4, "description": "-4,00 % korrekt", "required": true},
   {"criterion": "Nominal vs Real Bewertung", "weight": 3, "description": "-0,7 % Kaufkraftverlust", "required": true},
   {"criterion": "3 Produktivitätskennzahlen", "weight": 3, "description": "mit Formel", "required": true},
   {"criterion": "Umsatz/Gewinn/Cashflow", "weight": 3, "description": "Unterschied klar", "required": true}]',
 17, 'bw-stil-schnellinger-rechnung', 5, 2400),

-- ============================================================
-- 11. TARIF — BW-Operator-Blurt
-- ============================================================

('wiso-tarif', 'application',
 'In der IT-Branche verhandeln ver.di und der Arbeitgeberverband Bitkom über einen neuen Flächentarifvertrag. Die Gewerkschaft fordert +8 % Lohn bei 24 Monaten Laufzeit, die Arbeitgeber bieten +4 % bei 36 Monaten. Nach der 3. Verhandlungsrunde scheitern die Gespräche.

a) Nennen Sie die rechtliche Grundlage der Tarifautonomie im deutschen Grundgesetz. (2P)
b) Unterscheiden Sie Lohn-/Gehaltstarifvertrag, Manteltarifvertrag und Rahmentarifvertrag nach Inhalt und Laufzeit. (4P)
c) Beschreiben Sie den typischen Ablauf eines Tarifkonflikts in der korrekten Reihenfolge der 6 Schritte. (5P)
d) Erläutern Sie den Unterschied zwischen Warnstreik, Streik nach Urabstimmung und Aussperrung. (4P)
e) Begründen Sie, was unter der Friedenspflicht zu verstehen ist und ab wann/bis wann sie gilt. (3P)',
 'a) Tarifautonomie:
Rechtsgrundlage: **Art. 9 Abs. 3 Grundgesetz** — Koalitionsfreiheit. Jeder hat das Recht, Vereinigungen zur Wahrung und Förderung der Arbeits- und Wirtschaftsbedingungen zu bilden (Gewerkschaften und Arbeitgeberverbände). Das Recht, eigenständig Tarifverträge abzuschließen, ist geschützt — ohne staatliche Eingriffe. Konkretisierung im TVG (Tarifvertragsgesetz).

b) Drei Tarifvertragsarten:

**Lohn- und Gehaltstarifvertrag (Entgelttarifvertrag)**:
- Inhalt: konkrete Höhe von Löhnen, Gehältern, Ausbildungsvergütungen, Zulagen.
- Laufzeit: meist 12-24 Monate (kurzfristig, da Löhne regelmäßig angepasst werden).

**Manteltarifvertrag**:
- Inhalt: allgemeine Arbeitsbedingungen — Arbeitszeit, Urlaub, Kündigungsfristen, Überstundenregelung, Sonderzahlungen wie Urlaubs- und Weihnachtsgeld, Sozialleistungen.
- Laufzeit: typisch 3-10 Jahre (langfristig — Rahmen bleibt stabil).

**Rahmentarifvertrag**:
- Inhalt: Eingruppierung von Arbeitsplätzen in Lohn-/Gehaltsgruppen, Qualifikationsmerkmale. Legt das Tarifsystem strukturell fest.
- Laufzeit: sehr langfristig (5-10+ Jahre, wird oft nur bei großen Systemreformen geändert).

Zusätzlich: **Entgeltrahmentarifvertrag (ERA)** als Moderne Bezeichnung für eine Kombination aus Rahmen- und Entgelttarif.

c) Ablauf Tarifkonflikt (typische 6 Schritte):
1. **Kündigung** des alten Tarifvertrags durch eine der Tarifparteien (meist zum Laufzeitende).
2. **Forderungsaufstellung** durch die Gewerkschaft (Beschluss der Tarifkommission), Übergabe an Arbeitgeberverband.
3. **Verhandlungsrunden** (typisch 3-5), bei denen Forderungen und Angebote ausgetauscht werden.
4. **Scheitern der Verhandlungen** oder Schlichtung: wenn Verhandlungen ohne Ergebnis, kann eine unparteiische Schlichtung versucht werden (Schlichter schlägt Kompromiss vor, beide Seiten können annehmen oder ablehnen).
5. **Urabstimmung** bei Gewerkschaftsmitgliedern: mind. 75 % Zustimmung erforderlich, damit Streik ausgerufen werden kann.
6. **Arbeitskampf (Streik/Aussperrung)** → meist endet in neuem Tarifabschluss → 7. Unterzeichnung.

d) Streikformen:
**Warnstreik**: kurze, stunden- bis tageslange Arbeitsniederlegung während laufender Tarifverhandlungen. Keine Urabstimmung nötig. Soll Druck auf Verhandlungen aufbauen.

**Urabstimmungsstreik (Vollstreik)**: unbefristete Arbeitsniederlegung NACH Urabstimmung mit mind. 75 % Zustimmung. Ziel: Tarifdurchsetzung. Streikgeld aus Gewerkschaftskasse.

**Aussperrung**: vom Arbeitgeber ausgerufener Entzug der Beschäftigung und Lohnzahlung für alle oder bestimmte Arbeitnehmer. Rechtlich nur als **ABWEHR** eines Streiks zulässig (BVerfG-Rechtsprechung). Ziel: den Streik zu verteuern, weil Gewerkschaft auch Streikgeld für Nicht-Streikende zahlen muss.

Merke: Streik = AN-Waffe; Aussperrung = AG-Waffe (nur defensiv).

e) Friedenspflicht:
Gemäß §1 TVG + Rechtsprechung gilt: **Während der Laufzeit eines Tarifvertrags dürfen keine Streiks geführt werden**, die Gegenstand des bestehenden Tarifvertrags sind. Grund: ein gültiger Tarifvertrag ist eine verbindliche Abmachung — er verliert seinen Sinn, wenn jederzeit Streik möglich wäre.

Beginn: mit Inkrafttreten des Tarifvertrags.
Ende: mit Ablauf der Laufzeit bzw. wirksamer Kündigung.

Ausnahmen:
- **Sekundäre Streiks** (Solidaritätsstreiks) in Deutschland rechtlich fast ausgeschlossen.
- **Warnstreiks während Verhandlungen** nach Ablauf des alten Tarifs sind erlaubt (Nachwirkung §4 Abs. 5 TVG).

Verstoß gegen Friedenspflicht → Schadensersatzforderung gegen Gewerkschaft / Streikende möglich (seltene Praxis, aber rechtlich möglich).',
 '{"required_concepts": ["Art 9 Abs 3 GG Koalitionsfreiheit", "TVG", "Lohntarif 12-24 Monate", "Manteltarif 3-10 Jahre", "Rahmentarif sehr langfristig", "6 Schritte Kündigung Forderung Verhandlung Scheitern Urabstimmung Streik", "75 % Urabstimmung", "Warnstreik ohne Urabstimmung", "Aussperrung Abwehr", "Friedenspflicht Laufzeit §1 TVG"]}',
 '[{"criterion": "Art 9 Abs 3 GG", "weight": 2, "description": "Koalitionsfreiheit", "required": true},
   {"criterion": "3 Tarifarten unterschieden", "weight": 4, "description": "Inhalt + Laufzeit", "required": true},
   {"criterion": "6 Schritte Reihenfolge", "weight": 5, "description": "korrekt geordnet", "required": true},
   {"criterion": "3 Streikformen", "weight": 4, "description": "Warn/Voll/Aussperrung", "required": true},
   {"criterion": "Friedenspflicht", "weight": 3, "description": "Laufzeit + Ausnahmen", "required": true}]',
 18, 'bw-stil-verdi-bitkom', 5, 2400),

-- ============================================================
-- 12. WIRTSCHAFTSPOLITIK — BW-Operator-Blurt
-- ============================================================

('wiso-wirtschaftspolitik', 'application',
 'In Deutschland meldet das Statistische Bundesamt folgende Zahlen für das erste Quartal 2026:
- BIP-Wachstum: −0,8 % (Vorjahr: +0,5 %, Vorquartal: −0,3 %)
- Inflation (HVPI): +5,2 %
- Arbeitslosenquote: 6,8 % (steigend)
- Investitionen: rückläufig

a) Nennen Sie die vier Phasen des Konjunkturzyklus und ordnen Sie die aktuelle Lage zu. (4P)
b) Beschreiben Sie die Zielkonflikte des „magischen Vierecks" anhand der vorliegenden Kennzahlen. (4P)
c) Erläutern Sie drei fiskalpolitische Maßnahmen, die die Bundesregierung ergreifen könnte, und bewerten Sie deren kurzfristige vs. langfristige Wirkung. (5P)
d) Begründen Sie, warum die EZB in dieser Situation vor einem Dilemma steht und welche Maßnahmen welche Folgen hätten. (4P)
e) Bewerten Sie, welche Situation als „Stagflation" bezeichnet wird und ob Deutschland sich darin befindet. (3P)',
 'a) Vier Konjunkturphasen:
1. **Aufschwung / Expansion**: BIP-Wachstum positiv und steigend, Investitionen nehmen zu, Arbeitslosigkeit sinkt, moderate Inflation.
2. **Boom / Hochkonjunktur**: Vollbeschäftigung, Kapazitätsauslastung maximal, Preise + Löhne steigen stark, Inflationsdruck hoch.
3. **Abschwung / Rezession**: BIP-Wachstum negativ (mind. 2 Quartale in Folge), Investitionen sinken, Arbeitslosigkeit steigt, Gewinne schrumpfen.
4. **Tiefstand / Depression**: BIP stark negativ, Massenarbeitslosigkeit, Deflationsgefahr, Unternehmensinsolvenzen.

Einordnung: BIP aktuell −0,8 % (Vorquartal bereits −0,3 %, Vorjahr noch +0,5 %) → 2 Quartale negatives Wachstum = **technische Rezession** = **Abschwung**. Noch kein Tiefstand (keine Massenpleiten, keine Deflation).

b) Magisches Viereck — Zielkonflikte:
Die vier Ziele (§1 Stabilitätsgesetz 1967):
1. Preisniveaustabilität (~2 % Inflation).
2. Hoher Beschäftigungsstand.
3. Stetiges und angemessenes Wirtschaftswachstum.
4. Außenwirtschaftliches Gleichgewicht.

„Magisch", weil alle Ziele GLEICHZEITIG kaum erreichbar sind. Typische Konflikte:

Aktuell:
- Preisniveaustabilität **verletzt**: 5,2 % Inflation (Soll: ~2 %).
- Beschäftigung **problematisch**: 6,8 % AL und steigend.
- Wachstum **verletzt**: BIP negativ.
- Außenwirtschaft: nicht beurteilbar aus Daten.

Konflikt: Maßnahmen gegen Inflation (Zinserhöhung) bremsen Wachstum zusätzlich. Maßnahmen für Wachstum (Zinssenkung, Staatsausgaben) befeuern Inflation. Daher Zielkonflikt = „magisch".

c) Drei fiskalpolitische Maßnahmen:
1. **Konjunkturprogramm (Staatsinvestitionen)**: Staat erhöht Ausgaben für Infrastruktur, Bildung, Digitalisierung.
   - Kurzfristig: stützt Nachfrage, schafft Aufträge → Beschäftigung.
   - Langfristig: Staatsverschuldung steigt, möglicher Crowding-out-Effekt.

2. **Steuersenkung (EKSt oder Unternehmenssteuer)**: Entlastet Kaufkraft bzw. Investitionstätigkeit.
   - Kurzfristig: Konsum/Investition steigen.
   - Langfristig: Steuereinnahmen fehlen → Schulden / spätere Kürzungen.

3. **Erhöhung Transferleistungen (Bürgergeld, Kindergeld, Kurzarbeitergeld)**: direkt an Haushalte mit hoher Konsumquote.
   - Kurzfristig: schnelle Nachfragebelebung, da Einkommensschwache sofort konsumieren.
   - Langfristig: Abhängigkeit von Sozialleistungen, Arbeitsanreize sinken ggf.

Bewertung: Kombination wirkt am besten. Einzelne Maßnahmen haben oft nur begrenzte Reichweite („too small to matter") oder Zielverfehlungen.

d) EZB-Dilemma:
Die EZB hat das **Primärziel Preisstabilität** (~2 % Inflation mittelfristig). Aktuell 5,2 % Inflation = massiv über Ziel.

Maßnahme A — Zinserhöhung (Anti-Inflation):
- Wirkung: Kredite verteuern sich, Investitionen/Konsum gehen zurück → Inflation sinkt.
- NACHTEIL: verschärft Rezession, Arbeitslosigkeit steigt weiter, Staatsschulden werden teurer.

Maßnahme B — Zinssenkung (Pro-Wachstum):
- Wirkung: Kredite billiger, Investitionen/Konsum steigen → Wachstum kommt zurück.
- NACHTEIL: Inflation bleibt hoch oder steigt → Kaufkraftverlust, Lohn-Preis-Spirale, Vertrauen in Geldwert erodiert.

Dilemma: EZB muss zwischen Inflationsbekämpfung (mandat-treue, aber schmerzhaft) und Wachstumsstützung (politisch erwünscht, aber mandatwidrig) wählen. In der Praxis wird die EZB der Preisstabilität Vorrang geben (höhere Zinsen akzeptieren Rezession), weil das Primärmandat vertraglich (EU-Vertrag Art. 127) festgeschrieben ist.

e) Stagflation:
**Stagflation** = gleichzeitig stagnierende oder negative Wirtschaftsentwicklung UND hohe Inflation. Kunstwort aus „Stagnation" + „Inflation".

Prüfung Deutschland Q1/2026:
- Stagnation: ✓ (BIP −0,8 %, 2 Quartale rückläufig = Rezession).
- Inflation: ✓ (5,2 % — deutlich über 2 %-Ziel).
- Arbeitslosigkeit: ✓ (steigend).

→ **Ja, das ist eine klassische Stagflation.**

Historisches Beispiel: 1973-1975 Ölkrise in der BRD (BIP negativ + Inflation > 7 %). Stagflation ist besonders problematisch, weil klassische Fiskal- und Geldpolitik immer ein Ziel verfehlt (s. EZB-Dilemma in d).',
 '{"required_concepts": ["4 Phasen Aufschwung Boom Rezession Depression", "2 Quartale negatives BIP Rezession", "magisches Viereck 4 Ziele", "§1 StabG", "Konfliktsituation", "Konjunkturprogramm Steuersenkung Transfers", "kurz vs langfristig", "EZB Preisstabilität Primärmandat", "Zinserhöhung Inflation runter Rezession schlimmer", "Stagflation Stagnation + Inflation"]}',
 '[{"criterion": "4 Phasen + Einordnung Rezession", "weight": 4, "description": "mit Kriterium 2 Quartale", "required": true},
   {"criterion": "Magisches Viereck 4 Ziele + Konflikte", "weight": 4, "description": "mit Daten belegt", "required": true},
   {"criterion": "3 Fiskalmaßnahmen + Bewertung", "weight": 5, "description": "kurz vs lang", "required": true},
   {"criterion": "EZB-Dilemma", "weight": 4, "description": "beide Maßnahmen bewertet", "required": true},
   {"criterion": "Stagflation definiert + geprüft", "weight": 3, "description": "Kunstwort + historisches Beispiel", "required": true}]',
 20, 'bw-stil-makro-2026', 5, 2700),

-- ============================================================
-- 13. AGG — BW-Operator-Blurt
-- ============================================================

('wiso-agg-diversity', 'application',
 'Die Schnellinger GmbH sucht einen neuen Systemadministrator und veröffentlicht folgende Stellenanzeige:
„Wir suchen einen dynamischen jungen Mann mit perfektem Deutsch und repräsentativem Erscheinungsbild, der körperlich belastbar ist."

Bei der Bewerbung erscheinen u.a.: eine 52-jährige Bewerberin, ein Bewerber mit leichter Gehbehinderung, ein Bewerber türkischer Herkunft.

a) Nennen Sie die acht Diskriminierungsmerkmale des Allgemeinen Gleichbehandlungsgesetzes (AGG §1). (4P)
b) Analysieren Sie die Stellenanzeige und markieren Sie die konkreten AGG-Verstöße mit Merkmal. (4P)
c) Beschreiben Sie drei unzulässige Fragen aus einem Einstellungsgespräch und begründen Sie. (3P)
d) Erläutern Sie die Rechtsfolgen eines AGG-Verstoßes nach §15 AGG für Bewerber und Unternehmen. (3P)
e) Begründen Sie, wann eine Stellenausschreibung „nur Frau" oder „nur Mann" ausnahmsweise zulässig ist, und geben Sie ein konkretes Beispiel. (3P)',
 'a) Acht Diskriminierungsmerkmale (§1 AGG):
1. Rasse / ethnische Herkunft
2. Geschlecht
3. Religion oder Weltanschauung
4. Behinderung
5. Alter
6. Sexuelle Identität
(+ ggf. implizit: Schwangerschaft, Familienstand, Elternschaft werden oft unter Geschlecht subsumiert)

Merkhilfe: „R-G-R-B-A-S" (Reime, Gesang, Reim, Ball, Anno, Sieg) oder einfach alphabetisch.

b) Analyse der Stellenanzeige:
- „jungen" → Diskriminierung wegen **Alter** (AGG §1).
- „Mann" → Diskriminierung wegen **Geschlecht** (AGG §1).
- „perfektem Deutsch" → potentielle Diskriminierung wegen **ethnischer Herkunft** (außer wenn Kenntnisse tätigkeitsrelevant; reine Deutschkenntnisse sind meist überzogen formuliert).
- „repräsentativem Erscheinungsbild" → Diskriminierung wegen **Behinderung** (Menschen mit sichtbarer Behinderung können benachteiligt werden) + Alter + Geschlecht (Schönheitsideale).
- „körperlich belastbar" → potentiell Diskriminierung wegen **Behinderung** (ausser für Jobs mit tatsächlichem körperlichem Anspruch).

Folge: Anzeige ist **mehrfach AGG-widrig**. Formulierungsvorschlag: „Wir suchen eine/n Systemadministrator/in (m/w/d) mit guten Deutschkenntnissen, Teamfähigkeit und Lernbereitschaft."

c) Drei unzulässige Fragen im Einstellungsgespräch:
1. **„Sind Sie schwanger?" / „Planen Sie eine Familie?"** — diskriminiert wegen Geschlecht. Verboten auch bei Einstellung für eine befristete Stelle, Ausnahme: Arbeitsplatz mit Tätigkeitsverbot für Schwangere (selten).
2. **„Gehören Sie einer Gewerkschaft an?"** — verletzt Koalitionsfreiheit (Art. 9 GG) und berührt Weltanschauung (AGG). Unzulässig.
3. **„Waren Sie schonmal vorbestraft?"** — nur zulässig wenn unmittelbar tätigkeitsrelevant (z.B. Vermögensdelikte bei Buchhalter). Allgemeine Frage nach allen Vorstrafen: unzulässig.

Weitere unzulässige Fragen: Krankheiten (allgemein), sexuelle Orientierung, Religion, Parteizugehörigkeit, Vermögensverhältnisse.

d) Rechtsfolgen §15 AGG:
Bei Verstoß gegen das Benachteiligungsverbot:
1. **Schadensersatz** für materielle Schäden (z.B. Bewerbungskosten, entgangenes Gehalt wenn Stelle nachweisbar erhalten hätte) — unbegrenzt.
2. **Entschädigung** für immaterielle Schäden (Schmerzensgeld-ähnlich) — **max. 3 Bruttomonatsgehälter** wenn Bewerber auch bei diskriminierungsfreier Auswahl NICHT eingestellt worden wäre.
3. **Beweiserleichterung** (§22 AGG): Bewerber muss nur Indizien vortragen, die eine Diskriminierung vermuten lassen. Dann muss der Arbeitgeber beweisen, dass KEINE Diskriminierung vorlag (Beweislastumkehr).
4. **Klagefrist**: 2 Monate ab Zugang der Ablehnung (§15 Abs. 4).

Reputationsschaden für Unternehmen nicht zu unterschätzen (Presse, Glassdoor, Arbeitgeberbewertungen).

e) Ausnahmen vom Diskriminierungsverbot:
§8 AGG — Zulässige unterschiedliche Behandlung wegen **beruflicher Anforderungen**, wenn aufgrund der Art der Tätigkeit oder der Bedingungen ihrer Ausübung ein bestimmtes Merkmal eine **wesentliche und entscheidende berufliche Anforderung** darstellt UND angemessen ist.

Konkrete Beispiele:
- Stellenausschreibung „nur Frau" für eine **Frauenhaus-Mitarbeiterin** (Schutz der Klientinnen, nur Frauen zumutbar).
- „nur Mann" für einen **Umkleideraum-Wart in einer reinen Männer-Schwimmabteilung** (Intimsphäre).
- **Schauspielerrollen** können bestimmte Merkmale voraussetzen (Alter, Geschlecht, ethnische Herkunft) — §8 Abs. 1 AGG.
- **Religionsgemeinschaften**: Ein katholischer Kindergarten darf „nur katholische ErzieherIn" verlangen (§9 AGG Tendenzbetrieb).

Kein Rechtfertigung: „Kunden bevorzugen junge Verkäufer" oder „Im Team sind nur junge Leute" → NICHT ausreichend.',
 '{"required_concepts": ["8 Diskriminierungsmerkmale AGG §1", "Rasse Geschlecht Religion Behinderung Alter sexuelle Identität", "jungen = Alter", "Mann = Geschlecht", "perfektem Deutsch = ethnische Herkunft", "Erscheinungsbild = Behinderung", "Schwangerschaft Frage verboten", "Gewerkschaftsfrage verboten", "§15 Schadensersatz + Entschädigung max 3 Monatsgehälter", "§22 Beweislastumkehr", "2 Monate Klagefrist", "§8 AGG Ausnahmen wesentliche Anforderung", "Frauenhaus Tendenzbetrieb"]}',
 '[{"criterion": "8 AGG-Merkmale", "weight": 4, "description": "alle 8", "required": true},
   {"criterion": "Anzeige analysiert + Merkmale", "weight": 4, "description": "mind. 3 Verstöße benannt", "required": true},
   {"criterion": "3 unzulässige Fragen", "weight": 3, "description": "mit Begründung", "required": true},
   {"criterion": "§15 Rechtsfolgen", "weight": 3, "description": "Schadensersatz + max 3 Monatsgehälter + Beweislast", "required": true},
   {"criterion": "§8 Ausnahmen", "weight": 3, "description": "mit Beispiel Frauenhaus etc.", "required": true}]',
 17, 'bw-stil-schnellinger-agg', 5, 2100),

-- ============================================================
-- 14. UMWELTSCHUTZ — BW-Operator-Blurt
-- ============================================================

('wiso-umweltschutz', 'application',
 'Die Schnellinger GmbH plant ein IT-Recycling-Projekt. Alte Server, Monitore und Notebooks sollen aus dem Unternehmen sowie von Privatkunden gesammelt und fachgerecht entsorgt werden. Das Unternehmen möchte das Projekt mit einem Umweltsiegel bewerben.

a) Beschreiben Sie die fünf Stufen der Abfallhierarchie nach §6 KrWG in der richtigen Reihenfolge. (5P)
b) Erläutern Sie das Verursacherprinzip und nennen Sie zwei konkrete Umsetzungsbeispiele in der IT-Branche. (4P)
c) Ordnen Sie den folgenden Umweltsiegeln die korrekte Bedeutung zu: Blauer Engel, EU-Ecolabel, FSC, FairTrade, CE-Kennzeichnung. (5P)
d) Begründen Sie, warum die CE-Kennzeichnung NICHT als Umweltsiegel beworben werden darf. (2P)
e) Erläutern Sie das ElektroG (Elektro- und Elektronikgerätegesetz) und die Pflichten eines Unternehmens bei der Rücknahme von Altgeräten. (4P)',
 'a) Fünf Stufen der Abfallhierarchie (§6 Abs. 1 KrWG — Kreislaufwirtschaftsgesetz):
1. **Vermeidung** — Abfall gar nicht erst entstehen lassen (Mehrweg, Produktdesign, Ressourceneffizienz).
2. **Vorbereitung zur Wiederverwendung** — aufbereiten für gleichen Zweck (Server aufrüsten und weiterverkaufen, Monitore reparieren).
3. **Recycling** — stoffliche Verwertung (Kupfer aus Platinen zurückgewinnen, Aluminium einschmelzen).
4. **Sonstige Verwertung**, insbesondere energetische Verwertung (Müllverbrennung mit Stromgewinnung).
5. **Beseitigung** — Deponie als letzte Option, nur wenn keine Verwertung möglich.

Merksatz: „Vermeiden vor Verwerten vor Beseitigen."

Maßstab: Das für den Schutz von Mensch und Umwelt beste Verfahren hat Vorrang (§6 Abs. 2), nicht blind die Reihenfolge.

b) Verursacherprinzip:
Wer eine Umweltbelastung verursacht, trägt die Kosten für deren Vermeidung, Beseitigung und Sanierung. Verankert u.a. in §7 KrWG, §8 BBodSchG, Art. 191 Abs. 2 AEUV.

IT-spezifische Beispiele:
1. **CO2-Abgabe und Ökostrom-Umlage**: Ein IT-Unternehmen, das Rechenzentren mit fossilem Strom betreibt, zahlt pro Tonne CO2 (aktuell 55 EUR, steigend). Alternativ: eigener Ökostrom → geringere Belastung.
2. **Rücknahmepflicht Elektroaltgeräte**: Hersteller und Importeure von IT-Hardware sind verpflichtet, die Kosten der Altgerätesammlung und Verwertung zu tragen (ElektroG, vgl. e). Verbraucher darf kostenfrei zurückgeben.
3. Alternatives Beispiel: REACH-Verordnung für Chemikalien → Hersteller von Lötverbindungen haften für Folgeschäden.

c) Umweltsiegel-Zuordnung:

**Blauer Engel**: DEUTSCHES staatliches Umweltzeichen, vergeben vom Umweltbundesamt seit 1978. Kennzeichnet Produkte, die deutlich umweltfreundlicher als vergleichbare sind (Papier, Elektrogeräte, Farben).

**EU-Ecolabel (Europäische Blume)**: EU-weites Umweltzeichen, ähnlicher Anspruch wie Blauer Engel, aber für alle 27 EU-Länder gültig. Häufig bei Reinigungsmitteln, Textilien.

**FSC (Forest Stewardship Council)**: Siegel für Holz- und Papierprodukte aus NACHHALTIGER Forstwirtschaft. Internationale NGO, keine staatliche Einrichtung.

**FairTrade**: SOZIALES Siegel (kein Umweltsiegel im engeren Sinne) — garantiert Mindestpreise und bessere Arbeitsbedingungen für Produzenten in Entwicklungsländern. Oft in Kombination mit Bio/Öko-Kriterien. Produkte: Kaffee, Schokolade, Bananen.

**CE-Kennzeichnung**: GESETZLICHE Konformitätserklärung für den EU-Binnenmarkt. Der Hersteller erklärt damit, dass das Produkt EU-Mindestanforderungen für Sicherheit, Gesundheit, EMV erfüllt. **KEIN Umweltsiegel!** Jedes Elektrogerät braucht CE, unabhängig von Öko-Eigenschaften.

d) CE ist kein Umweltsiegel, weil:
1. CE ist kein freiwilliges Qualitäts- oder Umweltsiegel, sondern eine **gesetzlich vorgeschriebene Konformitätserklärung** (Produktsicherheitsgesetz, Niederspannungsrichtlinie, EMV-Richtlinie etc.).
2. CE bedeutet lediglich, dass das Produkt die EU-Mindestanforderungen erfüllt — NICHT dass es besonders umweltfreundlich ist. Ein Notebook mit hohem Energieverbrauch trägt trotzdem CE.
3. CE basiert auf Selbsterklärung des Herstellers, nicht auf unabhängiger Prüfung durch eine Öko-Institution.

Werbung „CE-Notebook = umweltfreundlich" wäre irreführende Werbung (UWG §5) und wettbewerbsrechtlich abmahnbar.

e) ElektroG (Elektro- und Elektronikgerätegesetz):
Nationale Umsetzung der EU-WEEE-Richtlinie. Regelt die Rücknahme, Verwertung und Entsorgung von Elektro- und Elektronikaltgeräten in Deutschland.

Pflichten eines Unternehmens:
1. **Registrierungspflicht** bei der Stiftung EAR (Stiftung Elektro-Altgeräte Register) vor erstem Inverkehrbringen. Unregistriertes Inverkehrbringen = Ordnungswidrigkeit.
2. **Finanzierungspflicht**: Hersteller zahlen Garantien für die Entsorgung, werden an den Sammel- und Recyclingkosten beteiligt.
3. **Rücknahmepflicht stationärer Handel** (Ladenflächen > 400 m² Verkaufsfläche für Elektrogeräte): Altgeräte gleicher Art kostenlos zurücknehmen + kleine Altgeräte (< 25 cm) ohne Neukauf (so genanntes „0:1-Prinzip").
4. **Aufklärungspflicht**: Kunden über Rückgabemöglichkeiten informieren, Symbol „durchgestrichene Mülltonne" auf Gerät anbringen.
5. **Dokumentations- und Meldepflichten**: Mengen jährlich an Stiftung EAR melden.

Ziele: Getrenntsammlung, stoffliche Verwertung, Vermeidung gefährlicher Stoffe (Quecksilber, Blei, Cadmium).',
 '{"required_concepts": ["5 Stufen Abfallhierarchie §6 KrWG", "Vermeidung Wiederverwendung Recycling energetisch Beseitigung", "Verursacherprinzip §7 KrWG Art 191 AEUV", "CO2-Abgabe ElektroG Rücknahme", "Blauer Engel UBA seit 1978", "EU-Ecolabel", "FSC Holz nachhaltig", "FairTrade sozial nicht Umwelt", "CE gesetzlich EU-Konformität kein Umweltsiegel", "UWG §5 irreführende Werbung", "ElektroG WEEE", "Stiftung EAR Registrierung", "Rücknahmepflicht ab 400 m² stationär", "durchgestrichene Mülltonne"]}',
 '[{"criterion": "5 Stufen Reihenfolge korrekt", "weight": 5, "description": "Vermeidung zuerst", "required": true},
   {"criterion": "Verursacherprinzip + 2 IT-Beispiele", "weight": 4, "description": "CO2/Rücknahme", "required": true},
   {"criterion": "5 Siegel korrekt erklärt", "weight": 5, "description": "incl. CE als Nicht-Siegel", "required": true},
   {"criterion": "CE kein Umweltsiegel", "weight": 2, "description": "begründet", "required": true},
   {"criterion": "ElektroG + 3+ Pflichten", "weight": 4, "description": "Stiftung EAR, Rücknahme, Aufklärung", "required": true}]',
 20, 'bw-stil-schnellinger-recycling', 5, 2700),

-- ============================================================
-- 15. ORGANISATION & FÜHRUNG — BW-Operator-Blurt
-- ============================================================

('wiso-organisation-fuehrung', 'application',
 'Die Schnellinger GmbH (45 Mitarbeiter) ist als kleine IT-Beratung in Stuttgart organisiert. Der Geschäftsführer plant die Einführung einer klareren Organisationsstruktur, da Kundenaufträge immer komplexer werden und parallel ablaufen. Die Struktur soll auch größeres Wachstum ermöglichen.

a) Nennen Sie die drei Wirtschaftssektoren und ordnen Sie die Schnellinger GmbH zu. (3P)
b) Beschreiben Sie vier klassische Leitungssysteme (Einlinien, Mehrlinien, Stablinien, Matrix) mit je einem Vor- und Nachteil. (8P)
c) Erläutern Sie, welches Leitungssystem sich für eine projektorientierte IT-Beratung mit parallelen Kundenaufträgen besonders eignet, und begründen Sie. (4P)
d) Unterscheiden Sie die drei Zieldimensionen (ökonomisch, ökologisch, sozial) eines modernen Unternehmens mit je einem konkreten Ziel. (3P)
e) Beschreiben Sie drei Formen von Unternehmenszusammenschlüssen (Fusion, Konzern, Kartell) mit Unterschieden in rechtlicher Selbständigkeit. (3P)',
 'a) Wirtschaftssektoren nach Fourastié:

1. **Primärsektor (Urproduktion)**: Rohstoffgewinnung aus der Natur.
   Branchen: Landwirtschaft, Forstwirtschaft, Fischerei, Bergbau.
2. **Sekundärsektor (Verarbeitung/Industrie)**: Veredelung von Rohstoffen zu Gütern.
   Branchen: Maschinenbau, Automobilfertigung, Bauwesen, produzierendes Handwerk.
3. **Tertiärsektor (Dienstleistungen)**: Immaterielle Leistungen.
   Branchen: Handel, Banken, Versicherungen, Bildung, Gesundheit, IT-Dienstleistungen.

Einordnung Schnellinger GmbH (IT-Beratung): **Tertiärsektor**. Dienstleistungen sind immateriell, individuell zugeschnitten auf Kundenprojekte. (Manche Statistiken führen IT/Forschung als „Quartärsektor" — dann wäre das auch vertretbar.)

b) Vier Leitungssysteme:

1. **Einliniensystem**:
   - Struktur: jeder Mitarbeiter hat genau EINEN Vorgesetzten. Klarer Dienstweg top-down.
   - Vorteil: eindeutige Zuständigkeit, klare Verantwortung, einfach nachvollziehbar.
   - Nachteil: lange Informationswege, hohe Belastung der Spitze, Überlastung bei Wachstum.

2. **Mehrliniensystem (nach Taylor)**:
   - Struktur: jeder Mitarbeiter hat MEHRERE Vorgesetzte, jeweils fachlich spezialisiert.
   - Vorteil: Spezialisierung, schnelle Fachkommunikation.
   - Nachteil: widersprüchliche Weisungen, Kompetenzkonflikte.
   - In Reinform heute kaum noch gebräuchlich.

3. **Stabliniensystem**:
   - Struktur: Einlinien-Grundsystem ergänzt durch Stabsstellen (beratend, ohne Weisungsbefugnis). Stäbe: Recht, Controlling, PR, Personal.
   - Vorteil: Entlastung der Leitung durch Spezialwissen, klare Hierarchie bleibt.
   - Nachteil: Konflikte Stab (theoretisch) vs. Linie (umsetzend), Stabsflut möglich.
   - **Klassiker im deutschen Mittelstand.**

4. **Matrixorganisation**:
   - Struktur: ZWEI Vorgesetzte pro Mitarbeiter — funktional (Fachabteilung) + objektbezogen (Projekt / Produkt / Kunde).
   - Vorteil: flexibel, Parallelbearbeitung vieler Projekte, Ressourcenteilung.
   - Nachteil: Kompetenzkonflikte (wer entscheidet bei Ressourcenknappheit?), hoher Kommunikationsaufwand, Rollenkonflikte für MA.
   - Typisch: Unternehmensberatungen, IT-Dienstleister, Multiprojekt-Umgebungen.

c) Empfehlung Schnellinger GmbH:
Für projektorientierte IT-Beratung mit parallelen Kundenaufträgen eignet sich **Matrixorganisation** am besten.

Begründung:
1. **Funktionale Achse**: Fachabteilungen wie „Systemadministration", „Netzwerk", „Sicherheit" bündeln Kompetenzen und Weiterbildung.
2. **Projekt-/Kunden-Achse**: Jeder Kundenauftrag wird von einem Projektleiter verantwortet, der Mitarbeiter aus mehreren Fachabteilungen bekommt.
3. **Ressourcen-Flexibilität**: Dieselbe Netzwerk-Spezialistin kann in Kalenderwoche 1 für Kunde A, Woche 2 für Kunde B arbeiten.
4. **Skalierbarkeit**: Bei Wachstum können neue Projekte aufgesetzt werden, ohne Fachstruktur zu ändern.

Alternative Stabliniensystem: einfacher, aber bei vielen parallelen Projekten weniger flexibel. Stablinien passt eher, wenn Kunden in wiederkehrenden Schubladen bearbeitet werden.

Wichtig bei Matrix: klare Regelungen, wer Priorität setzt bei Konflikt (meist ist die Fachabteilung zuständig für fachliche Qualität, der Projektleiter für Termin und Budget). Ohne klare Regeln zerfällt Matrix in Streit.

d) Drei Zieldimensionen:

1. **Ökonomisch (wirtschaftlich)**:
   - Ziele: Gewinnmaximierung, Umsatzwachstum, Rentabilität, Liquidität, Marktanteil, Shareholder Value.
   - Beispiel Schnellinger GmbH: „Umsatzwachstum 10 % p.a. in den nächsten 3 Jahren."

2. **Ökologisch (Umwelt)**:
   - Ziele: Ressourcenschonung, CO2-Reduktion, Kreislaufwirtschaft, Biodiversität.
   - Beispiel Schnellinger GmbH: „Bis 2028 CO2-neutrales Rechenzentrum durch 100 % Ökostrom."

3. **Sozial (gesellschaftlich / ethisch)**:
   - Ziele: Mitarbeiterzufriedenheit, Diversität, Weiterbildung, faire Bezahlung, Work-Life-Balance, gesellschaftliches Engagement.
   - Beispiel Schnellinger GmbH: „Mitarbeiterfluktuation unter 5 %, 2 Tage Weiterbildung pro Jahr, flexibles Home-Office."

Moderne Nachhaltigkeits-Konzepte (Triple Bottom Line, ESG) integrieren alle drei Dimensionen. Zielkonflikte möglich: z.B. Gewinnmaximierung (ökonomisch) vs. hohe Löhne (sozial).

e) Drei Unternehmenszusammenschlüsse:

1. **Fusion (Verschmelzung, UmwG)**:
   - Zwei Unternehmen verschmelzen zu einer Einheit. EINE behält Rechtspersönlichkeit, die andere(n) gehen unter.
   - Rechtliche Selbständigkeit: ALLE beteiligten verlieren ihre bisherige Rechtsform; es entsteht ein neues Unternehmen ODER das aufnehmende führt den anderen fort.
   - Beispiel: Daimler-Benz + Chrysler → DaimlerChrysler AG (1998).

2. **Konzern (AktG §18)**:
   - Mehrere rechtlich selbständige Unternehmen werden unter einheitlicher Leitung zusammengefasst (Mutter + Tochter(n)).
   - Rechtliche Selbständigkeit: BLEIBT ERHALTEN — jede Gesellschaft hat eigene Rechtspersönlichkeit, eigene Bilanz, eigene Haftung.
   - Einheitliche Leitung durch Weisungs- oder Beherrschungsvertrag oder Mehrheitsbeteiligung.
   - Beispiel: Bosch-Konzern mit vielen selbständigen Tochtergesellschaften.

3. **Kartell**:
   - Zusammenschluss rechtlich und wirtschaftlich selbständiger Unternehmen zur Beschränkung des Wettbewerbs (Preis-, Gebiets-, Quoten-Kartell).
   - Rechtliche Selbständigkeit: BLEIBT vollständig ERHALTEN. Nur bestimmte Marktverhaltensweisen werden abgestimmt.
   - **Grundsätzlich verboten** in Deutschland (§1 GWB) und EU (Art. 101 AEUV). Ausnahmen nur restriktiv.
   - Beispiel LKW-Kartell 2016: EU-Kommission verhängte 2,93 Mrd. EUR Bußgeld gegen Daimler, MAN, Volvo, DAF, Iveco für illegale Preisabsprachen.

Weitere Formen (nicht gefragt, aber wichtig): Konzern → auch als Horizontal- und Vertikalkonzern; Joint Venture (gemeinsames Tochterunternehmen); Strategische Allianz (Kooperation ohne Zusammenschluss).',
 '{"required_concepts": ["3 Sektoren Primär Sekundär Tertiär", "IT-Beratung Tertiär", "Einlinie Mehrlinie Stablinie Matrix mit Vor-/Nachteil", "Stablinie Mittelstand-Klassiker", "Matrix funktional + objekt", "Empfehlung Matrix begründet", "Drei Ziele ökonomisch ökologisch sozial mit Beispiel", "Fusion Rechtspersönlichkeit verloren", "Konzern rechtlich selbständig einheitliche Leitung §18 AktG", "Kartell selbständig §1 GWB verboten", "LKW-Kartell Beispiel"]}',
 '[{"criterion": "3 Sektoren + Zuordnung", "weight": 3, "description": "Tertiär korrekt", "required": true},
   {"criterion": "4 Leitungssysteme + Vor/Nachteil", "weight": 8, "description": "alle 4 mit je 1 Vor/1 Nach", "required": true},
   {"criterion": "Matrix empfohlen + begründet", "weight": 4, "description": "mit Projekt-Argument", "required": true},
   {"criterion": "3 Zieldimensionen + Beispiele", "weight": 3, "description": "ökonomisch/ökologisch/sozial", "required": true},
   {"criterion": "3 Zusammenschlüsse + Selbständigkeit", "weight": 3, "description": "Fusion/Konzern/Kartell unterschieden", "required": true}]',
 21, 'bw-stil-schnellinger-organisation', 5, 2700)

) AS v(slug, item_type, prompt, model_answer,
       expected_answer_structure, grading_criteria, points, source_exam, difficulty, estimated_time_sec)
JOIN topic_lookup t ON t.slug = v.slug;

COMMIT;
