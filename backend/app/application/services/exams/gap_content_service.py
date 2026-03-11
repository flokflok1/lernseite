"""
Gap Content Service

Generates learning content for curriculum positions that have no exam questions (gaps).
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class GapContentService:
    """Generate learning content for gap positions."""

    @staticmethod
    def generate_gap_content(
        framework_id: int,
        position_id: Optional[int] = None,
        provider: str = None,
        model: str = None,
    ) -> List[Dict[str, Any]]:
        """Generate learning content for gap positions.

        Args:
            framework_id: Curriculum framework ID.
            position_id: Optional specific position. If None, generates for all gaps.
            provider: Optional AI provider.
            model: Optional AI model.

        Returns:
            List of generated content dicts.
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
            context = _build_objective_context(objectives)
            query = f"IHK Fachinformatiker: {position_title}"

            content = WebSearchService.search_and_summarize(
                query=query,
                context=context,
                provider=provider,
                model=model,
            )

            content['position_id'] = pid
            content['position_title'] = position_title
            content['generated_at'] = datetime.utcnow().isoformat()
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


def _build_objective_context(objectives: List[Dict[str, Any]]) -> str:
    """Build a bullet-point context string from the first 5 objectives."""
    lines = []
    for obj in objectives[:5]:
        desc = obj.get('description_text') or obj.get('description') or ''
        if isinstance(desc, dict):
            desc = desc.get('de', '') or next(iter(desc.values()), '')
        desc_str = str(desc)[:100]
        if desc_str:
            lines.append(f"- {desc_str}")
    return "\n".join(lines)
