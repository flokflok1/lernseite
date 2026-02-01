"""
LernsystemX Feature Configuration Models

Pydantic models for Enterprise Feature Configuration System:
- Feature flags configuration
- Role-based access control
- Tier-based limits
- Progressive rollout plans
- A/B testing
- Organization overrides
- Audit logging

Phase 1b - Repository Layer Integration
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum


# ==================== ENUMS ====================

class RoleCode(str, Enum):
    """Valid role codes"""
    ADMIN = "admin"
    CREATOR = "creator"
    TEACHER = "teacher"
    STUDENT = "student"
    PARENT = "parent"
    MODERATOR = "moderator"
    SUPPORT = "support"
    COMPANY = "company"
    SCHOOL = "school"


class TierCode(str, Enum):
    """Valid subscription tier codes"""
    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class RolloutStatus(str, Enum):
    """Rollout plan status"""
    PLANNED = "planned"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ROLLED_BACK = "rolled_back"


class ABTestStatus(str, Enum):
    """A/B test status"""
    PLANNED = "planned"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


class FeatureCategory(str, Enum):
    """Feature categories"""
    SOCIAL = "social"
    DISCOVERY = "discovery"
    MESSAGING = "messaging"
    ADVANCED_SOCIAL = "advanced_social"
    MODERATION = "moderation"
    ANALYTICS = "analytics"
    COMPLIANCE = "compliance"
    DRM = "drm"
    GDPR = "gdpr"
    SYSTEM = "system"


class AuditAction(str, Enum):
    """Audit log action types"""
    FEATURE_CREATED = "feature_created"
    FEATURE_ENABLED = "feature_enabled"
    FEATURE_DISABLED = "feature_disabled"
    ROLE_PERMISSION_ADDED = "role_permission_added"
    ROLE_PERMISSION_REMOVED = "role_permission_removed"
    ROLE_QUOTA_UPDATED = "role_quota_updated"
    TIER_LIMIT_ADDED = "tier_limit_added"
    TIER_LIMIT_REMOVED = "tier_limit_removed"
    TIER_LIMIT_UPDATED = "tier_limit_updated"
    ORG_OVERRIDE_ADDED = "org_override_added"
    ORG_OVERRIDE_REMOVED = "org_override_removed"
    ORG_OVERRIDE_UPDATED = "org_override_updated"
    ROLLOUT_STARTED = "rollout_started"
    ROLLOUT_PAUSED = "rollout_paused"
    ROLLOUT_COMPLETED = "rollout_completed"
    ROLLOUT_ROLLED_BACK = "rollout_rolled_back"
    ROLLOUT_PHASE_ADVANCED = "rollout_phase_advanced"
    ROLLOUT_PERCENTAGE_ADJUSTED = "rollout_percentage_adjusted"
    AB_TEST_STARTED = "ab_test_started"
    AB_TEST_ENDED = "ab_test_ended"
    AB_TEST_WINNER_ANNOUNCED = "ab_test_winner_announced"
    SEGMENT_ENABLED = "segment_enabled"
    SEGMENT_DISABLED = "segment_disabled"
    SEGMENT_UPDATED = "segment_updated"
    USER_OVERRIDE_ADDED = "user_override_added"
    USER_OVERRIDE_REMOVED = "user_override_removed"


# ==================== BASE MODELS ====================

class FeatureBase(BaseModel):
    """Base feature configuration model"""
    name: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z_]+$")
    description: Optional[str] = Field(None, max_length=500)
    category: FeatureCategory = Field(default=FeatureCategory.SYSTEM)
    is_enabled: bool = Field(default=False)


class FeatureCreate(FeatureBase):
    """Create new feature"""
    created_by: Optional[str] = Field(None, max_length=36)


class FeatureUpdate(BaseModel):
    """Update feature"""
    description: Optional[str] = Field(None, max_length=500)
    is_enabled: Optional[bool] = None
    updated_at: Optional[datetime] = None


class FeatureResponse(FeatureBase):
    """Feature response model"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ==================== ROLE MAPPING MODELS ====================

