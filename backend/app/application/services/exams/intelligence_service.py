"""
Exam Intelligence Service

Orchestrates exam context detection and weakness analysis:
- Auto-detects exam relevance from user goals + course content
- Builds ExamContext for AI prompt enrichment
- Computes WeaknessProfile for adaptive learning

Uses the domain registry (repos.*) for all data access.
"""

import logging
from typing import Optional, List, Dict, Any

from app.domain.models.exam_intelligence import (
    TopicWeakness,
    WeaknessProfile,
    ExamContext,
)
from app.domain.ports.core.registry import repos
from app.infrastructure.persistence.database.connection import fetch_all

logger = logging.getLogger(__name__)


class ExamIntelligenceService:
    """Central service for exam intelligence features."""

    @staticmethod
    def get_exam_context_for_ai(
        user_id: str,
        course_id: Optional[str] = None,
    ) -> Optional[ExamContext]:
        """
        Auto-detect exam context from user goals and course metadata.

        Returns ExamContext if exam relevance is detected, None otherwise.
        No manual configuration required — detection is automatic.

        Args:
            user_id: Current user UUID
            course_id: Optional course UUID for additional context

        Returns:
            ExamContext value object or None
        """
        # 1. Get user's active exam goals via registry
        active_types = repos.user_exam_goals.find_active_exam_types(user_id)

        # 2. Get course metadata for additional signals
        course_exam_type = None
        course_topics = []
        if course_id:
            try:
                from app.infrastructure.persistence.repositories.ai.exam_context import (
                    ExamContextRepository,
                )
                course_meta = ExamContextRepository.get_course_metadata(course_id)
                if course_meta:
                    course_exam_type = course_meta.get('detected_exam_type')
                    course_topics = course_meta.get('detected_topics') or []
            except Exception as e:
                logger.debug("Could not load course metadata: %s", e)

        # 3. Determine primary exam type
        exam_type = None
        if active_types:
            if course_exam_type and course_exam_type in active_types:
                exam_type = course_exam_type
            else:
                exam_type = active_types[0]
        elif course_exam_type:
            exam_type = course_exam_type

        if not exam_type:
            return None

        # 4. Load taxonomy for this exam type via registry
        taxonomy = repos.topic_taxonomy.find_by_exam_type(exam_type)
        all_topic_keys = [t['topic_key'] for t in taxonomy]

        # 5. Identify hard topics from global stats
        hard_topics = _get_hard_topics(exam_type)

        # 6. Get passing score from registry
        registry_entry = repos.exam_type_registry.find_by_type(exam_type)
        passing_score = (
            registry_entry.get('passing_score', 50) if registry_entry else 50
        )

        # 7. Determine relevant topics
        if course_topics:
            relevant = [t for t in all_topic_keys if t in course_topics]
            if not relevant:
                relevant = all_topic_keys[:10]
        else:
            relevant = all_topic_keys[:10]

        return ExamContext.from_dict({
            'exam_type': exam_type,
            'relevant_topics': relevant,
            'hard_topics': hard_topics,
            'passing_score': passing_score,
        })

    @staticmethod
    def get_weakness_profile(
        user_id: str,
        exam_type: str,
    ) -> WeaknessProfile:
        """
        Compute a user's weakness profile for a specific exam type.

        Args:
            user_id: User UUID
            exam_type: Exam type key (e.g. 'FI_AP1')

        Returns:
            WeaknessProfile value object
        """
        # Get user's per-topic stats from existing analytics
        analytics = None
        try:
            from app.infrastructure.persistence.repositories.ai.exam_context import (
                ExamContextRepository,
            )
            analytics = ExamContextRepository.get_learning_analytics(
                user_id, None
            )
        except Exception as e:
            logger.debug("Could not load learning analytics: %s", e)

        # Get taxonomy topics for this exam type via registry
        taxonomy = repos.topic_taxonomy.find_by_exam_type(exam_type)
        taxonomy_keys = {t['topic_key'] for t in taxonomy}

        # Build weaknesses from analytics
        weaknesses = []
        total_score = 0.0
        scored_count = 0

        if analytics:
            topic_scores = analytics.get('topic_scores') or {}
            for topic_key, score_data in topic_scores.items():
                if topic_key not in taxonomy_keys:
                    continue
                score = (
                    float(score_data)
                    if isinstance(score_data, (int, float))
                    else 0.0
                )
                weaknesses.append(TopicWeakness.from_dict({
                    'topic_key': topic_key,
                    'score': score,
                    'attempts': 0,
                    'trend': 'stable',
                }))
                total_score += score
                scored_count += 1

        # Add unscored taxonomy topics as zero-score weaknesses
        scored_keys = {w.topic_key for w in weaknesses}
        for t in taxonomy:
            if t['topic_key'] not in scored_keys:
                weaknesses.append(TopicWeakness.from_dict({
                    'topic_key': t['topic_key'],
                    'score': 0.0,
                    'trend': 'stable',
                }))

        weaknesses.sort(key=lambda w: w.score)
        overall = total_score / scored_count if scored_count > 0 else 0.0

        # Build recommendation
        registry_entry = repos.exam_type_registry.find_by_type(exam_type)
        passing = (
            registry_entry.get('passing_score', 50) if registry_entry else 50
        )
        if overall >= passing:
            recommendation = (
                'Gute Vorbereitung! Fokussiere auf die schwächsten Topics.'
            )
        elif overall >= passing * 0.7:
            recommendation = (
                'Fast bereit. Intensiviere die schwachen Bereiche.'
            )
        else:
            recommendation = (
                'Noch Übungsbedarf. Starte mit den Top-3 Schwächen.'
            )

        return WeaknessProfile.from_dict({
            'exam_type': exam_type,
            'weaknesses': [w.to_dict() for w in weaknesses],
            'overall_score': round(overall, 1),
            'recommendation': recommendation,
        })

    @staticmethod
    def list_programs_with_parts() -> List[Dict[str, Any]]:
        """Return all exam programs with their nested parts.

        Application layer method — API calls this, not the repository directly.
        """
        from app.infrastructure.persistence.repositories.exams.programs import (
            ExamProgramRepository,
        )
        return ExamProgramRepository.find_with_parts()


