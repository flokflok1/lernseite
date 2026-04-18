"""
AP2 TopicMastery — Aggregierte Mastery pro User+Topic.

Mastery-Score nutzt einen **asymmetrischen** Exponential Moving Average:
- Verschlechterung: alpha=0.5 (schnell sinken — "Desirable Difficulty")
- Verbesserung:    alpha=0.2 (langsam steigen — Konsistenz wird belohnt)

Zusätzlich wird ein Personal Best (höchste je erreichte pct) getrackt sowie
eine regression_streak (Versuche in Folge unter best_pct - 10).

DDD Layer: Domain — NO Flask, DB, or Infrastructure imports.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


# Asymmetrischer EMA — schneller sinken als steigen
EMA_ALPHA_DOWN = 0.5    # neuer pct < alter score: schnell adaptieren
EMA_ALPHA_UP = 0.2      # neuer pct > alter score: langsam adaptieren

# Regression-Schwellwert
REGRESSION_THRESHOLD = 10   # %-Punkte unter best_pct → zählt als Regression


@dataclass
class TopicMastery:
    """Pro User+Topic: Mastery-Score + Aggregat-Zähler.

    Mastery-Score-Skala:
    - 0     = noch nicht gelernt
    - 50    = IHK-Bestehensgrenze
    - 80    = solide beherrscht
    - 100   = perfekt
    """
    user_id: UUID
    topic_id: UUID
    mastery_score: float = 0.0
    attempts_count: int = 0
    correct_count: int = 0
    total_points_earned: float = 0.0
    total_points_possible: float = 0.0
    best_pct: int = 0
    best_pct_date: Optional[datetime] = None
    regression_streak: int = 0
    last_attempt_at: Optional[datetime] = None
    last_review_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def apply_attempt(
        self,
        pct: int,
        points_earned: float,
        points_total: float,
        now: datetime,
    ) -> None:
        """Aktualisiert Mastery nach einem neuen Attempt.

        Asymmetrischer EMA + Personal Best + Regression Streak.
        """
        # 1. Asymmetrischer EMA: schneller sinken als steigen
        if pct < self.mastery_score:
            alpha = EMA_ALPHA_DOWN
        else:
            alpha = EMA_ALPHA_UP
        self.mastery_score = round(
            alpha * pct + (1 - alpha) * self.mastery_score, 2
        )

        # 2. Counter aktualisieren
        self.attempts_count += 1
        if pct >= 50:
            self.correct_count += 1
        self.total_points_earned += points_earned
        self.total_points_possible += points_total
        self.last_attempt_at = now

        # 3. Personal Best updaten — wächst monoton
        if pct > self.best_pct:
            self.best_pct = pct
            self.best_pct_date = now

        # 4. Regression Streak: zählt Versuche die deutlich unter best_pct sind
        if pct < self.best_pct - REGRESSION_THRESHOLD:
            self.regression_streak += 1
        else:
            self.regression_streak = 0

    @property
    def accuracy(self) -> float:
        """Anteil 'richtiger' Versuche (pct >= 50)."""
        if self.attempts_count == 0:
            return 0.0
        return round(self.correct_count / self.attempts_count * 100, 2)

    @property
    def point_ratio(self) -> float:
        """Gesammelte Punkte / mögliche Punkte in Prozent."""
        if self.total_points_possible == 0:
            return 0.0
        return round(self.total_points_earned / self.total_points_possible * 100, 2)

    @property
    def is_passing(self) -> bool:
        """Thema gilt als bestanden wenn Mastery >= 50."""
        return self.mastery_score >= 50

    @property
    def is_weakness(self) -> bool:
        """Thema gilt als Schwäche wenn Mastery < 40 nach >= 3 Versuchen."""
        return self.attempts_count >= 3 and self.mastery_score < 40

    @property
    def is_in_regression(self) -> bool:
        """User regrediert: 2+ Versuche in Folge deutlich unter Personal Best."""
        return self.regression_streak >= 2

    @property
    def gap_to_best(self) -> int:
        """Wie weit ist der aktuelle Score unter dem Personal Best?"""
        return max(0, self.best_pct - int(self.mastery_score))
