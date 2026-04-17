"""
AP2 TopicMastery — Aggregierte Mastery pro User+Topic.

Mastery-Score ist ein Exponential Moving Average (EMA) der letzten
Attempts, stärker gewichtet auf jüngere Versuche. Treibt das Dashboard
und die Prognose-Berechnung.

DDD Layer: Domain — NO Flask, DB, or Infrastructure imports.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


# Wie stark zählt der neue Versuch (EMA-Glättungsfaktor)
EMA_ALPHA = 0.3


@dataclass
class TopicMastery:
    """Pro User+Topic: Mastery-Score + Aggregat-Zähler.

    Mastery-Score:
    - 0 = noch nichts gelernt
    - 50 = IHK-Bestehensgrenze
    - 80 = solide beherrscht
    - 100 = perfekt
    """
    user_id: UUID
    topic_id: UUID
    mastery_score: float = 0.0             # 0-100
    attempts_count: int = 0
    correct_count: int = 0                 # wo pct >= 50
    total_points_earned: float = 0.0
    total_points_possible: float = 0.0
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

        EMA: neuer_score = alpha * pct + (1 - alpha) * alter_score
        """
        self.mastery_score = round(
            EMA_ALPHA * pct + (1 - EMA_ALPHA) * self.mastery_score, 2
        )
        self.attempts_count += 1
        if pct >= 50:
            self.correct_count += 1
        self.total_points_earned += points_earned
        self.total_points_possible += points_total
        self.last_attempt_at = now

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
