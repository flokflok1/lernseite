-- ============================================================================
-- Migration 070: Prompt Templates System
-- ============================================================================
-- Description: Database tables for editable prompt templates
--              Allows admins to customize AI prompts for content generation
--              Supports multiple styles: ADHS, Kurz, Ausfuehrlich, Pruefungsfokus
--
-- Phase: KI-Studio Enhancement
-- Date: 2025-01
-- ============================================================================

-- ============================================================================
-- 1. Prompt Templates Table
-- ============================================================================
-- Stores customizable prompt templates for AI content generation

CREATE TABLE IF NOT EXISTS prompt_templates (
    template_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Template identification
    code VARCHAR(100) NOT NULL,              -- Unique code: 'theory_sheet_adhs', 'lesson_steps_short'
    category VARCHAR(50) NOT NULL,           -- 'theory', 'lesson', 'quiz', 'flashcard', 'tutor'
    style VARCHAR(50) NOT NULL DEFAULT 'standard',  -- 'standard', 'adhs', 'short', 'detailed', 'exam_focus'

    -- Display info
    title VARCHAR(255) NOT NULL,             -- "Theorieblatt (ADHS-freundlich)"
    description TEXT,                        -- "Kurze, visuelle Erklaerungen mit Schritt-fuer-Schritt Anleitungen"
    icon VARCHAR(50),                        -- Emoji or icon code

    -- The actual prompt
    system_prompt TEXT NOT NULL,             -- System message for AI
    user_prompt_template TEXT NOT NULL,      -- User message template with {{variables}}

    -- AI Configuration
    model VARCHAR(100) DEFAULT 'gpt-4o-mini',
    provider VARCHAR(50) DEFAULT 'openai',
    temperature DECIMAL(3,2) DEFAULT 0.7,
    max_tokens INTEGER DEFAULT 4000,

    -- Variables definition (JSON)
    -- Example: [{"name": "chapter_title", "required": true, "description": "Kapiteltitel"}]
    variables JSONB DEFAULT '[]'::jsonb,

    -- Output format
    output_format VARCHAR(50) DEFAULT 'json',  -- 'json', 'markdown', 'html', 'text'
    output_schema JSONB,                        -- Expected JSON schema for validation

    -- TTS Settings
    tts_enabled BOOLEAN DEFAULT false,
    tts_voice VARCHAR(50) DEFAULT 'alloy',     -- OpenAI voice: alloy, echo, fable, onyx, nova, shimmer
    tts_model VARCHAR(50) DEFAULT 'tts-1',     -- tts-1 or tts-1-hd
    tts_speed DECIMAL(3,2) DEFAULT 1.0,        -- 0.25 to 4.0

    -- Metadata
    language VARCHAR(10) DEFAULT 'de',
    target_audience VARCHAR(255),              -- "Fachinformatiker Systemintegration"
    difficulty_level VARCHAR(50),              -- "beginner", "intermediate", "advanced", "exam"

    -- Learning method association (optional)
    lm_type INTEGER,                           -- 0-32 (LM00-LM32), NULL for general templates

    -- Status
    is_active BOOLEAN DEFAULT true,
    is_default BOOLEAN DEFAULT false,          -- Default template for this category+style
    is_system BOOLEAN DEFAULT false,           -- System template (cannot be deleted)

    -- Versioning
    version INTEGER DEFAULT 1,
    parent_template_id UUID REFERENCES prompt_templates(template_id),  -- For version history

    -- Audit
    created_by UUID REFERENCES users(user_id),
    updated_by UUID REFERENCES users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    CONSTRAINT unique_template_code UNIQUE (code),
    CONSTRAINT valid_temperature CHECK (temperature >= 0 AND temperature <= 2),
    CONSTRAINT valid_tts_speed CHECK (tts_speed >= 0.25 AND tts_speed <= 4.0),
    CONSTRAINT valid_lm_type CHECK (lm_type IS NULL OR (lm_type >= 0 AND lm_type <= 32))
);

