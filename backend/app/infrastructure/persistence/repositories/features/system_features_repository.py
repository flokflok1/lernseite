"""
LernsystemX System Features Repository

Data access layer for system feature management.
Handles CRUD operations for support_systems.system_features table.
"""

from typing import Dict, List, Optional, Any

from app.infrastructure.persistence.repositories.core.base import BaseRepository
from app.infrastructure.persistence.database.connection import (
    fetch_one,
    fetch_all,
    update_returning
)


class SystemFeaturesRepository(BaseRepository):
    """
    Repository for support_systems.system_features table.

    System features are tools/services separate from Content-LMs:
    - whiteboard_engine
    - it_sandbox
    - npc_tutor
    - etc.
    """

    table_name = "support_systems.system_features"
    pk_column = "feature_id"

    @classmethod
    def find_by_code(cls, feature_code: str) -> Optional[Dict]:
        """
        Find feature by unique code.

        Args:
            feature_code: Unique feature identifier

        Returns:
            Feature dict or None
        """
        query = f"""
            SELECT * FROM {cls.table_name}
            WHERE feature_code = %s
        """
        return fetch_one(query, (feature_code,))

    @classmethod
    def find_active(cls, category: Optional[str] = None) -> List[Dict]:
        """
        Find all active features, optionally filtered by category.

        Args:
            category: Optional category filter

        Returns:
            List of active feature dicts
        """
        if category:
            query = f"""
                SELECT * FROM {cls.table_name}
                WHERE active = TRUE AND category = %s
                ORDER BY category, feature_name
            """
            return fetch_all(query, (category,))
        else:
            query = f"""
                SELECT * FROM {cls.table_name}
                WHERE active = TRUE
                ORDER BY category, feature_name
            """
            return fetch_all(query)

    @classmethod
    def find_by_category(cls, category: str) -> List[Dict]:
        """
        Find all features in a category.

        Args:
            category: Category name

        Returns:
            List of feature dicts
        """
        query = f"""
            SELECT * FROM {cls.table_name}
            WHERE category = %s
            ORDER BY feature_name
        """
        return fetch_all(query, (category,))

    @classmethod
    def get_categories(cls) -> List[str]:
        """
        Get all distinct feature categories.

        Returns:
            List of category names
        """
        query = """
            SELECT DISTINCT category
            FROM support_systems.system_features
            ORDER BY category
        """
        results = fetch_all(query)
        return [r['category'] for r in results] if results else []

    @classmethod
    def update_feature(cls, feature_id: int, data: Dict[str, Any]) -> Optional[Dict]:
        """
        Update feature by ID.

        Allowed fields:
        - active: Boolean
        - config: JSONB
        - feature_name: String (display name)

        Args:
            feature_id: Primary key
            data: Fields to update

        Returns:
            Updated feature dict
        """
        # Filter to allowed fields only
        allowed_fields = {'active', 'config', 'feature_name', 'description', 'icon'}
        filtered_data = {k: v for k, v in data.items() if k in allowed_fields}

        if not filtered_data:
            return cls.find_by_id(feature_id)

        return cls.update(feature_id, filtered_data)

    @classmethod
    def toggle_active(cls, feature_id: int, active: bool) -> Optional[Dict]:
        """
        Toggle feature active status.

        Args:
            feature_id: Primary key
            active: New active status

        Returns:
            Updated feature dict
        """
        return cls.update(feature_id, {'active': active})

    @classmethod
    def update_config(cls, feature_id: int, config: Dict[str, Any]) -> Optional[Dict]:
        """
        Update feature config JSONB.

        Args:
            feature_id: Primary key
            config: New config dict (replaces existing)

        Returns:
            Updated feature dict
        """
        return cls.update(feature_id, {'config': config})

    @classmethod
    def merge_config(cls, feature_id: int, config_updates: Dict[str, Any]) -> Optional[Dict]:
        """
        Merge updates into feature config JSONB.

        Args:
            feature_id: Primary key
            config_updates: Config fields to merge

        Returns:
            Updated feature dict
        """
        query = """
            UPDATE support_systems.system_features
            SET config = config || %s,
                updated_at = NOW()
            WHERE feature_id = %s
            RETURNING *
        """
        import json
        return fetch_one(query, (json.dumps(config_updates), feature_id))

    @classmethod
    def find_by_codes(cls, feature_codes: List[str]) -> List[Dict]:
        """
        Find multiple features by codes.

        Args:
            feature_codes: List of feature codes

        Returns:
            List of feature dicts
        """
        if not feature_codes:
            return []

        placeholders = ', '.join(['%s'] * len(feature_codes))
        query = f"""
            SELECT * FROM {cls.table_name}
            WHERE feature_code IN ({placeholders})
            ORDER BY category, feature_name
        """
        return fetch_all(query, tuple(feature_codes))

    @classmethod
    def find_requiring_infrastructure(cls) -> List[Dict]:
        """
        Find features that require infrastructure.

        Returns:
            List of infrastructure-dependent features
        """
        query = f"""
            SELECT * FROM {cls.table_name}
            WHERE requires_infrastructure = TRUE AND active = TRUE
            ORDER BY category, feature_name
        """
        return fetch_all(query)

    @classmethod
    def find_requiring_external_service(cls) -> List[Dict]:
        """
        Find features that require external services.

        Returns:
            List of external-service-dependent features
        """
        query = f"""
            SELECT * FROM {cls.table_name}
            WHERE requires_external_service = TRUE AND active = TRUE
            ORDER BY category, feature_name
        """
        return fetch_all(query)


class CourseSystemFeaturesRepository(BaseRepository):
    """
    Repository for support_systems.course_system_features table.

    Manages course-level feature activation.
    """

    table_name = "support_systems.course_system_features"
    pk_column = "mapping_id"

    @classmethod
    def find_by_course(cls, course_id: str) -> List[Dict]:
        """
        Find all feature mappings for a course.

        Args:
            course_id: Course UUID

        Returns:
            List of feature mapping dicts with feature details
        """
        query = """
            SELECT
                csf.*,
                sf.feature_code,
                sf.feature_name,
                sf.category,
                sf.icon,
                sf.requires_infrastructure,
                sf.requires_external_service
            FROM support_systems.course_system_features csf
            JOIN support_systems.system_features sf ON csf.feature_id = sf.feature_id
            WHERE csf.course_id = %s::uuid AND sf.active = TRUE
            ORDER BY sf.category, sf.feature_name
        """
        return fetch_all(query, (course_id,))

    @classmethod
    def get_enabled_features(cls, course_id: str) -> List[Dict]:
        """
        Get only enabled features for a course.

        Args:
            course_id: Course UUID

        Returns:
            List of enabled feature dicts
        """
        query = """
            SELECT
                sf.*,
                csf.config_override
            FROM support_systems.course_system_features csf
            JOIN support_systems.system_features sf ON csf.feature_id = sf.feature_id
            WHERE csf.course_id = %s::uuid
              AND csf.enabled = TRUE
              AND sf.active = TRUE
            ORDER BY sf.category, sf.feature_name
        """
        return fetch_all(query, (course_id,))
