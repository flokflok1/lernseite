"""
LernsystemX Backend - Flask Extensions

Initialize all Flask extensions used in the application.
Extensions are initialized here and then bound to the app in the factory pattern.
"""

import os
import redis
from psycopg_pool import ConnectionPool
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail
from celery import Celery


# Database Connection Pool (psycopg)
# Will be initialized in factory with actual config
db_pool = None


def init_db_pool(database_url: str, min_size: int = 2, max_size: int = 10):
    """
    Initialize PostgreSQL connection pool

    Args:
        database_url: PostgreSQL connection string
        min_size: Minimum pool size
        max_size: Maximum pool size

    Returns:
        ConnectionPool: Configured connection pool
    """
    global db_pool
    db_pool = ConnectionPool(
        conninfo=database_url,
        min_size=min_size,
        max_size=max_size,
        timeout=30,
        max_idle=300
    )
    return db_pool


def refresh_db_pool(database_url: str = None):
    """
    Refresh database connection pool (close old connections and create new pool)

    This is needed after database schema changes (e.g., during setup wizard)
    to ensure all connections are fresh and not stale.

    Args:
        database_url: Optional new database URL (uses existing if not provided)
    """
    global db_pool

    # Close existing pool if it exists
    if db_pool is not None:
        try:
            db_pool.close()
        except Exception as e:
            print(f"Warning: Error closing old pool: {e}")

    # Reinitialize with new or existing URL
    if database_url:
        init_db_pool(database_url)
    else:
        # Use existing DATABASE_URL from environment
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            init_db_pool(database_url)
        else:
            raise ValueError("DATABASE_URL not set in environment")

# JWT Authentication
jwt = JWTManager()

# WebSocket Support
socketio = SocketIO(
    cors_allowed_origins="*",  # Will be configured in factory
    async_mode='threading',  # Using threading mode for Python 3.13 compatibility
    logger=True,
    engineio_logger=True
)

# Redis Client
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=int(os.getenv('REDIS_DB', 0)),
    decode_responses=True
)

# Celery Task Queue
celery = Celery(
    'lernsystemx',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/1'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/2')
)

# Rate Limiting
def rate_limit_key_func():
    """
    Custom key function for rate limiting.
    Returns None for OPTIONS requests to exempt them from rate limiting.
    This allows CORS preflight requests to pass through without being rate-limited.
    """
    from flask import request
    if request.method == 'OPTIONS':
        return None  # Exempt OPTIONS from rate limiting
    return get_remote_address()

limiter = Limiter(
    key_func=rate_limit_key_func,
    storage_uri=os.getenv('RATELIMIT_STORAGE_URL', 'redis://localhost:6379/4'),
    default_limits=[os.getenv('RATELIMIT_DEFAULT', '200 per hour')]
)

# Email Support
mail = Mail()


# JWT Callbacks
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    """
    Check if a JWT token has been revoked

    Args:
        jwt_header (dict): JWT header
        jwt_payload (dict): JWT payload containing user info

    Returns:
        bool: True if token is revoked, False otherwise
    """
    jti = jwt_payload['jti']
    token_in_redis = redis_client.get(f'revoked_token:{jti}')
    return token_in_redis is not None


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    """
    Handle expired token

    Args:
        jwt_header (dict): JWT header
        jwt_payload (dict): JWT payload

    Returns:
        tuple: JSON response and status code
    """
    return {
        'error': 'Token Expired',
        'message': 'The token has expired',
        'status_code': 401
    }, 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    """
    Handle invalid token

    Args:
        error (str): Error message

    Returns:
        tuple: JSON response and status code
    """
    return {
        'error': 'Invalid Token',
        'message': 'Signature verification failed',
        'status_code': 401
    }, 401


@jwt.unauthorized_loader
def missing_token_callback(error):
    """
    Handle missing token

    Args:
        error (str): Error message

    Returns:
        tuple: JSON response and status code
    """
    return {
        'error': 'Authorization Required',
        'message': 'Request does not contain an access token',
        'status_code': 401
    }, 401


@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    """
    Handle revoked token

    Args:
        jwt_header (dict): JWT header
        jwt_payload (dict): JWT payload

    Returns:
        tuple: JSON response and status code
    """
    return {
        'error': 'Token Revoked',
        'message': 'The token has been revoked',
        'status_code': 401
    }, 401


# Celery Configuration
@celery.task(bind=True)
def debug_task(self):
    """
    Debug task for testing Celery

    Returns:
        str: Request info
    """
    return f'Request: {self.request!r}'


# Redis Helper Functions
class RedisHelper:
    """Helper class for Redis operations"""

    @staticmethod
    def set_with_expiry(key, value, expiry_seconds):
        """
        Set a key with expiration time

        Args:
            key (str): Redis key
            value (str): Value to store
            expiry_seconds (int): Expiration time in seconds
        """
        redis_client.setex(key, expiry_seconds, value)

    @staticmethod
    def get(key):
        """
        Get value from Redis

        Args:
            key (str): Redis key

        Returns:
            str: Value or None
        """
        return redis_client.get(key)

    @staticmethod
    def delete(key):
        """
        Delete key from Redis

        Args:
            key (str): Redis key
        """
        redis_client.delete(key)

    @staticmethod
    def exists(key):
        """
        Check if key exists

        Args:
            key (str): Redis key

        Returns:
            bool: True if exists, False otherwise
        """
        return redis_client.exists(key)

    @staticmethod
    def increment(key, amount=1):
        """
        Increment a counter

        Args:
            key (str): Redis key
            amount (int): Amount to increment by

        Returns:
            int: New value
        """
        return redis_client.incrby(key, amount)

    @staticmethod
    def decrement(key, amount=1):
        """
        Decrement a counter

        Args:
            key (str): Redis key
            amount (int): Amount to decrement by

        Returns:
            int: New value
        """
        return redis_client.decrby(key, amount)


# Export all extensions
__all__ = [
    'db_pool',
    'init_db_pool',
    'refresh_db_pool',
    'jwt',
    'socketio',
    'celery',
    'redis_client',
    'limiter',
    'mail',
    'RedisHelper'
]
