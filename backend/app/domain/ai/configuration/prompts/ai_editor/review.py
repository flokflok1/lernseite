"""
LernsystemX KI - AI Editor Review Step Prompt

Consistency check and improvement suggestions.
"""

from app.domain.ai.configuration.prompts.models import PromptTemplate, PromptMessage, PromptVariable
from app.domain.ai.configuration.prompts.registry import register_prompt
from ._base import AI_EDITOR_SYSTEM_BASE


AI_EDITOR_REVIEW_PROMPT = """Führe einen Konsistenz-Check der generierten Inhalte durch.

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


def init_review_prompt() -> None:
    """Initialize the REVIEW step prompt template."""
    ai_editor_review = PromptTemplate(
        code="ai_editor_review",
        title="KI-Studio: Review & Konsistenz",
        description=(
            "Prüft die Konsistenz der generierten Inhalte und identifiziert "
            "Verbesserungspotenziale."
        ),
        version=1,
        tags=["ai-editor", "authoring", "review", "consistency"],
        messages=[
            PromptMessage(
                role="system",
                content=AI_EDITOR_SYSTEM_BASE
            ),
            PromptMessage(
                role="user",
                content=AI_EDITOR_REVIEW_PROMPT
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
        temperature=0.5,
        language_mode="target",
        allowed_roles=["teacher", "admin"],
        created_by="system"
    )
    register_prompt(ai_editor_review)
