"""
LernsystemX KI - AI Editor Finalize Step Prompt

Final course blueprint generation.
"""

from app.domain.ai.configuration.prompts.models import PromptTemplate, PromptMessage, PromptVariable
from app.domain.ai.configuration.prompts.registry import register_prompt
from ._base import AI_EDITOR_SYSTEM_BASE


AI_EDITOR_FINALIZE_PROMPT = """Erstelle die finale, saubere Kursstruktur.

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


def init_finalize_prompt() -> None:
    """Initialize the FINALIZE step prompt template."""
    ai_editor_finalize = PromptTemplate(
        code="ai_editor_finalize",
        title="KI-Studio: Finalisierung",
        description=(
            "Erstellt die finale, saubere Kursstruktur zur Speicherung "
            "und zum Export."
        ),
        version=1,
        tags=["ai-editor", "authoring", "finalize", "export"],
        messages=[
            PromptMessage(
                role="system",
                content=AI_EDITOR_SYSTEM_BASE
            ),
            PromptMessage(
                role="user",
                content=AI_EDITOR_FINALIZE_PROMPT
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
        temperature=0.5,
        language_mode="target",
        allowed_roles=["teacher", "admin"],
        created_by="system"
    )
    register_prompt(ai_editor_finalize)
