-- ============================================================================
-- Seed Data: Authoring Actions (Quick-Actions für KI-Studio)
-- Description: Standard authoring actions for course builder, content, lessons
-- Source: 066_authoring_actions.sql
-- Author: LernsystemX Migration System
-- Date: 2026-01-26
-- Phase: 4 (Seed Data)
-- ============================================================================

INSERT INTO learning_methods.authoring_actions (action_key, category, label, description, icon, prompt_template, mode, context_entity, action_type, output_format, is_system, order_index)
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
-- Verification
-- ============================================================================

SELECT COUNT(*) as total_authoring_actions FROM learning_methods.authoring_actions WHERE is_system = TRUE;
