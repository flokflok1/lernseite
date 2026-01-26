-- ============================================================================
-- Migration: 02_system_features_seed.sql
-- Version: 1.0.0
-- Description: Seed Data - 25 System-Features (Tools/Services with Infrastructure)
-- Author: LernsystemX Migration System
-- Date: 2026-01-26
-- Phase: 5 (Seed Data - System Configuration)
-- Dependencies: 070_system_features.sql (tables must exist)
--
-- CRITICAL DISTINCTION:
-- This is SEED DATA, not STRUCTURE.
-- Structure (tables) is in 070_system_features.sql
-- Configuration (actual 25 features) is HERE
--
-- These 25 System-Features are different from Content-Lernmethoden (Flashcards, Multiple Choice, etc.)
-- See: LernsystemX-Doku/01_Core/02a_System-Features.md
-- ============================================================================

BEGIN TRANSACTION;

-- ============================================================================
-- 1. INTERACTIVE TOOLS (3 features)
-- ============================================================================

INSERT INTO system_features.system_features
    (feature_code, feature_name, description, category, requires_infrastructure, requires_external_service, icon)
VALUES
    (
        'math_patterns',
        'Math Pattern Recognition',
        'Advanced regex-based pattern matching for mathematical expressions. Validates student math answers across algebra, calculus, trigonometry.',
        'interactive_tools',
        true,
        false,
        'calculator'
    ),
    (
        'whiteboard_engine',
        'Interactive Whiteboard',
        'Real-time collaborative whiteboard with formula recognition, shape detection, and diagram analysis powered by AI vision models.',
        'interactive_tools',
        true,
        true,  -- requires_external_service for vision API
        'pencil-square'
    ),
    (
        'speech_to_text',
        'Speech Recognition',
        'Convert student spoken answers to text for evaluation in language courses and oral exams.',
        'interactive_tools',
        true,
        true,  -- requires external STT service
        'mic'
    )
ON CONFLICT (feature_code) DO NOTHING;

-- ============================================================================
-- 2. EXAM & ASSESSMENT SYSTEMS (4 features)
-- ============================================================================

INSERT INTO system_features.system_features
    (feature_code, feature_name, description, category, requires_infrastructure, requires_external_service, icon)
VALUES
    (
        'ihk_exam_system',
        'IHK Exam Format',
        'German vocational (IHK) style exams with scenario-based questions and practical tasks.',
        'exam_systems',
        false,
        false,
        'clipboard-check'
    ),
    (
        'practical_exam_engine',
        'Practical Exam Engine',
        'Hands-on practical assessments with automated code/solution execution and evaluation.',
        'exam_systems',
        true,  -- requires Docker/containers
        false,
        'code-bracket'
    ),
    (
        'comprehension_checker',
        'Comprehension Verification',
        'AI-powered tool to verify students actually understand concepts (not just memorizing).',
        'exam_systems',
        false,
        true,  -- uses AI API
        'brain'
    ),
    (
        'chapter_completion_system',
        'Chapter Completion Assessment',
        'Automatic assessment when students complete a chapter (validates learning objectives).',
        'exam_systems',
        false,
        true,  -- uses AI for assessment
        'flag-checkered'
    )
ON CONFLICT (feature_code) DO NOTHING;

-- ============================================================================
-- 3. TUTOR & COACHING (2 features)
-- ============================================================================

INSERT INTO system_features.system_features
    (feature_code, feature_name, description, category, requires_infrastructure, requires_external_service, icon)
VALUES
    (
        'npc_tutor',
        'NPC Tutor Companion',
        'AI-powered tutor that explains concepts, answers questions, and guides students through problems.',
        'tutor_coaching',
        false,
        true,  -- uses AI API
        'robot'
    ),
    (
        'socratic_dialog',
        'Socratic Questioning',
        'Tutor uses Socratic method to guide students to discover answers themselves.',
        'tutor_coaching',
        false,
        true,  -- uses AI for dialog
        'lightbulb'
    )
ON CONFLICT (feature_code) DO NOTHING;

-- ============================================================================
-- 4. GAMIFICATION (3 features)
-- ============================================================================

INSERT INTO system_features.system_features
    (feature_code, feature_name, description, category, requires_infrastructure, requires_external_service, icon)
VALUES
    (
        'adaptive_difficulty',
        'Adaptive Difficulty',
        'System automatically adjusts task difficulty based on student performance (easier if struggling, harder if excelling).',
        'gamification',
        false,
        false,
        'gauge'
    ),
    (
        'xp_quest_system',
        'XP & Quest System',
        'Gamified learning with experience points, quests, and progression mechanics.',
        'gamification',
        false,
        false,
        'star'
    ),
    (
        'daily_recall',
        'Daily Recall Challenge',
        'Spaced repetition system with daily challenges to reinforce learning.',
        'gamification',
        false,
        false,
        'calendar'
    )
