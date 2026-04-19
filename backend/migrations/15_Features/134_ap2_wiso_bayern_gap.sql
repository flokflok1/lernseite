-- ============================================================================
-- Migration: 134_ap2_wiso_bayern_gap.sql
-- Description: Schließt WISO-Lücken basierend auf Bayern-AP2-Prüfungen 2021-2025.
--              WICHTIG: IHK-WiSo ist BUNDESEINHEITLICH (ZPA Nord-West) — Bayern
--              bekommt exakt denselben Aufgabensatz wie BW. Daher 1:1 übertragbar.
--
--              8 neue Topics + 14 neue Items (deckt die in Bayern-Prüfungen
--              regelmäßig wiederkehrenden Themen ab die bisher fehlten):
--              — wiso-arbeitsschutz-unfall (JArbSchG, MuSchG, Kennzeichen, BG)
--              — wiso-betriebsrat-jav (BetrVG §102, Mitbestimmung)
--              — wiso-rechtsformen-unternehmen (GmbH/KG/AG/eG + Gewinnverteilung)
--              — wiso-agg-diversity (AGG §1, zulässige Fragen Einstellung)
--              — wiso-umweltschutz (Verursacherprinzip, Siegel, Hierarchie)
--              — wiso-rechnungswesen-kennzahlen (Umsatz/MA, Real-Nominal)
--              — wiso-organisation-fuehrung (Leitungssysteme, Sektoren)
--              — wiso-bgb-kuendigung-frist (§622-Staffelung, Datumsrechnung)
--
--              Plus 4 konkrete Aufgaben 1:1 aus Sommer-2025-BW-Prüfung.
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-04-18
-- ============================================================================

-- ============================================================================
-- Teil 1: Neue WISO-Topics anlegen
-- ============================================================================

INSERT INTO assessments.ap2_topics
    (slug, name_de, name_en, bereich, priority, expected_points, description)
VALUES

('wiso-arbeitsschutz-unfall',
 'Arbeitsschutz, Mutterschutz & Unfallverhütung',
 'Occupational Safety & Accident Prevention',
 'WISO', 'sehr-hoch', 10,
 'JArbSchG, MuSchG, ArbSchG, BG-Meldung, Sicherheitskennzeichen, Erste Hilfe, Feuerlöscher. Kommt in ALLEN Bayern-Prüfungen 2022-2025 mit 3-4 Aufgaben vor.'),

('wiso-betriebsrat-jav',
 'Betriebsrat & Jugendvertretung (BetrVG)',
 'Works Council & Youth Representation',
 'WISO', 'sehr-hoch', 10,
 'BetrVG §102 Anhörung, Mitbestimmungsrechte, Wahlvoraussetzungen, JAV unter 25, Betriebsversammlung, Betriebsvereinbarung vs. Tarifvertrag.'),

('wiso-rechtsformen-unternehmen',
 'Rechtsformen & Gewinnverteilung',
 'Corporate Legal Forms',
 'WISO', 'sehr-hoch', 10,
 'Einzelunternehmen, GbR, OHG, KG (Komplementär/Kommanditist), GmbH (25k Stammkapital), AG, eG. Haftung, Geschäftsführung, Gewinnverteilung nach Einlagen (Rechenaufgabe!).'),

('wiso-agg-diversity',
 'AGG & Gleichbehandlung',
 'General Equal Treatment Act',
 'WISO', 'hoch', 6,
 'AGG §1 Diskriminierungsmerkmale, zulässige Fragen im Einstellungsgespräch, Stellenanzeigen-Prüfung, Charta der Vielfalt.'),

('wiso-umweltschutz',
 'Umweltschutz & Nachhaltigkeit',
 'Environmental Protection',
 'WISO', 'hoch', 6,
 'Verursacherprinzip, Kreislaufwirtschaftsgesetz, Abfallhierarchie (Vermeidung vor Recycling), Umweltsiegel (Blauer Engel, FairTrade, CE).'),

('wiso-rechnungswesen-kennzahlen',
 'Rechnungswesen & Wirtschaftskennzahlen',
 'Accounting & Business Metrics',
 'WISO', 'sehr-hoch', 8,
 'Umsatz pro Mitarbeiter + %-Veränderung, wirtschaftlichster Auftrag (Ertrag/Aufwand), Real- vs. Nominaleinkommen bei Inflation, Ökonomisches Prinzip (Max/Min).'),

('wiso-organisation-fuehrung',
 'Unternehmensorganisation',
 'Company Organization',
 'WISO', 'hoch', 6,
 'Leitungssysteme (Einlinien, Mehrlinien, Stablinien, Matrix), 3 Wirtschaftssektoren, Unternehmenszusammenschlüsse (Fusion/Kartell/Konzern), Unternehmensziele.'),

('wiso-bgb-kuendigung-frist',
 'BGB §622 Kündigungsfristen',
 'Notice Periods §622 BGB',
 'WISO', 'sehr-hoch', 8,
 'Staffelung nach Beschäftigungsdauer (2 Wochen Probezeit → bis 7 Monate zum Quartalsende bei 20+ Jahren). Datumsrechnung. Betriebsbedingte Kündigung, Sozialauswahl, KSchG, besonderer Kündigungsschutz.')

ON CONFLICT (slug) DO UPDATE
SET priority = EXCLUDED.priority,
    expected_points = EXCLUDED.expected_points,
    description = EXCLUDED.description;

-- ============================================================================
-- Teil 2: Learning Items für die neuen Topics
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
-- ARBEITSSCHUTZ & UNFALL
-- ============================================================

