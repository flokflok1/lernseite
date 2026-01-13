"""
Learning Methods Services (DDD)

Domain services for learning methods business logic.
"""

from typing import List, Dict, Any, Optional
import logging

from .value_objects import MethodGroup, MethodStatus, LearningMethodType

logger = logging.getLogger(__name__)


class MethodValidationService:
    """
    Service for validating learning method operations.

    Domain Service: Complex validation logic.
    """

    @staticmethod
    def validate_method_type(method_type: int) -> bool:
        """
        Validate method_type is in allowed range.

        Args:
            method_type: Method type to validate

        Returns:
            True if valid

        Raises:
            ValueError: If method_type invalid

        Business Rules:
        - Must be 0-11 (12 Content-Lernmethoden)
        """
        if not isinstance(method_type, int):
            raise ValueError(f"method_type must be int, got {type(method_type)}")

        if not (0 <= method_type <= 11):
            raise ValueError(
                f"method_type must be 0-11 (12 Content-LMs), got {method_type}"
            )

        return True

    @staticmethod
    def validate_status_transition(
        current_status: MethodStatus,
        new_status: MethodStatus
    ) -> bool:
        """
        Validate status transition is allowed.

        Args:
            current_status: Current status
            new_status: Desired new status

        Returns:
            True if transition allowed

        Raises:
            ValueError: If transition not allowed

        Business Rules:
        - DRAFT → PUBLISHED: Allowed
        - DRAFT → ARCHIVED: Allowed
        - PUBLISHED → DRAFT: Allowed (unpublish)
        - PUBLISHED → ARCHIVED: Allowed
        - ARCHIVED → *: Not allowed (archived is final)
        """
        if current_status == MethodStatus.ARCHIVED:
            raise ValueError("Cannot change status of archived method")

        # All other transitions allowed
        return True

    @staticmethod
    def validate_reorder_list(
        method_ids: List[str],
        existing_ids: List[str]
    ) -> bool:
        """
        Validate reorder list contains all and only existing methods.

        Args:
            method_ids: New order of method IDs
            existing_ids: Existing method IDs in chapter

        Returns:
            True if valid

        Raises:
            ValueError: If lists don't match

        Business Rules:
        - Must contain exactly the same IDs
        - No duplicates
        - No missing IDs
        - No extra IDs
        """
        method_set = set(method_ids)
        existing_set = set(existing_ids)

        # Check for duplicates
        if len(method_set) != len(method_ids):
            raise ValueError("method_ids contains duplicates")

        # Check for missing IDs
        missing = existing_set - method_set
        if missing:
            raise ValueError(f"Missing method IDs: {missing}")

        # Check for extra IDs
        extra = method_set - existing_set
        if extra:
            raise ValueError(f"Extra method IDs not in chapter: {extra}")

        return True


class MethodEnrichmentService:
    """
    Service for enriching method instances with type information.

    Domain Service: Combines instance data with type metadata.
    """

    @staticmethod
    def enrich_instance(
        instance: Dict[str, Any],
        method_types: Dict[int, LearningMethodType]
    ) -> Dict[str, Any]:
        """
        Enrich instance with method type information.

        Args:
            instance: Method instance data
            method_types: Mapping of method_type → LearningMethodType

        Returns:
            Enriched instance dict

        Business Rules:
        - Adds type metadata to instance
        - Preserves all instance fields
        """
        method_type = instance.get('method_type')
        enriched = dict(instance)

        if method_type in method_types:
            type_info = method_types[method_type]
            enriched['type_info'] = type_info.to_dict()

        return enriched

    @staticmethod
    def calculate_statistics(instances: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate statistics for method instances.

        Args:
            instances: List of method instances

        Returns:
            Statistics dict

        Business Rules:
        - Count by status
        - Count by group
        - Total count
        """
        total = len(instances)
        by_status = {
            'draft': 0,
            'published': 0,
            'archived': 0
        }
        by_group = {
            'A': 0,
            'B': 0,
            'C': 0
        }

        for instance in instances:
            # Count by status
            status = instance.get('status', 'draft')
            if status in by_status:
                by_status[status] += 1

            # Count by group (from method_type)
            method_type = instance.get('method_type')
            if method_type is not None:
                try:
                    group = MethodGroup.from_method_type(method_type)
                    by_group[group.value] += 1
                except ValueError:
                    pass

        return {
            'total': total,
            'by_status': by_status,
            'by_group': by_group
        }
