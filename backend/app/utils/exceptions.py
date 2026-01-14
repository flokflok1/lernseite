"""
Custom exception classes for REST API responses.

These exceptions are caught by Flask error handlers and converted to
appropriate HTTP status codes and JSON error responses.
"""


class APIException(Exception):
    """Base exception for REST API errors."""

    status_code = 500
    error_code = "INTERNAL_ERROR"

    def __init__(self, message: str, error_code: str = None, status_code: int = None):
        self.message = message
        if error_code:
            self.error_code = error_code
        if status_code:
            self.status_code = status_code
        super().__init__(self.message)

    def to_dict(self):
        """Convert to JSON-serializable dictionary."""
        return {
            'error': {
                'code': self.error_code,
                'message': self.message
            }
        }


class NotFoundError(APIException):
    """Resource not found error (404)."""

    status_code = 404
    error_code = "NOT_FOUND"


class ValidationError(APIException):
    """Validation error (400)."""

    status_code = 400
    error_code = "VALIDATION_ERROR"


class UnauthorizedError(APIException):
    """Authentication error (401)."""

    status_code = 401
    error_code = "UNAUTHORIZED"


class ForbiddenError(APIException):
    """Authorization error (403)."""

    status_code = 403
    error_code = "FORBIDDEN"


class ConflictError(APIException):
    """Conflict error (409)."""

    status_code = 409
    error_code = "CONFLICT"