('wiso-arbeitsschutz-unfall', 'cued',
 'Welche Sicherheitskennzeichen nach ASR A1.3 gibt es? Nennen Sie die 5 Kategorien mit je Farbe, Form und einem konkreten Beispiel.',
 '1. Verbotszeichen — rund, rot-weiß mit Querbalken, schwarzes Symbol. Beispiel: "Rauchen verboten" (P002), "Für Fußgänger verboten" (P004).

2. Gebotszeichen — rund, blau-weiß. Beispiel: "Augenschutz benutzen" (M004), "Handschutz benutzen" (M009).

3. Warnzeichen — dreieckig, gelb-schwarz. Beispiel: "Warnung vor elektrischer Spannung" (W012), "Warnung vor heißer Oberfläche" (W017).

4. Rettungszeichen — quadratisch/rechteckig, grün-weiß. Beispiel: "Rettungsweg" (E001/E002), "Erste-Hilfe-Kasten" (E003), "Notausgang".

5. Brandschutzzeichen — quadratisch/rechteckig, rot-weiß. Beispiel: "Feuerlöscher" (F001), "Brandmelder" (F005), "Löschschlauch" (F002).

Zusatz: Hinweiszeichen (blau-weiß-schwarz, rechteckig) sind keine eigene ASR-Kategorie, werden aber häufig mit genannt.',
 '{"required_concepts": ["5 Kategorien", "Verbot rot rund", "Gebot blau rund", "Warnung gelb dreieck", "Rettung grün rechteckig", "Brandschutz rot rechteckig", "Beispiele je Kategorie"]}',
 NULL, 7, 'bayern-S2022-A23', 3, 420),

('wiso-arbeitsschutz-unfall', 'cued',
 'Nach welchem Prinzip gilt die Urlaubs-Staffelung nach JArbSchG §19 für minderjährige Azubis?',
 'JArbSchG §19 — Mindesturlaub für Jugendliche (jeweils ARBEITSTAGE bei 6-Tage-Woche, Stichtag 01.01. des Kalenderjahres):

- Unter 16 Jahren am 1. Januar: mindestens **30 Werktage**
- Unter 17 Jahren am 1. Januar: mindestens **27 Werktage**
- Unter 18 Jahren am 1. Januar: mindestens **25 Werktage**

BEISPIEL: Azubi wird am 04.04.2026 18 Jahre. Zum 01.01.2026 war er noch 17 → **25 Werktage JArbSchG-Minimum**.

WICHTIG: Gilt ein Tarifvertrag oder Betriebsvereinbarung mit mehr Urlaubstagen (z.B. 30 Arbeitstage bei 5-Tage-Woche), dann **gilt das Günstigkeitsprinzip** — die günstigere Regelung gewinnt. JArbSchG ist nur Untergrenze.',
 '{"required_concepts": ["§19 JArbSchG", "unter 16 → 30", "unter 17 → 27", "unter 18 → 25", "Stichtag 01.01.", "Günstigkeitsprinzip", "Tarif schlägt Minimum"]}',
 NULL, 4, 'bayern-S2022-A5', 3, 300),

('wiso-arbeitsschutz-unfall', 'cued',
 'Ordnen Sie folgende Gesetze der richtigen Schutzgruppe zu: ArbZG, BUrlG, EFZG, BEEG, MuSchG, JArbSchG, SGB IX, ArbSchG.',
 'ArbZG (Arbeitszeitgesetz) — regelt Arbeitszeit, Pausen, Ruhezeit für alle Volljährigen (max. 8h/Tag, erweiterbar auf 10h, Ausgleich binnen 6 Monaten).

BUrlG (Bundesurlaubsgesetz) — Mindesturlaub 24 Werktage bei 6-Tage-Woche, 20 bei 5-Tage-Woche.

EFZG (Entgeltfortzahlungsgesetz) — 6 Wochen Lohnfortzahlung bei Krankheit (§3).

BEEG (Bundeselterngeld- und Elternzeitgesetz) — Elternzeit bis 3 Jahre, Elterngeld 65-67% Netto, max. 1.800 EUR.

MuSchG (Mutterschutzgesetz) — Beschäftigungsverbote, Kündigungsschutz während Schwangerschaft + 4 Monate nach Geburt, Mutterschutzlohn 75 %.

JArbSchG (Jugendarbeitsschutzgesetz) — Schutz Minderjähriger unter 18.

SGB IX — Rehabilitation und Teilhabe, Schwerbehindertenrecht (ab GdB 50), besonderer Kündigungsschutz.

ArbSchG (Arbeitsschutzgesetz) — allgemeine Arbeitgeberpflichten zur Gefährdungsbeurteilung, Unterweisung, Schutzmaßnahmen.',
 '{"required_concepts": ["ArbZG Arbeitszeit Pausen", "BUrlG 24/20 Werktage", "EFZG 6 Wochen", "BEEG Elternzeit", "MuSchG Mutterschutzlohn 75%", "JArbSchG Minderjährige", "SGB IX Schwerbehinderte", "ArbSchG Gefährdungsbeurteilung"]}',
 NULL, 8, 'bayern-W2021-A18', 4, 480),

-- ============================================================
-- BETRIEBSRAT & JAV
-- ============================================================

('wiso-betriebsrat-jav', 'cued',
 'In welchen Bereichen hat der Betriebsrat zwingende Mitbestimmungsrechte nach BetrVG §87? Nennen Sie mindestens 5 konkrete Beispiele.',
 'Nach BetrVG §87 hat der Betriebsrat ein ECHTES Mitbestimmungsrecht (Arbeitgeber kann NICHT alleine entscheiden) in sozialen Angelegenheiten:

1. **Beginn und Ende der täglichen Arbeitszeit** sowie Verteilung auf die Wochentage (§87 Abs. 1 Nr. 2).
2. **Vorübergehende Verkürzung oder Verlängerung der Arbeitszeit** (Kurzarbeit / Mehrarbeit / Überstunden) (§87 Abs. 1 Nr. 3).
3. **Urlaubsplan und allgemeine Urlaubsgrundsätze** (§87 Abs. 1 Nr. 5).
4. **Einführung und Anwendung von technischen Einrichtungen zur Mitarbeiterüberwachung** (z.B. Videokameras, Keylogger, Zeiterfassung) (§87 Abs. 1 Nr. 6).
5. **Arbeitsschutz-Regelungen und Unfallverhütung** über gesetzliche Mindeststandards hinaus (§87 Abs. 1 Nr. 7).
6. **Betriebliche Lohngestaltung, Akkord-/Prämiensätze** (§87 Abs. 1 Nr. 10/11).
7. **Ordnung des Betriebs und Verhalten der Arbeitnehmer** (z.B. Hausordnung, Rauchverbot, Kleiderordnung) (§87 Abs. 1 Nr. 1).

ANHÖRUNGSRECHT (§102) — KEINE Mitbestimmung, aber Anhörungspflicht VOR jeder Kündigung. Kündigung ohne BR-Anhörung ist **unwirksam**.

WICHTIG: Personalauswahl (Einstellung, Eingruppierung, Versetzung) ist nur in Betrieben mit regelmäßig MEHR ALS 20 Arbeitnehmern mitbestimmungspflichtig (§99).',
 '{"required_concepts": ["BetrVG §87 Mitbestimmung", "Arbeitszeit Beginn Ende", "Überstunden Kurzarbeit", "Urlaubsplan", "Mitarbeiterüberwachung", "Lohngestaltung", "§102 Anhörung vor Kündigung", "§99 ab 20 MA Einstellung"]}',
 NULL, 8, 'bayern-W2021-A15-16', 4, 420),

