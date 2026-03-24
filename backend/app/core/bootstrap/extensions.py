"""
LernsystemX Backend - Flask Extensions

Initialize all Flask extensions used in the application.
Extensions are initialized here and then bound to the app in the factory pattern.
"""

import os
import atexit
import logging
from pathlib import Path
import redis
from dotenv import load_dotenv

# Load app/.env explicitly (the canonical config location)
_env_file = Path(__file__).parents[2] / '.env'
load_dotenv(dotenv_path=_env_file)
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
    Initialize PostgreSQL connection pool (idempotent).

    Args:
        database_url: PostgreSQL connection string
        min_size: Minimum pool size
        max_size: Maximum pool size

    Returns:
        ConnectionPool: Configured connection pool
    """
    global db_pool
    if db_pool is not None:
        return db_pool
    db_pool = ConnectionPool(
        conninfo=database_url,
        min_size=min_size,
        max_size=max_size,
        timeout=30,
        max_idle=300
    )
    atexit.register(close_db_pool)
    return db_pool


def close_db_pool() -> None:
    """
    Close the database connection pool safely.

    Safe to call multiple times or when db_pool is None.
    Registered via atexit for CLI one-shots, and via
    app.teardown_appcontext for Flask request lifecycle.
    """
    global db_pool
    if db_pool is None:
        return
    try:
        db_pool.close()
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.warning("Error closing db_pool: %s", e)
    finally:
        db_pool = None


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
        try:
            init_db_pool(database_url)
        except Exception as e:
            print(f"Warning: Could not initialize DB pool (normal during setup): {e}")
            db_pool = None
    else:
        # Use existing DATABASE_URL from environment
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            try:
                init_db_pool(database_url)
            except Exception as e:
                print(f"Warning: Could not initialize DB pool (normal during setup): {e}")
                db_pool = None
        else:
            print("Warning: DATABASE_URL not set - DB pool will be initialized later")
            db_pool = None

# JWT Authentication
jwt = JWTManager()

# WebSocket Support
socketio = SocketIO(
    cors_allowed_origins="*",  # Will be configured in factory
    async_mode='threading',  # Using threading mode for Python 3.13 compatibility
    logger=True,
    engineio_logger=True
)

# Redis Client (lazy initialization - will be None during setup)
try:
    redis_client = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        db=int(os.getenv('REDIS_DB', 0)),
        decode_responses=True,
        socket_connect_timeout=2  # Fast fail if Redis not available
    )
    # Test connection
    redis_client.ping()
except Exception as e:
    print(f"Warning: Redis not available (normal during setup): {e}")
    redis_client = None

# Celery Task Queue
celery = Celery(
    'lernsystemx',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/1'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/2'),
    include=[
        'app.infrastructure.tasks.course_generation_tasks',
        'app.infrastructure.tasks.exam_tasks',
        'app.infrastructure.tasks.exam_archive_tasks',
        'app.infrastructure.tasks.crawl_tasks',
    ],
)

# Initialize Flask app context in Celery worker processes so tasks
# have access to db_pool, redis, and other extensions.
from celery.signals import worker_process_init

@worker_process_init.connect
def _init_celery_worker(**kwargs):
    """Bootstrap Flask app when a Celery worker process starts.

    After fork, the parent's db_pool has stale connections that are
    not safe to use. We must close the inherited pool and let
    create_app() build a fresh one.
    """
    global db_pool
    if db_pool is not None:
        try:
            db_pool.close()
        except Exception:
            pass
        db_pool = None

    from app import create_app
    app = create_app()
    app.app_context().push()

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

# Dummy limiter class for setup mode (when Redis not available)
class DummyLimiter:
    """No-op limiter for setup mode"""
    def limit(self, *args, **kwargs):
        def decorator(f):
            return f
        return decorator

    def exempt(self, f):
        """No-op exempt decorator"""
        return f

    def init_app(self, app):
        pass

    def reset(self):
        """No-op reset"""
        pass

# Rate limiter (optional - Dummy during setup without Redis)
# IMPORTANT: Only create real limiter if Redis is actually connected
if redis_client is not None:
    try:
        ratelimit_storage = os.getenv('RATELIMIT_STORAGE_URL')
        if not ratelimit_storage:
            redis_host = os.getenv('REDIS_HOST', 'localhost')
            redis_port = os.getenv('REDIS_PORT', '6379')
            ratelimit_storage = f'redis://{redis_host}:{redis_port}/4'

        limiter = Limiter(
            key_func=rate_limit_key_func,
            storage_uri=ratelimit_storage,
            default_limits=[os.getenv('RATELIMIT_DEFAULT', '1000 per hour')]
        )
    except Exception as e:
        print(f"Warning: Rate limiter not available (normal during setup): {e}")
        limiter = DummyLimiter()
else:
    print("Warning: Redis not available - using DummyLimiter (normal during setup)")
    limiter = DummyLimiter()

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
    # If Redis not available (during setup), allow all tokens
    if redis_client is None:
        return False

    jti = jwt_payload['jti']
    try:
        token_in_redis = redis_client.get(f'revoked_token:{jti}')
        return token_in_redis is not None
    except Exception:
        # Redis connection failed, allow token to continue
        return False


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
    'close_db_pool',
    'refresh_db_pool',
    'jwt',
    'socketio',
    'celery',
    'redis_client',
    'limiter',
    'mail',
    'RedisHelper'
]
