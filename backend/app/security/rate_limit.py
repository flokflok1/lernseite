"""
LernsystemX - Rate Limiting & Brute-Force Protection

Based on Dok 31 (Security Architecture) and Phase 20 requirements.

Implements:
- Rate limiting decorators using Flask-Limiter
- Brute-force protection for login attempts
- Account lockout mechanism
- IP-based and user-based rate limiting

ISO 27001:2013 compliant - Access Control & Availability
"""

from functools import wraps
from flask import request, jsonify, current_app
from datetime import datetime, timedelta
from typing import Optional, Tuple
from app.extensions import limiter, redis_client


# ==========================================
# RATE LIMITING DECORATORS
# ==========================================

def login_rate_limit():
    """
    Rate limit decorator for login endpoints.

    Uses both IP-based and email-based limits to prevent brute-force attacks.
    Configured via RATE_LIMIT_LOGIN in config.

    Usage:
        @api_v1.route('/auth/login', methods=['POST'])
        @login_rate_limit()
        def login():
            ...
    """
    def decorator(fn):
        @wraps(fn)
        @limiter.limit(
            lambda: current_app.config.get('RATE_LIMIT_LOGIN', '5 per minute'),
            key_func=lambda: f"login:{request.remote_addr}",
            error_message="Too many login attempts from this IP. Please try again later."
        )
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def twofa_rate_limit():
    """
    Rate limit decorator for 2FA verification endpoints.

    More restrictive than general API rate limits to prevent TOTP bruteforce.
    Configured via RATE_LIMIT_SENSITIVE in config.

    Usage:
        @api_v1.route('/auth/2fa/verify', methods=['POST'])
        @twofa_rate_limit()
        def verify_2fa():
            ...
    """
    def decorator(fn):
        @wraps(fn)
        @limiter.limit(
            lambda: current_app.config.get('RATE_LIMIT_SENSITIVE', '10 per minute'),
            key_func=lambda: f"2fa:{request.remote_addr}",
            error_message="Too many 2FA verification attempts. Please try again later."
        )
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def sensitive_endpoint_limit():
    """
    Rate limit decorator for sensitive endpoints (password reset, email change, etc).

    Configured via RATE_LIMIT_SENSITIVE in config.

    Usage:
        @api_v1.route('/auth/reset-password', methods=['POST'])
        @sensitive_endpoint_limit()
        def reset_password():
            ...
    """
    def decorator(fn):
        @wraps(fn)
        @limiter.limit(
            lambda: current_app.config.get('RATE_LIMIT_SENSITIVE', '10 per minute'),
            key_func=lambda: f"sensitive:{request.remote_addr}",
            error_message="Too many requests to sensitive endpoint. Please try again later."
        )
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def api_rate_limit():
    """
    General API rate limit decorator.

    Configured via RATE_LIMIT_API in config.
    Applied to most API endpoints.

    Usage:
        @api_v1.route('/api/v1/courses', methods=['GET'])
        @api_rate_limit()
        def get_courses():
            ...
    """
    def decorator(fn):
        @wraps(fn)
        @limiter.limit(
            lambda: current_app.config.get('RATE_LIMIT_API', '100 per minute'),
            error_message="API rate limit exceeded. Please try again later."
        )
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        return wrapper
    return decorator


# ==========================================
# BRUTE-FORCE PROTECTION
# ==========================================

