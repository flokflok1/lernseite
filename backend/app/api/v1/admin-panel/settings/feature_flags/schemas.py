"""
Feature Flags API - Pydantic Validation Schemas

Validates all Feature Flags API request/response data:
- FeatureFlagCreateSchema: Create new flag
- FeatureFlagUpdateSchema: Update flag
- RolloutPlanSchema: Rollout plan management
- FeatureFlagResponseSchema: API response format
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum


class FeatureCategoryEnum(str, Enum):
    """Valid feature flag categories."""
    AI_FEATURES = "ai_features"
    CONTENT_MANAGEMENT = "content_management"
    SOCIAL_FEATURES = "social_features"
    GAMIFICATION = "gamification"
    COMPLIANCE = "compliance"
    PERFORMANCE = "performance"
    EXPERIMENTAL = "experimental"
    OTHER = "other"


class RolloutStatusEnum(str, Enum):
    """Valid rollout statuses."""
    NOT_ROLLING_OUT = "not_rolling_out"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAUSED = "paused"
    ROLLED_BACK = "rolled_back"


class FeatureFlagCreateSchema(BaseModel):
    """
    Schema for creating a new feature flag.

    Validates:
    - feature_code: Unique identifier (must be lowercase, alphanumeric + underscores)
    - feature_name: Display name (1-100 chars)
    - description: Optional description
    - category: Feature category
    - enabled: Initial state (default: false)
    - rollout_percentage: Initial percentage (0-100)
    - target_percentage: Target rollout (0-100)
    """

    feature_code: str = Field(..., min_length=3, max_length=50,
                             pattern=r'^[a-z0-9_]+$',
                             description="Unique feature code")
    feature_name: str = Field(..., min_length=1, max_length=100,
                             description="Display name")
    description: Optional[str] = Field(None, max_length=500,
                                      description="Feature description")
    category: FeatureCategoryEnum = Field(..., description="Feature category")
    enabled: bool = Field(default=False, description="Initial state")
    rollout_percentage: int = Field(default=0, ge=0, le=100,
                                   description="Initial rollout %")
    target_percentage: Optional[int] = Field(None, ge=0, le=100,
                                            description="Target rollout %")

    class Config:
        use_enum_values = True

    @validator('feature_code')
    def validate_feature_code(cls, v):
        """Ensure feature code is unique pattern."""
        if v.startswith('_') or v.endswith('_'):
            raise ValueError('Feature code cannot start or end with underscore')
        return v

    @validator('target_percentage')
    def validate_target_percentage(cls, v, values):
        """Ensure target >= initial rollout."""
        if v is not None and 'rollout_percentage' in values:
            if v < values['rollout_percentage']:
                raise ValueError('Target percentage must be >= initial rollout percentage')
        return v


class FeatureFlagUpdateSchema(BaseModel):
    """
    Schema for updating a feature flag.

    All fields are optional - only specified fields are updated.

    Validates:
    - feature_name: Display name
    - description: Description
    - category: Category
    - target_percentage: Target rollout
    """

    feature_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    category: Optional[FeatureCategoryEnum] = None
    target_percentage: Optional[int] = Field(None, ge=0, le=100)

    class Config:
        use_enum_values = True


class RolloutPlanSchema(BaseModel):
    """
    Schema for rollout plan management.

    Defines progressive rollout schedule:
    - start_date: When rollout begins
    - target_percentage: Final rollout %
    - estimated_end_date: Expected completion
    - rollout_status: Current status
    """

    flag_id: str = Field(..., description="Feature flag ID")
    start_date: datetime = Field(..., description="Rollout start")
    target_percentage: int = Field(..., ge=0, le=100,
                                  description="Target rollout %")
    estimated_end_date: Optional[datetime] = Field(None,
                                                  description="Expected end")
    rollout_status: RolloutStatusEnum = Field(default="not_rolling_out",
                                            description="Rollout status")

    class Config:
        use_enum_values = True

    @validator('estimated_end_date')
    def validate_end_date(cls, v, values):
        """Ensure end_date > start_date."""
        if v is not None and 'start_date' in values:
            if v <= values['start_date']:
                raise ValueError('End date must be after start date')
        return v


class FeatureFlagResponseSchema(BaseModel):
    """
    Schema for API response - single feature flag.

    Includes:
    - Flag details (id, code, name, category)
    - Status information (enabled, rollout %)
    - Rollout plan data
    - Timestamps (created, updated)
    """

    id: str
    feature_code: str
    feature_name: str
    description: Optional[str]
    category: str
    is_active: bool
    rollout_percentage: int
    target_percentage: Optional[int]
    rollout_status: str
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[str]

    class Config:
        from_attributes = True
