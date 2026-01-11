"""
System Features Repository

Handles database operations for system features configuration at course/chapter/lesson level.

DDD Repository Pattern - Single source of truth for features data access.
"""

from typing import Optional, List, Dict, Any
from app.repositories.base_repository import BaseRepository


class SystemFeaturesRepository:
    """
    Repository for System Features operations.

    Handles:
    - Feature types retrieval
    - Course-level feature configuration (CRUD)
    - Chapter/Lesson-level overrides (future)
    """

    @staticmethod
    def get_feature_types() -> List[Dict]:
        """
        Get all system feature types.

        Returns:
            List of all active system feature types

        Example:
            [
                {
                    'feature_type_id': 1,
                    'feature_code': 'socratic_dialog',
                    'name': 'Sokratischer Dialog',
                    'category': 'tutor',
                    'description': 'KI-geführter Dialog',
                    'former_lm_id': 4,
                    'is_premium': True,
                    'is_active': True
                },
                ...
            ]
        """
        query = """
            SELECT
                feature_type_id,
                feature_code,
                name,
                category,
                description,
                former_lm_id,
                is_premium,
                is_active
            FROM system_feature_types
            WHERE is_active = TRUE
            ORDER BY category, feature_code
        """
        return BaseRepository.fetch_all(query) or []

    @staticmethod
    def get_course_features(course_id: str) -> List[Dict]:
        """
        Get all features enabled for a course.

        Args:
            course_id: UUID of the course

        Returns:
            List of course features with type details

        Example:
            [
                {
                    'course_feature_id': 'uuid',
                    'course_id': 'course-uuid',
                    'feature_type_id': 1,
                    'is_enabled': True,
                    'config': {'max_questions': 10},
                    'feature_code': 'socratic_dialog',
                    'name': 'Sokratischer Dialog',
                    'category': 'tutor'
                },
                ...
            ]
        """
        query = """
            SELECT
                cf.course_feature_id,
                cf.course_id,
                cf.feature_type_id,
                cf.is_enabled,
                cf.config,
                sft.feature_code,
                sft.name,
                sft.category
            FROM course_features cf
            JOIN system_feature_types sft ON cf.feature_type_id = sft.feature_type_id
            WHERE cf.course_id = %s
        """
        return BaseRepository.fetch_all(query, (course_id,)) or []

    @staticmethod
    def get_feature_type_by_code(feature_code: str) -> Optional[Dict]:
        """
        Get feature type by code.

        Args:
            feature_code: Feature code (e.g., 'socratic_dialog')

        Returns:
            Feature type dict or None if not found

        Example:
            {
                'feature_type_id': 1,
                'feature_code': 'socratic_dialog',
                'name': 'Sokratischer Dialog',
                'category': 'tutor',
                'is_premium': True
            }
        """
        query = """
            SELECT feature_type_id, feature_code, name, category, is_premium
            FROM system_feature_types
            WHERE feature_code = %s AND is_active = TRUE
        """
        return BaseRepository.fetch_one(query, (feature_code,))

    @staticmethod
    def upsert_course_feature(
        course_id: str,
        feature_type_id: int,
        is_enabled: bool,
        config: Optional[Dict] = None
    ) -> Dict:
        """
        Insert or update a course feature.

        Args:
            course_id: UUID of the course
            feature_type_id: ID of the feature type
            is_enabled: Enable or disable
            config: Optional feature-specific configuration

        Returns:
            Created/updated course feature record

        Example:
            {
                'course_feature_id': 'uuid',
                'course_id': 'course-uuid',
                'feature_type_id': 1,
                'is_enabled': True,
                'config': {'max_questions': 10}
            }
        """
        query = """
            INSERT INTO course_features (course_id, feature_type_id, is_enabled, config)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (course_id, feature_type_id)
            DO UPDATE SET
                is_enabled = EXCLUDED.is_enabled,
                config = COALESCE(EXCLUDED.config, course_features.config),
                updated_at = NOW()
            RETURNING course_feature_id, course_id, feature_type_id, is_enabled, config
        """
        import json
        config_json = json.dumps(config or {})
        return BaseRepository.fetch_one(query, (course_id, feature_type_id, is_enabled, config_json))

    @staticmethod
    def delete_course_feature(course_id: str, feature_type_id: int) -> bool:
        """
        Remove a course feature (resets to default/inherited).

        Args:
            course_id: UUID of the course
            feature_type_id: ID of the feature type

        Returns:
            True if deleted successfully
        """
        query = """
            DELETE FROM course_features
            WHERE course_id = %s AND feature_type_id = %s
        """
        BaseRepository.execute(query, (course_id, feature_type_id))
        return True
