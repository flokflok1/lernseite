-- ============================================================================
-- Migration: 136_ap2_calculator_hints.sql
-- Description: Aktiver Taschenrechner-Guide für Application-Items mit
--              Berechnungen. Pascal nutzt Casio FX-991DE X in Prüfung
--              (11.05. WISO, 12.05. AP2). Schritt-für-Schritt Tastendruck-
--              Sequenzen werden im UI als ausklappbares Panel angezeigt.
--
--              Schema:
--              calculator_hint = JSONB mit Array von Steps:
--                [{"keys": "4200 × 1.7 SHIFT + % =", "result": "71.40",
--                  "note": "paritätischer PV-Anteil des AN"}]
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-04-18
-- ============================================================================

-- Spalte anlegen (nullable — nur rechnerische Items brauchen den Guide)
ALTER TABLE assessments.ap2_learning_items
    ADD COLUMN IF NOT EXISTS calculator_hint JSONB;

COMMENT ON COLUMN assessments.ap2_learning_items.calculator_hint IS
'Optionaler Schritt-für-Schritt Taschenrechner-Guide (Casio FX-991DE X).
Format: {"mode": "1 Berechnungen", "setup_note": "…", "steps": [{"keys": "…", "result": "…", "note": "…"}], "exam_tip": "…"}';

-- ============================================================================
-- Seed Calculator Hints für wichtigste Rechenaufgaben
-- ============================================================================

-- Helper: Update pro Item anhand von prompt-Suchbegriff (robust auch wenn IDs variieren)

-- 1. Sozialversicherung — 4200€ Brutto, kinderlos
UPDATE assessments.ap2_learning_items
SET calculator_hint = '{
    "mode": "1: Berechnungen",
    "setup_note": "Stelle sicher: MODE 1 (Berechnungen), SETUP → 1 (MathIO) für natürliche Darstellung.",
    "steps": [
        {"keys": "4200 × 1.7 SHIFT + ( % ) =", "result": "71,4", "note": "Paritätischer PV-Anteil AN (1,7 %)"},
        {"keys": "4200 × 0.6 SHIFT + ( % ) =", "result": "25,2", "note": "Kinderlosenzuschlag allein (0,6 %)"},
        {"keys": "71.4 + 25.2 =", "result": "96,6", "note": "Summe AN-Anteil PV"},
        {"keys": "STO → A (zum Speichern)", "result": "A = 96.6", "note": "Zwischenergebnis merken, falls mehr Säulen gefragt"}
    ],
    "exam_tip": "Die %-Taste ist SHIFT gefolgt von [(]. Also: Zahl × Prozent SHIFT [(] =. Ergebnis ist sofort der Prozent-Wert. Mit der Ans-Taste kannst du fortlaufend rechnen ohne Zwischenergebnisse abzuschreiben."
}'::jsonb
WHERE source_exam = 'bw-stil-schnellinger-2026' AND prompt LIKE '%Anna Müller%';

-- 2. Gewinnverteilung GmbH — 60k bei 80/30/10
UPDATE assessments.ap2_learning_items
SET calculator_hint = '{
    "mode": "1: Berechnungen",
    "setup_note": "MODE 1. Für exakte Brüche: Template [a/b] über SHIFT + Bruch.",
    "steps": [
        {"keys": "60 + 30 + 10 =", "result": "100", "note": "Gesamt-Einlagen in Tausend EUR"},
        {"keys": "Bruch-Template: 60 ▢ 100 → × 90 =", "result": "54", "note": "Becker: 60/100 × 90 = 54 T€"},
        {"keys": "30 ÷ 100 × 90 =", "result": "27", "note": "Huber: 30/100 × 90 = 27 T€"},
        {"keys": "10 ÷ 100 × 90 =", "result": "9", "note": "Klein: 10/100 × 90 = 9 T€"},
        {"keys": "Ans + (vorher speichern) =", "result": "90", "note": "Kontrolle: 54+27+9 = 90 ✓"}
    ],
    "exam_tip": "Bruch-Eingabe mit Template spart Tipparbeit und zeigt die Formel prüfbar auf dem Display. Kettenrechnung: Ergebnis mit Ans weiterverwenden. Kontrollrechnung IMMER machen — der Prüfer liebt Nachvollziehbarkeit."
}'::jsonb
WHERE source_exam = 'bw-stil-it-systemhaus';

