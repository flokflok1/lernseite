"""
LernsystemX Runner State Manager

Redis-based state management for runner sessions.
Provides TTL-aware state storage, locking, and payload caching.

Prefix: lsx:
Keys:
- lsx:runner:session:{session_id}        -> JSON session state
- lsx:runner:lock:{user_id}:{course_id}  -> exam lock
- lsx:runner:payload:{method_id}:{hash}  -> prepared payload cache

TTL Strategy:
- standard / learn: 24h (86400s)
- exam / timed: time_limit + 30m
- review: 1h after completion (3600s)
"""

import json
import hashlib
from typing import Any, Dict, Optional
from datetime import datetime

from app.core.bootstrap.extensions import redis_client


class RunnerStateManager:
    """
    Manages runner session state in Redis.

    All runner session state is stored in Redis for:
    - Fast read/write during learning execution
    - TTL-based automatic cleanup
    - Atomic operations for exam locking
    """

    # Key prefixes
    PREFIX = "lsx:runner"
    SESSION_KEY = f"{PREFIX}:session"
    LOCK_KEY = f"{PREFIX}:lock"
    PAYLOAD_KEY = f"{PREFIX}:payload"

    # TTL values (seconds)
    TTL_STANDARD = 86400      # 24 hours
    TTL_EXAM_BUFFER = 1800    # 30 minutes buffer after exam time limit
    TTL_REVIEW = 3600         # 1 hour for review mode
    TTL_PAYLOAD_CACHE = 300   # 5 minutes for payload cache

    # =========================================================================
    # Session State Management
    # =========================================================================

    @classmethod
    def get_session_state(cls, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session state from Redis.

        Args:
            session_id: UUID of the runner session

        Returns:
            Session state dict or None if not found/expired
        """
        key = f"{cls.SESSION_KEY}:{session_id}"
        data = redis_client.get(key)

        if data:
            return json.loads(data)
        return None

    @classmethod
    def set_session_state(
        cls,
        session_id: str,
        state: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set session state in Redis with TTL.

        Args:
            session_id: UUID of the runner session
            state: State dict to store
            ttl: Time-to-live in seconds (default: 24h)

        Returns:
            True if successful
        """
        key = f"{cls.SESSION_KEY}:{session_id}"
        ttl = ttl or cls.TTL_STANDARD

        # Add metadata
        state['_updated_at'] = datetime.utcnow().isoformat()

        redis_client.setex(key, ttl, json.dumps(state))
        return True

    @classmethod
    def update_session_state(
        cls,
        session_id: str,
        state: Dict[str, Any],
        preserve_ttl: bool = True
    ) -> bool:
        """
        Update session state preserving existing TTL.

        Args:
            session_id: UUID of the runner session
            state: New state dict
            preserve_ttl: If True, keeps existing TTL

        Returns:
            True if successful, False if session not found
        """
        key = f"{cls.SESSION_KEY}:{session_id}"

        if preserve_ttl:
            # Get remaining TTL
            remaining_ttl = redis_client.ttl(key)
            if remaining_ttl <= 0:
                return False

            state['_updated_at'] = datetime.utcnow().isoformat()
            redis_client.setex(key, remaining_ttl, json.dumps(state))
        else:
            state['_updated_at'] = datetime.utcnow().isoformat()
            redis_client.set(key, json.dumps(state))

        return True

    @classmethod
    def delete_session_state(cls, session_id: str) -> bool:
        """
        Delete session state from Redis.

        Args:
            session_id: UUID of the runner session

        Returns:
            True if deleted, False if not found
        """
        key = f"{cls.SESSION_KEY}:{session_id}"
        return redis_client.delete(key) > 0

    @classmethod
    def extend_session_ttl(cls, session_id: str, additional_seconds: int) -> bool:
        """
        Extend session TTL by additional seconds.

        Args:
            session_id: UUID of the runner session
            additional_seconds: Seconds to add to current TTL

        Returns:
            True if successful
        """
        key = f"{cls.SESSION_KEY}:{session_id}"
        current_ttl = redis_client.ttl(key)

        if current_ttl > 0:
            redis_client.expire(key, current_ttl + additional_seconds)
            return True
        return False

    @classmethod
    def get_session_ttl(cls, session_id: str) -> int:
        """
        Get remaining TTL for session.

        Args:
            session_id: UUID of the runner session

        Returns:
            Remaining TTL in seconds, -2 if key doesn't exist, -1 if no TTL
        """
        key = f"{cls.SESSION_KEY}:{session_id}"
        return redis_client.ttl(key)

    # =========================================================================
    # Exam Locking (for timed exams)
    # =========================================================================

    @classmethod
    def acquire_exam_lock(
        cls,
        user_id: str,
        course_id: str,
        session_id: str,
        time_limit_seconds: int
    ) -> bool:
        """
        Acquire exclusive exam lock for user in course.

        Prevents user from starting multiple exam sessions simultaneously.

        Args:
            user_id: User UUID
            course_id: Course UUID
            session_id: Session UUID (stored as lock value)
            time_limit_seconds: Exam time limit

        Returns:
            True if lock acquired, False if already locked
        """
        key = f"{cls.LOCK_KEY}:{user_id}:{course_id}"
        ttl = time_limit_seconds + cls.TTL_EXAM_BUFFER

        # NX = only set if not exists
        return redis_client.set(key, session_id, nx=True, ex=ttl)

    @classmethod
    def release_exam_lock(cls, user_id: str, course_id: str) -> bool:
        """
        Release exam lock for user in course.

        Args:
            user_id: User UUID
            course_id: Course UUID

        Returns:
            True if released
        """
        key = f"{cls.LOCK_KEY}:{user_id}:{course_id}"
        return redis_client.delete(key) > 0

    @classmethod
    def get_exam_lock(cls, user_id: str, course_id: str) -> Optional[str]:
        """
        Get current exam lock session for user in course.

        Args:
            user_id: User UUID
            course_id: Course UUID

        Returns:
            Session ID if locked, None otherwise
        """
        key = f"{cls.LOCK_KEY}:{user_id}:{course_id}"
        return redis_client.get(key)

    # =========================================================================
    # Payload Caching
    # =========================================================================

    @classmethod
    def _hash_payload(cls, payload: Dict[str, Any]) -> str:
        """Generate hash for payload content."""
        content = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    @classmethod
    def cache_payload(
        cls,
        method_id: str,
        payload: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> str:
        """
        Cache prepared payload for method.

        Args:
            method_id: Learning method UUID
            payload: Prepared payload dict
            ttl: Cache TTL in seconds

        Returns:
            Cache hash for retrieval
        """
        payload_hash = cls._hash_payload(payload)
        key = f"{cls.PAYLOAD_KEY}:{method_id}:{payload_hash}"
        ttl = ttl or cls.TTL_PAYLOAD_CACHE

        redis_client.setex(key, ttl, json.dumps(payload))
        return payload_hash

    @classmethod
    def get_cached_payload(
        cls,
        method_id: str,
        payload_hash: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached payload for method.

        Args:
            method_id: Learning method UUID
            payload_hash: Hash from cache_payload

        Returns:
            Cached payload or None
        """
        key = f"{cls.PAYLOAD_KEY}:{method_id}:{payload_hash}"
        data = redis_client.get(key)

        if data:
            return json.loads(data)
        return None

    # =========================================================================
    # Utility Methods
    # =========================================================================

    @classmethod
    def calculate_ttl(cls, mode_code: str, time_limit_minutes: Optional[int] = None) -> int:
        """
        Calculate appropriate TTL based on runner mode.

        Args:
            mode_code: Runner mode code (standard, exam, timed, review)
            time_limit_minutes: Optional time limit for timed modes

        Returns:
            TTL in seconds
        """
        if mode_code in ('exam', 'timed') and time_limit_minutes:
            return (time_limit_minutes * 60) + cls.TTL_EXAM_BUFFER
        elif mode_code == 'review':
            return cls.TTL_REVIEW
        else:
            return cls.TTL_STANDARD

    @classmethod
    def session_exists(cls, session_id: str) -> bool:
        """
        Check if session exists in Redis.

        Args:
            session_id: UUID of the runner session

        Returns:
            True if exists
        """
        key = f"{cls.SESSION_KEY}:{session_id}"
        return redis_client.exists(key) > 0

    @classmethod
    def get_initial_state(cls, mode_code: str) -> Dict[str, Any]:
        """
        Generate initial state template for runner mode.

        Args:
            mode_code: Runner mode code

        Returns:
            Initial state dict
        """
        return {
            'answers': {},
            'progress': {
                'current_index': 0,
                'completed_items': [],
                'total_items': 0
            },
            'timers': {
                'started_at': datetime.utcnow().isoformat(),
                'elapsed_seconds': 0,
                'paused': False
            },
            'flags': {
                'submitted': False,
                'timed_out': False,
                'paused': False
            },
            '_created_at': datetime.utcnow().isoformat(),
            '_updated_at': datetime.utcnow().isoformat()
        }
