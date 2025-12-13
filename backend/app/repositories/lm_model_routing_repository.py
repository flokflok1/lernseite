"""
LernsystemX Learning Method Model Routing Repository

Repository for managing Learning Method to AI Model assignments.
Implements hierarchical model resolution (System -> Course -> Chapter).

Phase KI-Architektur - Model Routing System
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from app.database.connection import fetch_one, fetch_all, insert_returning, update_returning, delete_returning, execute_query
from app.repositories.base_repository import BaseRepository


class LMModelAssignmentRepository(BaseRepository):
    """Repository for learning_method_model_assignments table"""

    table_name = 'learning_method_model_assignments'
    pk_column = 'assignment_id'

    @classmethod
    def get_system_assignments(cls) -> List[Dict]:
        """
        Get all system-level (global) model assignments.

        Returns:
            List of assignments with model and provider details
        """
        query = """
            SELECT
                a.assignment_id,
                a.learning_method_id,
                a.model_id,
                a.scope,
                a.priority,
                a.active,
                a.created_at,
                m.model_name,
                m.display_name AS model_display_name,
                m.category AS model_category,
                p.name AS provider_name,
                p.display_name AS provider_display_name
            FROM learning_method_model_assignments a
            JOIN ai_models m ON a.model_id = m.model_id
            LEFT JOIN ai_providers p ON m.provider_id = p.provider_id
            WHERE a.scope = 'system' AND a.active = TRUE
            ORDER BY a.learning_method_id ASC
        """
        return fetch_all(query)

    @classmethod
    def get_assignment_for_lm(
        cls,
        learning_method_id: int,
        scope: str = 'system',
        scope_reference_id: str = None
    ) -> Optional[Dict]:
        """
        Get assignment for a specific learning method and scope.

        Args:
            learning_method_id: Learning method ID (0-32)
            scope: 'system', 'course', or 'chapter'
            scope_reference_id: Course ID or Chapter ID (required for course/chapter scope)

        Returns:
            Assignment with model details or None
        """
        if scope == 'system':
            query = """
                SELECT
                    a.assignment_id,
                    a.learning_method_id,
                    a.model_id,
                    a.scope,
                    a.priority,
                    a.active,
                    m.model_name,
                    m.display_name AS model_display_name,
                    m.category AS model_category,
                    p.name AS provider_name,
                    p.display_name AS provider_display_name
                FROM learning_method_model_assignments a
                JOIN ai_models m ON a.model_id = m.model_id
                LEFT JOIN ai_providers p ON m.provider_id = p.provider_id
                WHERE a.learning_method_id = %s
                AND a.scope = 'system'
                AND a.active = TRUE
            """
            return fetch_one(query, (learning_method_id,))
        else:
            query = """
                SELECT
                    a.assignment_id,
                    a.learning_method_id,
                    a.model_id,
                    a.scope,
                    a.scope_reference_id,
                    a.priority,
                    a.active,
                    m.model_name,
                    m.display_name AS model_display_name,
                    m.category AS model_category,
                    p.name AS provider_name,
                    p.display_name AS provider_display_name
                FROM learning_method_model_assignments a
                JOIN ai_models m ON a.model_id = m.model_id
                LEFT JOIN ai_providers p ON m.provider_id = p.provider_id
                WHERE a.learning_method_id = %s
                AND a.scope = %s
                AND a.scope_reference_id = %s
                AND a.active = TRUE
            """
            return fetch_one(query, (learning_method_id, scope, scope_reference_id))

    @classmethod
    def resolve_model_for_lm(
        cls,
        learning_method_id: int,
        chapter_id: str = None,
        course_id: str = None
    ) -> Dict:
        """
        Resolve the best matching model for a learning method.
        Uses hierarchical resolution: Chapter -> Course -> System

        Args:
            learning_method_id: Learning method ID (0-32)
            chapter_id: Optional chapter ID for chapter-level override
            course_id: Optional course ID for course-level override

        Returns:
            Dict with model info and is_configured flag
        """
        query = "SELECT * FROM resolve_lm_model(%s, %s, %s)"
        result = fetch_one(query, (learning_method_id, chapter_id, course_id))

        if result:
            return {
                'model_id': result.get('model_id'),
                'model_name': result.get('model_name'),
                'provider_name': result.get('provider_name'),
                'scope': result.get('scope'),
                'is_configured': result.get('is_configured', False)
            }

        return {
            'model_id': None,
            'model_name': None,
            'provider_name': None,
            'scope': 'none',
            'is_configured': False
        }

    @classmethod
    def set_system_assignment(
        cls,
        learning_method_id: int,
        model_id: int,
        created_by: str = None
    ) -> Optional[Dict]:
        """
        Set or update system-level model assignment for a learning method.
        Deactivates existing assignment before creating new one.

        Args:
            learning_method_id: Learning method ID (0-32)
            model_id: AI model ID
            created_by: User ID who created the assignment

        Returns:
            Created assignment
        """
        # Deactivate existing system assignment for this LM
        deactivate_query = """
            UPDATE learning_method_model_assignments
            SET active = FALSE, updated_at = NOW()
            WHERE learning_method_id = %s AND scope = 'system' AND active = TRUE
        """
        execute_query(deactivate_query, (learning_method_id,))

        # Create new assignment
        data = {
            'learning_method_id': learning_method_id,
            'model_id': model_id,
            'scope': 'system',
            'scope_reference_id': None,
            'priority': 100,
            'active': True,
            'created_by': created_by
        }

        return insert_returning(cls.table_name, data, '*')

    @classmethod
    def set_course_assignment(
        cls,
        learning_method_id: int,
        model_id: int,
        course_id: str,
        created_by: str = None
    ) -> Optional[Dict]:
        """
        Set or update course-level model assignment.

        Args:
            learning_method_id: Learning method ID
            model_id: AI model ID
            course_id: Course UUID
            created_by: User ID

        Returns:
            Created assignment
        """
        # Deactivate existing course assignment for this LM and course
        deactivate_query = """
            UPDATE learning_method_model_assignments
            SET active = FALSE, updated_at = NOW()
            WHERE learning_method_id = %s
            AND scope = 'course'
            AND scope_reference_id = %s
            AND active = TRUE
        """
        execute_query(deactivate_query, (learning_method_id, course_id))

        data = {
            'learning_method_id': learning_method_id,
            'model_id': model_id,
            'scope': 'course',
            'scope_reference_id': course_id,
            'priority': 50,
            'active': True,
            'created_by': created_by
        }

        return insert_returning(cls.table_name, data, '*')

    @classmethod
    def set_chapter_assignment(
        cls,
        learning_method_id: int,
        model_id: int,
        chapter_id: str,
        created_by: str = None
    ) -> Optional[Dict]:
        """
        Set or update chapter-level model assignment.

        Args:
            learning_method_id: Learning method ID
            model_id: AI model ID
            chapter_id: Chapter UUID
            created_by: User ID

        Returns:
            Created assignment
        """
        # Deactivate existing chapter assignment
        deactivate_query = """
            UPDATE learning_method_model_assignments
            SET active = FALSE, updated_at = NOW()
            WHERE learning_method_id = %s
            AND scope = 'chapter'
            AND scope_reference_id = %s
            AND active = TRUE
        """
        execute_query(deactivate_query, (learning_method_id, chapter_id))

        data = {
            'learning_method_id': learning_method_id,
            'model_id': model_id,
            'scope': 'chapter',
            'scope_reference_id': chapter_id,
            'priority': 10,
            'active': True,
            'created_by': created_by
        }

        return insert_returning(cls.table_name, data, '*')

    @classmethod
    def remove_assignment(cls, assignment_id: int) -> Optional[Dict]:
        """
        Remove (deactivate) an assignment.

        Args:
            assignment_id: Assignment ID

        Returns:
            Updated assignment
        """
        query = """
            UPDATE learning_method_model_assignments
            SET active = FALSE, updated_at = NOW()
            WHERE assignment_id = %s
            RETURNING *
        """
        return fetch_one(query, (assignment_id,))

    @classmethod
    def get_overview(cls) -> List[Dict]:
        """
        Get overview of all learning methods with their model assignments.
        Uses the v_learning_method_model_overview view.

        Returns:
            List of all LMs with their assigned models (or NULL if not assigned)
        """
        query = """
            SELECT * FROM v_learning_method_model_overview
            ORDER BY learning_method_id ASC
        """
        return fetch_all(query)

    @classmethod
    def get_unconfigured_lms(cls) -> List[Dict]:
        """
        Get all learning methods that require a model but don't have one configured.

        Returns:
            List of unconfigured required LMs
        """
        query = """
            SELECT
                lmr.learning_method_id,
                lmr.required,
                lmr.recommended_categories,
                lmr.description
            FROM learning_method_model_requirements lmr
            LEFT JOIN learning_method_model_assignments a
                ON lmr.learning_method_id = a.learning_method_id
                AND a.scope = 'system'
                AND a.active = TRUE
            WHERE lmr.required = TRUE
            AND a.assignment_id IS NULL
            ORDER BY lmr.learning_method_id ASC
        """
        return fetch_all(query)

    @classmethod
    def get_assignments_for_course(cls, course_id: str) -> List[Dict]:
        """
        Get all model assignments for a specific course.

        Args:
            course_id: Course UUID

        Returns:
            List of course-level assignments
        """
        query = """
            SELECT
                a.assignment_id,
                a.learning_method_id,
                a.model_id,
                a.priority,
                m.model_name,
                m.display_name AS model_display_name,
                p.name AS provider_name
            FROM learning_method_model_assignments a
            JOIN ai_models m ON a.model_id = m.model_id
            LEFT JOIN ai_providers p ON m.provider_id = p.provider_id
            WHERE a.scope = 'course'
            AND a.scope_reference_id = %s
            AND a.active = TRUE
            ORDER BY a.learning_method_id ASC
        """
        return fetch_all(query, (course_id,))

    @classmethod
    def bulk_set_system_assignments(
        cls,
        assignments: List[Dict],
        created_by: str = None
    ) -> Dict:
        """
        Bulk set multiple system-level assignments.

        Args:
            assignments: List of {learning_method_id, model_id} dicts
            created_by: User ID

        Returns:
            Dict with counts (created, updated, errors)
        """
        created = 0
        errors = []

        for assignment in assignments:
            try:
                cls.set_system_assignment(
                    learning_method_id=assignment['learning_method_id'],
                    model_id=assignment['model_id'],
                    created_by=created_by
                )
                created += 1
            except Exception as e:
                errors.append({
                    'learning_method_id': assignment.get('learning_method_id'),
                    'error': str(e)
                })

        return {
            'created': created,
            'errors': errors
        }


class LMModelRequirementsRepository(BaseRepository):
    """Repository for learning_method_model_requirements table"""

    table_name = 'learning_method_model_requirements'
    pk_column = 'requirement_id'

    @classmethod
    def get_all_requirements(cls) -> List[Dict]:
        """Get all LM requirements."""
        query = """
            SELECT
                requirement_id,
                learning_method_id,
                required,
                recommended_categories,
                requires_vision,
                requires_functions,
                min_context_window,
                description
            FROM learning_method_model_requirements
            ORDER BY learning_method_id ASC
        """
        return fetch_all(query)

    @classmethod
    def get_requirement(cls, learning_method_id: int) -> Optional[Dict]:
        """Get requirement for a specific LM."""
        query = """
            SELECT
                requirement_id,
                learning_method_id,
                required,
                recommended_categories,
                requires_vision,
                requires_functions,
                min_context_window,
                description
            FROM learning_method_model_requirements
            WHERE learning_method_id = %s
        """
        return fetch_one(query, (learning_method_id,))

    @classmethod
    def is_model_required(cls, learning_method_id: int) -> bool:
        """
        Check if a model assignment is required for this LM.

        Args:
            learning_method_id: Learning method ID

        Returns:
            True if model is required (no fallback), False otherwise
        """
        req = cls.get_requirement(learning_method_id)
        if req:
            return req.get('required', True)
        # Default to required if not in table
        return True

    @classmethod
    def update_requirement(
        cls,
        learning_method_id: int,
        data: Dict
    ) -> Optional[Dict]:
        """
        Update requirement for a learning method.

        Args:
            learning_method_id: Learning method ID
            data: Fields to update

        Returns:
            Updated requirement
        """
        data['updated_at'] = datetime.utcnow()

        query = """
            UPDATE learning_method_model_requirements
            SET required = COALESCE(%s, required),
                recommended_categories = COALESCE(%s, recommended_categories),
                requires_vision = COALESCE(%s, requires_vision),
                requires_functions = COALESCE(%s, requires_functions),
                min_context_window = COALESCE(%s, min_context_window),
                description = COALESCE(%s, description),
                updated_at = NOW()
            WHERE learning_method_id = %s
            RETURNING *
        """
        return fetch_one(query, (
            data.get('required'),
            data.get('recommended_categories'),
            data.get('requires_vision'),
            data.get('requires_functions'),
            data.get('min_context_window'),
            data.get('description'),
            learning_method_id
        ))
