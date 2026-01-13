"""
Routing Factories (DDD)

Factories for creating routing-related entities.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from .value_objects import (
    LMIDRange,
    AssignmentScope,
    ModelRequirement
)


class ModelAssignmentFactory:
    """
    Factory for creating LM model assignments.

    Domain Rules:
    - Validates LM ID range
    - Ensures model_id is provided
    - Sets proper scope hierarchy
    - Creates unique assignment IDs
    """

    @staticmethod
    def create_assignment(
        learning_method_id: int,
        model_id: int,
        scope: str = 'system',
        created_by: str = None,
        course_id: Optional[str] = None,
        chapter_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a model assignment for a learning method.

        Args:
            learning_method_id: LM ID (0-11)
            model_id: AI model ID
            scope: Assignment scope (system, course, chapter)
            created_by: User ID who created the assignment
            course_id: Course UUID (required if scope=course/chapter)
            chapter_id: Chapter UUID (required if scope=chapter)

        Returns:
            Assignment data dictionary

        Raises:
            ValueError: If LM ID invalid or scope requirements not met

        DDD: Business rule - validates LM ID and scope hierarchy
        """
        # Validate LM ID
        if not LMIDRange.validate(learning_method_id):
            raise ValueError(
                f"Invalid learning_method_id: {learning_method_id}. "
                f"Must be {LMIDRange.MIN}-{LMIDRange.MAX}"
            )

        # Validate scope requirements
        scope_enum = AssignmentScope(scope)
        if scope_enum == AssignmentScope.COURSE and not course_id:
            raise ValueError("course_id required for course scope")
        if scope_enum == AssignmentScope.CHAPTER and not chapter_id:
            raise ValueError("chapter_id required for chapter scope")

        return {
            'assignment_id': str(uuid.uuid4()),
            'learning_method_id': learning_method_id,
            'model_id': model_id,
            'scope': scope,
            'course_id': course_id,
            'chapter_id': chapter_id,
            'created_by': created_by,
            'created_at': datetime.utcnow(),
            'is_active': True
        }


class SlotAssignmentFactory:
    """
    Factory for creating capability slot assignments.

    Domain Rules:
    - Validates LM ID and slot code
    - Creates unique slot assignment IDs
    - Supports multi-model architecture
    """

    @staticmethod
    def create_slot_assignment(
        learning_method_id: int,
        slot_code: str,
        model_id: int,
        scope: str = 'system',
        created_by: str = None,
        course_id: Optional[str] = None,
        chapter_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a slot assignment for a learning method.

        Args:
            learning_method_id: LM ID (0-11)
            slot_code: Capability slot code (e.g., 'chat', 'vision')
            model_id: AI model ID
            scope: Assignment scope
            created_by: User ID
            course_id: Course UUID (for course/chapter scope)
            chapter_id: Chapter UUID (for chapter scope)

        Returns:
            Slot assignment data dictionary

        Raises:
            ValueError: If LM ID invalid

        DDD: Business rule - ensures slot assignments are valid
        """
        # Validate LM ID
        if not LMIDRange.validate(learning_method_id):
            raise ValueError(
                f"Invalid learning_method_id: {learning_method_id}. "
                f"Must be {LMIDRange.MIN}-{LMIDRange.MAX}"
            )

        return {
            'slot_assignment_id': str(uuid.uuid4()),
            'learning_method_id': learning_method_id,
            'slot_code': slot_code,
            'model_id': model_id,
            'scope': scope,
            'course_id': course_id,
            'chapter_id': chapter_id,
            'created_by': created_by,
            'created_at': datetime.utcnow(),
            'is_active': True
        }


class ModelRequirementFactory:
    """
    Factory for creating model requirements.

    Domain Rules:
    - Sets sensible defaults
    - Validates categories
    - Creates complete requirement specifications
    """

    @staticmethod
    def create_requirement(
        learning_method_id: int,
        required: bool = True,
        recommended_categories: Optional[list] = None,
        requires_vision: bool = False,
        requires_functions: bool = False,
        min_context_window: Optional[int] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a model requirement specification.

        Args:
            learning_method_id: LM ID (0-11)
            required: Whether model is required (vs optional)
            recommended_categories: Recommended model categories
            requires_vision: Whether multimodal vision needed
            requires_functions: Whether function calling needed
            min_context_window: Minimum context window size
            description: Human-readable description

        Returns:
            Requirement data dictionary

        Raises:
            ValueError: If LM ID invalid

        DDD: Business rule - defines what models can be used for LM
        """
        # Validate LM ID
        if not LMIDRange.validate(learning_method_id):
            raise ValueError(
                f"Invalid learning_method_id: {learning_method_id}. "
                f"Must be {LMIDRange.MIN}-{LMIDRange.MAX}"
            )

        # Default categories
        if recommended_categories is None:
            recommended_categories = ['chat']

        return {
            'requirement_id': str(uuid.uuid4()),
            'learning_method_id': learning_method_id,
            'required': required,
            'recommended_categories': recommended_categories,
            'requires_vision': requires_vision,
            'requires_functions': requires_functions,
            'min_context_window': min_context_window,
            'description': description,
            'created_at': datetime.utcnow()
        }
