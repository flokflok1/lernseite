"""
Multi-step generation pipeline for course authoring.

When QualityProfile.pipeline_enabled=True, large generation tasks
are broken into focused steps: structure -> content -> methods.
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


STEP_PROMPTS = {
    'structure': (
        "\n\nAKTUELLER SCHRITT: NUR STRUKTUR.\n"
        "Erstelle Kapitel (add_chapter) und Lektionen (add_lesson) mit kurzem "
        "Platzhalter-Text in content.content_html. KEINE Lernmethoden in diesem Schritt."
    ),
    'content': (
        "\n\nAKTUELLER SCHRITT: NUR THEORIE-INHALTE.\n"
        "Verwende update_lesson um content.content_html mit vollstaendigem "
        "HTML-Theorieblatt zu fuellen. KEINE neuen Kapitel oder Methoden."
    ),
    'methods': (
        "\n\nAKTUELLER SCHRITT: NUR LERNMETHODEN.\n"
        "Verwende add_method fuer jede Lektion. KEINE neuen Kapitel oder "
        "Lektionen. IMMER vollstaendige Inhalte und Loesungen."
    ),
}


class GenerationPipeline:
    """Orchestrates multi-step course generation."""

    @classmethod
    def determine_step(cls, structure: Dict) -> str:
        """Auto-detect which step is needed next."""
        chapters = structure.get('chapters', [])
        if not chapters:
            return 'structure'

        total = 0
        needs_content = 0
        needs_methods = 0

        for ch in chapters:
            for ls in ch.get('lessons', []):
                total += 1
                content = ls.get('content', {})
                raw = (
                    content.get('content_html') or content.get('raw_text', '')
                ) if isinstance(content, dict) else ''
                if len(raw) < 200:
                    needs_content += 1
                elif not ls.get('methods'):
                    needs_methods += 1

        if total == 0:
            return 'structure'
        if needs_content > total * 0.5:
            return 'content'
        if needs_methods > 0:
            return 'methods'
        return 'complete'

    @classmethod
    def get_step_prompt(cls, step: str) -> Optional[str]:
        """Get prompt suffix for a pipeline step."""
        return STEP_PROMPTS.get(step)

    @classmethod
    def get_focused_chapters(
        cls, structure: Dict, step: str, batch_size: int = 3
    ) -> List[str]:
        """Get chapter IDs needing work for this step."""
        result = []
        for ch in structure.get('chapters', []):
            needs = False
            for ls in ch.get('lessons', []):
                content = ls.get('content', {})
                raw = (
                    (content.get('content_html') or content.get('raw_text', ''))
                    if isinstance(content, dict) else ''
                )
                if step == 'content' and len(raw) < 200:
                    needs = True
                    break
                if step == 'methods' and not ls.get('methods'):
                    needs = True
                    break
            if needs:
                result.append(ch.get('id'))
            if len(result) >= batch_size:
                break
        return result
