"""
LernsystemX KI - AI Editor Source Step Prompt

PDF analysis and didactic perspectives generation.
"""

from app.domain.ai.configuration.prompts.models import PromptTemplate, PromptMessage, PromptVariable
from app.domain.ai.configuration.prompts.registry import register_prompt
from ._base import AI_EDITOR_SYSTEM_BASE


AI_EDITOR_SOURCE_PROMPT = """Analysiere das bereitgestellte PDF-Dokument und erstelle eine didaktische Diagnose.

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


def init_source_prompt() -> None:
    """Initialize the SOURCE step prompt template."""
    ai_editor_source = PromptTemplate(
        code="ai_editor_source",
        title="KI-Studio: Quellen-Analyse",
        description=(
            "Analysiert PDF-Dokumente und erstellt didaktische Diagnosen "
            "mit verschiedenen Perspektiven für die Aufbereitung."
        ),
        version=1,
        tags=["ai-editor", "authoring", "pdf-analysis", "source"],
        messages=[
            PromptMessage(
                role="system",
                content=AI_EDITOR_SYSTEM_BASE
            ),
            PromptMessage(
                role="user",
                content=AI_EDITOR_SOURCE_PROMPT
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
    register_prompt(ai_editor_source)
