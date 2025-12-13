"""
LernsystemX - Monitoring Module

Provides Prometheus metrics and monitoring capabilities.
"""

from .metrics import (
    # HTTP Metrics
    http_requests_total,
    http_request_duration_seconds,
    http_errors_total,
    # Analytics Metrics
    analytics_events_total,
    analytics_active_users,
    # AI Metrics
    ai_method_calls_total,
    ai_method_duration_seconds,
    ai_tokens_consumed_total,
    ai_cost_eur_total,
    ai_errors_total,
    # Cache Metrics
    cache_operations_total,
    cache_hit_ratio,
    cache_size_bytes,
    # Database Metrics
    db_connections_active,
    db_connections_idle,
    db_query_duration_seconds,
    db_errors_total,
    # Redis Metrics
    redis_operations_total,
    redis_operation_duration_seconds,
    # Celery Metrics
    celery_tasks_total,
    celery_task_duration_seconds,
    celery_queue_length,
    # App Info
    app_info,
    # Helper Functions
    record_http_request,
    record_ai_call,
    record_cache_operation,
    record_db_query,
    record_analytics_event,
    record_celery_task,
    initialize_app_info,
)

__all__ = [
    # HTTP Metrics
    'http_requests_total',
    'http_request_duration_seconds',
    'http_errors_total',
    # Analytics Metrics
    'analytics_events_total',
    'analytics_active_users',
    # AI Metrics
    'ai_method_calls_total',
    'ai_method_duration_seconds',
    'ai_tokens_consumed_total',
    'ai_cost_eur_total',
    'ai_errors_total',
    # Cache Metrics
    'cache_operations_total',
    'cache_hit_ratio',
    'cache_size_bytes',
    # Database Metrics
    'db_connections_active',
    'db_connections_idle',
    'db_query_duration_seconds',
    'db_errors_total',
    # Redis Metrics
    'redis_operations_total',
    'redis_operation_duration_seconds',
    # Celery Metrics
    'celery_tasks_total',
    'celery_task_duration_seconds',
    'celery_queue_length',
    # App Info
    'app_info',
    # Helper Functions
    'record_http_request',
    'record_ai_call',
    'record_cache_operation',
    'record_db_query',
    'record_analytics_event',
    'record_celery_task',
    'initialize_app_info',
]
