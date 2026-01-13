"""
Learning Method Model Resolution Repository

Handles hierarchical model resolution for learning methods.
Implements the model selection logic: Chapter -> Course -> System fallback.

Methods:
  - resolve_model_for_lm: Resolve best matching model with hierarchical fallback
  - get_unconfigured_lms: Get LMs missing required model configuration

Phase KI-Architektur - Model Routing System
"""

from typing import Optional, List, Dict

from app.database.connection import fetch_one, fetch_all
from app.repositories.base_repository import BaseRepository


class LMModelResolverRepository(BaseRepository):
    """Repository for hierarchical model resolution logic

    Implements the model resolution strategy:
    1. Check chapter-level override (highest priority)
    2. Check course-level override
    3. Fall back to system-level assignment (lowest priority)
    4. Return None if no configuration found

    This uses the resolve_lm_model() PostgreSQL function for efficient
    hierarchical lookup.
    """

    table_name = 'learning_method_model_assignments'
    pk_column = 'assignment_id'

    @classmethod
    def resolve_model_for_lm(
        cls,
        learning_method_id: int,
        chapter_id: str = None,
        course_id: str = None,
    ) -> Dict:
        """Resolve the best matching model for a learning method.

        Uses hierarchical resolution: Chapter -> Course -> System

        Args:
            learning_method_id: Learning method ID (0-32)
            chapter_id: Optional chapter ID for chapter-level override
            course_id: Optional course ID for course-level override

        Returns:
            Dict with keys:
              - model_id: AI model ID or None
              - model_name: Model name or None
              - provider_name: Provider name or None
              - scope: Resolution scope ('chapter', 'course', 'system', 'none')
              - is_configured: True if model is configured, False if fallback
        """
        query = "SELECT * FROM resolve_lm_model(%s, %s, %s)"
        result = fetch_one(query, (learning_method_id, chapter_id, course_id))

        if result:
            return {
                'model_id': result.get('model_id'),
                'model_name': result.get('model_name'),
                'provider_name': result.get('provider_name'),
                'scope': result.get('scope'),
                'is_configured': result.get('is_configured', False),
            }

        return {
            'model_id': None,
            'model_name': None,
            'provider_name': None,
            'scope': 'none',
            'is_configured': False,
        }

    @classmethod
    def get_unconfigured_lms(cls) -> List[Dict]:
        """Get all learning methods that require a model but don't have one.

        Returns learning methods marked as 'required' in requirements table
        that lack an active system-level assignment.

        Returns:
            List of unconfigured required LMs with metadata
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
