"""UserGamification Entity"""
from dataclasses import dataclass
from decimal import Decimal

@dataclass
class UserGamification:
    """User gamification stats."""
    user_id: str
    total_xp: int = 0
    level: int = 1
    streak_days: int = 0
    badges_earned: int = 0
    
    def level_up(self) -> None:
        if self.total_xp >= (self.level * 1000):
            self.level += 1
