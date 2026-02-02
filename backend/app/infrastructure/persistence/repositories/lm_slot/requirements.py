"""
LM Slot Requirements Repository

Repository for lm_slot_requirements table:
- LM → Slot mappings (which slots does each LM need?)
- Required vs optional slots
- Primary slot designation
- Queries across LM/slot relationships

Author: LernsystemX Team
Date: 2025-12-29
"""

from typing import Optional, List, Dict

from app.infrastructure.persistence.database.connection import fetch_one, fetch_all
from app.infrastructure.persistence.repositories.base_repository import BaseRepository


class LMSlotRequirementRepository(BaseRepository):
    """
    Repository for lm_slot_requirements table.

    Manages which slots are required by each learning method.
    """

    table_name = 'lm_slot_requirements'
    pk_column = 'requirement_id'

    @classmethod
    def find_by_lm(cls, learning_method_id: int) -> List[Dict]:
        """
        Get all slot requirements for a learning method.

        Joins with capability_slots to include slot definitions.

        Args:
            learning_method_id: Learning method ID (0-32)

        Returns:
            List of requirements with slot metadata joined
        """
        query = """
            SELECT
                r.requirement_id,
                r.learning_method_id,
                r.slot_id,
                r.is_required,
                r.is_primary,
                r.usage_description,
                s.slot_code,
                s.display_name AS slot_display_name,
                s.description AS slot_description,
                s.required_category,
                s.accepted_categories,
                s.icon,
                s.sort_order
            FROM lm_slot_requirements r
            JOIN learning_methods.capability_slots s ON r.slot_id = s.slot_id
            WHERE r.learning_method_id = %s
            ORDER BY r.is_primary DESC, r.is_required DESC, s.sort_order ASC
        """
        return fetch_all(query, (learning_method_id,))

    @classmethod
    def find_by_lm_and_slot(
        cls,
        learning_method_id: int,
        slot_code: str
    ) -> Optional[Dict]:
        """
        Get specific slot requirement for an LM.

        Args:
            learning_method_id: Learning method ID
            slot_code: Slot code (e.g., 'chat')

        Returns:
            Requirement record or None if not found
        """
        query = """
            SELECT r.*, s.slot_code, s.display_name AS slot_display_name
            FROM lm_slot_requirements r
            JOIN learning_methods.capability_slots s ON r.slot_id = s.slot_id
            WHERE r.learning_method_id = %s AND s.slot_code = %s
        """
        return fetch_one(query, (learning_method_id, slot_code))

    @classmethod
    def get_required_slots_for_lm(cls, learning_method_id: int) -> List[str]:
        """
        Get list of required slot codes for an LM.

        Returns only slots marked as required=true.

        Args:
            learning_method_id: Learning method ID

        Returns:
            List of required slot codes ordered by sort_order
        """
        query = """
            SELECT s.slot_code
            FROM lm_slot_requirements r
            JOIN learning_methods.capability_slots s ON r.slot_id = s.slot_id
            WHERE r.learning_method_id = %s AND r.is_required = TRUE
            ORDER BY s.sort_order
        """
        results = fetch_all(query, (learning_method_id,))
        return [r['slot_code'] for r in results]

    @classmethod
    def get_lms_requiring_slot(cls, slot_code: str) -> List[int]:
        """
        Get all LM IDs that require a specific slot.

        Returns only LMs that have is_required=true for this slot.

        Args:
            slot_code: Slot code (e.g., 'chat')

        Returns:
            List of learning method IDs
        """
        query = """
            SELECT r.learning_method_id
            FROM lm_slot_requirements r
            JOIN learning_methods.capability_slots s ON r.slot_id = s.slot_id
            WHERE s.slot_code = %s AND r.is_required = TRUE
            ORDER BY r.learning_method_id
        """
        results = fetch_all(query, (slot_code,))
        return [r['learning_method_id'] for r in results]
