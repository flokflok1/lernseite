"""
LernsystemX Feature Configuration Repositories - Part 1

Data access layer for Enterprise Feature Configuration System:
- Feature flags (CRUD)
- Role-based access control

Phase 1b - Repository Layer Implementation (Part 1)
Using BaseRepository pattern with psycopg3 (NO ORM)

For Tier, Rollout, A/B Test, and Cache repositories see:
- feature_configuration_part2.py
"""

from typing import Optional, Dict, List, Any
from datetime import datetime

from app.database.connection import (
    fetch_one,
    fetch_all,
    insert_returning,
    update_returning,
    delete_returning,
    execute_query
)


# ==================== FEATURE CONFIGURATION REPOSITORY ====================

class FeatureConfigurationRepository:
    """
    Repository for global feature flags (feature_flags table)

    Handles CRUD operations for feature flags and their basic configuration.
    """

    table_name = 'feature_flags'

    @classmethod
    def create(cls, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create new feature flag

        Args:
            data: {
                'name': str (required),
                'description': str (optional),
                'category': str (required),
                'is_enabled': bool (default False),
                'created_by': str (optional)
            }

        Returns:
            Created feature flag with id
        """
        return insert_returning(cls.table_name, data)

    @classmethod
    def find_by_id(cls, feature_id: int) -> Optional[Dict[str, Any]]:
        """Find feature by ID"""
        query = f"SELECT * FROM {cls.table_name} WHERE id = %s"
        return fetch_one(query, (feature_id,))

    @classmethod
    def find_by_name(cls, feature_name: str) -> Optional[Dict[str, Any]]:
        """Find feature by name (unique field)"""
        query = f"SELECT * FROM {cls.table_name} WHERE name = %s"
        return fetch_one(query, (feature_name,))

    @classmethod
    def find_all(
        cls,
        limit: int = 100,
        offset: int = 0,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find all features with optional filtering

        Args:
            limit: Max results (default 100, max 1000)
            offset: Skip N results
            category: Filter by category

        Returns:
            List of feature flags
        """
        if limit > 1000:
            limit = 1000

        if category:
            query = f"""
                SELECT * FROM {cls.table_name}
                WHERE category = %s
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            return fetch_all(query, (category, limit, offset))
        else:
            query = f"""
                SELECT * FROM {cls.table_name}
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            return fetch_all(query, (limit, offset))

    @classmethod
    def find_enabled(cls, limit: int = 100) -> List[Dict[str, Any]]:
        """Find all enabled features"""
        query = f"""
            SELECT * FROM {cls.table_name}
            WHERE is_enabled = TRUE
            ORDER BY created_at DESC
            LIMIT %s
        """
        return fetch_all(query, (limit,))

    @classmethod
    def update(
        cls,
        feature_id: int,
        data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update feature by ID"""
        if 'updated_at' not in data:
            data['updated_at'] = datetime.utcnow()

        query = f"""
            UPDATE {cls.table_name}
            SET {', '.join(f'{k} = %s' for k in data.keys())}
            WHERE id = %s
            RETURNING *
        """
        params = list(data.values()) + [feature_id]
        return fetch_one(query, params)

    @classmethod
    def enable(cls, feature_id: int) -> Optional[Dict[str, Any]]:
        """Enable feature"""
        return cls.update(feature_id, {'is_enabled': True})

    @classmethod
    def disable(cls, feature_id: int) -> Optional[Dict[str, Any]]:
        """Disable feature"""
        return cls.update(feature_id, {'is_enabled': False})

    @classmethod
    def count(cls, category: Optional[str] = None) -> int:
        """Count features"""
        if category:
            query = f"SELECT COUNT(*) FROM {cls.table_name} WHERE category = %s"
            result = fetch_one(query, (category,))
        else:
            query = f"SELECT COUNT(*) FROM {cls.table_name}"
            result = fetch_one(query)

        return result[0] if result else 0


# ==================== ROLE MAPPING REPOSITORY ====================

class FeatureRoleMappingRepository:
    """
    Repository for role-based feature access control
    (feature_flag_role_mappings table)

    Manages per-role feature enablement with quotas.
    """

    table_name = 'feature_flag_role_mappings'

    @classmethod
    def create(cls, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create role mapping with quotas

        Args:
            data: {
                'feature_name': str,
                'role_code': str,
                'is_enabled': bool,
                'max_usage_per_day': int (optional),
                'max_creation_per_month': int (optional),
                'priority_level': int (optional)
            }
        """
        return insert_returning(cls.table_name, data)

    @classmethod
    def find_by_feature_and_role(
        cls,
        feature_name: str,
        role_code: str
    ) -> Optional[Dict[str, Any]]:
        """Find role mapping for specific feature and role"""
        query = f"""
            SELECT * FROM {cls.table_name}
            WHERE feature_name = %s AND role_code = %s
        """
        return fetch_one(query, (feature_name, role_code))

    @classmethod
    def find_by_feature(cls, feature_name: str) -> List[Dict[str, Any]]:
        """Get all role mappings for a feature"""
        query = f"""
            SELECT * FROM {cls.table_name}
            WHERE feature_name = %s
            ORDER BY role_code
        """
        return fetch_all(query, (feature_name,))

    @classmethod
    def find_by_role(cls, role_code: str) -> List[Dict[str, Any]]:
        """Get all enabled features for a role"""
        query = f"""
            SELECT * FROM {cls.table_name}
            WHERE role_code = %s AND is_enabled = TRUE
            ORDER BY priority_level DESC, feature_name
        """
        return fetch_all(query, (role_code,))

    @classmethod
    def update(
        cls,
        feature_name: str,
        role_code: str,
        data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update role mapping"""
        if 'updated_at' not in data:
            data['updated_at'] = datetime.utcnow()

        query = f"""
            UPDATE {cls.table_name}
            SET {', '.join(f'{k} = %s' for k in data.keys())}
            WHERE feature_name = %s AND role_code = %s
            RETURNING *
        """
        params = list(data.values()) + [feature_name, role_code]
        return fetch_one(query, params)

    @classmethod
    def delete(cls, feature_name: str, role_code: str) -> bool:
        """Delete role mapping"""
        query = f"""
            DELETE FROM {cls.table_name}
            WHERE feature_name = %s AND role_code = %s
        """
        return execute_query(query, (feature_name, role_code)) > 0
