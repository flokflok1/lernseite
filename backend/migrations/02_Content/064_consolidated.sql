-- ============================================================================
-- Migration 070: MathToolkit - Dynamisches Mathe-Lern-System
-- ============================================================================
--
-- Flexibles, dynamisches System für:
-- 1. Taschenrechner mit Rechenweg-Tracking
-- 2. Rechenweg-Builder (Schritt-für-Schritt)
-- 3. Muster-Erkennung (Pattern Recognition)
-- 4. Tutorial-Modus mit Scaffolding
-- 5. Formel-Bibliothek
--
-- Alles dynamisch konfigurierbar, nichts hardcoded!
--
-- ============================================================================

-- ============================================================================
-- 1. math_pattern_categories - Kategorien für Rechenarten
-- ============================================================================

CREATE TABLE IF NOT EXISTS learning_methods.math_pattern_categories (
    category_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    icon VARCHAR(50),
    color VARCHAR(20),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_math_pattern_cat_active ON learning_methods.math_pattern_categories (is_active, sort_order);

COMMENT ON TABLE learning_methods.math_pattern_categories IS
'Kategorien für Rechenarten (z.B. Prozent, Kalkulation, Zins). Dynamisch erweiterbar.';

-- ============================================================================
-- 1b. Standard Math Pattern Categories (IHK-relevant)
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
-- 2. math_patterns - Dynamische Rechenmuster
-- ============================================================================

CREATE TABLE IF NOT EXISTS learning_methods.math_patterns (
    pattern_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_id UUID REFERENCES learning_methods.math_pattern_categories(category_id) ON DELETE SET NULL,
    pattern_code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(150) NOT NULL,
    description TEXT,

    -- Formel-Definition (dynamisch)
    formula_template TEXT NOT NULL,
    formula_latex TEXT,

    -- Variablen-Definition (JSONB für Flexibilität)
    -- z.B. [{"var": "G", "name": "Grundwert", "unit": "€"}, {"var": "p", "name": "Prozentsatz", "unit": "%"}]
    variables JSONB NOT NULL DEFAULT '[]',

    -- Schritte-Template (dynamisch)
    -- z.B. [{"step": 1, "description": "Grundwert ermitteln", "formula": "G = ...", "hint": "..."}]
    steps_template JSONB NOT NULL DEFAULT '[]',

    -- Beispiel-Werte für Tutorial
    example_values JSONB DEFAULT '{}',

    -- Schwierigkeit & Meta
    difficulty INTEGER DEFAULT 1 CHECK (difficulty BETWEEN 1 AND 5),
    ihk_relevant BOOLEAN DEFAULT FALSE,
    tags JSONB DEFAULT '[]',

    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_math_patterns_category ON learning_methods.math_patterns (category_id);
CREATE INDEX IF NOT EXISTS idx_math_patterns_active ON learning_methods.math_patterns (is_active, sort_order);
CREATE INDEX IF NOT EXISTS idx_math_patterns_ihk ON learning_methods.math_patterns (ihk_relevant) WHERE ihk_relevant = TRUE;
CREATE INDEX IF NOT EXISTS idx_math_patterns_tags ON learning_methods.math_patterns USING GIN(tags);

COMMENT ON TABLE learning_methods.math_patterns IS
'Dynamische Rechenmuster mit Formel-Templates und Schritt-Definitionen.
Alles über JSONB konfigurierbar, keine hardcoded Logik.';

-- ============================================================================
-- 3. math_formulas - Formel-Bibliothek
-- ============================================================================

CREATE TABLE IF NOT EXISTS learning_methods.math_formulas (
    formula_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_id UUID REFERENCES learning_methods.math_pattern_categories(category_id) ON DELETE SET NULL,
    pattern_id UUID REFERENCES learning_methods.math_patterns(pattern_id) ON DELETE SET NULL,

    name VARCHAR(150) NOT NULL,
    description TEXT,

    -- Formel in verschiedenen Formaten
    formula_text TEXT NOT NULL,
    formula_latex TEXT,
    formula_display TEXT,

    -- Variablen-Erklärung
    variables JSONB DEFAULT '[]',

    -- Beispiel
    example_input JSONB DEFAULT '{}',
    example_output VARCHAR(100),

    -- Meta
    tags JSONB DEFAULT '[]',
    is_favorite BOOLEAN DEFAULT FALSE,
    usage_count INTEGER DEFAULT 0,

    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_math_formulas_category ON learning_methods.math_formulas (category_id);
CREATE INDEX IF NOT EXISTS idx_math_formulas_pattern ON learning_methods.math_formulas (pattern_id);
CREATE INDEX IF NOT EXISTS idx_math_formulas_favorite ON learning_methods.math_formulas (is_favorite) WHERE is_favorite = TRUE;

COMMENT ON TABLE learning_methods.math_formulas IS
'Formel-Bibliothek für Schnellzugriff. Verknüpft mit Patterns.';

-- ============================================================================
-- 4. math_toolkit_sessions - Übungssitzungen
-- ============================================================================

CREATE TABLE IF NOT EXISTS learning_methods.math_toolkit_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,

    -- Kontext (optional)
    course_id UUID REFERENCES courses.courses(course_id) ON DELETE SET NULL,
    lesson_id UUID REFERENCES courses.lessons(lesson_id) ON DELETE SET NULL,
    learning_method_id UUID,

    -- Session-Typ
    session_type VARCHAR(30) NOT NULL DEFAULT 'practice',
    pattern_id UUID REFERENCES learning_methods.math_patterns(pattern_id) ON DELETE SET NULL,

    -- Scaffolding-Level (1=volle Hilfe, 2=Hinweise, 3=selbstständig)
    scaffolding_level INTEGER DEFAULT 1 CHECK (scaffolding_level BETWEEN 1 AND 3),

    -- Status
    started_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ,

    -- Ergebnis
    tasks_completed INTEGER DEFAULT 0,
    tasks_correct INTEGER DEFAULT 0,
    hints_used INTEGER DEFAULT 0,

    CONSTRAINT chk_session_type CHECK (session_type IN (
        'tutorial', 'practice', 'exam', 'pattern_recognition', 'free'
    ))
);

CREATE INDEX IF NOT EXISTS idx_math_sessions_user ON learning_methods.math_toolkit_sessions (user_id, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_math_sessions_pattern ON learning_methods.math_toolkit_sessions (pattern_id);
CREATE INDEX IF NOT EXISTS idx_math_sessions_active ON learning_methods.math_toolkit_sessions (ended_at) WHERE ended_at IS NULL;

COMMENT ON TABLE learning_methods.math_toolkit_sessions IS
'Übungssitzungen im MathToolkit. Trackt Fortschritt und Scaffolding-Level.';

-- ============================================================================
-- 5. math_calculation_steps - Gespeicherte Rechenschritte
-- ============================================================================

CREATE TABLE IF NOT EXISTS learning_methods.math_calculation_steps (
    step_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES learning_methods.math_toolkit_sessions(session_id) ON DELETE CASCADE,

    -- Schritt-Nummer
    step_number INTEGER NOT NULL,

    -- Was wurde eingegeben
    input_expression TEXT NOT NULL,
    input_values JSONB DEFAULT '{}',

    -- Ergebnis
    result_value DECIMAL(20, 6),
    result_display VARCHAR(100),

    -- Taschenrechner-Eingabe (für Replay)
    calculator_keystrokes JSONB DEFAULT '[]',

    -- Bewertung
    is_correct BOOLEAN,
    expected_value DECIMAL(20, 6),
    error_type VARCHAR(50),
    hint_shown TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_math_steps_session ON learning_methods.math_calculation_steps (session_id, step_number);

COMMENT ON TABLE learning_methods.math_calculation_steps IS
'Einzelne Rechenschritte mit Taschenrechner-Eingaben für Replay und Analyse.';

-- ============================================================================
-- 6. math_calculator_history - Taschenrechner-Verlauf
-- ============================================================================

CREATE TABLE IF NOT EXISTS learning_methods.math_calculator_history (
    history_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES learning_methods.math_toolkit_sessions(session_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,

    -- Eingabe
    expression TEXT NOT NULL,

    -- Ergebnis
    result DECIMAL(20, 6),
    result_display VARCHAR(100),

    -- Keystrokes für Replay
    keystrokes JSONB DEFAULT '[]',

    -- Memory-Werte
    memory_used BOOLEAN DEFAULT FALSE,
    memory_value DECIMAL(20, 6),

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_calc_history_user ON learning_methods.math_calculator_history (user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_calc_history_session ON learning_methods.math_calculator_history (session_id);

COMMENT ON TABLE learning_methods.math_calculator_history IS
'Taschenrechner-Verlauf für Analyse und Replay.';

-- ============================================================================
-- 7. math_user_progress - User-Fortschritt pro Pattern
-- ============================================================================

CREATE TABLE IF NOT EXISTS learning_methods.math_user_progress (
    progress_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),


-- ============================================================================
-- Migration: 064_math_toolkit_part2.sql
-- Description: Math Toolkit - Part 2: Advanced Features
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-01-16
-- ============================================================================
-- Note: Split from original 064_math_toolkit.sql (522 lines)
--       Part 2 of 2
-- ============================================================================

    user_id UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,
    pattern_id UUID NOT NULL REFERENCES learning_methods.math_patterns(pattern_id) ON DELETE CASCADE,

    -- Fortschritt
    current_level INTEGER DEFAULT 1 CHECK (current_level BETWEEN 1 AND 3),
    total_attempts INTEGER DEFAULT 0,
    correct_attempts INTEGER DEFAULT 0,

    -- Mastery (0-100%)
    mastery_score DECIMAL(5,2) DEFAULT 0,

    -- Streaks
    current_streak INTEGER DEFAULT 0,
    best_streak INTEGER DEFAULT 0,

    -- Letzte Aktivität
    last_practiced_at TIMESTAMPTZ,
    next_review_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE (user_id, pattern_id)
);

CREATE INDEX IF NOT EXISTS idx_math_progress_user ON learning_methods.math_user_progress (user_id);
CREATE INDEX IF NOT EXISTS idx_math_progress_pattern ON learning_methods.math_user_progress (pattern_id);
CREATE INDEX IF NOT EXISTS idx_math_progress_review ON learning_methods.math_user_progress (next_review_at)
    WHERE next_review_at IS NOT NULL;

COMMENT ON TABLE learning_methods.math_user_progress IS
'User-Fortschritt pro Rechenmuster. Trackt Mastery und Spaced Repetition.';

-- ============================================================================
-- 8. math_pattern_recognition_tasks - Muster-Erkennungs-Aufgaben
-- ============================================================================

CREATE TABLE IF NOT EXISTS learning_methods.math_pattern_recognition_tasks (
    task_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pattern_id UUID NOT NULL REFERENCES learning_methods.math_patterns(pattern_id) ON DELETE CASCADE,

    -- Aufgabenstellung
    task_type VARCHAR(30) NOT NULL,
    task_text TEXT NOT NULL,

    -- Aufgaben-Daten (dynamisch)
    task_data JSONB NOT NULL DEFAULT '{}',

    -- Lösung
    solution JSONB NOT NULL DEFAULT '{}',

    -- Schwierigkeit
    difficulty INTEGER DEFAULT 1 CHECK (difficulty BETWEEN 1 AND 5),

    -- Meta
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT chk_task_type CHECK (task_type IN (
        'identify_pattern',      -- "Welches Muster ist das?"
        'order_steps',           -- "Bringe die Schritte in Reihenfolge"
        'fill_formula',          -- "Ergänze die Formel"
        'match_values',          -- "Ordne Werte zu"
        'spot_error',            -- "Finde den Fehler"
        'complete_calculation'   -- "Vervollständige die Rechnung"
    ))
);

CREATE INDEX IF NOT EXISTS idx_pattern_tasks_pattern ON learning_methods.math_pattern_recognition_tasks (pattern_id);
CREATE INDEX IF NOT EXISTS idx_pattern_tasks_type ON learning_methods.math_pattern_recognition_tasks (task_type);
CREATE INDEX IF NOT EXISTS idx_pattern_tasks_difficulty ON learning_methods.math_pattern_recognition_tasks (difficulty);

COMMENT ON TABLE learning_methods.math_pattern_recognition_tasks IS
'Muster-Erkennungs-Aufgaben. task_data und solution sind dynamisch per JSONB.';

-- ============================================================================
-- 9. math_scaffolding_hints - Dynamische Hilfe-Texte
-- ============================================================================

CREATE TABLE IF NOT EXISTS learning_methods.math_scaffolding_hints (
    hint_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pattern_id UUID REFERENCES learning_methods.math_patterns(pattern_id) ON DELETE CASCADE,

    -- Hint-Kontext
    hint_type VARCHAR(30) NOT NULL,
    step_number INTEGER,
    error_type VARCHAR(50),

    -- Hint-Inhalt (nach Level)
    hint_level_1 TEXT NOT NULL,  -- Volle Erklärung
    hint_level_2 TEXT,           -- Kurzer Hinweis
    hint_level_3 TEXT,           -- Nur "Denk nochmal nach"

    -- Wann zeigen
    trigger_condition JSONB DEFAULT '{}',

    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT chk_hint_type CHECK (hint_type IN (
        'step_intro',      -- Einführung für einen Schritt
        'step_help',       -- Hilfe während des Schritts
        'error_feedback',  -- Feedback bei Fehler
        'success_praise',  -- Lob bei Erfolg
        'pattern_tip',     -- Allgemeiner Tipp zum Muster
        'calculator_tip'   -- Taschenrechner-Tipp
    ))
);

CREATE INDEX IF NOT EXISTS idx_scaffolding_pattern ON learning_methods.math_scaffolding_hints (pattern_id);
CREATE INDEX IF NOT EXISTS idx_scaffolding_type ON learning_methods.math_scaffolding_hints (hint_type);

COMMENT ON TABLE learning_methods.math_scaffolding_hints IS
'Dynamische Hilfe-Texte für verschiedene Scaffolding-Level.';

-- ============================================================================
-- 9b. Standard Math Patterns (IHK-relevant, Handelskalkulation)
-- ============================================================================

-- Bezugskalkulation Pattern
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

-- Prozentrechnung Grundwert
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

-- Prozentrechnung Prozentwert
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

-- Dreisatz
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
-- 12. Trigger für updated_at
-- ============================================================================

CREATE TRIGGER update_math_pattern_categories_updated_at
    BEFORE UPDATE ON learning_methods.math_pattern_categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_math_patterns_updated_at
    BEFORE UPDATE ON learning_methods.math_patterns
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_math_user_progress_updated_at
    BEFORE UPDATE ON learning_methods.math_user_progress
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- NOTE: system_feature_types wird via Frontend konfiguriert (math_toolkit Feature)
-- ============================================================================

-- ============================================================================
-- Migration 070 abgeschlossen
-- ============================================================================
