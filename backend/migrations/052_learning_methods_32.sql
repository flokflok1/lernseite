-- ============================================================================
-- Migration 052: Lernmethoden-System auf 32 Methoden (LM00-LM31) umstellen
-- ============================================================================
--
-- Phase D3.1 - LernsystemX
--
-- Änderungen:
-- 1. CHECK-Constraint für method_type von BETWEEN 1 AND 21 auf BETWEEN 0 AND 31
-- 2. CHECK-Constraint für method_number von BETWEEN 1 AND 21 auf BETWEEN 0 AND 31
-- 3. Erweitere learning_method_types um group_code Spalte
-- 4. Ersetze tier-Constraint durch group-basiertes System
-- 5. Seed der 32 Lernmethoden-Typen in learning_method_types
--
-- Referenz: 02_Lernmethoden.md (Master-Dokument)
--
-- Gruppe A (LM00-LM07): Erklärende Methoden - 8 Methoden
-- Gruppe B (LM08-LM17): Praxis/Übung - 10 Methoden
-- Gruppe C (LM18-LM25): Prüfungsorientierte Methoden - 8 Methoden
-- Gruppe D (LM26-LM31): Pro/Gamification - 6 Methoden
--
-- ============================================================================

-- ============================================================================
-- 1. DROP alte CHECK-Constraints
-- ============================================================================

-- learning_methods Tabelle
ALTER TABLE learning_methods
DROP CONSTRAINT IF EXISTS chk_method_type;

-- learning_method_types Tabelle
ALTER TABLE learning_method_types
DROP CONSTRAINT IF EXISTS chk_method_number;

-- Drop tier constraint (wird durch group_code ersetzt)
ALTER TABLE learning_method_types
DROP CONSTRAINT IF EXISTS chk_tier;

-- ============================================================================
-- 2. ADD neue Spalten für das 32-Methoden-System
-- ============================================================================

-- Gruppe-Code (A, B, C, D)
ALTER TABLE learning_method_types
ADD COLUMN IF NOT EXISTS group_code CHAR(1);

-- KI-Nutzungsintensität
ALTER TABLE learning_method_types
ADD COLUMN IF NOT EXISTS ki_usage VARCHAR(20) DEFAULT 'optional';

-- Default Prompt-Key für KI-System
ALTER TABLE learning_method_types
ADD COLUMN IF NOT EXISTS default_prompt_key VARCHAR(50);

-- ============================================================================
-- 3. ADD neue CHECK-Constraints (0-31)
-- ============================================================================

-- learning_methods: method_type muss zwischen 0 und 31 liegen
ALTER TABLE learning_methods
ADD CONSTRAINT chk_method_type CHECK (method_type BETWEEN 0 AND 31);

-- learning_method_types: method_number muss zwischen 0 und 31 liegen
ALTER TABLE learning_method_types
ADD CONSTRAINT chk_method_number CHECK (method_number BETWEEN 0 AND 31);

-- group_code Constraint
ALTER TABLE learning_method_types
ADD CONSTRAINT chk_group_code CHECK (group_code IN ('A', 'B', 'C', 'D'));

-- ki_usage Constraint
ALTER TABLE learning_method_types
ADD CONSTRAINT chk_ki_usage CHECK (ki_usage IN ('intensive', 'medium', 'optional'));

-- ============================================================================
-- 4. TRUNCATE und Seed learning_method_types mit allen 32 Methoden
-- ============================================================================

-- Alte Daten löschen (nur Type-Definitionen, nicht Instanzen)
TRUNCATE TABLE learning_method_types CASCADE;

-- Reset sequence
ALTER SEQUENCE IF EXISTS learning_method_types_type_id_seq RESTART WITH 1;

