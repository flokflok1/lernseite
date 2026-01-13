"""
LM Slot Resolver Repository

Repository for resolving which models are assigned to which slots:
- Hierarchical resolution (chapter > course > system)
- Required slot validation
- Configuration status checking

Uses the resolve_lm_slot_models database function for the heavy lifting.

Author: LernsystemX Team
Date: 2025-12-29
"""

from typing import Optional, List, Dict, Any

from app.database.connection import fetch_all
from app.repositories.base_repository import BaseRepository


class LMSlotResolverRepository(BaseRepository):
    """
    Repository for resolving models for LM slots.

    Uses the resolve_lm_slot_models database function to implement
    hierarchical resolution: chapter > course > system scope.
    """

    @classmethod
    def resolve_all_slots(
        cls,
        learning_method_id: int,
        chapter_id: str = None,
        course_id: str = None
    ) -> List[Dict]:
        """
        Resolve all assigned models for all slots of an LM.

        Uses hierarchical resolution: chapter > course > system.

        Args:
            learning_method_id: LM ID (0-32)
            chapter_id: Chapter ID (optional, for chapter-level resolution)
            course_id: Course ID (optional, for course-level resolution)

        Returns:
            List of resolved slots with assigned models and configuration status
        """
        query = """
            SELECT * FROM resolve_lm_slot_models(%s, %s, %s)
        """
        return fetch_all(query, (learning_method_id, chapter_id, course_id))

    @classmethod
    def resolve_slot(
        cls,
        learning_method_id: int,
        slot_code: str,
        chapter_id: str = None,
        course_id: str = None
    ) -> Optional[Dict]:
        """
        Resolve the model for a specific slot.

        Args:
            learning_method_id: LM ID
            slot_code: Slot code (e.g., 'chat')
            chapter_id: Chapter ID (optional)
            course_id: Course ID (optional)

        Returns:
            Resolved slot record or None if not found
        """
        results = cls.resolve_all_slots(learning_method_id, chapter_id, course_id)
        for slot in results:
            if slot['slot_code'] == slot_code:
                return slot
        return None

    @classmethod
    def check_required_slots_configured(
        cls,
        learning_method_id: int,
        chapter_id: str = None,
        course_id: str = None
    ) -> Dict[str, Any]:
        """
        Check if all required slots for an LM are configured.

        Validates that every required slot has a model assigned
        at the requested scope level.

        Args:
            learning_method_id: LM ID
            chapter_id: Chapter ID (optional)
            course_id: Course ID (optional)

        Returns:
            Dictionary with:
            - all_configured: bool - True if all required slots are configured
            - configured_count: int - Number of configured required slots
            - required_count: int - Total number of required slots
            - missing_slots: list - Slot codes that are not configured
        """
        results = cls.resolve_all_slots(learning_method_id, chapter_id, course_id)

        required_slots = []
        missing_slots = []

        for slot in results:
            if slot['is_required']:
                required_slots.append(slot['slot_code'])
                if not slot['is_configured']:
                    missing_slots.append(slot['slot_code'])

        return {
            'all_configured': len(missing_slots) == 0,
            'configured_count': len(required_slots) - len(missing_slots),
            'required_count': len(required_slots),
            'missing_slots': missing_slots
        }