-- Indexes
CREATE INDEX idx_prompt_templates_category ON prompt_templates(category);
CREATE INDEX idx_prompt_templates_style ON prompt_templates(style);
CREATE INDEX idx_prompt_templates_category_style ON prompt_templates(category, style);
CREATE INDEX idx_prompt_templates_lm_type ON prompt_templates(lm_type) WHERE lm_type IS NOT NULL;
CREATE INDEX idx_prompt_templates_active ON prompt_templates(is_active) WHERE is_active = true;
CREATE INDEX idx_prompt_templates_default ON prompt_templates(category, style, is_default) WHERE is_default = true;

-- ============================================================================
-- 2. Prompt Template Usage Tracking
-- ============================================================================
-- Tracks usage statistics for each template

CREATE TABLE IF NOT EXISTS prompt_template_usage (
    usage_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES prompt_templates(template_id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(user_id),

    -- What was generated
    content_type VARCHAR(50) NOT NULL,         -- 'chapter_theory', 'lesson_steps', 'quiz'
    content_id UUID,                            -- Reference to generated content

    -- AI Response metrics
    tokens_input INTEGER,
    tokens_output INTEGER,
    tokens_total INTEGER,
    cost_eur DECIMAL(10,6),
    response_time_ms INTEGER,

    -- TTS metrics (if generated)
    tts_generated BOOLEAN DEFAULT false,
    tts_duration_seconds DECIMAL(10,2),
    tts_cost_eur DECIMAL(10,6),
    tts_audio_url TEXT,

    -- Quality feedback
    user_rating INTEGER CHECK (user_rating >= 1 AND user_rating <= 5),
    user_feedback TEXT,

    -- Context
    context_data JSONB,                        -- Variables used

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_prompt_usage_template ON prompt_template_usage(template_id);
CREATE INDEX idx_prompt_usage_user ON prompt_template_usage(user_id);
CREATE INDEX idx_prompt_usage_created ON prompt_template_usage(created_at);

-- ============================================================================
-- 3. Insert Default Prompt Templates
-- ============================================================================

-- Theory Sheet Templates (verschiedene Stile)
INSERT INTO prompt_templates (
    code, category, style, title, description, icon,
    system_prompt, user_prompt_template,
    variables, output_format, output_schema,
    tts_enabled, target_audience, is_default, is_system
) VALUES
-- ADHS-freundlich (Default)
(
    'theory_sheet_adhs',
    'theory',
    'adhs',
    'Theorieblatt (ADHS-freundlich)',
    'Kurze, visuelle Erklaerungen mit klarer Struktur. Ideal fuer schnelles Erfassen.',
    '🧠',
    'Du bist ein erfahrener IT-Ausbilder, spezialisiert auf ADHS-freundliches Lernen.
Deine Erklaerungen sind:
- KURZ und praegnant (max. 2-3 Saetze pro Punkt)
- VISUELL strukturiert mit Aufzaehlungen und Emojis
- SCHRITTWEISE aufgebaut
- Mit KONKRETEN Beispielen
- Ohne Fachjargon (oder sofort erklaert)

Antworte NUR mit validem JSON.',
    'Erstelle ein ADHS-freundliches Theorieblatt fuer das Kapitel "{{chapter_title}}" im Kurs "{{course_title}}".

Kapitel-Beschreibung: {{chapter_description}}
Lektionen: {{lesson_titles}}
Zielgruppe: {{target_audience}}

JSON-Struktur:
{
    "overview": "Kurze Uebersicht (2-3 Saetze, was lernst du hier?)",
    "learningGoals": ["Ziel 1 (kurz!)", "Ziel 2", ...],
    "concepts": [
        {
            "title": "Konzept-Name",
            "emoji": "passendes Emoji",
            "oneLiner": "Erklaerung in EINEM Satz",
            "example": "Konkretes Beispiel",
            "tip": "Merkhilfe oder Eselsbruecke"
        }
    ],
    "terms": [
        {
            "term": "Fachbegriff",
            "simple": "Einfache Erklaerung (wie fuer 10-Jaehrigen)",
            "example": "Beispiel aus dem Alltag"
        }
    ],
    "examTips": ["Pruefungstipp 1", "Pruefungstipp 2"],
    "summary": "3 Bullet Points: Das Wichtigste auf einen Blick"
}',
    '[
        {"name": "chapter_title", "required": true, "description": "Titel des Kapitels"},
        {"name": "course_title", "required": true, "description": "Titel des Kurses"},
        {"name": "chapter_description", "required": false, "description": "Beschreibung des Kapitels"},
        {"name": "lesson_titles", "required": false, "description": "Titel der Lektionen"},
        {"name": "target_audience", "required": false, "default": "Fachinformatiker Systemintegration"}
    ]'::jsonb,
    'json',
    '{
        "type": "object",
        "required": ["overview", "learningGoals", "concepts", "terms", "examTips", "summary"],
        "properties": {
            "overview": {"type": "string"},
            "learningGoals": {"type": "array", "items": {"type": "string"}},
            "concepts": {"type": "array"},
            "terms": {"type": "array"},
            "examTips": {"type": "array", "items": {"type": "string"}},
            "summary": {"type": "string"}
        }
    }'::jsonb,
    true,
    'Fachinformatiker Systemintegration (FISI)',
    true,
    true
),

