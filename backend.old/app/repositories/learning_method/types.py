"""
Learning Method Repository Type Definitions

Pydantic models and type hints for learning method operations.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime


class LearningMethodBase:
    """Base type for learning method records"""
    method_id: str
    method_type: int
    title: str
    description: Optional[str]
    tier: str
    config: Dict[str, Any]
    active: bool
    created_at: datetime
    updated_at: datetime


class AIExecutionResult:
    """Result from AI method execution"""
    execution_id: str
    method_id: str
    method_name: str
    output_text: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    model: str
    provider: str
    latency_ms: int
    cost_eur: float
    executed_at: datetime


class TokenUsageStats:
    """Token usage statistics"""
    user_id: str
    total_tokens: int
    total_cost_eur: float
    total_requests: int
    by_method: Dict[str, int]
    by_provider: Dict[str, int]
    by_model: Dict[str, int]
    period_start: datetime
    period_end: datetime


class FeedbackStats:
    """Feedback statistics"""
    method_id: Optional[str]
    total_feedback: int
    average_rating: float
    helpful_count: int
    not_helpful_count: int
    rating_distribution: Dict[int, int]


class MethodStatistics:
    """Overall method statistics"""
    total_methods: int
    active_methods: int
    by_tier: Dict[str, int]
    ai_powered_count: int
    most_used: Optional[str]
    total_executions: int
    total_tokens: int
    total_cost_eur: float
