"""
LernsystemX KI - AI Studio Prompts

Specialized prompts for the KI-Authoring-Studio wizard steps:
- Source: PDF analysis and didactic perspectives
- Theory: Theory variant generation
- Lessons: Lesson structure generation
- Methods: Method variants per lesson
- Review: Consistency check and improvements
- Finalize: Final course blueprint generation

Phase D4 - KI-Authoring-Studio
"""

from typing import List
from flask import current_app

from app.ki.prompt_models import (
    PromptTemplate,
    PromptMessage,
    PromptVariable
)
from app.ki.prompt_registry import register_prompt


# ==============================================================================
# AI STUDIO SYSTEM PROMPT (BASE)
# ==============================================================================

AI_STUDIO_SYSTEM_BASE = """Du bist das serverseitige KI-Authoring-Modul in einem mehrstufigen Lern-Content-Studio.
Du arbeitest stets **zustandslos im Modell**, aber **zustandsbehaftet in der Datenbank / Session**, d. h. alle relevanten Informationen zum aktuellen Vorgang kommen über die API-Payload (Session, Schritt, IDs, Kontext).

## Rolle und Verantwortlichkeit

Du hast drei Kernaufgaben:

1. **Didaktische Strukturierung**
   - Aus PDF-Analysen und Metadaten didaktisch sinnvolle Strukturen ableiten:
     - Theorie-Bausteine
     - Lektionen / Lerneinheiten
     - Methoden / Aktivitäten
   - Zielgruppenorientiert (Schulform, Niveau, Fach, Vorkenntnisse).

2. **Varianten-Generierung**
   - Für jede Ebene **mehrere qualitativ unterschiedliche Varianten** generieren, z. B.:
     - 3–5 Theorie-Varianten (unterschiedliche Tiefenschärfe, Beispiele, Metaphern)
     - 3–7 Lektionen mit alternativen Schwerpunktsetzungen
     - zu jeder Lektion 2–4 Methoden-Varianten (z. B. Partnerarbeit, Gruppenarbeit, digitale Tools, Hausaufgabe)

3. **Schrittweises Arbeiten je Wizard-Step**
   - Du generierst **nie alles auf einmal**, sondern immer fokussiert auf den aktuell angeforderten Schritt.

## Allgemeine Regeln

- Schreibe in der vom Request-Kontext angegebenen Sprache (`target_language`), standardmäßig **Deutsch**.
- Nutze **klare, didaktische Sprache**: kurze Sätze, wenige verschachtelte Nebensätze.
- Fachbegriffe erklären, falls Zielgruppe ≤ Sek II bzw. Berufsschule.
- Erzeuge **strukturierten Output**: klar benannte Objekte, gut parsebare Listen & Unterpunkte.
- Du darfst **keine** Originaltexte des PDFs replizieren, sondern nur zusammenfassen, umformulieren, didaktisch transformieren.

## Stilrichtlinien

- Keine Floskeln wie "Hier ist deine Antwort".
- Keine Meta-Erklärungen über dein eigenes Modell.
- Schreibe Output so, dass er direkt serialisiert und in der DB gespeichert werden kann (JSON-Struktur).
- Wenn etwas unklar ist, löse es mit einer konkreten Annahme und dokumentiere diese im `assumptions` Feld."""


# ==============================================================================
# STEP: SOURCE - PDF Analysis
# ==============================================================================

AI_STUDIO_SOURCE_PROMPT = """Analysiere das bereitgestellte PDF-Dokument und erstelle eine didaktische Diagnose.

## Kontext
- Zielgruppe: {{target_audience}}
- Schwierigkeitsgrad: {{difficulty}}
- Sprache: {{target_language}}

## PDF-Analyse Daten
Titel: {{pdf_title}}
Inhaltsverzeichnis: {{pdf_toc}}
Abschnitte: {{pdf_sections}}
Globale Zusammenfassung: {{pdf_global_summary}}
Schlüsselbegriffe: {{pdf_keywords}}

## Aufgabe
Erstelle eine didaktische Analyse mit:
1. **Diagnose**: Domain, Komplexität, implizites Niveau, geeignete Zielgruppen
2. **Didaktische Perspektiven**: 2-4 verschiedene Ansätze, wie der Inhalt aufbereitet werden könnte
3. **Empfohlene nächste Schritte**: Konkrete Handlungsempfehlungen

## Output-Format (JSON)
{
  "step": "source",
  "diagnosis": {
    "domain": "...",
    "complexity": "niedrig|mittel|hoch",
    "implicit_level": "...",
    "suitable_for": "..."
  },
  "proposed_didactic_angles": [
    {
      "id": "angle_...",
      "title": "...",
      "description": "...",
      "risks": ["..."]
    }
  ],
  "recommended_next_actions": ["..."],
  "assumptions": ["..."],
  "internal_steps": ["SOURCE: Analysiere Dokumentstruktur", "SOURCE: Identifiziere Kernkonzepte", "SOURCE: Bewerte Zielgruppeneignung"]
}"""


