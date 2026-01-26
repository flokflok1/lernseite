-- ============================================================================
-- Seed Data: Math Patterns & Categories
-- Description: IHK-relevant math patterns for MathToolkit (dynamically configured)
-- Source: 068_consolidated.sql
-- Author: LernsystemX Migration System
-- Date: 2026-01-26
-- Phase: 4 (Seed Data)
-- ============================================================================

-- ============================================================================
-- Math Pattern Categories (8 categories - IHK-relevant)
-- ============================================================================

INSERT INTO learning_methods.math_pattern_categories (category_code, name, description, icon, color, sort_order)
VALUES
    ('percent', 'Prozentrechnung', 'Grundwert, Prozentsatz, Prozentwert', '📊', '#3B82F6', 10),
    ('calculation', 'Handelskalkulation', 'Bezugs-, Verkaufs- und Selbstkostenkalkulation', '🧮', '#10B981', 20),
    ('interest', 'Zinsrechnung', 'Einfache Zinsen, Zinseszins, Effektivzins', '💰', '#F59E0B', 30),
    ('ratio', 'Dreisatz & Verhältnisse', 'Einfacher/Doppelter Dreisatz, Verhältnisrechnung', '⚖️', '#8B5CF6', 40),
    ('currency', 'Währungsrechnung', 'Umrechnung, Kurse, Arbitrage', '💱', '#EC4899', 50),
    ('statistics', 'Statistik', 'Mittelwerte, Streuung, Häufigkeiten', '📈', '#06B6D4', 60),
    ('geometry', 'Geometrie', 'Flächen, Volumen, Umfang', '📐', '#84CC16', 70),
    ('algebra', 'Algebra', 'Gleichungen, Terme, Funktionen', '🔢', '#F97316', 80)
ON CONFLICT (category_code) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    icon = EXCLUDED.icon,
    color = EXCLUDED.color,
    sort_order = EXCLUDED.sort_order,
    updated_at = NOW();

-- ============================================================================
-- Math Patterns (6 IHK-relevant patterns for core competencies)
-- ============================================================================

-- Bezugskalkulation
INSERT INTO learning_methods.math_patterns (category_id, pattern_code, name, description, formula_template, formula_latex, variables, steps_template, example_values, difficulty, ihk_relevant, tags)
SELECT
    (SELECT category_id FROM learning_methods.math_pattern_categories WHERE category_code = 'calculation'),
    'bezugskalkulation',
    'Bezugskalkulation',
    'Berechnung des Einstandspreises (Bezugspreis) aus Listeneinkaufspreis abzüglich Rabatt und Skonto plus Bezugskosten.',
    'BEP = (LEP - Rabatt) - Skonto + Bezugskosten',
    'BEP = (LEP - \frac{LEP \cdot r}{100}) \cdot (1 - \frac{s}{100}) + BK',
    '[{"var": "LEP", "name": "Listeneinkaufspreis", "unit": "€"},
      {"var": "r", "name": "Rabatt", "unit": "%"},
      {"var": "s", "name": "Skonto", "unit": "%"},
      {"var": "BK", "name": "Bezugskosten", "unit": "€"},
      {"var": "BEP", "name": "Bezugspreis/Einstandspreis", "unit": "€"}]'::jsonb,
    '[{"step": 1, "description": "Lieferantenrabatt berechnen", "formula": "Rabatt = LEP × r / 100", "hint": "Rabatt wird vom Listenpreis abgezogen"},
      {"step": 2, "description": "Zieleinkaufspreis ermitteln", "formula": "ZEP = LEP - Rabatt", "hint": "Nach Abzug des Rabatts"},
      {"step": 3, "description": "Lieferantenskonto berechnen", "formula": "Skonto = ZEP × s / 100", "hint": "Skonto bei Barzahlung"},
      {"step": 4, "description": "Bareinkaufspreis ermitteln", "formula": "BEP_bar = ZEP - Skonto", "hint": "Preis bei sofortiger Zahlung"},
      {"step": 5, "description": "Bezugskosten addieren", "formula": "BEP = BEP_bar + BK", "hint": "Transport, Verpackung, Versicherung"}]'::jsonb,
    '{"LEP": 1000, "r": 20, "s": 2, "BK": 50}'::jsonb,
    3, TRUE, '["ihk", "kaufmann", "bwl", "kalkulation"]'::jsonb
