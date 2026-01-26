-- ============================================================================
-- Seed Data: Prompt Templates for AI Content Generation
-- Description: Default prompt templates for content generation (theory, lessons, quizzes)
-- Source: 062_prompt_templates.sql
-- Author: LernsystemX Migration System
-- Date: 2026-01-26
-- Phase: 4 (Seed Data)
-- ============================================================================

-- ============================================================================
-- Theory Sheet Templates (4 styles: ADHS, Detailed, Short, Exam)
-- ============================================================================

INSERT INTO ai_pipeline.prompt_templates (
    code, category, style, title, description, icon,
    system_prompt, user_prompt_template,
    variables, output_format, output_schema,
    tts_enabled, target_audience, is_default, is_system
) VALUES
-- ADHS-freundlich (Default)
(
    'theory_sheet_adhs',
    'theory',
    'adhs',
    'Theorieblatt (ADHS-freundlich)',
    'Kurze, visuelle Erklaerungen mit klarer Struktur. Ideal fuer schnelles Erfassen.',
    '🧠',
    'Du bist ein erfahrener IT-Ausbilder, spezialisiert auf ADHS-freundliches Lernen.
Deine Erklaerungen sind:
- KURZ und praegnant (max. 2-3 Saetze pro Punkt)
- VISUELL strukturiert mit Aufzaehlungen und Emojis
- SCHRITTWEISE aufgebaut
- Mit KONKRETEN Beispielen
- Ohne Fachjargon (oder sofort erklaert)

Antworte NUR mit validem JSON.',
    'Erstelle ein ADHS-freundliches Theorieblatt fuer das Kapitel "{{chapter_title}}" im Kurs "{{course_title}}".

Kapitel-Beschreibung: {{chapter_description}}
Lektionen: {{lesson_titles}}
Zielgruppe: {{target_audience}}

JSON-Struktur:
{
    "overview": "Kurze Uebersicht (2-3 Saetze, was lernst du hier?)",
    "learningGoals": ["Ziel 1 (kurz!)", "Ziel 2", ...],
    "concepts": [
        {
            "title": "Konzept-Name",
            "emoji": "passendes Emoji",
            "oneLiner": "Erklaerung in EINEM Satz",
            "example": "Konkretes Beispiel",
            "tip": "Merkhilfe oder Eselsbruecke"
        }
    ],
    "terms": [
        {
            "term": "Fachbegriff",
            "simple": "Einfache Erklaerung (wie fuer 10-Jaehrigen)",
            "example": "Beispiel aus dem Alltag"
        }
    ],
    "examTips": ["Pruefungstipp 1", "Pruefungstipp 2"],
    "summary": "3 Bullet Points: Das Wichtigste auf einen Blick"
}',
    '[
        {"name": "chapter_title", "required": true, "description": "Titel des Kapitels"},
        {"name": "course_title", "required": true, "description": "Titel des Kurses"},
        {"name": "chapter_description", "required": false, "description": "Beschreibung des Kapitels"},
        {"name": "lesson_titles", "required": false, "description": "Titel der Lektionen"},
        {"name": "target_audience", "required": false, "default": "Fachinformatiker Systemintegration"}
    ]'::jsonb,
    'json',
    '{
        "type": "object",
        "required": ["overview", "learningGoals", "concepts", "terms", "examTips", "summary"],
        "properties": {
            "overview": {"type": "string"},
            "learningGoals": {"type": "array", "items": {"type": "string"}},
            "concepts": {"type": "array"},
            "terms": {"type": "array"},
            "examTips": {"type": "array", "items": {"type": "string"}},
            "summary": {"type": "string"}
        }
    }'::jsonb,
    true,
    'Fachinformatiker Systemintegration (FISI)',
    true,
    true
),

