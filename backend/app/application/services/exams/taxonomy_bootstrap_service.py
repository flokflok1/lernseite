"""
Taxonomy Bootstrap Service — Application Layer.

Bootstraps exam topic taxonomy by:
1. Extracting distinct topics from exam_questions
2. Calling AI to group them into 6-10 parent categories
3. Writing hierarchical taxonomy to exam_topic_taxonomy

Also supports classifying orphan topics into existing parents.
"""

import json
import logging
from typing import Dict, Any, Optional, List

from app.infrastructure.persistence.repositories.exams.topic_taxonomy import (
    TopicTaxonomyRepository,
)

logger = logging.getLogger(__name__)


class TaxonomyBootstrapService:
    """Application service for bootstrapping exam topic taxonomy via AI."""

    @staticmethod
    def bootstrap_exam_type(
        exam_type: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Bootstrap taxonomy for an exam type.

        1. Check if taxonomy already populated — skip if yes.
        2. Get distinct topics from exam_questions.
        3. AI call to group topics into 6-10 parent categories.
        4. Write results to exam_topic_taxonomy.

        Returns summary dict with counts and created categories.
        """
        existing = TopicTaxonomyRepository.find_roots_by_exam_type(exam_type)
        if existing:
            logger.info(
                "Taxonomy already populated for %s (%d roots), skipping",
                exam_type, len(existing),
            )
            return {
                'skipped': True,
                'reason': 'taxonomy_already_populated',
                'existing_roots': len(existing),
            }

        topics = TopicTaxonomyRepository.find_distinct_question_topics(exam_type)
        if not topics:
            logger.warning("No topics found in questions for exam_type=%s", exam_type)
            return {
                'skipped': True,
                'reason': 'no_topics_in_questions',
                'topic_count': 0,
            }

        logger.info(
            "Bootstrapping taxonomy for %s with %d distinct topics",
            exam_type, len(topics),
        )

        grouping = _ai_group_topics(topics, exam_type, provider, model)
        created = _persist_grouping(exam_type, grouping)

        return {
            'skipped': False,
            'exam_type': exam_type,
            'input_topics': len(topics),
            'parent_categories': len(grouping),
            'total_created': created,
        }

    @staticmethod
    def classify_orphan_topic(
        exam_type: str,
        topic_key: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Classify a single new topic into an existing parent category.

        Returns the matched parent info or creates a new root if no match.
        """
        existing_roots = TopicTaxonomyRepository.find_roots_by_exam_type(exam_type)
        if not existing_roots:
            logger.warning(
                "No taxonomy roots for %s, cannot classify orphan %s",
                exam_type, topic_key,
            )
            return {'classified': False, 'reason': 'no_taxonomy_exists'}

        parent = _ai_classify_single(
            topic_key, existing_roots, exam_type, provider, model,
        )

        if not parent:
            logger.info("No matching parent for %s, creating as new root", topic_key)
            TopicTaxonomyRepository.create({
                'exam_type': exam_type,
                'topic_key': topic_key,
                'topic_label': {'de': topic_key, 'en': topic_key},
                'parent_topic_id': None,
                'weight': 0.5,
            })
            return {'classified': False, 'created_as_root': True}

        TopicTaxonomyRepository.create({
            'exam_type': exam_type,
            'topic_key': topic_key,
            'topic_label': {'de': topic_key, 'en': topic_key},
            'parent_topic_id': parent['topic_id'],
            'weight': 1.0,
        })
        return {
            'classified': True,
            'parent_topic_id': parent['topic_id'],
            'parent_key': parent['topic_key'],
        }


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _build_adapter(
    provider: Optional[str], model: Optional[str],
):
    """Build AIAdapter with optional provider/model override (G07)."""
    from app.application.services.ai.adapter import AIAdapter

    kwargs: Dict[str, Any] = {}
    if provider:
        kwargs['provider'] = provider
    if model:
        kwargs['model'] = model
    return AIAdapter(**kwargs)


def _ai_group_topics(
    topics: List[str],
    exam_type: str,
    provider: Optional[str],
    model: Optional[str],
) -> List[Dict[str, Any]]:
    """Ask AI to group flat topics into 6-10 parent categories.

    Returns list of dicts: [{"key": str, "label_de": str, "label_en": str,
                             "children": [str, ...]}]
    """
    adapter = _build_adapter(provider, model)

    topics_str = '\n'.join(f'- {t}' for t in topics)
    prompt = (
        f"You are an education taxonomy expert. "
        f"Given these exam topics for '{exam_type}', group them into "
        f"6 to 10 parent categories.\n\n"
        f"Topics:\n{topics_str}\n\n"
        f"Return ONLY valid JSON — an array of objects with:\n"
        f'  "key": short_snake_case_key,\n'
        f'  "label_de": German display name,\n'
        f'  "label_en": English display name,\n'
        f'  "children": [list of original topic strings that belong here]\n\n'
        f"Every input topic must appear in exactly one category. "
        f"Do not invent new child topics."
    )

    response = adapter.send_request(
        prompt=prompt,
        temperature=0.3,
        max_tokens=4000,
    )

    return _parse_grouping_response(response.get('output_text', ''))


def _parse_grouping_response(text: str) -> List[Dict[str, Any]]:
    """Parse AI JSON response, stripping markdown fences if present."""
    cleaned = text.strip()
    if cleaned.startswith('```'):
        lines = cleaned.split('\n')
        lines = [l for l in lines if not l.strip().startswith('```')]
        cleaned = '\n'.join(lines)

    try:
        result = json.loads(cleaned)
    except json.JSONDecodeError:
        logger.exception("Failed to parse AI taxonomy grouping response")
        raise ValueError("AI returned invalid JSON for taxonomy grouping")

    if not isinstance(result, list):
        raise ValueError("AI response must be a JSON array")
    return result


def _persist_grouping(
    exam_type: str, grouping: List[Dict[str, Any]],
) -> int:
    """Write AI grouping to exam_topic_taxonomy.

    Creates parent categories first, then child topics under each.
    Validates each category dict before persisting — malformed entries
    are skipped with a warning log.
    Returns total number of records created.
    """
    total = 0
    for idx, category in enumerate(grouping):
        # C3: Validate AI response structure before accessing keys
        if not isinstance(category, dict):
            logger.warning(
                "Skipping malformed category at index %d: expected dict, got %s",
                idx, type(category).__name__,
            )
            continue
        if 'key' not in category:
            logger.warning(
                "Skipping category at index %d: missing required 'key' field",
                idx,
            )
            continue

        parent = TopicTaxonomyRepository.create({
            'exam_type': exam_type,
            'topic_key': category['key'],
            'topic_label': {
                'de': category.get('label_de', category['key']),
                'en': category.get('label_en', category['key']),
            },
            'parent_topic_id': None,
            'weight': 1.0,
        })

        # W2: Only count after confirming parent was created
        if not parent:
            logger.warning("Failed to create parent category %s", category['key'])
            continue

        total += 1
        parent_id = parent['topic_id']
        children = category.get('children', [])
        child_records = [
            {
                'exam_type': exam_type,
                'topic_key': child,
                'topic_label': {'de': child, 'en': child},
                'parent_topic_id': parent_id,
                'weight': 1.0,
            }
            for child in children
            if isinstance(child, str) and child.strip()
        ]
        total += TopicTaxonomyRepository.bulk_create(child_records)

    return total


def _ai_classify_single(
    topic_key: str,
    existing_roots: List[Dict[str, Any]],
    exam_type: str,
    provider: Optional[str],
    model: Optional[str],
) -> Optional[Dict[str, Any]]:
    """Ask AI which existing parent category a topic belongs to.

    Returns the matched root dict or None.
    """
    adapter = _build_adapter(provider, model)

    categories_str = '\n'.join(
        f'- {r["topic_key"]}' for r in existing_roots
    )
    prompt = (
        f"Given these parent categories for '{exam_type}':\n"
        f"{categories_str}\n\n"
        f"Which category does the topic '{topic_key}' belong to?\n"
        f'Return ONLY the category key as plain text. '
        f'If none fits, return "NONE".'
    )

    response = adapter.send_request(
        prompt=prompt,
        temperature=0.1,
        max_tokens=100,
    )

    matched_key = response.get('output_text', '').strip().strip('"').strip("'")
    if matched_key == 'NONE':
        return None

    for root in existing_roots:
        if root['topic_key'] == matched_key:
            return root

    logger.warning(
        "AI returned unknown category key '%s' for topic '%s'",
        matched_key, topic_key,
    )
    return None