('wiso-betriebsrat-jav', 'cued',
 'Wer ist wahlberechtigt und wer ist wählbar zur Betriebsratswahl? Was gilt für JAV-Wahlen?',
 'BETRIEBSRAT — BetrVG §7, §8:

Wahlberechtigt (aktives Wahlrecht):
- Alle Arbeitnehmer des Betriebs
- Mindestalter: **16 Jahre** (seit Betriebsrätemodernisierungsgesetz 2021)
- Leiharbeitnehmer nach 3 Monaten Einsatzdauer

Wählbar (passives Wahlrecht):
- **Volljährig** (18 Jahre)
- **6 Monate** ununterbrochen im Betrieb ODER im Konzern

JAV (Jugend- und Auszubildendenvertretung) — BetrVG §60-73:

Wahlberechtigt:
- Alle Arbeitnehmer unter 18 Jahren
- Alle Auszubildenden unter 25 Jahren (unabhängig vom Alter)

Wählbar:
- Alle Arbeitnehmer unter 25 Jahren (keine 6-Monate-Voraussetzung für JAV!)

Kernaufgabe JAV: Interessenvertretung Jugendlicher/Azubis, TEILNAHME an Betriebsratssitzungen mit beratender Stimme.

Betriebsversammlung: Findet in bezahlter Arbeitszeit statt, Arbeitnehmer müssen freigestellt werden.',
 '{"required_concepts": ["aktiv 16 Jahre", "passiv 18 Jahre + 6 Monate", "JAV unter 18 oder Azubi unter 25", "JAV wählbar unter 25", "Leiharbeitnehmer nach 3 Monaten", "Betriebsversammlung bezahlt"]}',
 NULL, 6, 'bayern-S2022-A7-11', 3, 360),

-- ============================================================
-- RECHTSFORMEN & GEWINNVERTEILUNG
-- ============================================================

('wiso-rechtsformen-unternehmen', 'cued',
 'Vergleichen Sie Einzelunternehmen, GbR, OHG, KG, GmbH, AG und eG hinsichtlich: Mindestkapital, Haftung der Gesellschafter, Geschäftsführung, Gewinnverteilung, Handelsregister.',
 'EINZELUNTERNEHMEN / e.K.:
- Kapital: kein Mindest.
- Haftung: UNBESCHRÄNKT mit Privatvermögen.
- GF: Inhaber selbst.
- HR: Eintragung ab kaufmännischer Tätigkeit (e.K.).

GbR (Gesellschaft bürgerlichen Rechts) — BGB §705 ff.:
- Kapital: kein Mindest.
- Haftung: ALLE Gesellschafter gesamtschuldnerisch + unbeschränkt mit Privatvermögen.
- GF: alle gemeinsam (mitbestimmend).
- Keine HR-Eintragung (nur Gewerbeanmeldung).

OHG (Offene Handelsgesellschaft) — HGB §105 ff.:
- Kapital: kein Mindest.
- Haftung: ALLE persönlich, unbeschränkt, gesamtschuldnerisch.
- GF: alle einzeln (Einzelvertretungsbefugnis).
- HR-Abteilung A.

KG (Kommanditgesellschaft) — HGB §161 ff.:
- Kapital: kein Mindest.
- Haftung: KOMPLEMENTÄR voll + unbeschränkt; KOMMANDITIST nur bis zur Einlage.
- GF: nur Komplementär.
- HR-Abteilung A.

GmbH (Gesellschaft mit beschränkter Haftung) — GmbHG:
- Kapital: **25.000 EUR** Stammkapital (davon bei Gründung min. 12.500 EUR einzuzahlen).
- Haftung: NUR Gesellschaftsvermögen (Gesellschafter haften nicht privat).
- GF: ein oder mehrere Geschäftsführer (Angestellte, müssen nicht Gesellschafter sein).
- HR-Abteilung B.
- Gewinnverteilung: im Verhältnis der Stammeinlagen, sofern Satzung nichts anderes regelt.

AG (Aktiengesellschaft) — AktG:
- Kapital: **50.000 EUR** Grundkapital, zerlegt in Aktien.
- Haftung: nur Gesellschaftsvermögen.
- GF: **Vorstand**, kontrolliert vom **Aufsichtsrat**. Aktionäre entscheiden in Hauptversammlung.
- HR-Abteilung B.

eG (eingetragene Genossenschaft) — GenG:
- Kapital: kein festes Mindestkapital, aber Genossenschaftsanteile.
- Haftung: grundsätzlich nur mit Genossenschaftsvermögen (Nachschusspflicht satzungsabhängig).
- GF: Vorstand.
- Eintragung ins GENOSSENSCHAFTSREGISTER (nicht HR!).

MERKHILFE: "GmbH 25k, AG 50k, Rest keins."',
 '{"required_concepts": ["GmbH 25000 Stammkapital", "AG 50000 Grundkapital", "Einzel GbR OHG unbeschränkt privat", "KG Komplementär voll Kommanditist Einlage", "HR A Personengesellschaften, HR B Kapitalgesellschaften", "eG Genossenschaftsregister", "AG Vorstand Aufsichtsrat Hauptversammlung"]}',
 NULL, 12, 'bayern-S2023-A13-15-21-23', 4, 600),

