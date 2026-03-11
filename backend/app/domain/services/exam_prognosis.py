"""
Domain Service: Exam Prognosis Prediction

Pure Python domain logic — NO Flask, NO infrastructure, NO ORM imports.
Predicts probability of an exam position appearing in the next exam period.
"""
from __future__ import annotations

import statistics
from datetime import datetime
from typing import Optional

# Reference year for recency calculations
_REFERENCE_YEAR = 2025
_TOTAL_YEARS = 8          # 8-year historical window
_TOTAL_PERIODS = 16       # ~16 semesters in 8 years (2 per year)
_RECENT_YEARS = 3
_OLDER_YEARS = _TOTAL_YEARS - _RECENT_YEARS  # 5


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _compute_base_rate(years: list[int]) -> float:
    """Frequency factor: how often position appeared across total periods."""
    appearances = len(years)
    return appearances / _TOTAL_PERIODS


def _compute_trend_factor(years: list[int]) -> tuple[float, str]:
    """Compare recent 3 years vs older 5 years to detect trend."""
    if not years:
        return 1.0, 'stable'

    cutoff = _REFERENCE_YEAR - _RECENT_YEARS  # 2022

    recent_count = sum(1 for y in years if y > cutoff)
    older_count = sum(1 for y in years if y <= cutoff)

    recent_rate = recent_count / _RECENT_YEARS
    older_rate = older_count / _OLDER_YEARS if _OLDER_YEARS > 0 else 0.0

    if older_rate == 0 and recent_rate > 0:
        return 1.2, 'rising'
    if recent_rate == 0 and older_rate > 0:
        return 0.8, 'declining'
    if older_rate == 0:
        return 1.0, 'stable'

    ratio = recent_rate / older_rate
    if ratio > 1.3:
        return 1.2, 'rising'
    if ratio < 0.7:
        return 0.8, 'declining'
    return 1.0, 'stable'


def _compute_cycle_factor(semesters: list[str]) -> float:
    """Detect regular appearance cycle and check if position is due."""
    if len(semesters) < 3:
        return 1.0

    # Sort semesters chronologically by parsing WS/SS + year
    def _sem_sort_key(sem: str) -> int:
        prefix = sem[:2].upper()
        year_str = sem[2:].strip()
        try:
            year = int(year_str)
        except ValueError:
            return 0
        # WS = second half of year (index 1), SS = first half (index 0)
        half = 1 if prefix == 'WS' else 0
        return year * 2 + half

    sorted_sems = sorted(semesters, key=_sem_sort_key)
    keys = [_sem_sort_key(s) for s in sorted_sems]

    # Gaps between consecutive appearances (in half-year units)
    gaps = [keys[i + 1] - keys[i] for i in range(len(keys) - 1)]
    if not gaps:
        return 1.0

    median_gap = statistics.median(gaps)
    try:
        std_gap = statistics.stdev(gaps) if len(gaps) >= 2 else 0.0
    except statistics.StatisticsError:
        std_gap = 0.0

    # Only use cycle logic if variance is low enough
    if std_gap >= 1.5:
        return 1.0

    # Predict next expected key
    last_key = keys[-1]
    next_expected_key = last_key + median_gap

    # Current period key (reference: mid-2026 ≈ WS2025 end / SS2026 start)
    current_key = _REFERENCE_YEAR * 2 + 1  # approx WS2025

    # Is next occurrence at or just after current period?
    if next_expected_key <= current_key + 1:
        return 1.15  # due
    return 0.9  # not yet due


def _compute_recency_factor(years: list[int]) -> float:
    """Penalise recently seen positions; boost overdue ones."""
    if not years:
        return 0.5

    last_year = max(years)
    gap = _REFERENCE_YEAR - last_year  # years since last appearance

    if gap <= 1:
        return 0.85   # just appeared
    if gap <= 3:
        return 1.1    # getting due
    return 1.25       # overdue


def _build_reasoning(
    trend: str,
    semesters: list[str],
    cycle_factor: float,
    recency_factor: float,
    base_rate: float,
) -> str:
    """Construct a German human-readable reasoning string."""
    parts: list[str] = []

    # Trend
    trend_labels = {'rising': 'Steigende Tendenz', 'declining': 'Sinkende Tendenz', 'stable': 'Stabile Häufigkeit'}
    parts.append(trend_labels.get(trend, 'Stabile Häufigkeit'))

    # Last appearance
    if semesters:
        def _sem_sort_key(sem: str) -> int:
            prefix = sem[:2].upper()
            year_str = sem[2:].strip()
            try:
                year = int(year_str)
            except ValueError:
                return 0
            half = 1 if prefix == 'WS' else 0
            return year * 2 + half

        last_sem = sorted(semesters, key=_sem_sort_key)[-1]
        parts.append(f'zuletzt {last_sem}')
    else:
        parts.append('noch nie geprüft')

    # Cycle hint
    if cycle_factor == 1.15:
        parts.append('planmäßig fällig (regelmäßiger Zyklus)')
    elif cycle_factor == 0.9:
        parts.append('laut Zyklus noch nicht fällig')

    # Frequency hint
    total = int(base_rate * _TOTAL_PERIODS)
    if base_rate < 0.2:
        parts.append(f'selten geprüft ({total}x in {_TOTAL_YEARS} Jahren)')

    return ', '.join(parts)


def _confidence_level(years: list[int]) -> str:
    """Derive confidence from data volume and variance."""
    n = len(years)
    if n < 3:
        return 'low'
    if n < 6:
        return 'medium'
    # High confidence: 6+ data points with low variance
    if n >= 6:
        try:
            variance = statistics.variance(years)
        except statistics.StatisticsError:
            variance = float('inf')
        if variance < 5.0:
            return 'high'
    return 'medium'


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def predict_next_exam(position_history: dict) -> dict:
    """
    Predict probability of a position appearing in the next exam period.

    Args:
        position_history: dict with keys position_id, position_code,
                          position_title, years, semesters, total_questions.

    Returns:
        dict with probability (float), confidence (str), trend (str), reasoning (str).
    """
    years: list[int] = position_history.get('years') or []
    semesters: list[str] = position_history.get('semesters') or []

    base_rate = _compute_base_rate(years)
    trend_factor, trend = _compute_trend_factor(years)
    cycle_factor = _compute_cycle_factor(semesters)
    recency_factor = _compute_recency_factor(years)

    raw = base_rate * trend_factor * cycle_factor * recency_factor
    probability = min(max(raw, 0.05), 0.95)

    confidence = _confidence_level(years)
    reasoning = _build_reasoning(trend, semesters, cycle_factor, recency_factor, base_rate)

    return {
        'probability': round(probability, 4),
        'confidence': confidence,
        'trend': trend,
        'reasoning': reasoning,
    }


def predict_all_positions(
    positions_history: list[dict],
    current_year: Optional[int] = None,
) -> list[dict]:
    """
    Run predict_next_exam for every position and return sorted results.

    Args:
        positions_history: list of position_history dicts.
        current_year: unused override (reserved for future extension).

    Returns:
        List of dicts combining original position data with prediction fields,
        sorted by probability descending.
    """
    results = []
    for pos in positions_history:
        prediction = predict_next_exam(pos)
        entry = {
            'position_id': pos.get('position_id'),
            'position_code': pos.get('position_code'),
            'position_title': pos.get('position_title'),
            'total_questions': pos.get('total_questions', 0),
            **prediction,
        }
        results.append(entry)

    results.sort(key=lambda x: x['probability'], reverse=True)
    return results