-- Ausfuehrlich
(
    'theory_sheet_detailed',
    'theory',
    'detailed',
    'Theorieblatt (Ausfuehrlich)',
    'Umfassende Erklaerungen mit allen Details. Ideal zum tiefen Verstaendnis.',
    '📚',
    'Du bist ein erfahrener IT-Ausbilder mit akademischem Hintergrund.
Erstelle ausfuehrliche, gut strukturierte Lerninhalte mit:
- Vollstaendigen Erklaerungen aller Konzepte
- Hintergrundwissen und Zusammenhaengen
- Mehreren Beispielen pro Konzept
- Formeln und Berechnungswegen (wo relevant)
- Verweisen auf weitere Themen

Antworte NUR mit validem JSON.',
    'Erstelle ein ausfuehrliches Theorieblatt fuer das Kapitel "{{chapter_title}}" im Kurs "{{course_title}}".

Kapitel-Beschreibung: {{chapter_description}}
Lektionen: {{lesson_titles}}
Zielgruppe: {{target_audience}}

JSON-Struktur:
{
    "overview": "Ausfuehrliche Uebersicht mit Einordnung ins Gesamtthema",
    "learningGoals": ["Detailliertes Lernziel 1", "Lernziel 2", ...],
    "prerequisites": ["Vorwissen 1", "Vorwissen 2"],
    "concepts": [
        {
            "title": "Konzept-Name",
            "description": "Ausfuehrliche Erklaerung (mehrere Saetze)",
            "background": "Hintergrund und Kontext",
            "formula": "Formel falls relevant",
            "examples": ["Beispiel 1", "Beispiel 2"],
            "commonMistakes": ["Haeufiger Fehler 1"],
            "relatedTopics": ["Verwandtes Thema 1"]
        }
    ],
    "terms": [
        {
            "term": "Fachbegriff",
            "definition": "Vollstaendige Definition",
            "etymology": "Wortherkunft (optional)",
            "usage": "Verwendung im Kontext"
        }
    ],
    "examRelevance": "Detaillierte Erklaerung zur Pruefungsrelevanz mit typischen Aufgabentypen",
    "furtherReading": ["Weiterführende Ressource 1"],
    "summary": "Zusammenfassung aller wichtigen Punkte"
}',
    '[
        {"name": "chapter_title", "required": true, "description": "Titel des Kapitels"},
        {"name": "course_title", "required": true, "description": "Titel des Kurses"},
        {"name": "chapter_description", "required": false, "description": "Beschreibung des Kapitels"},
        {"name": "lesson_titles", "required": false, "description": "Titel der Lektionen"},
        {"name": "target_audience", "required": false, "default": "Fachinformatiker Systemintegration"}
    ]'::jsonb,
    'json',
    NULL,
    true,
    'Fachinformatiker Systemintegration (FISI)',
    false,
    true
),

