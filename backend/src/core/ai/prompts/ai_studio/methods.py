"""
LernsystemX KI - AI Studio Methods Step Prompt

Method variants generation for each lesson.
"""

from src.ki.prompt_models import PromptTemplate, PromptMessage, PromptVariable
from src.ki.prompts.registry import register_prompt
from ._base import AI_STUDIO_SYSTEM_BASE


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


def init_methods_prompt() -> None:
    """Initialize the METHODS step prompt template."""
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
