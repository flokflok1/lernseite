"""
LernsystemX Runner Modes Repository

Data access layer for runner mode management.
Handles CRUD operations for runner_modes table.
"""

from typing import Dict, List, Optional, Any

from app.infrastructure.persistence.repositories.core.base import BaseRepository
from app.infrastructure.persistence.database.connection import (
    fetch_one,
    fetch_all,
    insert_returning,
    update_returning,
    execute_query
)


class RunnerModesRepository(BaseRepository):
    """
    Repository for learning_methods.runner_modes table.

    Runner modes define how learning methods are executed:
    - standard: Normal learning flow
    - exam: Timed, graded execution
    - practice: Untimed, with hints
    - review: Read-only review of completed work
    """

    table_name = "learning_methods.runner_modes"
    pk_column = "mode_id"

    @classmethod
    def find_by_code(cls, mode_code: str) -> Optional[Dict]:
        """
        Find runner mode by unique code.

        Args:
            mode_code: Unique mode identifier (e.g., 'standard', 'exam')

        Returns:
            Mode dict or None
        """
        query = f"""
            SELECT * FROM {cls.table_name}
            WHERE mode_code = %s
        """
        return fetch_one(query, (mode_code,))

    @classmethod
    def find_active(cls, limit: int = 100) -> List[Dict]:
        """
        Find all active runner modes.

        Args:
            limit: Maximum results

        Returns:
            List of active mode dicts
        """
        query = f"""
            SELECT * FROM {cls.table_name}
            WHERE active = TRUE
            ORDER BY display_order ASC, mode_code ASC
            LIMIT %s
        """
        return fetch_all(query, (limit,))

    @classmethod
    def create_mode(cls, data: Dict[str, Any]) -> Optional[Dict]:
        """
        Create new runner mode.

        Args:
            data: Mode data dict with:
                - mode_code: Unique identifier
                - name: Display name
                - description: Optional description
                - config: JSONB configuration
                - features_included: Array of default feature codes
                - time_limited: Boolean
                - graded: Boolean
                - allows_hints: Boolean
                - allows_skip: Boolean

        Returns:
            Created mode dict
        """
        return insert_returning(cls.table_name, data)

    @classmethod
    def update_mode(cls, mode_id: int, data: Dict[str, Any]) -> Optional[Dict]:
        """
        Update runner mode by ID.

        Args:
            mode_id: Primary key
            data: Fields to update

        Returns:
            Updated mode dict
        """
        return cls.update(mode_id, data)

    @classmethod
    def soft_delete(cls, mode_id: int) -> Optional[Dict]:
        """
        Soft delete runner mode (set active = false).

        Args:
            mode_id: Primary key

        Returns:
            Updated mode dict
        """
        return cls.update(mode_id, {'active': False})

    @classmethod
    def code_exists(cls, mode_code: str, exclude_id: Optional[int] = None) -> bool:
        """
        Check if mode_code already exists.

        Args:
            mode_code: Code to check
            exclude_id: Optional ID to exclude from check (for updates)

        Returns:
            True if exists
        """
        if exclude_id:
            query = f"""
                SELECT EXISTS(
                    SELECT 1 FROM {cls.table_name}
                    WHERE mode_code = %s AND mode_id != %s
                )
            """
            result = fetch_one(query, (mode_code, exclude_id))
        else:
            query = f"""
                SELECT EXISTS(
                    SELECT 1 FROM {cls.table_name}
                    WHERE mode_code = %s
                )
            """
            result = fetch_one(query, (mode_code,))

        return result['exists'] if result else False


class RunnerModeFeatureMapRepository(BaseRepository):
    """
    Repository for learning_methods.runner_mode_feature_map table.

    Maps runner modes to system features with relationship types:
    - required: Feature must be active
    - optional: Feature can be toggled
    - excluded: Feature must be disabled
    """

    table_name = "learning_methods.runner_mode_feature_map"
    pk_column = "mapping_id"

    @classmethod
    def find_by_mode(cls, mode_id: int) -> List[Dict]:
        """
        Find all feature mappings for a runner mode.

        Args:
            mode_id: Runner mode ID

        Returns:
            List of feature mapping dicts with feature details
        """
        query = """
            SELECT
                rmfm.*,
                sf.feature_code,
                sf.feature_name,
                sf.category,
                sf.icon
            FROM learning_methods.runner_mode_feature_map rmfm
            JOIN support_systems.system_features sf ON rmfm.feature_id = sf.feature_id
            WHERE rmfm.mode_id = %s
            ORDER BY sf.category, sf.feature_name
        """
        return fetch_all(query, (mode_id,))

    @classmethod
    def set_features(cls, mode_id: int, features: List[Dict[str, Any]]) -> bool:
        """
        Replace all feature mappings for a mode.

        Args:
            mode_id: Runner mode ID
            features: List of feature mappings with:
                - feature_id: Feature ID
                - relationship: 'required' | 'optional' | 'excluded'
                - config: Optional JSONB override

        Returns:
            True if successful
        """
        # Delete existing mappings
        delete_query = f"""
            DELETE FROM {cls.table_name}
            WHERE mode_id = %s
        """
        execute_query(delete_query, (mode_id,))

        # Insert new mappings
        for feature in features:
            insert_data = {
                'mode_id': mode_id,
                'feature_id': feature['feature_id'],
                'relationship': feature.get('relationship', 'optional'),
                'config': feature.get('config', {})
            }
            insert_returning(cls.table_name, insert_data)

        return True

    @classmethod
    def get_required_features(cls, mode_id: int) -> List[Dict]:
        """
        Get only required features for a mode.

        Args:
            mode_id: Runner mode ID

        Returns:
            List of required feature mappings
        """
        query = """
            SELECT
                rmfm.*,
                sf.feature_code,
                sf.feature_name
            FROM learning_methods.runner_mode_feature_map rmfm
            JOIN support_systems.system_features sf ON rmfm.feature_id = sf.feature_id
            WHERE rmfm.mode_id = %s AND rmfm.relationship = 'required'
        """
        return fetch_all(query, (mode_id,))

    @classmethod
    def get_excluded_features(cls, mode_id: int) -> List[Dict]:
        """
        Get excluded features for a mode.

        Args:
            mode_id: Runner mode ID

        Returns:
            List of excluded feature mappings
        """
        query = """
            SELECT
                rmfm.*,
                sf.feature_code,
                sf.feature_name
            FROM learning_methods.runner_mode_feature_map rmfm
            JOIN support_systems.system_features sf ON rmfm.feature_id = sf.feature_id
            WHERE rmfm.mode_id = %s AND rmfm.relationship = 'excluded'
        """
        return fetch_all(query, (mode_id,))


