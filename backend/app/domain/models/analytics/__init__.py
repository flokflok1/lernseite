"""
Analytics Models Package

Provides Pydantic models for analytics event tracking.
"""

from app.domain.models.analytics.core import (
    EventType,
    ResourceType,
    AnalyticsEventBase,
    AnalyticsEventCreateRequest,
    AnalyticsEventResponse,
    AnalyticsUserStats,
    AnalyticsOrgStats,
    AnalyticsStatsResponse,
    EventCount,
    TimeSeriesPoint,
    AnalyticsChartData,
    SystemAnalyticsTimeSeriesRequest,
    TimeSeriesDataPoint,
    TimeSeriesResponse,
    TopCourseAnalytics,
    TopMethodAnalytics,
    TopCoursesResponse,
    TopMethodsResponse,
    OrgTopCourseAnalytics,
    OrgTopModuleAnalytics,
)

__all__ = [
    'EventType',
    'ResourceType',
    'AnalyticsEventBase',
    'AnalyticsEventCreateRequest',
    'AnalyticsEventResponse',
    'AnalyticsUserStats',
    'AnalyticsOrgStats',
    'AnalyticsStatsResponse',
    'EventCount',
    'TimeSeriesPoint',
    'AnalyticsChartData',
    'SystemAnalyticsTimeSeriesRequest',
    'TimeSeriesDataPoint',
    'TimeSeriesResponse',
    'TopCourseAnalytics',
    'TopMethodAnalytics',
    'TopCoursesResponse',
    'TopMethodsResponse',
    'OrgTopCourseAnalytics',
    'OrgTopModuleAnalytics',
]
