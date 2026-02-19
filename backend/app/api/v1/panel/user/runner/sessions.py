"""
LernsystemX Runner API - Sessions

Execution endpoints for runner sessions.
Runner API - Execution ONLY, NO configuration logic.
"""

from flask import Blueprint, request, jsonify, g
from pydantic import ValidationError

from app.application.services.content.runner import RunnerSessionService
from app.domain.models.runner.sessions import (
    SessionStartRequest,
    SessionStateUpdate,
    SessionFinishRequest
)
from app.api.middleware.auth import token_required, permission_required
from app.infrastructure.i18n.error_codes import ErrorCode
from app.api.responses.responses import success_response, error_response

bp = Blueprint('runner_sessions', __name__, url_prefix='/runner/sessions')


# =============================================================================
# Session Lifecycle
# =============================================================================

@bp.route('', methods=['POST'])
@token_required
@permission_required('runner.sessions.execute')
def start_session():
    """
    POST /api/v1/runner/sessions

    Start or resume a runner session.

    Request Body:
        method_id: str - Learning method instance UUID (required)
        mode_code: str - Runner mode code (optional, uses default if not provided)
        resume: bool - Whether to resume existing active session (default: false)

    Flow:
        1. Validate learning_method_instances.method_id exists
        2. Resolve runner mode (provided → instance default → type default → 'standard')
        3. Check lm_type_mode_compatibility
        4. Resolve active system features
        5. Create DB record (or resume existing)
        6. Initialize Redis state
        7. Return response

    Returns:
        201: SessionStartResponse
            - session_id: str
            - mode: str
            - mode_name: str
            - features: Feature[]
            - initial_state: object
            - ttl_seconds: int
            - method_info: object
            - resumed: bool
        400: Validation error
        403: No access to method
        404: Method not found
    """
    try:
        data = SessionStartRequest(**request.get_json())
    except ValidationError as e:
        return error_response(ErrorCode.VALIDATION_ERROR, details=e.errors())

    result, error = RunnerSessionService.start_session(
        user_id=g.current_user.id,
        method_id=data.method_id,
        mode_code=data.mode_code,
        resume=data.resume
    )

    if error:
        return error_response(error)

    return success_response(data=result, status_code=201)


@bp.route('/<string:session_id>', methods=['GET'])
@token_required
@permission_required('runner.sessions.read')
def get_session_state(session_id: str):
    """
    GET /api/v1/runner/sessions/{session_id}

    Get current session state.

    Path Parameters:
        session_id: str - Session UUID

    Returns:
        200: SessionStateResponse
            - session_id: str
            - status: str
            - mode: str
            - mode_name: str
            - state: object (current state from Redis)
            - ttl_remaining: int
            - method_info: object
            - started_at: datetime
            - heartbeat_at: datetime
        403: Not session owner
        404: Session not found
        410: Session expired (Redis state gone)
    """
    result, error = RunnerSessionService.get_session_state(
        session_id=session_id,
        user_id=g.current_user.id
    )

    if error:
        return error_response(error)

    return success_response(data=result)


@bp.route('/<string:session_id>/state', methods=['PATCH'])
@token_required
@permission_required('runner.sessions.execute')
def update_session_state(session_id: str):
    """
    PATCH /api/v1/runner/sessions/{session_id}/state

    Update session state (autosave).

    Path Parameters:
        session_id: str - Session UUID

    Request Body:
        state: object - Full session state snapshot (not diff)

    Note:
        - State is stored in Redis with existing TTL preserved
        - Updates heartbeat timestamp in DB

    Returns:
        200: {session_id, saved: true, ttl_remaining: int}
        403: Not session owner
        404: Session not found
        410: Session expired
    """
    try:
        data = SessionStateUpdate(**request.get_json())
    except ValidationError as e:
        return error_response(ErrorCode.VALIDATION_ERROR, details=e.errors())

    result, error = RunnerSessionService.update_session_state(
        session_id=session_id,
        user_id=g.current_user.id,
        state=data.state
    )

    if error:
        return error_response(error)

    return success_response(data=result)


@bp.route('/<string:session_id>/finish', methods=['POST'])
@token_required
@permission_required('runner.sessions.execute')
def finish_session(session_id: str):
    """
    POST /api/v1/runner/sessions/{session_id}/finish

    Finish/submit a runner session.

    Path Parameters:
        session_id: str - Session UUID

    Request Body:
        final_state: object - Final session state snapshot
        force_submit: bool - Force submission even if incomplete (default: false)

    Flow:
        1. Validate session ownership and status
        2. Calculate score (if graded mode)
        3. Save completion data to DB
        4. Save progress to learning_method_progress
        5. Clean up Redis state
        6. Release exam lock (if applicable)

    Returns:
        200: SessionFinishResponse
            - session_id: str
            - status: 'completed'
            - score: float (0-100, if graded)
            - passed: bool (if graded)
            - duration_seconds: int
            - summary: object
            - progress_saved: bool
        403: Not session owner
        404: Session not found
        400: Session not active
    """
    try:
        data = SessionFinishRequest(**request.get_json())
    except ValidationError as e:
        return error_response(ErrorCode.VALIDATION_ERROR, details=e.errors())

    result, error = RunnerSessionService.finish_session(
        session_id=session_id,
        user_id=g.current_user.id,
        final_state=data.final_state,
        force_submit=data.force_submit
    )

    if error:
        return error_response(error)

    return success_response(data=result)
