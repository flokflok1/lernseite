-- ============================================================================
-- Migration: 078_add_ui_schema.sql
-- Description: Add ui_schema JSONB column for schema-based dynamic LM forms
--              Enables zero-file-creation system for adding new Learning Methods
--              Supports i18n via keys + English fallbacks (hybrid approach)
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-01-21
-- ============================================================================

-- Add ui_schema column to learning_method_types table
-- This stores the form definition as JSON schema for dynamic rendering
ALTER TABLE IF EXISTS learning_methods.learning_method_types
ADD COLUMN IF NOT EXISTS ui_schema JSONB DEFAULT NULL;

-- Index for ui_schema queries (for performance on large JSONB queries)
CREATE INDEX IF NOT EXISTS idx_lm_types_ui_schema ON learning_methods.learning_method_types USING GIN(ui_schema);

-- Add ui_schema column to learning_method_instances table
-- (for future extensibility of instance-specific schemas)
ALTER TABLE IF EXISTS learning_methods.learning_method_instances
ADD COLUMN IF NOT EXISTS ui_schema JSONB DEFAULT NULL;

CREATE INDEX IF NOT EXISTS idx_lm_instances_ui_schema ON learning_methods.learning_method_instances USING GIN(ui_schema);

-- Add ui_schema column to system_features table
-- NOTE: system_features table created in 11_System/074_system_features.sql
-- These statements moved there to avoid forward reference errors
-- DO $$
-- BEGIN
--   ALTER TABLE IF EXISTS support_systems.system_features
--   ADD COLUMN IF NOT EXISTS ui_schema JSONB DEFAULT NULL;
--
--   CREATE INDEX IF NOT EXISTS idx_system_features_ui_schema ON support_systems.system_features USING GIN(ui_schema);
-- EXCEPTION WHEN OTHERS THEN
--   -- Table doesn't exist yet - will be created in 11_System/074_system_features.sql
--   NULL;
-- END $$;

-- ============================================================================
-- SEED DATA: ui_schema for all 12 Learning Methods
-- Strategy: i18n_label/placeholder + label_fallback/placeholder_fallback
-- Frontend: try i18n key first, fall back to English default
-- ============================================================================

-- Group A: Erklärend (lm00-lm04) - Explanation Methods
UPDATE learning_methods.learning_method_types SET ui_schema = '{
  "lm_id": 0,
  "lm_name": "Tiefgehende Erklärung",
  "form_type": "dynamic",
  "language_support": ["de", "en", "pl"],
  "layout": "vertical",
  "fields": [
    {
      "name": "concept",
      "type": "text",
      "required": true,
      "i18n_label": "windows.lm00.conceptLabel",
      "i18n_placeholder": "windows.lm00.conceptPlaceholder",
      "label_fallback": "Concept",
      "placeholder_fallback": "e.g. Photosynthesis, Quantum Mechanics",
      "validation": { "min_length": 3, "max_length": 100 }
    },
    {
      "name": "explanation",
      "type": "textarea",
      "required": true,
      "i18n_label": "windows.lm00.explanationLabel",
      "i18n_placeholder": "windows.lm00.explanationPlaceholder",
      "label_fallback": "Explanation",
      "placeholder_fallback": "Detailed explanation of the concept...",
      "validation": { "min_length": 50, "max_length": 5000 }
    },
    {
      "name": "examples",
      "type": "textarea",
      "required": false,
      "i18n_label": "windows.lm00.examplesLabel",
      "i18n_placeholder": "windows.lm00.examplesPlaceholder",
      "label_fallback": "Examples",
      "placeholder_fallback": "Practical examples...",
      "validation": { "min_length": 0, "max_length": 3000 }
    }
  ]
}'::jsonb WHERE method_type = 0;

UPDATE learning_methods.learning_method_types SET ui_schema = '{
  "lm_id": 1,
  "lm_name": "Schritt-für-Schritt",
  "form_type": "dynamic",
  "language_support": ["de", "en", "pl"],
  "layout": "vertical",
  "fields": [
    {
      "name": "topic",
      "type": "text",
      "required": true,
      "i18n_label": "windows.lm01.topicLabel",
      "i18n_placeholder": "windows.lm01.topicPlaceholder",
      "label_fallback": "Topic",
      "placeholder_fallback": "What is the main topic?"
    },
    {
      "name": "steps",
      "type": "array",
      "required": true,
      "i18n_label": "windows.lm01.stepsLabel",
      "label_fallback": "Steps",
      "item_schema": {
        "type": "object",
        "fields": [
          {
            "name": "step_number",
            "type": "number",
            "required": true,
            "label_fallback": "Step Number"
          },
          {
            "name": "step_description",
            "type": "textarea",
            "required": true,
            "i18n_label": "windows.lm01.stepDescriptionLabel",
            "label_fallback": "Step Description"
          }
        ]
      }
    }
  ]
}'::jsonb WHERE method_type = 1;

