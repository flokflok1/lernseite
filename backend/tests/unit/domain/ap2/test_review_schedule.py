"""Tests für SM-2 Spaced Repetition (ReviewScheduleEntry.apply_quality)."""
import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from app.domain.models.ap2 import ReviewScheduleEntry
from app.domain.models.ap2.review_schedule import (
    EASE_FACTOR_DEFAULT, EASE_FACTOR_MIN,
    INITIAL_INTERVAL_DAYS, SECOND_INTERVAL_DAYS,
)


NOW = datetime(2026, 4, 18, 12, 0, 0)


@pytest.fixture
def fresh_entry():
    return ReviewScheduleEntry(
        user_id=uuid4(),
        item_id=uuid4(),
        next_review_at=NOW,
    )


class TestInitialDefaults:
    def test_defaults(self, fresh_entry):
        assert fresh_entry.ease_factor == EASE_FACTOR_DEFAULT
        assert fresh_entry.interval_days == INITIAL_INTERVAL_DAYS
        assert fresh_entry.repetitions == 0


class TestQualityValidation:
    def test_quality_below_zero_raises(self, fresh_entry):
        with pytest.raises(ValueError):
            fresh_entry.apply_quality(-1, NOW)

    def test_quality_above_5_raises(self, fresh_entry):
        with pytest.raises(ValueError):
            fresh_entry.apply_quality(6, NOW)


class TestSuccessfulQuality:
    """Quality >= 3: SM-2 Standard Interval-Sequenz."""

    def test_first_review_perfect(self, fresh_entry):
        result = fresh_entry.apply_quality(5, NOW)
        assert result.new_repetitions == 1
        assert result.new_interval_days == INITIAL_INTERVAL_DAYS
        assert result.next_review_at == NOW + timedelta(days=1)

    def test_second_review_perfect_uses_6_days(self, fresh_entry):
        first = fresh_entry.apply_quality(5, NOW)
        # State manuell für 2. Review setzen
        fresh_entry.repetitions = first.new_repetitions
        fresh_entry.interval_days = first.new_interval_days
        fresh_entry.ease_factor = first.new_ease_factor
        result = fresh_entry.apply_quality(5, NOW + timedelta(days=1))
        assert result.new_repetitions == 2
        assert result.new_interval_days == SECOND_INTERVAL_DAYS

    def test_third_plus_uses_ease_factor_multiplication(self, fresh_entry):
        # State nach 2 perfekten Reviews simulieren
        fresh_entry.repetitions = 2
        fresh_entry.interval_days = 6
        fresh_entry.ease_factor = 2.6
        result = fresh_entry.apply_quality(5, NOW)
        # 6 * 2.6 = 15.6 → round = 16
        assert result.new_interval_days == 16

    def test_ease_factor_increases_with_perfect(self, fresh_entry):
        result = fresh_entry.apply_quality(5, NOW)
        assert result.new_ease_factor > EASE_FACTOR_DEFAULT


class TestFailedQuality:
    """Quality < 3: Repetitions reset to 0, kurzes Interval."""

    def test_quality_2_resets_repetitions(self, fresh_entry):
        # State nach mehreren Reviews
        fresh_entry.repetitions = 5
        fresh_entry.interval_days = 30
        fresh_entry.ease_factor = 2.7

        result = fresh_entry.apply_quality(2, NOW)
        assert result.new_repetitions == 0
        assert result.new_interval_days == INITIAL_INTERVAL_DAYS
        assert result.next_review_at == NOW + timedelta(days=INITIAL_INTERVAL_DAYS)

    def test_quality_0_total_failure(self, fresh_entry):
        fresh_entry.repetitions = 10
        fresh_entry.interval_days = 90
        result = fresh_entry.apply_quality(0, NOW)
        assert result.new_repetitions == 0

    def test_ease_factor_decreases_with_failure(self, fresh_entry):
        # Start with 2.5
        result = fresh_entry.apply_quality(2, NOW)
        assert result.new_ease_factor < EASE_FACTOR_DEFAULT


class TestEaseFactorBoundary:
    def test_ease_factor_never_below_minimum(self, fresh_entry):
        """Auch nach vielen Failures: ease_factor >= 1.3 (SM-2 Spec)."""
        fresh_entry.ease_factor = 1.4
        result = fresh_entry.apply_quality(0, NOW)
        assert result.new_ease_factor >= EASE_FACTOR_MIN

        # Mehrere Failures hintereinander
        for q in [0, 0, 1, 0]:
            fresh_entry.ease_factor = result.new_ease_factor
            result = fresh_entry.apply_quality(q, NOW)
        assert result.new_ease_factor >= EASE_FACTOR_MIN
