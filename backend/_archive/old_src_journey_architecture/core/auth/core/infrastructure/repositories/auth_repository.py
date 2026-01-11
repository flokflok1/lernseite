"""Auth Repository (DDD Infrastructure Layer)

Handles database operations for authentication.
Uses direct SQL with psycopg3 - NO ORM.
"""

from typing import Optional
from datetime import datetime, timedelta
import bcrypt
import logging

from src.infrastructure.database.connection import get_db_connection
from src.api.auth.core.domain.entities.user import User
from src.api.auth.core.domain.entities.user_session import UserSession

logger = logging.getLogger(__name__)


class AuthRepository:
    """
    Authentication repository.
    
    Handles user authentication, session management, and password operations.
    All operations return domain entities (User, UserSession).
    """
    
    # ====================================================================
    # USER AUTHENTICATION
    # ====================================================================
    
    @staticmethod
    def create_user(
        email: str,
        password_hash: str,
        firstname: str,
        lastname: str,
        role_id: int,
        organization_id: Optional[str] = None
    ) -> User:
        """
        Create a new user.
        
        Args:
            email: User email
            password_hash: Bcrypt hashed password
            firstname: User first name
            lastname: User last name
            role_id: Role ID
            organization_id: Organization ID (optional)
            
        Returns:
            User entity
        """
        query = """
        INSERT INTO core.users (
            email, password_hash, firstname, lastname, role_id, organization_id,
            status, email_verified, created_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, 'active', FALSE, NOW())
        RETURNING *
        """
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (
                    email, password_hash, firstname, lastname, role_id, organization_id
                ))
                row = cur.fetchone()
                conn.commit()
                
                if not row:
                    raise RuntimeError("Failed to create user")
                
                # Convert row to User entity
                return User(
                    user_id=str(row[0]),
                    email=row[1],
                    password_hash=row[2],
                    firstname=row[3],
                    lastname=row[4],
                    role_id=row[5],
                    language=row[6],
                    timezone=row[7],
                    theme_preference=row[8],
                    avatar_url=row[9],
                    email_verified=row[10],
                    email_verified_at=row[11],
                    two_factor_enabled=row[12],
                    two_factor_secret=row[13],
                    last_login=row[14],
                    last_login_ip=row[15],
                    status=row[16],
                    banned_until=row[17],
                    creator_verified=row[18],
                    creator_verified_at=row[19],
                    created_at=row[20],
                    updated_at=row[21],
                    deleted_at=row[22]
                )
    
    @staticmethod
    def find_user_by_email(email: str) -> Optional[User]:
        """
        Find user by email address.
        
        Args:
            email: User email
            
        Returns:
            User entity or None
        """
        query = "SELECT * FROM core.users WHERE email = %s AND deleted_at IS NULL"
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (email,))
                row = cur.fetchone()
                
                if not row:
                    return None
                
                return User(
                    user_id=str(row[0]),
                    email=row[1],
                    password_hash=row[2],
                    firstname=row[3],
                    lastname=row[4],
                    role_id=row[5],
                    language=row[6],
                    timezone=row[7],
                    theme_preference=row[8],
                    avatar_url=row[9],
                    email_verified=row[10],
                    email_verified_at=row[11],
                    two_factor_enabled=row[12],
                    two_factor_secret=row[13],
                    last_login=row[14],
                    last_login_ip=row[15],
                    status=row[16],
                    banned_until=row[17],
                    creator_verified=row[18],
                    creator_verified_at=row[19],
                    created_at=row[20],
                    updated_at=row[21],
                    deleted_at=row[22]
                )
    
    @staticmethod
    def find_user_by_id(user_id: str) -> Optional[User]:
        """
        Find user by ID.
        
        Args:
            user_id: User UUID
            
        Returns:
            User entity or None
        """
        query = "SELECT * FROM core.users WHERE user_id = %s AND deleted_at IS NULL"
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (user_id,))
                row = cur.fetchone()
                
                if not row:
                    return None
                
                return User(
                    user_id=str(row[0]),
                    email=row[1],
                    password_hash=row[2],
                    firstname=row[3],
                    lastname=row[4],
                    role_id=row[5],
                    language=row[6],
                    timezone=row[7],
                    theme_preference=row[8],
                    avatar_url=row[9],
                    email_verified=row[10],
                    email_verified_at=row[11],
                    two_factor_enabled=row[12],
                    two_factor_secret=row[13],
                    last_login=row[14],
                    last_login_ip=row[15],
                    status=row[16],
                    banned_until=row[17],
                    creator_verified=row[18],
                    creator_verified_at=row[19],
                    created_at=row[20],
                    updated_at=row[21],
                    deleted_at=row[22]
                )
    
    @staticmethod
    def update_last_login(user_id: str, ip_address: str) -> None:
        """
        Update user's last login timestamp and IP.
        
        Args:
            user_id: User UUID
            ip_address: Client IP address
        """
        query = """
        UPDATE core.users
        SET last_login = NOW(), last_login_ip = %s, updated_at = NOW()
        WHERE user_id = %s
        """
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (ip_address, user_id))
                conn.commit()
    
    @staticmethod
    def verify_email(user_id: str) -> None:
        """
        Mark user email as verified.
        
        Args:
            user_id: User UUID
        """
        query = """
        UPDATE core.users
        SET email_verified = TRUE, email_verified_at = NOW(), updated_at = NOW()
        WHERE user_id = %s
        """
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (user_id,))
                conn.commit()
    
    # ====================================================================
    # SESSION MANAGEMENT
    # ====================================================================
    
    @staticmethod
    def create_session(
        user_id: str,
        jti: str,
        refresh_token_hash: str,
        ip_address: Optional[str],
        user_agent: Optional[str],
        device_info: Optional[dict],
        expires_at: datetime
    ) -> UserSession:
        """
        Create a new user session.
        
        Args:
            user_id: User UUID
            jti: JWT ID
            refresh_token_hash: Hashed refresh token
            ip_address: Client IP address
            user_agent: Browser user agent
            device_info: Device information (JSONB)
            expires_at: Session expiration timestamp
            
        Returns:
            UserSession entity
        """
        query = """
        INSERT INTO core.user_sessions (
            user_id, jti, refresh_token_hash, ip_address, user_agent,
            device_info, expires_at, revoked, created_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, FALSE, NOW())
        RETURNING *
        """
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (
                    user_id, jti, refresh_token_hash, ip_address,
                    user_agent, device_info, expires_at
                ))
                row = cur.fetchone()
                conn.commit()
                
                if not row:
                    raise RuntimeError("Failed to create session")
                
                return UserSession(
                    session_id=str(row[0]),
                    user_id=str(row[1]),
                    jti=row[2],
                    refresh_token_hash=row[3],
                    ip_address=row[4],
                    user_agent=row[5],
                    device_info=row[6],
                    expires_at=row[7],
                    revoked=row[8],
                    revoked_at=row[9],
                    created_at=row[10]
                )
    
    @staticmethod
    def find_session_by_jti(jti: str) -> Optional[UserSession]:
        """
        Find session by JWT ID.
        
        Args:
            jti: JWT ID
            
        Returns:
            UserSession entity or None
        """
        query = "SELECT * FROM core.user_sessions WHERE jti = %s"
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (jti,))
                row = cur.fetchone()
                
                if not row:
                    return None
                
                return UserSession(
                    session_id=str(row[0]),
                    user_id=str(row[1]),
                    jti=row[2],
                    refresh_token_hash=row[3],
                    ip_address=row[4],
                    user_agent=row[5],
                    device_info=row[6],
                    expires_at=row[7],
                    revoked=row[8],
                    revoked_at=row[9],
                    created_at=row[10]
                )
    
    @staticmethod
    def revoke_session(jti: str) -> None:
        """
        Revoke a session.
        
        Args:
            jti: JWT ID
        """
        query = """
        UPDATE core.user_sessions
        SET revoked = TRUE, revoked_at = NOW()
        WHERE jti = %s
        """
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (jti,))
                conn.commit()
    
    @staticmethod
    def revoke_all_user_sessions(user_id: str) -> None:
        """
        Revoke all sessions for a user.
        
        Args:
            user_id: User UUID
        """
        query = """
        UPDATE core.user_sessions
        SET revoked = TRUE, revoked_at = NOW()
        WHERE user_id = %s AND revoked = FALSE
        """
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (user_id,))
                conn.commit()
    
    # ====================================================================
    # PASSWORD OPERATIONS
    # ====================================================================
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Bcrypt hashed password
        """
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verify password against hash.
        
        Args:
            password: Plain text password
            password_hash: Bcrypt hash
            
        Returns:
            True if password matches
        """
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    @staticmethod
    def update_password(user_id: str, new_password_hash: str) -> None:
        """
        Update user password.
        
        Args:
            user_id: User UUID
            new_password_hash: New bcrypt password hash
        """
        query = """
        UPDATE core.users
        SET password_hash = %s, updated_at = NOW()
        WHERE user_id = %s
        """
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (new_password_hash, user_id))
                conn.commit()