-- Seed alle 32 Lernmethoden-Typen
-- Spalten: method_number, name, group_code, description, ki_usage, default_prompt_key, tier (für Abwärtskompatibilität), active
-- Tier-Mapping: A+B teilweise = basic, A+B+C = premium, D = pro
INSERT INTO learning_method_types (method_number, name, group_code, description, ki_usage, default_prompt_key, tier, active) VALUES
-- ============================================================================
-- GRUPPE A – Erklärende Methoden (LM00-LM07) - tier: basic
-- ============================================================================
(0, 'Deep Explanation', 'A', 'Tiefgehende, KI-generierte Erklärungen komplexer Themen', 'intensive', 'deep_explanation', 'basic', true),
(1, 'Schritt-für-Schritt-Erklärung', 'A', 'Sequenzielle Anleitung für komplexe Prozesse', 'medium', 'step_by_step', 'basic', true),
(2, 'Interaktive Theorie', 'A', 'Theoretische Erklärung mit eingebetteten Verständnisfragen', 'medium', 'interactive_theory', 'basic', true),
(3, 'Diagramm/Visualisierung', 'A', 'Visuelle Darstellung von Konzepten (Flowcharts, UML, etc.)', 'medium', 'visualization', 'basic', true),
(4, 'Glossar-Autogenerator', 'A', 'Automatische Erstellung eines Glossars mit Fachbegriffen', 'medium', 'glossary', 'basic', true),
(5, 'Mindmap-Generator', 'A', 'KI-generierte Wissenslandkarten für Konzeptzusammenhänge', 'medium', 'mindmap', 'basic', true),
(6, 'Beispiel-Szenario-Erklärung', 'A', 'Erklärung anhand realer Praxisbeispiele (Real-World-Cases)', 'medium', 'scenario_explanation', 'basic', true),
(7, 'NPC-Tutor-Lecture', 'A', 'Virtueller Tutor erklärt Kapitel als Vorlesung', 'intensive', 'npc_tutor', 'basic', true),

-- ============================================================================
-- GRUPPE B – Praxis / Übung (LM08-LM17) - tier: basic
-- ============================================================================
(8, 'Whiteboard-Aufgabe', 'B', 'Zeichenaufgaben auf digitalem Whiteboard mit KI-Analyse', 'intensive', 'whiteboard', 'basic', true),
(9, 'Code/IT-Config Sandbox', 'B', 'Interaktive Coding-/Konfigurations-Umgebung', 'medium', 'code_sandbox', 'basic', true),
(10, 'Netzwerk-Aufbau Simulation', 'B', 'Simulierte Netzwerkumgebung für Topologie-Aufbau', 'medium', 'network_sim', 'basic', true),
(11, 'IT-Szenario lösen', 'B', 'Komplexe, mehrstufige IT-Case-Studies', 'intensive', 'it_scenario', 'basic', true),
(12, 'Mathe-Interaktiv', 'B', 'Mathematikaufgaben mit schrittweiser Eingabe und Feedback', 'medium', 'math_interactive', 'basic', true),
(13, 'Flashcards', 'B', 'Karteikarten mit Spaced-Repetition-Vorbereitung', 'optional', 'flashcards', 'basic', true),
(14, 'Drag & Drop Aufgaben', 'B', 'Elemente in richtige Reihenfolge/Kategorie ziehen', 'optional', 'drag_drop', 'basic', true),
(15, 'Lückentext-Aufgaben', 'B', 'Text mit auszufüllenden Lücken', 'optional', 'fill_blanks', 'basic', true),
(16, 'Fehleranalyse', 'B', 'Fehler in Code/Konfiguration finden und beheben', 'medium', 'error_analysis', 'basic', true),
(17, 'Hands-on Lab', 'B', 'Praktische Labor-Übungen mit virtueller Umgebung', 'intensive', 'hands_on_lab', 'basic', true),