class FeatureRoleMappingBase(BaseModel):
    """Base role mapping model"""
    feature_name: str = Field(..., max_length=100)
    role_code: RoleCode
    is_enabled: bool = Field(default=False)
    max_usage_per_day: Optional[int] = Field(None, ge=0)
    max_creation_per_month: Optional[int] = Field(None, ge=0)
    priority_level: int = Field(default=0, ge=0)


class FeatureRoleMappingCreate(FeatureRoleMappingBase):
    """Create role mapping"""
    pass


class FeatureRoleMappingUpdate(BaseModel):
    """Update role mapping"""
    is_enabled: Optional[bool] = None
    max_usage_per_day: Optional[int] = Field(None, ge=0)
    max_creation_per_month: Optional[int] = Field(None, ge=0)
    priority_level: Optional[int] = Field(None, ge=0)


class FeatureRoleMappingResponse(FeatureRoleMappingBase):
    """Role mapping response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ==================== TIER LIMIT MODELS ====================

class FeatureTierLimitBase(BaseModel):
    """Base tier limit model"""
    feature_name: str = Field(..., max_length=100)
    tier_code: TierCode
    is_enabled: bool = Field(default=False)
    max_concurrent_usage: Optional[int] = Field(None, ge=0)
    max_monthly_quota: Optional[int] = Field(None, ge=0)
    max_per_day: Optional[int] = Field(None, ge=0)
    max_storage_gb: Optional[float] = Field(None, ge=0)


class FeatureTierLimitCreate(FeatureTierLimitBase):
    """Create tier limit"""
    pass


class FeatureTierLimitUpdate(BaseModel):
    """Update tier limit"""
    is_enabled: Optional[bool] = None
    max_concurrent_usage: Optional[int] = Field(None, ge=0)
    max_monthly_quota: Optional[int] = Field(None, ge=0)
    max_per_day: Optional[int] = Field(None, ge=0)
    max_storage_gb: Optional[float] = Field(None, ge=0)


class FeatureTierLimitResponse(FeatureTierLimitBase):
    """Tier limit response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ==================== ROLLOUT PLAN MODELS ====================

class FeatureRolloutPlanBase(BaseModel):
    """Base rollout plan model"""
    feature_name: str = Field(..., max_length=100)
    plan_name: str = Field(..., max_length=255)
    phase_1_percentage: int = Field(default=5, ge=0, le=100)
    phase_1_duration_hours: int = Field(default=12, ge=1)
    phase_2_percentage: int = Field(default=25, ge=0, le=100)
    phase_2_duration_hours: int = Field(default=24, ge=1)
    phase_3_percentage: int = Field(default=50, ge=0, le=100)
    phase_3_duration_hours: int = Field(default=48, ge=1)
    status: RolloutStatus = Field(default=RolloutStatus.PLANNED)
    target_roles: Optional[List[str]] = None
    target_tiers: Optional[List[str]] = None
    reason: Optional[str] = Field(None, max_length=500)


class FeatureRolloutPlanCreate(FeatureRolloutPlanBase):
    """Create rollout plan"""
    created_by: Optional[str] = Field(None, max_length=36)


class FeatureRolloutPlanUpdate(BaseModel):
    """Update rollout plan"""
    status: Optional[RolloutStatus] = None
    phase_1_percentage: Optional[int] = Field(None, ge=0, le=100)
    phase_2_percentage: Optional[int] = Field(None, ge=0, le=100)
    phase_3_percentage: Optional[int] = Field(None, ge=0, le=100)
    current_phase: Optional[int] = Field(None, ge=0, le=5)


