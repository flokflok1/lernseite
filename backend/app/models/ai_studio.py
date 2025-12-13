"""
LernsystemX AI Studio Models

Pydantic models for KI-Authoring-Studio:
- Session creation/update requests
- Session responses
- Variant management
- Template responses
- PDF upload responses

Phase D4 - KI-Authoring-Studio - ISO 9001:2015 compliant
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum


class SessionStatus(str, Enum):
    """Session status enum"""
    DRAFT = 'draft'
    IN_PROGRESS = 'in_progress'
    REVIEW = 'review'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'


class SourceType(str, Enum):
    """Source type enum"""
    MANUAL = 'manual'
    PDF = 'pdf'
    URL = 'url'
    EXISTING_CHAPTER = 'existing_chapter'
    TEMPLATE = 'template'


class VariantType(str, Enum):
    """Variant type enum"""
    THEORY = 'theory'
    LESSON = 'lesson'
    METHOD = 'method'
    QUIZ = 'quiz'
    SUMMARY = 'summary'
    FULL_CHAPTER = 'full_chapter'


class SessionStep(str, Enum):
    """Session workflow steps"""
    SOURCE_SELECTION = 'source_selection'
    THEORY_GENERATION = 'theory_generation'
    LESSON_GENERATION = 'lesson_generation'
    METHOD_GENERATION = 'method_generation'
    QUIZ_GENERATION = 'quiz_generation'
    REVIEW = 'review'
    FINALIZE = 'finalize'


# ============================================================================
# Request Models
# ============================================================================

class AIStudioSessionCreateRequest(BaseModel):
    """
    Create new AI authoring session

    Example:
        >>> request = AIStudioSessionCreateRequest(
        ...     course_id="uuid",
        ...     session_name="Kapitel 1: Einführung",
        ...     source_type="pdf"
        ... )
    """
    course_id: str = Field(..., description="Course UUID")
    session_name: Optional[str] = Field(None, max_length=255, description="Session name")
    source_type: SourceType = Field(default=SourceType.MANUAL, description="Source content type")
    template_key: Optional[str] = Field(None, description="Template key to use")
    chapter_id: Optional[str] = Field(None, description="Existing chapter ID (for editing)")

    model_config = ConfigDict(from_attributes=True)


class AIStudioSessionUpdateRequest(BaseModel):
    """Update session data"""
    session_name: Optional[str] = Field(None, max_length=255)
    status: Optional[SessionStatus] = None
    current_step: Optional[SessionStep] = None
    ai_config: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class AIStudioSourceDataRequest(BaseModel):
    """Update source data for session"""
    source_type: SourceType = Field(..., description="Source type")
    source_data: Dict[str, Any] = Field(default_factory=dict, description="Source content data")

    model_config = ConfigDict(from_attributes=True)


class AIStudioGenerateRequest(BaseModel):
    """
    Request AI content generation

    Example:
        >>> request = AIStudioGenerateRequest(
        ...     content_type="theory",
        ...     prompt="Erstelle eine Einführung zum Thema Python",
        ...     generate_variants=3
        ... )
    """
    content_type: VariantType = Field(..., description="Type of content to generate")
    prompt: Optional[str] = Field(None, max_length=5000, description="Custom generation prompt")
    generate_variants: int = Field(default=1, ge=1, le=5, description="Number of variants to generate")
    ai_config_override: Optional[Dict[str, Any]] = Field(None, description="Override AI settings for this generation")

    model_config = ConfigDict(from_attributes=True)


class AIStudioSelectVariantRequest(BaseModel):
    """Select a variant for use"""
    variant_id: str = Field(..., description="Variant UUID to select")

    model_config = ConfigDict(from_attributes=True)


class AIStudioRateVariantRequest(BaseModel):
    """Rate a generated variant"""
    variant_id: str = Field(..., description="Variant UUID")
    rating: int = Field(..., ge=1, le=5, description="Rating 1-5")
    feedback: Optional[str] = Field(None, max_length=1000, description="Optional feedback")

    model_config = ConfigDict(from_attributes=True)


class AIStudioFinalizeRequest(BaseModel):
    """
    Finalize session and create chapter

    Example:
        >>> request = AIStudioFinalizeRequest(
        ...     create_chapter=True,
        ...     create_lessons=True,
        ...     create_methods=True,
        ...     chapter_title="Kapitel 1: Einführung"
        ... )
    """
    create_chapter: bool = Field(default=True, description="Create chapter from generated content")
    create_lessons: bool = Field(default=True, description="Create lessons")
    create_methods: bool = Field(default=True, description="Create learning methods")
    chapter_title: Optional[str] = Field(None, max_length=255, description="Override chapter title")
    publish_immediately: bool = Field(default=False, description="Publish chapter immediately")

    model_config = ConfigDict(from_attributes=True)


class AIStudioSnapshotRequest(BaseModel):
    """Create session snapshot"""
    description: Optional[str] = Field(None, max_length=255, description="Snapshot description")

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Response Models
# ============================================================================

class AIStudioSessionResponse(BaseModel):
    """
    AI authoring session response

    Example response:
        {
            "session_id": "uuid",
            "user_id": "uuid",
            "course_id": "uuid",
            "session_name": "Kapitel 1",
            "status": "in_progress",
            "current_step": "theory_generation",
            "steps_completed": ["source_selection"],
            ...
        }
    """
    session_id: str
    user_id: str
    course_id: str
    chapter_id: Optional[str] = None
    session_name: Optional[str] = None
    status: SessionStatus
    source_type: SourceType
    source_data: Dict[str, Any] = Field(default_factory=dict)
    ai_config: Dict[str, Any] = Field(default_factory=dict)
    generated_theory: Optional[Dict[str, Any]] = None
    generated_lessons: List[Dict[str, Any]] = Field(default_factory=list)
    generated_methods: List[Dict[str, Any]] = Field(default_factory=list)
    current_step: str
    steps_completed: List[str] = Field(default_factory=list)
    started_at: datetime
    last_activity_at: datetime
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    # Joined fields
    user_email: Optional[str] = None
    course_title: Optional[str] = None
    chapter_title: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AIStudioSessionListItem(BaseModel):
    """Session list item (compact)"""
    session_id: str
    session_name: Optional[str] = None
    course_id: str
    course_title: Optional[str] = None
    status: SessionStatus
    current_step: str
    source_type: SourceType
    last_activity_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AIStudioVariantResponse(BaseModel):
    """Generated variant response"""
    variant_id: str
    session_id: str
    variant_type: VariantType
    variant_index: int
    content: Dict[str, Any]
    ai_provider: Optional[str] = None
    ai_model: Optional[str] = None
    is_selected: bool = False
    user_rating: Optional[int] = None
    user_feedback: Optional[str] = None
    generation_duration_ms: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AIStudioSnapshotResponse(BaseModel):
    """Session snapshot response"""
    snapshot_id: str
    session_id: str
    description: Optional[str] = None
    sequence_number: int
    is_current: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AIStudioTemplateResponse(BaseModel):
    """Authoring template response"""
    template_id: str
    template_name: str
    template_key: str
    category: str
    description: Optional[str] = None
    template_config: Dict[str, Any]
    is_system: bool
    usage_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AIStudioPDFUploadResponse(BaseModel):
    """PDF upload response"""
    file_hash: str
    original_filename: str
    file_size_bytes: int
    page_count: int
    extracted_text: str
    structure_analysis: Dict[str, Any] = Field(default_factory=dict)
    from_cache: bool = False

    model_config = ConfigDict(from_attributes=True)


class AIStudioStatsResponse(BaseModel):
    """User statistics response"""
    total_sessions: int
    active_sessions: int
    completed_sessions: int
    total_chapters_created: int
    total_tokens_used: int
    avg_generation_time_ms: float

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# WebSocket Event Models
# ============================================================================

class AIStudioProgressEvent(BaseModel):
    """Progress update event for WebSocket"""
    session_id: str
    event_type: str = Field(..., description="Event type: progress, complete, error")
    step: str
    progress: int = Field(ge=0, le=100)
    message: str
    data: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)
