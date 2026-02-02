"""
LernsystemX Runner API - Session Schemas

Pydantic models for runner session execution endpoints.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


class SessionStatus(str, Enum):
    """Runner session status values."""
    ACTIVE = "active"
    COMPLETED = "completed"
    TIMED_OUT = "timed_out"
    ABANDONED = "abandoned"


# =============================================================================
# Session Start
# =============================================================================

class SessionStartRequest(BaseModel):
    """Request schema for starting/resuming a runner session."""

    method_id: str = Field(
        ...,
        description="Learning method instance UUID"
    )
    mode_code: Optional[str] = Field(
        None,
        description="Optional runner mode code (defaults to method's default mode)"
    )
    resume: bool = Field(
        False,
        description="Whether to resume existing active session"
    )

    @validator('method_id')
    def validate_uuid(cls, v):
        import uuid
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError('method_id must be a valid UUID')
        return v

    class Config:
        schema_extra = {
            "example": {
                "method_id": "550e8400-e29b-41d4-a716-446655440000",
                "mode_code": "practice",
                "resume": False
            }
        }


class SessionStartResponse(BaseModel):
    """Response schema for session start."""

    session_id: str = Field(..., description="Created session UUID")
    mode: str = Field(..., description="Active runner mode code")
    mode_name: str = Field(..., description="Runner mode display name")
    features: List[Dict[str, Any]] = Field(
        ...,
        description="List of active features for this session"
    )
    initial_state: Dict[str, Any] = Field(
        ...,
        description="Initial session state"
    )
    ttl_seconds: int = Field(
        ...,
        description="Session time-to-live in seconds"
    )
    method_info: Dict[str, Any] = Field(
        ...,
        description="Learning method information"
    )
    resumed: bool = Field(
        False,
        description="Whether this was a resumed session"
    )

    class Config:
        schema_extra = {
            "example": {
                "session_id": "660e8400-e29b-41d4-a716-446655440001",
                "mode": "practice",
                "mode_name": "Practice Mode",
                "features": [
                    {"feature_code": "timer_wrapper", "feature_name": "Timer"},
                    {"feature_code": "adaptive_difficulty", "feature_name": "Adaptive Difficulty"}
                ],
                "initial_state": {
                    "answers": {},
                    "progress": {"current_index": 0, "completed_items": [], "total_items": 10},
                    "timers": {"started_at": "2026-01-01T10:00:00Z", "elapsed_seconds": 0},
                    "flags": {"submitted": False, "timed_out": False}
                },
                "ttl_seconds": 86400,
                "method_info": {
                    "method_id": "550e8400-e29b-41d4-a716-446655440000",
                    "title": "Introduction to Python",
                    "method_type": 5,
                    "difficulty": "medium"
                },
                "resumed": False
            }
        }


# =============================================================================
# Session State
# =============================================================================

class SessionStateUpdate(BaseModel):
    """Request schema for updating session state (autosave)."""

    state: Dict[str, Any] = Field(
        ...,
        description="Full session state snapshot (not diff)"
    )

    class Config:
        schema_extra = {
            "example": {
                "state": {
                    "answers": {"q1": "A", "q2": "B"},
                    "progress": {"current_index": 2, "completed_items": ["q1", "q2"], "total_items": 10},
                    "timers": {"started_at": "2026-01-01T10:00:00Z", "elapsed_seconds": 300},
                    "flags": {"submitted": False, "timed_out": False}
                }
            }
        }


class SessionStateResponse(BaseModel):
    """Response schema for session state retrieval."""

    session_id: str
    status: SessionStatus
    mode: str
    mode_name: str
    state: Dict[str, Any] = Field(
        ...,
        description="Current session state from Redis"
    )
    ttl_remaining: int = Field(
        ...,
        description="Remaining TTL in seconds"
    )
    method_info: Dict[str, Any]
    started_at: datetime
    heartbeat_at: Optional[datetime]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "session_id": "660e8400-e29b-41d4-a716-446655440001",
                "status": "active",
                "mode": "practice",
                "mode_name": "Practice Mode",
                "state": {
                    "answers": {"q1": "A"},
                    "progress": {"current_index": 1, "completed_items": ["q1"], "total_items": 10}
                },
                "ttl_remaining": 85000,
                "method_info": {"title": "Introduction to Python"},
                "started_at": "2026-01-01T10:00:00Z",
                "heartbeat_at": "2026-01-01T10:05:00Z"
            }
        }


# =============================================================================
# Session Finish
# =============================================================================

class SessionFinishRequest(BaseModel):
    """Request schema for finishing/submitting a session."""

    final_state: Dict[str, Any] = Field(
        ...,
        description="Final session state snapshot"
    )
    force_submit: bool = Field(
        False,
        description="Force submission even if incomplete"
    )

    class Config:
        schema_extra = {
            "example": {
                "final_state": {
                    "answers": {"q1": "A", "q2": "B", "q3": "C"},
                    "progress": {"current_index": 3, "completed_items": ["q1", "q2", "q3"], "total_items": 3},
                    "timers": {"elapsed_seconds": 600},
                    "flags": {"submitted": True}
                },
                "force_submit": False
            }
        }


class SessionFinishResponse(BaseModel):
    """Response schema for session finish."""

    session_id: str
    status: SessionStatus
    score: Optional[float] = Field(
        None,
        description="Computed score (0-100) if graded"
    )
    passed: Optional[bool] = Field(
        None,
        description="Whether passed threshold (if applicable)"
    )
    duration_seconds: int = Field(
        ...,
        description="Total session duration"
    )
    summary: Dict[str, Any] = Field(
        ...,
        description="Session summary (correct/incorrect counts, etc.)"
    )
    progress_saved: bool = Field(
        ...,
        description="Whether progress was saved to learning_method_progress"
    )

    class Config:
        schema_extra = {
            "example": {
                "session_id": "660e8400-e29b-41d4-a716-446655440001",
                "status": "completed",
                "score": 85.5,
                "passed": True,
                "duration_seconds": 600,
                "summary": {
                    "total_items": 10,
                    "completed_items": 10,
                    "correct_count": 8,
                    "incorrect_count": 2
                },
                "progress_saved": True
            }
        }
