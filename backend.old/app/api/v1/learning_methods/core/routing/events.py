"""
Routing Domain Events (DDD)

Events emitted when routing configuration changes.
"""

import uuid
from datetime import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ModelAssignedEvent:
    """
    Event: Model assigned to learning method.

    Triggered when:
    - New assignment created
    - Assignment updated to different model
    """
    event_id: str
    learning_method_id: int
    model_id: int
    scope: str
    course_id: Optional[str]
    chapter_id: Optional[str]
    assigned_by: str
    timestamp: datetime

    @classmethod
    def create(
        cls,
        learning_method_id: int,
        model_id: int,
        scope: str,
        assigned_by: str,
        course_id: Optional[str] = None,
        chapter_id: Optional[str] = None
    ) -> 'ModelAssignedEvent':
        """Create new ModelAssignedEvent."""
        return cls(
            event_id=str(uuid.uuid4()),
            learning_method_id=learning_method_id,
            model_id=model_id,
            scope=scope,
            course_id=course_id,
            chapter_id=chapter_id,
            assigned_by=assigned_by,
            timestamp=datetime.utcnow()
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for logging/audit."""
        return {
            'event_id': self.event_id,
            'event_type': 'model_assigned',
            'learning_method_id': self.learning_method_id,
            'model_id': self.model_id,
            'scope': self.scope,
            'course_id': self.course_id,
            'chapter_id': self.chapter_id,
            'assigned_by': self.assigned_by,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass(frozen=True)
class ModelUnassignedEvent:
    """
    Event: Model assignment removed from learning method.

    Triggered when:
    - Assignment deleted
    """
    event_id: str
    learning_method_id: int
    assignment_id: str
    unassigned_by: str
    timestamp: datetime

    @classmethod
    def create(
        cls,
        learning_method_id: int,
        assignment_id: str,
        unassigned_by: str
    ) -> 'ModelUnassignedEvent':
        """Create new ModelUnassignedEvent."""
        return cls(
            event_id=str(uuid.uuid4()),
            learning_method_id=learning_method_id,
            assignment_id=assignment_id,
            unassigned_by=unassigned_by,
            timestamp=datetime.utcnow()
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for logging/audit."""
        return {
            'event_id': self.event_id,
            'event_type': 'model_unassigned',
            'learning_method_id': self.learning_method_id,
            'assignment_id': self.assignment_id,
            'unassigned_by': self.unassigned_by,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass(frozen=True)
class SlotPresetAppliedEvent:
    """
    Event: Cost preset applied to all slot assignments.

    Triggered when:
    - Auto-configuration preset (cheap/medium/expensive) applied system-wide
    """
    event_id: str
    preset: str
    configured_count: int
    skipped_count: int
    failed_count: int
    applied_by: str
    timestamp: datetime

    @classmethod
    def create(
        cls,
        preset: str,
        configured_count: int,
        skipped_count: int,
        failed_count: int,
        applied_by: str
    ) -> 'SlotPresetAppliedEvent':
        """Create new SlotPresetAppliedEvent."""
        return cls(
            event_id=str(uuid.uuid4()),
            preset=preset,
            configured_count=configured_count,
            skipped_count=skipped_count,
            failed_count=failed_count,
            applied_by=applied_by,
            timestamp=datetime.utcnow()
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for logging/audit."""
        return {
            'event_id': self.event_id,
            'event_type': 'slot_preset_applied',
            'preset': self.preset,
            'configured_count': self.configured_count,
            'skipped_count': self.skipped_count,
            'failed_count': self.failed_count,
            'applied_by': self.applied_by,
            'timestamp': self.timestamp.isoformat()
        }