-- Kurz & Knapp
(
    'theory_sheet_short',
    'theory',
    'short',
    'Theorieblatt (Kurz & Knapp)',
    'Nur das Wichtigste auf einen Blick. Ideal zur Wiederholung.',
    '⚡',
    'Du bist ein IT-Ausbilder, der auf Effizienz setzt.
Erstelle extrem kompakte Zusammenfassungen:
- Maximal 5 Kernpunkte
- Jeder Punkt in einem Satz
- Nur pruefungsrelevante Inhalte
- Keine Beispiele, nur Fakten

Antworte NUR mit validem JSON.',
    'Erstelle eine Kurzuebersicht fuer das Kapitel "{{chapter_title}}".

JSON-Struktur:
{
    "title": "Kapiteltitel",
    "keyPoints": ["Kernpunkt 1", "Kernpunkt 2", "Kernpunkt 3", "Kernpunkt 4", "Kernpunkt 5"],
    "mustKnowTerms": [{"term": "Begriff", "definition": "Ein-Satz-Definition"}],
    "examFormula": "Wichtigste Formel (falls relevant)",
    "oneMinuteSummary": "Das Kapitel in 60 Sekunden erklaert"
}',
    '[
        {"name": "chapter_title", "required": true, "description": "Titel des Kapitels"}
    ]'::jsonb,
    'json',
    NULL,
    true,
    'Fachinformatiker Systemintegration (FISI)',
    false,
    true
),

-- Pruefungsfokus
(
    'theory_sheet_exam',
    'theory',
    'exam_focus',
    'Theorieblatt (Pruefungsfokus)',
    'Optimiert fuer IHK-Pruefungsvorbereitung. Was kommt dran?',
    '🎯',
    'Du bist ein IHK-Pruefer und kennst die AP1-Pruefung genau.
Erstelle Lerninhalte mit klarem Pruefungsfokus:
- Was wird WIRKLICH geprueft?
- Typische Aufgabenstellungen
- Punkteverteilung beachten
- Haeufige Fehler vermeiden
- Zeitmanagement-Tipps

Antworte NUR mit validem JSON.',
    'Erstelle ein pruefungsfokussiertes Theorieblatt fuer "{{chapter_title}}".

JSON-Struktur:
{
    "examRelevance": "HOCH/MITTEL/NIEDRIG",
    "typicalPoints": "Wie viele Punkte gibt es typischerweise?",
    "mustKnow": ["Das MUSS sitzen 1", "Das MUSS sitzen 2"],
    "typicalTasks": [
        {
            "type": "Aufgabentyp (z.B. Berechnung, Erklaerung)",
            "example": "Beispielaufgabe",
            "solution": "Loesungsweg",
            "points": "Typische Punktzahl",
            "timeMinutes": "Empfohlene Zeit"
        }
    ],
    "commonMistakes": [
        {
            "mistake": "Haeufiger Fehler",
            "consequence": "Punktabzug",
            "howToAvoid": "So vermeidest du ihn"
        }
    ],
    "examTips": ["Pruefungstipp 1", "Pruefungstipp 2"],
    "lastMinuteChecklist": ["Vor der Pruefung checken 1", "Checken 2"]
}',
    '[
        {"name": "chapter_title", "required": true, "description": "Titel des Kapitels"}
    ]'::jsonb,
    'json',
    NULL,
    true,
    'Fachinformatiker Systemintegration (FISI) - IHK AP1',
    false,
    true
);

