"""Tests für TopicMastery — asymmetrischer EMA + Personal-Best + Regression-Streak."""
import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from app.domain.models.ap2 import TopicMastery


NOW = datetime(2026, 4, 18, 12, 0, 0)


@pytest.fixture
def fresh_mastery():
    """Frische Mastery, noch keine Versuche."""
    return TopicMastery(user_id=uuid4(), topic_id=uuid4())


class TestInitialState:
    def test_defaults(self, fresh_mastery):
        m = fresh_mastery
        assert m.mastery_score == 0.0
        assert m.attempts_count == 0
        assert m.correct_count == 0
        assert m.best_pct == 0
        assert m.regression_streak == 0
        assert not m.is_passing
        assert not m.is_in_regression


class TestAsymmetricEMA:
    """EMA steigt langsam (alpha=0.2), sinkt schnell (alpha=0.5)."""

    def test_first_attempt_perfect_uses_up_alpha(self, fresh_mastery):
        # 0 → 100: steigt → alpha_up=0.2
        fresh_mastery.apply_attempt(100, 1.0, 1.0, NOW)
        assert fresh_mastery.mastery_score == pytest.approx(20.0)

    def test_consecutive_perfect_attempts_grow_slowly(self, fresh_mastery):
        for _ in range(5):
            fresh_mastery.apply_attempt(100, 1.0, 1.0, NOW)
        # 0 → 20 → 36 → 49 → 59 → 67
        assert fresh_mastery.mastery_score == pytest.approx(67.23, abs=0.5)

    def test_drop_after_high_score_falls_fast(self, fresh_mastery):
        """Personal-Pain-Point: 4× perfekt, dann 30% — Score sinkt deutlich."""
        for _ in range(4):
            fresh_mastery.apply_attempt(100, 1.0, 1.0, NOW)
        score_before = fresh_mastery.mastery_score   # ~59
        fresh_mastery.apply_attempt(30, 0.3, 1.0, NOW)
        # 30 < 59 → alpha_down=0.5: 0.5*30 + 0.5*59 = 44.5
        assert fresh_mastery.mastery_score < score_before
        assert fresh_mastery.mastery_score == pytest.approx(44.5, abs=1)

    def test_small_regression_still_updates_score(self, fresh_mastery):
        """User-Wunsch: 1P weniger als best soll erkennbar sein."""
        for _ in range(5):
            fresh_mastery.apply_attempt(100, 1.0, 1.0, NOW)
        before = fresh_mastery.mastery_score   # ~67
        # 90% < 67? Nein. → alpha_up: 0.2*90 + 0.8*67 = 71.6 → steigt
        fresh_mastery.apply_attempt(90, 0.9, 1.0, NOW)
        # Score steigt zwar, aber: best_pct + regression_streak fangen das
        # — hier nur EMA-Test. Asym-Test im Drop-Fall darüber.
        assert fresh_mastery.mastery_score > before


class TestPersonalBest:
    def test_best_pct_grows_monotonically(self, fresh_mastery):
        fresh_mastery.apply_attempt(60, 0.6, 1.0, NOW)
        assert fresh_mastery.best_pct == 60
        fresh_mastery.apply_attempt(95, 0.95, 1.0, NOW)
        assert fresh_mastery.best_pct == 95
        fresh_mastery.apply_attempt(40, 0.4, 1.0, NOW)
        # Best wird NICHT zurückgesetzt
        assert fresh_mastery.best_pct == 95

    def test_best_pct_date_records_when_reached(self, fresh_mastery):
        t1 = NOW
        t2 = NOW + timedelta(days=1)
        fresh_mastery.apply_attempt(80, 0.8, 1.0, t1)
        assert fresh_mastery.best_pct_date == t1
        fresh_mastery.apply_attempt(95, 0.95, 1.0, t2)
        assert fresh_mastery.best_pct_date == t2

    def test_gap_to_best(self, fresh_mastery):
        for _ in range(5):
            fresh_mastery.apply_attempt(100, 1.0, 1.0, NOW)
        # mastery ~67, best=100 → gap = 100 - 67 = 33
        assert fresh_mastery.gap_to_best > 30


class TestRegressionStreak:
    """User-Wunsch: nach erreichtem Niveau soll Verschlechterung erkannt werden."""

    def test_first_attempt_no_streak(self, fresh_mastery):
        fresh_mastery.apply_attempt(80, 0.8, 1.0, NOW)
        assert fresh_mastery.regression_streak == 0

    def test_score_under_best_minus_threshold_increments_streak(self, fresh_mastery):
        # Best wird 95
        fresh_mastery.apply_attempt(95, 0.95, 1.0, NOW)
        assert fresh_mastery.regression_streak == 0
        # 80 < 95 - 10 = 85? 80 < 85 → ja → Streak +1
        fresh_mastery.apply_attempt(80, 0.8, 1.0, NOW)
        assert fresh_mastery.regression_streak == 1
        fresh_mastery.apply_attempt(70, 0.7, 1.0, NOW)
        assert fresh_mastery.regression_streak == 2
        # Streak >= 2 → is_in_regression
        assert fresh_mastery.is_in_regression

    def test_score_within_threshold_resets_streak(self, fresh_mastery):
        fresh_mastery.apply_attempt(95, 0.95, 1.0, NOW)
        fresh_mastery.apply_attempt(70, 0.7, 1.0, NOW)
        fresh_mastery.apply_attempt(70, 0.7, 1.0, NOW)
        assert fresh_mastery.regression_streak == 2
        # Wieder 90 → 90 < 95-10=85? Nein → Reset
        fresh_mastery.apply_attempt(90, 0.9, 1.0, NOW)
        assert fresh_mastery.regression_streak == 0
        assert not fresh_mastery.is_in_regression


class TestCounters:
    def test_attempts_count_increments(self, fresh_mastery):
        for _ in range(3):
            fresh_mastery.apply_attempt(80, 0.8, 1.0, NOW)
        assert fresh_mastery.attempts_count == 3

    def test_correct_count_only_for_passing(self, fresh_mastery):
        fresh_mastery.apply_attempt(80, 0.8, 1.0, NOW)   # passes (>=50)
        fresh_mastery.apply_attempt(40, 0.4, 1.0, NOW)   # fails
        fresh_mastery.apply_attempt(50, 0.5, 1.0, NOW)   # passes (boundary)
        assert fresh_mastery.attempts_count == 3
        assert fresh_mastery.correct_count == 2

    def test_total_points_accumulate(self, fresh_mastery):
        fresh_mastery.apply_attempt(80, 8.0, 10.0, NOW)
        fresh_mastery.apply_attempt(50, 5.0, 10.0, NOW)
        assert fresh_mastery.total_points_earned == 13.0
        assert fresh_mastery.total_points_possible == 20.0
        assert fresh_mastery.point_ratio == 65.0


class TestPropertyHelpers:
    def test_is_weakness_requires_3plus_attempts(self, fresh_mastery):
        for _ in range(2):
            fresh_mastery.apply_attempt(20, 0.2, 1.0, NOW)
        assert not fresh_mastery.is_weakness   # nur 2 Versuche

        fresh_mastery.apply_attempt(20, 0.2, 1.0, NOW)
        assert fresh_mastery.is_weakness       # 3+ Versuche, score < 40

    def test_accuracy_zero_when_no_attempts(self, fresh_mastery):
        assert fresh_mastery.accuracy == 0.0

    def test_is_passing_at_50_threshold(self, fresh_mastery):
        # mastery muss >= 50 sein
        for _ in range(20):
            fresh_mastery.apply_attempt(60, 0.6, 1.0, NOW)
        assert fresh_mastery.is_passing
