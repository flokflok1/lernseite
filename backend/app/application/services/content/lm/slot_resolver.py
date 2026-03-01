"""
LM Slot Resolver Service

Service for resolving AI models for Learning Method capability slots.
Provides high-level API for getting the right models for each LM functionality.

All learning method configurations are loaded from the database (learning_method_types table).
No hardcoded LM definitions - fully database-driven.

Author: LernsystemX Team
Date: 2025-12-04
"""

from typing import Optional, Dict, List, Any
from dataclasses import dataclass

from app.domain.ai.configuration.slots.capability_slots import CapabilitySlot, get_slot_definition
from app.infrastructure.persistence.repositories.lm_slot import (
    LMSlotAssignmentRepository,
    LMSlotResolverRepository,
    CapabilitySlotRepository
)
from app.infrastructure.persistence.repositories.learning_method.config.catalog import LearningMethodCatalogRepository


@dataclass
class ResolvedModel:
    """Resolved model for a slot."""
    slot_code: str
    slot_display_name: str
    is_required: bool
    is_primary: bool
    is_configured: bool
    model_id: Optional[int] = None
    model_name: Optional[str] = None
    model_display_name: Optional[str] = None
    provider_name: Optional[str] = None
    resolved_scope: str = 'none'


class LMSlotResolver:
    """
    Service for resolving models for LM capability slots.

    Supports hierarchical resolution: chapter > course > system.
    """

    def resolve_lm_models(
        self,
        learning_method_id: int,
        chapter_id: str = None,
        course_id: str = None
    ) -> Dict[str, Optional[ResolvedModel]]:
        """
        Resolve all models for all slots of a learning method.

        Args:
            learning_method_id: LM ID (0-11, database-driven)
            chapter_id: Optional chapter ID for override
            course_id: Optional course ID for override

        Returns:
            Dict mapping slot_code to ResolvedModel (or None if slot not used)
        """
        # Get slot resolutions from database
        db_results = LMSlotResolverRepository.resolve_all_slots(
            learning_method_id,
            chapter_id,
            course_id
        )

        # Convert to ResolvedModel objects
        result = {}
        for row in db_results:
            resolved = ResolvedModel(
                slot_code=row['slot_code'],
                slot_display_name=row['slot_display_name'],
                is_required=row['is_required'],
                is_primary=row['is_primary'],
                is_configured=row['is_configured'],
                model_id=row['model_id'],
                model_name=row['model_name'],
                model_display_name=row['model_display_name'],
                provider_name=row['provider_name'],
                resolved_scope=row['resolved_scope']
            )
            result[row['slot_code']] = resolved

        return result

    def get_model_for_slot(
        self,
        learning_method_id: int,
        slot: CapabilitySlot,
        chapter_id: str = None,
        course_id: str = None
    ) -> Optional[ResolvedModel]:
        """
        Get the resolved model for a specific slot.

        Args:
            learning_method_id: LM ID (0-11, database-driven)
            slot: Capability slot enum
            chapter_id: Optional chapter ID
            course_id: Optional course ID

        Returns:
            ResolvedModel if slot is used by this LM, None otherwise
        """
        models = self.resolve_lm_models(learning_method_id, chapter_id, course_id)
        return models.get(slot.value)

    def get_chat_model(
        self,
        learning_method_id: int,
        chapter_id: str = None,
        course_id: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Shortcut to get the chat model for an LM.

        Returns model info dict or None.
        """
        resolved = self.get_model_for_slot(
            learning_method_id,
            CapabilitySlot.CHAT,
            chapter_id,
            course_id
        )
        if resolved and resolved.is_configured:
            return {
                'model_id': resolved.model_id,
                'model_name': resolved.model_name,
                'display_name': resolved.model_display_name,
                'provider': resolved.provider_name
            }
        return None

    def get_stt_model(
        self,
        learning_method_id: int,
        chapter_id: str = None,
        course_id: str = None
    ) -> Optional[Dict[str, Any]]:
        """Get the STT model for an LM."""
        resolved = self.get_model_for_slot(
            learning_method_id,
            CapabilitySlot.STT,
            chapter_id,
            course_id
        )
        if resolved and resolved.is_configured:
            return {
                'model_id': resolved.model_id,
                'model_name': resolved.model_name,
                'display_name': resolved.model_display_name,
                'provider': resolved.provider_name
            }
        return None

    def get_tts_model(
        self,
        learning_method_id: int,
        chapter_id: str = None,
        course_id: str = None
    ) -> Optional[Dict[str, Any]]:
        """Get the TTS model for an LM."""
        resolved = self.get_model_for_slot(
            learning_method_id,
            CapabilitySlot.TTS,
            chapter_id,
            course_id
        )
        if resolved and resolved.is_configured:
            return {
                'model_id': resolved.model_id,
                'model_name': resolved.model_name,
                'display_name': resolved.model_display_name,
                'provider': resolved.provider_name
            }
        return None

    def check_lm_ready(
        self,
        learning_method_id: int,
        chapter_id: str = None,
        course_id: str = None
    ) -> Dict[str, Any]:
        """
        Check if all required slots for an LM are configured.

        Returns:
            {
                'ready': bool,
                'learning_method_id': int,
                'learning_method_name': str,
                'required_slots': [slot_code, ...],
                'configured_slots': [slot_code, ...],
                'missing_slots': [slot_code, ...]
            }
        """
        # Get LM config from database (not hardcoded)
        lm_def = LearningMethodCatalogRepository.get_by_type(method_type=learning_method_id)
        lm_name = lm_def.get('name') if lm_def else f'LM{learning_method_id:02d}'

        # Get resolution status from database
        check_result = LMSlotResolverRepository.check_required_slots_configured(
            learning_method_id,
            chapter_id,
            course_id
        )

        # Get all resolved models
        models = self.resolve_lm_models(learning_method_id, chapter_id, course_id)

        configured_slots = [
            code for code, model in models.items()
            if model and model.is_configured
        ]

        return {
            'ready': check_result['all_configured'],
            'learning_method_id': learning_method_id,
            'learning_method_name': lm_name,
            'required_count': check_result['required_count'],
            'configured_count': check_result['configured_count'],
            'required_slots': check_result.get('missing_slots', []) + [
                code for code, model in models.items()
                if model and model.is_required and model.is_configured
            ],
            'configured_slots': configured_slots,
            'missing_slots': check_result['missing_slots']
        }

    def get_lm_overview(self, learning_method_id: int) -> Dict[str, Any]:
        """
        Get complete overview of an LM's slot configuration.

        Includes requirements, assignments, and status.
        """
        # Get LM from database (not hardcoded)
        lm_def = LearningMethodCatalogRepository.get_by_type(method_type=learning_method_id)
        if not lm_def:
            return None

        # Get all slots for this LM
        models = self.resolve_lm_models(learning_method_id)
        ready_check = self.check_lm_ready(learning_method_id)

        # Build slot list
        slots = []
        for slot_code, resolved in models.items():
            if resolved:
                slots.append({
                    'slot_code': slot_code,
                    'slot_display_name': resolved.slot_display_name,
                    'is_required': resolved.is_required,
                    'is_primary': resolved.is_primary,
                    'is_configured': resolved.is_configured,
                    'model': {
                        'model_id': resolved.model_id,
                        'model_name': resolved.model_name,
                        'display_name': resolved.model_display_name,
                        'provider': resolved.provider_name
                    } if resolved.is_configured else None,
                    'resolved_scope': resolved.resolved_scope
                })

        return {
            'learning_method_id': learning_method_id,
            'name': lm_def.get('name'),
            'group': lm_def.get('group_code'),
            'ready': ready_check['ready'],
            'required_count': ready_check['required_count'],
            'configured_count': ready_check['configured_count'],
            'slots': slots
        }

    def get_all_lm_overview(self) -> List[Dict[str, Any]]:
        """
        Get overview of all active learning methods with their slot configurations.

        Used for admin dashboard. Queries database for all active learning methods.
        """
        overviews = []

        # Get all active learning methods from database
        max_type = LearningMethodCatalogRepository.get_max_active_type()

        for lm_id in range(max_type + 1):
            overview = self.get_lm_overview(lm_id)
            if overview:
                overviews.append(overview)
        return overviews


class LMSlotManager:
    """
    Service for managing LM slot assignments.

    Provides admin operations for assigning models to slots.
    """

    def assign_model(
        self,
        learning_method_id: int,
        slot_code: str,
        model_id: int,
        scope: str = 'system',
        scope_reference_id: str = None,
        created_by: str = None
    ) -> Dict[str, Any]:
        """
        Assign a model to a slot for an LM.

        Args:
            learning_method_id: LM ID (0-11, database-driven)
            slot_code: Slot code (e.g., 'chat', 'stt')
            model_id: AI model ID
            scope: 'system', 'course', or 'chapter'
            scope_reference_id: Course/chapter ID (for non-system scope)
            created_by: User ID making the assignment

        Returns:
            Created assignment dict
        """
        # Validate LM exists (using database)
        lm_def = LearningMethodCatalogRepository.get_by_type(method_type=learning_method_id)
        if not lm_def:
            raise ValueError(f"Invalid learning_method_id: {learning_method_id}")

        # Validate slot code
        slot = CapabilitySlotRepository.find_by_code(slot_code)
        if not slot:
            raise ValueError(f"Unknown slot code: {slot_code}")

        # Create assignment
        return LMSlotAssignmentRepository.assign_model_to_slot(
            learning_method_id=learning_method_id,
            slot_code=slot_code,
            model_id=model_id,
            scope=scope,
            scope_reference_id=scope_reference_id,
            created_by=created_by
        )

    def remove_assignment(
        self,
        learning_method_id: int,
        slot_code: str,
        scope: str = 'system',
        scope_reference_id: str = None
    ) -> bool:
        """
        Remove a slot assignment.

        Returns True if removed, False if not found.
        """
        return LMSlotAssignmentRepository.remove_slot_assignment(
            learning_method_id=learning_method_id,
            slot_code=slot_code,
            scope=scope,
            scope_reference_id=scope_reference_id
        )

    def bulk_assign(
        self,
        learning_method_id: int,
        assignments: List[Dict[str, Any]],
        scope: str = 'system',
        scope_reference_id: str = None,
        created_by: str = None
    ) -> List[Dict]:
        """
        Bulk assign multiple slots.

        Args:
            learning_method_id: LM ID
            assignments: List of {slot_code, model_id, priority?}
            scope: Assignment scope
            scope_reference_id: Scope reference
            created_by: User ID

        Returns:
            List of created assignments
        """
        return LMSlotAssignmentRepository.bulk_assign_slots(
            learning_method_id=learning_method_id,
            assignments=assignments,
            scope=scope,
            scope_reference_id=scope_reference_id,
            created_by=created_by
        )

    def get_compatible_models(self, slot_code: str) -> List[Dict]:
        """
        Get all models compatible with a slot.

        Used for dropdown in admin UI.
        """
        return LMSlotAssignmentRepository.get_compatible_models_for_slot(slot_code)

    def get_all_slots(self) -> List[Dict]:
        """
        Get all available capability slots.

        Used for slot selection in admin UI.
        """
        return CapabilitySlotRepository.find_all_sorted()


# Singleton instances for convenience
_resolver: Optional[LMSlotResolver] = None
_manager: Optional[LMSlotManager] = None


def get_resolver() -> LMSlotResolver:
    """Get the singleton resolver instance."""
    global _resolver
    if _resolver is None:
        _resolver = LMSlotResolver()
    return _resolver


def get_manager() -> LMSlotManager:
    """Get the singleton manager instance."""
    global _manager
    if _manager is None:
        _manager = LMSlotManager()
    return _manager