-- 3. Umsatz pro Mitarbeiter + %-Veränderung
UPDATE assessments.ap2_learning_items
SET calculator_hint = '{
    "mode": "1: Berechnungen",
    "setup_note": "SETUP → 4 (Fix) → 2 für 2 Nachkommastellen falls gewünscht. Oder nach Berechnung manuell runden.",
    "steps": [
        {"keys": "5000000 ÷ 40 =", "result": "125000", "note": "Umsatz/MA Vorjahr 2024"},
        {"keys": "5400000 ÷ 45 =", "result": "120000", "note": "Umsatz/MA aktuelles Jahr 2025"},
        {"keys": "( 120000 - 125000 ) ÷ 125000 × 100 =", "result": "-4,00", "note": "%-Veränderung vom Vorjahr aus"},
        {"keys": "3.5 - 4.2 =", "result": "-0,7", "note": "Reallohn-Berechnung: Nominal minus Inflation"}
    ],
    "exam_tip": "IMMER vom ALTEN Wert prozentual rechnen (nicht vom neuen). Klammern nicht vergessen bei (neu − alt). Fix-Mode in SETUP erspart manuelles Runden — aber auf Anzeige und Musterlösung achten: oft wird auf 2 Nachkommastellen erwartet."
}'::jsonb
WHERE source_exam = 'bw-stil-schnellinger-rechnung';

-- 4. BGB §622 Kündigungsfrist — Datumsrechnung
UPDATE assessments.ap2_learning_items
SET calculator_hint = '{
    "mode": "1: Berechnungen (Datumsrechnung manuell)",
    "setup_note": "Der FX-991DE X hat keine echte Kalenderfunktion. Datums-Aufgaben rechnet man im Kopf + Monatskalender. Aber: Jahres-Differenz als Entscheidungsgrundlage lässt sich prüfen.",
    "steps": [
        {"keys": "2026 - 2012 =", "result": "14", "note": "Betriebszugehörigkeit Herr A: 14 Jahre Ende 2025 → Stufe 12 Jahre greift"},
        {"keys": "2026 - 2014 =", "result": "12", "note": "Für Frau B analog"},
        {"keys": "Monatsdifferenz: Februar + 5 Monate = Juli", "result": "Juli 2026", "note": "Bei 5-Monats-Frist zum Monatsende: 31.07.2026"},
        {"keys": "Probezeit-Frist: 15. + 14 Tage = 1.3.", "result": "01.03.2026", "note": "Januar hat 31 Tage; 15.02 + 14 Tage = 01.03"}
    ],
    "exam_tip": "Die Datumsrechnung selbst macht der Taschenrechner NICHT. Nutze Monatslogik im Kopf: Februar hat 28 Tage (2026 ist kein Schaltjahr). Der Rechner hilft nur beim Zählen der Jahre zur Stufen-Zuordnung. TIPP: Kleine Tabelle im Konzept zeichnen: Monat | Ende-Datum — das macht die Prüfung übersichtlicher."
}'::jsonb
WHERE source_exam = 'bw-stil-schnellinger-kuendigung';

