"""
LernsystemX Runner Session Service

Business logic for runner session execution.
Runner API - Execution only, NO configuration logic.
"""

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import uuid

from app.infrastructure.persistence.repositories.runner_modes_repository import (
    RunnerModesRepository,
    RunnerModeFeatureMapRepository,
    LMTypeModeCompatibilityRepository
)
from app.infrastructure.persistence.repositories.runner_sessions_repository import (
    RunnerSessionsRepository
)
from app.infrastructure.persistence.repositories.system_features_repository import (
    CourseSystemFeaturesRepository
)
from app.infrastructure.persistence.repositories.learning_method import (
    LearningMethodInstanceRepository,
    LearningMethodProgressRepository
)
from app.infrastructure.redis.runner_state import RunnerStateManager
from app.infrastructure.i18n.error_codes import ErrorCode


class RunnerSessionService:
    """
    Service for managing runner session execution.

    Responsibilities:
    - Start/resume learning sessions
    - Manage session state (via Redis)
    - Handle session completion and scoring

    Does NOT handle:
    - Mode configuration (that's Panel API)
    - Feature configuration (that's Panel API)
    """

    # =========================================================================
    # Session Start / Resume
    # =========================================================================

    @classmethod
    def start_session(
        cls,
        user_id: str,
        method_id: str,
        mode_code: Optional[str] = None,
        resume: bool = False
    ) -> Tuple[Optional[Dict], Optional[ErrorCode]]:
        """
        Start or resume a runner session.

        Args:
            user_id: Current user ID
            method_id: Learning method instance UUID
            mode_code: Optional runner mode code (uses default if not provided)
            resume: Whether to resume existing active session

        Returns:
            Tuple of (session response, error code)

        Flow:
        1. Validate learning_method_instances.method_id exists
        2. Resolve runner mode (provided → instance default → type default → 'standard')
        3. Check lm_type_mode_compatibility
        4. Resolve active system features
        5. Create DB record (or resume existing)
        6. Initialize Redis state
        7. Return response
        """
        # Step 1: Validate method instance exists and get method info
        method_info = cls._get_method_instance(method_id)
        if not method_info:
            return None, ErrorCode.RUNNER_METHOD_NOT_FOUND

        # Check if user has access to this method
        if not cls._user_can_access_method(user_id, method_info):
            return None, ErrorCode.RUNNER_ACCESS_DENIED

        # Step 2: Resolve runner mode
        resolved_mode = cls._resolve_runner_mode(
            provided_code=mode_code,
            instance_default_mode_id=method_info.get('default_mode_id'),
            method_type=method_info['method_type']
        )

        if not resolved_mode:
            return None, ErrorCode.RUNNER_MODE_NOT_FOUND

        # Step 3: Check mode compatibility with LM type
        if not cls._check_mode_compatibility(method_info['method_type'], resolved_mode['mode_id']):
            return None, ErrorCode.RUNNER_MODE_INCOMPATIBLE

        # Step 4: Resolve active features for this session
        features = cls._resolve_session_features(
            mode_id=resolved_mode['mode_id'],
            course_id=method_info.get('course_id')
        )

        # Handle resume logic
        if resume:
            existing_session = RunnerSessionsRepository.find_active_session(
                user_id=user_id,
                method_id=method_id
            )
            if existing_session:
                # Check if Redis state still exists
                redis_state = RunnerStateManager.get_session_state(existing_session['session_id'])
                if redis_state:
                    # Use session's ACTUAL mode (not newly resolved mode)
                    session_mode = RunnerModesRepository.find_by_id(existing_session['mode_id'])
                    if not session_mode:
                        return None, ErrorCode.RUNNER_MODE_NOT_FOUND

                    # Resolve features for the session's actual mode
                    session_features = cls._resolve_session_features(
                        mode_id=existing_session['mode_id'],
                        course_id=method_info.get('course_id')
                    )

                    return cls._build_session_response(
                        session=existing_session,
                        mode=session_mode,
                        features=session_features,
                        state=redis_state,
                        method_info=method_info,
                        resumed=True
                    ), None

        # Step 5: Create new session record
        session_id = str(uuid.uuid4())
        session_data = {
            'session_id': session_id,
            'user_id': user_id,
            'method_id': method_id,
            'mode_id': resolved_mode['mode_id'],
            'course_id': method_info.get('course_id'),
            'status': 'active'
        }

        session = RunnerSessionsRepository.create_session(session_data)
        if not session:
            return None, ErrorCode.RUNNER_SESSION_CREATE_FAILED

        # Step 6: Initialize Redis state
        initial_state = RunnerStateManager.get_initial_state(resolved_mode['mode_code'])

        # Calculate TTL based on mode
        ttl = cls._calculate_session_ttl(resolved_mode, method_info)

        # Store in Redis
        RunnerStateManager.set_session_state(
            session_id=session_id,
            state=initial_state,
            ttl=ttl
        )

        # Handle exam lock if needed
        if resolved_mode.get('time_limited') and resolved_mode.get('graded'):
            time_limit = method_info.get('time_limit_seconds', 3600)
            # Use course_id if available, otherwise method_id for scope
            lock_scope = method_info.get('course_id') or method_id
            lock_acquired = RunnerStateManager.acquire_exam_lock(
                user_id=user_id,
                course_id=lock_scope,
                session_id=session_id,
                time_limit_seconds=time_limit
            )
            if not lock_acquired:
                # Another exam session is already active
                RunnerSessionsRepository.abandon_session(session_id)
                RunnerStateManager.delete_session_state(session_id)
                return None, ErrorCode.RUNNER_EXAM_LOCKED

        # Step 7: Return response
        return cls._build_session_response(
            session=session,
            mode=resolved_mode,
            features=features,
            state=initial_state,
            method_info=method_info,
            resumed=False,
            ttl=ttl
        ), None

    # =========================================================================
    # Session State Management
    # =========================================================================

    @classmethod
    def get_session_state(
        cls,
        session_id: str,
        user_id: str
    ) -> Tuple[Optional[Dict], Optional[ErrorCode]]:
        """
        Get current session state.

        Args:
            session_id: Session UUID
            user_id: Current user ID (for ownership check)

        Returns:
            Tuple of (session state, error code)
        """
        # Get session metadata from DB
        session = RunnerSessionsRepository.find_by_id(session_id)
        if not session:
            return None, ErrorCode.RUNNER_SESSION_NOT_FOUND

        # Verify ownership
        if session['user_id'] != user_id:
            return None, ErrorCode.RUNNER_ACCESS_DENIED

        # Check session status
        if session['status'] != 'active':
            return None, ErrorCode.RUNNER_SESSION_NOT_ACTIVE

        # Get state from Redis
        state = RunnerStateManager.get_session_state(session_id)
        if not state:
            # Session expired in Redis - mark as timed out with empty state
            RunnerSessionsRepository.timeout_session(session_id, final_state={})
            return None, ErrorCode.RUNNER_SESSION_EXPIRED

        # Get mode info
        mode = RunnerModesRepository.find_by_id(session['mode_id'])

        # Calculate remaining TTL
        ttl_remaining = RunnerStateManager.get_session_ttl(session_id)

        return {
            'session_id': session_id,
            'status': session['status'],
            'mode': mode['mode_code'] if mode else 'unknown',
            'mode_name': mode['name'] if mode else 'Unknown',
            'state': state,
            'ttl_remaining': ttl_remaining or 0,
            'method_info': {
                'method_id': session['method_id']
            },
            'started_at': session['started_at'].isoformat() if session.get('started_at') else None,
            'heartbeat_at': session.get('heartbeat_at', '').isoformat() if session.get('heartbeat_at') else None
        }, None

    @classmethod
    def update_session_state(
        cls,
        session_id: str,
        user_id: str,
        state: Dict[str, Any]
    ) -> Tuple[Optional[Dict], Optional[ErrorCode]]:
        """
        Update session state (autosave).

        Args:
            session_id: Session UUID
            user_id: Current user ID
            state: Full session state snapshot

        Returns:
            Tuple of (result dict, error code)
        """
        # Get session metadata
        session = RunnerSessionsRepository.find_by_id(session_id)
        if not session:
            return None, ErrorCode.RUNNER_SESSION_NOT_FOUND

        # Verify ownership
        if session['user_id'] != user_id:
            return None, ErrorCode.RUNNER_ACCESS_DENIED

        # Check session is active
        if session['status'] != 'active':
            return None, ErrorCode.RUNNER_SESSION_NOT_ACTIVE

        # Update state in Redis (preserve TTL safely)
        success = RunnerStateManager.update_session_state(
            session_id=session_id,
            state=state,
            preserve_ttl=True
        )
        if not success:
            # Session expired in Redis
            RunnerSessionsRepository.timeout_session(session_id, final_state=state)
            return None, ErrorCode.RUNNER_SESSION_EXPIRED

        # Update heartbeat in DB
        RunnerSessionsRepository.update_heartbeat(session_id)

        # Get remaining TTL for response
        current_ttl = RunnerStateManager.get_session_ttl(session_id)

        return {
            'session_id': session_id,
            'saved': True,
            'ttl_remaining': current_ttl
        }, None

    # =========================================================================
    # Session Completion
    # =========================================================================

    @classmethod
    def finish_session(
        cls,
        session_id: str,
        user_id: str,
        final_state: Dict[str, Any],
        force_submit: bool = False
    ) -> Tuple[Optional[Dict], Optional[ErrorCode]]:
        """
        Finish/submit a runner session.

        Args:
            session_id: Session UUID
            user_id: Current user ID
            final_state: Final session state snapshot
            force_submit: Force submission even if incomplete

        Returns:
            Tuple of (result dict, error code)
        """
        # Get session metadata
        session = RunnerSessionsRepository.find_by_id(session_id)
        if not session:
            return None, ErrorCode.RUNNER_SESSION_NOT_FOUND

        # Verify ownership
        if session['user_id'] != user_id:
            return None, ErrorCode.RUNNER_ACCESS_DENIED

        # Check session is active
        if session['status'] != 'active':
            return None, ErrorCode.RUNNER_SESSION_NOT_ACTIVE

        # Get mode info for grading logic
        mode = RunnerModesRepository.find_by_id(session['mode_id'])
        if not mode:
            return None, ErrorCode.RUNNER_MODE_NOT_FOUND

        # Calculate results
        score = None
        passed = None

        if mode.get('graded'):
            score, passed = cls._calculate_score(final_state, session)

        # Calculate duration
        started_at = session.get('started_at')
        duration_seconds = 0
        if started_at:
            duration_seconds = int((datetime.utcnow() - started_at).total_seconds())

        # Build summary
        summary = cls._build_session_summary(final_state)

        # Complete session in DB
        completion_data = {
            'score': score,
            'passed': passed,
            'duration_seconds': duration_seconds,
            'final_state': final_state
        }

        completed_session = RunnerSessionsRepository.complete_session(
            session_id=session_id,
            score=score,
            final_state=final_state
        )

        if not completed_session:
            return None, ErrorCode.OPERATION_FAILED

        # Save progress to learning_method_progress
        progress_saved = cls._save_learning_progress(
            user_id=user_id,
            method_id=session['method_id'],
            score=score,
            duration_seconds=duration_seconds,
            final_state=final_state
        )

        # Clean up Redis state
        RunnerStateManager.delete_session_state(session_id)

        # Release exam lock if applicable
        if mode.get('time_limited') and mode.get('graded'):
            # Use course_id if available, otherwise method_id for scope
            lock_scope = session.get('course_id') or session['method_id']
            RunnerStateManager.release_exam_lock(
                user_id=user_id,
                course_id=lock_scope
            )

        return {
            'session_id': session_id,
            'status': 'completed',
            'score': score,
            'passed': passed,
            'duration_seconds': duration_seconds,
            'summary': summary,
            'progress_saved': progress_saved
        }, None

    # =========================================================================
    # Private Helper Methods
    # =========================================================================

    @classmethod
    def _get_method_instance(cls, method_id: str) -> Optional[Dict]:
        """Get learning method instance info via repository."""
        return LearningMethodInstanceRepository.find_for_runner(method_id)

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