('wiso-rechtsformen-unternehmen', 'application',
 'Zwei Gesellschafter gründen eine GmbH mit dem gesetzlich vorgesehenen Mindest-Stammkapital. Herr Trout bringt 80.000 EUR und Frau Wegener 40.000 EUR als Stammeinlagen ein (zusätzlich zum Stammkapital). Im ersten Geschäftsjahr erwirtschaftet die GmbH einen Gewinn von 60.000 EUR. In der Satzung wurde KEINE Regelung zur Gewinnverteilung getroffen.

a) Wie hoch ist das gesetzliche Mindest-Stammkapital einer GmbH?
b) Nach welchem Prinzip wird der Gewinn verteilt, wenn die Satzung schweigt?
c) Berechnen Sie den Gewinnanteil von Frau Wegener.',
 'a) Mindest-Stammkapital GmbH: **25.000 EUR** (§5 Abs. 1 GmbHG).

b) Verteilungsprinzip bei fehlender Satzungsregelung: Nach §29 Abs. 3 GmbHG verteilt sich der Gewinn **im Verhältnis der Geschäftsanteile** (= Stammeinlagen). Das heißt: Jeder Gesellschafter bekommt den Anteil, der seinem Kapitalanteil an der Gesamt-Stammeinlage entspricht.

c) Gewinnanteil Frau Wegener:

Gesamt-Einlagen = Trout 80.000 + Wegener 40.000 = **120.000 EUR**.
Wegener-Anteil = 40.000 / 120.000 = 1/3 = 33,33 %.
Wegener-Gewinnanteil = 60.000 × 1/3 = **20.000,00 EUR**.

Kontrollrechnung: Trout bekommt 60.000 × 80.000/120.000 = 40.000 EUR. Summe 20k + 40k = 60k ✓',
 '{"required_concepts": ["GmbH 25000 Stammkapital", "§29 GmbHG Verhältnis Stammeinlagen", "120000 Gesamt", "40000/120000 = 1/3", "60000 × 1/3 = 20000"]}',
 '[{"criterion": "25000 EUR korrekt", "weight": 2, "description": "Mindest-Stammkapital", "required": true},
   {"criterion": "Verteilungsprinzip benannt", "weight": 3, "description": "nach Einlagen-Verhältnis", "required": true},
   {"criterion": "Berechnung korrekt", "weight": 3, "description": "20000 EUR Wegener", "required": true}]',
 8, 'bayern-S2025-A23', 3, 600),

-- ============================================================
-- AGG & DIVERSITY
-- ============================================================

('wiso-agg-diversity', 'cued',
 'Welche Diskriminierungsmerkmale schützt das Allgemeine Gleichbehandlungsgesetz (AGG §1)? Welche Fragen im Einstellungsgespräch sind zulässig, welche verboten?',
 'AGG §1 — acht Diskriminierungsmerkmale:
1. **Rasse / ethnische Herkunft**
2. **Geschlecht**
3. **Religion / Weltanschauung**
4. **Behinderung**
5. **Alter**
6. **Sexuelle Identität**
(+ implizit: Sprache, Abstammung, Staatsangehörigkeit werden oft mit-diskutiert)

Zulässige Fragen im Einstellungsgespräch:
- Fachliche Qualifikationen, Berufserfahrung.
- Erwartete Vergütung.
- Fähigkeiten, die für die konkrete Tätigkeit erforderlich sind (z.B. Führerschein bei Fahrer, körperliche Belastbarkeit bei körperlicher Arbeit — muss sachlich gerechtfertigt sein).
- Vorstrafen NUR wenn einschlägig (z.B. Vermögensdelikte bei Buchhalter).

VERBOTENE Fragen (AGG-Verstoß oder Persönlichkeitsrecht):
- Familienplanung / Schwangerschaft / Kinderwunsch (Geschlecht).
- Religions- oder Parteizugehörigkeit (außer bei Tendenzbetrieben wie Kirche).
- Sexuelle Orientierung.
- Gesundheitszustand allgemein / Krankheitsgeschichte (nur bei klarer Tätigkeitsrelevanz zulässig).
- Vermögensverhältnisse (außer bei Berufen mit Vertrauensstellung).
- Gewerkschaftszugehörigkeit.
- Ethnische Herkunft / Muttersprache (außer Sprachkenntnisse für Tätigkeit nötig).

RECHTSFOLGE bei Verstoß (AGG §15): Schadensersatz bis zu 3 Bruttomonatsgehältern.

STELLENANZEIGEN-TEST: "Junge dynamische Mitarbeiterin mit repräsentativem Erscheinungsbild" → diskriminiert ALTER und GESCHLECHT → unzulässig.',
 '{"required_concepts": ["8 AGG-Merkmale", "Rasse Geschlecht Religion Behinderung Alter Sexualität", "zulässig Qualifikation Gehalt", "verboten Familie Religion Krankheit Vermögen", "§15 AGG 3 Monatsgehälter", "Stellenanzeige jung + Erscheinungsbild diskriminiert"]}',
 NULL, 8, 'bayern-S2023-A1-A29', 3, 420),

-- ============================================================
-- UMWELTSCHUTZ
-- ============================================================

('wiso-umweltschutz', 'cued',
 'Erläutern Sie die Abfallhierarchie nach KrWG § 6 und das Verursacherprinzip. Welche bekannten Umweltsiegel gibt es und wofür stehen sie?',
 'ABFALLHIERARCHIE — §6 KrWG (Kreislaufwirtschaftsgesetz), 5 Stufen in Priorität:

1. **Vermeidung** — Abfall gar nicht erst entstehen lassen (z.B. Mehrweg statt Einweg).
2. **Vorbereitung zur Wiederverwendung** — gebrauchte Produkte aufbereiten (Pfandflaschen spülen/neu befüllen).
3. **Recycling** — stoffliche Verwertung (Papier/Glas einschmelzen).
4. **Sonstige Verwertung** — insbesondere energetische Verwertung (Müllverbrennung mit Stromgewinnung).
5. **Beseitigung** — Deponie, letzte Option.

MERKSATZ: "Vermeiden vor Verwerten vor Beseitigen."

VERURSACHERPRINZIP (Umweltrecht): Wer Umweltbelastung verursacht, trägt die Kosten für Vermeidung, Beseitigung, Sanierung. Konkretisiert in BImSchG, BBodSchG, KrWG.

Beispiel: Unternehmen, das mit Diesel-LKWs CO2 ausstößt, zahlt CO2-Abgabe; Chemiefirma, die Boden kontaminiert, zahlt Sanierung.

UMWELTSIEGEL:
- **Blauer Engel** — DEUTSCHES staatliches Umweltzeichen, seit 1978. Vergeben vom Umweltbundesamt. Bedeutet: Produkt ist deutlich umweltfreundlicher als vergleichbare Alternativen.
- **EU-Ecolabel (Euro-Blume)** — EU-weit, ähnliche Kriterien wie Blauer Engel.
- **FairTrade** — faire Bezahlung von Produzenten in Entwicklungsländern, nicht primär ökologisch.
- **Bio-Siegel (EU)** — ökologische Landwirtschaft.
- **FSC** (Forest Stewardship Council) — nachhaltige Forstwirtschaft.
- **GS-Zeichen** — "Geprüfte Sicherheit", freiwillig, geht über CE hinaus.
- **CE-Kennzeichnung** — gesetzliche Konformitätserklärung, KEIN Umweltzeichen!

ACHTUNG: CE bedeutet NUR "Produkt erfüllt EU-Mindestanforderungen" (Sicherheit, EMV), NICHT Umweltfreundlichkeit.',
 '{"required_concepts": ["5 Stufen Abfallhierarchie", "Vermeidung Wiederverwendung Recycling energetisch Beseitigung", "§6 KrWG", "Verursacherprinzip", "Blauer Engel Umweltbundesamt", "EU-Ecolabel", "FairTrade soziale Kriterien", "CE kein Umweltsiegel"]}',
 NULL, 7, 'bayern-S2022-A27', 3, 360),

