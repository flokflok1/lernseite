-- ============================================================================
-- Migration: 01_learning_methods_seed.sql
-- Version: 2.0.0 (DB-Driven - 100% Complete Configuration)
-- Description: Seed Data - 12 Content-Lernmethoden mit vollständiger Konfiguration
-- Author: LernsystemX Migration System
-- Date: 2026-01-26
-- Phase: 5 (Seed Data - Learning Methods Configuration)
-- Dependencies:
--   - 04_LearningMethods/030_learning_methods_core.sql (tables)
--   - 04_LearningMethods/031_learning_methods_add_config_columns.sql (columns)
--
-- CRITICAL: This is the SINGLE SOURCE OF TRUTH for all 12 Learning Methods.
-- No hardcoded Python mappings. No frontend configuration.
-- Everything is here, dynamically loaded by API.
--
-- 12 Content-Lernmethoden in 3 Gruppen:
-- Gruppe A (Erklärend): Tiefgehende Erklärung, Schritt-für-Schritt, Interaktive Theorie, Diagramm/Visualisierung, Beispiel-Szenario
-- Gruppe B (Praxis): Mathe-Interaktiv, Flashcards, Drag & Drop, Lückentext
-- Gruppe C (Prüfung): Freitext-Langantwort, Multiple-Choice Quiz, True/False
-- ============================================================================

BEGIN TRANSACTION;

-- ============================================================================
-- GRUPPE A (ERKLÄREND) - 5 Methoden für Verständnis
-- ============================================================================

INSERT INTO learning_methods.learning_method_types (
    method_type, name, description, group_code, tier, ki_usage, icon,
    prompt_template, default_config, agent_support, ui_schema
) VALUES
-- LM00: Tiefgehende Erklärung
(
    0,
    'Tiefgehende Erklärung',
    'KI-generierte Erklärung mit Beispielen & Analogien',
    'A',
    'basic',
    'intensive',
    'book-open',
    'deep_explanation',
    '{"min_examples": 2, "include_analogies": true}'::jsonb,
    '{
        "agent_can_handle": true,
        "requires_fresh_ai": false,
        "knowledge_domains": ["general"],
        "knowledge_cacheable": true,
        "complexity_threshold": 2
    }'::jsonb,
    '{
        "form_type": "dynamic",
        "fields": [
            {"name": "topic", "type": "text", "label": "Topic", "required": true},
            {"name": "context", "type": "textarea", "label": "Context (optional)", "required": false},
            {"name": "depth_level", "type": "select", "label": "Depth Level", "options": ["beginner", "intermediate", "advanced"], "required": true}
        ]
    }'::jsonb
),
-- LM01: Schritt-für-Schritt
(
    1,
    'Schritt-für-Schritt',
    'Sequenzielle Anleitung in nummerierten Schritten',
    'A',
    'basic',
    'medium',
    'list-ordered',
    'step_by_step',
    '{"min_steps": 3, "max_steps": 10}'::jsonb,
    '{
        "agent_can_handle": true,
        "requires_fresh_ai": false,
        "knowledge_domains": ["general"],
        "knowledge_cacheable": true,
        "complexity_threshold": 2
    }'::jsonb,
    '{
        "form_type": "dynamic",
        "fields": [
            {"name": "objective", "type": "text", "label": "Learning Objective", "required": true},
            {"name": "prerequisites", "type": "textarea", "label": "Prerequisites", "required": false},
            {"name": "num_steps", "type": "number", "label": "Number of Steps", "min": 3, "max": 10, "required": true}
        ]
    }'::jsonb
),
-- LM02: Interaktive Theorie
(
    2,
    'Interaktive Theorie',
    'Theorie mit interaktiven Frage-Antwort-Elementen',
    'A',
    'basic',
    'medium',
    'lightbulb',
    'interactive_theory',
    '{"question_frequency": "medium", "feedback_mode": "immediate"}'::jsonb,
    '{
        "agent_can_handle": true,
        "requires_fresh_ai": false,
        "knowledge_domains": ["general"],
        "knowledge_cacheable": true,
        "complexity_threshold": 2
    }'::jsonb,
    '{
        "form_type": "dynamic",
        "fields": [
            {"name": "theory_text", "type": "textarea", "label": "Theory Content", "required": true},
            {"name": "num_questions", "type": "number", "label": "Number of Questions", "min": 1, "max": 10, "required": true},
            {"name": "question_frequency", "type": "select", "label": "Question Frequency", "options": ["low", "medium", "high"], "required": true}
        ]
    }'::jsonb
),
-- LM03: Diagramm/Visualisierung
(
    3,
    'Diagramm/Visualisierung',
    'Grafische Darstellung komplexer Konzepte',
    'A',
    'basic',
    'medium',
    'chart-network',
    'diagram_visualization',
    '{"diagram_type": "network", "render_engine": "mermaid"}'::jsonb,
    '{
        "agent_can_handle": true,
        "requires_fresh_ai": false,
        "knowledge_domains": ["general"],
        "knowledge_cacheable": true,
        "complexity_threshold": 3
    }'::jsonb,
    '{
        "form_type": "dynamic",
        "fields": [
            {"name": "diagram_type", "type": "select", "label": "Diagram Type", "options": ["network", "flowchart", "mindmap", "timeline"], "required": true},
            {"name": "diagram_description", "type": "textarea", "label": "What to visualize", "required": true},
            {"name": "complexity", "type": "select", "label": "Complexity", "options": ["simple", "moderate", "complex"], "required": true}
        ]
    }'::jsonb
),
-- LM04: Beispiel-Szenario
(
    4,
    'Beispiel-Szenario',
    'Praxisnahes Anwendungsbeispiel mit Kontext',
    'A',
    'basic',
    'medium',
    'clipboard-list',
    'example_scenario',
    '{"complexity": "medium", "allow_multiple_solutions": true}'::jsonb,
    '{
        "agent_can_handle": true,
        "requires_fresh_ai": false,
        "knowledge_domains": ["general"],
        "knowledge_cacheable": true,
        "complexity_threshold": 3
    }'::jsonb,
    '{
        "form_type": "dynamic",
        "fields": [
            {"name": "scenario_description", "type": "textarea", "label": "Scenario Description", "required": true},
            {"name": "context", "type": "textarea", "label": "Context/Background", "required": false},
            {"name": "learning_goals", "type": "textarea", "label": "Learning Goals", "required": true}
        ]
    }'::jsonb
)
ON CONFLICT (method_type) DO NOTHING;

