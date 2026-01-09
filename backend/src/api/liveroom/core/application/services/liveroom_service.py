"""LiveRoom Service (Application Layer)"""
from typing import List, Optional
from datetime import datetime
from src.api.liveroom.core.domain.entities.room import Room
from src.api.liveroom.core.domain.entities.room_participant import RoomParticipant
from src.api.liveroom.core.infrastructure.repositories.liveroom_repository import LiveRoomRepository
from src.core.events import EventBus, EventType, DomainEvent

class LiveRoomService:
    """LiveRoom service for business logic."""

    @staticmethod
    def get_room_by_id(room_id: int) -> Optional[Room]:
        """Get room by ID."""
        return LiveRoomRepository.find_room_by_id(room_id)

    @staticmethod
    def create_room(
        org_id: str, name: str, room_type: str, created_by: str,
        course_id: Optional[str] = None, enable_ai: bool = False
    ) -> Room:
        """Create new LiveRoom."""
        room = Room(
            id=0,  # Assigned by DB
            org_id=org_id, name=name, room_type=room_type,
            created_by=created_by, course_id=course_id,
            enable_ai=enable_ai, created_at=datetime.utcnow()
        )
        created_room = LiveRoomRepository.create_room(room)
        
        # Publish event
        event = DomainEvent(
            event_type=EventType.LIVEROOM_CREATED,
            aggregate_id=str(created_room.id),
            occurred_at=datetime.utcnow(),
            data={'room_type': created_room.room_type, 'enable_ai': created_room.enable_ai}
        )
        EventBus.publish(event)
        
        # Auto-add creator as host
        LiveRoomService.add_participant(created_room.id, created_by, 'host')
        return created_room

    @staticmethod
    def add_participant(room_id: int, user_id: str, role: str = 'student') -> RoomParticipant:
        """Add participant to room."""
        participant = RoomParticipant(
            id=0, room_id=room_id, user_id=user_id, role=role,
            joined_at=datetime.utcnow()
        )
        return LiveRoomRepository.create_participant(participant)

    @staticmethod
    def get_room_participants(room_id: int) -> List[RoomParticipant]:
        """Get all participants in a room."""
        return LiveRoomRepository.find_participants_by_room(room_id)
