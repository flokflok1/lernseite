"""
LernsystemX Runner Session Service - Part 2

Private helper methods for session resolution, scoring, and response building.
Split from session_service.py for Quality Gate G01 compliance (max 500 lines/file).
"""

from typing import Any, Dict, List, Optional, Tuple

from app.infrastructure.persistence.repositories.runner.modes import (
    RunnerModesRepository,
    RunnerModeFeatureMapRepository,
    LMTypeModeCompatibilityRepository
)
from app.infrastructure.persistence.repositories.features.system_features_repository import (
    CourseSystemFeaturesRepository
)
from app.infrastructure.persistence.repositories.learning_method import (
    LearningMethodInstanceStatisticsRepository,
    LearningMethodProgressRepository
)
from app.infrastructure.redis.runner_state import RunnerStateManager


class RunnerSessionHelpersMixin:
    """
    Mixin providing private helper methods for RunnerSessionService.

    Contains:
    - Method instance lookup and access checks
    - Runner mode resolution and compatibility
    - Feature resolution with course-level overrides
    - TTL calculation
    - Session response building
    - Score calculation and summary generation
    - Progress persistence
    """

    @classmethod
    def _get_method_instance(cls, method_id: str) -> Optional[Dict]:
        """Get learning method instance info via repository."""
        return LearningMethodInstanceStatisticsRepository.find_for_runner(method_id)

    @classmethod
    def _user_can_access_method(cls, user_id: str, method_info: Dict) -> bool:
        """Check if user has access to learning method."""
        # TODO: Implement proper access control
        # For now, allow access (enrollment check would go here)
        return True

    @classmethod
    def _resolve_runner_mode(
        cls,
        provided_code: Optional[str],
        instance_default_mode_id: Optional[int],
        method_type: int
    ) -> Optional[Dict]:
        """
        Resolve which runner mode to use.

        Priority:
        1. Provided mode_code (if valid)
        2. Instance default_mode_id
        3. Type default mode (from lm_type_mode_compatibility)
        4. Fallback: 'standard'
        """
        # 1. Try provided code
        if provided_code:
            mode = RunnerModesRepository.find_by_code(provided_code)
            if mode and mode.get('active'):
                return mode

        # 2. Try instance default
        if instance_default_mode_id:
            mode = RunnerModesRepository.find_by_id(instance_default_mode_id)
            if mode and mode.get('active'):
                return mode

        # 3. Try type default
        type_modes = LMTypeModeCompatibilityRepository.find_by_type(method_type)
        for tm in type_modes:
            if tm.get('is_default'):
                mode = RunnerModesRepository.find_by_id(tm['mode_id'])
                if mode and mode.get('active'):
                    return mode

        # 4. Fallback to 'standard'
        return RunnerModesRepository.find_by_code('standard')

    @classmethod
    def _check_mode_compatibility(cls, method_type: int, mode_id: int) -> bool:
        """Check if mode is compatible with LM type."""
        compatibilities = LMTypeModeCompatibilityRepository.find_by_type(method_type)

        # If no compatibility records, allow all modes
        if not compatibilities:
            return True

        # Check if mode_id is in compatible modes
        return any(c['mode_id'] == mode_id for c in compatibilities)

    @classmethod
    def _resolve_session_features(
        cls,
        mode_id: int,
        course_id: Optional[str]
    ) -> List[Dict]:
        """
        Resolve active features for session.

        Combines:
        - Mode feature mappings (required/optional)
        - Course-level feature overrides
        """
        # Get mode feature mappings
        mode_features = RunnerModeFeatureMapRepository.find_by_mode(mode_id)

        # Filter to required + optional (exclude excluded)
        active_features = []
        for mf in mode_features:
            if mf['relationship'] in ('required', 'optional'):
                feature = {
                    'feature_id': mf['feature_id'],
                    'feature_code': mf.get('feature_code', ''),
                    'feature_name': mf.get('feature_name', ''),
                    'relationship': mf['relationship'],
                    'config': mf.get('config', {})
                }

                # Check course-level override
                if course_id:
                    course_feature = CourseSystemFeaturesRepository.get_course_feature(
                        course_id=course_id,
                        feature_id=mf['feature_id']
                    )
                    if course_feature:
                        if not course_feature.get('is_active'):
                            continue  # Skip if disabled at course level
                        # Merge course config
                        feature['config'] = {
                            **feature['config'],
                            **course_feature.get('config', {})
                        }

                active_features.append(feature)

        return active_features

    @classmethod
    def _calculate_session_ttl(cls, mode: Dict, method_info: Dict) -> int:
        """Calculate appropriate TTL for session."""
        if mode.get('time_limited') and mode.get('graded'):
            # Exam mode: time limit + buffer
            time_limit = method_info.get('time_limit_seconds', 3600)
            return time_limit + RunnerStateManager.TTL_EXAM_BUFFER
        elif mode.get('graded'):
            # Graded but not timed: review period
            return RunnerStateManager.TTL_REVIEW
        else:
            # Standard: 24 hours
            return RunnerStateManager.TTL_STANDARD

    @classmethod
    def _build_session_response(
        cls,
        session: Dict,
        mode: Dict,
        features: List[Dict],
        state: Dict,
        method_info: Dict,
        resumed: bool,
        ttl: Optional[int] = None
    ) -> Dict:
        """Build session start/resume response."""
        return {
            'session_id': session['session_id'],
            'mode': mode['mode_code'],
            'mode_name': mode['name'],
            'features': features,
            'initial_state': state,
            'ttl_seconds': ttl or RunnerStateManager.TTL_STANDARD,
            'method_info': {
                'method_id': method_info['method_id'],
                'method_type': method_info['method_type'],
                'title': method_info.get('title', ''),
                'difficulty': method_info.get('difficulty', 'medium')
            },
            'resumed': resumed
        }

    @classmethod
    def _calculate_score(
        cls,
        final_state: Dict,
        session: Dict
    ) -> Tuple[Optional[float], Optional[bool]]:
        """
        Calculate score from final state.

        Returns:
            Tuple of (score 0-100, passed boolean)
        """
        answers = final_state.get('answers', {})
        progress = final_state.get('progress', {})

        total_items = progress.get('total_items', 0)
        if total_items == 0:
            return None, None

        # Count correct answers
        correct_count = 0
        for item_id, answer in answers.items():
            if isinstance(answer, dict) and answer.get('correct'):
                correct_count += 1
            elif answer == 'correct':  # Simple format
                correct_count += 1

        score = (correct_count / total_items) * 100.0

        # Default passing threshold is 60%
        passing_threshold = 60.0
        passed = score >= passing_threshold

        return round(score, 2), passed

    @classmethod
    def _build_session_summary(cls, final_state: Dict) -> Dict:
        """Build session completion summary."""
        answers = final_state.get('answers', {})
        progress = final_state.get('progress', {})

        total_items = progress.get('total_items', len(answers))
        completed_items = len(progress.get('completed_items', []))

        correct_count = 0
        incorrect_count = 0
        for item_id, answer in answers.items():
            if isinstance(answer, dict):
                if answer.get('correct'):
                    correct_count += 1
                else:
                    incorrect_count += 1

        return {
            'total_items': total_items,
            'completed_items': completed_items,
            'correct_count': correct_count,
            'incorrect_count': incorrect_count
        }

    @classmethod
    def _save_learning_progress(
        cls,
        user_id: str,
        method_id: str,
        score: Optional[float],
        duration_seconds: int,
        final_state: Dict
    ) -> bool:
        """Save progress via repository."""
        return LearningMethodProgressRepository.upsert_progress(
            user_id=user_id,
            method_id=method_id,
            score=score,
            duration_seconds=duration_seconds,
            state_snapshot=final_state
        )