-- ============================================================
-- RECHNUNGSWESEN & KENNZAHLEN
-- ============================================================

('wiso-rechnungswesen-kennzahlen', 'application',
 'Ein Unternehmen hat im Vorjahr einen Umsatz von 4.900.000 EUR bei 50 Mitarbeitern erzielt. Im aktuellen Jahr wurde der Umsatz auf 5.100.000 EUR bei 50 Mitarbeitern gesteigert.

a) Berechnen Sie den Umsatz pro Mitarbeiter in beiden Jahren.
b) Um wie viel Prozent ist der Umsatz pro Mitarbeiter gestiegen? (Auf zwei Nachkommastellen runden.)
c) Was ist der Unterschied zwischen Nominal- und Realeinkommen, und wie wirkt sich 3 % Inflation auf einen nominal um 2 % gestiegenen Lohn aus?',
 'a) Umsatz pro Mitarbeiter:
- Vorjahr:    4.900.000 / 50 = **98.000 EUR/MA**
- Aktuell:    5.100.000 / 50 = **102.000 EUR/MA**

b) Prozentuale Veränderung:
Differenz = 102.000 − 98.000 = 4.000 EUR.
Prozent = (4.000 / 98.000) × 100 = **4,0816 %** ≈ **4,08 %**.

Merke: IMMER vom ALTEN Wert rechnen (nicht vom neuen). Also: neu − alt, dann / alt × 100.

c) NOMINALEINKOMMEN: tatsächlich gezahlter Geldbetrag (in EUR).
REALEINKOMMEN: Kaufkraft des Nominaleinkommens, bereinigt um Inflation.

Formel: Realeinkommen-Veränderung ≈ Nominal-Veränderung − Inflationsrate

Beispiel: Nominal +2 %, Inflation +3 %.
Real = +2 % − 3 % = **−1 %**.

Der Arbeitnehmer bekommt nominal MEHR Geld, kann aber real WENIGER damit kaufen → faktische Lohnsenkung.

BW-Klassiker: Tarifabschluss über Inflation als Forderung der Gewerkschaften.',
 '{"required_concepts": ["98000 Umsatz/MA alt", "102000 neu", "4,08 %", "vom alten Wert", "Nominal Geldbetrag", "Real Kaufkraft", "Real ≈ Nominal − Inflation", "negativer Reallohn"]}',
 '[{"criterion": "Umsatz/MA beide Jahre", "weight": 2, "description": "98k und 102k", "required": true},
   {"criterion": "%-Berechnung korrekt", "weight": 2, "description": "4,08 % mit 2 Nachkomma", "required": true},
   {"criterion": "Nominal vs Real definiert", "weight": 2, "description": "Kaufkraft-Konzept", "required": true},
   {"criterion": "Inflationsrechnung", "weight": 2, "description": "2 − 3 = −1 %", "required": true}]',
 8, 'bayern-S2023-A17+A9', 4, 900),

-- ============================================================
-- ORGANISATION & FÜHRUNG
-- ============================================================

('wiso-organisation-fuehrung', 'cued',
 'Vergleichen Sie die vier klassischen Leitungssysteme (Einlinien, Mehrlinien, Stablinien, Matrix) hinsichtlich: Anzahl Vorgesetzter, Befehlsweg, Vor- und Nachteil, typisches Einsatzgebiet.',
 'EINLINIENSYSTEM:
- Genau **1 Vorgesetzter** pro Mitarbeiter.
- Befehlsweg: streng hierarchisch top-down.
- Vorteil: klare Zuständigkeit, eindeutige Verantwortung.
- Nachteil: lange Dienstwege, Überlastung der Spitze, Bürokratie.
- Einsatz: Militär, Behörden, kleine Unternehmen.

MEHRLINIENSYSTEM (nach Taylor):
- **Mehrere fachliche Vorgesetzte** pro Mitarbeiter (je nach Sachgebiet).
- Befehlsweg: direkt nach Funktion.
- Vorteil: Spezialisierung, schnelle fachliche Kommunikation.
- Nachteil: Kompetenz-/Zuständigkeitskonflikte, widersprüchliche Weisungen.
- Einsatz: selten in Reinform, historisch in Produktion.

STABLINIENSYSTEM:
- 1 Vorgesetzter (wie Einlinie) + beratende **Stabsstellen** (ohne Weisungsbefugnis).
- Befehlsweg: Linie; Stäbe geben Empfehlungen.
- Vorteil: Entlastung der Leitung durch Expertenwissen (Recht, Controlling, PR).
- Nachteil: Konflikte zwischen Stab (theoretisch) und Linie (praktisch).
- Einsatz: MITTELSTÄNDISCHE Unternehmen — DER BW-KLASSIKER.

MATRIXORGANISATION:
- Mitarbeiter hat 2 Vorgesetzte: **Funktional** (z.B. Entwicklung) + **Objektbezogen** (z.B. Projekt X).
- Befehlsweg: zweidimensional, projektbezogen.
- Vorteil: Flexibilität, Spezialisierung nach Fach UND Projekt.
- Nachteil: Kompetenzkonflikte, hoher Kommunikationsaufwand.
- Einsatz: Große Tech-Konzerne, Projektorganisationen, IT-Beratungen.

BW-TREND: Stablinien bei Mittelstand, Matrix bei IT/Agenturen.',
 '{"required_concepts": ["Einlinie 1 Vorgesetzter Hierarchie", "Mehrlinie fachliche Vorgesetzte Taylor", "Stablinie + Stäbe beratend", "Matrix 2 Vorgesetzte funktional + Projekt", "Vor/Nachteile je System"]}',
 NULL, 8, 'bayern-W2021-A13-S2022-A21', 3, 480),

