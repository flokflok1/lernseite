"""User Repository (DDD Infrastructure Layer)

Handles user management operations (CRUD, Search, Profile).
Authentication operations are in AuthRepository (Auth Domain).
"""

from typing import Optional, List
from datetime import datetime
import logging

from src.infrastructure.database.connection import get_db_connection
from src.api.auth.core.domain.entities.user import User

logger = logging.getLogger(__name__)


class UserRepository:
    """
    User management repository.
    
    Handles user CRUD, search, profile updates.
    Auth operations (login, sessions) are in AuthRepository.
    """
    
    # ====================================================================
    # READ OPERATIONS
    # ====================================================================
    
    @staticmethod
    def find_by_id(user_id: str) -> Optional[User]:
        """Find user by ID."""
        query = "SELECT * FROM core.users WHERE user_id = %s AND deleted_at IS NULL"
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (user_id,))
                row = cur.fetchone()
                
                if not row:
                    return None
                
                return User(
                    user_id=str(row[0]), email=row[1], password_hash=row[2],
                    firstname=row[3], lastname=row[4], role_id=row[5],
                    language=row[6], timezone=row[7], theme_preference=row[8],
                    avatar_url=row[9], email_verified=row[10], email_verified_at=row[11],
                    two_factor_enabled=row[12], two_factor_secret=row[13],
                    last_login=row[14], last_login_ip=row[15], status=row[16],
                    banned_until=row[17], creator_verified=row[18], creator_verified_at=row[19],
                    created_at=row[20], updated_at=row[21], deleted_at=row[22]
                )
    
    @staticmethod
    def list_users(limit: int = 100, offset: int = 0) -> List[User]:
        """List all users (paginated)."""
        query = """
        SELECT * FROM core.users
        WHERE deleted_at IS NULL
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
        """
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (limit, offset))
                rows = cur.fetchall()
                
                users = []
                for row in rows:
                    users.append(User(
                        user_id=str(row[0]), email=row[1], password_hash=row[2],
                        firstname=row[3], lastname=row[4], role_id=row[5],
                        language=row[6], timezone=row[7], theme_preference=row[8],
                        avatar_url=row[9], email_verified=row[10], email_verified_at=row[11],
                        two_factor_enabled=row[12], two_factor_secret=row[13],
                        last_login=row[14], last_login_ip=row[15], status=row[16],
                        banned_until=row[17], creator_verified=row[18], creator_verified_at=row[19],
                        created_at=row[20], updated_at=row[21], deleted_at=row[22]
                    ))
                
                return users
    
    @staticmethod
    def search_users(query_text: str, limit: int = 50) -> List[User]:
        """Search users by email, firstname, lastname."""
        query = """
        SELECT * FROM core.users
        WHERE deleted_at IS NULL
        AND (
            email ILIKE %s OR
            firstname ILIKE %s OR
            lastname ILIKE %s
        )
        ORDER BY created_at DESC
        LIMIT %s
        """
        search_pattern = f"%{query_text}%"
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (search_pattern, search_pattern, search_pattern, limit))
                rows = cur.fetchall()
                
                users = []
                for row in rows:
                    users.append(User(
                        user_id=str(row[0]), email=row[1], password_hash=row[2],
                        firstname=row[3], lastname=row[4], role_id=row[5],
                        language=row[6], timezone=row[7], theme_preference=row[8],
                        avatar_url=row[9], email_verified=row[10], email_verified_at=row[11],
                        two_factor_enabled=row[12], two_factor_secret=row[13],
                        last_login=row[14], last_login_ip=row[15], status=row[16],
                        banned_until=row[17], creator_verified=row[18], creator_verified_at=row[19],
                        created_at=row[20], updated_at=row[21], deleted_at=row[22]
                    ))
                
                return users
    
    # ====================================================================
    # UPDATE OPERATIONS
    # ====================================================================
    
    @staticmethod
    def update_profile(
        user_id: str,
        firstname: Optional[str] = None,
        lastname: Optional[str] = None,
        avatar_url: Optional[str] = None,
        language: Optional[str] = None,
        timezone: Optional[str] = None,
        theme_preference: Optional[str] = None
    ) -> None:
        """Update user profile."""
        updates = []
        params = []
        
        if firstname is not None:
            updates.append("firstname = %s")
            params.append(firstname)
        if lastname is not None:
            updates.append("lastname = %s")
            params.append(lastname)
        if avatar_url is not None:
            updates.append("avatar_url = %s")
            params.append(avatar_url)
        if language is not None:
            updates.append("language = %s")
            params.append(language)
        if timezone is not None:
            updates.append("timezone = %s")
            params.append(timezone)
        if theme_preference is not None:
            updates.append("theme_preference = %s")
            params.append(theme_preference)
        
        if not updates:
            return
        
        updates.append("updated_at = NOW()")
        params.append(user_id)
        
        query = f"""
        UPDATE core.users
        SET {', '.join(updates)}
        WHERE user_id = %s
        """
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, tuple(params))
                conn.commit()
    
    @staticmethod
    def update_status(user_id: str, status: str) -> None:
        """Update user status."""
        query = """
        UPDATE core.users
        SET status = %s, updated_at = NOW()
        WHERE user_id = %s
        """
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (status, user_id))
                conn.commit()
    
    # ====================================================================
    # DELETE OPERATIONS
    # ====================================================================
    
    @staticmethod
    def soft_delete(user_id: str) -> None:
        """Soft delete user (set deleted_at)."""
        query = """
        UPDATE core.users
        SET deleted_at = NOW(), status = 'deactivated', updated_at = NOW()
        WHERE user_id = %s
        """
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (user_id,))
                conn.commit()
    
    @staticmethod
    def restore_user(user_id: str) -> None:
        """Restore soft-deleted user."""
        query = """
        UPDATE core.users
        SET deleted_at = NULL, status = 'active', updated_at = NOW()
        WHERE user_id = %s
        """
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (user_id,))
                conn.commit()
    
    # ====================================================================
    # STATISTICS
    # ====================================================================
    
    @staticmethod
    def count_users() -> int:
        """Count total active users."""
        query = "SELECT COUNT(*) FROM core.users WHERE deleted_at IS NULL"
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                result = cur.fetchone()
                return result[0] if result else 0
    
    @staticmethod
    def count_by_role(role_id: int) -> int:
        """Count users by role."""
        query = """
        SELECT COUNT(*) FROM core.users
        WHERE role_id = %s AND deleted_at IS NULL
        """
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (role_id,))
                result = cur.fetchone()
                return result[0] if result else 0
