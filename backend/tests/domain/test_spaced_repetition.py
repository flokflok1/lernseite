"""Tests for SM-2 Spaced Repetition Algorithm — Domain Service."""
import pytest
from datetime import datetime, timedelta

from app.domain.services.spaced_repetition import (
    ReviewState,
    compute_next_review,
    initial_state,
    quality_from_score,
)


NOW = datetime(2026, 3, 10, 12, 0, 0)


class TestInitialState:
    """Tests for initial_state factory."""

    def test_defaults(self):
        state = initial_state(now=NOW)
        assert state.easiness_factor == 2.5
        assert state.interval_days == 1
        assert state.repetition == 0
        assert state.next_review == NOW
        assert state.mastery_score == 0.0
        assert state.difficulty_level == "medium"

    def test_immutable(self):
        state = initial_state(now=NOW)
        with pytest.raises(AttributeError):
            state.easiness_factor = 3.0


class TestComputeNextReviewPerfect:
    """Tests for compute_next_review with perfect responses (quality=5)."""

    def test_first_review_perfect(self):
        state = initial_state(now=NOW)
        result = compute_next_review(state, quality=5, now=NOW)
        assert result.interval_days == 1
        assert result.repetition == 1
        assert result.next_review == NOW + timedelta(days=1)

    def test_second_review_perfect(self):
        state = initial_state(now=NOW)
        after_first = compute_next_review(state, quality=5, now=NOW)
        after_second = compute_next_review(after_first, quality=5, now=NOW)
        assert after_second.interval_days == 6
        assert after_second.repetition == 2
        assert after_second.next_review == NOW + timedelta(days=6)

    def test_third_review_perfect(self):
        state = initial_state(now=NOW)
        s1 = compute_next_review(state, quality=5, now=NOW)
        s2 = compute_next_review(s1, quality=5, now=NOW)
        s3 = compute_next_review(s2, quality=5, now=NOW)
        assert s3.repetition == 3
        # SM-2 computes new EF first, then uses it for interval:
        # new_ef = s2.ef + 0.1 = 2.7 + 0.1 = 2.8
        # interval = round(s2.interval_days * new_ef) = round(6 * 2.8) = 17
        assert s3.easiness_factor == 2.8
        assert s3.interval_days == round(s2.interval_days * s3.easiness_factor)
        assert s3.interval_days == 17
        assert s3.next_review == NOW + timedelta(days=17)

    def test_ef_increases_with_perfect(self):
        state = initial_state(now=NOW)
        result = compute_next_review(state, quality=5, now=NOW)
        # EF = 2.5 + (0.1 - 0*0.08 - 0*0.02) = 2.5 + 0.1 = 2.6
        assert result.easiness_factor == 2.6


class TestComputeNextReviewFailed:
    """Tests for compute_next_review with failed responses."""

    def test_failed_resets_repetition(self):
        state = initial_state(now=NOW)
        # Build up some successful reviews
        s1 = compute_next_review(state, quality=5, now=NOW)
        s2 = compute_next_review(s1, quality=5, now=NOW)
        assert s2.repetition == 2
        # Fail
        failed = compute_next_review(s2, quality=2, now=NOW)
        assert failed.repetition == 0
        assert failed.interval_days == 1
        assert failed.next_review == NOW + timedelta(days=1)

    def test_failed_quality_1(self):
        state = initial_state(now=NOW)
        s1 = compute_next_review(state, quality=5, now=NOW)
        failed = compute_next_review(s1, quality=1, now=NOW)
        assert failed.repetition == 0
        assert failed.interval_days == 1

    def test_failed_quality_0(self):
        state = initial_state(now=NOW)
        s1 = compute_next_review(state, quality=5, now=NOW)
        failed = compute_next_review(s1, quality=0, now=NOW)
        assert failed.repetition == 0
        assert failed.interval_days == 1


class TestEasinessFactorFloor:
    """EF must never drop below 1.3."""

    def test_ef_floor_with_quality_0(self):
        state = initial_state(now=NOW)
        # Multiple quality=0 reviews
        s = state
        for _ in range(10):
            s = compute_next_review(s, quality=0, now=NOW)
        assert s.easiness_factor >= 1.3

    def test_ef_floor_with_quality_1(self):
        state = initial_state(now=NOW)
        s = state
        for _ in range(10):
            s = compute_next_review(s, quality=1, now=NOW)
        assert s.easiness_factor >= 1.3

    def test_ef_floor_exact(self):
        # Construct a state with EF already at floor
        state = ReviewState(
            easiness_factor=1.3,
            interval_days=1,
            repetition=0,
            next_review=NOW,
            mastery_score=20.0,
            difficulty_level="hard",
        )
        result = compute_next_review(state, quality=0, now=NOW)
        assert result.easiness_factor == 1.3


