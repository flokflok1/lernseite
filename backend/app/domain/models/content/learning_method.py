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