class FeatureRolloutPlanResponse(FeatureRolloutPlanBase):
    """Rollout plan response"""
    id: int
    current_phase: int = Field(default=0)
    phase_1_start_at: Optional[datetime] = None
    phase_2_start_at: Optional[datetime] = None
    phase_3_start_at: Optional[datetime] = None
    phase_4_start_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ==================== A/B TEST MODELS ====================

class FeatureABTestBase(BaseModel):
    """Base A/B test model"""
    feature_name: str = Field(..., max_length=100)
    test_name: str = Field(..., max_length=255)
    variant_a_name: str = Field(..., max_length=100)
    variant_a_percentage: int = Field(default=50, ge=0, le=100)
    variant_a_config: Optional[Dict[str, Any]] = None
    variant_b_name: str = Field(..., max_length=100)
    variant_b_percentage: int = Field(default=50, ge=0, le=100)
    variant_b_config: Optional[Dict[str, Any]] = None
    target_roles: Optional[List[str]] = None
    target_tiers: Optional[List[str]] = None
    metrics_to_track: Optional[List[str]] = None
    planned_duration_days: int = Field(default=14, ge=1)
    status: ABTestStatus = Field(default=ABTestStatus.PLANNED)

    @field_validator('variant_a_percentage', 'variant_b_percentage')
    @classmethod
    def validate_percentages(cls, value):
        """Validate percentage is 0-100"""
        if not (0 <= value <= 100):
            raise ValueError('Percentage must be between 0 and 100')
        return value


class FeatureABTestCreate(FeatureABTestBase):
    """Create A/B test"""
    created_by: Optional[str] = Field(None, max_length=36)


class FeatureABTestUpdate(BaseModel):
    """Update A/B test"""
    status: Optional[ABTestStatus] = None
    variant_a_percentage: Optional[int] = Field(None, ge=0, le=100)
    variant_b_percentage: Optional[int] = Field(None, ge=0, le=100)
    winner: Optional[str] = Field(None, pattern=r"^[AB]$")


class FeatureABTestResponse(FeatureABTestBase):
    """A/B test response"""
    id: int
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    winner: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ==================== AUDIT LOG MODELS ====================

class FeatureAuditLogResponse(BaseModel):
    """Feature audit log response"""
    id: int
    feature_name: str
    action: AuditAction
    changed_field: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    change_details: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    organisation_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    estimated_affected_users: Optional[int] = None
    estimated_affected_organizations: Optional[int] = None
    rollback_possible: bool = Field(default=True)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==================== CACHE STATUS MODELS ====================

class FeatureCacheStatusResponse(BaseModel):
    """Feature cache status response"""
    feature_name: str
    last_config_change: datetime
    cache_invalidated_at: Optional[datetime] = None
    cache_ttl_seconds: int = Field(default=300)
    requires_redis_pubsub: bool = Field(default=True)

    model_config = ConfigDict(from_attributes=True)


# ==================== BULK OPERATIONS ====================

class FeatureConfigSnapshot(BaseModel):
    """Complete feature configuration snapshot"""
    feature_name: str
    feature_config: Dict[str, Any]
    role_mappings: Optional[List[Dict[str, Any]]] = None
    tier_limits: Optional[List[Dict[str, Any]]] = None
    org_overrides: Optional[List[Dict[str, Any]]] = None
    rollout_plan: Optional[Dict[str, Any]] = None
    ab_tests: Optional[List[Dict[str, Any]]] = None
    created_at: datetime
    reason: Optional[str] = None


class BulkFeatureEnableRequest(BaseModel):
    """Request to enable multiple features"""
    feature_names: List[str] = Field(..., min_items=1, max_items=50)
    reason: str = Field(..., max_length=500)
    target_roles: Optional[List[RoleCode]] = None
    target_tiers: Optional[List[TierCode]] = None


class BulkFeatureResponse(BaseModel):
    """Response for bulk operations"""
    success_count: int = 0
    failed_count: int = 0
    errors: List[Dict[str, Any]] = []
