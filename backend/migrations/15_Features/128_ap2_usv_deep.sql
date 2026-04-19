-- ============================================================================
-- Migration: 128_ap2_usv_deep.sql
-- Description: USV-Schlüsselthema massiv erweitern. Basiert auf Dozenten-Skript
--              LZ_020_USV_I.pdf (Marcel Lindner) + Screenshots 135126/140349/140805
--              + AP1-2026-BW RTO/RPO (Screenshot 115209). Deckt ab:
--              — IEC-62040-3 Klassen VFD/VI/VFI inkl. Synonyme
--              — Schutz-Matrix (9 Störungen × 3 Klassen) als Ordnen-Sie-zu
--              — Wirkleistung/Scheinleistung mit cos φ (BW-Klassiker)
--              — 3 IHK-Style Berechnungsaufgaben (Modellwahl, Reserve, cos φ)
--              — Bypass-Mechanismus, Einsatzorte, Sinusform
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
-- USV — Schutz-Matrix (Ordnen Sie zu / Zuordnungsaufgabe BW-Stil)
-- ============================================================

('usv', 'cued',
 'Welche USV-Klasse schützt vor welchen Störungen? Ordnen Sie die 9 Störungsarten den drei Klassen VFD (Off-Line), VI (Line-Interactive) und VFI (Online) zu.',
 'VFD schützt: Netzausfall, Spannungseinbrüche (Sag), Spannungsspitzen (Spike).\nVI schützt zusätzlich: Unterspannung (Brownout), Überspannung.\nVFI schützt zusätzlich: Spannungsstöße (Surge), Frequenzschwankungen, Spannungsverzerrung (Burst), Oberschwingungen.\n\nRegel: VFI deckt ALLE 9 Störungen ab (deshalb Krankenhäuser/RZ). VI deckt 5 (Office-Server). VFD deckt nur 3 (einfache Office-PCs).',
 '{"required_concepts": ["VFD 3 Störungen", "VI 5 Störungen", "VFI 9 Störungen alle", "Netzausfall Sag Spike", "Brownout Überspannung", "Surge Frequenz Burst Oberschwingungen"]}',
 NULL, 9, 'ki-generated-lindner-skript', 4, 300),

('usv', 'cued',
 'Was bedeutet der Begriff "Autonomiezeit" (auch "Überbrückungszeit") einer USV und welche Formel berechnet sie bei gegebener Akkukapazität in Ah, Akkuspannung in V, Last in W und cos φ?',
 'Autonomiezeit = Zeit, die die USV bei Netzausfall allein aus dem Akku weiterläuft.\n\nFormel (Wirkleistung-Variante):\nt [h] = (U_Akku × C_Ah × cos φ) / P_Last_W\n\nFormel ohne cos φ (bei reiner Wh-Rechnung):\nt [h] = (U_Akku × C_Ah) / S_VA\n\nBeispiel: 12 V × 100 Ah × 0,85 / 600 W = 1020/600 = 1,7 h ≈ 102 min.',
 '{"required_concepts": ["Autonomiezeit Definition", "Formel U × C × cos phi / P", "h in Minuten umrechnen"]}',
 NULL, 4, 'ki-generated-lindner-skript', 3, 240),

('usv', 'cued',
 'Erläutern Sie den Unterschied zwischen Wirkleistung P (Watt) und Scheinleistung S (Voltampere) und welche Bedeutung der Leistungsfaktor cos φ bei der USV-Dimensionierung hat.',
 'Scheinleistung S [VA] = U × I — das ist die elektrische Leistung, die die Quelle (USV) liefern MUSS. Hersteller geben USV-Leistung meist in VA an.\n\nWirkleistung P [W] = S × cos φ — das ist die tatsächlich nutzbare Leistung, die beim Verbraucher in Arbeit/Wärme umgesetzt wird.\n\nLeistungsfaktor cos φ liegt bei modernen Netzteilen mit PFC nahe 1,0 (meist 0,85-0,95). Bei induktiven Lasten (Motoren, alte Netzteile) kann er bis 0,6 sinken.\n\nDimensionierungs-Regel: USV in VA muss mindestens so groß sein, dass S × cos φ ≥ Summe aller P der Verbraucher. Also S [VA] = P_gesamt [W] / cos φ.',
 '{"required_concepts": ["S in VA Quelle", "P in W Verbraucher", "S = U × I", "P = S × cos phi", "PFC cos phi nahe 1", "USV in VA dimensionieren"]}',
 NULL, 5, 'ki-generated-lindner-skript', 4, 300),