('wiso-organisation-fuehrung', 'cued',
 'Ordnen Sie folgende Tätigkeiten den drei Wirtschaftssektoren zu: Landwirtschaft, Autofabrik, Softwareentwicklung, Bergbau, Frisörsalon, Bäckerei (Handwerk), Lehrer, Online-Shop.',
 'WIRTSCHAFTSSEKTOREN:

**Primärsektor (Urproduktion)** — Rohstoffgewinnung aus der Natur:
- Landwirtschaft ✓
- Bergbau ✓
- Forstwirtschaft, Fischerei

**Sekundärsektor (Industrie/Produktion)** — Verarbeitung zu Gütern:
- Autofabrik ✓
- Bäckerei ✓ (Verarbeitung von Rohstoffen zu Brötchen)
- produzierendes Handwerk allgemein
- Chemie, Maschinenbau

**Tertiärsektor (Dienstleistungen)** — immaterielle Leistungen:
- Softwareentwicklung ✓
- Frisörsalon ✓
- Lehrer ✓
- Online-Shop ✓ (Handel)
- Banken, Versicherungen, Beratung, Gesundheit

HISTORISCHE VERSCHIEBUNG in Deutschland:
- 1900: ~40 % Primär, 40 % Sekundär, 20 % Tertiär.
- 2025: ~1 % Primär, ~24 % Sekundär, ~75 % Tertiär (Dienstleistungsgesellschaft).

QUARTÄRSEKTOR (moderne Erweiterung): wissensintensive Tätigkeiten wie Forschung, IT, Informationswirtschaft — oft als Teil des Tertiär gezählt, aber zunehmend separat betrachtet.',
 '{"required_concepts": ["Primär Urproduktion Landwirtschaft Bergbau", "Sekundär Industrie Autofabrik Bäckerei", "Tertiär Dienstleistung Software Frisör Lehrer Online-Shop", "Verschiebung zur Dienstleistungsgesellschaft", "Quartär Wissen"]}',
 NULL, 6, 'bayern-S2023-A27', 2, 300),

-- ============================================================
-- BGB §622 KÜNDIGUNGSFRISTEN
-- ============================================================

('wiso-bgb-kuendigung-frist', 'application',
 'Herr Paul Kropp arbeitet seit dem 01.01.2012 als kaufmännischer Angestellter bei der Schnellinger GmbH. Aufgrund eines Auftragseinbruchs möchte die Geschäftsführung ihm im Dezember 2025 betriebsbedingt zum nächstmöglichen Termin kündigen.

Ausschnitt BGB §622:
„Das Arbeitsverhältnis eines Arbeitnehmers kann mit einer Frist von vier Wochen zum Fünfzehnten oder zum Ende eines Kalendermonats gekündigt werden. Für eine Kündigung durch den Arbeitgeber beträgt die Kündigungsfrist, wenn das Arbeitsverhältnis in dem Betrieb oder Unternehmen
- 2 Jahre bestanden hat, 1 Monat zum Ende eines Kalendermonats,
- 5 Jahre bestanden hat, 2 Monate zum Ende eines Kalendermonats,
- 8 Jahre bestanden hat, 3 Monate zum Ende eines Kalendermonats,
- 10 Jahre bestanden hat, 4 Monate zum Ende eines Kalendermonats,
- 12 Jahre bestanden hat, 5 Monate zum Ende eines Kalendermonats,
- 15 Jahre bestanden hat, 6 Monate zum Ende eines Kalendermonats,
- 20 Jahre bestanden hat, 7 Monate zum Ende eines Kalendermonats."

a) Wie lange ist Herr Kropp bei der Firma beschäftigt?
b) Welche Kündigungsfrist gilt laut BGB §622?
c) Zu welchem Datum endet das Arbeitsverhältnis bei Kündigung im Dezember 2025?
d) Welche formellen Voraussetzungen muss die Kündigung erfüllen?',
 'a) Beschäftigungsdauer:
01.01.2012 → Dezember 2025 = **13 Jahre und 11 Monate**.

b) Anwendbare Stufe: Bei 10 Jahren gilt "4 Monate zum Monatsende", bei 12 Jahren "5 Monate". Herr Kropp hat mehr als 12, weniger als 15 Jahre → **5 Monate zum Ende eines Kalendermonats**.

c) Kündigung im Dezember 2025 → 5 Monate Frist → frühestmögliches Beendigungsdatum:
- Januar, Februar, März, April, Mai 2026 → Frist endet am **31.05.2026**.

d) Formelle Voraussetzungen:
1. **Schriftform** zwingend (§623 BGB) — E-Mail oder mündlich reichen NICHT, eigenhändige Unterschrift.
2. **Zugang** beim Arbeitnehmer (Einschreiben oder persönlich übergeben — Beweislast beim Arbeitgeber).
3. **Anhörung des Betriebsrats** nach §102 BetrVG vor Ausspruch der Kündigung, sonst unwirksam.
4. **Kündigungsgrund**: betriebsbedingt erfordert dringende betriebliche Erfordernisse + **Sozialauswahl** nach §1 KSchG (Dauer Betriebszugehörigkeit, Lebensalter, Unterhaltspflichten, Schwerbehinderung).
5. Besonderer Kündigungsschutz beachten:
   - Schwangere/Mütter in Mutterschutzfrist (MuSchG).
   - Schwerbehinderte (Zustimmung Integrationsamt §168 SGB IX).
   - Betriebsratsmitglieder (§15 KSchG — nahezu nicht kündbar).