# ==============================================================================
# STEP: THEORY - Theory Variants Generation
# ==============================================================================

AI_STUDIO_THEORY_PROMPT = """Generiere Theorie-Varianten basierend auf der PDF-Analyse und dem gewählten didaktischen Ansatz.

## Kontext
- Zielgruppe: {{target_audience}}
- Schwierigkeitsgrad: {{difficulty}}
- Sprache: {{target_language}}
- Lernziele: {{learning_objectives}}
- Max. Theorie-Varianten: {{max_theory_variants}}

## PDF-Analyse
{{pdf_analysis}}

## Gewählter didaktischer Ansatz
{{selected_didactic_angle}}

## Aufgabe
Erstelle {{max_theory_variants}} verschiedene Theorie-Varianten. Jede Variante soll einen anderen didaktischen Zugang bieten.

## Theorie-Varianten Schema
Jede Theorie-Variante enthält:
- `id`: stabiler, sprechender Key (z. B. `theory_variant_concept_first`)
- `title`: kurzer Titel (z. B. "Praxisnaher Einstieg über Beispiel-Szenario")
- `approach`: kurze Beschreibung des didaktischen Ansatzes
- `summary`: prägnante Zusammenfassung der Theorie (max. 150–250 Wörter)
- `structure`: Liste von inhaltlichen Unterpunkten / Subkapiteln
- `suitable_for`: Beschreibung der passenden Zielgruppe / Vorkenntnisse
- `pros`: Liste von Vorteilen
- `cons`: Liste von Nachteilen

## Output-Format (JSON)
{
  "step": "theory",
  "theory_variants": [
    {
      "id": "theory_variant_...",
      "title": "...",
      "approach": "...",
      "summary": "...",
      "structure": ["...", "..."],
      "suitable_for": "...",
      "pros": ["...", "..."],
      "cons": ["...", "..."]
    }
  ],
  "assumptions": ["..."],
  "internal_steps": ["THEORY: Relevante PDF-Sektionen filtern", "THEORY: Konzepte clustern", "THEORY: Varianten formulieren"]
}"""


# ==============================================================================
# STEP: LESSONS - Lesson Structure Generation
# ==============================================================================

AI_STUDIO_LESSONS_PROMPT = """Generiere eine Lektionen-Sequenz basierend auf der gewählten Theorie-Variante.

## Kontext
- Zielgruppe: {{target_audience}}
- Schwierigkeitsgrad: {{difficulty}}
- Sprache: {{target_language}}
- Lernziele: {{learning_objectives}}
- Max. Lektionen: {{max_lessons}}

## PDF-Analyse
{{pdf_analysis}}

## Gewählte Theorie-Variante
{{selected_theory_variant}}

## Aufgabe
Erstelle eine Sequenz von max. {{max_lessons}} Lektionen. Bei umfangreichen PDFs: Themen bündeln statt 1:1 Kapitel abbilden.

## Lektionen Schema
Jede Lektion enthält:
- `id`: z. B. `lesson_01_einfuehrung`
- `title`: Lektionstitel
- `duration`: grobe Zeiteinschätzung (z. B. "45–60 min")
- `prerequisites`: notwendige Vorkenntnisse (stichpunktartig)
- `learning_objectives`: 2–5 klare, beobachtbare Ziele ("Die Lernenden können ...")
- `content_outline`: inhaltliche Teilschritte
- `assessment_ideas`: 1–3 Ideen zur Lernstandsüberprüfung

## Output-Format (JSON)
{
  "step": "lessons",
  "lessons": [
    {
      "id": "lesson_01_...",
      "title": "...",
      "duration": "45-60 min",
      "prerequisites": ["...", "..."],
      "learning_objectives": ["Die Lernenden können ...", "..."],
      "content_outline": ["...", "..."],
      "assessment_ideas": ["...", "..."]
    }
  ],
  "assumptions": ["..."],
  "internal_steps": ["LESSONS: Themen aus Theorie extrahieren", "LESSONS: Sequenz strukturieren", "LESSONS: Lernziele formulieren"]
}"""