('usv', 'cued',
 'Nennen Sie fünf typische Einsatzorte einer USV in einem mittelständischen Unternehmen.',
 '1. Server-/IT-Raum (Datenbanken, Anwendungsserver, Virtualisierung).\n2. Netzwerk-Infrastruktur (Firewall, Core-Switches, Router, WLAN-Controller).\n3. Sicherheitssysteme (Alarmanlage, Zugangskontrolle, Videoüberwachung).\n4. Kassensysteme/POS-Systeme im Einzelhandel (Warenwirtschaft muss weiterlaufen).\n5. Medizintechnik (Arztpraxen, Krankenhäuser — lebenserhaltende Geräte).\n\nWeitere: Leitstellen, Telefonanlagen (VoIP-Gateways), Labore mit empfindlichen Messgeräten.',
 '{"required_concepts": ["Serverraum", "Netzwerk Firewall Switch", "Sicherheit Alarm Videoüberwachung", "Kasse POS", "Medizin"]}',
 NULL, 5, 'ki-generated-lindner-skript', 2, 240),

('usv', 'cued',
 'Was ist der Bypass einer Online-USV (VFI) und in welcher Situation wird er aktiv?',
 'Bypass = interner Umgehungsschalter, der die Verbraucher direkt mit dem Netz verbindet und die USV-Elektronik (Gleichrichter + Wechselrichter) umgeht.\n\nAktivierung in zwei Szenarien:\n1. Eigenfehler der USV (Wechselrichter defekt): Automatische Umschaltung auf Bypass, damit Verbraucher weiter Strom bekommt statt auszufallen.\n2. Wartungs-Bypass: Manuell aktivierbar, damit Techniker die USV tauschen kann ohne die Verbraucher abzuschalten.\n\nBypass heißt implizit: während Bypass keine USV-Schutzwirkung — Verbraucher bekommt ungefiltertes Netz.',
 '{"required_concepts": ["Umgehungsschalter", "Eigenfehler USV", "Wartung", "keine Filterung während Bypass"]}',
 NULL, 3, 'ki-generated-lindner-skript', 3, 180),

-- ============================================================
-- USV — Screenshot 135126 (GIGA-1 USV / Modellwahl)
-- ============================================================

('usv', 'application',
 'Die Firma "Agrarenergie Müller e. K." betreibt einen kleinen Serverraum. Bei einem Stromausfall muss die USV den Raum für 20 Minuten mit Energie versorgen. Die Gesamtleistung aller Geräte beträgt 4.200 Watt. Die Akkuspannung der USV beträgt 12 V.

Folgende USV-Modelle stehen zur Auswahl:
- ALPHA-USV: 12 V, 90 Ah
- BETA-USV:  12 V, 120 Ah
- GIGA-1:    12 V, 150 Ah
- OMEGA-USV: 12 V, 200 Ah

Berechnen Sie, welches Modell die Mindestanforderung erfüllt und begründen Sie. Rechnen Sie ohne Reserve und mit cos φ = 1,0.',
 'Benötigte Energie für 20 Minuten:\nE_nötig = 4.200 W × (20/60) h = 4.200 × 1/3 = 1.400 Wh.\n\nVerfügbare Energie je Modell (E = U × C × cos φ = U × C bei cos φ = 1):\n- ALPHA:  12 × 90  = 1.080 Wh → reicht NICHT (< 1.400).\n- BETA:   12 × 120 = 1.440 Wh → reicht knapp.\n- GIGA-1: 12 × 150 = 1.800 Wh → reicht sicher.\n- OMEGA:  12 × 200 = 2.400 Wh → reicht mit Reserve.\n\nAntwort: GIGA-1 (oder BETA) erfüllt die Mindestanforderung. Empfehlung GIGA-1, da bei realen Einsätzen immer Reserven vorgesehen werden sollten (Akku-Alterung, Belastungsspitzen).

Begründung: Die Wirkenergie des Akkus muss mindestens der Wirkleistung × Zeit entsprechen. GIGA-1 liefert 1.800 Wh für eine Anforderung von 1.400 Wh — genügend Puffer gegen Akkuverschleiß.',
 '{"required_concepts": ["1400 Wh benötigt", "U × C = Wh", "BETA 1440 Wh knapp", "GIGA 1800 Wh empfehlen", "Reserve Alterung"]}',
 '[{"criterion": "Energiebedarf berechnet", "weight": 2, "description": "1400 Wh für 20 min", "required": true},
   {"criterion": "Modellkapazitäten berechnet", "weight": 2, "description": "je Modell Wh", "required": true},
   {"criterion": "Modellwahl begründet", "weight": 3, "description": "BETA knapp / GIGA empfohlen", "required": true},
   {"criterion": "Puffer für Alterung erwähnt", "weight": 1, "description": "Reserve-Argument", "required": false}]',
 8, 'W2026-BW-Lindner-Uebung-1', 4, 900),

