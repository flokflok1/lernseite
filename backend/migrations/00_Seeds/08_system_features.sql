-- ============================================================================
-- Seed Data: 25 System Features (Meta-features, not Content-Lernmethoden)
-- Description: System features support infrastructure (audio, collaboration, exams, etc.)
-- Source: 100_system_features.sql
-- Author: LernsystemX Migration System
-- Date: 2026-01-26
-- Phase: 4 (Seed Data)
-- ============================================================================

INSERT INTO support_systems.system_features (feature_code, feature_name, description, category, requires_infrastructure, requires_external_service, icon, former_lm_id) VALUES
    -- Visualization Features (1)
    ('mindmap_generator', 'Mindmap-Generator', 'Generiert kursweite Mindmaps aus Theorie-Inhalten', 'visualization', FALSE, FALSE, 'sitemap', NULL),

    -- Interactive Tools (3) - formerly content LMs
    ('whiteboard_engine', 'Whiteboard-Engine', 'Interaktive Whiteboard-Aufgaben mit KI-Erkennung (Formeln, Diagramme, Keywords)', 'interactive_tools', TRUE, TRUE, 'pencil-ruler', 5),
    ('it_sandbox', 'IT-Sandbox', 'Praktische Übungen in simulierten IT-Umgebungen (Code, Config, Netzwerk, Terminal)', 'it_environments', TRUE, TRUE, 'laptop-code', 10),
    ('speech_to_text', 'Speech-to-Text Engine', 'Sprachaufnahme mit KI-Transkription & Bewertung', 'audio', TRUE, TRUE, 'microphone', 17),

    -- Meta-Features (1)
    ('timer_wrapper', 'Timer/Zeitlimit-Feature', 'Zeitbegrenzung für beliebige Aufgaben (Meta-Feature)', 'meta_features', FALSE, FALSE, 'clock', 14),

    -- Exam & Assessment Systems (3)
    ('ihk_exam_system', 'IHK-Prüfungssystem', 'Prüfungsaufgaben im IHK/Kammer-Format', 'exam_systems', TRUE, TRUE, 'certificate', 10),
    ('practical_exam_engine', 'Praxisprüfungs-Engine', 'Mehrstufige praktische Prüfungsaufgaben', 'exam_systems', TRUE, FALSE, 'clipboard-check', 11),
    ('chapter_completion_system', 'Kapitelabschluss-System', 'Umfassende Kapitelabschluss-Prüfung', 'exam_systems', FALSE, TRUE, 'trophy', 14),

    -- Tutor & Coaching (3)
    ('npc_tutor', 'NPC-/Persona-Tutor', 'KI-basierter Tutor mit verschiedenen Rollen/Personas', 'tutor', FALSE, TRUE, 'user-graduate', NULL),
    ('socratic_dialog', 'Sokratischer Dialog', 'KI-geführter Dialog zur Wissensvermittlung', 'tutor', FALSE, TRUE, 'comments', NULL),
    ('comprehension_checker', 'Verständnis-Checker', 'Mikro-Checks basierend auf Bloom-Taxonomie', 'tutor', FALSE, TRUE, 'check-circle', 13),

    -- Gamification (3)
    ('adaptive_difficulty', 'Adaptive Schwierigkeit', 'Passt Aufgabenschwierigkeit automatisch an Leistungsstand an', 'gamification', FALSE, FALSE, 'chart-line', NULL),
    ('xp_quest_system', 'XP & Quest System', 'Erfahrungspunkte, Level, Achievements, Daily Quests', 'gamification', FALSE, FALSE, 'trophy', NULL),
    ('daily_recall', 'Daily Recall', 'Tägliche Wiederholungslogik (Spaced Repetition)', 'gamification', FALSE, FALSE, 'calendar-check', NULL),

    -- Learning Paths (1)
    ('learning_path_generator', 'Lernpfad-Generator', 'KI-gestützte Lernpfad-Erstellung und -Optimierung', 'learning_paths', FALSE, TRUE, 'route', NULL),

    -- Collaboration (7)
    ('peer_instruction', 'Peer Instruction', 'Peer Instruction Methode (Think-Pair-Share)', 'collaboration', FALSE, FALSE, 'users', 26),
    ('peer_review', 'Peer Review', 'Gegenseitige Bewertung von Lösungen', 'collaboration', FALSE, FALSE, 'users', NULL),
    ('team_case', 'Team-Case', 'Kollaborative Fallbearbeitung', 'collaboration', FALSE, FALSE, 'people-carry', NULL),
    ('learning_journal', 'Lerntagebuch', 'Persönliche Reflexion und Dokumentation', 'collaboration', FALSE, FALSE, 'book', NULL),
    ('project_portfolio', 'Projekt-Portfolio', 'Sammlung eigener Projekte', 'collaboration', FALSE, FALSE, 'folder-open', NULL),
    ('project_based_learning', 'Projektbasiertes Lernen', 'Project-Based Learning Workflows', 'collaboration', FALSE, FALSE, 'tasks', 31),
    ('inverted_classroom', 'Inverted Classroom', 'Flipped Classroom Unterstützung', 'collaboration', FALSE, FALSE, 'chalkboard-teacher', NULL),

    -- IT Environments (3)
    ('code_sandbox', 'Code-Sandbox', 'Isolierte Code-Ausführungsumgebung', 'it_environments', TRUE, FALSE, 'code', NULL),
    ('network_simulation', 'Netzwerk-Simulation', 'Virtuelle Netzwerk-Topologien', 'it_environments', TRUE, FALSE, 'network-wired', NULL),
    ('terminal_access', 'Terminal-Zugriff', 'Web-basierter Terminal-Zugang', 'it_environments', TRUE, FALSE, 'terminal', NULL)
ON CONFLICT (feature_code) DO NOTHING;

-- Verification
SELECT COUNT(*) as total_system_features FROM support_systems.system_features;