WHERE NOT EXISTS (SELECT 1 FROM learning_methods.math_patterns WHERE pattern_code = 'bezugskalkulation');

-- Prozentrechnung: Grundwert
INSERT INTO learning_methods.math_patterns (category_id, pattern_code, name, description, formula_template, formula_latex, variables, steps_template, example_values, difficulty, ihk_relevant, tags)
SELECT
    (SELECT category_id FROM learning_methods.math_pattern_categories WHERE category_code = 'percent'),
    'prozent_grundwert',
    'Prozent: Grundwert berechnen',
    'Berechnung des Grundwerts aus Prozentwert und Prozentsatz.',
    'G = W × 100 / p',
    'G = \frac{W \cdot 100}{p}',
    '[{"var": "G", "name": "Grundwert", "unit": ""},
      {"var": "W", "name": "Prozentwert", "unit": ""},
      {"var": "p", "name": "Prozentsatz", "unit": "%"}]'::jsonb,
    '[{"step": 1, "description": "Formel anwenden", "formula": "G = W × 100 / p", "hint": "Prozentwert durch Prozentsatz, dann mal 100"}]'::jsonb,
    '{"W": 150, "p": 25}'::jsonb,
    1, TRUE, '["prozent", "grundlagen"]'::jsonb
WHERE NOT EXISTS (SELECT 1 FROM learning_methods.math_patterns WHERE pattern_code = 'prozent_grundwert');

-- Prozentrechnung: Prozentwert
INSERT INTO learning_methods.math_patterns (category_id, pattern_code, name, description, formula_template, formula_latex, variables, steps_template, example_values, difficulty, ihk_relevant, tags)
SELECT
    (SELECT category_id FROM learning_methods.math_pattern_categories WHERE category_code = 'percent'),
    'prozent_prozentwert',
    'Prozent: Prozentwert berechnen',
    'Berechnung des Prozentwerts aus Grundwert und Prozentsatz.',
    'W = G × p / 100',
    'W = \frac{G \cdot p}{100}',
    '[{"var": "G", "name": "Grundwert", "unit": ""},
      {"var": "W", "name": "Prozentwert", "unit": ""},
      {"var": "p", "name": "Prozentsatz", "unit": "%"}]'::jsonb,
    '[{"step": 1, "description": "Formel anwenden", "formula": "W = G × p / 100", "hint": "Grundwert mal Prozentsatz, geteilt durch 100"}]'::jsonb,
    '{"G": 600, "p": 25}'::jsonb,
    1, TRUE, '["prozent", "grundlagen"]'::jsonb
WHERE NOT EXISTS (SELECT 1 FROM learning_methods.math_patterns WHERE pattern_code = 'prozent_prozentwert');

-- Einfacher Dreisatz
INSERT INTO learning_methods.math_patterns (category_id, pattern_code, name, description, formula_template, formula_latex, variables, steps_template, example_values, difficulty, ihk_relevant, tags)
SELECT
    (SELECT category_id FROM learning_methods.math_pattern_categories WHERE category_code = 'ratio'),
    'dreisatz_einfach',
    'Einfacher Dreisatz',
    'Proportionale Zuordnung: Je mehr, desto mehr.',
    'x = (a2 × b1) / a1',
    'x = \frac{a_2 \cdot b_1}{a_1}',
    '[{"var": "a1", "name": "Ausgangsmenge A", "unit": ""},
      {"var": "b1", "name": "Ausgangsmenge B", "unit": ""},
      {"var": "a2", "name": "Gesuchte Menge A", "unit": ""},
      {"var": "x", "name": "Gesuchte Menge B", "unit": ""}]'::jsonb,
    '[{"step": 1, "description": "Auf 1 Einheit umrechnen", "formula": "1 × A = b1 / a1", "hint": "Teile B durch A"},
      {"step": 2, "description": "Auf gesuchte Menge hochrechnen", "formula": "x = (b1 / a1) × a2", "hint": "Multipliziere mit der gesuchten A-Menge"}]'::jsonb,
    '{"a1": 5, "b1": 15, "a2": 8}'::jsonb,
    1, TRUE, '["dreisatz", "grundlagen"]'::jsonb
WHERE NOT EXISTS (SELECT 1 FROM learning_methods.math_patterns WHERE pattern_code = 'dreisatz_einfach');