class TestMasteryScore:
    """Mastery uses weighted moving average: 70% old + 30% new."""

    def test_mastery_from_zero_perfect(self):
        state = initial_state(now=NOW)
        result = compute_next_review(state, quality=5, now=NOW)
        # mastery = 0.0 * 0.7 + (5/5*100) * 0.3 = 30.0
        assert result.mastery_score == 30.0

    def test_mastery_from_zero_failed(self):
        state = initial_state(now=NOW)
        result = compute_next_review(state, quality=0, now=NOW)
        # mastery = 0.0 * 0.7 + (0/5*100) * 0.3 = 0.0
        assert result.mastery_score == 0.0

    def test_mastery_accumulates(self):
        state = initial_state(now=NOW)
        s = state
        for _ in range(5):
            s = compute_next_review(s, quality=5, now=NOW)
        # After 5 perfect reviews, mastery should be significant
        assert s.mastery_score > 60.0

    def test_mastery_weighted_average(self):
        state = ReviewState(
            easiness_factor=2.5,
            interval_days=1,
            repetition=0,
            next_review=NOW,
            mastery_score=50.0,
            difficulty_level="medium",
        )
        result = compute_next_review(state, quality=3, now=NOW)
        # mastery = 50.0 * 0.7 + (3/5*100) * 0.3 = 35.0 + 18.0 = 53.0
        assert result.mastery_score == 53.0


class TestDifficultyLevel:
    """Difficulty derives from mastery score."""

    def test_easy_at_80(self):
        state = ReviewState(
            easiness_factor=2.5,
            interval_days=6,
            repetition=2,
            next_review=NOW,
            mastery_score=90.0,
            difficulty_level="medium",
        )
        # After quality=5: mastery = 90*0.7 + 100*0.3 = 63 + 30 = 93
        result = compute_next_review(state, quality=5, now=NOW)
        assert result.mastery_score >= 80
        assert result.difficulty_level == "easy"

    def test_medium_between_50_and_80(self):
        state = ReviewState(
            easiness_factor=2.5,
            interval_days=1,
            repetition=0,
            next_review=NOW,
            mastery_score=60.0,
            difficulty_level="easy",
        )
        # After quality=3: mastery = 60*0.7 + 60*0.3 = 42+18 = 60
        result = compute_next_review(state, quality=3, now=NOW)
        assert 50 <= result.mastery_score < 80
        assert result.difficulty_level == "medium"

    def test_hard_below_50(self):
        state = ReviewState(
            easiness_factor=2.5,
            interval_days=1,
            repetition=0,
            next_review=NOW,
            mastery_score=20.0,
            difficulty_level="medium",
        )
        # After quality=0: mastery = 20*0.7 + 0*0.3 = 14.0
        result = compute_next_review(state, quality=0, now=NOW)
        assert result.mastery_score < 50
        assert result.difficulty_level == "hard"


class TestQualityFromScore:
    """Tests for quality_from_score conversion."""

    @pytest.mark.parametrize(
        "score, expected_quality",
        [
            (100, 5),
            (95, 5),
            (94, 4),
            (80, 4),
            (79, 3),
            (60, 3),
            (59, 2),
            (40, 2),
            (39, 1),
            (20, 1),
            (19, 0),
            (0, 0),
        ],
    )
    def test_boundary_values(self, score, expected_quality):
        assert quality_from_score(score) == expected_quality

    def test_time_penalty_reduces_quality(self):
        # Without time penalty: score=80 → q=4
        assert quality_from_score(80, time_ratio=1.0) == 4
        # With time penalty: score=80, slow → q=3
        assert quality_from_score(80, time_ratio=2.5) == 3

    def test_time_penalty_floor_at_zero(self):
        # quality=0 should stay at 0 even with time penalty
        assert quality_from_score(0, time_ratio=3.0) == 0
        assert quality_from_score(10, time_ratio=3.0) == 0

    def test_time_penalty_threshold(self):
        # time_ratio=2.0 should NOT trigger penalty (only >2.0)
        assert quality_from_score(80, time_ratio=2.0) == 4
        # time_ratio=2.01 should trigger penalty
        assert quality_from_score(80, time_ratio=2.01) == 3


class TestQualityClamping:
    """Quality values outside 0-5 are clamped."""

    def test_quality_above_5_clamped(self):
        state = initial_state(now=NOW)
        result = compute_next_review(state, quality=10, now=NOW)
        # Should behave like quality=5
        expected = compute_next_review(state, quality=5, now=NOW)
        assert result.easiness_factor == expected.easiness_factor
        assert result.interval_days == expected.interval_days
        assert result.repetition == expected.repetition
        assert result.mastery_score == expected.mastery_score

    def test_quality_below_0_clamped(self):
        state = initial_state(now=NOW)
        result = compute_next_review(state, quality=-3, now=NOW)
        # Should behave like quality=0
        expected = compute_next_review(state, quality=0, now=NOW)
        assert result.easiness_factor == expected.easiness_factor
        assert result.interval_days == expected.interval_days
        assert result.repetition == expected.repetition
        assert result.mastery_score == expected.mastery_score
