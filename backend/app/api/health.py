"""
LernsystemX Health Check API

Provides health check endpoints for monitoring and load balancing.

Endpoints:
- GET /health - Basic health check
- GET /health/detailed - Detailed health check with component status

ISO 27001:2013 compliant - System monitoring
"""

import time
from datetime import datetime
from flask import jsonify
import psycopg

from app.extensions import redis_client, db_pool

# Track application start time
_app_start_time = time.time()


def check_redis() -> dict:
    """
    Check Redis connection and availability

    Returns:
        dict: Redis status with response time
    """
    try:
        start = time.time()
        redis_client.ping()
        latency_ms = round((time.time() - start) * 1000, 2)

        return {
            'status': 'healthy',
            'latency_ms': latency_ms
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e)
        }


def check_database() -> dict:
    """
    Check PostgreSQL database connection and availability

    Returns:
        dict: Database status with response time
    """
    try:
        start = time.time()
        with db_pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT 1')
                cur.fetchone()
        latency_ms = round((time.time() - start) * 1000, 2)

        return {
            'status': 'healthy',
            'latency_ms': latency_ms
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e)
        }


def get_uptime() -> dict:
    """
    Get application uptime

    Returns:
        dict: Uptime in seconds and human-readable format
    """
    uptime_seconds = int(time.time() - _app_start_time)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)

    return {
        'seconds': uptime_seconds,
        'human_readable': f"{days}d {hours}h {minutes}m {seconds}s"
    }


def health_check():
    """
    Basic health check endpoint

    Returns:
        Response with basic health status (200 OK or 503 Service Unavailable)

    Example Response (Healthy):
        {
            "status": "healthy",
            "timestamp": "2025-11-16T20:00:00Z",
            "uptime_seconds": 3600
        }

    Example Response (Unhealthy):
        {
            "status": "unhealthy",
            "timestamp": "2025-11-16T20:00:00Z",
            "uptime_seconds": 3600
        }
    """
    # Check critical components
    redis_status = check_redis()
    db_status = check_database()

    # System is healthy if both Redis and DB are healthy
    is_healthy = (
        redis_status['status'] == 'healthy' and
        db_status['status'] == 'healthy'
    )

    status_code = 200 if is_healthy else 503

    uptime = get_uptime()

    response = {
        'status': 'healthy' if is_healthy else 'unhealthy',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'uptime_seconds': uptime['seconds']
    }

    return jsonify(response), status_code


def health_check_detailed():
    """
    Detailed health check endpoint

    Returns:
        Response with detailed component status

    Example Response:
        {
            "status": "healthy",
            "timestamp": "2025-11-16T20:00:00Z",
            "uptime": {
                "seconds": 3600,
                "human_readable": "0d 1h 0m 0s"
            },
            "components": {
                "redis": {
                    "status": "healthy",
                    "latency_ms": 1.23
                },
                "database": {
                    "status": "healthy",
                    "latency_ms": 5.67
                }
            },
            "version": "1.0.0",
            "environment": "production"
        }
    """
    # Check all components
    redis_status = check_redis()
    db_status = check_database()

    # Overall health
    is_healthy = (
        redis_status['status'] == 'healthy' and
        db_status['status'] == 'healthy'
    )

    status_code = 200 if is_healthy else 503

    uptime = get_uptime()

    # Get version from environment or config
    import os
    version = os.getenv('LSX_VERSION', '1.0.0')
    environment = os.getenv('FLASK_ENV', os.getenv('LSX_ENV', 'development'))

    response = {
        'status': 'healthy' if is_healthy else 'unhealthy',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'uptime': uptime,
        'components': {
            'redis': redis_status,
            'database': db_status
        },
        'version': version,
        'environment': environment
    }

    return jsonify(response), status_code


def readiness_check():
    """
    Readiness check for Kubernetes/load balancers

    Checks if the application is ready to serve traffic.
    Returns 200 if ready, 503 if not ready.
    """
    # Check if critical dependencies are available
    redis_status = check_redis()
    db_status = check_database()

    is_ready = (
        redis_status['status'] == 'healthy' and
        db_status['status'] == 'healthy'
    )

    if is_ready:
        return jsonify({'status': 'ready'}), 200
    else:
        return jsonify({'status': 'not_ready'}), 503


def liveness_check():
    """
    Liveness check for Kubernetes

    Checks if the application is alive (not deadlocked).
    Returns 200 if alive, 503 if dead.
    """
    # Simple check - just return OK if the endpoint responds
    # Can be extended with deadlock detection if needed
    return jsonify({'status': 'alive'}), 200
