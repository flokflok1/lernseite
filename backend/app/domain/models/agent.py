"""
LernsystemX Agent Models

Pydantic models for Smart Agent System:
- Agent configuration
- Agent queries (ask)
- Knowledge entries
- Agent feedback

ISO 9001:2015 compliant - Agent data validation
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum


# =========================================================================
# Enums
# =========================================================================

class AgentPersona(str, Enum):
    """Agent persona types"""
    FRIENDLY = 'friendly'
    PROFESSIONAL = 'professional'
    ENCOURAGING = 'encouraging'
    SOCRATIC = 'socratic'


class KnowledgeStatus(str, Enum):
    """Agent knowledge status"""
    PENDING = 'pending'
    WARMING = 'warming'
    READY = 'ready'
    STALE = 'stale'


class KnowledgeType(str, Enum):
    """Knowledge entry types"""
    QA_PAIR = 'qa_pair'
    EXPLANATION = 'explanation'
    EXAMPLE = 'example'
    CONCEPT = 'concept'
    DEFINITION = 'definition'


class ScopeType(str, Enum):
    """Knowledge scope types"""
    COURSE = 'course'
    CHAPTER = 'chapter'
    LESSON = 'lesson'


class ResponseSource(str, Enum):
    """Response source types"""
    CACHE_HIT = 'cache_hit'
    KNOWLEDGE_MATCH = 'knowledge_match'
    AI_GENERATED = 'ai_generated'
    OFFLINE_FALLBACK = 'offline_fallback'
    OFFLINE_NO_DATA = 'offline_no_data'
    ERROR = 'error'


# =========================================================================
# Request Models
# =========================================================================

class AgentAskRequest(BaseModel):
    """
    Request model for asking the agent a question

    Example:
        >>> request = AgentAskRequest(
        ...     question="Was ist Polymorphismus?",
        ...     context={"lesson_id": "uuid", "lesson_title": "OOP Grundlagen"}
        ... )
    """
    question: str = Field(
        ...,
        min_length=3,
        max_length=2000,
        description="Question to ask the agent"
    )
    context: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional context (lesson_id, chapter_id, course_title, etc.)"
    )
    language: str = Field(
        default='de',
        max_length=5,
        description="Response language"
    )

    @field_validator('question')
    @classmethod
    def validate_question(cls, v: str) -> str:
        """Validate and clean question"""
        v = v.strip()
        if len(v) < 3:
            raise ValueError('Question must be at least 3 characters')
        return v

    @field_validator('language')
    @classmethod
    def validate_language(cls, v: str) -> str:
        """Validate language code"""
        valid_languages = ['de', 'en', 'fr', 'es', 'it', 'pt', 'nl', 'pl', 'ru', 'zh']
        if v not in valid_languages:
            raise ValueError(f'Language must be one of: {", ".join(valid_languages)}')
        return v

    model_config = ConfigDict(from_attributes=True)


class AgentFeedbackRequest(BaseModel):
    """
    Request model for submitting feedback on agent response

    Example:
        >>> feedback = AgentFeedbackRequest(
        ...     query_id="uuid",
        ...     rating=5,
        ...     helpful=True,
        ...     feedback_text="Sehr hilfreiche Erklaerung!"
        ... )
    """
    query_id: str = Field(..., description="Query ID from agent response")
    rating: int = Field(
        ...,
        ge=1,
        le=5,
        description="Rating from 1 (poor) to 5 (excellent)"
    )
    helpful: bool = Field(default=True, description="Was the response helpful?")
    feedback_text: Optional[str] = Field(
        None,
        max_length=1000,
        description="Optional feedback text"
    )

    model_config = ConfigDict(from_attributes=True)


class AgentConfigUpdate(BaseModel):
    """
    Request model for updating agent configuration

    Example:
        >>> config = AgentConfigUpdate(
        ...     name="Python Tutor",
        ...     persona="friendly",
        ...     temperature=0.7
        ... )
    """
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    persona: Optional[AgentPersona] = None
    language: Optional[str] = Field(None, max_length=5)
    primary_provider: Optional[str] = None
    primary_model: Optional[str] = None
    fallback_provider: Optional[str] = None
    fallback_model: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=100, le=8000)

    @field_validator('primary_provider', 'fallback_provider')
    @classmethod
    def validate_provider(cls, v: Optional[str]) -> Optional[str]:
        """Validate AI provider"""
        if v is None:
            return v
        valid_providers = ['openai', 'anthropic', 'google', 'cohere', 'huggingface']
        if v not in valid_providers:
            raise ValueError(f'Provider must be one of: {", ".join(valid_providers)}')
        return v

    model_config = ConfigDict(from_attributes=True)


class KnowledgeCreateRequest(BaseModel):
    """
    Request model for manually adding knowledge to agent

    Example:
        >>> knowledge = KnowledgeCreateRequest(
        ...     question="Was ist eine Klasse?",
        ...     answer="Eine Klasse ist ein Bauplan fuer Objekte...",
        ...     scope_type="lesson",
        ...     scope_id="uuid"
        ... )
    """
    question: str = Field(
        ...,
        min_length=3,
        max_length=2000,
        description="Question text"
    )
    answer: str = Field(
        ...,
        min_length=10,
        max_length=10000,
        description="Answer text"
    )
    scope_type: ScopeType = Field(
        default=ScopeType.COURSE,
        description="Knowledge scope"
    )
    scope_id: Optional[str] = Field(
        None,
        description="Scope ID (course_id, chapter_id, or lesson_id)"
    )
    knowledge_type: KnowledgeType = Field(
        default=KnowledgeType.QA_PAIR,
        description="Type of knowledge entry"
    )

    model_config = ConfigDict(from_attributes=True)


class AgentWarmRequest(BaseModel):
    """
    Request model for warming up agent knowledge

    Example:
        >>> warm = AgentWarmRequest(tier=1)
    """
    tier: Optional[int] = Field(
        None,
        ge=1,
        le=3,
        description="Cache tier to warm (1=full, 2=template, 3=minimal)"
    )
    force: bool = Field(
        default=False,
        description="Force regeneration even if cache exists"
    )

    model_config = ConfigDict(from_attributes=True)


# =========================================================================
# Response Models
# =========================================================================

class AgentAskResponse(BaseModel):
    """
    Response model for agent ask endpoint

    Example:
        >>> response = AgentAskResponse(
        ...     answer="Polymorphismus bedeutet...",
        ...     source="cache_hit",
        ...     tokens_used=0,
        ...     tokens_saved=500
        ... )
    """
    answer: str = Field(..., description="Agent's answer")
    source: ResponseSource = Field(..., description="Where the answer came from")
    tokens_used: int = Field(default=0, ge=0, description="Tokens consumed")
    tokens_saved: int = Field(default=0, ge=0, description="Tokens saved by caching")
    was_offline_mode: bool = Field(default=False, description="Was this in offline mode?")
    agent_id: str = Field(..., description="Agent UUID")
    knowledge_id: Optional[str] = Field(None, description="Knowledge entry ID if from KB")
    query_id: Optional[str] = Field(None, description="Query log ID for feedback")
    offline_message: Optional[str] = Field(None, description="Message if offline")
    model: Optional[str] = Field(None, description="AI model used")
    provider: Optional[str] = Field(None, description="AI provider used")
    used_fallback: bool = Field(default=False, description="Was fallback provider used?")
    error: Optional[str] = Field(None, description="Error message if any")

    model_config = ConfigDict(from_attributes=True)


class AgentStatusResponse(BaseModel):
    """
    Response model for agent status endpoint

    Example:
        >>> status = AgentStatusResponse(
        ...     agent_id="uuid",
        ...     knowledge_status="ready",
        ...     cache_hit_rate=75.5,
        ...     tokens_saved=15000
        ... )
    """
    agent_id: Optional[str] = Field(None, description="Agent UUID")
    knowledge_status: str = Field(..., description="Knowledge base status")
    cache_hit_rate: float = Field(default=0, ge=0, le=100, description="Cache hit percentage")
    tokens_saved: int = Field(default=0, ge=0, description="Total tokens saved")
    total_queries: int = Field(default=0, ge=0, description="Total queries received")
    cache_hits: int = Field(default=0, ge=0, description="Number of cache hits")
    knowledge_entries: int = Field(default=0, ge=0, description="Knowledge base entries")
    last_warmed_at: Optional[datetime] = Field(None, description="Last warm-up timestamp")
    knowledge_version: Optional[int] = Field(None, description="Knowledge version")

    model_config = ConfigDict(from_attributes=True)


class AgentConfigResponse(BaseModel):
    """
    Response model for agent configuration

    Example:
        >>> config = AgentConfigResponse(
        ...     agent_id="uuid",
        ...     name="KI-Tutor",
        ...     persona="friendly",
        ...     language="de"
        ... )
    """
    agent_id: str = Field(..., description="Agent UUID")
    course_id: str = Field(..., description="Course UUID")
    name: str = Field(..., description="Agent name")
    persona: str = Field(..., description="Agent persona")
    language: str = Field(..., description="Response language")
    knowledge_status: str = Field(..., description="Knowledge status")
    primary_provider: str = Field(..., description="Primary AI provider")
    primary_model: str = Field(..., description="Primary AI model")
    fallback_provider: Optional[str] = Field(None, description="Fallback provider")
    fallback_model: Optional[str] = Field(None, description="Fallback model")
    temperature: float = Field(..., description="AI temperature")
    max_tokens: int = Field(..., description="Max response tokens")
    total_queries: int = Field(default=0, description="Total queries")
    cache_hits: int = Field(default=0, description="Cache hits")
    tokens_saved: int = Field(default=0, description="Tokens saved")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class KnowledgeEntryResponse(BaseModel):
    """
    Response model for knowledge entry

    Example:
        >>> entry = KnowledgeEntryResponse(
        ...     knowledge_id="uuid",
        ...     question_text="Was ist OOP?",
        ...     answer_text="OOP steht fuer...",
        ...     usage_count=42
        ... )
    """
    knowledge_id: str = Field(..., description="Knowledge UUID")
    agent_id: str = Field(..., description="Agent UUID")
    scope_type: str = Field(..., description="Scope type")
    scope_id: str = Field(..., description="Scope ID")
    knowledge_type: str = Field(..., description="Knowledge type")
    question_text: Optional[str] = Field(None, description="Question")
    answer_text: str = Field(..., description="Answer")
    source: str = Field(..., description="Source (auto_generated, user_interaction, manual)")
    quality_score: float = Field(..., description="Quality score (0-1)")
    usage_count: int = Field(default=0, description="Times used")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = ConfigDict(from_attributes=True)


class AgentWarmResponse(BaseModel):
    """
    Response model for agent warm-up job

    Example:
        >>> warm = AgentWarmResponse(
        ...     job_id="uuid",
        ...     status="running",
        ...     progress=45
        ... )
    """
    job_id: str = Field(..., description="Warm-up job UUID")
    agent_id: str = Field(..., description="Agent UUID")
    status: str = Field(..., description="Job status")
    job_type: str = Field(..., description="Job type")
    progress: int = Field(default=0, ge=0, le=100, description="Progress percentage")
    total_items: int = Field(default=0, description="Total items to process")
    completed_items: int = Field(default=0, description="Items completed")
    estimated_tokens: Optional[int] = Field(None, description="Estimated tokens")
    started_at: Optional[datetime] = Field(None, description="Start timestamp")

    model_config = ConfigDict(from_attributes=True)


# =========================================================================
# Organisation Extension Models
# =========================================================================

class OrgExtensionRequest(BaseModel):
    """
    Request model for organisation-specific agent extension

    Example:
        >>> ext = OrgExtensionRequest(
        ...     custom_persona="professional",
        ...     custom_terminology={"API": "Schnittstelle"},
        ...     blocked_topics=["Politik", "Religion"]
        ... )
    """
    custom_persona: Optional[AgentPersona] = None
    custom_language: Optional[str] = Field(None, max_length=5)
    custom_terminology: Optional[Dict[str, str]] = Field(
        None,
        description="Custom term translations"
    )
    custom_examples: Optional[List[str]] = Field(
        None,
        description="Custom examples to use"
    )
    additional_context: Optional[str] = Field(
        None,
        max_length=2000,
        description="Additional context for prompts"
    )
    blocked_topics: Optional[List[str]] = Field(
        None,
        description="Topics to avoid"
    )
    enabled: bool = Field(default=True, description="Is extension enabled?")

    model_config = ConfigDict(from_attributes=True)


class OrgExtensionResponse(BaseModel):
    """
    Response model for organisation extension
    """
    extension_id: str = Field(..., description="Extension UUID")
    agent_id: str = Field(..., description="Agent UUID")
    organization_id: str = Field(..., description="Organisation UUID")
    custom_persona: Optional[str] = None
    custom_language: Optional[str] = None
    custom_terminology: Optional[Dict[str, str]] = None
    custom_examples: Optional[List[str]] = None
    additional_context: Optional[str] = None
    blocked_topics: Optional[List[str]] = None
    enabled: bool = Field(default=True)
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update")

    model_config = ConfigDict(from_attributes=True)
