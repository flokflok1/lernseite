"""
Web Research Service

Infrastructure service for searching and summarizing web content.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class WebSearchService:
    """Search the web for learning content and summarize results."""

    @staticmethod
    def search_and_summarize(
        query: str,
        context: str = '',
        provider: str = None,
        model: str = None,
        max_results: int = 3,
    ) -> Dict[str, Any]:
        """Use AI to generate a learning summary for a topic.

        Since we don't have a web search API integrated yet, this uses
        AI knowledge to generate learning content based on the query.
        The content is clearly marked as AI-generated, not from live web.

        Args:
            query: Search query / topic description.
            context: Additional context (objectives, etc.).
            provider: Optional AI provider.
            model: Optional AI model.
            max_results: Not used yet (for future web API integration).

        Returns:
            Dict with summary, key_points, source info.
        """
        from app.infrastructure.ai.adapter import AIAdapter

        prompt = _build_prompt(query, context)
        ai_opts = {k: v for k, v in {'provider': provider, 'model': model}.items() if v}

        try:
            adapter = AIAdapter(**ai_opts)
            response = adapter.send_request(
                prompt=prompt,
                temperature=0.3,
                max_tokens=4000,
            )
            return _parse_response(response, query)

        except Exception:
            logger.exception("Web research failed for query: %s", query[:100])
            return {
                'summary': f'Lerninhalt für "{query}" konnte nicht generiert werden.',
                'key_points': [],
                'source': 'error',
                'source_label': 'Fehler bei der Generierung',
            }


def _build_prompt(query: str, context: str) -> str:
    """Build the AI prompt for learning content generation."""
    prompt = (
        "Du bist ein Experte für IT-Ausbildung (IHK Fachinformatiker). "
        "Erstelle eine kompakte Lernzusammenfassung zum folgenden Thema.\n\n"
        f"Thema: {query}\n"
    )
    if context:
        prompt += f"\nKontext/Lernziele:\n{context}\n"

    prompt += (
        "\nAntwort als JSON:\n"
        '{"summary": "Zusammenfassung (200-400 Wörter)", '
        '"key_points": ["Kernpunkt 1", "Kernpunkt 2", ...], '
        '"difficulty_level": "kennen|anwenden|beherrschen", '
        '"recommended_study_time_minutes": 15}'
    )
    return prompt


def _parse_response(response: Dict[str, Any], query: str) -> Dict[str, Any]:
    """Parse the AI response into a structured result dict."""
    import json
    from app.application.services.exams.curriculum_mapping_helpers import extract_json_object

    raw = extract_json_object(response.get('output_text', ''))
    result = json.loads(raw)
    result['source'] = 'ai_knowledge'
    result['source_label'] = 'KI-generierter Lerninhalt'
    return result