-- 5. USV-Kapazität (aus bestehendem USV-Topic)
UPDATE assessments.ap2_learning_items
SET calculator_hint = '{
    "mode": "1: Berechnungen",
    "setup_note": "Normale Multiplikation und Division. Für Zeit-Umrechnung Stunden in Minuten Bruch-Template hilfreich.",
    "steps": [
        {"keys": "2 × 800 + 3 × 200 + 150 + 200 + 150 =", "result": "2700", "note": "Gesamtlast in Watt"},
        {"keys": "20 ÷ 60 =", "result": "0,333…", "note": "20 Minuten in Stunden (besser als Bruch 1/3)"},
        {"keys": "Ans × 2700 =", "result": "900", "note": "Wirkenergie in Wh für 20 Min"},
        {"keys": "900 ÷ 0.8 =", "result": "1125", "note": "Mit 20%-Reserve-Faktor (Tiefentladeschutz)"},
        {"keys": "Ans ÷ 12 =", "result": "93,75", "note": "Benötigte Akkukapazität in Ah bei 12 V"}
    ],
    "exam_tip": "Statt 20/60 kannst du den Bruch 1/3 als Template eingeben — exaktere Zwischenergebnisse. Mit der Ans-Taste Kettenrechnung aufbauen: 2700 × 1/3 ÷ 0.8 ÷ 12 = 93,75. Ein Eingabevorgang, keine Abschreibfehler."
}'::jsonb
WHERE source_exam = 'W2026-BW-Lindner-Uebung-2';

-- 6. USV-Kapazität GIGA-1
UPDATE assessments.ap2_learning_items
SET calculator_hint = '{
    "mode": "1: Berechnungen",
    "setup_note": "MODE 1. Nutze Ans-Taste für aufeinanderfolgende Modellprüfungen.",
    "steps": [
        {"keys": "4200 × 20 ÷ 60 =", "result": "1400", "note": "Benötigte Energie für 20 Min bei 4200 W"},
        {"keys": "12 × 90 =", "result": "1080", "note": "ALPHA-USV (90 Ah): Wh-Kapazität"},
        {"keys": "12 × 120 =", "result": "1440", "note": "BETA-USV (120 Ah): knapp genug"},
        {"keys": "12 × 150 =", "result": "1800", "note": "GIGA-1 (150 Ah): sicher"},
        {"keys": "12 × 200 =", "result": "2400", "note": "OMEGA-USV (200 Ah): viel Reserve"}
    ],
    "exam_tip": "Energieformel: U × C (bei cos φ = 1). Für jede Modell-Option einmal × drücken. Ergebnisse mit dem geforderten Bedarf vergleichen. Tipp: Nutze den REPLAY-Knopf (Pfeile) um die letzte Eingabe zu bearbeiten — ersetze einfach die Ah-Zahl."
}'::jsonb
WHERE source_exam = 'W2026-BW-Lindner-Uebung-1';

-- 7. cos φ Wirkleistung vs Scheinleistung
UPDATE assessments.ap2_learning_items
SET calculator_hint = '{
    "mode": "1: Berechnungen",
    "setup_note": "Normale Multiplikation, Division und Prozentrechnung.",
    "steps": [
        {"keys": "450 × 0.85 =", "result": "382,5", "note": "Wirkleistung P = S × cos φ"},
        {"keys": "450 - 382.5 =", "result": "67,5", "note": "Verlustleistung (Wärme)"},
        {"keys": "3 × 450 =", "result": "1350", "note": "3 Server × Scheinleistung"},
        {"keys": "Ans × 1.25 =", "result": "1687,5", "note": "Mit 25% Sicherheitszuschlag"}
    ],
    "exam_tip": "Sicherheitszuschlag 25% → Multiplikation mit 1.25 (schneller als separate % Rechnung). Der FX-991DE X zeigt im MathIO-Modus auch Nachkommastellen präzise — keine Rundungsfehler."
}'::jsonb
WHERE source_exam = 'W2026-BW-Lindner-Uebung-3';

