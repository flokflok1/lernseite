"""
LernsystemX Panel API - System Features Schemas

Pydantic models for system feature configuration endpoints.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class SystemFeatureUpdate(BaseModel):
    """Schema for updating a system feature (partial update)."""

    feature_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Display name"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Feature description"
    )
    active: Optional[bool] = Field(
        None,
        description="Whether feature is active"
    )
    config: Optional[Dict[str, Any]] = Field(
        None,
        description="Feature configuration"
    )
    icon: Optional[str] = Field(
        None,
        max_length=50,
        description="Icon identifier"
    )

    class Config:
        schema_extra = {
            "example": {
                "feature_name": "Updated Whiteboard Engine",
                "active": True,
                "config": {"max_canvas_size": 4096}
            }
        }


class SystemFeatureResponse(BaseModel):
    """Response schema for a single system feature."""

    feature_id: int
    feature_code: str
    feature_name: str
    description: Optional[str]
    category: str
    requires_infrastructure: bool
    requires_external_service: bool
    active: bool
    config: Dict[str, Any]
    icon: Optional[str]
    former_lm_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "feature_id": 1,
                "feature_code": "whiteboard_engine",
                "feature_name": "Whiteboard-Engine",
                "description": "Interactive whiteboard with AI recognition",
                "category": "interactive_tools",
                "requires_infrastructure": True,
                "requires_external_service": True,
                "active": True,
                "config": {},
                "icon": "pencil-ruler",
                "former_lm_id": 5,
                "created_at": "2026-01-01T00:00:00Z",
                "updated_at": "2026-01-01T00:00:00Z"
            }
        }


class SystemFeatureListResponse(BaseModel):
    """Response schema for system feature list."""

    data: List[SystemFeatureResponse]
    total: int
    categories: List[str]

    class Config:
        schema_extra = {
            "example": {
                "data": [],
                "total": 25,
                "categories": [
                    "audio",
                    "collaboration",
                    "exam_systems",
                    "gamification",
                    "interactive_tools",
                    "it_environments",
                    "learning_paths",
                    "meta_features",
                    "tutor",
                    "visualization"
                ]
            }
        }
