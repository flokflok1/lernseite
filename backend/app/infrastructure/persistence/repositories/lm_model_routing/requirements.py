"""
Learning Method Model Requirements Repository

Handles LM requirements and validation for model assignment constraints.
Specifies which learning methods require AI models vs. optional fallbacks.

Methods:
  - get_all_requirements: Fetch all LM requirements
  - get_requirement: Get requirement for specific LM
  - is_model_required: Check if LM requires a model assignment
  - update_requirement: Update LM requirement configuration

Phase KI-Architektur - Model Routing System
"""

from typing import Optional, Dict
from datetime import datetime

from app.infrastructure.persistence.database.connection import fetch_one, fetch_all
from app.infrastructure.persistence.repositories.core.base import BaseRepository


class LMModelRequirementsRepository(BaseRepository):
    """Repository for learning_method_model_requirements table

    Defines constraints and requirements for model assignments per learning
    method. Includes:
    - Whether model assignment is required or optional
    - Recommended AI model categories (vision, functions, etc.)
    - Minimum context window requirements
    - Special capability requirements (vision, functions)
    """

    table_name = 'learning_method_model_requirements'
    pk_column = 'requirement_id'

    @classmethod
    def get_all_requirements(cls) -> list[Dict]:
        """Get all learning method requirements.

        Returns:
            List of requirements with all metadata
        """
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
        """Get requirement configuration for a specific learning method.

        Args:
            learning_method_id: Learning method ID (0-32)

        Returns:
            Requirement dict or None if not configured
        """
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
        """Check if a model assignment is required for this learning method.

        Returns True for LMs that need AI model assignment (no fallback available).
        Returns False for optional/offline LMs.

        Args:
            learning_method_id: Learning method ID

        Returns:
            True if model is required, False if optional
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
        data: Dict,
    ) -> Optional[Dict]:
        """Update requirement configuration for a learning method.

        Args:
            learning_method_id: Learning method ID
            data: Fields to update (partial update supported)

        Returns:
            Updated requirement or None if not found
        """
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
        return fetch_one(
            query,
            (
                data.get('required'),
                data.get('recommended_categories'),
                data.get('requires_vision'),
                data.get('requires_functions'),
                data.get('min_context_window'),
                data.get('description'),
                learning_method_id,
            ),
        )
