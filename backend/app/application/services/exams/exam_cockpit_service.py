"""
Exam Cockpit Service

Aggregates all exam intelligence data for the user's personal cockpit:
weakness map, predictions, coverage, recommendations.
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class ExamCockpitService:
    """Aggregates exam intelligence data for user cockpit."""

    @staticmethod
    def get_dashboard(user_id: str, exam_type_key: str) -> Dict[str, Any]:
        """Get complete cockpit data for a user and exam type.

        Returns dict with: overall_readiness, strengths, critical_weaknesses,
        predictions, recommendations, coverage_percent, gap_count.
        """
        framework_id = _resolve_framework(exam_type_key)
        weaknesses, predictions, coverage = _fetch_intelligence(
            user_id, exam_type_key, framework_id,
        )
        return _assemble_dashboard(weaknesses, predictions, coverage)


def _resolve_framework(exam_type_key: str) -> int:
    """Resolve exam_type_key to a curriculum framework ID."""
    from app.infrastructure.persistence.repositories.exams.curriculum import (
        CurriculumFrameworkRepository,
    )

    framework = CurriculumFrameworkRepository.find_framework_for_exam_type(
        exam_type_key,
    )
    if not framework:
        raise ValueError(f"No curriculum framework for '{exam_type_key}'")
    return framework['id']


def _fetch_intelligence(
    user_id: str, exam_type_key: str, framework_id: int,
) -> tuple:
    """Fetch weaknesses, predictions, and coverage with graceful fallback."""
    from app.application.services.exams.prognosis_service import PrognosisService
    from app.application.services.exams.curriculum_service import CurriculumService

    try:
        weaknesses = PrognosisService.get_user_weakness_map(user_id, exam_type_key)
    except Exception:
        logger.exception("Failed to get weakness map for user=%s", user_id)
        weaknesses = []

    try:
        predictions = PrognosisService.predict_all(framework_id)
    except Exception:
        logger.exception("Failed to get predictions for framework=%s", framework_id)
        predictions = []

    try:
        coverage = CurriculumService.get_coverage_report(framework_id)
    except Exception:
        logger.exception("Failed to get coverage for framework=%s", framework_id)
        coverage = {'summary': {'coverage_percent': 0}, 'positions': []}

    return weaknesses, predictions, coverage


def _assemble_dashboard(
    weaknesses: List[Dict[str, Any]],
    predictions: List[Dict[str, Any]],
    coverage: Dict[str, Any],
) -> Dict[str, Any]:
    """Assemble cockpit dashboard response from raw intelligence data."""
    overall_readiness = _compute_readiness(weaknesses)

    strengths = [w for w in weaknesses if w.get('severity') == 'none']
    critical = [w for w in weaknesses if w.get('severity') == 'critical']

    recommendations = _build_recommendations(weaknesses, predictions, top_n=5)

    cov_summary = coverage.get('summary', {})

    return {
        'overall_readiness': overall_readiness,
        'strengths': strengths[:10],
        'critical_weaknesses': critical[:10],
        'predictions': predictions[:10],
        'recommendations': recommendations,
        'coverage_percent': cov_summary.get('coverage_percent', 0),
        'gap_count': cov_summary.get('gap_positions', 0),
        'total_positions': cov_summary.get('total_positions', 0),
    }


def _compute_readiness(weaknesses: List[Dict[str, Any]]) -> int:
    """Compute overall readiness score (0-100) from weakness map.

    Uses average proficiency across all positions, weighted by relevance.
    """
    if not weaknesses:
        return 0

    total_weight = 0.0
    weighted_sum = 0.0
    for w in weaknesses:
        relevance = w.get('relevance_score', 0.5) or 0.5
        proficiency = w.get('proficiency_score', 0) or 0
        weighted_sum += proficiency * relevance
        total_weight += relevance

    if total_weight == 0:
        return 0

    readiness = int(round(weighted_sum / total_weight))
    return max(0, min(100, readiness))


def _build_recommendations(
    weaknesses: List[Dict[str, Any]],
    predictions: List[Dict[str, Any]],
    top_n: int = 5,
) -> List[Dict[str, Any]]:
    """Build top-N study recommendations.

    Score = weakness_severity_weight * relevance * prediction_probability
    """
    prediction_map = {}
    for p in predictions:
        pid = p.get('position_id')
        if pid:
            prediction_map[pid] = p.get('probability', 0.5)

    severity_weights = {
        'critical': 1.0,
        'moderate': 0.7,
        'minor': 0.3,
        'none': 0.0,
    }

    scored = []
    for w in weaknesses:
        severity = w.get('severity', 'none')
        if severity == 'none':
            continue  # No recommendation needed for strong positions

        scored.append(_score_weakness(w, severity, severity_weights, prediction_map))

    scored.sort(key=lambda x: x['priority_score'], reverse=True)
    for i, item in enumerate(scored[:top_n], 1):
        item['priority'] = i
    return scored[:top_n]


def _score_weakness(
    w: Dict[str, Any],
    severity: str,
    severity_weights: Dict[str, float],
    prediction_map: Dict[Any, float],
) -> Dict[str, Any]:
    """Score a single weakness for recommendation ranking."""
    pid = w.get('position_id')
    relevance = w.get('relevance_score', 0.5) or 0.5
    prob = prediction_map.get(pid, 0.5)
    sev_weight = severity_weights.get(severity, 0.5)

    score = sev_weight * relevance * prob

    reason_parts = []
    if severity == 'critical':
        reason_parts.append('Schwach')
    elif severity == 'moderate':
        reason_parts.append('Verbesserungsbedarf')
    if relevance > 0.7:
        reason_parts.append('hochrelevant')
    if prob > 0.6:
        reason_parts.append('wahrscheinlich in nächster Prüfung')

    pos_code = w.get('position_code', '')
    pos_title = w.get('position_title', '')

    return {
        'position_id': pid,
        'position_code': pos_code,
        'position_title': pos_title,
        'action': f"Übe {pos_code} — {pos_title}",
        'reason': ' + '.join(reason_parts) if reason_parts else 'Empfohlen',
        'priority_score': round(score, 3),
        'severity': severity,
        'proficiency_score': w.get('proficiency_score', 0),
    }
