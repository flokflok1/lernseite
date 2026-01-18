"""
LernsystemX Course Publishing Models

Pydantic models for course publishing workflow:
- CoursePublishingResponse: API response for publishing status
- CoursePublishingStateChange: Request model for state transitions
- CoursePublishingCreate: Request model for initial publishing record

Publishing Workflow: draft → submitted → approved/rejected → published → community visibility

Phase: AI Editor Implementation - Publishing System
"""

from typing import Optional, Literal
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, ConfigDict


PublishingStatus = Literal["draft", "submitted", "approved", "published", "rejected"]
PublishingVisibility = Literal["private", "community", "public"]


class CoursePublishingResponse(BaseModel):
    """
    Course publishing status response model.

    Tracks the complete publishing workflow state.
    """
    publish_id: str = Field(..., description="Unique publishing record ID (UUID)")
    course_id: str = Field(..., description="Associated course ID (UUID)")
    status: PublishingStatus = Field(
        ...,
        description="Publishing status (draft, submitted, approved, published, rejected)"
    )
    visibility: PublishingVisibility = Field(
        ...,
        description="Visibility level (private, community, public)"
    )
    submission_date: Optional[datetime] = Field(
        None,
        description="Date when submitted for review"
    )
    moderator_id: Optional[str] = Field(
        None,
        description="ID of moderator who reviewed this course"
    )
    moderation_notes: Optional[str] = Field(
        None,
        description="Notes from moderator (rejection reasons, feedback, etc.)"
    )
    moderation_ai_score: Optional[Decimal] = Field(
        None,
        description="AI moderation score (0.00-1.00, higher is better)"
    )
    published_date: Optional[datetime] = Field(
        None,
        description="Date when published"
    )
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "publish_id": "550e8400-e29b-41d4-a716-446655440000",
                "course_id": "550e8400-e29b-41d4-a716-446655440001",
                "status": "published",
                "visibility": "community",
                "submission_date": "2026-01-10T14:00:00Z",
                "moderator_id": "550e8400-e29b-41d4-a716-446655440002",
                "moderation_notes": "Excellent course content",
                "moderation_ai_score": 0.92,
                "published_date": "2026-01-12T10:00:00Z",
                "created_at": "2026-01-10T14:00:00Z",
                "updated_at": "2026-01-12T10:00:00Z"
            }
        }
    )


class CoursePublishingCreate(BaseModel):
    """
    Model for creating initial publishing record.
    """
    course_id: str = Field(..., description="Course ID (UUID)")
    status: PublishingStatus = Field(
        default="draft",
        description="Initial status (default: draft)"
    )
    visibility: PublishingVisibility = Field(
        default="private",
        description="Initial visibility (default: private)"
    )

    @field_validator('status')
    @classmethod
    def status_valid(cls, v: str) -> str:
        """Validate status."""
        valid = ("draft", "submitted", "approved", "published", "rejected")
        if v not in valid:
            raise ValueError(f'status must be one of: {", ".join(valid)}')
        return v

    @field_validator('visibility')
    @classmethod
    def visibility_valid(cls, v: str) -> str:
        """Validate visibility."""
        valid = ("private", "community", "public")
        if v not in valid:
            raise ValueError(f'visibility must be one of: {", ".join(valid)}')
        return v


class CoursePublishingStateChange(BaseModel):
    """
    Model for changing publishing state (submit, approve, reject, etc.).
    """
    new_status: PublishingStatus = Field(
        ...,
        description="New publishing status"
    )
    new_visibility: Optional[PublishingVisibility] = Field(
        None,
        description="New visibility (optional, only if changing)"
    )
    moderation_notes: Optional[str] = Field(
        None,
        description="Notes from moderator (e.g., rejection reason, feedback)"
    )

    @field_validator('new_status')
    @classmethod
    def status_valid(cls, v: str) -> str:
        """Validate status."""
        valid = ("draft", "submitted", "approved", "published", "rejected")
        if v not in valid:
            raise ValueError(f'new_status must be one of: {", ".join(valid)}')
        return v

    @field_validator('new_visibility')
    @classmethod
    def visibility_valid(cls, v: Optional[str]) -> Optional[str]:
        """Validate visibility if provided."""
        if v is not None:
            valid = ("private", "community", "public")
            if v not in valid:
                raise ValueError(f'new_visibility must be one of: {", ".join(valid)}')
        return v


class CoursePublishingListItem(BaseModel):
    """
    Course publishing list item (minimal response).
    """
    publish_id: str = Field(..., description="Publishing record ID")
    course_id: str = Field(..., description="Course ID")
    status: PublishingStatus = Field(..., description="Current status")
    visibility: PublishingVisibility = Field(..., description="Current visibility")
    submission_date: Optional[datetime] = Field(None, description="Submission date")
    moderation_ai_score: Optional[Decimal] = Field(None, description="AI score")

    model_config = ConfigDict(from_attributes=True)