-- ============================================================
-- USV — Screenshot 140349 (Kapazität mit 20% Reserve)
-- ============================================================

('usv', 'application',
 'Der Serverraum der "Agrarenergie Müller e. K." hat folgende Verbraucher:
- 2 Server à 800 W
- 3 Switches à 200 W
- 1 Access Point 150 W
- 1 Router 200 W
- 1 Firewall 150 W

Bei Stromausfall soll die USV 15 Minuten Betrieb sicherstellen, danach 5 Minuten kontrolliertes Herunterfahren. Es muss eine Restkapazität von 20% im Akku verbleiben (Tiefentladeschutz). Akkuspannung 12 V. Berechnen Sie die benötigte Akkukapazität in Ah und empfehlen Sie einen Standardakku (50, 75, 100, 125 Ah).',
 'Gesamtlast (alle Verbraucher):\nP_ges = 2×800 + 3×200 + 150 + 200 + 150 = 1.600 + 600 + 150 + 200 + 150 = 2.700 W.

Gesamtbetriebszeit: 15 min + 5 min = 20 min = 1/3 h.

Energie für 20 Minuten:\nE_nutzbar = 2.700 W × 1/3 h = 900 Wh.

Mit Tiefentladeschutz (nur 80% des Akkus nutzbar):\nE_Akku = 900 / 0,80 = 1.125 Wh.

Benötigte Kapazität in Ah bei 12 V:\nC = 1.125 / 12 = 93,75 Ah.

Standardakku-Empfehlung: 100 Ah (der nächstgrößere Standardwert). 75 Ah würde knapp nicht reichen (75 × 12 × 0,80 = 720 Wh < 900 Wh).

Ergebnis: 12 V / 100 Ah USV.',
 '{"required_concepts": ["2700 W Gesamtlast", "20 min = 1/3 h", "900 Wh nutzbar", "1125 Wh Akku mit Reserve", "93,75 Ah berechnet", "100 Ah gewählt", "75 Ah reicht nicht"]}',
 '[{"criterion": "Gesamtlast addiert", "weight": 2, "description": "2700 W", "required": true},
   {"criterion": "Betriebszeit summiert", "weight": 1, "description": "20 min = 1/3 h", "required": true},
   {"criterion": "Reserve eingerechnet", "weight": 3, "description": "/ 0,80 Tiefentladeschutz", "required": true},
   {"criterion": "Kapazität in Ah", "weight": 2, "description": "≈ 93,75 Ah", "required": true},
   {"criterion": "Standardgröße begründet", "weight": 2, "description": "100 Ah gewählt, 75 zu klein", "required": true}]',
 10, 'W2026-BW-Lindner-Uebung-2', 5, 1200),

-- ============================================================
-- USV — Screenshot 140805 (cos φ / Wirkleistung-Scheinleistung)
-- ============================================================

('usv', 'application',
 'Das Netzteil eines Servers hat eine Leistungsaufnahme von 450 VA. Das Datenblatt nennt einen Wirkungsgrad von 85 % bezogen auf die Scheinleistung.

a) Berechnen Sie die nutzbare Wirkleistung in Watt.
b) Wie viel elektrische Leistung wird als Verlustwärme abgegeben?
c) Eine USV soll drei solcher Server versorgen. Welche Scheinleistung in VA muss die USV mindestens bereitstellen, wenn ein Sicherheitszuschlag von 25 % berücksichtigt werden soll?',
 'a) Wirkleistung:\nP = S × cos φ = 450 VA × 0,85 = 382,5 W.

