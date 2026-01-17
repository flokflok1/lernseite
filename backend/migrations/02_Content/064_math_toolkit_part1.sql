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
