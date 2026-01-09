"""
LM Slot Repository - Capability Slots CRUD

Repository for capability_slots table:
- Slot definitions (capabilities like 'chat', 'vision', 'stt')
- Slot metadata (categories, icons, display names)
- Lookup operations by code or ID

Author: LernsystemX Team
Date: 2025-12-29
"""

from typing import Optional, List, Dict

from app.database.connection import fetch_one, fetch_all
from app.repositories.base_repository import BaseRepository


class CapabilitySlotRepository(BaseRepository):
    """
    Repository for capability_slots table.

    Manages slot definitions and metadata.
    """

    table_name = 'learning_methods.capability_slots'
    pk_column = 'slot_id'

    @classmethod
    def find_by_code(cls, slot_code: str) -> Optional[Dict]:
        """
        Find slot by its unique code.

        Args:
            slot_code: Unique slot code (e.g., 'chat', 'vision', 'stt')

        Returns:
            Slot record or None if not found
        """
        query = "SELECT * FROM learning_methods.capability_slots WHERE slot_code = %s"
        return fetch_one(query, (slot_code,))

    @classmethod
    def find_all_sorted(cls) -> List[Dict]:
        """
        Get all slots sorted by sort_order.

        Returns:
            List of all slot records ordered by sort_order then slot_code
        """
        query = """
            SELECT * FROM learning_methods.capability_slots
            ORDER BY sort_order ASC, slot_code ASC
        """
        return fetch_all(query)

    @classmethod
    def get_slot_id_by_code(cls, slot_code: str) -> Optional[int]:
        """
        Get slot_id by slot_code.

        Args:
            slot_code: Unique slot code

        Returns:
            slot_id if found, None otherwise
        """
        query = "SELECT slot_id FROM learning_methods.capability_slots WHERE slot_code = %s"
        result = fetch_one(query, (slot_code,))
        return result['slot_id'] if result else None