-- Ausfuehrlich
(
    'theory_sheet_detailed',
    'theory',
    'detailed',
    'Theorieblatt (Ausfuehrlich)',
    'Umfassende Erklaerungen mit allen Details. Ideal zum tiefen Verstaendnis.',
    '📚',
    'Du bist ein erfahrener IT-Ausbilder mit akademischem Hintergrund.
Erstelle ausfuehrliche, gut strukturierte Lerninhalte mit:
- Vollstaendigen Erklaerungen aller Konzepte
- Hintergrundwissen und Zusammenhaengen
- Mehreren Beispielen pro Konzept
- Formeln und Berechnungswegen (wo relevant)
- Verweisen auf weitere Themen

Antworte NUR mit validem JSON.',
    'Erstelle ein ausfuehrliches Theorieblatt fuer das Kapitel "{{chapter_title}}" im Kurs "{{course_title}}".

Kapitel-Beschreibung: {{chapter_description}}
Lektionen: {{lesson_titles}}
Zielgruppe: {{target_audience}}

JSON-Struktur:
{
    "overview": "Ausfuehrliche Uebersicht mit Einordnung ins Gesamtthema",
    "learningGoals": ["Detailliertes Lernziel 1", "Lernziel 2", ...],
    "prerequisites": ["Vorwissen 1", "Vorwissen 2"],
    "concepts": [
        {
            "title": "Konzept-Name",
            "description": "Ausfuehrliche Erklaerung (mehrere Saetze)",
            "background": "Hintergrund und Kontext",
            "formula": "Formel falls relevant",
            "examples": ["Beispiel 1", "Beispiel 2"],
            "commonMistakes": ["Haeufiger Fehler 1"],
            "relatedTopics": ["Verwandtes Thema 1"]
        }
    ],
    "terms": [
        {
            "term": "Fachbegriff",
            "definition": "Vollstaendige Definition",
            "etymology": "Wortherkunft (optional)",
            "usage": "Verwendung im Kontext"
        }
    ],
    "examRelevance": "Detaillierte Erklaerung zur Pruefungsrelevanz mit typischen Aufgabentypen",
    "furtherReading": ["Weiterführende Ressource 1"],
    "summary": "Zusammenfassung aller wichtigen Punkte"
}',
    '[
        {"name": "chapter_title", "required": true, "description": "Titel des Kapitels"},
        {"name": "course_title", "required": true, "description": "Titel des Kurses"},
        {"name": "chapter_description", "required": false, "description": "Beschreibung des Kapitels"},
        {"name": "lesson_titles", "required": false, "description": "Titel der Lektionen"},
        {"name": "target_audience", "required": false, "default": "Fachinformatiker Systemintegration"}
    ]'::jsonb,
    'json',
    NULL,
    true,
    'Fachinformatiker Systemintegration (FISI)',
    false,
    true
),

-- Kurz & Knapp
(
    'theory_sheet_short',
    'theory',
    'short',
    'Theorieblatt (Kurz & Knapp)',
    'Nur das Wichtigste auf einen Blick. Ideal zur Wiederholung.',
    '⚡',
    'Du bist ein IT-Ausbilder, der auf Effizienz setzt.
Erstelle extrem kompakte Zusammenfassungen:
- Maximal 5 Kernpunkte
- Jeder Punkt in einem Satz
- Nur pruefungsrelevante Inhalte
- Keine Beispiele, nur Fakten

Antworte NUR mit validem JSON.',
    'Erstelle eine Kurzuebersicht fuer das Kapitel "{{chapter_title}}".

JSON-Struktur:
{
    "title": "Kapiteltitel",
    "keyPoints": ["Kernpunkt 1", "Kernpunkt 2", "Kernpunkt 3", "Kernpunkt 4", "Kernpunkt 5"],
    "mustKnowTerms": [{"term": "Begriff", "definition": "Ein-Satz-Definition"}],
    "examFormula": "Wichtigste Formel (falls relevant)",
    "oneMinuteSummary": "Das Kapitel in 60 Sekunden erklaert"
}',
    '[
        {"name": "chapter_title", "required": true, "description": "Titel des Kapitels"}
    ]'::jsonb,
    'json',
    NULL,
    true,
    'Fachinformatiker Systemintegration (FISI)',
    false,
    true
),

