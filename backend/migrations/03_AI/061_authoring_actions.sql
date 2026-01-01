-- ============================================================================
-- Migration 067: Authoring Actions System
-- ============================================================================
-- Description: Database tables for dynamic authoring actions (Quick-Actions)
--              Replaces hardcoded buttons in KI-Studio with DB-driven actions
--              Enables flexible, extensible action management for bots/agents
--
-- Phase: DB-Zentriertes KI-Authoring
-- Date: 2025-12
-- ============================================================================

-- ============================================================================
-- 1. Authoring Actions Table
-- ============================================================================
-- Stores Quick-Actions for KI-Studio (KursBuilder, Chat, Content, Tutor)

CREATE TABLE IF NOT EXISTS authoring_actions (
    action_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Action identification
    action_key VARCHAR(100) UNIQUE NOT NULL,   -- 'structure_suggest', 'explain', 'quiz_create'
    category VARCHAR(50) NOT NULL,              -- 'course_builder', 'content', 'tutor', 'chat', 'lesson', 'chapter', 'method'

    -- Display info
    label VARCHAR(255) NOT NULL,                -- "Struktur vorschlagen"
    description TEXT,                           -- "Analysiert das Kursmaterial und schlaegt eine Struktur vor"
    icon VARCHAR(50),                           -- Emoji or icon code
    color VARCHAR(50),                          -- Button color class or hex

    -- The actual prompt template
    prompt_template TEXT NOT NULL,              -- "Analysiere das Material und schlage eine Struktur vor..."

    -- Context requirements
    mode VARCHAR(50),                           -- 'structure', 'lesson', 'exam', 'quiz', 'explain', etc.
    requires_context JSONB DEFAULT '{}'::jsonb, -- {"course": true, "chapter": false, "lesson": false}
    context_entity VARCHAR(50),                 -- 'course', 'chapter', 'lesson', 'method' - what entity this action works on

    -- Variables for prompt interpolation
    -- Example: [{"name": "course_title", "required": true, "source": "context.course.title"}]
    variables JSONB DEFAULT '[]'::jsonb,

    -- Action behavior
    action_type VARCHAR(50) DEFAULT 'chat',     -- 'chat', 'generate', 'edit', 'delete', 'preview'
    requires_confirmation BOOLEAN DEFAULT false, -- Show preview before saving to DB
    confirmation_label VARCHAR(100),             -- "Kapitel erstellen?"

    -- AI Configuration (optional overrides)
    model VARCHAR(100),                          -- Override default model
    provider VARCHAR(50),                        -- Override default provider
    temperature DECIMAL(3,2),                    -- Override temperature
    max_tokens INTEGER,                          -- Override max tokens

    -- Output handling
    output_format VARCHAR(50) DEFAULT 'text',    -- 'text', 'json', 'markdown', 'html'
    output_entity VARCHAR(50),                   -- 'chapter', 'lesson', 'method', 'quiz' - what to create
    output_schema JSONB,                         -- Expected JSON schema for structured output

    -- Learning method association (optional)
    lm_types INTEGER[],                          -- [0, 1, 12] - specific LM types this applies to

    -- Visibility & access
    roles_allowed VARCHAR(100)[] DEFAULT ARRAY['admin', 'creator', 'teacher'],
    is_premium BOOLEAN DEFAULT false,

    -- Ordering & status
    order_index INT DEFAULT 0,
    is_system BOOLEAN DEFAULT false,             -- System actions cannot be deleted
    is_active BOOLEAN DEFAULT true,

    -- Audit
    created_by UUID REFERENCES users(user_id),
    updated_by UUID REFERENCES users(user_id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_authoring_actions_category ON authoring_actions(category);
CREATE INDEX idx_authoring_actions_mode ON authoring_actions(mode);
CREATE INDEX idx_authoring_actions_active ON authoring_actions(is_active) WHERE is_active = true;
CREATE INDEX idx_authoring_actions_context_entity ON authoring_actions(context_entity);
CREATE INDEX idx_authoring_actions_order ON authoring_actions(category, order_index);

-- ============================================================================
-- 2. Authoring Action Usage Tracking
-- ============================================================================
-- Tracks usage statistics for analytics and improvement

CREATE TABLE IF NOT EXISTS authoring_action_usage (
    usage_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action_id UUID NOT NULL REFERENCES authoring_actions(action_id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(user_id),
    session_id UUID,                             -- Reference to authoring session

    -- Context when action was used
    context_data JSONB,                          -- {"course_id": "...", "chapter_id": "..."}

    -- Result tracking
    was_successful BOOLEAN DEFAULT true,
    was_confirmed BOOLEAN,                       -- If requires_confirmation, did user confirm?
    result_entity_id UUID,                       -- ID of created/modified entity

    -- AI metrics
    tokens_input INTEGER,
    tokens_output INTEGER,
    tokens_total INTEGER,
    cost_eur DECIMAL(10,6),
    response_time_ms INTEGER,

    -- Feedback
    user_rating INTEGER CHECK (user_rating >= 1 AND user_rating <= 5),
    user_feedback TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_action_usage_action ON authoring_action_usage(action_id);
CREATE INDEX idx_action_usage_user ON authoring_action_usage(user_id);
CREATE INDEX idx_action_usage_session ON authoring_action_usage(session_id);
CREATE INDEX idx_action_usage_created ON authoring_action_usage(created_at);

-- ============================================================================
-- 3. Standard Authoring Actions (Quick-Actions für KI-Studio)
-- ============================================================================

INSERT INTO authoring_actions (action_key, category, label, description, icon, prompt_template, mode, context_entity, action_type, output_format, is_system, order_index)
VALUES
    -- Course Builder Actions
    ('structure_suggest', 'course_builder', 'Struktur vorschlagen', 'Analysiert das Kursmaterial und schlägt eine Kapitelstruktur vor', '📋',
     'Analysiere das folgende Kursmaterial und schlage eine sinnvolle Kapitelstruktur vor. Berücksichtige dabei die Lernziele und den logischen Aufbau.\n\nMaterial:\n{{source_content}}\n\nErstelle eine Struktur mit Kapiteln und Unterthemen.',
     'structure', 'course', 'generate', 'json', TRUE, 10),

    ('chapter_outline', 'course_builder', 'Kapitel-Gliederung', 'Erstellt eine detaillierte Gliederung für ein Kapitel', '📝',
     'Erstelle eine detaillierte Gliederung für das Kapitel "{{chapter_title}}" im Kurs "{{course_title}}".\n\nBerücksichtige:\n- Lernziele\n- Theorie-Abschnitte\n- Praktische Übungen\n- Prüfungsvorbereitung',
     'outline', 'chapter', 'generate', 'json', TRUE, 20),

    -- Content Actions
    ('theory_generate', 'content', 'Theorie generieren', 'Generiert Theorie-Inhalte für ein Kapitel', '📚',
     'Erstelle Theorie-Inhalte für das Kapitel "{{chapter_title}}".\n\nThema: {{topic}}\n\nStrukturiere den Inhalt mit:\n- Einleitung\n- Hauptteil mit Erklärungen\n- Beispiele\n- Zusammenfassung',
     'theory', 'chapter', 'generate', 'markdown', TRUE, 30),

    ('explain_concept', 'content', 'Begriff erklären', 'Erklärt einen Fachbegriff ausführlich', '💡',
     'Erkläre den Begriff "{{term}}" im Kontext von {{context}}.\n\nBerücksichtige:\n- Definition\n- Beispiele\n- Praktische Anwendung\n- Häufige Missverständnisse',
     'explain', NULL, 'chat', 'markdown', TRUE, 40),

    -- Lesson Actions
    ('lesson_create', 'lesson', 'Lektion erstellen', 'Erstellt eine vollständige Lektion mit Lernmethoden', '📖',
     'Erstelle eine Lektion zum Thema "{{lesson_topic}}" für das Kapitel "{{chapter_title}}".\n\nDie Lektion soll enthalten:\n- Lernziele\n- Theorie-Einführung\n- Passende Lernmethoden\n- Übungsaufgaben',
     'lesson', 'lesson', 'generate', 'json', TRUE, 50),

    ('quiz_generate', 'lesson', 'Quiz generieren', 'Erstellt Quiz-Fragen basierend auf dem Lektionsinhalt', '❓',
     'Erstelle 5-10 Quiz-Fragen zum Thema "{{lesson_topic}}".\n\nFragetypen:\n- Multiple Choice\n- Single Choice\n- Wahr/Falsch\n- Lückentext\n\nSchwierigkeit: {{difficulty}}',
     'quiz', 'lesson', 'generate', 'json', TRUE, 60),

    -- Method Actions
    ('method_suggest', 'method', 'Lernmethoden vorschlagen', 'Schlägt passende Lernmethoden für ein Thema vor', '🎯',
     'Schlage passende Lernmethoden für das Thema "{{topic}}" vor.\n\nVerfügbare Methoden: Tiefgehende Erklärung, Schritt-für-Schritt, Flashcards, Quiz, Drag&Drop, Whiteboard\n\nBerücksichtige das Lernziel: {{learning_goal}}',
     'method', 'lesson', 'chat', 'json', TRUE, 70),

    ('flashcards_create', 'method', 'Flashcards erstellen', 'Generiert Flashcards für Vokabeln oder Begriffe', '🃏',
     'Erstelle Flashcards für das Thema "{{topic}}".\n\nFormat:\n- Vorderseite: Begriff/Frage\n- Rückseite: Definition/Antwort\n\nAnzahl: {{count}} Karten',
     'flashcards', 'lesson', 'generate', 'json', TRUE, 80),

    -- Chat Actions
    ('improve_text', 'chat', 'Text verbessern', 'Verbessert und optimiert einen Text', '✨',
     'Verbessere den folgenden Text:\n\n{{text}}\n\nOptimiere:\n- Klarheit\n- Struktur\n- Fachliche Korrektheit\n- Lesbarkeit',
     NULL, NULL, 'chat', 'text', TRUE, 90),

    ('summarize', 'chat', 'Zusammenfassen', 'Erstellt eine Zusammenfassung', '📋',
     'Fasse den folgenden Inhalt zusammen:\n\n{{content}}\n\nLänge: {{length}} (kurz/mittel/ausführlich)',
     NULL, NULL, 'chat', 'text', TRUE, 100),

    -- Exam Actions
    ('exam_questions', 'lesson', 'Prüfungsfragen erstellen', 'Generiert IHK-konforme Prüfungsfragen', '📝',
     'Erstelle IHK-konforme Prüfungsfragen zum Thema "{{topic}}".\n\nAnforderungen:\n- Situationsbezogene Aufgaben\n- Handlungsorientiert\n- Verschiedene Schwierigkeitsgrade\n\nAnzahl: {{count}} Fragen',
     'exam', 'lesson', 'generate', 'json', TRUE, 110)

ON CONFLICT (action_key) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    icon = EXCLUDED.icon,
    prompt_template = EXCLUDED.prompt_template,
    mode = EXCLUDED.mode,
    context_entity = EXCLUDED.context_entity,
    action_type = EXCLUDED.action_type,
    output_format = EXCLUDED.output_format,
    order_index = EXCLUDED.order_index,
    updated_at = NOW();

-- ============================================================================
-- 4. Update Trigger
-- ============================================================================

CREATE OR REPLACE FUNCTION update_authoring_actions_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_authoring_actions_updated
    BEFORE UPDATE ON authoring_actions
    FOR EACH ROW
    EXECUTE FUNCTION update_authoring_actions_timestamp();


-- ============================================================================
-- Migration complete
-- ============================================================================
-- New tables: authoring_actions, authoring_action_usage
-- All data configured via Frontend/API
