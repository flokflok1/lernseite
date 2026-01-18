"""
Feature Repository - Feature-Based Authorization Data Access

Implements feature access control queries:
- Role-to-Feature mapping
- Organization feature subscriptions
- Granular feature permissions

RBAC 2.0: Database-driven feature authorization (separate from permission thresholds).
"""

from typing import Optional, List, Dict, Any
from app.infrastructure.persistence.repositories.base_repository import BaseRepository
from app.infrastructure.persistence.database.connection import fetch_one, fetch_all, execute_query


class FeatureRepository(BaseRepository):
    """
    Repository for feature-based authorization queries.

    Implements feature access patterns:
    - Role-Feature access mapping
    - Organization subscriptions
    - Granular permissions within features
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
    def get_role_features(cls, role_id: int) -> List[Dict[str, Any]]:
        """
        Get all features accessible to a role.

        Args:
            role_id: Role ID to query

        Returns:
            List of features with access levels

        Example:
            >>> features = FeatureRepository.get_role_features(role_id=2)
            >>> [f['feature_code'] for f in features]
            ['ai_editor', 'code_sandbox', 'learning_journal', ...]
        """
        try:
            results = fetch_all(
                """
                SELECT DISTINCT
                    rf.id,
                    rf.role_id,
                    rf.feature_code,
                    rf.access_level,
                    rf.enabled,
                    sf.feature_name,
                    sf.description,
                    sf.category,
                    sf.icon
                FROM roles.role_features rf
                JOIN support_systems.system_features sf
                    ON rf.feature_code = sf.feature_code
                WHERE rf.role_id = %s AND rf.enabled = TRUE
                ORDER BY sf.feature_name
                """,
                (role_id,)
            )
            return results or []
        except Exception as e:
            import logging
            logging.error(f"Error fetching role features for role {role_id}: {e}")
            return []

    @classmethod
    def get_org_subscribed_features(
        cls,
        org_id: str,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get all features subscribed to by organization.

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
    def check_role_feature_access(
        cls,
        role_id: int,
        feature_code: str
    ) -> bool:
        """
        Check if role has access to a feature.

        Args:
            role_id: Role ID
            feature_code: Feature code

        Returns:
            True if role can access feature, False otherwise

        Example:
            >>> can_access = FeatureRepository.check_role_feature_access(2, 'ai_editor')
            >>> can_access
            True
        """
        try:
            result = fetch_one(
                """
                SELECT 1 FROM roles.role_features
                WHERE role_id = %s AND feature_code = %s AND enabled = TRUE
                LIMIT 1
                """,
                (role_id, feature_code)
            )
            return result is not None
        except Exception as e:
            import logging
            logging.error(
                f"Error checking role feature access ({role_id}, {feature_code}): {e}"
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
        Check if organization has active subscription to feature.

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
    def get_feature_permission(
        cls,
        role_id: int,
        feature_code: str,
        permission_key: str
    ) -> Optional[bool]:
        """
        Get specific permission for role within feature.

        Args:
            role_id: Role ID
            feature_code: Feature code
            permission_key: Permission key (e.g., 'ai_editor.execute')

        Returns:
            True if allowed, False if denied, None if not defined

        Example:
            >>> allowed = FeatureRepository.get_feature_permission(
            ...     2, 'ai_editor', 'ai_editor.execute'
            ... )
            >>> allowed
            True
        """
        try:
            result = fetch_one(
                """
                SELECT allowed FROM roles.feature_permissions
                WHERE role_id = %s AND feature_code = %s AND permission_key = %s
                """,
                (role_id, feature_code, permission_key)
            )

            if result:
                return result.get('allowed')
            return None
        except Exception as e:
            import logging
            logging.error(
                f"Error getting feature permission ({role_id}, {feature_code}, {permission_key}): {e}"
            )
            return None

    @classmethod
    def get_all_role_feature_permissions(
        cls,
        role_id: int,
        feature_code: str
    ) -> Dict[str, bool]:
        """
        Get all permissions for role within a feature.

        Args:
            role_id: Role ID
            feature_code: Feature code

        Returns:
            Dictionary of {permission_key: allowed}

        Example:
            >>> perms = FeatureRepository.get_all_role_feature_permissions(2, 'ai_editor')
            >>> perms
            {'ai_editor.execute': True, 'ai_editor.manage': False}
        """
        try:
            results = fetch_all(
                """
                SELECT permission_key, allowed
                FROM roles.feature_permissions
                WHERE role_id = %s AND feature_code = %s
                """,
                (role_id, feature_code)
            )

            permissions = {}
            for row in results:
                permissions[row['permission_key']] = row['allowed']

            return permissions
        except Exception as e:
            import logging
            logging.error(
                f"Error getting role feature permissions ({role_id}, {feature_code}): {e}"
            )
            return {}

    @classmethod
    def count_org_features(
        cls,
        org_id: str,
        tier: Optional[str] = None,
        active_only: bool = True
    ) -> int:
        """
        Count features subscribed by organization.

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
