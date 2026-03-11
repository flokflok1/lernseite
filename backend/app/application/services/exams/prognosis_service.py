"""
Prognosis Service

Orchestrates exam prognosis predictions using domain logic and repository data.
"""

import logging
import statistics
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


def _derive_trend(recent_count: Optional[int], older_count: Optional[int]) -> str:
    """Derive trend string from recent vs older exam appearance counts."""
    recent = recent_count or 0
    older = older_count or 0
    if recent > older:
        return 'rising'
    if recent < older:
        return 'declining'
    return 'stable'


def _build_weakness_entry(
    row: Dict[str, Any],
    relevance_by_id: Dict[int, Dict[str, Any]],
    median_relevance: float,
    compute_proficiency_score: Any,
    classify_weakness: Any,
    build_recommendation: Any,
) -> Dict[str, Any]:
    """Build a single weakness result dict for one curriculum position."""
    from app.domain.services.proficiency_scorer import (
        compute_proficiency_score, classify_weakness, build_recommendation,
    )
    proficiency = compute_proficiency_score(
        mastery_avg=row.get('mastery_avg'),
        accuracy_pct=row.get('accuracy_pct'),
        attempts_count=row.get('attempt_count', 0),
    )
    rel = relevance_by_id.get(row['position_id'], {})
    rel_score = rel.get('weighted_score', 0) or 0
    trend = _derive_trend(rel.get('recent_count'), rel.get('older_count'))
    severity = classify_weakness(proficiency, rel_score, median_relevance)
    recommendation = build_recommendation(
        severity, trend, row.get('position_title', ''),
    )
    return {
        'position_id': row['position_id'],
        'position_code': f"{row.get('section_code', '?')}.{row['position_code']}",
        'position_title': row.get('position_title', ''),
        'section_title': row.get('section_title', ''),
        'proficiency_score': proficiency,
        'mastery_avg': row.get('mastery_avg'),
        'accuracy_pct': row.get('accuracy_pct'),
        'attempt_count': row.get('attempt_count', 0),
        'relevance_score': rel_score,
        'trend': trend,
        'severity': severity,
        'recommendation': recommendation,
    }


