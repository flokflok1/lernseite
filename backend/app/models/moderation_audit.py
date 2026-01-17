"""
LernsystemX Moderation Audit Models

Pydantic models for moderation audit trail:
- ModerationAuditResponse: API response for audit records
- ModerationAuditCreate: Request model for creating audit entries
- Immutable audit trail (no updates or deletions)

Tracks all moderation actions for compliance, transparency, and accountability.

Phase: AI Editor Implementation - KI Moderation
"""

from typing import Optional, Literal, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict


ModerationAction = Literal[
    "submitted",
    "reviewed",
    "approved",
    "rejected",
    "revision_requested",
    "ai_analyzed"
]


class ModerationAuditResponse(BaseModel):
    """
    Moderation audit log entry response model.

    Immutable record of all moderation actions taken on courses.
    """
    audit_id: str = Field(..., description="Unique audit record ID (UUID)")
    course_id: str = Field(..., description="Associated course ID (UUID)")
    moderator_id: Optional[str] = Field(
        None,
        description="ID of human moderator who took action (null for AI actions)"
    )
    action: ModerationAction = Field(
        ...,
        description="Action taken (submitted, reviewed, approved, rejected, revision_requested, ai_analyzed)"
    )
    notes: Optional[str] = Field(
        None,
        description="Notes about the action (feedback, rejection reason, etc.)"
    )
    ai_analysis: Optional[Dict[str, Any]] = Field(
        None,
        description="AI analysis results (JSONB): {quality, appropriateness, originality, learning_methods, overall_score, issues, recommendations}"
    )
    created_at: datetime = Field(..., description="When action was taken")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "audit_id": "550e8400-e29b-41d4-a716-446655440000",
                "course_id": "550e8400-e29b-41d4-a716-446655440001",
                "moderator_id": "550e8400-e29b-41d4-a716-446655440002",
                "action": "approved",
                "notes": "Great content, engaging teaching style",
                "ai_analysis": None,
                "created_at": "2026-01-12T10:30:00Z"
            }
        }
    )


class AIAnalysisData(BaseModel):
    """
    AI moderation analysis results (JSONB structure).
    """
    quality: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Content quality score (0.0-1.0)"
    )
    appropriateness: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Content appropriateness for target audience"
    )
    originality: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Content originality/uniqueness"
    )
    learning_methods: Optional[str] = Field(
        None,
        description="Assessment of learning methods used"
    )
    overall_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall KI assessment score"
    )
    issues: Optional[list[str]] = Field(
        None,
        description="List of detected issues or concerns"
    )
    recommendations: Optional[list[str]] = Field(
        None,
        description="List of recommendations for improvement"
    )

    model_config = ConfigDict(from_attributes=True)


class ModerationAuditCreate(BaseModel):
    """
    Model for creating moderation audit entries.
    """
    course_id: str = Field(..., description="Course ID (UUID)")
    moderator_id: Optional[str] = Field(
        None,
        description="ID of human moderator (null for AI-only actions)"
    )
    action: ModerationAction = Field(
        ...,
        description="Action taken"
    )
    notes: Optional[str] = Field(
        None,
        max_length=2000,
        description="Notes or feedback (max 2000 chars)"
    )
    ai_analysis: Optional[Dict[str, Any]] = Field(
        None,
        description="AI analysis results (optional, for ai_analyzed action)"
    )

    @field_validator('action')
    @classmethod
    def action_valid(cls, v: str) -> str:
        """Validate action type."""
        valid = (
            "submitted",
            "reviewed",
            "approved",
            "rejected",
            "revision_requested",
            "ai_analyzed"
        )
        if v not in valid:
            raise ValueError(f'action must be one of: {", ".join(valid)}')
        return v

    @field_validator('notes')
    @classmethod
    def notes_not_blank(cls, v: Optional[str]) -> Optional[str]:
        """Ensure notes is not just whitespace if provided."""
        if v is not None and not v.strip():
            raise ValueError('notes cannot be empty string')
        return v.strip() if v else None


class ModerationAuditFilter(BaseModel):
    """
    Model for filtering audit records.
    """
    course_id: Optional[str] = Field(None, description="Filter by course ID")
    moderator_id: Optional[str] = Field(None, description="Filter by moderator ID")
    action: Optional[ModerationAction] = Field(None, description="Filter by action type")
    start_date: Optional[datetime] = Field(None, description="Filter records after this date")
    end_date: Optional[datetime] = Field(None, description="Filter records before this date")
    limit: int = Field(default=100, ge=1, le=1000, description="Max results (1-1000)")
    offset: int = Field(default=0, ge=0, description="Skip N records")


class ModerationAuditListItem(BaseModel):
    """
    Moderation audit list item (minimal response).
    """
    audit_id: str = Field(..., description="Audit record ID")
    course_id: str = Field(..., description="Course ID")
    moderator_id: Optional[str] = Field(None, description="Moderator ID")
    action: ModerationAction = Field(..., description="Action taken")
    created_at: datetime = Field(..., description="When action was taken")

    model_config = ConfigDict(from_attributes=True)
