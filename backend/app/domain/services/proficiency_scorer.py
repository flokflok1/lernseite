"""
Domain Service: Proficiency Scorer

Calculates a combined proficiency score from multiple signals.
Pure domain logic — no infrastructure imports.
"""
from typing import Optional


def compute_proficiency_score(
    mastery_avg: Optional[float],
    accuracy_pct: Optional[float],
    attempts_count: int = 0,
) -> float:
    """Combine SRS mastery and simulation accuracy into a 0-100 score.

    Weights:
    - mastery_avg (from SRS review_schedule): 40%
    - accuracy_pct (from simulation answers): 40%
    - attempts_bonus: 20% (more attempts = more reliable data)
    """
    mastery = mastery_avg if mastery_avg is not None else 50.0
    accuracy = accuracy_pct if accuracy_pct is not None else 50.0

    # Attempts bonus: scales from 0 (no attempts) to 100 (10+ attempts)
    attempts_bonus = min(attempts_count / 10.0, 1.0) * 100

    score = mastery * 0.4 + accuracy * 0.4 + attempts_bonus * 0.2
    return round(min(max(score, 0), 100), 1)


def classify_weakness(
    proficiency_score: float,
    relevance_score: float,
    median_relevance: float,
) -> str:
    """Classify weakness severity.

    Returns: 'critical', 'moderate', 'minor', or 'none'
    """
    is_weak = proficiency_score < 50
    is_very_weak = proficiency_score < 30
    is_relevant = relevance_score > median_relevance

    if is_very_weak and is_relevant:
        return 'critical'
    if is_weak and is_relevant:
        return 'moderate'
    if is_weak:
        return 'minor'
    return 'none'


def build_recommendation(severity: str, trend: str, position_title: str) -> str:
    """Build German recommendation text based on severity and trend."""
    if severity == 'critical':
        base = f'Dringend empfohlen — {position_title} ist hochrelevant und schwach'
        if trend == 'rising':
            return f'{base} (steigende Prüfungsrelevanz!)'
        return base
    if severity == 'moderate':
        return f'Fokus empfohlen — {position_title} hat Verbesserungspotenzial'
    if severity == 'minor':
        return f'Optional — {position_title} kann verbessert werden'
    return ''
