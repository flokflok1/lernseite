"""
LernsystemX Panel API - Runner Modes Schemas

Pydantic models for runner mode configuration endpoints.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


class FeatureRelationship(str, Enum):
    """Feature relationship types for runner modes."""
    REQUIRED = "required"
    OPTIONAL = "optional"
    EXCLUDED = "excluded"


# =============================================================================
# Runner Modes
# =============================================================================

class RunnerModeCreate(BaseModel):
    """Schema for creating a new runner mode."""

    mode_code: str = Field(
        ...,
        min_length=2,
        max_length=50,
        pattern=r'^[a-z][a-z0-9_]*$',
        description="Unique code (lowercase, underscores allowed)"
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Display name"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Mode description"
    )
    config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Mode configuration JSONB"
    )
    features_included: List[str] = Field(
        default_factory=list,
        description="Default feature codes to include"
    )
    time_limited: bool = Field(
        False,
        description="Whether mode has time limits"
    )
    graded: bool = Field(
        False,
        description="Whether mode is graded"
    )
    allows_hints: bool = Field(
        True,
        description="Whether hints are allowed"
    )
    allows_skip: bool = Field(
        True,
        description="Whether skipping items is allowed"
    )
    display_order: int = Field(
        0,
        ge=0,
        description="Display order (lower = first)"
    )

    @validator('mode_code')
    def validate_mode_code(cls, v):
        reserved = ['system', 'admin', 'test', 'debug']
        if v.lower() in reserved:
            raise ValueError(f"'{v}' is a reserved mode code")
        return v.lower()

    class Config:
        json_schema_extra = {
            "example": {
                "mode_code": "practice",
                "name": "Practice Mode",
                "description": "Untimed practice with hints enabled",
                "time_limited": False,
                "graded": False,
                "allows_hints": True,
                "allows_skip": True
            }
        }


class RunnerModeUpdate(BaseModel):
    """Schema for updating a runner mode (partial update)."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    config: Optional[Dict[str, Any]] = None
    features_included: Optional[List[str]] = None
    time_limited: Optional[bool] = None
    graded: Optional[bool] = None
    allows_hints: Optional[bool] = None
    allows_skip: Optional[bool] = None
    display_order: Optional[int] = Field(None, ge=0)
    active: Optional[bool] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Updated Practice Mode",
                "allows_hints": False
            }
        }


class RunnerModeResponse(BaseModel):
    """Response schema for a single runner mode."""

    mode_id: int
    mode_code: str
    name: str
    description: Optional[str]
    config: Dict[str, Any]
    features_included: List[str]
    time_limited: bool
    graded: bool
    allows_hints: bool
    allows_skip: bool
    display_order: int
    active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RunnerModeListResponse(BaseModel):
    """Response schema for runner mode list."""

    data: List[RunnerModeResponse]
    total: int


# =============================================================================
# Feature Mappings
# =============================================================================

class FeatureMappingItem(BaseModel):
    """Single feature mapping item."""

    feature_id: int = Field(..., description="Feature ID")
    relationship: FeatureRelationship = Field(
        FeatureRelationship.OPTIONAL,
        description="Feature relationship type"
    )
    config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Feature config override"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "feature_id": 3,
                "relationship": "required",
                "config": {}
            }
        }


class FeatureMappingRequest(BaseModel):
    """Request schema for setting feature mappings."""

    features: List[FeatureMappingItem] = Field(
        ...,
        description="List of feature mappings"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "features": [
                    {"feature_id": 3, "relationship": "required", "config": {}},
                    {"feature_id": 7, "relationship": "optional", "config": {}},
                    {"feature_id": 12, "relationship": "excluded", "config": {}}
                ]
            }
        }


class FeatureMappingResponse(BaseModel):
    """Response schema for feature mappings."""

    mode_id: int
    mode_code: str
    features: List[Dict[str, Any]]

    class Config:
        json_schema_extra = {
            "example": {
                "mode_id": 1,
                "mode_code": "exam",
                "features": [
                    {
                        "feature_id": 3,
                        "feature_code": "timer_wrapper",
                        "feature_name": "Timer/Zeitlimit-Feature",
                        "relationship": "required",
                        "config": {}
                    }
                ]
            }
        }


# =============================================================================
# LM Type Mode Compatibility
# =============================================================================

class LMTypeModeItem(BaseModel):
    """Single LM type mode compatibility item."""

    mode_id: int = Field(..., description="Runner mode ID")
    is_compatible: bool = Field(True, description="Whether mode is compatible")
    is_default: bool = Field(False, description="Whether this is the default mode")
    config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Mode config override for this LM type"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "mode_id": 2,
                "is_compatible": True,
                "is_default": False,
                "config": {}
            }
        }


class LMTypeModeRequest(BaseModel):
    """Request schema for setting LM type mode compatibility."""

    modes: List[LMTypeModeItem] = Field(
        ...,
        description="List of mode compatibilities"
    )

    @validator('modes')
    def validate_single_default(cls, v):
        defaults = [m for m in v if m.is_default]
        if len(defaults) > 1:
            raise ValueError("Only one mode can be marked as default")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "modes": [
                    {"mode_id": 1, "is_compatible": True, "is_default": True},
                    {"mode_id": 2, "is_compatible": True, "is_default": False},
                    {"mode_id": 3, "is_compatible": False, "is_default": False}
                ]
            }
        }


class LMTypeModeResponse(BaseModel):
    """Response schema for LM type mode compatibilities."""

    method_type: int
    modes: List[Dict[str, Any]]

    class Config:
        json_schema_extra = {
            "example": {
                "method_type": 5,
                "modes": [
                    {
                        "mode_id": 1,
                        "mode_code": "standard",
                        "mode_name": "Standard Mode",
                        "is_compatible": True,
                        "is_default": True
                    }
                ]
            }
        }


# =============================================================================
# Aliases for API Blueprint imports
# =============================================================================

# Alias for feature mapping set (used in PUT endpoint)
FeatureMappingSet = FeatureMappingRequest

# Alias for LM type mode compatibility set (used in PUT endpoint)
LMTypeModeCompatibilitySet = LMTypeModeRequest
