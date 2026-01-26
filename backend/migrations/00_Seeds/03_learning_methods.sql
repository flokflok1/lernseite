-- ============================================================================
-- Seed Migration: 03_learning_methods.sql
-- Description: Seed data for 12 Content-Lernmethoden (LM00-LM11)
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-01-25
-- Phase: 4 (Seeds - executes AFTER all table creation)
-- Dependencies: 015_learning_methods.sql (tables must exist first)
-- ============================================================================

-- ============================================================================
-- SEED DATA: 12 Content-Lernmethoden (Gruppe A-C)
-- LM00-LM11: 12 Content-Lernmethoden in 3 Gruppen
-- LM12-LM32: Deprecated - moved to support_systems.system_features
-- ============================================================================
INSERT INTO learning_methods.learning_method_types (method_type, name, description, group_code, tier, ki_usage, icon) VALUES
    -- Gruppe A: Erklärend (lm00-lm04) - 5 Methoden
    (0, 'Tiefgehende Erklärung', 'KI-generierte Erklärung mit Beispielen & Analogien', 'A', 'basic', 'intensive', 'book-open'),
    (1, 'Schritt-für-Schritt', 'Sequenzielle Anleitung in nummerierten Schritten', 'A', 'basic', 'medium', 'list-ordered'),
    (2, 'Interaktive Theorie', 'Theorie mit interaktiven Frage-Antwort-Elementen', 'A', 'basic', 'medium', 'lightbulb'),
    (3, 'Diagramm/Visualisierung', 'Grafische Darstellung komplexer Konzepte', 'A', 'basic', 'medium', 'chart-network'),
    (4, 'Beispiel-Szenario', 'Praxisnahes Anwendungsbeispiel mit Kontext', 'A', 'basic', 'medium', 'clipboard-list'),
    -- Gruppe B: Praxis (lm05-lm08) - 4 Methoden
    (5, 'Mathe-Interaktiv', 'Mathematische Aufgaben mit Schritt-Erkennung', 'B', 'basic', 'medium', 'calculator'),
    (6, 'Flashcards', 'Digitale Lernkarten für Wiederholung', 'B', 'basic', 'optional', 'cards'),
    (7, 'Drag & Drop', 'Zuordnungsaufgaben per Drag & Drop', 'B', 'basic', 'optional', 'hand-pointer'),
    (8, 'Lückentext', 'Lückentexte mit Auto-Korrektur', 'B', 'basic', 'optional', 'align-left'),
    -- Gruppe C: Prüfung (lm09-lm11) - 3 Methoden
    (9, 'Freitext-Langantwort', 'Offene Fragen mit KI-Bewertung', 'C', 'premium', 'medium', 'pen-fancy'),
    (10, 'IHK-Stil Aufgaben', 'Prüfungsaufgaben nach IHK-Standard', 'C', 'premium', 'intensive', 'file-certificate'),
    (11, 'Multi-Step Praxisprüfung', 'Mehrstufige praktische Prüfung', 'C', 'premium', 'intensive', 'tasks')
ON CONFLICT (method_type) DO NOTHING;

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- Note: Function update_updated_at_column() defined in 007_functions.sql
-- ============================================================================
DROP TRIGGER IF EXISTS update_lm_types_updated_at ON learning_methods.learning_method_types;
CREATE TRIGGER update_lm_types_updated_at
    BEFORE UPDATE ON learning_methods.learning_method_types
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_lm_instances_updated_at ON learning_methods.learning_method_instances;
CREATE TRIGGER update_lm_instances_updated_at
    BEFORE UPDATE ON learning_methods.learning_method_instances
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Verification
-- ============================================================================
-- Expected: 12 learning methods (LM00-LM11)
SELECT COUNT(*) as "learning_methods_count",
       MIN(method_type) as "min_type",
       MAX(method_type) as "max_type"
FROM learning_methods.learning_method_types;

-- Expected: Groups A (5), B (4), C (3)
SELECT group_code, COUNT(*) as "count"
FROM learning_methods.learning_method_types
GROUP BY group_code
ORDER BY group_code;

-- Expected: 2 triggers created
SELECT COUNT(*) as "triggers_count" FROM information_schema.triggers
WHERE trigger_schema = 'learning_methods' AND trigger_name LIKE 'update_%_updated_at';

-- ============================================================================
-- End of Seed Migration: 03_learning_methods.sql
-- ============================================================================