b) Verlustleistung:\nP_Verlust = S - P = 450 - 382,5 = 67,5 W (als Wärme).\n(Alternative Sicht: 15 % der 450 VA = 67,5 W gehen als Wärme verloren.)

c) USV-Dimensionierung für drei Server:\nS_pro_Server = 450 VA (Leistungsaufnahme des Netzteils bereits in VA gegeben).\nSumme = 3 × 450 = 1.350 VA.\nMit 25 % Reserve: S_USV = 1.350 × 1,25 = 1.687,5 VA.\n\nNächste Standardgröße: 2.000 VA USV oder 2 kVA.',
 '{"required_concepts": ["P = S × cos phi", "382,5 W", "Verlust 67,5 W", "3 Server × 450 VA = 1350 VA", "1,25 Reservefaktor", "1687,5 VA", "2000 VA Standard"]}',
 '[{"criterion": "Wirkleistung berechnet", "weight": 2, "description": "382,5 W", "required": true},
   {"criterion": "Verlustleistung berechnet", "weight": 2, "description": "67,5 W Wärme", "required": true},
   {"criterion": "Summe VA addiert", "weight": 1, "description": "1350 VA", "required": true},
   {"criterion": "Reserve eingerechnet", "weight": 2, "description": "× 1,25", "required": true},
   {"criterion": "Standardgröße empfohlen", "weight": 1, "description": "2 kVA", "required": false}]',
 8, 'W2026-BW-Lindner-Uebung-3', 4, 900),

-- ============================================================
-- USV — Screenshot 095306 (Schaltbild-Zuordnung BW-Klausur-Stil)
-- ============================================================

('usv', 'application',
 'Die "Schnellinger GmbH" soll für ihren Serverraum eine USV beschaffen. Der Elektroplaner legt drei Schaltpläne vor.

Plan A: Netzeingang → Filter → Lastausgang; parallel dazu Akku + Wechselrichter als Notfall-Zweig.
Plan B: Netzeingang → Gleichrichter → Akku → Wechselrichter → Lastausgang (ständig aktiv); parallel Bypass-Schalter.
Plan C: Netzeingang → AVR (Automatic Voltage Regulator) + Filter → Lastausgang; parallel Akku als Backup.

a) Ordnen Sie jedem Plan die passende USV-Klasse (VFD, VI, VFI) zu.
b) Beschriften Sie die Pläne mit einem deutschen Synonym (Off-Line, Line-Interactive, Online/Doppelwandler).
c) Empfehlen Sie der Schnellinger GmbH eine Klasse für den Serverraum mit geschäftskritischen Datenbanken und begründen Sie.',
 'a) Zuordnung:\nPlan A = VFD (Off-Line/Standby) — Netz fließt direkt durch, Akku nur bei Ausfall aktiv.\nPlan B = VFI (Online/Doppelwandler) — permanente AC→DC→AC-Wandlung, Bypass als Notfall.\nPlan C = VI (Line-Interactive) — AVR regelt Spannung kontinuierlich, Akku nur bei Ausfall.

b) Synonyme:\nVFD = Off-Line / Standby-USV.\nVFI = Online / Doppelwandler / Dauerwandler / Double-Conversion.\nVI = Line-Interactive / Netzinteraktiv / Delta-Conversion.