Klageweg: Kündigungsschutzklage binnen 3 Wochen nach Zugang beim Arbeitsgericht.',
 '{"required_concepts": ["13 Jahre 11 Monate", "12-Jahre-Stufe 5 Monate", "31.05.2026", "Schriftform §623", "BR-Anhörung §102", "Sozialauswahl §1 KSchG", "Schwangere Schwerbehinderte besonderer Schutz", "3 Wochen Klagefrist"]}',
 '[{"criterion": "Dauer korrekt", "weight": 1, "description": "13J 11M", "required": true},
   {"criterion": "Frist identifiziert", "weight": 2, "description": "5 Monate bei 12+ Jahren", "required": true},
   {"criterion": "Datum berechnet", "weight": 2, "description": "31.05.2026", "required": true},
   {"criterion": "Schriftform §623", "weight": 1, "description": "genannt", "required": true},
   {"criterion": "BR-Anhörung + Sozialauswahl", "weight": 3, "description": "beide Punkte", "required": true},
   {"criterion": "Besonderer Schutz", "weight": 1, "description": "Schwangere/Behinderte", "required": false}]',
 10, 'bayern-S2025-A18', 4, 900),

-- ============================================================
-- Bonus: Konjunktur aus Tabelle ableiten (Bayern-Pattern)
-- ============================================================

('wiso-wirtschaftspolitik', 'application',
 'In einer Wirtschaftsanalyse finden Sie folgende Kennzahlen für die Europäische Union:

| Kennzahl           | Vorjahr | Aktuelles Jahr | Prognose |
|--------------------|--------:|---------------:|---------:|
| BIP-Wachstum       | -0,5 %  | -1,0 %         | -2,0 %   |
| Inflationsrate     |  2,2 %  |  2,2 %         |  2,0 %   |
| Arbeitslosenquote  |  6,0 %  |  6,5 %         |  7,5 %   |

a) In welcher Konjunkturphase befindet sich die EU im aktuellen Jahr? Begründen Sie anhand der Tabelle.
b) Welche fiskalpolitischen Maßnahmen könnte die Bundesregierung ergreifen?
c) Welche geldpolitischen Maßnahmen wären von der EZB zu erwarten?',
 'a) Konjunkturphase: **Abschwung/Rezession**.

Begründung aus der Tabelle:
1. BIP-Wachstum ist NEGATIV und zusätzlich fallend (−0,5 % → −1,0 % → −2,0 %) — klassisches Rezessions-Signal.
2. Arbeitslosigkeit steigt deutlich (6,0 → 6,5 → 7,5 %) — typisch für Abschwung.
3. Inflation stabil bei ~2 % — noch keine Deflation (die käme erst im Tiefstand).
4. KEIN Tiefstand, weil Investitionen/Preise noch nicht eingebrochen sind — BIP fällt aber weiter → echte Rezession.

b) Fiskalpolitik (antizyklisch):
1. **Erhöhung der Staatsausgaben**: Konjunkturprogramm für Infrastruktur (Straßen, Schulen, Digitalisierung).
2. **Steuersenkungen** (Einkommensteuer, temporäre MwSt-Senkung) zur Stärkung der Kaufkraft.
3. **Erhöhung sozialer Transferleistungen** (Bürgergeld, Kindergeld, Kurzarbeitergeld).
4. **Investitionszulagen** für Unternehmen (Abschreibungsvorteile, degressive AfA).
5. **Schuldenbremse ggf. aussetzen** für Sonderbelastung.

c) Geldpolitik (EZB, expansiv):
1. **Leitzinssenkung** — macht Kredite billiger, regt Investitionen und Konsum an.
2. **Quantitative Easing (QE)** — Ankauf von Staats- und Unternehmensanleihen, erhöht Geldmenge.
3. **Mindestreservesatz senken** — Banken können mehr Kredite vergeben.
4. **TLTRO** (Targeted Longer-Term Refinancing Operations) — zinsgünstige Langfristkredite an Banken, wenn sie Kredite an Realwirtschaft vergeben.

Zielkonflikt (magisches Viereck): Expansive Geldpolitik kann Inflation anheizen — Gefahr der Stagflation (niedriges Wachstum + hohe Inflation).',
 '{"required_concepts": ["Rezession/Abschwung", "BIP negativ fallend", "Arbeitslosigkeit steigt", "noch kein Tiefstand", "antizyklische Fiskalpolitik Staatsausgaben Steuern", "Transferleistungen", "EZB Leitzinssenkung QE", "TLTRO", "Stagflation Gefahr"]}',
 '[{"criterion": "Rezession erkannt + begründet", "weight": 3, "description": "mit Tabellen-Argumenten", "required": true},
   {"criterion": "3+ Fiskal-Maßnahmen", "weight": 3, "description": "Ausgaben, Steuern, Transfers", "required": true},
   {"criterion": "3+ EZB-Maßnahmen", "weight": 3, "description": "Zins, QE, Reserve", "required": true},
   {"criterion": "Zielkonflikt benannt", "weight": 1, "description": "Stagflations-Risiko", "required": false}]',
 10, 'bayern-S2025-A4-A6', 4, 900)

) AS v(slug, item_type, prompt, model_answer,
       expected_answer_structure, grading_criteria, points, source_exam, difficulty, estimated_time_sec)
JOIN topic_lookup t ON t.slug = v.slug;

-- ============================================================================
-- Teil 3: Seed Exam-Occurrences für neue Topics (damit X/5 korrekt zeigt)
-- ============================================================================

WITH topic_lookup AS (
    SELECT slug, topic_id FROM assessments.ap2_topics
)
INSERT INTO assessments.ap2_topic_exam_occurrences
    (topic_id, exam_term, bereich, aufgabe_nummer, points, notes)