def sync_exam_type_i18n(exam_type: str, display_name: dict):
    """Sync exam type display name to i18n system (called after create/update)."""
    from app.infrastructure.persistence.repositories.i18n.admin.bulk_seed import (
        I18nBulkSeedRepository,
    )
    I18nBulkSeedRepository.sync_entity_display_name(
        namespace='exams',
        key_path=f'exams.types.{exam_type}',
        display_name=display_name,
    )
    _invalidate_exam_i18n_cache(display_name)


def sync_exam_region_i18n(region_code: str, display_name: dict):
    """Sync exam region display name to i18n system (called after create/update)."""
    from app.infrastructure.persistence.repositories.i18n.admin.bulk_seed import (
        I18nBulkSeedRepository,
    )
    I18nBulkSeedRepository.sync_entity_display_name(
        namespace='exams',
        key_path=f'exams.regions.{region_code}',
        display_name=display_name,
    )
    _invalidate_exam_i18n_cache(display_name)


def _invalidate_exam_i18n_cache(display_name: dict):
    """Invalidate i18n bundle cache for affected languages."""
    try:
        from app.infrastructure.cache.service import CacheService
        for lang in display_name:
            CacheService.cache_delete(f"i18n:bundle:{lang}:exams")
            CacheService.cache_delete(f"i18n:bundle:{lang}:")
    except Exception:
        logger.warning("Failed to invalidate i18n cache", exc_info=True)


def _get_hard_topics(exam_type: str, limit: int = 5) -> List[str]:
    """Get the hardest topics for an exam type from global stats."""
    query = """
        SELECT topic_key
        FROM assessments.exam_topic_global_stats
        WHERE exam_type = %s AND difficulty_rating = 'hard'
        ORDER BY avg_score ASC
        LIMIT %s
    """
    rows = fetch_all(query, (exam_type, limit))
    return [r['topic_key'] for r in rows]