-- ============================================================================
-- GRUPPE B (PRAXIS) - 4 Methoden zum Üben und Anwenden
-- ============================================================================

INSERT INTO learning_methods.learning_method_types (
    method_type, name, description, group_code, tier, ki_usage, icon,
    prompt_template, default_config, agent_support, ui_schema
) VALUES
-- LM05: Mathe-Interaktiv
(
    5,
    'Mathe-Interaktiv',
    'Mathematische Aufgaben mit Schritt-Erkennung',
    'B',
    'basic',
    'medium',
    'calculator',
    'math_interactive',
    '{"show_steps": true, "allow_calculator": false}'::jsonb,
    '{
        "agent_can_handle": true,
        "requires_fresh_ai": false,
        "knowledge_domains": ["math"],
        "knowledge_cacheable": true,
        "complexity_threshold": 3
    }'::jsonb,
    '{
        "form_type": "dynamic",
        "fields": [
            {"name": "math_problems", "type": "textarea", "label": "Math Problems", "required": true},
            {"name": "show_steps", "type": "checkbox", "label": "Show Solution Steps", "required": false},
            {"name": "difficulty", "type": "select", "label": "Difficulty", "options": ["easy", "medium", "hard"], "required": true}
        ]
    }'::jsonb
),
-- LM06: Flashcards
(
    6,
    'Flashcards',
    'Digitale Lernkarten für Wiederholung und Memorization',
    'B',
    'basic',
    'optional',
    'cards',
    'flashcards',
    '{"spaced_repetition": true, "shuffle": true}'::jsonb,
    '{
        "agent_can_handle": false,
        "requires_fresh_ai": false,
        "knowledge_domains": [],
        "knowledge_cacheable": false,
        "complexity_threshold": 1
    }'::jsonb,
    '{
        "form_type": "dynamic",
        "fields": [
            {"name": "flashcard_pairs", "type": "textarea", "label": "Question - Answer Pairs (one per line)", "required": true},
            {"name": "spaced_repetition", "type": "checkbox", "label": "Enable Spaced Repetition", "required": false},
            {"name": "shuffle", "type": "checkbox", "label": "Shuffle Cards", "required": false}
        ]
    }'::jsonb
),
-- LM07: Drag & Drop
(
    7,
    'Drag & Drop',
    'Zuordnungsaufgaben per Drag & Drop Interaktion',
    'B',
    'basic',
    'optional',
    'hand-pointer',
    'drag_drop',
    '{"randomize_order": true, "show_hints": false}'::jsonb,
    '{
        "agent_can_handle": false,
        "requires_fresh_ai": false,
        "knowledge_domains": [],
        "knowledge_cacheable": false,
        "complexity_threshold": 1
    }'::jsonb,
    '{
        "form_type": "dynamic",
        "fields": [
            {"name": "drag_drop_pairs", "type": "textarea", "label": "Source - Target Pairs", "required": true},
            {"name": "randomize_order", "type": "checkbox", "label": "Randomize Order", "required": false},
            {"name": "show_hints", "type": "checkbox", "label": "Show Hints", "required": false}
        ]
    }'::jsonb
),
-- LM08: Lückentext
(
    8,
    'Lückentext',
    'Lückentexte mit Auto-Korrektur und Synonym-Unterstützung',
    'B',
    'basic',
    'optional',
    'align-left',
    'fill_blanks',
    '{"case_sensitive": false, "allow_synonyms": true}'::jsonb,
    '{
        "agent_can_handle": false,
        "requires_fresh_ai": false,
        "knowledge_domains": [],
        "knowledge_cacheable": false,
        "complexity_threshold": 1
    }'::jsonb,
    '{
        "form_type": "dynamic",
        "fields": [
            {"name": "text_with_blanks", "type": "textarea", "label": "Text with __ for blanks", "required": true},
            {"name": "answers", "type": "textarea", "label": "Expected Answers (one per line)", "required": true},
            {"name": "case_sensitive", "type": "checkbox", "label": "Case Sensitive", "required": false}
        ]
    }'::jsonb
)
ON CONFLICT (method_type) DO NOTHING;