# ==============================================================================
# STEP: METHODS - Method Variants per Lesson
# ==============================================================================

AI_STUDIO_METHODS_PROMPT = """Generiere Methoden-Varianten für jede Lektion.

## Kontext
- Zielgruppe: {{target_audience}}
- Schwierigkeitsgrad: {{difficulty}}
- Sprache: {{target_language}}
- Methoden-Präferenzen: {{method_preferences}}

## Lektionen
{{lessons}}

## Aufgabe
Erstelle für jede Lektion 2-4 verschiedene Methoden-Varianten, die das gleiche Lernziel unterschiedlich umsetzen.

## Methoden-Varianten Schema
Jede Methoden-Variante enthält:
- `id`: z. B. `method_l1_pairwork_use_case`
- `lesson_id`: Referenz auf die Lektion
- `title`: Methodentitel
- `method_type`: z. B. "Partnerarbeit", "Gruppenarbeit", "Lehrerinput", "Stationenlernen", "Projektarbeit", "Homework"
- `description`: kurzer Ablauf
- `materials`: benötigte Materialien / Tools
- `digital_tools`: falls sinnvoll (Padlet, Miro, IDE, Lernplattform etc.)
- `steps`: nummerierte Schrittfolge (1., 2., 3., …)
- `differentiation`: konkrete Hinweise zur Binnendifferenzierung
- `evaluation`: wie der Lernerfolg beobachtet / gesichert wird

## Output-Format (JSON)
{
  "step": "methods",
  "methods": [
    {
      "id": "method_l1_...",
      "lesson_id": "lesson_01_...",
      "title": "...",
      "method_type": "Partnerarbeit|Gruppenarbeit|Lehrerinput|...",
      "description": "...",
      "materials": ["...", "..."],
      "digital_tools": ["...", "..."],
      "steps": ["1. ...", "2. ...", "3. ..."],
      "differentiation": "...",
      "evaluation": "..."
    }
  ],
  "assumptions": ["..."],
  "internal_steps": ["METHODS: Lektionen analysieren", "METHODS: Passende Methoden wählen", "METHODS: Varianten ausarbeiten"]
}"""


# ==============================================================================
# STEP: REVIEW - Consistency Check
# ==============================================================================

AI_STUDIO_REVIEW_PROMPT = """Führe einen Konsistenz-Check der generierten Inhalte durch.

## Kontext
- Zielgruppe: {{target_audience}}
- Schwierigkeitsgrad: {{difficulty}}
- Lernziele: {{learning_objectives}}

## Generierte Inhalte

### Theorie-Variante
{{selected_theory_variant}}

### Lektionen
{{lessons}}

### Methoden
{{methods}}

## Aufgabe
Prüfe:
1. Sind Lernziele durch Inhalte & Methoden abgedeckt?
2. Gibt es offensichtliche Lücken?
3. Passen Niveau + Umfang zur Zielgruppe?
4. Sind die Methoden für die Lernziele geeignet?
5. Ist die zeitliche Planung realistisch?

## Output-Format (JSON)
{
  "step": "review",
  "issues": [
    {
      "type": "scope|alignment|timing|difficulty|coverage",
      "severity": "low|medium|high",
      "target": "lesson_01|method_...|theory_...",
      "message": "..."
    }
  ],
  "improvement_suggestions": [
    {
      "target": "lesson_03",
      "action": "split|merge|add|remove|modify",
      "reason": "..."
    }
  ],
  "coverage_analysis": {
    "learning_objectives_covered": ["..."],
    "learning_objectives_uncovered": ["..."],
    "overall_alignment_score": 0.85
  },
  "assumptions": ["..."],
  "internal_steps": ["REVIEW: Lernziel-Abdeckung prüfen", "REVIEW: Niveau analysieren", "REVIEW: Verbesserungen identifizieren"]
}"""


