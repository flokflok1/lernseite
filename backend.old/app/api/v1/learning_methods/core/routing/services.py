"""
Routing Services (DDD)

Business logic for model routing, resolution, and recommendations.
"""

from typing import Dict, Any, List, Optional
from .value_objects import (
    RoutingStats,
    CostPreset,
    AssignmentScope
)


class RoutingResolutionService:
    """
    Service for resolving which model to use for a learning method.

    Domain Rules:
    - More specific scopes override less specific (chapter > course > system)
    - Returns None if no model configured and not required
    - Validates context (course_id, chapter_id)
    """

    @staticmethod
    def resolve_model(
        learning_method_id: int,
        assignments: List[Dict[str, Any]],
        course_id: Optional[str] = None,
        chapter_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Resolve which model to use given context.

        Resolution order:
        1. Chapter-level assignment (if chapter_id provided)
        2. Course-level assignment (if course_id provided)
        3. System-level assignment

        Args:
            learning_method_id: LM ID
            assignments: List of all assignments for this LM
            course_id: Optional course context
            chapter_id: Optional chapter context

        Returns:
            Resolved assignment or None if no match

        DDD: Business rule - hierarchical scope resolution
        """
        if not assignments:
            return None

        # Filter assignments by scope and context
        chapter_assignments = []
        course_assignments = []
        system_assignments = []

        for assignment in assignments:
            scope = AssignmentScope(assignment['scope'])

            if scope == AssignmentScope.CHAPTER:
                if chapter_id and assignment.get('chapter_id') == chapter_id:
                    chapter_assignments.append(assignment)

            elif scope == AssignmentScope.COURSE:
                if course_id and assignment.get('course_id') == course_id:
                    course_assignments.append(assignment)

            elif scope == AssignmentScope.SYSTEM:
                system_assignments.append(assignment)

        # Resolve in priority order
        if chapter_assignments:
            return chapter_assignments[0]
        if course_assignments:
            return course_assignments[0]
        if system_assignments:
            return system_assignments[0]

        return None

    @staticmethod
    def can_generate(
        resolved_assignment: Optional[Dict[str, Any]],
        is_required: bool
    ) -> bool:
        """
        Check if content can be generated with current configuration.

        Args:
            resolved_assignment: Resolved model assignment (or None)
            is_required: Whether model is required for this LM

        Returns:
            True if can generate, False otherwise

        DDD: Business rule - required LMs need model, optional don't
        """
        if resolved_assignment is not None:
            return True  # Model configured
        return not is_required  # Can generate if model not required


class RoutingRecommendationService:
    """
    Service for recommending models for learning methods.

    Domain Rules:
    - Matches model capabilities to LM requirements
    - Considers cost preferences
    - Validates compatibility
    """

    @staticmethod
    def score_model_for_lm(
        model: Dict[str, Any],
        requirement: Dict[str, Any],
        cost_priority: List[str]
    ) -> int:
        """
        Score a model for a learning method based on requirements.

        Higher score = better match.

        Args:
            model: Model data (category, supports_vision, etc.)
            requirement: LM requirement data
            cost_priority: Cost level priority list

        Returns:
            Score (higher is better)

        DDD: Business rule - score calculation logic
        """
        score = 0

        # Category match (+100)
        recommended_categories = requirement.get('recommended_categories', ['chat'])
        if model.get('category') in recommended_categories:
            score += 100

        # Vision requirement match (+50 if required and supported)
        if requirement.get('requires_vision', False):
            if model.get('supports_vision', False):
                score += 50
            else:
                return 0  # Hard requirement not met

        # Functions requirement match (+30 if required and supported)
        if requirement.get('requires_functions', False):
            if model.get('supports_functions', False):
                score += 30
            else:
                return 0  # Hard requirement not met

        # Context window requirement (+20 if meets minimum)
        min_context = requirement.get('min_context_window')
        if min_context:
            if model.get('context_window', 0) >= min_context:
                score += 20
            else:
                return 0  # Hard requirement not met

        # Cost priority (0-10 based on position in priority list)
        model_cost = model.get('cost_level', 'medium')
        try:
            cost_index = cost_priority.index(model_cost)
            score += (len(cost_priority) - cost_index) * 2
        except ValueError:
            pass  # Cost not in priority list

        return score

    @staticmethod
    def recommend_models(
        models: List[Dict[str, Any]],
        requirement: Dict[str, Any],
        cost_preset: CostPreset = CostPreset.MEDIUM,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Recommend top models for a learning method.

        Args:
            models: Available models
            requirement: LM requirement
            cost_preset: Cost preference
            limit: Maximum recommendations

        Returns:
            Top N recommended models with scores

        DDD: Business rule - recommendation algorithm
        """
        cost_priority = cost_preset.cost_priority

        # Score all models
        scored_models = []
        for model in models:
            score = RoutingRecommendationService.score_model_for_lm(
                model, requirement, cost_priority
            )
            if score > 0:  # Only include compatible models
                scored_models.append({
                    **model,
                    'recommendation_score': score
                })

        # Sort by score (descending)
        scored_models.sort(
            key=lambda m: m['recommendation_score'],
            reverse=True
        )

        return scored_models[:limit]


class RoutingStatsService:
    """
    Service for calculating routing statistics.

    Domain Rules:
    - Counts configured vs unconfigured LMs
    - Distinguishes required vs optional
    - Calculates completion percentage
    """

    @staticmethod
    def calculate_stats(
        assignments: List[Dict[str, Any]],
        requirements: Dict[int, Dict[str, Any]],
        total_lms: int = 12
    ) -> RoutingStats:
        """
        Calculate routing overview statistics.

        Args:
            assignments: List of all LM assignments
            requirements: Dict of {lm_id: requirement}
            total_lms: Total number of LMs (default 12)

        Returns:
            RoutingStats value object

        DDD: Business rule - stats calculation
        """
        configured = len(set(a['learning_method_id'] for a in assignments))
        unconfigured_required = 0
        unconfigured_optional = 0

        # Count unconfigured LMs
        configured_lm_ids = set(a['learning_method_id'] for a in assignments)
        for lm_id in range(total_lms):
            if lm_id not in configured_lm_ids:
                req = requirements.get(lm_id, {})
                if req.get('required', True):
                    unconfigured_required += 1
                else:
                    unconfigured_optional += 1

        return RoutingStats(
            total=total_lms,
            configured=configured,
            unconfigured_required=unconfigured_required,
            unconfigured_optional=unconfigured_optional
        )

    @staticmethod
    def is_lm_configured(
        lm_id: int,
        assignments: List[Dict[str, Any]]
    ) -> bool:
        """
        Check if a specific LM has any model assignment.

        Args:
            lm_id: Learning method ID
            assignments: List of all assignments

        Returns:
            True if configured, False otherwise
        """
        return any(
            a['learning_method_id'] == lm_id
            for a in assignments
        )
