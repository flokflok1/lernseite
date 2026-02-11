"""
Feature Repository - Feature-Based Authorization Data Access

Implements feature access control queries (GBA - Group-Based Architecture):
- System feature metadata
- Organization feature subscriptions
- Granular feature permissions via groups

GBA: Users → Groups → Permissions (supersedes old RBAC 2.0 role-based system)
"""

from typing import Optional, List, Dict, Any
from app.infrastructure.persistence.repositories.core.base import BaseRepository
from app.infrastructure.persistence.database.connection import fetch_one, fetch_all, execute_query


class FeatureRepository(BaseRepository):
    """
    Repository for feature-based authorization queries.

    Implements feature access patterns with GBA:
    - System features by code
    - Organization subscriptions
    - User access via group-permission mappings
    """

    @classmethod
    def find_by_code(cls, feature_code: str) -> Optional[Dict[str, Any]]:
        """
        Find system feature by code.

        Args:
            feature_code: Feature code (e.g., 'ai_editor', 'code_sandbox')

        Returns:
            Feature dict with metadata or None if not found

        Example:
            >>> feature = FeatureRepository.find_by_code('ai_editor')
            >>> feature['feature_name']
            'AI-Studio'
        """
        try:
            result = fetch_one(
                """
                SELECT
                    feature_id,
                    feature_code,
                    feature_name,
                    description,
                    category,
                    requires_infrastructure,
                    requires_external_service,
                    active,
                    icon
                FROM support_systems.system_features
                WHERE feature_code = %s
                """,
                (feature_code,)
            )
            return result
        except Exception as e:
            import logging
            logging.error(f"Error finding feature {feature_code}: {e}")
            return None

    @classmethod
    def get_user_group_features(cls, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all features accessible to user via their groups (GBA).

        Args:
            user_id: User ID to query

        Returns:
            List of features with access levels

        Example:
            >>> features = FeatureRepository.get_user_group_features(user_id='user-123')
            >>> [f['feature_code'] for f in features]
            ['ai_editor', 'code_sandbox', 'learning_journal', ...]
        """
        try:
            results = fetch_all(
                """
                SELECT DISTINCT
                    sf.feature_id,
                    sf.feature_code,
                    sf.feature_name,
                    sf.description,
                    sf.category,
                    sf.icon,
                    g.name as group_name,
                    g.id as group_id
                FROM core.users_groups ug
                JOIN core.groups g ON ug.group_id = g.id
                JOIN support_systems.system_features sf
                    ON sf.feature_code = LOWER(g.slug)
                WHERE ug.user_id = %s
                    AND ug.is_active = TRUE
                    AND ug.left_at IS NULL
                    AND sf.active = TRUE
                ORDER BY sf.feature_name
                """,
                (user_id,)
            )
            return results or []
        except Exception as e:
            import logging
            logging.error(f"Error fetching user features for user {user_id}: {e}")
            return []

    @classmethod
    def get_org_subscribed_features(
        cls,
        org_id: str,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get all features subscribed to by organisation.

        Args:
            org_id: Organization ID
            active_only: Only return active subscriptions (default: True)

        Returns:
            List of subscribed features with tier info

        Example:
            >>> features = FeatureRepository.get_org_subscribed_features('org-123')
            >>> [f['feature_code'] for f in features]
            ['ai_editor', 'whiteboard_engine', ...]
        """
        try:
            where_clause = "fs.organisation_id = %s"
            params = [org_id]

            if active_only:
                where_clause += " AND fs.is_active = TRUE"

            results = fetch_all(
                f"""
                SELECT
                    fs.id,
                    fs.organisation_id,
                    fs.feature_code,
                    fs.tier,
                    fs.is_active,
                    fs.enabled_at,
                    fs.expires_at,
                    sf.feature_name,
                    sf.description,
                    sf.category,
                    sf.icon
                FROM organisations.feature_subscriptions fs
                JOIN support_systems.system_features sf
                    ON fs.feature_code = sf.feature_code
                WHERE {where_clause}
                ORDER BY sf.feature_name
                """,
                params
            )
            return results or []
        except Exception as e:
            import logging
            logging.error(
                f"Error fetching org subscriptions for org {org_id}: {e}"
            )
            return []

    @classmethod
    def check_user_group_feature_access(
        cls,
        user_id: str,
        feature_code: str
    ) -> bool:
        """
        Check if user has access to a feature via their groups (GBA).

        Args:
            user_id: User ID
            feature_code: Feature code

        Returns:
            True if user's groups provide access to feature, False otherwise

        Example:
            >>> can_access = FeatureRepository.check_user_group_feature_access(
            ...     'user-123', 'ai_editor'
            ... )
            >>> can_access
            True
        """
        try:
            result = fetch_one(
                """
                SELECT 1 FROM core.users_groups ug
                JOIN core.groups g ON ug.group_id = g.id
                JOIN support_systems.system_features sf
                    ON sf.feature_code = LOWER(g.slug)
                WHERE ug.user_id = %s
                    AND sf.feature_code = %s
                    AND ug.is_active = TRUE
                    AND ug.left_at IS NULL
                    AND sf.active = TRUE
                LIMIT 1
                """,
                (user_id, feature_code)
            )
            return result is not None
        except Exception as e:
            import logging
            logging.error(
                f"Error checking user feature access ({user_id}, {feature_code}): {e}"
            )
            return False

    @classmethod
    def check_org_feature_subscription(
        cls,
        org_id: str,
        feature_code: str,
        check_expiry: bool = True
    ) -> bool:
        """
        Check if organisation has active subscription to feature.

        Args:
            org_id: Organization ID
            feature_code: Feature code
            check_expiry: Check expiration date (default: True)

        Returns:
            True if org has active subscription, False otherwise

        Example:
            >>> has_sub = FeatureRepository.check_org_feature_subscription(
            ...     'org-123', 'ai_editor', check_expiry=True
            ... )
            >>> has_sub
            True
        """
        try:
            where_clause = (
                "organisation_id = %s AND feature_code = %s AND is_active = TRUE"
            )
            params = [org_id, feature_code]

            if check_expiry:
                where_clause += (
                    " AND (expires_at IS NULL OR expires_at > NOW())"
                )

            result = fetch_one(
                f"""
                SELECT 1 FROM organisations.feature_subscriptions
                WHERE {where_clause}
                LIMIT 1
                """,
                params
            )
            return result is not None
        except Exception as e:
            import logging
            logging.error(
                f"Error checking org subscription ({org_id}, {feature_code}): {e}"
            )
            return False

    @classmethod
    def get_org_feature_tier(
        cls,
        org_id: str,
        feature_code: str
    ) -> Optional[str]:
        """
        Get subscription tier for organisation feature.

        Args:
            org_id: Organization ID
            feature_code: Feature code

        Returns:
            Tier string (e.g., 'basic', 'premium') or None if not subscribed

        Example:
            >>> tier = FeatureRepository.get_org_feature_tier('org-123', 'ai_editor')
            >>> tier
            'premium'
        """
        try:
            result = fetch_one(
                """
                SELECT tier FROM organisations.feature_subscriptions
                WHERE organisation_id = %s AND feature_code = %s AND is_active = TRUE
                LIMIT 1
                """,
                (org_id, feature_code)
            )
            return result.get('tier') if result else None
        except Exception as e:
            import logging
            logging.error(
                f"Error getting org feature tier ({org_id}, {feature_code}): {e}"
            )
            return None

    @classmethod
    def count_org_features(
        cls,
        org_id: str,
        tier: Optional[str] = None,
        active_only: bool = True
    ) -> int:
        """
        Count features subscribed by organisation.

        Args:
            org_id: Organization ID
            tier: Optional tier filter
            active_only: Only count active subscriptions

        Returns:
            Count of features
        """
        try:
            where_clause = "organisation_id = %s"
            params = [org_id]

            if active_only:
                where_clause += " AND is_active = TRUE"

            if tier:
                where_clause += " AND tier = %s"
                params.append(tier)

            result = fetch_one(
                f"""
                SELECT COUNT(*) as count FROM organisations.feature_subscriptions
                WHERE {where_clause}
                """,
                params
            )

            return result.get('count', 0) if result else 0
        except Exception as e:
            import logging
            logging.error(f"Error counting org features for {org_id}: {e}")
            return 0

    @classmethod
    def list_all_features(cls, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        List all system features.

        Args:
            active_only: Only active features (default: True)

        Returns:
            List of all features

        Example:
            >>> features = FeatureRepository.list_all_features()
            >>> len(features)
            25
        """
        try:
            where_clause = "WHERE active = TRUE" if active_only else ""

            results = fetch_all(
                f"""
                SELECT
                    feature_code,
                    feature_name,
                    description,
                    category,
                    requires_infrastructure,
                    requires_external_service,
                    active,
                    icon
                FROM support_systems.system_features
                {where_clause}
                ORDER BY category, feature_name
                """
            )
            return results or []
        except Exception as e:
            import logging
            logging.error(f"Error listing features: {e}")
            return []