class LMTypeModeCompatibilityRepository(BaseRepository):
    """
    Repository for learning_methods.lm_type_mode_compatibility table.

    Defines which runner modes are compatible with which LM types.
    """

    table_name = "learning_methods.lm_type_mode_compatibility"
    pk_column = "compatibility_id"

    @classmethod
    def find_by_type(cls, method_type: int) -> List[Dict]:
        """
        Find all mode compatibilities for a LM type.

        Args:
            method_type: Learning method type ID (0-11)

        Returns:
            List of compatibility dicts with mode details
        """
        query = """
            SELECT
                ltmc.*,
                rm.mode_code,
                rm.name as mode_name,
                rm.description as mode_description,
                rm.time_limited,
                rm.graded
            FROM learning_methods.lm_type_mode_compatibility ltmc
            JOIN learning_methods.runner_modes rm ON ltmc.mode_id = rm.mode_id
            WHERE ltmc.method_type = %s AND rm.active = TRUE
            ORDER BY ltmc.is_default DESC, rm.display_order ASC
        """
        return fetch_all(query, (method_type,))

    @classmethod
    def find_compatible_modes(cls, method_type: int) -> List[Dict]:
        """
        Find only compatible modes for a LM type.

        Args:
            method_type: Learning method type ID

        Returns:
            List of compatible modes
        """
        query = """
            SELECT
                rm.*
            FROM learning_methods.lm_type_mode_compatibility ltmc
            JOIN learning_methods.runner_modes rm ON ltmc.mode_id = rm.mode_id
            WHERE ltmc.method_type = %s
              AND ltmc.is_compatible = TRUE
              AND rm.active = TRUE
            ORDER BY ltmc.is_default DESC, rm.display_order ASC
        """
        return fetch_all(query, (method_type,))

    @classmethod
    def get_default_mode(cls, method_type: int) -> Optional[Dict]:
        """
        Get default runner mode for a LM type.

        Args:
            method_type: Learning method type ID

        Returns:
            Default mode dict or None
        """
        query = """
            SELECT
                rm.*
            FROM learning_methods.lm_type_mode_compatibility ltmc
            JOIN learning_methods.runner_modes rm ON ltmc.mode_id = rm.mode_id
            WHERE ltmc.method_type = %s
              AND ltmc.is_default = TRUE
              AND ltmc.is_compatible = TRUE
              AND rm.active = TRUE
            LIMIT 1
        """
        return fetch_one(query, (method_type,))

    @classmethod
    def is_compatible(cls, method_type: int, mode_id: int) -> bool:
        """
        Check if mode is compatible with LM type.

        Args:
            method_type: Learning method type ID
            mode_id: Runner mode ID

        Returns:
            True if compatible
        """
        query = """
            SELECT EXISTS(
                SELECT 1 FROM learning_methods.lm_type_mode_compatibility
                WHERE method_type = %s AND mode_id = %s AND is_compatible = TRUE
            )
        """
        result = fetch_one(query, (method_type, mode_id))
        return result['exists'] if result else False

    @classmethod
    def set_modes(cls, method_type: int, modes: List[Dict[str, Any]]) -> bool:
        """
        Replace all mode compatibilities for a LM type.

        Args:
            method_type: Learning method type ID
            modes: List of mode configurations with:
                - mode_id: Runner mode ID
                - is_compatible: Boolean
                - is_default: Boolean (only one can be default)
                - config: Optional JSONB override

        Returns:
            True if successful
        """
        # Delete existing compatibilities
        delete_query = f"""
            DELETE FROM {cls.table_name}
            WHERE method_type = %s
        """
        execute_query(delete_query, (method_type,))

        # Insert new compatibilities
        for mode in modes:
            insert_data = {
                'method_type': method_type,
                'mode_id': mode['mode_id'],
                'is_compatible': mode.get('is_compatible', True),
                'is_default': mode.get('is_default', False),
                'config': mode.get('config', {})
            }
            insert_returning(cls.table_name, insert_data)

        return True