SELECT t.topic_id, v.exam_term, v.bereich, v.aufgabe_nummer, v.points, v.notes
FROM (VALUES
-- wiso-arbeitsschutz-unfall in allen 5 Terminen
('wiso-arbeitsschutz-unfall', 'S2022', 'WISO', '5,23,26', 10, 'JArbSchG Urlaub, Sicherheitskennzeichen, Feuerlöscher'),
('wiso-arbeitsschutz-unfall', 'W2022', 'WISO', '4,5,17,18,21', 15, 'JArbSchG, MuSchG, Gesetzes-Zuordnung, BG, Brandwunden'),
('wiso-arbeitsschutz-unfall', 'S2023', 'WISO', '5', 3, 'Unfallmeldung BG'),
('wiso-arbeitsschutz-unfall', 'W2023', 'WISO', '14,26,27,28', 12, 'JArbSchG + BG + Sicherheitskennzeichen'),
('wiso-arbeitsschutz-unfall', 'S2024', 'WISO', '14,26,27', 10, 'Arbeitsschutz Mix'),

-- wiso-betriebsrat-jav in allen 5
('wiso-betriebsrat-jav', 'S2022', 'WISO', '7,10,11', 9, 'BR + JAV + Mitbestimmung'),
('wiso-betriebsrat-jav', 'W2022', 'WISO', '4,15,16', 9, 'Rangordnung BetrV-Tarif + Mitbestimmung'),
('wiso-betriebsrat-jav', 'S2023', 'WISO', '10,11,12,19', 12, 'BR-Anhörung + Versammlung + Wahl'),
('wiso-betriebsrat-jav', 'W2023', 'WISO', '13,15', 6, 'BR-Wahlberechtigung'),
('wiso-betriebsrat-jav', 'S2024', 'WISO', '11,12,13', 9, 'JAV + BR'),

-- wiso-rechtsformen in allen 5
('wiso-rechtsformen-unternehmen', 'S2022', 'WISO', '18', 3, 'GmbH Haftung'),
('wiso-rechtsformen-unternehmen', 'W2022', 'WISO', '12', 3, 'Rechtsformvergleich'),
('wiso-rechtsformen-unternehmen', 'S2023', 'WISO', '13,15,21,22,23', 15, 'KG, GmbH, AG, eG'),
('wiso-rechtsformen-unternehmen', 'W2023', 'WISO', '21', 3, 'Rechtsform'),
('wiso-rechtsformen-unternehmen', 'S2024', 'WISO', '21,22,23', 9, 'GmbH + Gewinnverteilung Rechenaufgabe'),

-- wiso-agg-diversity in 4 von 5 (nicht W2023)
('wiso-agg-diversity', 'S2022', 'WISO', '29,30', 6, 'Charta der Vielfalt'),
('wiso-agg-diversity', 'W2022', 'WISO', '22', 3, 'Stellenanzeige diskriminierend'),
('wiso-agg-diversity', 'S2023', 'WISO', '1,29,30', 9, 'zulässige Fragen + AGG'),
('wiso-agg-diversity', 'S2024', 'WISO', '24,25', 6, 'AGG Fallprüfung'),

-- wiso-umweltschutz in allen 5 (letzte Aufgaben-Gruppe)
('wiso-umweltschutz', 'S2022', 'WISO', '27,28', 6, 'Verursacherprinzip + Siegel'),
('wiso-umweltschutz', 'W2022', 'WISO', '20', 3, 'Blauer Engel'),
('wiso-umweltschutz', 'S2023', 'WISO', '24,25', 6, 'Hierarchie + Siegel'),
('wiso-umweltschutz', 'W2023', 'WISO', '29,30', 6, 'Umweltsiegel-Zuordnung'),
('wiso-umweltschutz', 'S2024', 'WISO', '30', 3, 'Recycling-Pfeile'),

-- wiso-rechnungswesen in allen 5
('wiso-rechnungswesen-kennzahlen', 'S2022', 'WISO', '19', 3, 'wirtschaftlichster Auftrag'),
('wiso-rechnungswesen-kennzahlen', 'W2022', 'WISO', '6', 3, 'Kennzahlen'),
('wiso-rechnungswesen-kennzahlen', 'S2023', 'WISO', '9,17', 6, 'Real-Nominal + Umsatz/MA'),
('wiso-rechnungswesen-kennzahlen', 'W2023', 'WISO', '3', 3, 'Ökonomieprinzip'),
('wiso-rechnungswesen-kennzahlen', 'S2024', 'WISO', '2,3', 6, 'Maximal/Minimal-Prinzip'),

-- wiso-organisation in allen 5
('wiso-organisation-fuehrung', 'S2022', 'WISO', '17,20,21', 9, 'Sektoren + Zusammenschlüsse + Leitung'),
('wiso-organisation-fuehrung', 'W2022', 'WISO', '13', 3, 'Leitungssystem'),
('wiso-organisation-fuehrung', 'S2023', 'WISO', '14,27', 6, 'Standort + Sektoren'),
('wiso-organisation-fuehrung', 'W2023', 'WISO', '1', 3, 'Sektoren'),
('wiso-organisation-fuehrung', 'S2024', 'WISO', '1,7', 6, 'Sektoren + Ziele'),

-- wiso-bgb-kuendigung-frist in 4 von 5
('wiso-bgb-kuendigung-frist', 'W2022', 'WISO', '14', 3, 'Kündigungsfrist'),
('wiso-bgb-kuendigung-frist', 'S2023', 'WISO', '18,20', 6, '§622 + Arbeitsgericht'),
('wiso-bgb-kuendigung-frist', 'W2023', 'WISO', '16', 3, 'Rechtsquellen'),
('wiso-bgb-kuendigung-frist', 'S2024', 'WISO', '18,19,20', 9, '§622 Staffelung + Datumsrechnung')

) AS v(slug, exam_term, bereich, aufgabe_nummer, points, notes)
JOIN topic_lookup t ON t.slug = v.slug
ON CONFLICT DO NOTHING;

-- Exam-counts für alle neuen Topics aktualisieren
UPDATE assessments.ap2_topics t
SET exam_count = (
    SELECT count(DISTINCT exam_term)
    FROM assessments.ap2_topic_exam_occurrences o
    WHERE o.topic_id = t.topic_id
)
WHERE t.slug IN (
    'wiso-arbeitsschutz-unfall', 'wiso-betriebsrat-jav', 'wiso-rechtsformen-unternehmen',
    'wiso-agg-diversity', 'wiso-umweltschutz', 'wiso-rechnungswesen-kennzahlen',
    'wiso-organisation-fuehrung', 'wiso-bgb-kuendigung-frist'
);

COMMIT;