UPDATE learning_methods.learning_method_types SET ui_schema = '{
  "lm_id": 2,
  "lm_name": "Interaktive Theorie",
  "form_type": "dynamic",
  "language_support": ["de", "en", "pl"],
  "layout": "vertical",
  "fields": [
    {
      "name": "theory_content",
      "type": "textarea",
      "required": true,
      "i18n_label": "windows.lm02.theoryContentLabel",
      "i18n_placeholder": "windows.lm02.theoryContentPlaceholder",
      "label_fallback": "Theory Content",
      "placeholder_fallback": "Theory explanation..."
    },
    {
      "name": "interactive_questions",
      "type": "array",
      "required": false,
      "i18n_label": "windows.lm02.questionsLabel",
      "label_fallback": "Interactive Questions"
    }
  ]
}'::jsonb WHERE method_type = 2;

UPDATE learning_methods.learning_method_types SET ui_schema = '{
  "lm_id": 3,
  "lm_name": "Diagramm/Visualisierung",
  "form_type": "dynamic",
  "language_support": ["de", "en", "pl"],
  "layout": "vertical",
  "fields": [
    {
      "name": "diagram_description",
      "type": "textarea",
      "required": true,
      "i18n_label": "windows.lm03.diagramDescriptionLabel",
      "label_fallback": "Diagram Description",
      "placeholder_fallback": "Describe the visualization..."
    },
    {
      "name": "visual_elements",
      "type": "array",
      "required": false,
      "label_fallback": "Visual Elements"
    }
  ]
}'::jsonb WHERE method_type = 3;

UPDATE learning_methods.learning_method_types SET ui_schema = '{
  "lm_id": 4,
  "lm_name": "Beispiel-Szenario",
  "form_type": "dynamic",
  "language_support": ["de", "en", "pl"],
  "layout": "vertical",
  "fields": [
    {
      "name": "scenario_title",
      "type": "text",
      "required": true,
      "i18n_label": "windows.lm04.scenarioTitleLabel",
      "label_fallback": "Scenario Title"
    },
    {
      "name": "scenario_description",
      "type": "textarea",
      "required": true,
      "i18n_label": "windows.lm04.scenarioDescriptionLabel",
      "label_fallback": "Scenario Description",
      "placeholder_fallback": "Detailed scenario..."
    },
    {
      "name": "context",
      "type": "textarea",
      "required": false,
      "i18n_label": "windows.lm04.contextLabel",
      "label_fallback": "Context"
    }
  ]
}'::jsonb WHERE method_type = 4;

-- Group B: Praxis (lm05-lm08) - Practice Methods
UPDATE learning_methods.learning_method_types SET ui_schema = '{
  "lm_id": 5,
  "lm_name": "Mathe-Interaktiv",
  "form_type": "dynamic",
  "language_support": ["de", "en", "pl"],
  "layout": "vertical",
  "fields": [
    {
      "name": "problem_statement",
      "type": "textarea",
      "required": true,
      "i18n_label": "windows.lm05.problemStatementLabel",
      "label_fallback": "Problem Statement"
    },
    {
      "name": "solution_steps",
      "type": "array",
      "required": false,
      "label_fallback": "Solution Steps"
    }
  ]
}'::jsonb WHERE method_type = 5;

UPDATE learning_methods.learning_method_types SET ui_schema = '{
  "lm_id": 6,
  "lm_name": "Flashcards",
  "form_type": "dynamic",
  "language_support": ["de", "en", "pl"],
  "layout": "vertical",
  "fields": [
    {
      "name": "cards",
      "type": "array",
      "required": true,
      "i18n_label": "windows.lm06.cardsLabel",
      "label_fallback": "Flash Cards",
      "item_schema": {
        "type": "object",
        "fields": [
          {
            "name": "front",
            "type": "text",
            "required": true,
            "label_fallback": "Front (Question)"
          },
          {
            "name": "back",
            "type": "text",
            "required": true,
            "label_fallback": "Back (Answer)"
          }
        ]
      }
    }
  ]
}'::jsonb WHERE method_type = 6;

UPDATE learning_methods.learning_method_types SET ui_schema = '{
  "lm_id": 7,
  "lm_name": "Drag & Drop",
  "form_type": "dynamic",
  "language_support": ["de", "en", "pl"],
  "layout": "vertical",
  "fields": [
    {
      "name": "instruction",
      "type": "textarea",
      "required": true,
      "i18n_label": "windows.lm07.instructionLabel",
      "label_fallback": "Instruction"
    },
    {
      "name": "pairs",
      "type": "array",
      "required": true,
      "label_fallback": "Drag & Drop Pairs"
    }
  ]
}'::jsonb WHERE method_type = 7;

