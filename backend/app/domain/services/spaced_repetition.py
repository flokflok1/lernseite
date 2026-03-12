"""
SM-2 Spaced Repetition Algorithm — Domain Service.

Pure function: no DB, no side effects. Takes current state + quality,
returns new state.

Quality scale (0-5):
  5 = perfect response, no hesitation
  4 = correct, minor hesitation
  3 = correct, significant difficulty
  2 = incorrect, but close (almost recalled)
  1 = incorrect, recognized correct answer
  0 = complete blackout

Based on: Wozniak, P.A. (1990). SuperMemo algorithm SM-2.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass(frozen=True)
class ReviewState:
    """Immutable value object representing SRS state."""

    easiness_factor: float  # >= 1.3
    interval_days: int      # current interval
    repetition: int         # successful reps in a row
    next_review: datetime
    mastery_score: float    # 0-100
    difficulty_level: str   # easy/medium/hard


def compute_next_review(
    current: ReviewState,
    quality: int,
    now: datetime = None,
) -> ReviewState:
    """SM-2 algorithm: compute next review state from response quality.

    Args:
        current: Current review state.
        quality: Response quality 0-5.
        now: Current time (for testability).

    Returns:
        New ReviewState with updated interval, EF, mastery.
    """
    now = now or datetime.now(timezone.utc)
    quality = max(0, min(5, quality))

    # Update easiness factor
    ef = current.easiness_factor + (
        0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
    )
    ef = max(1.3, ef)

    # Update interval and repetition
    if quality >= 3:  # Correct response
        if current.repetition == 0:
            interval = 1
        elif current.repetition == 1:
            interval = 6
        else:
            interval = round(current.interval_days * ef)
        repetition = current.repetition + 1
    else:  # Failed — reset
        interval = 1
        repetition = 0

    # Update mastery (weighted moving average)
    quality_pct = (quality / 5.0) * 100
    mastery = current.mastery_score * 0.7 + quality_pct * 0.3

    # Derive difficulty from mastery
    if mastery >= 80:
        difficulty = 'easy'
    elif mastery >= 50:
        difficulty = 'medium'
    else:
        difficulty = 'hard'

    return ReviewState(
        easiness_factor=round(ef, 2),
        interval_days=interval,
        repetition=repetition,
        next_review=now + timedelta(days=interval),
        mastery_score=round(mastery, 1),
        difficulty_level=difficulty,
    )


def quality_from_score(score: float, time_ratio: float = 1.0) -> int:
    """Convert a percentage score + time factor to SM-2 quality (0-5).

    Args:
        score: Percentage 0-100.
        time_ratio: actual_time / expected_time. <1 = fast, >1 = slow.

    Returns:
        Quality 0-5.
    """
    # Base quality from score
    if score >= 95:
        q = 5
    elif score >= 80:
        q = 4
    elif score >= 60:
        q = 3
    elif score >= 40:
        q = 2
    elif score >= 20:
        q = 1
    else:
        q = 0

    # Time penalty: if very slow, reduce by 1
    if time_ratio > 2.0 and q > 0:
        q -= 1

    return q


def initial_state(now: datetime = None) -> ReviewState:
    """Create initial review state for a new LM instance."""
    now = now or datetime.now(timezone.utc)
    return ReviewState(
        easiness_factor=2.5,
        interval_days=1,
        repetition=0,
        next_review=now,
        mastery_score=0.0,
        difficulty_level='medium',
    )