c) Empfehlung für geschäftskritische Datenbanken: VFI (Plan B).\nBegründung: (1) Keine Umschaltzeit (0 ms statt 4-10 ms) — Datenbank-Transaktionen werden nicht abgebrochen. (2) Vollständige Filterung auch gegen Frequenzschwankungen, Oberschwingungen und Burst — schützt empfindliche Server-Netzteile. (3) Sinusförmige Ausgangsspannung — schont PSUs. (4) Bypass ermöglicht Wartung ohne Produktionsausfall.\nNachteile (für Vollständigkeit): höherer Preis, ca. 90 % Wirkungsgrad (mehr Energiekosten), Akku-Lebensdauer nur 3-4 Jahre.',
 '{"required_concepts": ["Plan A VFD Off-Line", "Plan B VFI Online Doppelwandler", "Plan C VI Line-Interactive AVR", "Empfehlung VFI", "0 ms Umschaltzeit", "Datenbank-Transaktion", "Frequenzschutz", "Bypass Wartung"]}',
 '[{"criterion": "Korrekte Klassenzuordnung A/B/C", "weight": 3, "description": "VFD/VFI/VI richtig", "required": true},
   {"criterion": "Deutsche Synonyme", "weight": 2, "description": "Off-Line/Online/Line-Interactive", "required": true},
   {"criterion": "Empfehlung mit Begründung", "weight": 4, "description": "VFI mit 2+ Argumenten", "required": true},
   {"criterion": "Trade-off erwähnt", "weight": 1, "description": "Preis / Wirkungsgrad / Akku-Lebensdauer", "required": false}]',
 10, 'W2026-BW-Schnellinger-Schaltbild', 5, 1200),

-- ============================================================
-- USV — Sinusform und Wirkungsgrad (BW-Detailfrage)
-- ============================================================

('usv', 'cued',
 'Warum liefert eine VFD-USV nur eine "trapezförmige" Ausgangsspannung bei Akkubetrieb, und warum ist das ein Problem für manche Verbraucher?',
 'VFD-USVs haben einen einfachen Wechselrichter, der eine stufenförmige Näherung an die Sinus-Kurve ausgibt — das Ergebnis sieht trapezförmig aus (Rechteck mit abgerundeten Ecken).\n\nProblem: Moderne Netzteile mit PFC, Server, Medizintechnik und induktive Lasten (Motoren) erwarten eine SAUBERE Sinus-Spannung:\n1. Trapez-Spannung enthält Oberschwingungen → erzeugt Wärme im Netzteil → vorzeitiger Ausfall.\n2. PFC-Netzteile können die Kurve nicht korrekt gleichrichten → hoher Wirkungsgradverlust.\n3. Motoren brummen mechanisch, laufen unruhig.\n\nVI- und VFI-USVs liefern echte Sinusform. Deshalb VFD nur für unkritische Desktop-PCs/einfache Monitore geeignet.',
 '{"required_concepts": ["trapezförmig = Näherung Sinus", "Oberschwingungen", "PFC-Netzteil Problem", "Sinus bei VI und VFI", "VFD nur unkritisch"]}',
 NULL, 4, 'ki-generated-lindner-skript', 4, 240),

('usv', 'cued',
 'Vergleichen Sie die Wirkungsgrade der drei USV-Klassen VFD, VI und VFI.',
 'VFD (Off-Line): bis zu 99 % — Netz fließt ungehindert durch, kein Verlust.\nVI (Line-Interactive): ca. 97-98 % — leichter Verlust durch AVR und Filter.\nVFI (Online): nur ca. 90 % — permanente AC→DC→AC-Wandlung verbraucht Energie.\n\nKonsequenz für BW-Wirtschaftlichkeitsrechnung: Eine 2000 VA VFI-USV verbraucht im Jahresbetrieb ca. 10 % der durchfließenden Energie als Eigenverlust — bei 24/7-Betrieb kann das mehrere hundert Euro Stromkosten/Jahr bedeuten. Bei geschäftskritischen Systemen rechtfertigt der Schutz diese Mehrkosten; für Office-PCs reicht eine VI-USV.',
 '{"required_concepts": ["VFD 99%", "VI 97-98%", "VFI 90%", "Wirtschaftlichkeit 24/7", "Schutz rechtfertigt Mehrkosten bei kritisch"]}',
 NULL, 3, 'ki-generated-lindner-skript', 3, 180)

) AS v(slug, item_type, prompt, model_answer,
       expected_answer_structure, grading_criteria, points, source_exam, difficulty, estimated_time_sec)
JOIN topic_lookup t ON t.slug = v.slug;

-- Expected-Points für USV hochziehen (BW-typisch 20-28 P in Netzwerk/Infrastruktur-Teil)
UPDATE assessments.ap2_topics
SET expected_points = 24,
    priority = 'sehr-hoch'
WHERE slug = 'usv';

COMMIT;
