"""
LernsystemX LM Slot Repository

Database access for the Capability Slots system:
- capability_slots - Slot definitions
- lm_slot_requirements - LM → Slot mapping
- lm_slot_assignments - Admin assignments

Author: LernsystemX Team
Date: 2025-12-04
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from app.database.connection import (
    fetch_one,
    fetch_all,
    insert_returning,
    update_returning,
    delete_returning,
    execute_query
)
from app.repositories.base_repository import BaseRepository


class CapabilitySlotRepository(BaseRepository):
    """Repository for capability_slots table."""

    table_name = 'capability_slots'
    pk_column = 'slot_id'

    @classmethod
    def find_by_code(cls, slot_code: str) -> Optional[Dict]:
        """Find slot by its unique code."""
        query = "SELECT * FROM capability_slots WHERE slot_code = %s"
        return fetch_one(query, (slot_code,))

    @classmethod
    def find_all_sorted(cls) -> List[Dict]:
        """Get all slots sorted by sort_order."""
        query = """
            SELECT * FROM capability_slots
            ORDER BY sort_order ASC, slot_code ASC
        """
        return fetch_all(query)

    @classmethod
    def get_slot_id_by_code(cls, slot_code: str) -> Optional[int]:
        """Get slot_id by slot_code."""
        query = "SELECT slot_id FROM capability_slots WHERE slot_code = %s"
        result = fetch_one(query, (slot_code,))
        return result['slot_id'] if result else None


class LMSlotRequirementRepository(BaseRepository):
    """Repository for lm_slot_requirements table."""

    table_name = 'lm_slot_requirements'
    pk_column = 'requirement_id'

    @classmethod
    def find_by_lm(cls, learning_method_id: int) -> List[Dict]:
        """
        Get all slot requirements for a learning method.

        Returns slots with their definitions joined.
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
            JOIN capability_slots s ON r.slot_id = s.slot_id
            WHERE r.learning_method_id = %s
            ORDER BY r.is_primary DESC, r.is_required DESC, s.sort_order ASC
        """
        return fetch_all(query, (learning_method_id,))

    @classmethod
    def find_by_lm_and_slot(cls, learning_method_id: int, slot_code: str) -> Optional[Dict]:
        """Get specific slot requirement for an LM."""
        query = """
            SELECT r.*, s.slot_code, s.display_name AS slot_display_name
            FROM lm_slot_requirements r
            JOIN capability_slots s ON r.slot_id = s.slot_id
            WHERE r.learning_method_id = %s AND s.slot_code = %s
        """
        return fetch_one(query, (learning_method_id, slot_code))

    @classmethod
    def get_required_slots_for_lm(cls, learning_method_id: int) -> List[str]:
        """Get list of required slot codes for an LM."""
        query = """
            SELECT s.slot_code
            FROM lm_slot_requirements r
            JOIN capability_slots s ON r.slot_id = s.slot_id
            WHERE r.learning_method_id = %s AND r.is_required = TRUE
            ORDER BY s.sort_order
        """
        results = fetch_all(query, (learning_method_id,))
        return [r['slot_code'] for r in results]

    @classmethod
    def get_lms_requiring_slot(cls, slot_code: str) -> List[int]:
        """Get all LM IDs that require a specific slot."""
        query = """
            SELECT r.learning_method_id
            FROM lm_slot_requirements r
            JOIN capability_slots s ON r.slot_id = s.slot_id
            WHERE s.slot_code = %s AND r.is_required = TRUE
            ORDER BY r.learning_method_id
        """
        results = fetch_all(query, (slot_code,))
        return [r['learning_method_id'] for r in results]


class LMSlotAssignmentRepository(BaseRepository):
    """Repository for lm_slot_assignments table."""

    table_name = 'lm_slot_assignments'
    pk_column = 'assignment_id'

    @classmethod
    def find_by_lm_and_slot(
        cls,
        learning_method_id: int,
        slot_code: str,
        scope: str = 'system',
        scope_reference_id: str = None
    ) -> Optional[Dict]:
        """
        Find assignment for a specific LM, slot, and scope.

        Args:
            learning_method_id: LM ID (0-32)
            slot_code: Slot code (e.g., 'chat', 'stt')
            scope: 'system', 'course', or 'chapter'
            scope_reference_id: Course or chapter ID (for non-system scope)
        """
        query = """
            SELECT
                a.*,
                s.slot_code,
                s.display_name AS slot_display_name,
                m.model_name,
                m.display_name AS model_display_name,
                m.category AS model_category,
                p.name AS provider_name,
                p.display_name AS provider_display_name
            FROM lm_slot_assignments a
            JOIN capability_slots s ON a.slot_id = s.slot_id
            JOIN ai_models m ON a.model_id = m.model_id
            LEFT JOIN ai_providers p ON m.provider_id = p.provider_id
            WHERE a.learning_method_id = %s
            AND s.slot_code = %s
            AND a.scope = %s
            AND a.active = TRUE
        """
        params = [learning_method_id, slot_code, scope]

        if scope == 'system':
            query += " AND a.scope_reference_id IS NULL"
        else:
            query += " AND a.scope_reference_id = %s"
            params.append(scope_reference_id)

        return fetch_one(query, tuple(params))

    @classmethod
    def find_all_by_lm(
        cls,
        learning_method_id: int,
        scope: str = 'system',
        scope_reference_id: str = None
    ) -> List[Dict]:
        """
        Get all slot assignments for an LM at a specific scope.

        Returns assignments with model and slot details.
        """
        query = """
            SELECT
                a.assignment_id,
                a.learning_method_id,
                a.slot_id,
                a.model_id,
                a.scope,
                a.scope_reference_id,
                a.priority,
                a.active,
                s.slot_code,
                s.display_name AS slot_display_name,
                s.icon AS slot_icon,
                m.model_name,
                m.display_name AS model_display_name,
                m.category AS model_category,
                m.supports_vision,
                m.supports_functions,
                p.name AS provider_name,
                p.display_name AS provider_display_name
            FROM lm_slot_assignments a
            JOIN capability_slots s ON a.slot_id = s.slot_id
            JOIN ai_models m ON a.model_id = m.model_id
            LEFT JOIN ai_providers p ON m.provider_id = p.provider_id
            WHERE a.learning_method_id = %s
            AND a.scope = %s
            AND a.active = TRUE
        """
        params = [learning_method_id, scope]

        if scope == 'system':
            query += " AND a.scope_reference_id IS NULL"
        else:
            query += " AND a.scope_reference_id = %s"
            params.append(scope_reference_id)

        query += " ORDER BY a.priority ASC, s.sort_order ASC"

        return fetch_all(query, tuple(params))

    @classmethod
    def get_system_overview(cls) -> List[Dict]:
        """
        Get overview of all LM slot assignments at system level.

        Used by admin dashboard for LM routing overview.
        """
        query = """
            SELECT
                lm.learning_method_id,
                s.slot_code,
                s.display_name AS slot_name,
                s.icon AS slot_icon,
                lsr.is_required,
                lsr.is_primary,
                a.assignment_id,
                m.model_id,
                m.model_name,
                m.display_name AS model_display_name,
                p.name AS provider_name
            FROM (SELECT generate_series(0, 32) AS learning_method_id) lm
            CROSS JOIN capability_slots s
            LEFT JOIN lm_slot_requirements lsr
                ON lm.learning_method_id = lsr.learning_method_id
                AND s.slot_id = lsr.slot_id
            LEFT JOIN lm_slot_assignments a
                ON lm.learning_method_id = a.learning_method_id
                AND s.slot_id = a.slot_id
                AND a.scope = 'system'
                AND a.active = TRUE
            LEFT JOIN ai_models m ON a.model_id = m.model_id
            LEFT JOIN ai_providers p ON m.provider_id = p.provider_id
            WHERE lsr.requirement_id IS NOT NULL
            ORDER BY lm.learning_method_id, lsr.is_primary DESC, lsr.is_required DESC, s.sort_order
        """
        return fetch_all(query)

    @classmethod
    def assign_model_to_slot(
        cls,
        learning_method_id: int,
        slot_code: str,
        model_id: int,
        scope: str = 'system',
        scope_reference_id: str = None,
        priority: int = 100,
        created_by: str = None
    ) -> Optional[Dict]:
        """
        Assign a model to a slot for an LM.

        If an assignment already exists for this LM/slot/scope, it will be
        deactivated and a new one created.
        """
        # Get slot_id from code
        slot = CapabilitySlotRepository.find_by_code(slot_code)
        if not slot:
            raise ValueError(f"Unknown slot code: {slot_code}")

        slot_id = slot['slot_id']

        # Deactivate existing assignment (if any)
        if scope == 'system':
            deactivate_query = """
                UPDATE lm_slot_assignments
                SET active = FALSE, updated_at = NOW()
                WHERE learning_method_id = %s
                AND slot_id = %s
                AND scope = 'system'
                AND active = TRUE
            """
            execute_query(deactivate_query, (learning_method_id, slot_id))
        else:
            deactivate_query = """
                UPDATE lm_slot_assignments
                SET active = FALSE, updated_at = NOW()
                WHERE learning_method_id = %s
                AND slot_id = %s
                AND scope = %s
                AND scope_reference_id = %s
                AND active = TRUE
            """
            execute_query(deactivate_query, (learning_method_id, slot_id, scope, scope_reference_id))

        # Create new assignment
        data = {
            'learning_method_id': learning_method_id,
            'slot_id': slot_id,
            'model_id': model_id,
            'scope': scope,
            'scope_reference_id': scope_reference_id,
            'priority': priority,
            'active': True,
            'created_by': created_by
        }

        return insert_returning(cls.table_name, data)

    @classmethod
    def remove_slot_assignment(
        cls,
        learning_method_id: int,
        slot_code: str,
        scope: str = 'system',
        scope_reference_id: str = None
    ) -> bool:
        """
        Remove (deactivate) a slot assignment.

        Returns True if an assignment was deactivated.
        """
        slot = CapabilitySlotRepository.find_by_code(slot_code)
        if not slot:
            return False

        slot_id = slot['slot_id']

        if scope == 'system':
            query = """
                UPDATE lm_slot_assignments
                SET active = FALSE, updated_at = NOW()
                WHERE learning_method_id = %s
                AND slot_id = %s
                AND scope = 'system'
                AND active = TRUE
                RETURNING assignment_id
            """
            result = fetch_one(query, (learning_method_id, slot_id))
        else:
            query = """
                UPDATE lm_slot_assignments
                SET active = FALSE, updated_at = NOW()
                WHERE learning_method_id = %s
                AND slot_id = %s
                AND scope = %s
                AND scope_reference_id = %s
                AND active = TRUE
                RETURNING assignment_id
            """
            result = fetch_one(query, (learning_method_id, slot_id, scope, scope_reference_id))

        return result is not None

    @classmethod
    def bulk_assign_slots(
        cls,
        learning_method_id: int,
        assignments: List[Dict[str, Any]],
        scope: str = 'system',
        scope_reference_id: str = None,
        created_by: str = None
    ) -> List[Dict]:
        """
        Bulk assign multiple slots for an LM.

        Args:
            learning_method_id: LM ID
            assignments: List of {slot_code, model_id, priority?}
            scope: Assignment scope
            scope_reference_id: Scope reference
            created_by: User ID

        Returns:
            List of created assignments
        """
        results = []
        for assignment in assignments:
            slot_code = assignment.get('slot_code')
            model_id = assignment.get('model_id')
            priority = assignment.get('priority', 100)

            if not slot_code or not model_id:
                continue

            result = cls.assign_model_to_slot(
                learning_method_id=learning_method_id,
                slot_code=slot_code,
                model_id=model_id,
                scope=scope,
                scope_reference_id=scope_reference_id,
                priority=priority,
                created_by=created_by
            )
            if result:
                results.append(result)

        return results

    @classmethod
    def get_compatible_models_for_slot(cls, slot_code: str) -> List[Dict]:
        """
        Get all models compatible with a slot.

        Uses the slot's required_category and accepted_categories to filter.
        """
        slot = CapabilitySlotRepository.find_by_code(slot_code)
        if not slot:
            return []

        required_category = slot['required_category']
        accepted_categories = slot.get('accepted_categories', []) or []

        # Build category list for IN clause
        all_categories = [required_category] + accepted_categories

        # Handle vision slot specially - needs models with supports_vision
        if slot_code == 'vision':
            query = """
                SELECT
                    m.model_id,
                    m.model_name,
                    m.display_name,
                    m.category,
                    m.supports_vision,
                    m.supports_functions,
                    m.context_window,
                    m.cost_level,
                    p.name AS provider_name,
                    p.display_name AS provider_display_name
                FROM ai_models m
                LEFT JOIN ai_providers p ON m.provider_id = p.provider_id
                WHERE m.active = TRUE
                AND m.supports_vision = TRUE
                ORDER BY m.display_name
            """
            return fetch_all(query)

        # Regular slot - filter by category
        placeholders = ', '.join(['%s'] * len(all_categories))
        query = f"""
            SELECT
                m.model_id,
                m.model_name,
                m.display_name,
                m.category,
                m.supports_vision,
                m.supports_functions,
                m.context_window,
                m.cost_level,
                p.name AS provider_name,
                p.display_name AS provider_display_name
            FROM ai_models m
            LEFT JOIN ai_providers p ON m.provider_id = p.provider_id
            WHERE m.active = TRUE
            AND m.category IN ({placeholders})
            ORDER BY m.display_name
        """
        return fetch_all(query, tuple(all_categories))


class LMSlotResolverRepository:
    """
    Repository for resolving models for LM slots.

    Uses the resolve_lm_slot_models database function.
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

        Returns:
            {
                'all_configured': bool,
                'configured_count': int,
                'required_count': int,
                'missing_slots': [slot_code, ...]
            }
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
