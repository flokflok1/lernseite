"""
LernsystemX Analytics Models

Pydantic models for analytics event tracking and statistics:
- Analytics event creation and retrieval
- User statistics aggregation
- Organisation statistics aggregation
- Event type validation

ISO 9001:2015 compliant - Analytics data standards
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum


class EventType(str, Enum):
    """
    Supported event types for analytics tracking

    Matches database CHECK constraint
    """
    # Authentication events
    LOGIN = 'login'
    LOGOUT = 'logout'

    # Navigation events
    PAGE_VIEW = 'page_view'

    # Course events
    COURSE_VIEW = 'course_view'
    COURSE_ENROLL = 'course_enroll'

    # Module events (legacy)
    MODULE_START = 'module_start'
    MODULE_COMPLETE = 'module_complete'

    # Chapter events (renamed from module)
    CHAPTER_START = 'chapter_start'
    CHAPTER_COMPLETE = 'chapter_complete'

    # Lesson events
    LESSON_START = 'lesson_start'
    LESSON_COMPLETE = 'lesson_complete'

    # Learning method events
    METHOD_EXECUTE = 'method_execute'

    # Exam events
    EXAM_START = 'exam_start'
    EXAM_COMPLETE = 'exam_complete'

    # LiveRoom events
    LIVEROOM_JOIN = 'liveroom_join'
    LIVEROOM_LEAVE = 'liveroom_leave'

    # KI events
    KI_JOB_START = 'ki_job_start'
    KI_JOB_COMPLETE = 'ki_job_complete'

    # Purchase events
    PURCHASE = 'purchase'
    SUBSCRIPTION_START = 'subscription_start'
    SUBSCRIPTION_CANCEL = 'subscription_cancel'


class ResourceType(str, Enum):
    """Resource types that can be tracked"""
    COURSE = 'course'
    MODULE = 'module'  # legacy
    CHAPTER = 'chapter'  # renamed from module
    LESSON = 'lesson'
    METHOD = 'method'
    LEARNING_METHOD = 'learning_method'  # alias for method
    EXAM = 'exam'
    LIVEROOM = 'liveroom'
    SUBSCRIPTION = 'subscription'
    PAGE = 'page'


class AnalyticsEventBase(BaseModel):
    """
    Base analytics event model

    Common fields for all analytics events
    """
    event_type: EventType = Field(..., description="Type of event")
    resource_type: Optional[ResourceType] = Field(None, description="Type of resource (e.g., course, module)")
    resource_id: Optional[Union[int, str]] = Field(None, description="ID of the resource (int or UUID)")
    payload: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional event data")
    session_id: Optional[str] = Field(None, description="Session identifier")

    model_config = ConfigDict(from_attributes=True)


class AnalyticsEventCreateRequest(AnalyticsEventBase):
    """
    Request model for creating analytics events

    Used by POST /api/v1/analytics/event
    User ID and organisation ID come from JWT token
    """
    pass


class AnalyticsEventResponse(AnalyticsEventBase):
    """
    Response model for analytics events

    Includes all database fields
    """
    event_id: int = Field(..., description="Event ID")
    user_id: Union[int, str] = Field(..., description="User ID (UUID or int)")
    organisation_id: Optional[Union[int, str]] = Field(None, description="Organisation ID (UUID or int)")
    ip_address_hash: Optional[str] = Field(None, description="Anonymized IP address hash")
    created_at: str = Field(..., description="Event timestamp (ISO 8601)")

    model_config = ConfigDict(from_attributes=True)


class AnalyticsUserStats(BaseModel):
    """
    User-level analytics statistics

    Aggregated statistics for individual user
    """
    user_id: Union[int, str] = Field(..., description="User ID (UUID or int)")
    total_events: int = Field(0, description="Total number of events")
    event_counts_by_type: Dict[str, int] = Field(
        default_factory=dict,
        description="Event counts grouped by type"
    )
    recent_events: List[AnalyticsEventResponse] = Field(
        default_factory=list,
        description="Recent events (last 10)"
    )
    first_event_at: Optional[str] = Field(None, description="First event timestamp")
    last_event_at: Optional[str] = Field(None, description="Last event timestamp")

    # Course-specific stats
    courses_viewed: int = Field(0, description="Number of courses viewed")
    courses_enrolled: int = Field(0, description="Number of courses enrolled")
    modules_completed: int = Field(0, description="Number of modules completed")
    lessons_completed: int = Field(0, description="Number of lessons completed")

    model_config = ConfigDict(from_attributes=True)


class AnalyticsOrgStats(BaseModel):
    """
    Organisation-level analytics statistics

    Aggregated statistics for entire organisation
    """
    organisation_id: Union[int, str] = Field(..., description="Organisation ID (UUID or int)")
    total_events: int = Field(0, description="Total number of events")
    total_users: int = Field(0, description="Number of users in organisation")
    active_users_30d: int = Field(0, description="Users active in last 30 days")
    event_counts_by_type: Dict[str, int] = Field(
        default_factory=dict,
        description="Event counts grouped by type"
    )
    top_courses: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Most viewed/enrolled courses"
    )
    first_event_at: Optional[str] = Field(None, description="First event timestamp")
    last_event_at: Optional[str] = Field(None, description="Last event timestamp")

    # Organisation-specific stats
    total_course_enrollments: int = Field(0, description="Total course enrollments")
    total_modules_completed: int = Field(0, description="Total modules completed")
    total_exams_completed: int = Field(0, description="Total exams completed")
    avg_completion_rate: float = Field(0.0, description="Average completion rate (%)")

    model_config = ConfigDict(from_attributes=True)


class AnalyticsStatsResponse(BaseModel):
    """
    Generic analytics statistics response

    Can contain either user or org stats
    """
    success: bool = Field(..., description="Operation success status")
    stats_type: str = Field(..., description="Type of statistics (user/organisation)")
    stats: Dict[str, Any] = Field(..., description="Statistics data")

    model_config = ConfigDict(from_attributes=True)


class EventCount(BaseModel):
    """Event count by type"""
    event_type: str = Field(..., description="Event type")
    count: int = Field(..., description="Number of events")

    model_config = ConfigDict(from_attributes=True)


class TimeSeriesPoint(BaseModel):
    """Time series data point for analytics charts"""
    timestamp: str = Field(..., description="Timestamp (ISO 8601)")
    value: int = Field(..., description="Value at this timestamp")
    label: Optional[str] = Field(None, description="Optional label")

    model_config = ConfigDict(from_attributes=True)


class AnalyticsChartData(BaseModel):
    """Chart data for analytics visualizations"""
    chart_type: str = Field(..., description="Chart type (line, bar, pie)")
    title: str = Field(..., description="Chart title")
    data_points: List[TimeSeriesPoint] = Field(..., description="Chart data points")

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Advanced Analytics Models (Phase B10)
# ============================================================================

class SystemAnalyticsTimeSeriesRequest(BaseModel):
    """Request model for time series analytics with range parameter"""
    range: Optional[str] = Field('7d', description="Time range (7d, 30d, 90d)")
    from_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    to_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")

    model_config = ConfigDict(from_attributes=True)


class TimeSeriesDataPoint(BaseModel):
    """Time series data point (simplified for frontend)"""
    date: str = Field(..., description="Date (YYYY-MM-DD)")
    value: int = Field(..., description="Value for this date")

    model_config = ConfigDict(from_attributes=True)


class TimeSeriesResponse(BaseModel):
    """Response for time series endpoints"""
    success: bool = Field(True, description="Operation success")
    data: List[TimeSeriesDataPoint] = Field(..., description="Time series points")
    total: int = Field(..., description="Total count across entire period")

    model_config = ConfigDict(from_attributes=True)


class TopCourseAnalytics(BaseModel):
    """Top course analytics data"""
    course_id: int = Field(..., description="Course ID")
    title: str = Field(..., description="Course title")
    events_count: int = Field(0, description="Number of events")
    enrollments: int = Field(0, description="Number of enrollments")
    completions: int = Field(0, description="Number of completions")
    avg_completion_rate: Optional[float] = Field(None, description="Average completion rate (%)")

    model_config = ConfigDict(from_attributes=True)


class TopMethodAnalytics(BaseModel):
    """Top learning method analytics data"""
    method_id: int = Field(..., description="Method ID")
    name: str = Field(..., description="Method name")
    calls: int = Field(0, description="Number of calls")
    tokens_used: Optional[int] = Field(None, description="Total tokens used")
    avg_tokens: Optional[int] = Field(None, description="Average tokens per call")

    model_config = ConfigDict(from_attributes=True)


class TopCoursesResponse(BaseModel):
    """Response for top courses endpoint"""
    success: bool = Field(True, description="Operation success")
    courses: List[TopCourseAnalytics] = Field(..., description="Top courses")
    total: int = Field(..., description="Total number of courses")

    model_config = ConfigDict(from_attributes=True)


class TopMethodsResponse(BaseModel):
    """Response for top methods endpoint"""
    success: bool = Field(True, description="Operation success")
    methods: List[TopMethodAnalytics] = Field(..., description="Top methods")
    total: int = Field(..., description="Total number of methods")

    model_config = ConfigDict(from_attributes=True)


class OrgTopCourseAnalytics(BaseModel):
    """Organisation top course analytics"""
    course_id: int = Field(..., description="Course ID")
    title: str = Field(..., description="Course title")
    enrolled_count: int = Field(0, description="Number of enrolled members")
    avg_progress: float = Field(0.0, description="Average progress (%)")
    completion_rate: Optional[float] = Field(None, description="Completion rate (%)")
    events_count: Optional[int] = Field(None, description="Number of events")

    model_config = ConfigDict(from_attributes=True)


class OrgTopModuleAnalytics(BaseModel):
    """Organisation top module analytics"""
    module_id: int = Field(..., description="Module ID")
    module_title: str = Field(..., description="Module title")
    course_title: str = Field(..., description="Course title")
    completions: int = Field(0, description="Number of completions")
    avg_time_spent: Optional[int] = Field(None, description="Average time spent (minutes)")

    model_config = ConfigDict(from_attributes=True)


class OrgTopCoursesResponse(BaseModel):
    """Response for org top courses endpoint"""
    success: bool = Field(True, description="Operation success")
    courses: List[OrgTopCourseAnalytics] = Field(..., description="Top courses")
    total: int = Field(..., description="Total number of courses")

    model_config = ConfigDict(from_attributes=True)


class OrgTopModulesResponse(BaseModel):
    """Response for org top modules endpoint"""
    success: bool = Field(True, description="Operation success")
    modules: List[OrgTopModuleAnalytics] = Field(..., description="Top modules")
    total: int = Field(..., description="Total number of modules")

    model_config = ConfigDict(from_attributes=True)
