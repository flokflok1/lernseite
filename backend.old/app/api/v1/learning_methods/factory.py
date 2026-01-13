"""
Learning Methods Factories (DDD)

Factory Pattern for creating learning method instances and configurations.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from .value_objects import MethodStatus, LearningMethodType


class LearningMethodInstanceFactory:
    """
    Factory for creating learning method instances.

    Implements Domain-Driven Design (DDD) Factory Pattern.
    """

    @staticmethod
    def create_instance(
        chapter_id: str,
        method_type: int,
        title: str,
        created_by: str,
        content: Optional[Dict[str, Any]] = None,
        order: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create learning method instance.

        Args:
            chapter_id: Chapter UUID
            method_type: Method type (0-11)
            title: Instance title
            created_by: Creator user ID
            content: Optional method content
            order: Optional position order

        Returns:
            Instance configuration dict

        Business Rules:
        - method_type must be 0-11
        - Status defaults to DRAFT
        - Order defaults to 0 if not specified
        """
        # Validate method_type
        if not (0 <= method_type <= 11):
            raise ValueError(f"method_type must be 0-11, got {method_type}")

        return {
            'method_id': str(uuid.uuid4()),
            'chapter_id': chapter_id,
            'method_type': method_type,
            'title': title,
            'content': content or {},
            'status': MethodStatus.DRAFT.value,
            'order': order if order is not None else 0,
            'created_by': created_by,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

    @staticmethod
    def create_update_data(
        title: Optional[str] = None,
        content: Optional[Dict[str, Any]] = None,
        status: Optional[MethodStatus] = None,
        updated_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create update data for instance.

        Args:
            title: Optional new title
            content: Optional new content
            status: Optional new status
            updated_by: User ID making update

        Returns:
            Update data dict

        Business Rules:
        - Only non-None values are included
        - updated_at is always set
        """
        update_data = {'updated_at': datetime.utcnow()}

        if title is not None:
            update_data['title'] = title

        if content is not None:
            update_data['content'] = content

        if status is not None:
            update_data['status'] = status.value

        if updated_by is not None:
            update_data['updated_by'] = updated_by

        return update_data


class RoutingConfigFactory:
    """
    Factory for creating AI model routing configurations.

    Business rules for LM → AI Model assignments.
    """

    @staticmethod
    def create_assignment(
        method_type: int,
        model_id: str,
        priority: int = 1,
        assigned_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create model assignment configuration.

        Args:
            method_type: Method type (0-11)
            model_id: AI model ID
            priority: Assignment priority (default: 1)
            assigned_by: Optional user who made assignment

        Returns:
            Assignment configuration dict

        Business Rules:
        - method_type must be 0-11
        - priority must be >= 1
        """
        if not (0 <= method_type <= 11):
            raise ValueError(f"method_type must be 0-11, got {method_type}")

        if priority < 1:
            raise ValueError(f"priority must be >= 1, got {priority}")

        return {
            'assignment_id': str(uuid.uuid4()),
            'method_type': method_type,
            'model_id': model_id,
            'priority': priority,
            'assigned_by': assigned_by,
            'assigned_at': datetime.utcnow(),
            'is_active': True
        }

    @staticmethod
    def create_resolution_request(
        method_type: int,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create routing resolution request.

        Args:
            method_type: Method type to resolve
            user_id: User requesting resolution
            context: Optional additional context

        Returns:
            Resolution request dict

        Business Rules:
        - method_type must be 0-11
        - Context is optional
        """
        if not (0 <= method_type <= 11):
            raise ValueError(f"method_type must be 0-11, got {method_type}")

        return {
            'request_id': str(uuid.uuid4()),
            'method_type': method_type,
            'user_id': user_id,
            'context': context or {},
            'requested_at': datetime.utcnow()
        }