-- Einfache Zinsrechnung
INSERT INTO learning_methods.math_patterns (category_id, pattern_code, name, description, formula_template, formula_latex, variables, steps_template, example_values, difficulty, ihk_relevant, tags)
SELECT
    (SELECT category_id FROM learning_methods.math_pattern_categories WHERE category_code = 'interest'),
    'zins_einfach',
    'Einfache Zinsrechnung',
    'Berechnung der Zinsen für Kapital, Zinssatz und Zeit.',
    'Z = K × p × t / (100 × 360)',
    'Z = \frac{K \cdot p \cdot t}{100 \cdot 360}',
    '[{"var": "K", "name": "Kapital", "unit": "€"},
      {"var": "p", "name": "Zinssatz", "unit": "% p.a."},
      {"var": "t", "name": "Zeit", "unit": "Tage"},
      {"var": "Z", "name": "Zinsen", "unit": "€"}]'::jsonb,
    '[{"step": 1, "description": "Jahreszinsen berechnen", "formula": "Jahreszins = K × p / 100", "hint": "Kapital mal Zinssatz"},
      {"step": 2, "description": "Tageszinsen ermitteln", "formula": "Z = Jahreszins × t / 360", "hint": "Kaufmännisches Jahr = 360 Tage"}]'::jsonb,
    '{"K": 10000, "p": 5, "t": 90}'::jsonb,
    2, TRUE, '["zins", "bankkaufmann", "ihk"]'::jsonb
WHERE NOT EXISTS (SELECT 1 FROM learning_methods.math_patterns WHERE pattern_code = 'zins_einfach');

-- Verkaufskalkulation
INSERT INTO learning_methods.math_patterns (category_id, pattern_code, name, description, formula_template, formula_latex, variables, steps_template, example_values, difficulty, ihk_relevant, tags)
SELECT
    (SELECT category_id FROM learning_methods.math_pattern_categories WHERE category_code = 'calculation'),
    'verkaufskalkulation',
    'Verkaufskalkulation',
    'Ermittlung des Bruttoverkaufspreises aus Selbstkostenpreis über Gewinn, Kundenskonto, Kundenrabatt und MwSt.',
    'BVP = ((SKP + Gewinn) / (1 - Skonto%) / (1 - Rabatt%)) × (1 + MwSt%)',
    'BVP = \frac{SKP + G}{(1-s)(1-r)} \cdot (1 + m)',
    '[{"var": "SKP", "name": "Selbstkostenpreis", "unit": "€"},
      {"var": "gewinn_pct", "name": "Gewinnzuschlag", "unit": "%"},
      {"var": "skonto_pct", "name": "Kundenskonto", "unit": "%"},
      {"var": "rabatt_pct", "name": "Kundenrabatt", "unit": "%"},
      {"var": "mwst_pct", "name": "Mehrwertsteuer", "unit": "%"},
      {"var": "BVP", "name": "Bruttoverkaufspreis", "unit": "€"}]'::jsonb,
    '[{"step": 1, "description": "Gewinn aufschlagen", "formula": "Barverkaufspreis = SKP × (1 + Gewinn%/100)", "hint": "Gewinnmarge hinzurechnen"},
      {"step": 2, "description": "Skonto einrechnen", "formula": "Zielverkaufspreis = BVP_bar / (1 - Skonto%/100)", "hint": "Skonto im Hundert"},
      {"step": 3, "description": "Rabatt einrechnen", "formula": "Nettoverkaufspreis = ZVP / (1 - Rabatt%/100)", "hint": "Rabatt im Hundert"},
      {"step": 4, "description": "MwSt aufschlagen", "formula": "Bruttoverkaufspreis = NVP × (1 + MwSt%/100)", "hint": "19% oder 7% MwSt"}]'::jsonb,
    '{"SKP": 800, "gewinn_pct": 25, "skonto_pct": 2, "rabatt_pct": 10, "mwst_pct": 19}'::jsonb,
    4, TRUE, '["ihk", "kaufmann", "bwl", "kalkulation"]'::jsonb
WHERE NOT EXISTS (SELECT 1 FROM learning_methods.math_patterns WHERE pattern_code = 'verkaufskalkulation');

-- ============================================================================
-- Verification
-- ============================================================================

SELECT COUNT(*) as total_math_categories FROM learning_methods.math_pattern_categories;
SELECT COUNT(*) as total_math_patterns FROM learning_methods.math_patterns;
