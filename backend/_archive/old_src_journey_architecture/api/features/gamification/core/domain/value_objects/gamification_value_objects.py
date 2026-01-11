"""
Gamification Domain - Value Objects

Immutable value objects representing Gamification domain concepts.

Value Objects:
- XPLevel: Experience points and level progression
- QuestStatus: Status of quests
- Achievement: Achievement type with criteria
- RecallInterval: Spaced repetition interval (SM2 algorithm)
- DifficultyRating: Adaptive difficulty rating (ELO-based)
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum
from decimal import Decimal
from datetime import datetime, timedelta
import math


class QuestStatusEnum(str, Enum):
    """Quest status enumeration"""
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class QuestTypeEnum(str, Enum):
    """Quest type enumeration"""
    DAILY = "daily"
    WEEKLY = "weekly"
    ACHIEVEMENT = "achievement"
    COURSE = "course"
    CHALLENGE = "challenge"


class AchievementTypeEnum(str, Enum):
    """Achievement type enumeration"""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


@dataclass(frozen=True)
class XPLevel:
    """
    XP Level Value Object.

    Represents experience points and level progression.
    Immutable.

    Attributes:
        xp_total: Total XP earned
        level: Current level
        xp_current_level: XP in current level
        xp_next_level: XP required for next level
    """
    xp_total: int
    level: int
    xp_current_level: int
    xp_next_level: int

    @staticmethod
    def calculate_level(xp_total: int) -> 'XPLevel':
        """
        Calculate level from total XP.

        Uses formula: level = floor(sqrt(xp_total / 100))
        Next level XP: (level + 1)^2 * 100

        Args:
            xp_total: Total XP earned

        Returns:
            XPLevel instance
        """
        if xp_total < 0:
            xp_total = 0

        # Calculate level
        level = int(math.sqrt(xp_total / 100))

        # Calculate XP for current level
        xp_for_current_level = level * level * 100
        xp_current_level = xp_total - xp_for_current_level

        # Calculate XP needed for next level
        xp_for_next_level = (level + 1) * (level + 1) * 100
        xp_next_level = xp_for_next_level - xp_total

        return XPLevel(
            xp_total=xp_total,
            level=level,
            xp_current_level=xp_current_level,
            xp_next_level=xp_next_level
        )

    def add_xp(self, xp_earned: int) -> 'XPLevel':
        """
        Add XP and recalculate level.

        Args:
            xp_earned: XP to add

        Returns:
            New XPLevel instance with updated values
        """
        return XPLevel.calculate_level(self.xp_total + xp_earned)

    def progress_percentage(self) -> Decimal:
        """
        Get progress percentage to next level.

        Returns:
            Percentage (0-100)
        """
        total_for_level = self.xp_current_level + self.xp_next_level
        if total_for_level == 0:
            return Decimal("0")
        return Decimal(self.xp_current_level) / Decimal(total_for_level) * Decimal("100")


@dataclass(frozen=True)
class QuestReward:
    """
    Quest Reward Value Object.

    Represents rewards for completing quests.
    Immutable.

    Attributes:
        xp: XP reward
        tokens: Token reward (optional)
        items: Item rewards (optional)
    """
    xp: int
    tokens: int = 0
    items: Optional[list] = None

    def __post_init__(self):
        """Validate rewards"""
        if self.xp < 0:
            raise ValueError("XP reward cannot be negative")
        if self.tokens < 0:
            raise ValueError("Token reward cannot be negative")


@dataclass(frozen=True)
class RecallInterval:
    """
    Recall Interval Value Object (SM2 Algorithm).

    Represents spaced repetition interval for daily recall system.
    Immutable.

    Attributes:
        interval_days: Days until next review
        repetition_count: Number of successful repetitions
        easiness_factor: Easiness factor (1.3+)
        next_review_date: Next review date
    """
    interval_days: int
    repetition_count: int
    easiness_factor: Decimal
    next_review_date: datetime

    @staticmethod
    def initial() -> 'RecallInterval':
        """
        Create initial recall interval.

        Returns:
            RecallInterval with default values
        """
        return RecallInterval(
            interval_days=1,
            repetition_count=0,
            easiness_factor=Decimal("2.5"),
            next_review_date=datetime.utcnow() + timedelta(days=1)
        )

    def calculate_next(self, quality: int) -> 'RecallInterval':
        """
        Calculate next interval using SM2 algorithm.

        Args:
            quality: Quality of recall (0-5)
                     5: perfect recall
                     4: correct after hesitation
                     3: correct with difficulty
                     2: incorrect, but remembered
                     1: incorrect, familiar
                     0: complete blackout

        Returns:
            New RecallInterval instance

        Raises:
            ValueError: If quality not in range 0-5
        """
        if not 0 <= quality <= 5:
            raise ValueError("Quality must be between 0 and 5")

        # Calculate new easiness factor
        new_ef = self.easiness_factor + Decimal("0.1") - (Decimal("5") - Decimal(quality)) * (
            Decimal("0.08") + (Decimal("5") - Decimal(quality)) * Decimal("0.02")
        )

        # Easiness factor minimum is 1.3
        if new_ef < Decimal("1.3"):
            new_ef = Decimal("1.3")

        # Calculate new interval
        if quality < 3:
            # Failed recall - reset to 1 day
            new_interval = 1
            new_repetition = 0
        else:
            # Successful recall
            new_repetition = self.repetition_count + 1

            if new_repetition == 1:
                new_interval = 1
            elif new_repetition == 2:
                new_interval = 6
            else:
                new_interval = int(self.interval_days * float(new_ef))

        next_date = datetime.utcnow() + timedelta(days=new_interval)

        return RecallInterval(
            interval_days=new_interval,
            repetition_count=new_repetition,
            easiness_factor=new_ef,
            next_review_date=next_date
        )

    def is_due(self, current_time: datetime) -> bool:
        """
        Check if review is due.

        Args:
            current_time: Current timestamp

        Returns:
            True if review is due
        """
        return current_time >= self.next_review_date


@dataclass(frozen=True)
class DifficultyRating:
    """
    Difficulty Rating Value Object (ELO-based).

    Represents adaptive difficulty rating for a user.
    Immutable.

    Attributes:
        rating: Current ELO rating (1000-3000)
        k_factor: K-factor for rating changes (default: 32)
    """
    rating: int
    k_factor: int = 32

    def __post_init__(self):
        """Validate rating"""
        if not 1000 <= self.rating <= 3000:
            raise ValueError("Rating must be between 1000 and 3000")
        if self.k_factor <= 0:
            raise ValueError("K-factor must be positive")

    @staticmethod
    def initial() -> 'DifficultyRating':
        """
        Create initial difficulty rating.

        Returns:
            DifficultyRating with default values (1500 rating)
        """
        return DifficultyRating(rating=1500, k_factor=32)

    def expected_score(self, opponent_rating: int) -> Decimal:
        """
        Calculate expected score against opponent.

        Args:
            opponent_rating: Opponent's rating

        Returns:
            Expected score (0-1)
        """
        return Decimal("1") / (Decimal("1") + Decimal(10) ** ((Decimal(opponent_rating) - Decimal(self.rating)) / Decimal("400")))

    def calculate_new_rating(self, opponent_rating: int, actual_score: Decimal) -> 'DifficultyRating':
        """
        Calculate new rating after a match.

        Args:
            opponent_rating: Opponent's rating (task difficulty)
            actual_score: Actual score (0 = loss, 0.5 = draw, 1 = win)

        Returns:
            New DifficultyRating instance

        Raises:
            ValueError: If actual_score not between 0 and 1
        """
        if not 0 <= actual_score <= 1:
            raise ValueError("Actual score must be between 0 and 1")

        expected = self.expected_score(opponent_rating)
        change = self.k_factor * (float(actual_score) - float(expected))

        new_rating = int(self.rating + change)

        # Clamp rating between 1000 and 3000
        new_rating = max(1000, min(3000, new_rating))

        return DifficultyRating(rating=new_rating, k_factor=self.k_factor)

    def get_difficulty_level(self) -> str:
        """
        Get difficulty level name.

        Returns:
            Difficulty level (beginner, intermediate, advanced, expert, master)
        """
        if self.rating < 1200:
            return "beginner"
        elif self.rating < 1500:
            return "intermediate"
        elif self.rating < 1800:
            return "advanced"
        elif self.rating < 2200:
            return "expert"
        else:
            return "master"


@dataclass(frozen=True)
class Achievement:
    """
    Achievement Value Object.

    Represents an achievement with criteria.
    Immutable.

    Attributes:
        achievement_type: Type (bronze, silver, gold, platinum)
        name: Achievement name
        description: Achievement description
        criteria: Criteria to earn achievement
        reward_xp: XP reward for earning
    """
    achievement_type: AchievementTypeEnum
    name: str
    description: str
    criteria: dict
    reward_xp: int

    def __post_init__(self):
        """Validate achievement"""
        if not self.name:
            raise ValueError("Achievement name cannot be empty")
        if self.reward_xp < 0:
            raise ValueError("Reward XP cannot be negative")

    @staticmethod
    def bronze(name: str, description: str, criteria: dict, reward_xp: int = 100) -> 'Achievement':
        """Create bronze achievement"""
        return Achievement(
            achievement_type=AchievementTypeEnum.BRONZE,
            name=name,
            description=description,
            criteria=criteria,
            reward_xp=reward_xp
        )

    @staticmethod
    def silver(name: str, description: str, criteria: dict, reward_xp: int = 250) -> 'Achievement':
        """Create silver achievement"""
        return Achievement(
            achievement_type=AchievementTypeEnum.SILVER,
            name=name,
            description=description,
            criteria=criteria,
            reward_xp=reward_xp
        )

    @staticmethod
    def gold(name: str, description: str, criteria: dict, reward_xp: int = 500) -> 'Achievement':
        """Create gold achievement"""
        return Achievement(
            achievement_type=AchievementTypeEnum.GOLD,
            name=name,
            description=description,
            criteria=criteria,
            reward_xp=reward_xp
        )

    @staticmethod
    def platinum(name: str, description: str, criteria: dict, reward_xp: int = 1000) -> 'Achievement':
        """Create platinum achievement"""
        return Achievement(
            achievement_type=AchievementTypeEnum.PLATINUM,
            name=name,
            description=description,
            criteria=criteria,
            reward_xp=reward_xp
        )
