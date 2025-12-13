"""
Pydantic Models for Course-Specific Prompts (Phase C1.4)

Provides validation and serialization for course-specific AI prompt overrides.
Allows administrators to customize AI generation behavior per course.

Phase: C1.4 - Prompt-System für Kurs/Modul/Prüfung
Date: 2025-01-23
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class PromptScope(str, Enum):
    """
    Scope of a prompt (which AI operation it applies to).
    """
    COURSE_GENERATION = "course_generation"
    MODULE_GENERATION = "module_generation"
    EXAM_GENERATION = "exam_generation"
    LESSON_GENERATION = "lesson_generation"
    QUIZ_GENERATION = "quiz_generation"


class CoursePromptBase(BaseModel):
    """
    Base model for course prompts (shared fields).
    """
    scope: PromptScope = Field(
        ...,
        description="Scope of this prompt (course_generation, module_generation, etc.)"
    )
    language: Optional[str] = Field(
        None,
        description="Optional language override (e.g., 'de', 'en'). If NULL, uses course default.",
        max_length=10
    )
    prompt_system: Optional[str] = Field(
        None,
        description="System prompt that defines AI role and behavior",
        max_length=5000
    )
    prompt_user_template: Optional[str] = Field(
        None,
        description="User prompt template with placeholders (e.g., '{{course_title}}')",
        max_length=10000
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (temperature, max_tokens, tags, etc.)"
    )
    is_active: bool = Field(
        True,
        description="Active flag. Set to False to disable without deleting."
    )

    @field_validator('prompt_system', 'prompt_user_template')
    @classmethod
    def validate_prompt_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """Ensure prompts are not empty strings (NULL is okay)."""
        if v is not None and v.strip() == '':
            raise ValueError("Prompt cannot be an empty string (use NULL instead)")
        return v

    @field_validator('language')
    @classmethod
    def validate_language_code(cls, v: Optional[str]) -> Optional[str]:
        """Validate language code format (2-5 characters, lowercase)."""
        if v is None:
            return None
        v = v.strip().lower()
        if not (2 <= len(v) <= 5) or not v.isalpha():
            raise ValueError("Language code must be 2-5 alphabetic characters (e.g., 'de', 'en-us')")
        return v


class CoursePromptCreateRequest(CoursePromptBase):
    """
    Request model for creating a new course prompt.
    """
    pass


class CoursePromptUpdateRequest(BaseModel):
    """
    Request model for updating an existing course prompt.
    All fields are optional (partial update).
    """
    language: Optional[str] = Field(
        None,
        description="Optional language override",
        max_length=10
    )
    prompt_system: Optional[str] = Field(
        None,
        description="System prompt",
        max_length=5000
    )
    prompt_user_template: Optional[str] = Field(
        None,
        description="User prompt template",
        max_length=10000
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Active flag"
    )

    @field_validator('prompt_system', 'prompt_user_template')
    @classmethod
    def validate_prompt_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """Ensure prompts are not empty strings."""
        if v is not None and v.strip() == '':
            raise ValueError("Prompt cannot be an empty string")
        return v


class CoursePromptResponse(CoursePromptBase):
    """
    Response model for course prompt (includes DB fields).
    """
    course_prompt_id: str = Field(
        ...,
        description="UUID of the course prompt"
    )
    course_id: str = Field(
        ...,
        description="UUID of the course this prompt belongs to"
    )
    created_by: Optional[str] = Field(
        None,
        description="UUID of user who created this prompt"
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when this prompt was created"
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when this prompt was last updated"
    )

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "course_prompt_id": "550e8400-e29b-41d4-a716-446655440000",
                "course_id": "123e4567-e89b-12d3-a456-426614174000",
                "scope": "module_generation",
                "language": "de",
                "prompt_system": "Du bist ein erfahrener IHK-Ausbilder...",
                "prompt_user_template": "Erstelle ein Modul über {{topic}} für den Kurs {{course_title}}",
                "metadata": {"temperature": 0.7, "max_tokens": 2000},
                "is_active": True,
                "created_by": "789e0123-e45b-67c8-d901-234567890abc",
                "created_at": "2025-01-23T10:30:00Z",
                "updated_at": "2025-01-23T10:30:00Z"
            }
        }
    }


class CoursePromptListItem(BaseModel):
    """
    Simplified model for listing course prompts (less detail).
    """
    course_prompt_id: str
    course_id: str
    scope: PromptScope
    language: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CoursePromptResolveRequest(BaseModel):
    """
    Request model for resolving a prompt (Prompt-Resolver).

    Used by AI services to request the appropriate prompt for a specific operation.
    """
    course_id: str = Field(
        ...,
        description="UUID of the course"
    )
    scope: PromptScope = Field(
        ...,
        description="Scope of the prompt to resolve"
    )
    language: Optional[str] = Field(
        None,
        description="Preferred language (if not specified, uses course default)"
    )


class CoursePromptResolveResponse(BaseModel):
    """
    Response model for prompt resolution.

    Returns the resolved prompt (either course-specific or global fallback).
    """
    source: str = Field(
        ...,
        description="Source of the prompt: 'course_specific', 'global', 'hardcoded_fallback'"
    )
    scope: PromptScope = Field(
        ...,
        description="Scope of the resolved prompt"
    )
    language: Optional[str] = Field(
        None,
        description="Language of the resolved prompt"
    )
    prompt_system: Optional[str] = Field(
        None,
        description="Resolved system prompt"
    )
    prompt_user_template: Optional[str] = Field(
        None,
        description="Resolved user prompt template"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata from the resolved prompt"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "source": "course_specific",
                "scope": "module_generation",
                "language": "de",
                "prompt_system": "Du bist ein erfahrener IHK-Ausbilder...",
                "prompt_user_template": "Erstelle ein Modul über {{topic}}",
                "metadata": {"temperature": 0.7, "max_tokens": 2000}
            }
        }
    }


class BulkResetRequest(BaseModel):
    """
    Request model for bulk resetting course prompts to global defaults.
    """
    scopes: Optional[List[PromptScope]] = Field(
        None,
        description="Optional list of scopes to reset. If None, resets all scopes."
    )
    confirm: bool = Field(
        False,
        description="Confirmation flag (must be True to proceed)"
    )

    @field_validator('confirm')
    @classmethod
    def validate_confirm(cls, v: bool) -> bool:
        """Ensure confirmation is True."""
        if not v:
            raise ValueError("confirm must be True to reset prompts")
        return v
