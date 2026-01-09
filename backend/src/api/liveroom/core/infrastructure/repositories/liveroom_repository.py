"""LiveRoom Repository (Infrastructure Layer)"""
from typing import List, Optional
from datetime import datetime
from src.core.database import get_db_connection
from src.api.liveroom.core.domain.entities.room import Room
from src.api.liveroom.core.domain.entities.room_participant import RoomParticipant

class LiveRoomRepository:
    """LiveRoom Repository - Rooms & Participants."""

    @staticmethod
    def find_room_by_id(room_id: int) -> Optional[Room]:
        """Find room by ID."""
        query = """
            SELECT id, org_id, course_id, chapter_id, created_by, room_type, name,
                   description, status, max_participants, start_time, end_time,
                   duration_minutes, enable_ai, enable_recording, ai_model,
                   ai_pipeline_version, access_code, created_at, updated_at
            FROM liveroom.rooms WHERE id = %s
        """
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (room_id,))
                row = cur.fetchone()
                if not row:
                    return None
                return Room(
                    id=row[0], org_id=row[1], course_id=row[2], chapter_id=row[3],
                    created_by=row[4], room_type=row[5], name=row[6],
                    description=row[7], status=row[8] or 'active',
                    max_participants=row[9] or 50, start_time=row[10],
                    end_time=row[11], duration_minutes=row[12],
                    enable_ai=row[13] or False, enable_recording=row[14] or False,
                    ai_model=row[15], ai_pipeline_version=row[16],
                    access_code=row[17], created_at=row[18], updated_at=row[19]
                )

    @staticmethod
    def create_room(room: Room) -> Room:
        """Create new room."""
        query = """
            INSERT INTO liveroom.rooms
            (org_id, course_id, chapter_id, created_by, room_type, name, description,
             status, max_participants, enable_ai, enable_recording, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, org_id, course_id, chapter_id, created_by, room_type, name,
                      description, status, max_participants, start_time, end_time,
                      duration_minutes, enable_ai, enable_recording, ai_model,
                      ai_pipeline_version, access_code, created_at, updated_at
        """
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (
                    room.org_id, room.course_id, room.chapter_id, room.created_by,
                    room.room_type, room.name, room.description, room.status,
                    room.max_participants, room.enable_ai, room.enable_recording,
                    room.created_at or datetime.utcnow()
                ))
                row = cur.fetchone()
                conn.commit()
                return Room(
                    id=row[0], org_id=row[1], course_id=row[2], chapter_id=row[3],
                    created_by=row[4], room_type=row[5], name=row[6],
                    description=row[7], status=row[8] or 'active',
                    max_participants=row[9] or 50, start_time=row[10],
                    end_time=row[11], duration_minutes=row[12],
                    enable_ai=row[13] or False, enable_recording=row[14] or False,
                    ai_model=row[15], ai_pipeline_version=row[16],
                    access_code=row[17], created_at=row[18], updated_at=row[19]
                )

    @staticmethod
    def find_participants_by_room(room_id: int) -> List[RoomParticipant]:
        """Find all participants in a room."""
        query = """
            SELECT id, room_id, user_id, role, joined_at, left_at, active, participation_score
            FROM liveroom.room_participants WHERE room_id = %s
        """
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (room_id,))
                return [
                    RoomParticipant(
                        id=row[0], room_id=row[1], user_id=row[2], role=row[3] or 'student',
                        joined_at=row[4], left_at=row[5], active=row[6] if row[6] is not None else True,
                        participation_score=row[7] or 0
                    )
                    for row in cur.fetchall()
                ]

    @staticmethod
    def create_participant(participant: RoomParticipant) -> RoomParticipant:
        """Add participant to room."""
        query = """
            INSERT INTO liveroom.room_participants
            (room_id, user_id, role, joined_at, active)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, room_id, user_id, role, joined_at, left_at, active, participation_score
        """
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (
                    participant.room_id, participant.user_id, participant.role,
                    participant.joined_at or datetime.utcnow(), participant.active
                ))
                row = cur.fetchone()
                conn.commit()
                return RoomParticipant(
                    id=row[0], room_id=row[1], user_id=row[2], role=row[3] or 'student',
                    joined_at=row[4], left_at=row[5], active=row[6] if row[6] is not None else True,
                    participation_score=row[7] or 0
                )
