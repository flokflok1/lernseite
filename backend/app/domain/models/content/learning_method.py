"""
LernsystemX Learning Method Models

Pydantic models for learning method operations:
- Learning method configuration
- Method creation and management
- Tier-based access control
- Configuration validation

ISO 9001:2015 compliant - Learning method standards
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict


class LearningMethodConfig(BaseModel):
    """
    Learning method configuration

    Flexible JSONB configuration for different method types.

    Example (Flashcards):
        >>> config = LearningMethodConfig(
        ...     supports_images=True,
        ...     supports_audio=True,
        ...     max_cards_per_set=500
        ... )

    Example (KI-Tutor):
        >>> config = LearningMethodConfig(
        ...     ai_model="gpt-4",
        ...     context_memory=True,
        ...     max_conversation_turns=50
        ... )
    """
    # Common fields
    supports_images: Optional[bool] = Field(None, description="Supports image content")
    supports_audio: Optional[bool] = Field(None, description="Supports audio content")
    supports_video: Optional[bool] = Field(None, description="Supports video content")
    ai_enabled: Optional[bool] = Field(None, description="Uses AI features")

    # Flashcards specific
    max_cards_per_set: Optional[int] = Field(None, ge=1, description="Max cards per flashcard set")

    # Quiz specific
    question_types: Optional[List[str]] = Field(None, description="Supported question types")
    max_questions: Optional[int] = Field(None, ge=1, description="Max questions per quiz")

    # KI features
    ai_model: Optional[str] = Field(None, description="AI model to use (gpt-4, claude, etc.)")
    context_memory: Optional[bool] = Field(None, description="Maintains conversation context")
    adaptive_difficulty: Optional[bool] = Field(None, description="Adjusts difficulty dynamically")
    max_conversation_turns: Optional[int] = Field(None, ge=1, description="Max conversation turns")

    # Live features
    max_participants: Optional[int] = Field(None, ge=1, description="Max participants in live session")
    screen_sharing: Optional[bool] = Field(None, description="Supports screen sharing")
    whiteboard: Optional[bool] = Field(None, description="Has whiteboard feature")
    recording: Optional[bool] = Field(None, description="Can record sessions")

    # Code features
    supported_languages: Optional[List[str]] = Field(None, description="Supported programming languages")
    code_execution: Optional[bool] = Field(None, description="Can execute code")
    step_by_step_debugging: Optional[bool] = Field(None, description="Supports step debugging")

    # Export features
    export_formats: Optional[List[str]] = Field(None, description="Supported export formats")

    # Additional custom fields
    extra: Optional[Dict[str, Any]] = Field(None, description="Additional configuration")

    model_config = ConfigDict(from_attributes=True, extra='allow')


class LearningMethodBase(BaseModel):
    """
    Base learning method model

    Example:
        >>> method = LearningMethodBase(
        ...     name="Flashcards",
        ...     description="Classic flashcards with Q&A"
        ... )
    """
    name: str = Field(..., min_length=2, max_length=100, description="Learning method name")
    description: Optional[str] = Field(None, description="Method description")

    model_config = ConfigDict(from_attributes=True)


class LearningMethodCreate(LearningMethodBase):
    """
    Learning method creation model

    Example:
        >>> method_data = LearningMethodCreate(
        ...     name="Advanced Quiz",
        ...     description="Quiz with adaptive difficulty",
        ...     tier="premium",
        ...     config={
        ...         "ai_enabled": True,
        ...         "adaptive_difficulty": True,
        ...         "max_questions": 100
        ...     }
        ... )
    """
    tier: str = Field(..., description="Access tier (basic, premium, pro)")
    config: Optional[LearningMethodConfig] = Field(None, description="Method configuration")
    active: bool = Field(default=True, description="Method is active")

    @field_validator('tier')
    @classmethod
    def validate_tier(cls, v: str) -> str:
        """Validate access tier"""
        valid_tiers = ['basic', 'premium', 'pro']
        if v not in valid_tiers:
            raise ValueError(f'Tier must be one of: {", ".join(valid_tiers)}')
        return v

    model_config = ConfigDict(from_attributes=True)


class LearningMethodUpdate(BaseModel):
    """
    Learning method update model

    All fields are optional for partial updates.

    Example:
        >>> update = LearningMethodUpdate(
        ...     description="Updated description",
        ...     active=False
        ... )
    """
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    tier: Optional[str] = None
    config: Optional[LearningMethodConfig] = None
    active: Optional[bool] = None

    @field_validator('tier')
    @classmethod
    def validate_tier(cls, v: Optional[str]) -> Optional[str]:
        """Validate access tier"""
        if v is None:
            return v
        valid_tiers = ['basic', 'premium', 'pro']
        if v not in valid_tiers:
            raise ValueError(f'Tier must be one of: {", ".join(valid_tiers)}')
        return v

    model_config = ConfigDict(from_attributes=True)


class LearningMethodResponse(LearningMethodBase):
    """
    Learning method response model

    Example:
        >>> method = LearningMethodResponse(
        ...     method_id="550e8400-e29b-41d4-a716-446655440000",
        ...     name="Flashcards",
        ...     tier="basic",
        ...     active=True,
        ...     created_at=datetime.now()
        ... )
    """
    method_id: str = Field(..., description="Learning method UUID")
    tier: str = Field(..., description="Access tier")
    config: Optional[Dict[str, Any]] = Field(None, description="Method configuration")
    active: bool = Field(default=True, description="Method is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    # Additional computed fields
    usage_count: Optional[int] = Field(None, description="Number of times used")
    is_ai_powered: Optional[bool] = Field(None, description="Uses AI features")

    model_config = ConfigDict(from_attributes=True)


class LearningMethodListResponse(BaseModel):
    """
    Learning method list response

    Example:
        >>> method_list = LearningMethodListResponse(
        ...     items=[method1, method2],
        ...     total=21,
        ...     by_tier={"basic": 11, "premium": 6, "pro": 4}
        ... )
    """
    items: List[LearningMethodResponse] = Field(..., description="List of learning methods")
    total: int = Field(..., description="Total number of methods")
    by_tier: Dict[str, int] = Field(..., description="Count by tier")

    model_config = ConfigDict(from_attributes=True)


class MethodAccessCheck(BaseModel):
    """
    Check user access to learning method

    Example:
        >>> access = MethodAccessCheck(method_id=5)
    """
    method_id: int = Field(..., description="Learning method ID")

    model_config = ConfigDict(from_attributes=True)


class MethodAccessResponse(BaseModel):
    """
    Method access check response

    Example:
        >>> access = MethodAccessResponse(
        ...     has_access=True,
        ...     method_name="KI-Tutor",
        ...     required_tier="premium",
        ...     user_tier="premium"
        ... )
    """
    has_access: bool = Field(..., description="User has access")
    method_id: int = Field(..., description="Learning method ID")
    method_name: str = Field(..., description="Method name")
    required_tier: str = Field(..., description="Required subscription tier")
    user_tier: str = Field(..., description="User's current tier")
    reason: Optional[str] = Field(None, description="Access denial reason if applicable")

    model_config = ConfigDict(from_attributes=True)


class LearningMethodStats(BaseModel):
    """
    Learning method statistics

    Example:
        >>> stats = LearningMethodStats(
        ...     total_methods=21,
        ...     active_methods=21,
        ...     by_tier={"basic": 11, "premium": 6, "pro": 4},
        ...     most_used="Flashcards"
        ... )
    """
    total_methods: int = Field(..., description="Total number of methods")
    active_methods: int = Field(..., description="Number of active methods")
    by_tier: Dict[str, int] = Field(..., description="Count by tier")
    ai_powered_count: int = Field(..., description="Number of AI-powered methods")
    most_used: Optional[str] = Field(None, description="Most used method name")
    least_used: Optional[str] = Field(None, description="Least used method name")

    model_config = ConfigDict(from_attributes=True)


class MethodUsageCreate(BaseModel):
    """
    Track learning method usage

    Example:
        >>> usage = MethodUsageCreate(
        ...     method_id="550e8400-e29b-41d4-a716-446655440000",
        ...     course_id="550e8400-e29b-41d4-a716-446655440001",
        ...     chapter_id="550e8400-e29b-41d4-a716-446655440002"
        ... )
    """
    method_id: str = Field(..., description="Learning method UUID")
    course_id: Optional[str] = Field(None, description="Course UUID (if applicable)")
    chapter_id: Optional[str] = Field(None, description="Chapter UUID (if applicable)")
    session_duration: Optional[int] = Field(None, ge=0, description="Session duration in seconds")

    model_config = ConfigDict(from_attributes=True)


class MethodUsageResponse(BaseModel):
    """
    Learning method usage response

    Example:
        >>> usage = MethodUsageResponse(
        ...     usage_id="550e8400-e29b-41d4-a716-446655440000",
        ...     user_id="550e8400-e29b-41d4-a716-446655440001",
        ...     method_id="550e8400-e29b-41d4-a716-446655440002",
        ...     used_at=datetime.now()
        ... )
    """
    usage_id: str = Field(..., description="Usage record UUID")
    user_id: str = Field(..., description="User UUID")
    method_id: str = Field(..., description="Learning method UUID")
    method_name: str = Field(..., description="Method name")
    course_id: Optional[str] = Field(None, description="Course UUID")
    chapter_id: Optional[str] = Field(None, description="Chapter UUID")
    session_duration: Optional[int] = Field(None, description="Session duration in seconds")
    used_at: datetime = Field(..., description="Usage timestamp")

    model_config = ConfigDict(from_attributes=True)


# Predefined method tier mappings
BASIC_METHODS = [
    'Flashcards', 'Quiz', 'Lückentext', 'Multiple Choice',
    'True/False', 'Zuordnung', 'Sortierung', 'Mindmap',
    'Video', 'Audio', 'PDF'
]

PREMIUM_METHODS = [
    'KI-Tutor', 'KI-Glossar', 'Braindump',
    'Zertifikatsprüfung', 'Lernpfad-KI', 'Live-Raum'
]

PRO_METHODS = [
    'Deep Praxis', 'Deep Scenario',
    'Projekt-Simulation', 'Echtzeit-Debugging'
]


def get_required_tier(method_name: str) -> str:
    """
    Get required tier for a learning method

    Args:
        method_name: Name of the learning method

    Returns:
        Required tier ('basic', 'premium', or 'pro')

    Example:
        >>> tier = get_required_tier('KI-Tutor')
        >>> print(tier)  # 'premium'
    """
    if method_name in BASIC_METHODS:
        return 'basic'
    elif method_name in PREMIUM_METHODS:
        return 'premium'
    elif method_name in PRO_METHODS:
        return 'pro'
    else:
        return 'basic'  # Default to basic for unknown methods


def check_tier_access(user_tier: str, required_tier: str) -> bool:
    """
    Check if user tier has access to required tier

    Tier hierarchy: basic < premium < pro

    Args:
        user_tier: User's subscription tier
        required_tier: Required tier for method

    Returns:
        True if user has access, False otherwise

    Example:
        >>> has_access = check_tier_access('premium', 'basic')
        >>> print(has_access)  # True

        >>> has_access = check_tier_access('basic', 'premium')
        >>> print(has_access)  # False
    """
    tier_hierarchy = {
        'basic': 1,
        'premium': 2,
        'pro': 3
    }

    user_level = tier_hierarchy.get(user_tier, 0)
    required_level = tier_hierarchy.get(required_tier, 0)

    return user_level >= required_level


# ============================================================================
# AI EXECUTION MODELS (Phase 11)
# ============================================================================

class LearningMethodExecutionRequest(BaseModel):
    """
    Learning method AI execution request

    Example (KI-Tutor):
        >>> request = LearningMethodExecutionRequest(
        ...     method_id="550e8400-e29b-41d4-a716-446655440000",
        ...     course_id="550e8400-e29b-41d4-a716-446655440001",
        ...     chapter_id="550e8400-e29b-41d4-a716-446655440002",
        ...     user_input="Erkläre mir Polymorphismus in Python",
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
        ...     output_text="Polymorphismus in Python ermöglicht...",
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
        ...     feedback_text="Gute Erklärung, aber könnte detaillierter sein",
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
        ...     feedback_text="Gute Erklärung",
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
