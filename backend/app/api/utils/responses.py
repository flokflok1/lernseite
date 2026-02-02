"""
LernsystemX API Response Utilities

Standardized response formatting for API endpoints.
Re-exports from error_codes module with additional convenience wrappers.
"""

from typing import Any, Dict, List, Optional, Union
from flask import jsonify

from app.infrastructure.i18n.error_codes import (
    ErrorCode,
    error_response as _error_response,
    success_response as _success_response
)


def success_response(
    data: Optional[Union[Dict, List]] = None,
    meta: Optional[Dict] = None,
    status_code: int = 200
):
    """
    Create a standardized success response with optional meta field.

    Args:
        data: Response data (dict or list)
        meta: Optional metadata (pagination, totals, etc.)
        status_code: HTTP status code (default: 200)

    Returns:
        Tuple of (Flask Response, status code)
    """
    if meta is not None:
        # Use custom response with meta
        response = {'success': True}
        if data is not None:
            response['data'] = data
        response['meta'] = meta
        return jsonify(response), status_code

    # Use standard response
    return _success_response(data=data, status=status_code)


def error_response(
    error_code: ErrorCode,
    details: Optional[Union[Dict, List]] = None,
    field: Optional[str] = None
):
    """
    Create a standardized error response.

    Args:
        error_code: ErrorCode enum value
        details: Optional error details (validation errors, etc.)
        field: Optional field name for validation errors

    Returns:
        Tuple of (Flask Response, status code)
    """
    # Map ErrorCode to HTTP status codes
    status_codes = {
        ErrorCode.NOT_FOUND: 404,
        ErrorCode.VALIDATION_ERROR: 400,
        ErrorCode.FORBIDDEN: 403,
        ErrorCode.UNAUTHORIZED: 401,
        ErrorCode.CONFLICT: 409,
        ErrorCode.GONE: 410,
        ErrorCode.OPERATION_FAILED: 500,
        ErrorCode.INTERNAL_ERROR: 500,
        ErrorCode.BAD_REQUEST: 400,
        # Runner-specific
        ErrorCode.RUNNER_SESSION_NOT_FOUND: 404,
        ErrorCode.RUNNER_SESSION_EXPIRED: 410,
        ErrorCode.RUNNER_SESSION_NOT_ACTIVE: 400,
        ErrorCode.RUNNER_MODE_NOT_FOUND: 404,
        ErrorCode.RUNNER_MODE_INCOMPATIBLE: 400,
        ErrorCode.RUNNER_METHOD_NOT_FOUND: 404,
        ErrorCode.RUNNER_ACCESS_DENIED: 403,
        ErrorCode.RUNNER_EXAM_LOCKED: 409,
    }

    status_code = status_codes.get(error_code, 400)

    return _error_response(
        code=error_code,
        status=status_code,
        details=details,
        field=field
    )
