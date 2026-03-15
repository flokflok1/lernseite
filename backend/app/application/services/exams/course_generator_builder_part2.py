"""Course Generator Builder Part 2 — support functions.

Split from course_generator_builder.py to comply with G01 (500 LOC limit).
"""
import logging
from typing import Dict, List

from app.domain.models.exam_course_plan import ChapterPlan, parse_label

logger = logging.getLogger(__name__)


def _estimate_duration(lm_type: int, item_count: int) -> int:
    """Estimate lesson duration in minutes from LM type and item count."""
    per_item = {
        0: 12, 1: 10,          # Explanation: ~12 min
        5: 5,                   # Math: 5 min/problem
        6: 2,                   # Flashcards: 2 min/card
        7: 2,                   # Drag & drop: 2 min/pair
        8: 3,                   # Cloze: 3 min/gap
        10: 6,                  # IHK tasks: 6 min/task
        11: 8,                  # Case study: 8 min/step
    }
    base = per_item.get(lm_type, 5)
    return max(2, base * max(1, item_count))


def build_chapter_metadata(chapter_plan: ChapterPlan) -> dict:
    """Build ai_metadata JSONB with intelligence data for frontend badges."""
    meta = {
        'coverage_source': chapter_plan.coverage_source,
        'coverage_pct': chapter_plan.coverage_pct,
        'intelligence_score': chapter_plan.intelligence_score,
        'relevance_score': chapter_plan.relevance_score,
        'prognosis_probability': chapter_plan.prognosis_probability,
    }
    if chapter_plan.prognosis_confidence:
        meta['prognosis_confidence'] = chapter_plan.prognosis_confidence
    if chapter_plan.user_proficiency is not None:
        meta['user_proficiency'] = chapter_plan.user_proficiency
        meta['user_severity'] = chapter_plan.user_severity
    return meta


def enrich_with_web_research(
    chapter_plan: ChapterPlan, plan_data: dict,
    language: str = 'de', region: str = '', exam_type: str = '',
) -> None:
    """Enrich AI plan with web research (Grounding + PDFs) for validation."""
    from app.domain.exceptions.web_research import WebResearchError

    label = chapter_plan.curriculum_position_code or chapter_plan.topic
    result = None
    try:
        result = _fetch_web_research(chapter_plan, language, region, exam_type)
    except WebResearchError as e:
        logger.warning("Grounding failed for %s: %s", label, e)
    except Exception:
        logger.exception("Web research failed for %s", label)

    if result and result.get('summary'):
        plan_data['web_research_context'] = result
        plan_data['grounding_status'] = result.get('grounding_status', 'success')
        plan_data['research_sources'] = result.get('sources', [])
        logger.info("Web research enriched %s (grounding=%s, src=%d)",
                     label, result.get('grounding_status', '?'),
                     len(result.get('sources', [])))
    else:
        plan_data['grounding_status'] = 'failed'
        plan_data['research_sources'] = []


def _fetch_web_research(
    chapter_plan: ChapterPlan, language: str,
    region: str = '', exam_type: str = '',
) -> dict:
    """Fetch web research — curriculum-based or topic-based."""
    if chapter_plan.curriculum_position_id:
        from app.application.services.exams.gap_content_service import (
            GapContentService,
        )
        results = GapContentService.generate_gap_content(
            framework_id=0,
            position_id=chapter_plan.curriculum_position_id,
            language=language, region=region, exam_type=exam_type,
        )
        return results[0] if results else {}

    from app.infrastructure.web_research.search_service import WebSearchService
    topic_name = chapter_plan.topic.replace('_', ' ')
    return WebSearchService.research_position(
        position_id=0, position_title=topic_name,
        objectives=[topic_name], language=language,
        region=region, exam_type=exam_type,
    )


def chapter_title_from_plan(chapter_plan: ChapterPlan, language: str) -> str:
    """Derive chapter title from parent_label or topic key."""
    label = parse_label(chapter_plan.parent_label)
    return label.get(language, chapter_plan.topic.replace('_', ' ').title())


# Maximum questions per LM type in a course chapter.
# The full question pool is handled by the exam trainer — courses are for learning.
MAX_QUESTIONS_PER_LM = 5
MAX_PER_SCENARIO = 2


def select_representative_questions(
    questions: List[Dict], max_total: int = MAX_QUESTIONS_PER_LM,
) -> List[Dict]:
    """Pick a diverse subset of questions for course lessons.

    Strategy:
    1. Group by scenario_title (at most MAX_PER_SCENARIO per scenario)
    2. Prefer higher-point questions (more substantial)
    3. Return at most max_total questions

    The full question pool stays in the exam trainer for practice.
    """
    if len(questions) <= max_total:
        return questions

    # Sort by points descending (most valuable first)
    sorted_qs = sorted(
        questions, key=lambda q: float(q.get('points', 0) or 0), reverse=True,
    )

    selected: List[Dict] = []
    scenario_counts: Dict[str, int] = {}

    for q in sorted_qs:
        if len(selected) >= max_total:
            break
        scenario = q.get('scenario_title') or '_none_'
        count = scenario_counts.get(scenario, 0)
        if count >= MAX_PER_SCENARIO:
            continue
        selected.append(q)
        scenario_counts[scenario] = count + 1

    return selected