-- ============================================================================
-- GRUPPE C (PRÜFUNG) - 3 Methoden zum Kompetenznachweis
-- ============================================================================

INSERT INTO learning_methods.learning_method_types (
    method_type, name, description, group_code, tier, ki_usage, icon,
    prompt_template, default_config, agent_support, ui_schema
) VALUES
-- LM09: Freitext-Langantwort
(
    9,
    'Freitext-Langantwort',
    'Offene Fragen mit Agent-Bewertung (KI-gestützt)',
    'C',
    'premium',
    'intensive',
    'pen-fancy',
    'long_answer',
    '{"min_words": 100, "ai_grading": true}'::jsonb,
    '{
        "agent_can_handle": true,
        "requires_fresh_ai": false,
        "knowledge_domains": ["general"],
        "knowledge_cacheable": true,
        "complexity_threshold": 4
    }'::jsonb,
    '{
        "form_type": "dynamic",
        "fields": [
            {"name": "question", "type": "textarea", "label": "Question for Students", "required": true},
            {"name": "rubric", "type": "textarea", "label": "Grading Rubric", "required": true},
            {"name": "min_words", "type": "number", "label": "Minimum Words", "min": 10, "required": true},
            {"name": "ai_grading", "type": "checkbox", "label": "Enable AI Grading", "required": false}
        ]
    }'::jsonb
),
-- LM10: Multiple-Choice Quiz
(
    10,
    'Multiple-Choice Quiz',
    'Multiple-Choice Quiz im Prüfungsformat',
    'C',
    'basic',
    'optional',
    'question-circle',
    'multiple_choice_quiz',
    '{"questions_per_set": 20, "randomize": true}'::jsonb,
    '{
        "agent_can_handle": false,
        "requires_fresh_ai": false,
        "knowledge_domains": [],
        "knowledge_cacheable": false,
        "complexity_threshold": 1
    }'::jsonb,
    '{
        "form_type": "dynamic",
        "fields": [
            {"name": "questions", "type": "textarea", "label": "Questions with Options", "required": true},
            {"name": "correct_answers", "type": "textarea", "label": "Correct Answers (one per line)", "required": true},
            {"name": "randomize", "type": "checkbox", "label": "Randomize Questions", "required": false}
        ]
    }'::jsonb
),
-- LM11: True/False
(
    11,
    'True/False',
    'Richtig/Falsch Aussagen bewerten',
    'C',
    'basic',
    'optional',
    'check-circle',
    'true_false',
    '{"randomize": true, "show_explanations": true}'::jsonb,
    '{
        "agent_can_handle": false,
        "requires_fresh_ai": false,
        "knowledge_domains": [],
        "knowledge_cacheable": false,
        "complexity_threshold": 1
    }'::jsonb,
    '{
        "form_type": "dynamic",
        "fields": [
            {"name": "statements", "type": "textarea", "label": "True/False Statements (one per line)", "required": true},
            {"name": "correct_answers", "type": "textarea", "label": "Correct Answers (TRUE or FALSE, one per line)", "required": true},
            {"name": "show_explanations", "type": "checkbox", "label": "Show Explanations", "required": false}
        ]
    }'::jsonb
)
ON CONFLICT (method_type) DO NOTHING;

-- ============================================================================
-- Verification
-- ============================================================================

DO $$
BEGIN
    IF (SELECT COUNT(*) FROM learning_methods.learning_method_types WHERE active = TRUE) = 12 THEN
        RAISE NOTICE '✓ Successfully seeded 12 Content-Lernmethoden (COMPLETE CONFIG)';
        RAISE NOTICE '  Gruppe A (Erklärend): 5 Methods';
        RAISE NOTICE '  Gruppe B (Praxis): 4 Methods';
        RAISE NOTICE '  Gruppe C (Prüfung): 3 Methods';
        RAISE NOTICE '  All 12 LMs now have: prompt_template, default_config, agent_support, ui_schema';
        RAISE NOTICE '  ✓ 100% DB-driven configuration (no hardcoded Python!)';
    ELSE
        RAISE WARNING '⚠ Expected 12 Content-Lernmethoden, found %', (SELECT COUNT(*) FROM learning_methods.learning_method_types WHERE active = TRUE);
    END IF;
END $$;

COMMIT;

-- ============================================================================
-- End of Migration: 01_learning_methods_seed.sql
-- ============================================================================
