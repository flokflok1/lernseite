"""
LernsystemX Panel Runner Mode Service

Business logic for runner mode configuration.
Panel API - Configuration only, NO execution logic.
"""

from typing import Any, Dict, List, Optional, Tuple

from app.infrastructure.persistence.repositories.runner.modes import (
    RunnerModesRepository,
    RunnerModeFeatureMapRepository,
    LMTypeModeCompatibilityRepository
)
from app.infrastructure.persistence.repositories.features.system_features_repository import (
    SystemFeaturesRepository
)
from app.infrastructure.i18n.error_codes import ErrorCode


class PanelRunnerModeService:
    """
    Service for managing runner modes via Panel API.

    Responsibilities:
    - CRUD operations for runner modes
    - Feature mapping management
    - LM type compatibility management

    Does NOT handle:
    - Session execution (that's Runner API)
    - Learning progress (that's Runner API)
    """

    # =========================================================================
    # Runner Modes CRUD
    # =========================================================================

    @classmethod
    def list_modes(cls, include_inactive: bool = False) -> Tuple[List[Dict], int]:
        """
        List all runner modes.

        Args:
            include_inactive: Include inactive modes

        Returns:
            Tuple of (modes list, total count)
        """
        if include_inactive:
            modes = RunnerModesRepository.find_all(order_by='display_order ASC')
        else:
            modes = RunnerModesRepository.find_active()

        return modes, len(modes)

    @classmethod
    def get_mode(cls, mode_id: int) -> Tuple[Optional[Dict], Optional[ErrorCode]]:
        """
        Get runner mode by ID.

        Args:
            mode_id: Mode primary key

        Returns:
            Tuple of (mode dict, error code)
        """
        mode = RunnerModesRepository.find_by_id(mode_id)

        if not mode:
            return None, ErrorCode.NOT_FOUND

        return mode, None

    @classmethod
    def get_mode_by_code(cls, mode_code: str) -> Tuple[Optional[Dict], Optional[ErrorCode]]:
        """
        Get runner mode by code.

        Args:
            mode_code: Unique mode code

        Returns:
            Tuple of (mode dict, error code)
        """
        mode = RunnerModesRepository.find_by_code(mode_code)

        if not mode:
            return None, ErrorCode.NOT_FOUND

        return mode, None

    @classmethod
    def create_mode(cls, data: Dict[str, Any]) -> Tuple[Optional[Dict], Optional[ErrorCode]]:
        """
        Create new runner mode.

        Args:
            data: Mode data from validated schema

        Returns:
            Tuple of (created mode, error code)
        """
        # Check code uniqueness
        if RunnerModesRepository.code_exists(data['mode_code']):
            return None, ErrorCode.CONFLICT

        # Create mode
        mode = RunnerModesRepository.create_mode(data)

        if not mode:
            return None, ErrorCode.OPERATION_FAILED

        return mode, None

    @classmethod
    def update_mode(
        cls,
        mode_id: int,
        data: Dict[str, Any]
    ) -> Tuple[Optional[Dict], Optional[ErrorCode]]:
        """
        Update runner mode.

        Args:
            mode_id: Mode primary key
            data: Update data from validated schema

        Returns:
            Tuple of (updated mode, error code)
        """
        # Check mode exists
        existing = RunnerModesRepository.find_by_id(mode_id)
        if not existing:
            return None, ErrorCode.NOT_FOUND

        # Filter out None values
        update_data = {k: v for k, v in data.items() if v is not None}

        if not update_data:
            return existing, None

        # Update mode
        mode = RunnerModesRepository.update_mode(mode_id, update_data)

        if not mode:
            return None, ErrorCode.OPERATION_FAILED

        return mode, None

    @classmethod
    def delete_mode(cls, mode_id: int) -> Tuple[bool, Optional[ErrorCode]]:
        """
        Soft delete runner mode (set active = false).

        Args:
            mode_id: Mode primary key

        Returns:
            Tuple of (success, error code)
        """
        # Check mode exists
        existing = RunnerModesRepository.find_by_id(mode_id)
        if not existing:
            return False, ErrorCode.NOT_FOUND

        # Soft delete
        result = RunnerModesRepository.soft_delete(mode_id)

        if not result:
            return False, ErrorCode.OPERATION_FAILED

        return True, None

    # =========================================================================
    # Feature Mappings
    # =========================================================================

    @classmethod
    def get_mode_features(cls, mode_id: int) -> Tuple[Optional[Dict], Optional[ErrorCode]]:
        """
        Get feature mappings for a runner mode.

        Args:
            mode_id: Mode primary key

        Returns:
            Tuple of (response dict, error code)
        """
        # Check mode exists
        mode = RunnerModesRepository.find_by_id(mode_id)
        if not mode:
            return None, ErrorCode.NOT_FOUND

        features = RunnerModeFeatureMapRepository.find_by_mode(mode_id)

        return {
            'mode_id': mode_id,
            'mode_code': mode['mode_code'],
            'features': features
        }, None

    @classmethod
    def set_mode_features(
        cls,
        mode_id: int,
        features: List[Dict[str, Any]]
    ) -> Tuple[Optional[Dict], Optional[ErrorCode]]:
        """
        Set feature mappings for a runner mode.

        Replaces all existing mappings.
        Enforces precedence: excluded > required > optional

        Args:
            mode_id: Mode primary key
            features: List of feature mappings

        Returns:
            Tuple of (response dict, error code)
        """
        # Check mode exists
        mode = RunnerModesRepository.find_by_id(mode_id)
        if not mode:
            return None, ErrorCode.NOT_FOUND

        # Validate feature IDs exist
        feature_ids = [f['feature_id'] for f in features]
        for fid in feature_ids:
            if not SystemFeaturesRepository.find_by_id(fid):
                return None, ErrorCode.VALIDATION_ERROR

        # Apply mappings
        RunnerModeFeatureMapRepository.set_features(mode_id, features)

        # Return updated mappings
        updated_features = RunnerModeFeatureMapRepository.find_by_mode(mode_id)

        return {
            'mode_id': mode_id,
            'mode_code': mode['mode_code'],
            'features': updated_features
        }, None

    # =========================================================================
    # LM Type Mode Compatibility
    # =========================================================================

    @classmethod
    def get_lm_type_modes(cls, method_type: int) -> Tuple[Optional[Dict], Optional[ErrorCode]]:
        """
        Get mode compatibilities for a LM type.

        Args:
            method_type: Learning method type ID (0-11)

        Returns:
            Tuple of (response dict, error code)
        """
        # Validate method_type range
        if method_type < 0 or method_type > 11:
            return None, ErrorCode.VALIDATION_ERROR

        modes = LMTypeModeCompatibilityRepository.find_by_type(method_type)

        return {
            'method_type': method_type,
            'modes': modes
        }, None

    @classmethod
    def set_lm_type_modes(
        cls,
        method_type: int,
        modes: List[Dict[str, Any]]
    ) -> Tuple[Optional[Dict], Optional[ErrorCode]]:
        """
        Set mode compatibilities for a LM type.

        Args:
            method_type: Learning method type ID (0-11)
            modes: List of mode compatibility configurations

        Returns:
            Tuple of (response dict, error code)
        """
        # Validate method_type range
        if method_type < 0 or method_type > 11:
            return None, ErrorCode.VALIDATION_ERROR

        # Validate mode IDs exist
        for mode in modes:
            if not RunnerModesRepository.find_by_id(mode['mode_id']):
                return None, ErrorCode.VALIDATION_ERROR

        # Validate only one default
        defaults = [m for m in modes if m.get('is_default')]
        if len(defaults) > 1:
            return None, ErrorCode.VALIDATION_ERROR

        # Apply compatibilities
        LMTypeModeCompatibilityRepository.set_modes(method_type, modes)

        # Return updated modes
        updated_modes = LMTypeModeCompatibilityRepository.find_by_type(method_type)

        return {
            'method_type': method_type,
            'modes': updated_modes
        }, None

    # =========================================================================
    # System Features (read + minimal edit)
    # =========================================================================

    @classmethod
    def list_system_features(
        cls,
        category: Optional[str] = None,
        include_inactive: bool = False
    ) -> Tuple[List[Dict], int, List[str]]:
        """
        List system features.

        Args:
            category: Optional category filter
            include_inactive: Include inactive features

        Returns:
            Tuple of (features list, total count, categories list)
        """
        if include_inactive:
            if category:
                features = SystemFeaturesRepository.find_by_category(category)
            else:
                features = SystemFeaturesRepository.find_all()
        else:
            features = SystemFeaturesRepository.find_active(category)

        categories = SystemFeaturesRepository.get_categories()

        return features, len(features), categories

    @classmethod
    def get_system_feature(cls, feature_id: int) -> Tuple[Optional[Dict], Optional[ErrorCode]]:
        """
        Get system feature by ID.

        Args:
            feature_id: Feature primary key

        Returns:
            Tuple of (feature dict, error code)
        """
        feature = SystemFeaturesRepository.find_by_id(feature_id)

        if not feature:
            return None, ErrorCode.NOT_FOUND

        return feature, None

    @classmethod
    def update_system_feature(
        cls,
        feature_id: int,
        data: Dict[str, Any]
    ) -> Tuple[Optional[Dict], Optional[ErrorCode]]:
        """
        Update system feature (limited fields).

        Allowed fields: active, config, feature_name, description, icon

        Args:
            feature_id: Feature primary key
            data: Update data

        Returns:
            Tuple of (updated feature, error code)
        """
        # Check feature exists
        existing = SystemFeaturesRepository.find_by_id(feature_id)
        if not existing:
            return None, ErrorCode.NOT_FOUND

        # Filter out None values
        update_data = {k: v for k, v in data.items() if v is not None}

        if not update_data:
            return existing, None

        # Update feature
        feature = SystemFeaturesRepository.update_feature(feature_id, update_data)

        if not feature:
            return None, ErrorCode.OPERATION_FAILED

        return feature, None
