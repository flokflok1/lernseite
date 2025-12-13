"""
LernsystemX - Prometheus Metrics Module

Defines application metrics for monitoring with Prometheus.
Metrics cover HTTP requests, business operations, and infrastructure.

Based on Dok 30 (30_Monitoring-Alerting.md)
"""

from prometheus_client import Counter, Histogram, Gauge, Info
from typing import Optional


# ==========================================
# HTTP REQUEST METRICS
# ==========================================

# Total HTTP requests counter
http_requests_total = Counter(
    'lsx_http_requests_total',
    'Total HTTP requests received',
    ['method', 'endpoint', 'status_code']
)

# HTTP request duration histogram
http_request_duration_seconds = Histogram(
    'lsx_http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint'],
    buckets=[.005, .01, .025, .05, .1, .25, .5, 1, 2.5, 5, 10]
)

# HTTP errors by type
http_errors_total = Counter(
    'lsx_http_errors_total',
    'Total HTTP errors',
    ['method', 'endpoint', 'error_type']
)


# ==========================================
# BUSINESS METRICS - ANALYTICS
# ==========================================

# Analytics events tracked
analytics_events_total = Counter(
    'lsx_analytics_events_total',
    'Total analytics events tracked',
    ['event_type', 'user_type']
)

# Active users gauge
analytics_active_users = Gauge(
    'lsx_analytics_active_users',
    'Number of currently active users',
    ['user_type']
)


# ==========================================
# BUSINESS METRICS - AI OPERATIONS
# ==========================================

# AI method calls
ai_method_calls_total = Counter(
    'lsx_ai_method_calls_total',
    'Total AI learning method calls',
    ['method_name', 'provider']
)

# AI method duration
ai_method_duration_seconds = Histogram(
    'lsx_ai_method_duration_seconds',
    'AI method call duration in seconds',
    ['method_name', 'provider'],
    buckets=[.1, .25, .5, 1, 2.5, 5, 10, 30, 60]
)

# AI tokens consumed
ai_tokens_consumed_total = Counter(
    'lsx_ai_tokens_consumed_total',
    'Total AI tokens consumed',
    ['provider', 'model']
)

# AI costs in EUR
ai_cost_eur_total = Counter(
    'lsx_ai_cost_eur_total',
    'Total AI costs in EUR',
    ['provider', 'model']
)

# AI errors
ai_errors_total = Counter(
    'lsx_ai_errors_total',
    'Total AI operation errors',
    ['provider', 'error_type']
)


# ==========================================
# BUSINESS METRICS - CACHE
# ==========================================

# Cache hits/misses
cache_operations_total = Counter(
    'lsx_cache_operations_total',
    'Total cache operations',
    ['operation', 'result']  # operation: get/set/delete, result: hit/miss/success/error
)

# Cache hit ratio (calculated via PromQL)
cache_hit_ratio = Gauge(
    'lsx_cache_hit_ratio',
    'Cache hit ratio (0-1)',
    []
)

# Cache size
cache_size_bytes = Gauge(
    'lsx_cache_size_bytes',
    'Current cache size in bytes',
    []
)


# ==========================================
# DATABASE METRICS
# ==========================================

# Database connections
db_connections_active = Gauge(
    'lsx_db_connections_active',
    'Number of active database connections',
    []
)

db_connections_idle = Gauge(
    'lsx_db_connections_idle',
    'Number of idle database connections',
    []
)

# Database query duration
db_query_duration_seconds = Histogram(
    'lsx_db_query_duration_seconds',
    'Database query duration in seconds',
    ['operation'],  # operation: select/insert/update/delete
    buckets=[.001, .005, .01, .025, .05, .1, .25, .5, 1, 2.5]
)

# Database errors
db_errors_total = Counter(
    'lsx_db_errors_total',
    'Total database errors',
    ['error_type']
)


# ==========================================
# REDIS METRICS
# ==========================================

# Redis operations
redis_operations_total = Counter(
    'lsx_redis_operations_total',
    'Total Redis operations',
    ['operation', 'result']
)

# Redis operation duration
redis_operation_duration_seconds = Histogram(
    'lsx_redis_operation_duration_seconds',
    'Redis operation duration in seconds',
    ['operation'],
    buckets=[.001, .005, .01, .025, .05, .1, .25, .5]
)