# ==============================================================================
# STEP: FINALIZE - Final Course Blueprint
# ==============================================================================

AI_STUDIO_FINALIZE_PROMPT = """Erstelle die finale, saubere Kursstruktur.

## Kontext
- Zielgruppe: {{target_audience}}
- Schwierigkeitsgrad: {{difficulty}}
- Sprache: {{target_language}}
- Lernziele: {{learning_objectives}}

## Überprüfte Inhalte

### Theorie
{{selected_theory_variant}}

### Lektionen
{{lessons}}

### Methoden
{{methods}}

### Review-Ergebnisse
{{review_results}}

## Aufgabe
Erstelle die finale, saubere Struktur zur Speicherung / zum Export.
- Alle IDs verknüpft
- Lücken aus dem Review adressiert
- Konsistente Formatierung

## Output-Format (JSON)
{
  "step": "finalize",
  "course_blueprint": {
    "meta": {
      "title": "...",
      "description": "...",
      "target_audience": "...",
      "difficulty": "...",
      "language": "...",
      "estimated_duration": "...",
      "learning_objectives": ["..."]
    },
    "theory": {
      "id": "...",
      "title": "...",
      "approach": "...",
      "summary": "...",
      "structure": ["..."]
    },
    "lessons": [
      {
        "id": "...",
        "title": "...",
        "duration": "...",
        "prerequisites": ["..."],
        "learning_objectives": ["..."],
        "content_outline": ["..."],
        "recommended_method_id": "..."
      }
    ],
    "methods": [
      {
        "id": "...",
        "lesson_id": "...",
        "title": "...",
        "method_type": "...",
        "description": "...",
        "steps": ["..."]
      }
    ]
  },
  "export_ready": true,
  "assumptions": ["..."],
  "internal_steps": ["FINALIZE: Struktur konsolidieren", "FINALIZE: IDs verknüpfen", "FINALIZE: Blueprint erstellen"]
}"""


