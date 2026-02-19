"""
LernsystemX Learning Method AI Execution Models

Pydantic models for AI-powered learning method execution:
- AI execution requests and responses
- Token usage tracking and statistics
- AI feedback collection and analytics

ISO 9001:2015 compliant - Learning method AI execution standards
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict


class LearningMethodExecutionRequest(BaseModel):
    """
    Learning method AI execution request

    Example (KI-Tutor):
        >>> request = LearningMethodExecutionRequest(
        ...     method_id="550e8400-e29b-41d4-a716-446655440000",
        ...     course_id="550e8400-e29b-41d4-a716-446655440001",
        ...     chapter_id="550e8400-e29b-41d4-a716-446655440002",
        ...     user_input="Erklaere mir Polymorphismus in Python",
        ...     context="Wir sind bei Lektion 3: OOP Konzepte",
        ...     language="de",
        ...     difficulty="intermediate"
        ... )

    Example (KI-Glossar):
        >>> request = LearningMethodExecutionRequest(
        ...     method_id="550e8400-e29b-41d4-a716-446655440000",
        ...     user_input="Rekursion",
        ...     language="de"
        ... )
    """
    method_id: str = Field(..., description="Learning method UUID")
    course_id: Optional[str] = Field(None, description="Course UUID (context)")
    chapter_id: Optional[str] = Field(None, description="Chapter UUID (context)")
    lesson_id: Optional[str] = Field(None, description="Lesson UUID (context)")
    user_input: Optional[str] = Field(default="", max_length=5000, description="User input/question (optional for some methods)")
    context: Optional[str] = Field(None, max_length=10000, description="Additional context (max 10k chars)")
    language: str = Field(default="de", description="Response language")
    difficulty: Optional[str] = Field(None, description="Difficulty level (beginner, intermediate, advanced)")
    conversation_history: Optional[List[Dict[str, str]]] = Field(None, description="Previous conversation turns")

    @field_validator('language')
    @classmethod
    def validate_language(cls, v: str) -> str:
        """Validate language code"""
        valid_languages = ['de', 'en', 'pl', 'es', 'fr', 'it']
        if v not in valid_languages:
            raise ValueError(f'Language must be one of: {", ".join(valid_languages)}')
        return v

    @field_validator('difficulty')
    @classmethod
    def validate_difficulty(cls, v: Optional[str]) -> Optional[str]:
        """Validate difficulty level"""
        if v is None:
            return v
        valid_difficulties = ['beginner', 'intermediate', 'advanced']
        if v not in valid_difficulties:
            raise ValueError(f'Difficulty must be one of: {", ".join(valid_difficulties)}')
        return v

    @field_validator('conversation_history')
    @classmethod
    def validate_conversation_history(cls, v: Optional[List[Dict[str, str]]]) -> Optional[List[Dict[str, str]]]:
        """Validate conversation history format"""
        if v is None:
            return v

        # Limit to last 20 turns
        if len(v) > 20:
            v = v[-20:]

        # Validate each turn has role and content
        for turn in v:
            if 'role' not in turn or 'content' not in turn:
                raise ValueError('Each conversation turn must have "role" and "content" keys')
            if turn['role'] not in ['user', 'assistant']:
                raise ValueError('Role must be "user" or "assistant"')

        return v

    model_config = ConfigDict(from_attributes=True)


class LearningMethodExecutionResponse(BaseModel):
    """
    Learning method AI execution response

    Example:
        >>> response = LearningMethodExecutionResponse(
        ...     execution_id="550e8400-e29b-41d4-a716-446655440000",
        ...     method_id="550e8400-e29b-41d4-a716-446655440001",
        ...     method_name="KI-Tutor",
        ...     output_text="Polymorphismus in Python ermoeglicht...",
        ...     input_tokens=150,
        ...     output_tokens=320,
        ...     total_tokens=470,
        ...     model="gpt-4o-mini",
        ...     provider="openai",
        ...     latency_ms=1234,
        ...     confidence=0.92,
        ...     cost_eur=0.0015
        ... )
    """
    execution_id: str = Field(..., description="Execution record UUID")
    method_id: str = Field(..., description="Learning method UUID")
    method_name: str = Field(..., description="Method name")
    output_text: str = Field(..., description="AI-generated response")
    input_tokens: int = Field(..., ge=0, description="Input tokens consumed")
    output_tokens: int = Field(..., ge=0, description="Output tokens consumed")
    total_tokens: int = Field(..., ge=0, description="Total tokens consumed")
    model: str = Field(..., description="AI model used (e.g., gpt-4o-mini, claude-3-5-sonnet)")
    provider: str = Field(..., description="AI provider (openai, anthropic, google, cohere, huggingface)")
    latency_ms: int = Field(..., ge=0, description="Response latency in milliseconds")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score (0.0-1.0)")
    cost_eur: float = Field(..., ge=0.0, description="Cost in EUR")
    feedback_score: Optional[float] = Field(None, ge=0.0, le=5.0, description="Average user feedback (0-5)")
    executed_at: datetime = Field(..., description="Execution timestamp")
    billing: Optional[Dict[str, Any]] = Field(None, description="Billing information (tokens_charged, new_balance, transaction_id)")

    model_config = ConfigDict(from_attributes=True)


class AITokenUsage(BaseModel):
    """
    AI token usage tracking

    Example:
        >>> usage = AITokenUsage(
        ...     user_id="550e8400-e29b-41d4-a716-446655440000",
        ...     organisation_id="550e8400-e29b-41d4-a716-446655440001",
        ...     method_id="550e8400-e29b-41d4-a716-446655440002",
        ...     method_name="KI-Tutor",
        ...     input_tokens=150,
        ...     output_tokens=320,
        ...     total_tokens=470,
        ...     model="gpt-4o-mini",
        ...     provider="openai",
        ...     cost_eur=0.0015
        ... )
    """
    usage_id: Optional[str] = Field(None, description="Usage record UUID")
    user_id: str = Field(..., description="User UUID")
    organisation_id: Optional[str] = Field(None, description="Organisation UUID (if applicable)")
    method_id: str = Field(..., description="Learning method UUID")
    method_name: str = Field(..., description="Method name")
    course_id: Optional[str] = Field(None, description="Course UUID (context)")
    chapter_id: Optional[str] = Field(None, description="Chapter UUID (context)")
    lesson_id: Optional[str] = Field(None, description="Lesson UUID (context)")
    input_tokens: int = Field(..., ge=0, description="Input tokens")
    output_tokens: int = Field(..., ge=0, description="Output tokens")
    total_tokens: int = Field(..., ge=0, description="Total tokens")
    model: str = Field(..., description="AI model used")
    provider: str = Field(..., description="AI provider")
    cost_eur: float = Field(..., ge=0.0, description="Cost in EUR")
    used_at: datetime = Field(default_factory=datetime.now, description="Usage timestamp")

    model_config = ConfigDict(from_attributes=True)


class AITokenUsageStats(BaseModel):
    """
    AI token usage statistics

    Example:
        >>> stats = AITokenUsageStats(
        ...     total_tokens=125000,
        ...     total_cost_eur=12.50,
        ...     total_requests=267,
        ...     by_method={"KI-Tutor": 85000, "KI-Glossar": 40000},
        ...     by_provider={"openai": 100000, "anthropic": 25000}
        ... )
    """
    user_id: Optional[int] = Field(None, description="User ID (if user-specific)")
    organisation_id: Optional[int] = Field(None, description="Organisation ID (if org-specific)")
    total_tokens: int = Field(..., ge=0, description="Total tokens consumed")
    total_cost_eur: float = Field(..., ge=0.0, description="Total cost in EUR")
    total_requests: int = Field(..., ge=0, description="Total AI requests")
    by_method: Dict[str, int] = Field(..., description="Token usage by method")
    by_provider: Dict[str, int] = Field(..., description="Token usage by provider")
    by_model: Dict[str, int] = Field(..., description="Token usage by model")
    period_start: Optional[datetime] = Field(None, description="Statistics period start")
    period_end: Optional[datetime] = Field(None, description="Statistics period end")

    model_config = ConfigDict(from_attributes=True)


class AIFeedbackCreate(BaseModel):
    """
    AI feedback submission

    Example:
        >>> feedback = AIFeedbackCreate(
        ...     execution_id="550e8400-e29b-41d4-a716-446655440000",
        ...     rating=4,
        ...     feedback_text="Gute Erklaerung, aber koennte detaillierter sein",
        ...     is_helpful=True
        ... )
    """
    execution_id: str = Field(..., description="Execution record UUID")
    course_id: Optional[str] = Field(None, description="Course UUID (context)")
    chapter_id: Optional[str] = Field(None, description="Chapter UUID (context)")
    lesson_id: Optional[str] = Field(None, description="Lesson UUID (context)")
    rating: int = Field(..., ge=1, le=5, description="Rating (1-5 stars)")
    feedback_text: Optional[str] = Field(None, max_length=2000, description="Feedback text")
    is_helpful: bool = Field(default=True, description="Was response helpful?")
    ai_generated: bool = Field(default=False, description="Is feedback AI-generated?")

    model_config = ConfigDict(from_attributes=True)


class AIFeedbackResponse(BaseModel):
    """
    AI feedback response

    Example:
        >>> feedback = AIFeedbackResponse(
        ...     feedback_id="550e8400-e29b-41d4-a716-446655440000",
        ...     user_id="550e8400-e29b-41d4-a716-446655440001",
        ...     execution_id="550e8400-e29b-41d4-a716-446655440002",
        ...     rating=4,
        ...     feedback_text="Gute Erklaerung",
        ...     is_helpful=True,
        ...     created_at=datetime.now()
        ... )
    """
    feedback_id: str = Field(..., description="Feedback record UUID")
    user_id: str = Field(..., description="User UUID")
    execution_id: str = Field(..., description="Execution record UUID")
    method_id: str = Field(..., description="Learning method UUID")
    method_name: str = Field(..., description="Method name")
    course_id: Optional[str] = Field(None, description="Course UUID")
    chapter_id: Optional[str] = Field(None, description="Chapter UUID")
    lesson_id: Optional[str] = Field(None, description="Lesson UUID")
    rating: int = Field(..., ge=1, le=5, description="Rating (1-5 stars)")
    feedback_text: Optional[str] = Field(None, description="Feedback text")
    is_helpful: bool = Field(..., description="Was response helpful?")
    ai_generated: bool = Field(..., description="Is feedback AI-generated?")
    created_at: datetime = Field(..., description="Feedback timestamp")

    model_config = ConfigDict(from_attributes=True)


class AIFeedbackStats(BaseModel):
    """
    AI feedback statistics

    Example:
        >>> stats = AIFeedbackStats(
        ...     total_feedback=156,
        ...     average_rating=4.2,
        ...     helpful_count=142,
        ...     not_helpful_count=14,
        ...     rating_distribution={1: 5, 2: 8, 3: 15, 4: 48, 5: 80}
        ... )
    """
    method_id: Optional[int] = Field(None, description="Method ID (if method-specific)")
    method_name: Optional[str] = Field(None, description="Method name")
    total_feedback: int = Field(..., ge=0, description="Total feedback submissions")
    average_rating: float = Field(..., ge=0.0, le=5.0, description="Average rating")
    helpful_count: int = Field(..., ge=0, description="Number of helpful ratings")
    not_helpful_count: int = Field(..., ge=0, description="Number of not helpful ratings")
    rating_distribution: Dict[int, int] = Field(..., description="Count by rating (1-5)")

    model_config = ConfigDict(from_attributes=True)