-- Lesson Steps Templates
INSERT INTO prompt_templates (
    code, category, style, title, description, icon,
    system_prompt, user_prompt_template,
    variables, output_format,
    tts_enabled, target_audience, is_default, is_system
) VALUES
(
    'lesson_steps_adhs',
    'lesson',
    'adhs',
    'Lektions-Erklaerung (ADHS-freundlich)',
    'Schritt-fuer-Schritt mit Taschenrechner-Anleitung',
    '🧮',
    'Du bist ein geduldiger Tutor, der komplexe Themen in kleine Haeppchen zerlegt.
Jeder Schritt muss:
- In 1-2 Saetzen erklaert sein
- Eine klare Aktion haben
- Visuelles Feedback geben (Schema/Formel)

Antworte NUR mit validem JSON.',
    'Erstelle eine Schritt-fuer-Schritt Erklaerung fuer die Lektion "{{lesson_title}}" (Lernmethode: {{lm_type}}).

JSON-Struktur:
{
    "steps": [
        {
            "stepNumber": 1,
            "title": "Kurzer Titel",
            "speech": "Was der Tutor sagt (freundlich, motivierend)",
            "action": "Was der User tun soll",
            "calculator": "Taschenrechner-Eingabe (z.B. 960 * 80.14)",
            "result": "Erwartetes Ergebnis",
            "schema": [
                {"label": "Zeile", "operator": "+/-/=", "value": "Wert", "highlight": false}
            ],
            "tip": "Hilfreicher Tipp (optional)"
        }
    ],
    "totalSteps": 5,
    "estimatedMinutes": 10
}',
    '[
        {"name": "lesson_title", "required": true, "description": "Titel der Lektion"},
        {"name": "lm_type", "required": false, "default": "LM00", "description": "Lernmethoden-Typ"}
    ]'::jsonb,
    'json',
    true,
    'Fachinformatiker Systemintegration (FISI)',
    true,
    true
);

-- ============================================================================
-- 4. Generated Content with TTS
-- ============================================================================
-- Stores generated content and associated TTS audio

CREATE TABLE IF NOT EXISTS generated_theory_sheets (
    sheet_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- References
    chapter_id UUID REFERENCES chapters(chapter_id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses(course_id) ON DELETE CASCADE,
    template_id UUID REFERENCES prompt_templates(template_id),

    -- Content
    style VARCHAR(50) NOT NULL,                -- Which style was used
    content JSONB NOT NULL,                    -- The generated JSON content
    content_html TEXT,                         -- Rendered HTML version
    content_markdown TEXT,                     -- Markdown version

    -- TTS Audio
    has_audio BOOLEAN DEFAULT false,
    audio_url TEXT,                            -- URL to audio file
    audio_duration_seconds DECIMAL(10,2),
    audio_voice VARCHAR(50),
    audio_generated_at TIMESTAMP WITH TIME ZONE,

    -- Generation info
    tokens_used INTEGER,
    cost_eur DECIMAL(10,6),
    generation_time_ms INTEGER,

    -- Status
    is_published BOOLEAN DEFAULT false,

    -- Audit
    created_by UUID REFERENCES users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_theory_sheets_chapter ON generated_theory_sheets(chapter_id);
CREATE INDEX idx_theory_sheets_course ON generated_theory_sheets(course_id);
CREATE INDEX idx_theory_sheets_style ON generated_theory_sheets(style);
CREATE INDEX idx_theory_sheets_has_audio ON generated_theory_sheets(has_audio) WHERE has_audio = true;

-- ============================================================================
-- 5. Update Trigger
-- ============================================================================

CREATE OR REPLACE FUNCTION update_prompt_templates_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_prompt_templates_updated
    BEFORE UPDATE ON prompt_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_prompt_templates_timestamp();

CREATE TRIGGER trigger_theory_sheets_updated
    BEFORE UPDATE ON generated_theory_sheets
    FOR EACH ROW
    EXECUTE FUNCTION update_prompt_templates_timestamp();

-- ============================================================================
-- Migration complete
-- ============================================================================
-- New tables: prompt_templates, prompt_template_usage, generated_theory_sheets
-- Default templates: 4 theory styles (ADHS, detailed, short, exam_focus)
--                   1 lesson steps style (ADHS)
