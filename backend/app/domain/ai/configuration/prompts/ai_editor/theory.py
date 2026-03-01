"""
LernsystemX KI - AI Editor Theory Step Prompt

Theory variant generation with different didactic approaches.
"""

from app.domain.ai.configuration.prompts.models import PromptTemplate, PromptMessage, PromptVariable
from app.domain.ai.configuration.prompts.registry import register_prompt
from ._base import AI_EDITOR_SYSTEM_BASE


AI_EDITOR_THEORY_PROMPT = """Generiere Theorie-Varianten basierend auf der PDF-Analyse und dem gewählten didaktischen Ansatz.

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


def init_theory_prompt() -> None:
    """Initialize the THEORY step prompt template."""
    ai_editor_theory = PromptTemplate(
        code="ai_editor_theory",
        title="KI-Studio: Theorie-Varianten",
        description=(
            "Generiert verschiedene Theorie-Varianten mit unterschiedlichen "
            "didaktischen Zugängen und Schwerpunkten."
        ),
        version=1,
        tags=["ai-editor", "authoring", "theory", "variants"],
        messages=[
            PromptMessage(
                role="system",
                content=AI_EDITOR_SYSTEM_BASE
            ),
            PromptMessage(
                role="user",
                content=AI_EDITOR_THEORY_PROMPT
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
        temperature=0.8,
        language_mode="target",
        allowed_roles=["teacher", "admin"],
        created_by="system"
    )
    register_prompt(ai_editor_theory)