-- 8. RAID Kapazitätsberechnung
UPDATE assessments.ap2_learning_items
SET calculator_hint = '{
    "mode": "1: Berechnungen",
    "setup_note": "MODE 1. Einfache Multiplikation pro RAID-Level.",
    "steps": [
        {"keys": "( 8 - 1 ) × 4 =", "result": "28", "note": "RAID 5: (n-1) × Plattengröße"},
        {"keys": "( 8 - 2 ) × 4 =", "result": "24", "note": "RAID 6: (n-2) × Plattengröße"},
        {"keys": "8 ÷ 2 × 4 =", "result": "16", "note": "RAID 10: n/2 × Plattengröße"},
        {"keys": "16 ÷ 28 × 100 =", "result": "57,14", "note": "Optional: RAID 10 hat nur 57 % der RAID-5-Kapazität"}
    ],
    "exam_tip": "Klammern konsequent setzen, damit Rechnungsreihenfolge stimmt. RAID-Formeln auswendig: 5=n-1, 6=n-2, 10=n/2 (alle × Plattengröße). Kontrolle: Summen kleiner als Rohkapazität (8×4=32 TB)."
}'::jsonb
WHERE source_exam = 'W2026-BW-AP1-Pattern-RAID';

-- 9. Verfügbarkeitsklassen
UPDATE assessments.ap2_learning_items
SET calculator_hint = '{
    "mode": "1: Berechnungen",
    "setup_note": "SETUP → 4 FIX → 2 für Minuten-Anzeige mit 2 Nachkomma.",
    "steps": [
        {"keys": "365 × 24 × 60 =", "result": "525600", "note": "Minuten pro Jahr"},
        {"keys": "Ans × 0.001 =", "result": "525,6", "note": "Klasse 3 (99,9 %): 525,6 min Downtime"},
        {"keys": "525600 × 0.0001 =", "result": "52,56", "note": "Klasse 4 (99,99 %): 52,56 min"},
        {"keys": "525600 × 0.00001 =", "result": "5,256", "note": "Klasse 5 (99,999 %): 5,256 min"}
    ],
    "exam_tip": "Prozent-Komma-Stellen zählen: 99,9 % → 0,1 % Ausfall → 0.001 als Faktor. Für die höheren Klassen jeweils eine Null mehr vor der 1. Ergebnis in Stunden umrechnen: ÷ 60 zusätzlich."
}'::jsonb
WHERE prompt LIKE '%Verfügbarkeitsklassen%' AND prompt LIKE '%99,999%';

-- 10. IPv6 EUI-64 (keine Rechnung, aber Bit-Manipulation)
UPDATE assessments.ap2_learning_items
SET calculator_hint = '{
    "mode": "3: Basis-N (Binär/Hex)",
    "setup_note": "MODE 3 (Basis-N). Standardmäßig Hex. Mit [DEC][HEX][BIN][OCT]-Tasten zwischen Basen wechseln.",
    "steps": [
        {"keys": "MODE 3", "result": "Basis-N aktiv", "note": "Umschalten auf Hex/Bin-Rechner"},
        {"keys": "HEX → DC → =", "result": "DC (Hex)", "note": "Erstes MAC-Oktett eingeben"},
        {"keys": "Umschalt auf BIN: 11011100", "result": "1101 1100", "note": "DC in Binär — 7. Bit ist 0"},
        {"keys": "7. Bit flippen → 11011110", "result": "1101 1110", "note": "Umschalt auf HEX: DE"},
        {"keys": "Ergebnis notieren: DE", "result": "DE56:7BFF:FEF8:8913", "note": "EUI-64 Suffix vollständig"}
    ],
    "exam_tip": "Modus 3 (Basis-N) ist GENAU für solche Bit-Aufgaben gebaut. Du kannst Eingabe in Hex und Anzeige in Binär umschalten — das macht das U/L-Bit-Invertieren visuell. Nach Fertig: MODE 1 zurück!"
}'::jsonb
WHERE source_exam = 'W2026-BW-Lindner-EUI64';

