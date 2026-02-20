"""
Feature Flag Seed Repository - Database Initialization

Handles seed/bootstrap operations for feature flags:
- Initial flag creation from config
- Feature group seeding
- Segment and rollout initialization
"""

from datetime import datetime
from typing import Dict, List
from app.infrastructure.persistence.database.connection import get_db_connection


class FeatureFlagSeedRepository:
    """
    Repository for feature flag seed operations.

    Uses get_db_connection() context manager for explicit transaction control
    since seed operations need batch commits.
    """

    @classmethod
    def seed_flags(cls, flags: Dict[str, bool]) -> int:
        """
        Upsert all feature flags from config.

        Args:
            flags: Dict mapping feature_name -> default enabled state

        Returns:
            Number of flags seeded
        """
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                for feature_name, default_state in flags.items():
                    cur.execute(
                        """
                        INSERT INTO feature_flags (name, is_enabled, created_at, updated_at)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (name) DO UPDATE
                        SET is_enabled = EXCLUDED.is_enabled, updated_at = EXCLUDED.updated_at
                        """,
                        (feature_name, default_state, datetime.utcnow(), datetime.utcnow())
                    )
                conn.commit()
        return len(flags)

    @classmethod
    def seed_groups(cls, groups: Dict[str, List[str]]) -> int:
        """
        Upsert feature flag groups.

        Args:
            groups: Dict mapping group_name -> list of feature_names

        Returns:
            Number of groups seeded
        """
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                for group_name, feature_list in groups.items():
                    for feature_name in feature_list:
                        cur.execute(
                            """
                            INSERT INTO feature_flag_groups (group_name, feature_name, created_at)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (group_name, feature_name) DO NOTHING
                            """,
                            (group_name, feature_name, datetime.utcnow())
                        )
                conn.commit()
        return len(groups)

    @classmethod
    def seed_segment(cls, feature_name: str, segment: str, is_enabled: bool = True) -> None:
        """
        Enable/disable a feature for a specific segment.

        Args:
            feature_name: Feature flag name
            segment: Segment name (e.g., 'beta', 'premium')
            is_enabled: Whether to enable for segment
        """
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO feature_flag_segments (feature_name, segment, is_enabled, created_at)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (feature_name, segment) DO UPDATE
                    SET is_enabled = EXCLUDED.is_enabled
                    """,
                    (feature_name, segment, is_enabled, datetime.utcnow())
                )
                conn.commit()

    @classmethod
    def seed_rollout(cls, feature_name: str, percentage: int) -> None:
        """
        Set percentage rollout for a feature.

        Args:
            feature_name: Feature flag name
            percentage: 0-100
        """
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO feature_flag_rollouts (feature_name, percentage, created_at, updated_at)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (feature_name) DO UPDATE
                    SET percentage = EXCLUDED.percentage, updated_at = EXCLUDED.updated_at
                    """,
                    (feature_name, percentage, datetime.utcnow(), datetime.utcnow())
                )
                conn.commit()
