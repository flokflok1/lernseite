-- ============================================================================
-- Seed Data: Capability Slots & Learning Method Slot Requirements
-- Description: Multi-Model LM Routing - Capability Slots System
-- Source: 056_consolidated.sql
-- Author: LernsystemX Migration System
-- Date: 2026-01-26
-- Phase: 4 (Seed Data)
-- ============================================================================

-- ============================================================================
-- Default Capability Slots (10 total)
-- Description: Definition of all available capability slots for AI models
-- ============================================================================

INSERT INTO learning_methods.capability_slots (slot_code, display_name, description, required_category, accepted_categories, icon, sort_order)
VALUES
    ('chat', 'Chat/Text', 'Standard text generation and chat completions', 'chat', ARRAY['reasoning', 'multimodal'], 'message-square', 10),
    ('reasoning', 'Reasoning', 'Complex reasoning and analysis tasks (o1, o3)', 'reasoning', ARRAY['chat'], 'brain', 20),
    ('vision', 'Vision', 'Image analysis and visual understanding', 'chat', ARRAY['multimodal'], 'eye', 30),
    ('stt', 'Speech-to-Text', 'Audio transcription (Whisper)', 'audio', ARRAY[]::TEXT[], 'mic', 40),
    ('tts', 'Text-to-Speech', 'Voice synthesis (TTS)', 'audio', ARRAY[]::TEXT[], 'volume-2', 50),
    ('realtime', 'Realtime', 'Bidirectional audio streaming for live conversations', 'realtime', ARRAY[]::TEXT[], 'radio', 60),
    ('code_exec', 'Code Execution', 'Code interpreter and execution sandbox', 'chat', ARRAY['reasoning'], 'terminal', 70),
    ('image_gen', 'Image Generation', 'Image creation (DALL-E)', 'image', ARRAY[]::TEXT[], 'image', 80),
    ('embedding', 'Embedding', 'Text embeddings for semantic search', 'embedding', ARRAY[]::TEXT[], 'layers', 90),
    ('moderation', 'Moderation', 'Content safety and moderation', 'moderation', ARRAY[]::TEXT[], 'shield', 100)
ON CONFLICT (slot_code) DO UPDATE SET
    display_name = EXCLUDED.display_name,
    description = EXCLUDED.description,
    required_category = EXCLUDED.required_category,
    accepted_categories = EXCLUDED.accepted_categories,
    icon = EXCLUDED.icon,
    sort_order = EXCLUDED.sort_order,
    updated_at = NOW();

-- ============================================================================
-- Helper Function for Slot ID Lookup
-- ============================================================================

CREATE OR REPLACE FUNCTION get_slot_id(p_slot_code VARCHAR) RETURNS INTEGER AS $$
    SELECT slot_id FROM learning_methods.capability_slots WHERE slot_code = p_slot_code;
$$ LANGUAGE SQL STABLE;

-- ============================================================================
-- Group A - Explanatory Methods (LM00-LM07)
-- ============================================================================

INSERT INTO learning_methods.lm_slot_requirements (learning_method_id, slot_id, is_required, is_primary, usage_description)
VALUES
    (0, get_slot_id('chat'), TRUE, TRUE, 'Haupttext-Generierung für tiefe Erklärungen'),
    (0, get_slot_id('tts'), FALSE, FALSE, 'Optionale Vorlesefunktion'),
    (1, get_slot_id('chat'), TRUE, TRUE, 'Sequenzielle Erklärungen generieren'),
    (2, get_slot_id('chat'), TRUE, TRUE, 'Theorie mit eingebetteten Fragen'),
    (3, get_slot_id('chat'), TRUE, TRUE, 'Diagramm-Beschreibungen und Mermaid-Code'),
    (3, get_slot_id('image_gen'), FALSE, FALSE, 'Optionale Bildgenerierung'),
    (4, get_slot_id('chat'), TRUE, TRUE, 'Fachbegriffe extrahieren und erklären'),
    (5, get_slot_id('chat'), TRUE, TRUE, 'Mindmap-Struktur generieren'),
    (6, get_slot_id('chat'), TRUE, TRUE, 'Real-World-Cases beschreiben'),
    (7, get_slot_id('chat'), TRUE, TRUE, 'Lecture-Content generieren'),
    (7, get_slot_id('tts'), FALSE, FALSE, 'Sprachausgabe für Tutor'),
    (7, get_slot_id('realtime'), FALSE, FALSE, 'Live-Dialog mit Tutor')
ON CONFLICT (learning_method_id, slot_id) DO UPDATE SET
    is_required = EXCLUDED.is_required,
    is_primary = EXCLUDED.is_primary,
    usage_description = EXCLUDED.usage_description,
    updated_at = NOW();

-- ============================================================================
-- Group B - Practice Methods (LM08-LM17)
-- ============================================================================