ON CONFLICT (feature_code) DO NOTHING;

-- ============================================================================
-- 5. LEARNING PATHS (1 feature)
-- ============================================================================

INSERT INTO system_features.system_features
    (feature_code, feature_name, description, category, requires_infrastructure, requires_external_service, icon)
VALUES
    (
        'learning_path_generator',
        'Personalized Learning Path',
        'AI generates optimal learning sequence based on student knowledge, goals, and learning style.',
        'learning_paths',
        false,
        true,  -- uses AI for path generation
        'path'
    )
ON CONFLICT (feature_code) DO NOTHING;

-- ============================================================================
-- 6. COLLABORATION (7 features)
-- ============================================================================

INSERT INTO system_features.system_features
    (feature_code, feature_name, description, category, requires_infrastructure, requires_external_service, icon)
VALUES
    (
        'peer_instruction',
        'Peer Instruction',
        'Students work together to solve problems and teach each other.',
        'collaboration',
        false,
        false,
        'handshake'
    ),
    (
        'team_case',
        'Team Case Study',
        'Group-based case study analysis with collaborative problem solving.',
        'collaboration',
        false,
        false,
        'folder'
    ),
    (
        'peer_review',
        'Peer Review System',
        'Students review and provide feedback on each other\'s work.',
        'collaboration',
        false,
        false,
        'eye'
    ),
    (
        'learning_journal',
        'Learning Journal',
        'Students maintain reflective journals with feedback from peers and tutors.',
        'collaboration',
        false,
        false,
        'journal'
    ),
    (
        'project_portfolio',
        'Project Portfolio',
        'Students build portfolio of work demonstrating competency across multiple domains.',
        'collaboration',
        false,
        false,
        'briefcase'
    ),
    (
        'project_based_learning',
        'Project-Based Learning',
        'Extended projects where students apply multiple competencies to real-world problems.',
        'collaboration',
        true,  -- may require external resources
        false,
        'hammer'
    ),
    (
        'inverted_classroom',
        'Inverted Classroom',
        'Students learn content outside class, class time used for discussion and problem-solving.',
        'collaboration',
        false,
        false,
        'door-open'
    )
ON CONFLICT (feature_code) DO NOTHING;

-- ============================================================================
-- 7. IT ENVIRONMENTS (3 features)
-- ============================================================================

INSERT INTO system_features.system_features
    (feature_code, feature_name, description, category, requires_infrastructure, requires_external_service, icon)
VALUES
    (
        'code_sandbox',
        'Code Execution Sandbox',
        'Safe containerized environment to run student code (supports Python, JavaScript, Java, etc.).',
        'it_environments',
        true,  -- requires Docker
        false,
        'box'
    ),
    (
        'network_simulation',
        'Network Simulation',
        'Virtual networking environment for IT networking courses (routers, switches, VLANs).',
        'it_environments',
        true,  -- resource intensive
        false,
        'broadcast'
    ),
    (
        'terminal_access',
        'Terminal/Shell Access',
        'Safe Linux terminal access for system administration and DevOps training.',
        'it_environments',
        true,  -- requires container
        false,
        'terminal'
    )
ON CONFLICT (feature_code) DO NOTHING;

-- ============================================================================
-- 8. VISUALIZATION (1 feature)
-- ============================================================================

INSERT INTO system_features.system_features
    (feature_code, feature_name, description, category, requires_infrastructure, requires_external_service, icon)
VALUES
    (
        'mindmap_generator',
        'Mind Map Generator',
        'AI-powered tool to generate mind maps from course content for better visual learning.',
        'visualization',
        false,
        true,  -- uses AI and visualization service
        'sitemap'
    )
ON CONFLICT (feature_code) DO NOTHING;

-- ============================================================================
-- 9. META FEATURES (1 feature)
-- ============================================================================

INSERT INTO system_features.system_features
    (feature_code, feature_name, description, category, requires_infrastructure, requires_external_service, icon)
VALUES
    (
        'timer_wrapper',
        'Timed Tasks',
        'Wrapper feature that adds time limits to any learning method (creates time pressure).',
        'meta_features',
        false,
        false,
        'hourglass-end'
    )
ON CONFLICT (feature_code) DO NOTHING;

-- ============================================================================
-- Summary: 25 System-Features Successfully Seeded
-- ============================================================================

-- Verify all 25 features were inserted
DO $$
BEGIN
    IF (SELECT COUNT(*) FROM system_features.system_features) = 25 THEN
        RAISE NOTICE '✓ Successfully seeded 25 System-Features';
    ELSE
        RAISE WARNING '⚠ Expected 25 System-Features, found %', (SELECT COUNT(*) FROM system_features.system_features);
    END IF;
END $$;

COMMIT;

-- ============================================================================
-- End of Migration: 02_system_features_seed.sql
-- ============================================================================