-- ============================================================================
-- GRUPPE C – Prüfungsorientierte Methoden (LM18-LM25) - tier: premium
-- ============================================================================
(18, 'Freitext-Langantwort', 'C', 'Ausführliche schriftliche Antworten mit KI-Bewertung', 'medium', 'long_answer', 'premium', true),
(19, 'IHK-Stil Aufgaben', 'C', 'Prüfungsaufgaben im IHK-/Kammer-Format', 'intensive', 'ihk_style', 'premium', true),
(20, 'Multi-Step Praxisprüfung', 'C', 'Mehrstufige praktische Prüfungsszenarien', 'intensive', 'multi_step_exam', 'premium', true),
(21, 'Zeitlimit-Training', 'C', 'Übungen unter Zeitdruck für Prüfungssimulation', 'optional', 'time_limit', 'premium', true),
(22, 'Prüfungs-Quiz', 'C', 'Multiple-Choice und andere Quiz-Formate für Prüfungen', 'optional', 'exam_quiz', 'premium', true),
(23, 'Verständnis-Checks', 'C', 'Kurze Verständnisüberprüfungen während des Lernens', 'optional', 'comprehension_check', 'premium', true),
(24, 'Mündliche Erklärung', 'C', 'Sprachbasierte Antworten mit KI-Analyse', 'intensive', 'oral_explanation', 'premium', true),
(25, 'Kapitel-Endprüfung', 'C', 'Abschlusstest für ein Kapitel/Modul', 'medium', 'chapter_exam', 'premium', true),

-- ============================================================================
-- GRUPPE D – Pro/Premium/Gamification/Tutor (LM26-LM31) - tier: pro
-- ============================================================================
(26, 'Adaptive Difficulty', 'D', 'KI passt Schwierigkeit dynamisch an Lernerfolg an', 'intensive', 'adaptive_difficulty', 'pro', true),
(27, 'Lernpfad-Autogenerator', 'D', 'KI generiert personalisierten Lernpfad', 'intensive', 'learning_path', 'pro', true),
(28, 'Persona-Tutor', 'D', 'KI-Tutor mit anpassbarer Persönlichkeit/Stil', 'intensive', 'persona_tutor', 'pro', true),
(29, 'Sokratischer Dialog', 'D', 'KI führt durch Fragen zum Verständnis (Sokratische Methode)', 'intensive', 'socratic_dialog', 'pro', true),
(30, 'Daily Recall / Spaced Repetition', 'D', 'Tägliche Wiederholungen mit Spaced-Repetition-Algorithmus', 'medium', 'spaced_repetition', 'pro', true),
(31, 'Quest-/XP-Verknüpfung', 'D', 'Gamification-Elemente: Quests, XP, Achievements', 'optional', 'quest_xp', 'pro', true);

-- ============================================================================
-- 5. Indexes für Performance
-- ============================================================================

-- Index für schnelle Suche nach group_code
CREATE INDEX IF NOT EXISTS idx_learning_method_types_group_code
ON learning_method_types(group_code);

-- Index für default_prompt_key für KI-System
CREATE INDEX IF NOT EXISTS idx_learning_method_types_prompt_key
ON learning_method_types(default_prompt_key);

-- ============================================================================
-- 6. Kommentare aktualisieren
-- ============================================================================

COMMENT ON TABLE learning_method_types IS
'32 Lernmethoden-Typen (LM00-LM31) gemäß 02_Lernmethoden.md.
Gruppe A (0-7): Erklärend,
Gruppe B (8-17): Praxis/Übung,
Gruppe C (18-25): Prüfungsorientiert,
Gruppe D (26-31): Pro/Gamification.
Migration 052 - Phase D3.1';

COMMENT ON COLUMN learning_method_types.method_number IS 'Methoden-ID 0-31: LM00 bis LM31';
COMMENT ON COLUMN learning_method_types.group_code IS 'Gruppen-Code: A (Erklärend), B (Praxis), C (Prüfung), D (Pro)';
COMMENT ON COLUMN learning_method_types.ki_usage IS 'KI-Nutzungsintensität: intensive, medium, optional';
COMMENT ON COLUMN learning_method_types.default_prompt_key IS 'Standard-Prompt-Key für KI-Generierung';
COMMENT ON COLUMN learning_method_types.tier IS 'Abwärtskompatibilität: basic, premium, pro';

-- ============================================================================
-- Migration 052 abgeschlossen - Phase D3.1
-- ============================================================================