class PrognosisService:
    """Application service for exam prognosis predictions."""

    @staticmethod
    def predict_all(framework_id: int) -> List[Dict[str, Any]]:
        """Predict probability of positions appearing in next exam.

        Args:
            framework_id: Curriculum framework ID.

        Returns:
            List of position predictions sorted by probability desc.
        """
        from app.infrastructure.persistence.repositories.exams.curriculum import (
            CurriculumFrameworkRepository,
        )
        from app.domain.services.exam_prognosis import predict_all_positions

        history = CurriculumFrameworkRepository.find_position_exam_history(
            framework_id,
        )

        # Transform DB rows to domain input format
        positions_history = []
        for row in history:
            years = row.get('years') or []
            semesters = row.get('semesters') or []
            positions_history.append({
                'position_id': row['position_id'],
                'position_code': f"{row.get('section_code', '?')}.{row['position_code']}",
                'position_title': row.get('position_title', ''),
                'years': [int(y) for y in years if y],
                'semesters': [str(s) for s in semesters if s],
                'total_questions': row.get('total_questions', 0),
            })

        results = predict_all_positions(positions_history)
        logger.info(
            "Prognosis for framework %d: %d positions predicted",
            framework_id, len(results),
        )
        return results

    @staticmethod
    def predict_for_position(
        framework_id: int, position_id: int,
    ) -> Dict[str, Any]:
        """Predict probability for a single position.

        Args:
            framework_id: Curriculum framework ID.
            position_id: Position ID.

        Returns:
            Prediction dict for the position.

        Raises:
            ValueError: If position not found.
        """
        from app.infrastructure.persistence.repositories.exams.curriculum import (
            CurriculumFrameworkRepository,
        )
        from app.domain.services.exam_prognosis import predict_next_exam

        history = CurriculumFrameworkRepository.find_position_exam_history(
            framework_id,
        )
        row = next(
            (r for r in history if r['position_id'] == position_id),
            None,
        )
        if not row:
            raise ValueError(
                f"Position {position_id} not found in framework {framework_id}",
            )

        years = row.get('years') or []
        semesters = row.get('semesters') or []
        pos = {
            'position_id': row['position_id'],
            'position_code': f"{row.get('section_code', '?')}.{row['position_code']}",
            'position_title': row.get('position_title', ''),
            'years': [int(y) for y in years if y],
            'semesters': [str(s) for s in semesters if s],
            'total_questions': row.get('total_questions', 0),
        }

        prediction = predict_next_exam(pos)
        prediction.update({
            'position_id': pos['position_id'],
            'position_code': pos['position_code'],
            'position_title': pos['position_title'],
            'total_questions': pos['total_questions'],
        })
        return prediction

    @staticmethod
    def get_user_weakness_map(
        user_id: str, exam_type_key: str,
    ) -> List[Dict[str, Any]]:
        """Get user weaknesses with proficiency scores and recommendations.

        Combines SRS mastery, simulation accuracy, and exam relevance to
        classify each curriculum position as critical/moderate/minor/none.
        Results are sorted: critical first, then by proficiency ascending.
        """
        from app.infrastructure.persistence.repositories.exams.curriculum import (
            CurriculumFrameworkRepository,
        )
        from app.domain.services.proficiency_scorer import (
            compute_proficiency_score, classify_weakness, build_recommendation,
        )

        framework = CurriculumFrameworkRepository.find_framework_for_exam_type(
            exam_type_key,
        )
        if not framework:
            raise ValueError(f"No curriculum framework for '{exam_type_key}'")

        framework_id = framework['id']
        rows = CurriculumFrameworkRepository.get_user_weakness_map(
            user_id, framework_id,
        )
        relevance = CurriculumFrameworkRepository.find_position_relevance_scores(
            framework_id,
        )
        relevance_by_id = {r['position_id']: r for r in relevance}

        relevance_scores = [r.get('weighted_score', 0) or 0 for r in relevance]
        median_rel = statistics.median(relevance_scores) if relevance_scores else 0.0

        results = [
            _build_weakness_entry(
                row, relevance_by_id, median_rel,
                compute_proficiency_score, classify_weakness, build_recommendation,
            )
            for row in rows
        ]

        severity_order = {'critical': 0, 'moderate': 1, 'minor': 2, 'none': 3}
        results.sort(
            key=lambda x: (severity_order.get(x['severity'], 3), x['proficiency_score']),
        )
        PrognosisService._enrich_with_peer_comparison(results, user_id, framework_id)
        logger.info(
            "Weakness map for user=%s exam_type=%s: %d positions, framework=%d",
            user_id, exam_type_key, len(results), framework_id,
        )
        return results

    @staticmethod
    def _enrich_with_peer_comparison(
        results: List[Dict], user_id: str, framework_id: int,
    ) -> None:
        """Add peer comparison data to weakness entries (in-place)."""
        from app.infrastructure.persistence.repositories.exams.performance_stats import (
            PerformanceStatsRepository,
        )

        percentiles = PerformanceStatsRepository.get_user_percentile(
            user_id, framework_id,
        )
        percentile_by_id = {p['position_id']: p for p in percentiles}

        aggregates = PerformanceStatsRepository.get_position_aggregates(framework_id)
        agg_by_id = {a['position_id']: a for a in aggregates}

        for entry in results:
            pid = entry['position_id']
            perc = percentile_by_id.get(pid)
            agg = agg_by_id.get(pid)

            if perc and agg:
                entry['peer_comparison'] = {
                    'percentile': perc.get('percentile', 0),
                    'avg_accuracy': agg.get('avg_accuracy', 0),
                    'user_count': agg.get('user_count', 0),
                }
            else:
                entry['peer_comparison'] = None

    @staticmethod
    def get_gap_positions(framework_id: int) -> List[Dict[str, Any]]:
        """Get positions with objectives but no tagged questions (gaps).

        Args:
            framework_id: Curriculum framework ID.

        Returns:
            List of gap position dicts with position info.
        """
        from app.application.services.exams.curriculum_service import CurriculumService

        report = CurriculumService.get_coverage_report(framework_id)
        gaps = [p for p in report['positions'] if p.get('gap')]
        logger.info(
            "Found %d gap positions in framework %d",
            len(gaps), framework_id,
        )
        return gaps
