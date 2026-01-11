"""
Gamification Repository

Handles database operations for gamification system (XP, Quests, Achievements, Recall, Difficulty).

DDD Repository Pattern - Single source of truth for gamification data access.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from app.repositories.base_repository import BaseRepository


class GamificationRepository:
    """
    Repository for Gamification operations.

    Handles:
    - XP & Level tracking
    - Quests (CRUD & progress)
    - Achievements (CRUD & unlocks)
    - Daily Recall (spaced repetition)
    - Adaptive Difficulty (ELO ratings)
    """

    # ========================================================================
    # XP & Level
    # ========================================================================

    @staticmethod
    def get_user_xp(user_id: str) -> Optional[Dict]:
        """Get user XP and level"""
        query = "SELECT user_id, xp_total, level, created_at, updated_at FROM user_xp WHERE user_id = %s"
        return BaseRepository.fetch_one(query, (user_id,))

    @staticmethod
    def add_xp(user_id: str, xp_amount: int, source: str) -> Dict:
        """Add XP to user"""
        query = """
            INSERT INTO user_xp (user_id, xp_total, level)
            VALUES (%s, %s, 1)
            ON CONFLICT (user_id) DO UPDATE SET
                xp_total = user_xp.xp_total + %s,
                updated_at = NOW()
            RETURNING user_id, xp_total, level
        """
        result = BaseRepository.fetch_one(query, (user_id, xp_amount, xp_amount))

        # Log XP transaction
        log_query = """
            INSERT INTO xp_transactions (user_id, xp_amount, source, created_at)
            VALUES (%s, %s, %s, NOW())
        """
        BaseRepository.execute(log_query, (user_id, xp_amount, source))

        return result

    @staticmethod
    def update_level(user_id: str, new_level: int) -> bool:
        """Update user level"""
        query = "UPDATE user_xp SET level = %s, updated_at = NOW() WHERE user_id = %s"
        BaseRepository.execute(query, (new_level, user_id))
        return True

    # ========================================================================
    # Quests
    # ========================================================================

    @staticmethod
    def create_quest(quest_data: Dict[str, Any]) -> Dict:
        """Create a quest"""
        query = """
            INSERT INTO quests (quest_type, title, description, criteria, reward_xp, reward_tokens,
                                expires_at, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING quest_id, quest_type, title, description, reward_xp, reward_tokens, is_active
        """
        import json
        return BaseRepository.fetch_one(query, (
            quest_data.get('quest_type'),
            quest_data.get('title'),
            quest_data.get('description'),
            json.dumps(quest_data.get('criteria', {})),
            quest_data.get('reward_xp', 100),
            quest_data.get('reward_tokens', 0),
            quest_data.get('expires_at'),
            quest_data.get('is_active', True)
        ))

    @staticmethod
    def get_active_quests(quest_type: Optional[str] = None) -> List[Dict]:
        """Get all active quests"""
        if quest_type:
            query = """
                SELECT quest_id, quest_type, title, description, criteria, reward_xp, reward_tokens, expires_at
                FROM quests
                WHERE is_active = TRUE AND quest_type = %s AND (expires_at IS NULL OR expires_at > NOW())
                ORDER BY created_at DESC
            """
            return BaseRepository.fetch_all(query, (quest_type,)) or []
        else:
            query = """
                SELECT quest_id, quest_type, title, description, criteria, reward_xp, reward_tokens, expires_at
                FROM quests
                WHERE is_active = TRUE AND (expires_at IS NULL OR expires_at > NOW())
                ORDER BY quest_type, created_at DESC
            """
            return BaseRepository.fetch_all(query) or []

    @staticmethod
    def get_user_quest_progress(user_id: str, quest_id: str) -> Optional[Dict]:
        """Get user's progress on a quest"""
        query = """
            SELECT uq.user_quest_id, uq.user_id, uq.quest_id, uq.status, uq.progress,
                   uq.completed_at, q.title, q.criteria, q.reward_xp
            FROM user_quests uq
            JOIN quests q ON uq.quest_id = q.quest_id
            WHERE uq.user_id = %s AND uq.quest_id = %s
        """
        return BaseRepository.fetch_one(query, (user_id, quest_id))

    @staticmethod
    def start_quest(user_id: str, quest_id: str) -> Dict:
        """Start a quest for user"""
        query = """
            INSERT INTO user_quests (user_id, quest_id, status, progress)
            VALUES (%s, %s, 'in_progress', 0)
            ON CONFLICT (user_id, quest_id) DO UPDATE SET status = 'in_progress', updated_at = NOW()
            RETURNING user_quest_id, user_id, quest_id, status, progress
        """
        return BaseRepository.fetch_one(query, (user_id, quest_id))

    @staticmethod
    def update_quest_progress(user_id: str, quest_id: str, progress: int) -> Dict:
        """Update quest progress"""
        query = """
            UPDATE user_quests
            SET progress = %s, updated_at = NOW()
            WHERE user_id = %s AND quest_id = %s
            RETURNING user_quest_id, status, progress
        """
        return BaseRepository.fetch_one(query, (progress, user_id, quest_id))

    @staticmethod
    def complete_quest(user_id: str, quest_id: str) -> Dict:
        """Complete a quest"""
        query = """
            UPDATE user_quests
            SET status = 'completed', progress = 100, completed_at = NOW()
            WHERE user_id = %s AND quest_id = %s
            RETURNING user_quest_id, status, completed_at
        """
        return BaseRepository.fetch_one(query, (user_id, quest_id))

    # ========================================================================
    # Achievements
    # ========================================================================

    @staticmethod
    def create_achievement(achievement_data: Dict[str, Any]) -> Dict:
        """Create an achievement"""
        query = """
            INSERT INTO achievements (achievement_type, name, description, criteria, reward_xp, icon, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING achievement_id, achievement_type, name, description, reward_xp, icon
        """
        import json
        return BaseRepository.fetch_one(query, (
            achievement_data.get('achievement_type'),
            achievement_data.get('name'),
            achievement_data.get('description'),
            json.dumps(achievement_data.get('criteria', {})),
            achievement_data.get('reward_xp', 100),
            achievement_data.get('icon', 'trophy'),
            achievement_data.get('is_active', True)
        ))

    @staticmethod
    def get_all_achievements() -> List[Dict]:
        """Get all active achievements"""
        query = """
            SELECT achievement_id, achievement_type, name, description, criteria, reward_xp, icon
            FROM achievements
            WHERE is_active = TRUE
            ORDER BY achievement_type, created_at
        """
        return BaseRepository.fetch_all(query) or []

    @staticmethod
    def get_user_achievements(user_id: str) -> List[Dict]:
        """Get user's unlocked achievements"""
        query = """
            SELECT ua.user_achievement_id, ua.achievement_id, ua.unlocked_at,
                   a.achievement_type, a.name, a.description, a.reward_xp, a.icon
            FROM user_achievements ua
            JOIN achievements a ON ua.achievement_id = a.achievement_id
            WHERE ua.user_id = %s
            ORDER BY ua.unlocked_at DESC
        """
        return BaseRepository.fetch_all(query, (user_id,)) or []

    @staticmethod
    def unlock_achievement(user_id: str, achievement_id: str) -> Dict:
        """Unlock an achievement for user"""
        query = """
            INSERT INTO user_achievements (user_id, achievement_id, unlocked_at)
            VALUES (%s, %s, NOW())
            ON CONFLICT (user_id, achievement_id) DO NOTHING
            RETURNING user_achievement_id, achievement_id, unlocked_at
        """
        return BaseRepository.fetch_one(query, (user_id, achievement_id))

    # ========================================================================
    # Daily Recall (Spaced Repetition)
    # ========================================================================

    @staticmethod
    def get_due_recalls(user_id: str, limit: int = 20) -> List[Dict]:
        """Get due recall cards for user"""
        query = """
            SELECT rc.recall_card_id, rc.content_type, rc.content_id, rc.interval_days,
                   rc.repetition_count, rc.easiness_factor, rc.next_review_date
            FROM recall_cards rc
            WHERE rc.user_id = %s AND rc.next_review_date <= NOW()
            ORDER BY rc.next_review_date ASC
            LIMIT %s
        """
        return BaseRepository.fetch_all(query, (user_id, limit)) or []

    @staticmethod
    def create_recall_card(user_id: str, content_type: str, content_id: str) -> Dict:
        """Create a new recall card"""
        query = """
            INSERT INTO recall_cards (user_id, content_type, content_id, interval_days,
                                      repetition_count, easiness_factor, next_review_date)
            VALUES (%s, %s, %s, 1, 0, 2.5, NOW() + INTERVAL '1 day')
            RETURNING recall_card_id, content_type, content_id, next_review_date
        """
        return BaseRepository.fetch_one(query, (user_id, content_type, content_id))

    @staticmethod
    def update_recall_card(recall_card_id: str, interval_days: int, repetition_count: int,
                          easiness_factor: float, next_review_date: datetime) -> Dict:
        """Update recall card after review"""
        query = """
            UPDATE recall_cards
            SET interval_days = %s, repetition_count = %s, easiness_factor = %s,
                next_review_date = %s, last_reviewed_at = NOW()
            WHERE recall_card_id = %s
            RETURNING recall_card_id, interval_days, next_review_date
        """
        return BaseRepository.fetch_one(query, (
            interval_days, repetition_count, easiness_factor, next_review_date, recall_card_id
        ))

    # ========================================================================
    # Adaptive Difficulty
    # ========================================================================

    @staticmethod
    def get_user_difficulty(user_id: str, domain: str = 'general') -> Optional[Dict]:
        """Get user's difficulty rating for a domain"""
        query = """
            SELECT difficulty_id, user_id, domain, rating, k_factor, updated_at
            FROM user_difficulty
            WHERE user_id = %s AND domain = %s
        """
        return BaseRepository.fetch_one(query, (user_id, domain))

    @staticmethod
    def update_difficulty_rating(user_id: str, domain: str, new_rating: int) -> Dict:
        """Update user's difficulty rating"""
        query = """
            INSERT INTO user_difficulty (user_id, domain, rating, k_factor)
            VALUES (%s, %s, %s, 32)
            ON CONFLICT (user_id, domain) DO UPDATE SET
                rating = %s, updated_at = NOW()
            RETURNING difficulty_id, user_id, domain, rating
        """
        return BaseRepository.fetch_one(query, (user_id, domain, new_rating, new_rating))