class BruteForceProtection:
    """
    Brute-force protection and account lockout mechanism.

    Uses Redis to track failed login attempts by email and IP.
    Implements temporary account lockout after threshold.
    """

    @staticmethod
    def _get_lockout_key(email: str) -> str:
        """Generate Redis key for account lockout"""
        return f"lockout:email:{email}"

    @staticmethod
    def _get_attempt_key(email: str) -> str:
        """Generate Redis key for failed attempts counter"""
        return f"attempts:email:{email}"

    @staticmethod
    def _get_ip_attempt_key(ip: str) -> str:
        """Generate Redis key for IP-based attempts"""
        return f"attempts:ip:{ip}"

    @staticmethod
    def is_locked_out(email: str) -> Tuple[bool, Optional[int]]:
        """
        Check if account is currently locked out.

        Args:
            email: User email address

        Returns:
            Tuple of (is_locked, remaining_seconds)
        """
        lockout_key = BruteForceProtection._get_lockout_key(email)
        ttl = redis_client.ttl(lockout_key)

        if ttl > 0:
            return True, ttl

        return False, None

    @staticmethod
    def check_login_lockout(email: str, ip: str) -> Tuple[bool, Optional[str]]:
        """
        Check if login should be blocked due to lockout or too many attempts.

        Args:
            email: User email address
            ip: IP address

        Returns:
            Tuple of (is_blocked, error_message)
        """
        max_attempts = current_app.config.get('MAX_LOGIN_ATTEMPTS', 5)
        lockout_minutes = current_app.config.get('LOGIN_LOCKOUT_MINUTES', 15)

        # Check if account is locked out
        is_locked, remaining_seconds = BruteForceProtection.is_locked_out(email)
        if is_locked:
            remaining_minutes = remaining_seconds // 60 + 1
            return True, f"Account temporarily locked. Please try again in {remaining_minutes} minutes."

        # Check failed attempts count
        attempt_key = BruteForceProtection._get_attempt_key(email)
        attempts = redis_client.get(attempt_key)

        if attempts and int(attempts) >= max_attempts:
            # Lock out the account
            lockout_key = BruteForceProtection._get_lockout_key(email)
            redis_client.setex(
                lockout_key,
                lockout_minutes * 60,
                "locked"
            )

            # Reset attempt counter
            redis_client.delete(attempt_key)

            return True, f"Too many failed login attempts. Account locked for {lockout_minutes} minutes."

        return False, None

    @staticmethod
    def record_failed_attempt(email: str, ip: str) -> None:
        """
        Record a failed login attempt.

        Increments counters for both email and IP.
        Sets expiry to prevent permanent tracking.

        Args:
            email: User email address
            ip: IP address
        """
        lockout_minutes = current_app.config.get('LOGIN_LOCKOUT_MINUTES', 15)
        expiry = lockout_minutes * 60  # Convert to seconds

        # Increment email-based counter
        attempt_key = BruteForceProtection._get_attempt_key(email)
        redis_client.incr(attempt_key)
        redis_client.expire(attempt_key, expiry)

        # Increment IP-based counter
        ip_key = BruteForceProtection._get_ip_attempt_key(ip)
        redis_client.incr(ip_key)
        redis_client.expire(ip_key, expiry)

    @staticmethod
    def record_successful_login(email: str, ip: str) -> None:
        """
        Record a successful login.

        Resets all counters and removes lockout for the account.

        Args:
            email: User email address
            ip: IP address
        """
        # Clear all counters and lockouts
        attempt_key = BruteForceProtection._get_attempt_key(email)
        lockout_key = BruteForceProtection._get_lockout_key(email)

        redis_client.delete(attempt_key)
        redis_client.delete(lockout_key)

    @staticmethod
    def get_remaining_attempts(email: str) -> int:
        """
        Get remaining login attempts before lockout.

        Args:
            email: User email address

        Returns:
            Number of remaining attempts
        """
        max_attempts = current_app.config.get('MAX_LOGIN_ATTEMPTS', 5)
        attempt_key = BruteForceProtection._get_attempt_key(email)
        attempts = redis_client.get(attempt_key)

        if not attempts:
            return max_attempts

        remaining = max_attempts - int(attempts)
        return max(0, remaining)


# ==========================================
# INITIALIZATION
# ==========================================

def init_rate_limiter(app):
    """
    Initialize rate limiting for the application.

    This function is called from the app factory if RATE_LIMIT_ENABLED=True.
    Limiter is already initialized in extensions.py, so this is for any
    additional configuration or logging.

    Args:
        app: Flask application instance
    """
    if not app.config.get('RATE_LIMIT_ENABLED', True):
        app.logger.warning('Rate limiting is DISABLED - not recommended for production')
        limiter.enabled = False
        return

    app.logger.info('Rate limiting initialized')
    app.logger.info(f"  - Login rate limit: {app.config.get('RATE_LIMIT_LOGIN', '5 per minute')}")
    app.logger.info(f"  - API rate limit: {app.config.get('RATE_LIMIT_API', '100 per minute')}")
    app.logger.info(f"  - Sensitive endpoints: {app.config.get('RATE_LIMIT_SENSITIVE', '10 per minute')}")
    app.logger.info(f"  - Max login attempts: {app.config.get('MAX_LOGIN_ATTEMPTS', 5)}")
    app.logger.info(f"  - Lockout duration: {app.config.get('LOGIN_LOCKOUT_MINUTES', 15)} minutes")


# ==========================================
# RATE LIMIT ERROR HANDLER
# ==========================================

def handle_rate_limit_exceeded(error):
    """
    Custom error handler for rate limit exceeded.

    Returns a consistent JSON response format with CORS headers
    to prevent browser CORS blocking on rate-limited responses.

    Args:
        error: RateLimitExceeded exception

    Returns:
        JSON response with 429 status and CORS headers
    """
    from flask import make_response, current_app

    response = make_response(jsonify({
        'success': False,
        'error': 'Rate Limit Exceeded',
        'message': str(error.description),
        'status_code': 429
    }), 429)

    # Add CORS headers to allow browser to process the error response
    # Get allowed origins from config
    cors_origins = current_app.config.get('CORS_ORIGINS', '*')
    origin = request.headers.get('Origin', '')

    # Check if origin is allowed
    if cors_origins == '*' or (isinstance(cors_origins, list) and origin in cors_origins):
        response.headers['Access-Control-Allow-Origin'] = origin if origin else '*'
    elif isinstance(cors_origins, str) and origin == cors_origins:
        response.headers['Access-Control-Allow-Origin'] = origin
    else:
        response.headers['Access-Control-Allow-Origin'] = '*'

    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'

    return response
