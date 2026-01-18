"""
LernsystemX LM Model Resolver Service

Resolves which AI model to use for a learning method.
Enforces no-fallback policy - blocks generation if required model is not configured.

Phase KI-Architektur - Model Routing System
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass

from app.infrastructure.persistence.repositories.lm_model_routing import (
    LMModelAssignmentRepository,
    LMModelRequirementsRepository
)
from app.infrastructure.persistence.repositories.ai_models import AIModelsRepository
from app.infrastructure.validation.learning_method_mapping import get_method_by_id


class ModelNotConfiguredError(Exception):
    """
    Raised when a required learning method has no model configured.
    This is the no-fallback policy in action.
    """
    def __init__(self, learning_method_id: int, lm_name: str = None):
        self.learning_method_id = learning_method_id
        self.lm_name = lm_name or f'LM{str(learning_method_id).zfill(2)}'
        self.lm_code = f'LM{str(learning_method_id).zfill(2)}'
        super().__init__(
            f'Kein KI-Modell konfiguriert für {self.lm_code} ({self.lm_name}). '
            f'Bitte konfiguriere ein Modell in den KI-Einstellungen.'
        )


@dataclass
class ResolvedModel:
    """Result of model resolution"""
    model_id: int
    model_name: str
    provider_name: str
    scope: str  # 'system', 'course', or 'chapter'
    learning_method_id: int


class LMModelResolver:
    """
    Resolves AI models for learning methods with hierarchical lookup.

    Resolution order:
    1. Chapter-level assignment (most specific)
    2. Course-level assignment
    3. System-level assignment (global default)

    If no model is configured and the LM requires one, raises ModelNotConfiguredError.
    """

    @staticmethod
    def resolve(
        learning_method_id: int,
        chapter_id: str = None,
        course_id: str = None,
        allow_fallback: bool = False
    ) -> ResolvedModel:
        """
        Resolve the AI model for a learning method.

        Args:
            learning_method_id: Learning method ID (0-32)
            chapter_id: Optional chapter UUID for chapter-level lookup
            course_id: Optional course UUID for course-level lookup
            allow_fallback: If True, allows returning None instead of raising error
                           (should only be used for preview/validation)

        Returns:
            ResolvedModel with model details

        Raises:
            ModelNotConfiguredError: If no model configured and LM requires one
            ValueError: If learning_method_id is invalid
        """
        # Validate LM ID
        if learning_method_id < 0 or learning_method_id > 32:
            raise ValueError(f'Invalid learning_method_id: {learning_method_id}')

        # Get LM definition for better error messages
        lm_def = get_method_by_id(learning_method_id)
        lm_name = lm_def.name if lm_def else None

        # Use the database function to resolve
        result = LMModelAssignmentRepository.resolve_model_for_lm(
            learning_method_id=learning_method_id,
            chapter_id=chapter_id,
            course_id=course_id
        )

        # Check if model is configured
        if result.get('is_configured'):
            return ResolvedModel(
                model_id=result['model_id'],
                model_name=result['model_name'],
                provider_name=result['provider_name'],
                scope=result['scope'],
                learning_method_id=learning_method_id
            )

        # No model configured - check if required
        is_required = LMModelRequirementsRepository.is_model_required(learning_method_id)

        if is_required and not allow_fallback:
            raise ModelNotConfiguredError(learning_method_id, lm_name)

        # Optional LM with no model - return None (caller should handle)
        return None

    @staticmethod
    def resolve_with_details(
        learning_method_id: int,
        chapter_id: str = None,
        course_id: str = None
    ) -> Dict[str, Any]:
        """
        Resolve model with full details including whether generation is allowed.

        Useful for UI to show status before generation.

        Returns:
            Dict with:
            - model_id, model_name, provider_name, scope (if configured)
            - is_configured: bool
            - model_required: bool
            - can_generate: bool
            - error_message: str (if can_generate is False)
        """
        lm_def = get_method_by_id(learning_method_id)
        lm_name = lm_def.name if lm_def else f'LM{learning_method_id}'
        lm_code = f'LM{str(learning_method_id).zfill(2)}'

        result = LMModelAssignmentRepository.resolve_model_for_lm(
            learning_method_id=learning_method_id,
            chapter_id=chapter_id,
            course_id=course_id
        )

        is_required = LMModelRequirementsRepository.is_model_required(learning_method_id)
        is_configured = result.get('is_configured', False)
        can_generate = is_configured or not is_required

        response = {
            'learning_method_id': learning_method_id,
            'lm_code': lm_code,
            'lm_name': lm_name,
            'model_id': result.get('model_id'),
            'model_name': result.get('model_name'),
            'provider_name': result.get('provider_name'),
            'scope': result.get('scope', 'none'),
            'is_configured': is_configured,
            'model_required': is_required,
            'can_generate': can_generate,
            'error_message': None
        }

        if not can_generate:
            response['error_message'] = (
                f'Kein KI-Modell konfiguriert für {lm_code} ({lm_name}). '
                f'Bitte konfiguriere ein Modell in Admin > KI-Einstellungen > Lernmethoden-Modelle.'
            )

        return response

    @staticmethod
    def get_model_for_generation(
        learning_method_id: int,
        chapter_id: str = None,
        course_id: str = None
    ) -> Dict[str, Any]:
        """
        Get full model details for generation.

        This is the main entry point for AI generation services.
        Returns complete model info including API key status.

        Args:
            learning_method_id: Learning method ID
            chapter_id: Optional chapter context
            course_id: Optional course context

        Returns:
            Dict with model_name, provider, context_window, etc.

        Raises:
            ModelNotConfiguredError: If no model configured for required LM
        """
        resolved = LMModelResolver.resolve(
            learning_method_id=learning_method_id,
            chapter_id=chapter_id,
            course_id=course_id
        )

        if resolved is None:
            # Optional LM with no model - return empty dict
            return {
                'model_configured': False,
                'learning_method_id': learning_method_id
            }

        # Get full model details from repository
        model = AIModelsRepository.get_by_id(resolved.model_id)

        if not model:
            raise ModelNotConfiguredError(
                learning_method_id,
                get_method_by_id(learning_method_id).name if get_method_by_id(learning_method_id) else None
            )

        return {
            'model_configured': True,
            'model_id': model.get('model_id'),
            'model_name': model.get('model_name'),
            'display_name': model.get('display_name'),
            'provider_name': resolved.provider_name,
            'provider_id': model.get('provider_id'),
            'context_window': model.get('context_window'),
            'max_output_tokens': model.get('max_output_tokens'),
            'supports_vision': model.get('supports_vision', False),
            'supports_functions': model.get('supports_functions', False),
            'category': model.get('category'),
            'resolution_scope': resolved.scope,
            'learning_method_id': learning_method_id
        }

    @staticmethod
    def validate_all_required_configured() -> Dict[str, Any]:
        """
        Check if all required learning methods have models configured.

        Useful for system health check and admin dashboard.

        Returns:
            Dict with:
            - all_configured: bool
            - missing_count: int
            - missing: List of unconfigured required LMs
        """
        unconfigured = LMModelAssignmentRepository.get_unconfigured_lms()

        return {
            'all_configured': len(unconfigured) == 0,
            'missing_count': len(unconfigured),
            'missing': [
                {
                    'learning_method_id': lm['learning_method_id'],
                    'lm_code': f'LM{str(lm["learning_method_id"]).zfill(2)}',
                    'recommended_categories': lm.get('recommended_categories', ['chat'])
                }
                for lm in unconfigured
            ]
        }
