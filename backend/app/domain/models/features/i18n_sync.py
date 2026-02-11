"""
LernsystemX i18n Sync Models

Pydantic models for i18n synchronization between frontend JSON and database:
- Sync operation management (MANUAL vs AUTO modes)
- Per-key comparison and resolution tracking
- Conflict detection and resolution
- Database snapshot and rollback

ISO 9001:2015 compliant - i18n data synchronization standards
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from uuid import UUID


# ============================================================================
# ENUMS
# ============================================================================

class SyncMode(str, Enum):
    """Sync operation modes"""
    MANUAL = 'MANUAL'  # Admin selects actions per-key
    AUTO = 'AUTO'      # System decides based on rules


class SyncStatus(str, Enum):
    """Sync operation status"""
    SCANNING = 'SCANNING'       # Comparing frontend JSON vs DB
    PENDING = 'PENDING'         # Ready to apply (waiting for decisions in MANUAL)
    APPLYING = 'APPLYING'       # Currently applying changes
    COMPLETED = 'COMPLETED'     # Successfully completed
    FAILED = 'FAILED'           # Operation failed with errors
    ROLLED_BACK = 'ROLLED_BACK' # Reverted to previous state


class ResolutionAction(str, Enum):
    """Actions for individual keys"""
    ADD = 'ADD'           # New key (in JSON, not in DB)
    UPDATE = 'UPDATE'     # Key exists but value changed
    DELETE = 'DELETE'     # Key in DB but not in JSON
    SKIP = 'SKIP'         # Ignore this key
    CONFLICT = 'CONFLICT' # Requires manual decision


class ResolutionStatus(str, Enum):
    """Status of per-key resolution"""
    PENDING = 'PENDING'                # Awaiting decision (MANUAL mode)
    RESOLVED = 'RESOLVED'              # Decision made (MANUAL)
    MANUAL_OVERRIDE = 'MANUAL_OVERRIDE' # Admin edited the value
    FAILED = 'FAILED'                  # Error during apply


class ConflictReason(str, Enum):
    """Reasons for conflicts"""
    VALUE_CHANGED = 'VALUE_CHANGED'
    MANUAL_EDIT = 'MANUAL_EDIT'
    LANGUAGE_MISMATCH = 'LANGUAGE_MISMATCH'
    ENCODING_ISSUE = 'ENCODING_ISSUE'


class ChangeMagnitude(str, Enum):
    """Magnitude of value changes"""
    MINOR = 'MINOR'         # <5% difference
    MODERATE = 'MODERATE'   # 5-10% difference
    MAJOR = 'MAJOR'         # >10% difference


# ============================================================================
# SYNC HISTORY MODELS
# ============================================================================

class SyncHistoryBase(BaseModel):
    """Base sync history model"""
    sync_mode: SyncMode = Field(..., description="MANUAL or AUTO mode")
    sync_status: SyncStatus = Field(..., description="Current sync status")
    languages_affected: List[str] = Field(
        default_factory=list,
        description="Language codes (de, en, pl)"
    )

    model_config = ConfigDict(from_attributes=True)


class SyncHistoryCreateRequest(SyncHistoryBase):
    """Request to initiate sync scan"""
    pass


class SyncHistoryApplyRequest(BaseModel):
    """Request to apply sync changes"""
    sync_id: UUID = Field(..., description="Sync ID to apply")
    force: bool = Field(False, description="Force apply even with conflicts")

    model_config = ConfigDict(from_attributes=True)


class SyncHistoryRollbackRequest(BaseModel):
    """Request to rollback sync"""
    sync_id: UUID = Field(..., description="Sync ID to rollback")
    reason: str = Field("", description="Reason for rollback")

    model_config = ConfigDict(from_attributes=True)


class SyncHistoryResponse(SyncHistoryBase):
    """Sync history response"""
    sync_id: UUID = Field(..., description="Unique sync identifier")

    # Statistics
    total_keys: int = Field(0, description="Total keys processed")
    keys_added: int = Field(0, description="New keys added")
    keys_updated: int = Field(0, description="Keys updated")
    keys_deleted: int = Field(0, description="Keys deleted")
    keys_skipped: int = Field(0, description="Keys skipped")
    keys_conflicted: int = Field(0, description="Keys with conflicts")

    # Timeline
    scan_started_at: Optional[datetime] = None
    scan_completed_at: Optional[datetime] = None
    apply_started_at: Optional[datetime] = None
    apply_completed_at: Optional[datetime] = None

    # Metadata
    initiated_by: Optional[UUID] = None
    completed_by: Optional[UUID] = None
    error_message: Optional[str] = None

    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class SyncHistorySummary(BaseModel):
    """Compact sync history summary"""
    sync_id: UUID
    sync_mode: SyncMode
    sync_status: SyncStatus
    total_changes: int = Field(description="keys_added + keys_updated + keys_deleted")
    conflicts: int = Field(description="keys_conflicted")
    created_at: datetime
    initiated_by: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)


class SyncHistoryListResponse(BaseModel):
    """Response for sync history list"""
    success: bool = True
    syncs: List[SyncHistorySummary]
    total: int
    limit: int
    offset: int

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# SYNC DETAILS MODELS (Per-Key Tracking)
# ============================================================================

class KeyComparison(BaseModel):
    """Comparison data for a single key"""
    namespace_code: str = Field(..., description="Namespace (e.g., 'admin', 'common')")
    key_path: str = Field(..., description="Key path (e.g., 'users.title')")
    language: str = Field(..., description="Language code (de, en, pl)")

    frontend_value: Optional[str] = Field(None, description="Value from JSON")
    database_value: Optional[str] = Field(None, description="Current DB value")
    similarity_score: float = Field(1.0, description="Text similarity 0-1")

    is_new: bool = Field(False, description="Key doesn't exist in DB")
    is_changed: bool = Field(False, description="Value differs from DB")
    is_deleted: bool = Field(False, description="In DB but not in JSON")
    change_magnitude: Optional[ChangeMagnitude] = None

    model_config = ConfigDict(from_attributes=True)


class SyncDetailBase(KeyComparison):
    """Base sync detail model"""
    action: ResolutionAction = Field(..., description="Planned action")
    resolution_status: ResolutionStatus = Field(..., description="Resolution status")
    conflict_reason: Optional[str] = None
    manual_resolution_value: Optional[str] = Field(None, description="Admin-edited value")


class SyncDetailResponse(SyncDetailBase):
    """Sync detail response"""
    detail_id: UUID
    sync_id: UUID
    resolved_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class SyncDetailUpdateRequest(BaseModel):
    """Request to resolve a single key"""
    action: ResolutionAction = Field(..., description="Action to take")
    manual_value: Optional[str] = Field(None, description="Manual override value")

    model_config = ConfigDict(from_attributes=True)


class SyncDetailsListResponse(BaseModel):
    """Response for sync details list"""
    success: bool = True
    sync_id: UUID
    details: List[SyncDetailResponse]
    total: int
    conflicts_count: int = Field(description="Number of conflicts")
    pending_count: int = Field(description="Number of pending resolutions")
    limit: int
    offset: int

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# SCAN RESULTS MODELS
# ============================================================================

class ScanSummary(BaseModel):
    """Summary of scan results"""
    scan_status: str = Field("COMPLETED", description="COMPLETED or FAILED")
    total_keys: int = Field(0, description="Total keys compared")
    new_keys: int = Field(0, description="Keys only in JSON")
    changed_keys: int = Field(0, description="Keys with different values")
    deleted_keys: int = Field(0, description="Keys only in DB")
    conflicted_keys: int = Field(0, description="Keys with conflicts")
    languages_affected: List[str] = Field(default_factory=list)
    scan_duration_ms: int = Field(0, description="Scan time in milliseconds")
    error_message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ScanResultsResponse(BaseModel):
    """Response after scan"""
    success: bool = True
    sync_id: UUID = Field(..., description="ID of this sync operation")
    summary: ScanSummary
    next_action: str = Field(
        "REVIEW",
        description="Next recommended action (REVIEW, APPLY_AUTO, APPLY_MANUAL)"
    )

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# COMPARISON PANEL MODELS
# ============================================================================

class ComparisonItem(BaseModel):
    """Single item for comparison view"""
    namespace_code: str
    key_path: str
    language: str

    action: ResolutionAction
    resolution_status: ResolutionStatus

    frontend_value: Optional[str]
    database_value: Optional[str]
    similarity: float

    conflict_reason: Optional[str] = None
    proposed_action: Optional[str] = Field(
        None,
        description="Auto-suggested action (for AUTO mode)"
    )

    model_config = ConfigDict(from_attributes=True)


class ComparisonCategory(BaseModel):
    """Grouped comparison results"""
    category: str = Field(..., description="NEW_KEYS, CHANGED_KEYS, DELETED_KEYS, or CONFLICTS")
    items: List[ComparisonItem]
    count: int = Field(description="Number of items in this category")

    model_config = ConfigDict(from_attributes=True)


class ComparisonPanelResponse(BaseModel):
    """Response for comparison panel"""
    success: bool = True
    sync_id: UUID
    categories: List[ComparisonCategory]
    total_items: int
    sync_mode: SyncMode
    can_apply: bool = Field(description="Whether sync can be applied")

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# SNAPSHOT MODELS
# ============================================================================

class SnapshotInfo(BaseModel):
    """Information about a snapshot"""
    snapshot_id: UUID
    sync_id: UUID
    snapshot_type: str = Field(..., description="PRE_SYNC, POST_SYNC, or ROLLBACK")
    reason: str = Field(description="Why this snapshot was created")
    total_keys: int
    affected_keys: int
    languages: List[str]
    created_at: datetime
    created_by: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)


class SnapshotCreateRequest(BaseModel):
    """Request to create snapshot"""
    snapshot_type: str = Field(..., description="PRE_SYNC, POST_SYNC, or ROLLBACK")
    reason: str = Field(..., description="Reason for snapshot")

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# ROLLBACK MODELS
# ============================================================================

class RollbackInfo(BaseModel):
    """Information about rollback operation"""
    previous_sync_id: UUID = Field(description="Sync that's being rolled back")
    snapshot_id: UUID = Field(description="Snapshot to restore from")
    keys_affected: int = Field(description="Number of keys being reverted")
    rollback_duration_ms: int = Field(0, description="Time taken to rollback")

    model_config = ConfigDict(from_attributes=True)


class RollbackResultResponse(BaseModel):
    """Response after rollback"""
    success: bool = True
    rollback_info: RollbackInfo
    message: str = Field(description="Human-readable result message")

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# DASHBOARD MODELS
# ============================================================================

class SyncStatistics(BaseModel):
    """Overall sync statistics for dashboard"""
    total_syncs: int
    total_syncs_today: int
    successful_syncs: int
    failed_syncs: int
    last_sync_id: Optional[UUID] = None
    last_sync_timestamp: Optional[datetime] = None
    last_sync_mode: Optional[SyncMode] = None
    avg_sync_duration_ms: int = Field(0, description="Average duration in milliseconds")
    pending_resolutions: int = Field(0, description="Pending manual resolutions")

    model_config = ConfigDict(from_attributes=True)


class DashboardResponse(BaseModel):
    """Dashboard overview"""
    success: bool = True
    statistics: SyncStatistics
    recent_syncs: List[SyncHistorySummary] = Field(description="Last 5 syncs")
    next_recommended_sync: Optional[str] = Field(
        None,
        description="Time or condition for next sync"
    )

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# ERROR MODELS
# ============================================================================

class SyncError(BaseModel):
    """Sync operation error"""
    error_code: str = Field(..., description="Error code (e.g., INVALID_KEY_FORMAT)")
    error_message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)


class SyncErrorResponse(BaseModel):
    """Error response from sync endpoint"""
    success: bool = False
    error: SyncError
    sync_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)
