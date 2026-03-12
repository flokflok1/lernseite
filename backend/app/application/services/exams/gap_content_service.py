"""
Gap Content Service

Generates learning content for curriculum gap positions via Gemini Grounding.
Raises WebResearchError on failure — no silent fallback.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class GapContentService:
    """Generate learning content for gap positions via web research."""

    @staticmethod
    def generate_gap_content(
        framework_id: int,
        position_id: Optional[int] = None,
        language: str = 'de',
    ) -> List[Dict[str, Any]]:
        """Generate content for gap positions via Gemini Grounding.

        Raises WebResearchError if Grounding fails.
        """
        from app.application.services.exams.prognosis_service import PrognosisService
        from app.infrastructure.web_research.search_service import WebSearchService
        from app.infrastructure.persistence.repositories.exams.curriculum import (
            CurriculumFrameworkRepository,
        )

        gaps = _resolve_gaps(framework_id, position_id, PrognosisService)

        results = []
        for gap in gaps:
            pid = gap['position_id']

            objectives = CurriculumFrameworkRepository.find_objectives_by_position(pid)
            if not objectives:
                continue

            position_title = _extract_position_title(gap, objectives)
            objective_texts = _extract_objective_texts(objectives)

            content = WebSearchService.research_position(
                position_id=pid,
                position_title=position_title,
                objectives=objective_texts,
                language=language,
            )

            content['position_id'] = pid
            content['position_title'] = position_title
            content['generated_at'] = datetime.now(timezone.utc).isoformat()
            results.append(content)

        logger.info(
            "Generated gap content for %d positions in framework %d",
            len(results), framework_id,
        )
        return results


def _resolve_gaps(
    framework_id: int,
    position_id: Optional[int],
    PrognosisService: Any,
) -> List[Dict[str, Any]]:
    """Return the list of gaps to process."""
    if position_id:
        return [{'position_id': position_id}]
    return PrognosisService.get_gap_positions(framework_id)


def _extract_position_title(
    gap: Dict[str, Any],
    objectives: List[Dict[str, Any]],
) -> str:
    """Extract a human-readable position title from gap or objectives."""
    title = gap.get('position_title', '')
    if title:
        return title
    first_obj = objectives[0]
    return first_obj.get('position_title', '')


def _extract_objective_texts(objectives: List[Dict[str, Any]]) -> List[str]:
    """Extract text strings from the first 5 objectives."""
    texts = []
    for obj in objectives[:5]:
        desc = obj.get('description_text') or obj.get('description') or ''
        if isinstance(desc, dict):
            desc = desc.get('de', '') or next(iter(desc.values()), '')
        desc_str = str(desc)[:100]
        if desc_str:
            texts.append(desc_str)
    return texts
