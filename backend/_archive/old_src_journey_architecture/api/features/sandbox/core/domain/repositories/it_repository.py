"""
IT Environments Repository

Handles database operations for IT practice environments.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from app.repositories.base_repository import BaseRepository


class ITEnvironmentsRepository:
    """Repository for IT Environments (Code Sandbox, Network Sim, Terminal)"""

    # ========================================================================
    # Code Sandbox
    # ========================================================================

    @staticmethod
    def create_sandbox_session(user_id: str, language: str, code: str) -> Dict:
        """Create code sandbox session"""
        query = """
            INSERT INTO sandbox_sessions (user_id, language, code, status, created_at)
            VALUES (%s, %s, %s, 'pending', NOW())
            RETURNING session_id, user_id, language, status, created_at
        """
        return BaseRepository.fetch_one(query, (user_id, language, code))

    @staticmethod
    def update_sandbox_result(session_id: str, status: str, output: str, error: Optional[str], execution_time_ms: int) -> Dict:
        """Update sandbox execution result"""
        query = """
            UPDATE sandbox_sessions
            SET status = %s, output = %s, error = %s, execution_time_ms = %s, completed_at = NOW()
            WHERE session_id = %s
            RETURNING session_id, status, output, error, execution_time_ms
        """
        return BaseRepository.fetch_one(query, (status, output, error, execution_time_ms, session_id))

    @staticmethod
    def get_sandbox_session(session_id: str) -> Optional[Dict]:
        """Get sandbox session by ID"""
        query = "SELECT * FROM sandbox_sessions WHERE session_id = %s"
        return BaseRepository.fetch_one(query, (session_id,))

    # ========================================================================
    # Network Simulation
    # ========================================================================

    @staticmethod
    def create_network_topology(user_id: str, topology_data: Dict) -> Dict:
        """Create network topology"""
        query = """
            INSERT INTO network_topologies (user_id, topology_data, created_at)
            VALUES (%s, %s, NOW())
            RETURNING topology_id, user_id, created_at
        """
        import json
        return BaseRepository.fetch_one(query, (user_id, json.dumps(topology_data)))

    @staticmethod
    def get_network_topology(topology_id: str) -> Optional[Dict]:
        """Get network topology"""
        query = "SELECT * FROM network_topologies WHERE topology_id = %s"
        return BaseRepository.fetch_one(query, (topology_id,))

    @staticmethod
    def get_user_topologies(user_id: str) -> List[Dict]:
        """Get user's network topologies"""
        query = """
            SELECT topology_id, created_at
            FROM network_topologies
            WHERE user_id = %s
            ORDER BY created_at DESC
        """
        return BaseRepository.fetch_all(query, (user_id,)) or []

    # ========================================================================
    # Terminal Access
    # ========================================================================

    @staticmethod
    def create_terminal_session(user_id: str, shell: str = "bash") -> Dict:
        """Create terminal session"""
        query = """
            INSERT INTO terminal_sessions (user_id, shell, status, started_at, expires_at)
            VALUES (%s, %s, 'active', NOW(), NOW() + INTERVAL '30 minutes')
            RETURNING session_id, user_id, shell, status, started_at, expires_at
        """
        return BaseRepository.fetch_one(query, (user_id, shell))

    @staticmethod
    def get_terminal_session(session_id: str) -> Optional[Dict]:
        """Get terminal session"""
        query = "SELECT * FROM terminal_sessions WHERE session_id = %s"
        return BaseRepository.fetch_one(query, (session_id,))

    @staticmethod
    def close_terminal_session(session_id: str) -> bool:
        """Close terminal session"""
        query = "UPDATE terminal_sessions SET status = 'closed', closed_at = NOW() WHERE session_id = %s"
        BaseRepository.execute(query, (session_id,))
        return True

    @staticmethod
    def log_terminal_command(session_id: str, command: str, output: str) -> Dict:
        """Log terminal command"""
        query = """
            INSERT INTO terminal_logs (session_id, command, output, executed_at)
            VALUES (%s, %s, %s, NOW())
            RETURNING log_id, session_id, command, executed_at
        """
        return BaseRepository.fetch_one(query, (session_id, command, output))
