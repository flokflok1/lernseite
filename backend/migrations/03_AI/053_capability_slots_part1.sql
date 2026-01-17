-- ============================================================================
-- Migration: 060_capability_slots.sql
-- Description: Capability Slots System for Multi-Model LM Routing
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-12-04
-- ============================================================================
--
-- This migration transforms the LM routing system from "1 model per LM" to
-- "multiple capability slots per LM". Each LM can now have different models
-- assigned to different functionality slots (chat, tts, stt, vision, realtime, etc.)
--
-- Example: LM24 (Mündliche Erklärung) needs:
--   - chat: gpt-4o (text analysis)
--   - stt: whisper-1 (speech-to-text)
--   - tts: tts-1 (text-to-speech)
--   - realtime: gpt-4o-realtime (live dialog) - optional
-- ============================================================================

-- ============================================================================
-- TABLE 1: capability_slots
-- Definition of all available capability slots
-- ============================================================================

CREATE TABLE IF NOT EXISTS learning_methods.capability_slots (
    slot_id SERIAL PRIMARY KEY,

    -- Unique slot code (used in code/API)
    slot_code VARCHAR(30) NOT NULL UNIQUE,

    -- Display name for UI
    display_name VARCHAR(100) NOT NULL,

    -- Description of what this slot is for
    description TEXT,

    -- Which ai_models.category this slot accepts
    -- NULL means any category is allowed
    required_category VARCHAR(50) NULL,

    -- Additional accepted categories (for flexibility)
    accepted_categories TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- Icon for UI (optional, e.g. 'chat', 'mic', 'eye')
    icon VARCHAR(50) DEFAULT 'cpu',

    -- Sort order for display
    sort_order INTEGER NOT NULL DEFAULT 100,

    -- Is this a core/system slot or custom?
    is_system BOOLEAN NOT NULL DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Comments
COMMENT ON TABLE learning_methods.capability_slots IS 'Definition of capability slots for multi-model LM routing';
COMMENT ON COLUMN learning_methods.capability_slots.slot_code IS 'Unique code for slot (used in code/API): chat, stt, tts, vision, realtime, etc.';
COMMENT ON COLUMN learning_methods.capability_slots.required_category IS 'Primary ai_models.category this slot accepts';
COMMENT ON COLUMN learning_methods.capability_slots.accepted_categories IS 'Additional categories that can be assigned to this slot';

-- ============================================================================
-- SEED: Default capability slots
-- ============================================================================

INSERT INTO learning_methods.capability_slots (slot_code, display_name, description, required_category, accepted_categories, icon, sort_order) VALUES
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
-- TABLE 2: lm_slot_requirements
-- Which capability slots does each Learning Method require/support
-- ============================================================================

CREATE TABLE IF NOT EXISTS learning_methods.lm_slot_requirements (
    requirement_id SERIAL PRIMARY KEY,

    -- Learning Method ID (0-25 = Content-LMs, 26-31 für Abwärtskompatibilität)
    learning_method_id INTEGER NOT NULL,

    -- Capability slot reference
    slot_id INTEGER NOT NULL REFERENCES learning_methods.capability_slots(slot_id) ON DELETE CASCADE,

    -- Is this slot required for the LM to function?
    is_required BOOLEAN NOT NULL DEFAULT FALSE,

    -- Is this the primary slot? (used as main model if only one configured)
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,

    -- Description of how this slot is used in this LM
    usage_description TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Constraints
    -- Constraint: 0-31 für Abwärtskompatibilität
    CONSTRAINT chk_lm_slot_req_lm_id CHECK (learning_method_id >= 0 AND learning_method_id <= 31),
    CONSTRAINT uq_lm_slot_requirement UNIQUE (learning_method_id, slot_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_lm_slot_req_lm ON learning_methods.lm_slot_requirements (learning_method_id);
CREATE INDEX IF NOT EXISTS idx_lm_slot_req_slot ON learning_methods.lm_slot_requirements (slot_id);
CREATE INDEX IF NOT EXISTS idx_lm_slot_req_required ON learning_methods.lm_slot_requirements (is_required) WHERE is_required = TRUE;

-- Comments
COMMENT ON TABLE learning_methods.lm_slot_requirements IS 'Defines which capability slots each Learning Method needs';
COMMENT ON COLUMN learning_methods.lm_slot_requirements.is_required IS 'TRUE = LM will not work without this slot assigned';
COMMENT ON COLUMN learning_methods.lm_slot_requirements.is_primary IS 'TRUE = Primary/fallback slot for this LM';

-- ============================================================================
-- SEED: LM Slot Requirements für alle Lernmethoden
-- ============================================================================

-- Helper function to get slot_id by code
CREATE OR REPLACE FUNCTION get_slot_id(p_slot_code VARCHAR) RETURNS INTEGER AS $$
    SELECT slot_id FROM learning_methods.capability_slots WHERE slot_code = p_slot_code;
$$ LANGUAGE SQL STABLE;

-- Group A - Explanatory Methods (LM00-LM07)
INSERT INTO learning_methods.lm_slot_requirements (learning_method_id, slot_id, is_required, is_primary, usage_description) VALUES
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

-- Group B - Practice (LM08-LM17)
INSERT INTO learning_methods.lm_slot_requirements (learning_method_id, slot_id, is_required, is_primary, usage_description) VALUES
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

-- Group C - Exam-Oriented (LM18-LM25)
INSERT INTO learning_methods.lm_slot_requirements (learning_method_id, slot_id, is_required, is_primary, usage_description) VALUES
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

-- Group D - Pro/Gamification (LM26-LM32)
INSERT INTO learning_methods.lm_slot_requirements (learning_method_id, slot_id, is_required, is_primary, usage_description) VALUES
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

-- Drop helper function
DROP FUNCTION IF EXISTS get_slot_id(VARCHAR);

-- ============================================================================
-- TABLE 3: lm_slot_assignments
-- Admin assignments of models to slots per LM
-- ============================================================================

CREATE TABLE IF NOT EXISTS learning_methods.lm_slot_assignments (
    assignment_id SERIAL PRIMARY KEY,

    -- Learning Method ID (0-25 = Content-LMs, 26-31 für Abwärtskompatibilität)
    learning_method_id INTEGER NOT NULL,

    -- Capability slot reference
    slot_id INTEGER NOT NULL REFERENCES learning_methods.capability_slots(slot_id) ON DELETE CASCADE,

    -- Assigned AI model
    model_id INTEGER NOT NULL REFERENCES ai_pipeline.ai_models(model_id) ON DELETE CASCADE,

    -- Scope: 'system' (global), 'course', or 'chapter'
    scope VARCHAR(20) NOT NULL DEFAULT 'system',

    -- Optional scope reference (course_id or chapter_id)
    scope_reference_id UUID NULL,
