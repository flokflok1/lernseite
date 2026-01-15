"""
LernsystemX Theory Sheet Models

Pydantic models for chapter and lesson theory sheet management:
- TheorySheetResponse: API response for theory sheets
- TheorySheetCreate: Request model for creating theory sheets
- TheorySheetUpdate: Request model for updating theory sheets
- Support both chapter-level and lesson-level theories

Phase: AI Studio Implementation - Theory Sheets
"""

from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict


class TheorySheetResponse(BaseModel):
    """
    Theory sheet response model.

    Represents a theory sheet entity (chapter or lesson level).
    """
    theory_id: str = Field(..., description="Unique theory sheet ID (UUID)")
    parent_id: str = Field(..., description="Parent ID (chapter_id or lesson_id)")
    parent_type: Literal["chapter", "lesson"] = Field(
        ...,
        description="Type of parent (chapter or lesson)"
    )
    title: str = Field(..., description="Theory sheet title")
    content: str = Field(..., description="Theory sheet content (markdown or rich text)")
    order_index: Optional[int] = Field(
        None,
        description="Display order (for lesson theories)"
    )
    is_summary: Optional[bool] = Field(
        None,
        description="Is this a chapter summary? (only for chapter theories)"
    )
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "theory_id": "550e8400-e29b-41d4-a716-446655440000",
                "parent_id": "550e8400-e29b-41d4-a716-446655440001",
                "parent_type": "chapter",
                "title": "Kapitel 1 Zusammenfassung",
                "content": "# Zusammenfassung...",
                "order_index": None,
                "is_summary": True,
                "created_at": "2026-01-14T10:30:00Z",
                "updated_at": "2026-01-14T10:30:00Z"
            }
        }
    )


class TheorySheetCreate(BaseModel):
    """
    Model for creating new theory sheets.
    """
    parent_id: str = Field(..., description="Parent ID (chapter_id or lesson_id)")
    parent_type: Literal["chapter", "lesson"] = Field(
        ...,
        description="Type of parent (chapter or lesson)"
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Theory sheet title"
    )
    content: str = Field(
        ...,
        min_length=1,
        description="Theory sheet content"
    )
    order_index: Optional[int] = Field(
        None,
        description="Display order (for lesson theories, optional)"
    )
    is_summary: Optional[bool] = Field(
        False,
        description="Is this a chapter summary? (only for chapter theories)"
    )

    @field_validator('title')
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        """Ensure title is not just whitespace."""
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()

    @field_validator('content')
    @classmethod
    def content_not_blank(cls, v: str) -> str:
        """Ensure content is not just whitespace."""
        if not v.strip():
            raise ValueError('Content cannot be empty')
        return v.strip()

    @field_validator('parent_type')
    @classmethod
    def parent_type_valid(cls, v: str) -> str:
        """Ensure parent_type is valid."""
        if v not in ('chapter', 'lesson'):
            raise ValueError('parent_type must be "chapter" or "lesson"')
        return v


class TheorySheetUpdate(BaseModel):
    """
    Model for updating theory sheets.
    """
    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="New title"
    )
    content: Optional[str] = Field(
        None,
        min_length=1,
        description="New content"
    )
    order_index: Optional[int] = Field(
        None,
        description="New display order"
    )

    @field_validator('title')
    @classmethod
    def title_not_blank(cls, v: Optional[str]) -> Optional[str]:
        """Ensure title is not just whitespace if provided."""
        if v is not None and not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip() if v else None

    @field_validator('content')
    @classmethod
    def content_not_blank(cls, v: Optional[str]) -> Optional[str]:
        """Ensure content is not just whitespace if provided."""
        if v is not None and not v.strip():
            raise ValueError('Content cannot be empty')
        return v.strip() if v else None


class TheorySheetListItem(BaseModel):
    """
    Theory sheet list item (minimal response).
    """
    theory_id: str = Field(..., description="Unique theory sheet ID")
    title: str = Field(..., description="Theory sheet title")
    parent_type: Literal["chapter", "lesson"] = Field(..., description="Parent type")
    order_index: Optional[int] = Field(None, description="Display order")
    is_summary: Optional[bool] = Field(None, description="Is summary?")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = ConfigDict(from_attributes=True)