-- Pruefungsfokus
(
    'theory_sheet_exam',
    'theory',
    'exam_focus',
    'Theorieblatt (Pruefungsfokus)',
    'Optimiert fuer IHK-Pruefungsvorbereitung. Was kommt dran?',
    '🎯',
    'Du bist ein IHK-Pruefer und kennst die AP1-Pruefung genau.
Erstelle Lerninhalte mit klarem Pruefungsfokus:
- Was wird WIRKLICH geprueft?
- Typische Aufgabenstellungen
- Punkteverteilung beachten
- Haeufige Fehler vermeiden
- Zeitmanagement-Tipps

Antworte NUR mit validem JSON.',
    'Erstelle ein pruefungsfokussiertes Theorieblatt fuer "{{chapter_title}}".

JSON-Struktur:
{
    "examRelevance": "HOCH/MITTEL/NIEDRIG",
    "typicalPoints": "Wie viele Punkte gibt es typischerweise?",
    "mustKnow": ["Das MUSS sitzen 1", "Das MUSS sitzen 2"],
    "typicalTasks": [
        {
            "type": "Aufgabentyp (z.B. Berechnung, Erklaerung)",
            "example": "Beispielaufgabe",
            "solution": "Loesungsweg",
            "points": "Typische Punktzahl",
            "timeMinutes": "Empfohlene Zeit"
        }
    ],
    "commonMistakes": [
        {
            "mistake": "Haeufiger Fehler",
            "consequence": "Punktabzug",
            "howToAvoid": "So vermeidest du ihn"
        }
    ],
    "examTips": ["Pruefungstipp 1", "Pruefungstipp 2"],
    "lastMinuteChecklist": ["Vor der Pruefung checken 1", "Checken 2"]
}',
    '[
        {"name": "chapter_title", "required": true, "description": "Titel des Kapitels"}
    ]'::jsonb,
    'json',
    NULL,
    true,
    'Fachinformatiker Systemintegration (FISI) - IHK AP1',
    false,
    true
)
ON CONFLICT (code) DO UPDATE SET
    title = EXCLUDED.title,
    description = EXCLUDED.description,
    icon = EXCLUDED.icon,
    system_prompt = EXCLUDED.system_prompt,
    user_prompt_template = EXCLUDED.user_prompt_template,
    variables = EXCLUDED.variables,
    output_schema = EXCLUDED.output_schema,
    tts_enabled = EXCLUDED.tts_enabled,
    is_default = EXCLUDED.is_default,
    updated_at = NOW();

-- ============================================================================
-- Lesson Steps Templates
-- ============================================================================

INSERT INTO ai_pipeline.prompt_templates (
    code, category, style, title, description, icon,
    system_prompt, user_prompt_template,
    variables, output_format,
    tts_enabled, target_audience, is_default, is_system
) VALUES
(
    'lesson_steps_adhs',
    'lesson',
    'adhs',
    'Lektions-Erklaerung (ADHS-freundlich)',
    'Schritt-fuer-Schritt mit Taschenrechner-Anleitung',
    '🧮',
    'Du bist ein geduldiger Tutor, der komplexe Themen in kleine Haeppchen zerlegt.
Jeder Schritt muss:
- In 1-2 Saetzen erklaert sein
- Eine klare Aktion haben
- Visuelles Feedback geben (Schema/Formel)

Antworte NUR mit validem JSON.',
    'Erstelle eine Schritt-fuer-Schritt Erklaerung fuer die Lektion "{{lesson_title}}" (Lernmethode: {{lm_type}}).

JSON-Struktur:
{
    "steps": [
        {
            "stepNumber": 1,
            "title": "Kurzer Titel",
            "speech": "Was der Tutor sagt (freundlich, motivierend)",
            "action": "Was der User tun soll",
            "calculator": "Taschenrechner-Eingabe (z.B. 960 * 80.14)",
            "result": "Erwartetes Ergebnis",
            "schema": [
                {"label": "Zeile", "operator": "+/-/=", "value": "Wert", "highlight": false}
            ],
            "tip": "Hilfreicher Tipp (optional)"
        }
    ],
    "totalSteps": 5,
    "estimatedMinutes": 10
}',
    '[
        {"name": "lesson_title", "required": true, "description": "Titel der Lektion"},
        {"name": "lm_type", "required": false, "default": "LM00", "description": "Lernmethoden-Typ"}
    ]'::jsonb,
    'json',
    true,
    'Fachinformatiker Systemintegration (FISI)',
    true,
    true
)
ON CONFLICT (code) DO UPDATE SET
    title = EXCLUDED.title,
    description = EXCLUDED.description,
    icon = EXCLUDED.icon,
    system_prompt = EXCLUDED.system_prompt,
    user_prompt_template = EXCLUDED.user_prompt_template,
    variables = EXCLUDED.variables,
    tts_enabled = EXCLUDED.tts_enabled,
    is_default = EXCLUDED.is_default,
    updated_at = NOW();

-- ============================================================================
-- Verification
-- ============================================================================

SELECT COUNT(*) as total_prompt_templates FROM ai_pipeline.prompt_templates;
