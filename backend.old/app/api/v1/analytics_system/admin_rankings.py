"""
Analytics Rankings Endpoints (DDD)

Admin endpoints for top courses and top learning methods analytics.
Uses AnalyticsQueryFactory and AnalyticsAggregationService.
"""

from flask import request, jsonify, g
from typing import Dict, Any, Tuple
import logging

from app.extensions import limiter
from app.middleware.auth import token_required
from app.security.permissions import require_permission, Permissions
from app.repositories.analytics import AnalyticsRepository
from app.models.analytics import (
    TopCoursesResponse,
    TopCourseAnalytics,
    TopMethodsResponse,
    TopMethodAnalytics
)

from app.api.v1.analytics_system.factory import AnalyticsQueryFactory
from app.api.v1.analytics_system.services import AnalyticsAggregationService
from app.api.v1.analytics_system.value_objects import TimeRange