def init_ai_studio_prompts() -> None:
    """
    Initialize AI Studio prompt templates.

    Registers templates for all 6 wizard steps:
    - ai_studio_source: PDF analysis and didactic perspectives
    - ai_studio_theory: Theory variant generation
    - ai_studio_lessons: Lesson structure generation
    - ai_studio_methods: Method variants per lesson
    - ai_studio_review: Consistency check
    - ai_studio_finalize: Final blueprint generation

    Called during application initialization.
    """
    current_app.logger.info("Initializing AI Studio prompt templates...")

    # =========================================================================
    # 1. SOURCE - PDF Analysis
    # =========================================================================
    ai_studio_source = PromptTemplate(
        code="ai_studio_source",
        title="KI-Studio: Quellen-Analyse",
        description=(
            "Analysiert PDF-Dokumente und erstellt didaktische Diagnosen "
            "mit verschiedenen Perspektiven für die Aufbereitung."
        ),
        version=1,
        tags=["ai-studio", "authoring", "pdf-analysis", "source"],
        messages=[
            PromptMessage(
                role="system",
                content=AI_STUDIO_SYSTEM_BASE
            ),
            PromptMessage(
                role="user",
                content=AI_STUDIO_SOURCE_PROMPT
            )
        ],
        variables=[
            PromptVariable(name="target_audience", description="Zielgruppe", required=True),
            PromptVariable(name="difficulty", description="Schwierigkeitsgrad", required=True),
            PromptVariable(name="target_language", description="Zielsprache", required=False, default="de"),
            PromptVariable(name="pdf_title", description="PDF Titel", required=True),
            PromptVariable(name="pdf_toc", description="PDF Inhaltsverzeichnis (JSON)", required=False, default="[]"),
            PromptVariable(name="pdf_sections", description="PDF Abschnitte (JSON)", required=True),
            PromptVariable(name="pdf_global_summary", description="Globale Zusammenfassung", required=True),
            PromptVariable(name="pdf_keywords", description="Schlüsselbegriffe (JSON)", required=True)
        ],
        model="claude-3-5-sonnet-20241022",
        max_tokens=4000,
        temperature=0.7,
        language_mode="target",
        allowed_roles=["teacher", "admin"],
        created_by="system"
    )
    register_prompt(ai_studio_source)

    # =========================================================================
    # 2. THEORY - Theory Variants
    # =========================================================================
    ai_studio_theory = PromptTemplate(
        code="ai_studio_theory",
        title="KI-Studio: Theorie-Varianten",
        description=(
            "Generiert verschiedene Theorie-Varianten mit unterschiedlichen "
            "didaktischen Zugängen und Schwerpunkten."
        ),
        version=1,
        tags=["ai-studio", "authoring", "theory", "variants"],
        messages=[
            PromptMessage(
                role="system",
                content=AI_STUDIO_SYSTEM_BASE
            ),
            PromptMessage(
                role="user",
                content=AI_STUDIO_THEORY_PROMPT
            )
        ],
        variables=[
            PromptVariable(name="target_audience", description="Zielgruppe", required=True),
            PromptVariable(name="difficulty", description="Schwierigkeitsgrad", required=True),
            PromptVariable(name="target_language", description="Zielsprache", required=False, default="de"),
            PromptVariable(name="learning_objectives", description="Lernziele (JSON)", required=False, default="[]"),
            PromptVariable(name="max_theory_variants", description="Max. Anzahl Theorie-Varianten", required=False, default="4"),
            PromptVariable(name="pdf_analysis", description="PDF-Analyse Ergebnisse (JSON)", required=True),
            PromptVariable(name="selected_didactic_angle", description="Gewählter didaktischer Ansatz", required=False, default="")
        ],
        model="claude-3-5-sonnet-20241022",
        max_tokens=6000,
        temperature=0.8,
        language_mode="target",
        allowed_roles=["teacher", "admin"],
        created_by="system"
    )
    register_prompt(ai_studio_theory)

    # =========================================================================
    # 3. LESSONS - Lesson Structure
    # =========================================================================
    ai_studio_lessons = PromptTemplate(
        code="ai_studio_lessons",
        title="KI-Studio: Lektionen-Struktur",
        description=(
            "Generiert eine Sequenz von Lektionen basierend auf der "
            "gewählten Theorie-Variante und PDF-Struktur."
        ),
        version=1,
        tags=["ai-studio", "authoring", "lessons", "structure"],
        messages=[
            PromptMessage(
                role="system",
                content=AI_STUDIO_SYSTEM_BASE
            ),
            PromptMessage(
                role="user",
                content=AI_STUDIO_LESSONS_PROMPT
            )
        ],
        variables=[
            PromptVariable(name="target_audience", description="Zielgruppe", required=True),
            PromptVariable(name="difficulty", description="Schwierigkeitsgrad", required=True),
            PromptVariable(name="target_language", description="Zielsprache", required=False, default="de"),
            PromptVariable(name="learning_objectives", description="Lernziele (JSON)", required=False, default="[]"),
            PromptVariable(name="max_lessons", description="Max. Anzahl Lektionen", required=False, default="5"),
            PromptVariable(name="pdf_analysis", description="PDF-Analyse Ergebnisse (JSON)", required=True),
            PromptVariable(name="selected_theory_variant", description="Gewählte Theorie-Variante (JSON)", required=True)
        ],
        model="claude-3-5-sonnet-20241022",
        max_tokens=8000,
        temperature=0.7,
        language_mode="target",
        allowed_roles=["teacher", "admin"],
        created_by="system"
    )
    register_prompt(ai_studio_lessons)

    # =========================================================================
    # 4. METHODS - Method Variants
    # =========================================================================
    ai_studio_methods = PromptTemplate(
        code="ai_studio_methods",
        title="KI-Studio: Methoden-Varianten",
        description=(
            "Generiert verschiedene Methoden-Varianten für jede Lektion "
            "mit unterschiedlichen didaktischen Ansätzen."
        ),
        version=1,
        tags=["ai-studio", "authoring", "methods", "variants"],
        messages=[
            PromptMessage(
                role="system",
                content=AI_STUDIO_SYSTEM_BASE
            ),
            PromptMessage(
                role="user",
                content=AI_STUDIO_METHODS_PROMPT
            )
        ],
        variables=[
            PromptVariable(name="target_audience", description="Zielgruppe", required=True),
            PromptVariable(name="difficulty", description="Schwierigkeitsgrad", required=True),
            PromptVariable(name="target_language", description="Zielsprache", required=False, default="de"),
            PromptVariable(name="method_preferences", description="Methoden-Präferenzen (JSON)", required=False, default="[]"),
            PromptVariable(name="lessons", description="Lektionen (JSON)", required=True)
        ],
        model="claude-3-5-sonnet-20241022",
        max_tokens=10000,
        temperature=0.8,
        language_mode="target",
        allowed_roles=["teacher", "admin"],
        created_by="system"
    )
    register_prompt(ai_studio_methods)

    # =========================================================================
    # 5. REVIEW - Consistency Check
    # =========================================================================
    ai_studio_review = PromptTemplate(
        code="ai_studio_review",
        title="KI-Studio: Review & Konsistenz",
        description=(
            "Prüft die Konsistenz der generierten Inhalte und identifiziert "
            "Verbesserungspotenziale."
        ),
        version=1,
        tags=["ai-studio", "authoring", "review", "consistency"],
        messages=[
            PromptMessage(
                role="system",
                content=AI_STUDIO_SYSTEM_BASE
            ),
            PromptMessage(
                role="user",
                content=AI_STUDIO_REVIEW_PROMPT
            )
        ],
        variables=[
            PromptVariable(name="target_audience", description="Zielgruppe", required=True),
            PromptVariable(name="difficulty", description="Schwierigkeitsgrad", required=True),
            PromptVariable(name="learning_objectives", description="Lernziele (JSON)", required=False, default="[]"),
            PromptVariable(name="selected_theory_variant", description="Gewählte Theorie-Variante (JSON)", required=True),
            PromptVariable(name="lessons", description="Lektionen (JSON)", required=True),
            PromptVariable(name="methods", description="Methoden (JSON)", required=True)
        ],
        model="claude-3-5-sonnet-20241022",
        max_tokens=4000,
        temperature=0.5,
        language_mode="target",
        allowed_roles=["teacher", "admin"],
        created_by="system"
    )
    register_prompt(ai_studio_review)

    # =========================================================================
    # 6. FINALIZE - Final Blueprint
    # =========================================================================
    ai_studio_finalize = PromptTemplate(
        code="ai_studio_finalize",
        title="KI-Studio: Finalisierung",
        description=(
            "Erstellt die finale, saubere Kursstruktur zur Speicherung "
            "und zum Export."
        ),
        version=1,
        tags=["ai-studio", "authoring", "finalize", "export"],
        messages=[
            PromptMessage(
                role="system",
                content=AI_STUDIO_SYSTEM_BASE
            ),
            PromptMessage(
                role="user",
                content=AI_STUDIO_FINALIZE_PROMPT
            )
        ],
        variables=[
            PromptVariable(name="target_audience", description="Zielgruppe", required=True),
            PromptVariable(name="difficulty", description="Schwierigkeitsgrad", required=True),
            PromptVariable(name="target_language", description="Zielsprache", required=False, default="de"),
            PromptVariable(name="learning_objectives", description="Lernziele (JSON)", required=False, default="[]"),
            PromptVariable(name="selected_theory_variant", description="Gewählte Theorie-Variante (JSON)", required=True),
            PromptVariable(name="lessons", description="Lektionen (JSON)", required=True),
            PromptVariable(name="methods", description="Methoden (JSON)", required=True),
            PromptVariable(name="review_results", description="Review-Ergebnisse (JSON)", required=True)
        ],
        model="claude-3-5-sonnet-20241022",
        max_tokens=12000,
        temperature=0.5,
        language_mode="target",
        allowed_roles=["teacher", "admin"],
        created_by="system"
    )
    register_prompt(ai_studio_finalize)

    current_app.logger.info("Registered 6 AI Studio prompt templates")


# List of all AI Studio prompt codes
AI_STUDIO_PROMPT_CODES: List[str] = [
    "ai_studio_source",
    "ai_studio_theory",
    "ai_studio_lessons",
    "ai_studio_methods",
    "ai_studio_review",
    "ai_studio_finalize"
]
