-- ============================================================================
-- Seed Data: Learning Method Model Requirements
-- Description: AI model requirements for all Learning Methods (LM0-LM32)
--              Specifies which LMs require KI assignment vs optional KI usage
-- Source: 055_learning_method_model_routing.sql
-- Author: LernsystemX Migration System
-- Date: 2026-01-26
-- Phase: 4 (Seed Data)
-- ============================================================================

-- ============================================================================
-- Learning Method Model Requirements - 33 Requirements (LM0-LM32)
-- ============================================================================
-- Seeds the learning_methods.learning_method_model_requirements table
-- Tracks which Learning Methods require an AI model assignment
--
-- Requirements Structure:
--   - learning_method_id: LM0-LM32 (33 total)
--   - required: TRUE if model assignment is mandatory, FALSE if optional
--   - recommended_categories: Array of suitable AI model categories
--   - requires_vision: TRUE if learning method needs vision capabilities
--   - description: Human-readable description for admin interface
--
-- Group A - Explanatory (LM0-LM7): Deep explanations, interactive theory, visualizations
-- Group B - Practice (LM8-LM17): Hands-on exercises, sandboxes, simulations
-- Group C - Exam (LM18-LM25): Assessments, free text answers, exam simulations
-- Group D - Pro/Meta (LM26-LM32): Adaptive difficulty, learning paths, tutors

INSERT INTO learning_methods.learning_method_model_requirements (learning_method_id, required, recommended_categories, requires_vision, description)
VALUES
    -- Group A - Explanatory (LM0-LM7)
    (0, TRUE, ARRAY['chat', 'reasoning'], FALSE, 'Deep Explanation - KI-intensiv'),
    (1, TRUE, ARRAY['chat'], FALSE, 'Schritt-für-Schritt-Erklärung'),
    (2, TRUE, ARRAY['chat'], FALSE, 'Interaktive Theorie'),
    (3, TRUE, ARRAY['chat', 'reasoning'], FALSE, 'Diagramm/Visualisierung'),
    (4, TRUE, ARRAY['chat'], FALSE, 'Glossar-Autogenerator'),
    (5, TRUE, ARRAY['chat'], FALSE, 'Mindmap-Generator'),
    (6, TRUE, ARRAY['chat'], FALSE, 'Beispiel-Szenario-Erklärung'),
    (7, TRUE, ARRAY['chat', 'reasoning'], FALSE, 'NPC-Tutor-Lecture - KI-intensiv'),

    -- Group B - Practice (LM8-LM17)
    (8, TRUE, ARRAY['chat', 'reasoning'], TRUE, 'Whiteboard-Aufgabe - KI-intensiv, Vision'),
    (9, TRUE, ARRAY['chat', 'reasoning'], FALSE, 'Code/IT-Config Sandbox'),
    (10, TRUE, ARRAY['chat'], FALSE, 'Netzwerk-Aufbau Simulation'),
    (11, TRUE, ARRAY['chat', 'reasoning'], FALSE, 'IT-Szenario lösen - KI-intensiv'),
    (12, TRUE, ARRAY['chat', 'reasoning'], FALSE, 'Mathe-Interaktiv'),
    (13, FALSE, ARRAY['chat'], FALSE, 'Flashcards - KI optional'),
    (14, FALSE, ARRAY['chat'], FALSE, 'Drag & Drop - KI optional'),
    (15, FALSE, ARRAY['chat'], FALSE, 'Lückentext - KI optional'),
    (16, TRUE, ARRAY['chat', 'reasoning'], FALSE, 'Fehleranalyse'),
    (17, TRUE, ARRAY['chat', 'reasoning'], FALSE, 'Hands-on Lab - KI-intensiv'),

    -- Group C - Exam (LM18-LM25)
    (18, TRUE, ARRAY['chat', 'reasoning'], FALSE, 'Freitext-Langantwort'),
    (19, TRUE, ARRAY['chat', 'reasoning'], FALSE, 'IHK-Stil Aufgaben - KI-intensiv'),
    (20, TRUE, ARRAY['chat', 'reasoning'], FALSE, 'Multi-Step Praxisprüfung - KI-intensiv'),
    (21, FALSE, ARRAY['chat'], FALSE, 'Zeitlimit-Training - KI optional'),
    (22, FALSE, ARRAY['chat'], FALSE, 'Prüfungs-Quiz - KI optional'),
    (23, FALSE, ARRAY['chat'], FALSE, 'Verständnis-Checks - KI optional'),
    (24, TRUE, ARRAY['chat', 'reasoning', 'audio'], FALSE, 'Mündliche Erklärung - KI-intensiv'),
    (25, TRUE, ARRAY['chat'], FALSE, 'Kapitel-Endprüfung'),

    -- Group D - Pro/Meta (LM26-LM31)
    (26, TRUE, ARRAY['reasoning', 'chat'], FALSE, 'Adaptive Difficulty - KI-intensiv'),
    (27, TRUE, ARRAY['reasoning', 'chat'], FALSE, 'Lernpfad-Autogenerator - KI-intensiv'),
    (28, TRUE, ARRAY['chat', 'reasoning'], FALSE, 'Persona-Tutor - KI-intensiv'),
    (29, TRUE, ARRAY['reasoning', 'chat'], FALSE, 'Sokratischer Dialog - KI-intensiv'),
    (30, TRUE, ARRAY['chat'], FALSE, 'Daily Recall / Spaced Repetition'),
    (31, FALSE, ARRAY['chat'], FALSE, 'Quest-/XP-Verknüpfung - KI optional'),
    (32, FALSE, ARRAY['chat'], FALSE, 'Vokabeltrainer - KI optional')

ON CONFLICT (learning_method_id) DO UPDATE SET
    required = EXCLUDED.required,
    recommended_categories = EXCLUDED.recommended_categories,
    requires_vision = EXCLUDED.requires_vision,
    description = EXCLUDED.description,
    updated_at = NOW();

-- ============================================================================
-- Verification
-- ============================================================================

SELECT COUNT(*) as total_lm_requirements FROM learning_methods.learning_method_model_requirements;
