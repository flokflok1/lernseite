"""
Feature Flag Repository - Dark Launch System Data Access

Handles all database operations for feature flags:
- Global flag lookups
- User-specific overrides
- Organization-specific overrides
- Segment-based flags
- Percentage rollouts

Used by: FeatureFlagManager (app/core/feature_flags/management/manager.py)
"""

from typing import Optional, Dict, List, Any
from app.infrastructure.persistence.database.connection import fetch_one, fetch_all, execute_query


class FeatureFlagRepository:
    """
    Repository for feature flag CRUD operations.

    Pattern A: @classmethod + global helpers (fetch_one, fetch_all, execute_query)
    """

    # ==================== READ OPERATIONS ====================

    @classmethod
    def get_global_flag(cls, feature_name: str) -> Optional[Dict[str, Any]]:
        """Get global feature flag status."""
        return fetch_one(
            "SELECT is_enabled FROM feature_flags WHERE name = %s",
            (feature_name,)
        )

    @classmethod
    def get_user_override(cls, feature_name: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user-specific feature flag override."""
        return fetch_one(
            """
            SELECT is_enabled FROM feature_flag_user_overrides
            WHERE feature_name = %s AND user_id = %s
            """,
            (feature_name, user_id)
        )

    @classmethod
    def get_org_override(cls, feature_name: str, org_id: str) -> Optional[Dict[str, Any]]:
        """Get organization-specific feature flag override."""
        return fetch_one(
            """
            SELECT is_enabled FROM feature_flag_org_overrides
            WHERE feature_name = %s AND organisation_id = %s
            """,
            (feature_name, org_id)
        )

    @classmethod
    def get_segment_config(cls, feature_name: str, segment: str) -> Optional[Dict[str, Any]]:
        """Get segment-based feature flag config."""
        return fetch_one(
            """
            SELECT is_enabled FROM feature_flag_segments
            WHERE feature_name = %s AND segment = %s
            """,
            (feature_name, segment)
        )

    @classmethod
    def get_rollout_percentage(cls, feature_name: str) -> Optional[Dict[str, Any]]:
        """Get percentage rollout config for feature."""
        return fetch_one(
            """
            SELECT percentage FROM feature_flag_rollouts
            WHERE feature_name = %s
            """,
            (feature_name,)
        )

    @classmethod
    def get_all_flags(cls) -> List[Dict[str, Any]]:
        """Get all feature flags ordered by name."""
        return fetch_all(
            """
            SELECT name, is_enabled, created_at, updated_at
            FROM feature_flags
            ORDER BY name
            """
        )

    # ==================== WRITE OPERATIONS ====================

    @classmethod
    def upsert_global_flag(cls, feature_name: str, is_enabled: bool) -> None:
        """Enable or disable a feature globally."""
        execute_query(
            """
            INSERT INTO feature_flags (name, is_enabled)
            VALUES (%s, %s)
            ON CONFLICT (name) DO UPDATE SET is_enabled = %s
            """,
            (feature_name, is_enabled, is_enabled)
        )

    @classmethod
    def upsert_user_override(cls, feature_name: str, user_id: str, is_enabled: bool) -> None:
        """Set user-specific feature flag override."""
        execute_query(
            """
            INSERT INTO feature_flag_user_overrides (feature_name, user_id, is_enabled)
            VALUES (%s, %s, %s)
            ON CONFLICT (feature_name, user_id) DO UPDATE SET is_enabled = %s
            """,
            (feature_name, user_id, is_enabled, is_enabled)
        )

    @classmethod
    def upsert_org_override(cls, feature_name: str, org_id: str, is_enabled: bool) -> None:
        """Set organization-specific feature flag override."""
        execute_query(
            """
            INSERT INTO feature_flag_org_overrides (feature_name, organisation_id, is_enabled)
            VALUES (%s, %s, %s)
            ON CONFLICT (feature_name, organisation_id) DO UPDATE SET is_enabled = %s
            """,
            (feature_name, org_id, is_enabled, is_enabled)
        )

    @classmethod
    def update_global_flag(cls, feature_name: str, is_enabled: bool) -> None:
        """Update existing global flag status."""
        execute_query(
            """
            UPDATE feature_flags SET is_enabled = %s
            WHERE name = %s
            """,
            (is_enabled, feature_name)
        )

    @classmethod
    def update_user_override(cls, feature_name: str, user_id: str, is_enabled: bool) -> None:
        """Update existing user override status."""
        execute_query(
            """
            UPDATE feature_flag_user_overrides SET is_enabled = %s
            WHERE feature_name = %s AND user_id = %s
            """,
            (is_enabled, feature_name, user_id)
        )

    @classmethod
    def update_org_override(cls, feature_name: str, org_id: str, is_enabled: bool) -> None:
        """Update existing organization override status."""
        execute_query(
            """
            UPDATE feature_flag_org_overrides SET is_enabled = %s
            WHERE feature_name = %s AND organisation_id = %s
            """,
            (is_enabled, feature_name, org_id)
        )

    @classmethod
    def upsert_rollout_percentage(cls, feature_name: str, percentage: int) -> None:
        """Set percentage rollout for feature."""
        execute_query(
            """
            INSERT INTO feature_flag_rollouts (feature_name, percentage)
            VALUES (%s, %s)
            ON CONFLICT (feature_name) DO UPDATE SET percentage = %s
            """,
            (feature_name, percentage, percentage)
        )