UPDATE learning_methods.learning_method_types SET ui_schema = '{
  "lm_id": 8,
  "lm_name": "Lückentext",
  "form_type": "dynamic",
  "language_support": ["de", "en", "pl"],
  "layout": "vertical",
  "fields": [
    {
      "name": "text_with_blanks",
      "type": "textarea",
      "required": true,
      "i18n_label": "windows.lm08.textWithBlanksLabel",
      "label_fallback": "Text with Blanks",
      "placeholder_fallback": "Use _____ to mark blanks"
    },
    {
      "name": "solutions",
      "type": "array",
      "required": true,
      "label_fallback": "Solutions"
    }
  ]
}'::jsonb WHERE method_type = 8;

-- Group C: Prüfung (lm09-lm11) - Assessment Methods
UPDATE learning_methods.learning_method_types SET ui_schema = '{
  "lm_id": 9,
  "lm_name": "Freitext-Langantwort",
  "form_type": "dynamic",
  "language_support": ["de", "en", "pl"],
  "layout": "vertical",
  "fields": [
    {
      "name": "question",
      "type": "textarea",
      "required": true,
      "i18n_label": "windows.lm09.questionLabel",
      "label_fallback": "Question",
      "placeholder_fallback": "What is the question?"
    },
    {
      "name": "evaluation_criteria",
      "type": "textarea",
      "required": false,
      "i18n_label": "windows.lm09.evaluationCriteriaLabel",
      "label_fallback": "Evaluation Criteria",
      "placeholder_fallback": "How should answers be evaluated?"
    }
  ]
}'::jsonb WHERE method_type = 9;

UPDATE learning_methods.learning_method_types SET ui_schema = '{
  "lm_id": 10,
  "lm_name": "IHK-Stil Aufgaben",
  "form_type": "dynamic",
  "language_support": ["de", "en", "pl"],
  "layout": "vertical",
  "fields": [
    {
      "name": "task_description",
      "type": "textarea",
      "required": true,
      "i18n_label": "windows.lm10.taskDescriptionLabel",
      "label_fallback": "Task Description"
    },
    {
      "name": "rubric",
      "type": "textarea",
      "required": false,
      "label_fallback": "Grading Rubric"
    }
  ]
}'::jsonb WHERE method_type = 10;

UPDATE learning_methods.learning_method_types SET ui_schema = '{
  "lm_id": 11,
  "lm_name": "Multi-Step Praxisprüfung",
  "form_type": "dynamic",
  "language_support": ["de", "en", "pl"],
  "layout": "vertical",
  "fields": [
    {
      "name": "examination_title",
      "type": "text",
      "required": true,
      "label_fallback": "Examination Title"
    },
    {
      "name": "exam_steps",
      "type": "array",
      "required": true,
      "label_fallback": "Examination Steps"
    }
  ]
}'::jsonb WHERE method_type = 11;

-- ============================================================================
-- SEED DATA: ui_schema for selected System-Features (25 total)
-- NOTE: System-Features table created in 11_System/074_system_features.sql
-- These UPDATEs are skipped to avoid forward references
-- System-Features will be seeded when their table is created
-- ============================================================================

-- System-Features UPDATEs removed - will be seeded in 11_System/074_system_features.sql
-- See end of file for COMMENT statements that still apply
DO $$
BEGIN
  -- Placeholder: System-Features ui_schema updates
  -- Will be populated after support_systems.system_features table is created
END $$;

-- All system_features UPDATE statements removed
-- System-Features table is created in 11_System/074_system_features.sql
-- ui_schema will be seeded when that table is created
-- (Removed to avoid forward reference errors in migration ordering)

-- ============================================================================
-- COMMENT: Document the new column structure
-- ============================================================================
COMMENT ON COLUMN learning_methods.learning_method_types.ui_schema IS
'JSONB schema for dynamic form rendering. Hybrid i18n approach:
- i18n_label/placeholder: keys to resolve via vue-i18n (de, en, pl)
- label_fallback/placeholder_fallback: English defaults if key not found
Frontend: try i18n key first, fall back to English. Enables zero-file creation.
Only 12 Content-LMs (lm00-lm11) use this for forms. System-Features use it for settings.';

COMMENT ON COLUMN learning_methods.learning_method_instances.ui_schema IS
'Optional instance-specific schema override. If NULL, uses type schema from learning_method_types.
Enables course/chapter-specific customization of LM forms.';

-- Note: COMMENT ON support_systems.system_features.ui_schema omitted here
-- because the system_features table is created later in 11_System/074_system_features.sql
-- This comment will be added when that table is created.

-- ============================================================================
-- End of Migration: 078_add_ui_schema.sql
-- ============================================================================
