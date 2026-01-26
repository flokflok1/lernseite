-- ============================================================================
-- Migration: 01_learning_methods_seed.sql
-- Version: 1.0.0
-- Description: Seed Data - 12 Content-Lernmethoden
-- Author: LernsystemX Migration System
-- Date: 2026-01-26
-- Phase: 5 (Seed Data - Content Configuration)
-- Dependencies: 04_LearningMethods/030_learning_methods_core.sql (tables must exist)
--
-- CRITICAL DISTINCTION:
-- This is SEED DATA, not STRUCTURE.
-- Structure (tables) is in 04_LearningMethods/030_learning_methods_core.sql
-- Configuration (actual 12 learning methods) is HERE
--
-- 12 Content-Lernmethoden in 3 Gruppen:
-- Gruppe A (Erklärend): Flashcards, Lückentext, Freitext, Multiple Choice, True/False (5 Methoden)
-- Gruppe B (Praxis): Code Challenge, Case Study, Simulation, Peer Review Exercise (4 Methoden)
-- Gruppe C (Prüfung): Objective Assessment, Practical Exam, Portfolio Assessment (3 Methoden)
--
-- Method Types: 0-11 (numeric IDs internally, real names in database)
-- See: LernsystemX-Doku/01_Core/02_Lernmethoden.md
-- ============================================================================

BEGIN TRANSACTION;

-- ============================================================================
-- GRUPPE A (ERKLÄREND) - 5 Methoden für Verständnis
-- Flashcards, Lückentext, Freitext, Multiple Choice, True/False
-- ============================================================================
-- Diese Methoden helfen Studenten, Konzepte zu VERSTEHEN

INSERT INTO learning_methods.learning_method_types
    (method_type, name, description, group_code, tier, ki_usage, icon)
VALUES
    (
        0,
        'Flashcards',
        'Interactive flashcard system for memorization and quick recall of key concepts, definitions, and vocabulary.',
        'A',
        'basic',
        'optional',
        'rectangle'
    ),
    (
        1,
        'Lückentext (Fill-in-the-Blank)',
        'Students complete sentences or passages by filling in missing words or phrases, testing comprehension.',
        'A',
        'basic',
        'optional',
        'text'
    ),
    (
        2,
        'Freitext (Free Text Response)',
        'Students write short or long-form responses to questions, essays, or prompts with AI-powered evaluation.',
        'A',
        'premium',
        'intensive',
        'pencil'
    ),
    (
        3,
        'Multiple Choice',
        'Students select one correct answer from multiple options, testing knowledge and reasoning.',
        'A',
        'basic',
        'optional',
        'list'
    ),
    (
        4,
        'True/False',
        'Binary choice questions where students determine if statements are true or false.',
        'A',
        'basic',
        'optional',
        'check'
    )
ON CONFLICT (method_type) DO NOTHING;

-- ============================================================================
-- GRUPPE B (PRAXIS) - 4 Methoden zum Üben und Anwenden
-- Code Challenge, Case Study, Simulation, Peer Review Exercise
-- ============================================================================
-- Diese Methoden ermöglichen Studenten zu ÜBEN und ANWENDEN

INSERT INTO learning_methods.learning_method_types
    (method_type, name, description, group_code, tier, ki_usage, icon)
VALUES
    (
        5,
        'Code Challenge',
        'Students write, test, and debug code in a containerized sandbox environment with auto-evaluation.',
        'B',
        'premium',
        'medium',
        'code'
    ),
    (
        6,
        'Case Study (Fallstudie)',
        'Real-world scenario analysis where students apply concepts to complex, multi-faceted problems.',
        'B',
        'premium',
        'medium',
        'folder'
    ),
    (
        7,
        'Simulation',
        'Interactive simulations where students experiment with systems and see consequences of their decisions.',
        'B',
        'premium',
        'medium',
        'sliders'
    ),
    (
        8,
        'Peer Review Exercise',
        'Students provide constructive feedback on peers'' work, developing critical evaluation skills.',
        'B',
        'basic',
        'optional',
        'eye'
    )
ON CONFLICT (method_type) DO NOTHING;

-- ============================================================================
-- GRUPPE C (PRÜFUNG) - 3 Methoden zum Kompetenznachweis
-- Objective Assessment, Practical Exam, Portfolio Assessment
-- ============================================================================
-- Diese Methoden ermöglichen Studenten ihre KOMPETENZ nachzuweisen

INSERT INTO learning_methods.learning_method_types
    (method_type, name, description, group_code, tier, ki_usage, icon)
VALUES
    (
        9,
        'Objective Assessment (Standardized Test)',
        'Structured assessment with multiple-choice, matching, and sequencing questions measuring knowledge.',
        'C',
        'basic',
        'optional',
        'clipboard-check'
    ),
    (
        10,
        'Practical Exam (Praktische Prüfung)',
        'Hands-on evaluation where students demonstrate skills in real or simulated environments.',
        'C',
        'premium',
        'intensive',
        'wrench'
    ),
    (
        11,
        'Portfolio Assessment',
        'Curated collection of student work demonstrating learning over time with reflective commentary.',
        'C',
        'premium',
        'medium',
        'briefcase'
    )
ON CONFLICT (method_type) DO NOTHING;

-- ============================================================================
-- Summary: 12 Content-Lernmethoden Successfully Seeded
-- ============================================================================

-- Verify all 12 methods were inserted
DO $$
BEGIN
    IF (SELECT COUNT(*) FROM learning_methods.learning_method_types) = 12 THEN
        RAISE NOTICE '✓ Successfully seeded 12 Content-Lernmethoden';
        RAISE NOTICE '  Gruppe A (Erklärend): Flashcards, Lückentext, Freitext, Multiple Choice, True/False';
        RAISE NOTICE '  Gruppe B (Praxis): Code Challenge, Case Study, Simulation, Peer Review Exercise';
        RAISE NOTICE '  Gruppe C (Prüfung): Objective Assessment, Practical Exam, Portfolio Assessment';
    ELSE
        RAISE WARNING '⚠ Expected 12 Content-Lernmethoden, found %', (SELECT COUNT(*) FROM learning_methods.learning_method_types);
    END IF;
END $$;

COMMIT;

-- ============================================================================
-- End of Migration: 01_learning_methods_seed.sql
-- ============================================================================