-- 11. IPv6 Subnetting (2^n Rechnung)
UPDATE assessments.ap2_learning_items
SET calculator_hint = '{
    "mode": "1: Berechnungen (Potenz-Taste)",
    "setup_note": "MODE 1. Nutze die [x^y] Taste oder [^] für Potenzen.",
    "steps": [
        {"keys": "64 - 56 =", "result": "8", "note": "Subnetz-Bits aus Präfix-Differenz"},
        {"keys": "2 x^y 8 =", "result": "256", "note": "Mögliche /64-Subnetze aus /56"},
        {"keys": "2 ^ 4 =", "result": "16", "note": "Bei /60 wären nur 16 Subnetze"},
        {"keys": "2 ^ 16 =", "result": "65536", "note": "Bei /48 → /64 wären 65.536 Subnetze"}
    ],
    "exam_tip": "Die [x^y]-Taste oder [^] ist DEINE Freundin bei Bit-Rechnungen. Merke: Subnetz-Anzahl = 2^(Unterschied der Präfix-Längen). Potenz von 2: 2^8=256, 2^10=1024, 2^16=65536 — kann man auswendig."
}'::jsonb
WHERE source_exam = 'W2026-BW-AP1-Pattern-IPv6';

-- 12. Zuschlagskalkulation (existierendes Topic)
UPDATE assessments.ap2_learning_items
SET calculator_hint = '{
    "mode": "1: Berechnungen",
    "setup_note": "MODE 1. Rückwärtskalkulation: immer von unten (Listenverkaufspreis) nach oben (Bezugspreis). Nutze Ans-Taste für Kette.",
    "steps": [
        {"keys": "1000 ÷ 1.05 =", "result": "952,38", "note": "Minus 5 % Gewinn → Selbstkostenpreis"},
        {"keys": "Ans ÷ 1.20 =", "result": "793,65", "note": "Minus 20 % Handlungskosten → Bezugspreis"},
        {"keys": "Ans - 25 =", "result": "768,65", "note": "Minus 25 EUR Bezugskosten → Einstandspreis"},
        {"keys": "Ans ÷ 0.97 =", "result": "792,42", "note": "Plus 3 % Skonto zurück → Zieleinkaufspreis"},
        {"keys": "Ans ÷ 0.90 =", "result": "880,46", "note": "Plus 10 % Rabatt zurück → Listeneinkaufspreis"}
    ],
    "exam_tip": "GOLDENE REGEL Rückwärtskalkulation: Prozent-Aufschlag = Division durch (1 + Prozent/100). Bei Rabatt/Skonto = Division durch (1 - Prozent/100). Immer mit Ans-Taste fortsetzen — keine Zwischenwerte abtippen (Fehlerquelle!)."
}'::jsonb
WHERE prompt LIKE '%Listenverkaufspreis%' OR prompt LIKE '%Rückwärtskalkulation%'
  OR prompt LIKE '%Zuschlagskalkulation%' OR prompt LIKE '%Handelskalkulation%';

-- 13. Autonomiezeit USV
UPDATE assessments.ap2_learning_items
SET calculator_hint = '{
    "mode": "1: Berechnungen",
    "setup_note": "MODE 1.",
    "steps": [
        {"keys": "12 × 100 × 0.85 =", "result": "1020", "note": "Wirkenergie (U × C × cos φ) in Wh"},
        {"keys": "Ans ÷ 600 =", "result": "1,7", "note": "Autonomiezeit in Stunden"},
        {"keys": "Ans × 60 =", "result": "102", "note": "In Minuten"}
    ],
    "exam_tip": "Formel: t = (U × C × cos φ) / P_Last. Ergebnis in Stunden, ggf. ×60 für Minuten. Merke: 1 Ah bei 12 V = 12 Wh Scheinleistung. Mit cos φ = 0,85 → 10,2 Wh Wirkenergie."
}'::jsonb
WHERE prompt LIKE '%Autonomiezeit%' AND source_exam = 'ki-generated-lindner-skript';

COMMIT;