INSERT INTO learning_methods.lm_slot_requirements (learning_method_id, slot_id, is_required, is_primary, usage_description)
VALUES
    (8, get_slot_id('chat'), TRUE, TRUE, 'Aufgaben generieren'),
    (8, get_slot_id('vision'), TRUE, FALSE, 'Zeichnungen analysieren'),
    (9, get_slot_id('chat'), TRUE, TRUE, 'Code-Generierung und Erklärung'),
    (9, get_slot_id('code_exec'), FALSE, FALSE, 'Code-Ausführung und Validierung'),
    (10, get_slot_id('chat'), TRUE, TRUE, 'Netzwerk-Topologien generieren'),
    (10, get_slot_id('vision'), FALSE, FALSE, 'Topologie-Analyse'),
    (11, get_slot_id('chat'), TRUE, TRUE, 'IT-Cases beschreiben'),
    (11, get_slot_id('code_exec'), FALSE, FALSE, 'Lösungen validieren'),
    (12, get_slot_id('chat'), TRUE, TRUE, 'Mathe-Erklärungen'),
    (12, get_slot_id('vision'), FALSE, FALSE, 'Handschrift-Erkennung'),
    (13, get_slot_id('chat'), TRUE, TRUE, 'Flashcards generieren'),
    (14, get_slot_id('chat'), TRUE, TRUE, 'Zuordnungs-Aufgaben'),
    (15, get_slot_id('chat'), TRUE, TRUE, 'Lückentexte erstellen'),
    (16, get_slot_id('chat'), TRUE, TRUE, 'Fehler beschreiben und erklären'),
    (16, get_slot_id('code_exec'), FALSE, FALSE, 'Code-Fehler ausführen'),
    (16, get_slot_id('vision'), FALSE, FALSE, 'Screenshot-Analyse'),
    (17, get_slot_id('chat'), TRUE, TRUE, 'Lab-Anweisungen'),
    (17, get_slot_id('code_exec'), TRUE, FALSE, 'Lab-Umgebung')
ON CONFLICT (learning_method_id, slot_id) DO UPDATE SET
    is_required = EXCLUDED.is_required,
    is_primary = EXCLUDED.is_primary,
    usage_description = EXCLUDED.usage_description,
    updated_at = NOW();

-- ============================================================================
-- Group C - Exam-Oriented Methods (LM18-LM25)
-- ============================================================================

INSERT INTO learning_methods.lm_slot_requirements (learning_method_id, slot_id, is_required, is_primary, usage_description)
VALUES
    (18, get_slot_id('chat'), TRUE, TRUE, 'Antworten bewerten'),
    (18, get_slot_id('reasoning'), FALSE, FALSE, 'Tiefe Bewertung komplexer Antworten'),
    (19, get_slot_id('chat'), TRUE, TRUE, 'Prüfungsaufgaben generieren'),
    (19, get_slot_id('image_gen'), FALSE, FALSE, 'Diagramme für Aufgaben'),
    (20, get_slot_id('chat'), TRUE, TRUE, 'Prüfungs-Szenarien'),
    (20, get_slot_id('code_exec'), FALSE, FALSE, 'Praxis-Validierung'),
    (21, get_slot_id('chat'), TRUE, TRUE, 'Zeitbasierte Aufgaben'),
    (22, get_slot_id('chat'), TRUE, TRUE, 'MC-Fragen generieren'),
    (23, get_slot_id('chat'), TRUE, TRUE, 'Kurze Verständnis-Checks'),
    (24, get_slot_id('chat'), TRUE, TRUE, 'Analyse der Erklärung'),
    (24, get_slot_id('stt'), TRUE, FALSE, 'Sprache transkribieren'),
    (24, get_slot_id('tts'), FALSE, FALSE, 'Feedback vorlesen'),
    (24, get_slot_id('realtime'), FALSE, FALSE, 'Live-Dialog mit Prüfer'),
    (25, get_slot_id('chat'), TRUE, TRUE, 'Umfassende Prüfung erstellen')
ON CONFLICT (learning_method_id, slot_id) DO UPDATE SET
    is_required = EXCLUDED.is_required,
    is_primary = EXCLUDED.is_primary,
    usage_description = EXCLUDED.usage_description,
    updated_at = NOW();

-- ============================================================================
-- Group D - Pro/Gamification Methods (LM26-LM32)
-- ============================================================================

INSERT INTO learning_methods.lm_slot_requirements (learning_method_id, slot_id, is_required, is_primary, usage_description)
VALUES
    (26, get_slot_id('chat'), TRUE, TRUE, 'Schwierigkeit anpassen'),
    (26, get_slot_id('reasoning'), FALSE, FALSE, 'Performance-Analyse'),
    (27, get_slot_id('chat'), TRUE, TRUE, 'Lernpfade generieren'),
    (27, get_slot_id('reasoning'), FALSE, FALSE, 'Optimale Pfade berechnen'),
    (28, get_slot_id('chat'), TRUE, TRUE, 'Tutor-Persönlichkeit'),
    (28, get_slot_id('tts'), FALSE, FALSE, 'Tutor-Stimme'),
    (28, get_slot_id('realtime'), FALSE, FALSE, 'Live-Konversation'),
    (29, get_slot_id('reasoning'), TRUE, TRUE, 'Sokratische Fragen'),
    (29, get_slot_id('chat'), FALSE, FALSE, 'Fallback für einfache Dialoge'),
    (29, get_slot_id('realtime'), FALSE, FALSE, 'Echtzeitdialog'),
    (30, get_slot_id('chat'), TRUE, TRUE, 'Wiederholungs-Content'),
    (31, get_slot_id('chat'), TRUE, TRUE, 'Quest-Beschreibungen')
ON CONFLICT (learning_method_id, slot_id) DO UPDATE SET
    is_required = EXCLUDED.is_required,
    is_primary = EXCLUDED.is_primary,
    usage_description = EXCLUDED.usage_description,
    updated_at = NOW();

-- ============================================================================
-- Cleanup Helper Function
-- ============================================================================

DROP FUNCTION IF EXISTS get_slot_id(VARCHAR);

-- ============================================================================
-- Verification
-- ============================================================================

SELECT COUNT(*) as total_capability_slots FROM learning_methods.capability_slots;
SELECT COUNT(*) as total_lm_slot_requirements FROM learning_methods.lm_slot_requirements;