# ==========================================
# CELERY/WORKER METRICS
# ==========================================

# Celery tasks
celery_tasks_total = Counter(
    'lsx_celery_tasks_total',
    'Total Celery tasks',
    ['task_name', 'status']  # status: success/failure/retry
)

# Celery task duration
celery_task_duration_seconds = Histogram(
    'lsx_celery_task_duration_seconds',
    'Celery task duration in seconds',
    ['task_name'],
    buckets=[.1, .5, 1, 5, 10, 30, 60, 120, 300]
)

# Celery queue length
celery_queue_length = Gauge(
    'lsx_celery_queue_length',
    'Number of tasks waiting in queue',
    ['queue_name']
)


# ==========================================
# APPLICATION INFO
# ==========================================

# Application info (static labels)
app_info = Info(
    'lsx_app',
    'LernsystemX application information'
)


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def record_http_request(method: str, endpoint: str, status_code: int, duration: float):
    """
    Record an HTTP request with all relevant metrics.

    Args:
        method: HTTP method (GET, POST, etc.)
        endpoint: Endpoint path (e.g., /api/courses)
        status_code: HTTP status code
        duration: Request duration in seconds
    """
    http_requests_total.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
    http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)

    # Track errors
    if status_code >= 400:
        error_type = 'client_error' if status_code < 500 else 'server_error'
        http_errors_total.labels(method=method, endpoint=endpoint, error_type=error_type).inc()


def record_ai_call(method_name: str, provider: str, duration: float, tokens: int,
                   cost: float, success: bool = True, error_type: Optional[str] = None):
    """
    Record an AI method call with all relevant metrics.

    Args:
        method_name: Name of the learning method (e.g., flashcard_generation)
        provider: AI provider (anthropic/openai)
        duration: Call duration in seconds
        tokens: Number of tokens consumed
        cost: Cost in EUR
        success: Whether the call succeeded
        error_type: Type of error if failed
    """
    ai_method_calls_total.labels(method_name=method_name, provider=provider).inc()
    ai_method_duration_seconds.labels(method_name=method_name, provider=provider).observe(duration)

    if success:
        ai_tokens_consumed_total.labels(provider=provider, model='auto').inc(tokens)
        ai_cost_eur_total.labels(provider=provider, model='auto').inc(cost)
    else:
        ai_errors_total.labels(provider=provider, error_type=error_type or 'unknown').inc()


def record_cache_operation(operation: str, result: str):
    """
    Record a cache operation.

    Args:
        operation: Operation type (get/set/delete)
        result: Operation result (hit/miss/success/error)
    """
    cache_operations_total.labels(operation=operation, result=result).inc()


def record_db_query(operation: str, duration: float, success: bool = True,
                    error_type: Optional[str] = None):
    """
    Record a database query.

    Args:
        operation: Query operation (select/insert/update/delete)
        duration: Query duration in seconds
        success: Whether the query succeeded
        error_type: Type of error if failed
    """
    db_query_duration_seconds.labels(operation=operation).observe(duration)

    if not success:
        db_errors_total.labels(error_type=error_type or 'unknown').inc()


def record_analytics_event(event_type: str, user_type: str):
    """
    Record an analytics event.

    Args:
        event_type: Type of event (page_view/button_click/etc)
        user_type: User type (free/premium/pro)
    """
    analytics_events_total.labels(event_type=event_type, user_type=user_type).inc()


def record_celery_task(task_name: str, status: str, duration: Optional[float] = None):
    """
    Record a Celery task execution.

    Args:
        task_name: Name of the task
        status: Task status (success/failure/retry)
        duration: Task duration in seconds (if completed)
    """
    celery_tasks_total.labels(task_name=task_name, status=status).inc()

    if duration is not None:
        celery_task_duration_seconds.labels(task_name=task_name).observe(duration)


def initialize_app_info(version: str, environment: str, python_version: str):
    """
    Initialize application info metric with static labels.

    Args:
        version: Application version
        environment: Environment (development/production)
        python_version: Python version
    """
    app_info.info({
        'version': version,
        'environment': environment,
        'python_version': python_version
    })
