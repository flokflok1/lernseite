"""
LernsystemX KI - AI Editor Lessons Step Prompt

Lesson structure generation based on selected theory variant.
"""

from app.ai.configuration.prompt_models import PromptTemplate, PromptMessage, PromptVariable
from app.ai.configuration.prompts.registry import register_prompt
from ._base import AI_EDITOR_SYSTEM_BASE


AI_EDITOR_LESSONS_PROMPT = """Generiere eine Lektionen-Sequenz basierend auf der gewählten Theorie-Variante.

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


def init_lessons_prompt() -> None:
    """Initialize the LESSONS step prompt template."""
    ai_editor_lessons = PromptTemplate(
        code="ai_editor_lessons",
        title="KI-Studio: Lektionen-Struktur",
        description=(
            "Generiert eine Sequenz von Lektionen basierend auf der "
            "gewählten Theorie-Variante und PDF-Struktur."
        ),
        version=1,
        tags=["ai-editor", "authoring", "lessons", "structure"],
        messages=[
            PromptMessage(
                role="system",
                content=AI_EDITOR_SYSTEM_BASE
            ),
            PromptMessage(
                role="user",
                content=AI_EDITOR_LESSONS_PROMPT
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
    register_prompt(ai_editor_lessons)
