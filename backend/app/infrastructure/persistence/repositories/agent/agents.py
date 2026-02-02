"""
Agent CRUD Operations Repository

Database access for course agents configuration:
- Get agents by course or ID
- Create and update agent configurations
- Knowledge status management
- Agent statistics tracking

ISO 9001:2015 compliant - Agent data management
"""

from typing import Dict, Any, Optional
from app.infrastructure.persistence.repositories.base_repository import BaseRepository


class AgentCRUDRepository(BaseRepository):
    """
    Repository for course agent CRUD operations

    Tables:
    - course_agents: Agent configuration per course
    """

    # =========================================================================
    # Retrieval
    # =========================================================================

    @staticmethod
    def get_agent_by_course(course_id: str) -> Optional[Dict[str, Any]]:
        """
        Get agent for a course

        Args:
            course_id: Course UUID

        Returns:
            Agent data or None if not found
        """
        query = """
            SELECT
                agent_id,
                course_id,
                name,
                persona,
                language,
                knowledge_status,
                last_warmed_at,
                knowledge_version,
                primary_provider,
                primary_model,
                fallback_provider,
                fallback_model,
                temperature,
                max_tokens,
                org_config_override,
                total_queries,
                cache_hits,
                tokens_saved,
                created_at,
                updated_at
            FROM smart_agents.course_agents
            WHERE course_id = %s
        """
        return AgentCRUDRepository.fetch_one(query, (course_id,))

    @staticmethod
    def get_agent_by_id(agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get agent by ID

        Args:
            agent_id: Agent UUID

        Returns:
            Agent data or None if not found
        """
        query = """
            SELECT
                agent_id,
                course_id,
                name,
                persona,
                language,
                knowledge_status,
                last_warmed_at,
                knowledge_version,
                primary_provider,
                primary_model,
                fallback_provider,
                fallback_model,
                temperature,
                max_tokens,
                org_config_override,
                total_queries,
                cache_hits,
                tokens_saved,
                created_at,
                updated_at
            FROM smart_agents.course_agents
            WHERE agent_id = %s
        """
        return AgentCRUDRepository.fetch_one(query, (agent_id,))

    # =========================================================================
    # Creation and Updates
    # =========================================================================

    @staticmethod
    def create_agent(course_id: str, **kwargs) -> Dict[str, Any]:
        """
        Create a new agent for a course

        Args:
            course_id: Course UUID
            **kwargs: Optional agent settings (name, persona, language, etc.)

        Returns:
            Created agent data
        """
        query = """
            INSERT INTO course_agents (
                course_id,
                name,
                persona,
                language,
                primary_provider,
                primary_model,
                temperature,
                max_tokens
            ) VALUES (
                %s,
                COALESCE(%s, 'KI-Tutor'),
                COALESCE(%s, 'friendly'),
                COALESCE(%s, 'de'),
                COALESCE(%s, 'openai'),
                COALESCE(%s, 'gpt-4o-mini'),
                COALESCE(%s, 0.7),
                COALESCE(%s, 2000)
            )
            RETURNING
                agent_id,
                course_id,
                name,
                persona,
                language,
                knowledge_status,
                primary_provider,
                primary_model,
                temperature,
                max_tokens,
                total_queries,
                cache_hits,
                tokens_saved,
                created_at
        """
        return AgentCRUDRepository.fetch_one(query, (
            course_id,
            kwargs.get('name'),
            kwargs.get('persona'),
            kwargs.get('language'),
            kwargs.get('primary_provider'),
            kwargs.get('primary_model'),
            kwargs.get('temperature'),
            kwargs.get('max_tokens')
        ))

    @staticmethod
    def get_or_create_agent(course_id: str, **kwargs) -> Dict[str, Any]:
        """
        Get existing agent or create new one for a course

        Args:
            course_id: Course UUID
            **kwargs: Optional agent settings for creation

        Returns:
            Agent data
        """
        agent = AgentCRUDRepository.get_agent_by_course(course_id)
        if agent:
            return agent
        return AgentCRUDRepository.create_agent(course_id, **kwargs)

    @staticmethod
    def update_agent(agent_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Update agent settings

        Args:
            agent_id: Agent UUID
            **kwargs: Fields to update

        Returns:
            Updated agent data or None
        """
        allowed_fields = {
            'name', 'persona', 'language', 'knowledge_status',
            'primary_provider', 'primary_model', 'fallback_provider',
            'fallback_model', 'temperature', 'max_tokens', 'org_config_override'
        }

        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            return AgentCRUDRepository.get_agent_by_id(agent_id)

        set_clause = ', '.join([f"{k} = %s" for k in updates.keys()])
        query = f"""
            UPDATE smart_agents.course_agents
            SET {set_clause}, updated_at = NOW()
            WHERE agent_id = %s
            RETURNING
                agent_id,
                course_id,
                name,
                persona,
                language,
                knowledge_status,
                primary_provider,
                primary_model,
                temperature,
                max_tokens,
                total_queries,
                cache_hits,
                tokens_saved,
                updated_at
        """
        values = list(updates.values()) + [agent_id]
        return AgentCRUDRepository.fetch_one(query, tuple(values))

    # =========================================================================
    # Knowledge Status
    # =========================================================================

    @staticmethod
    def update_knowledge_status(agent_id: str, status: str) -> bool:
        """
        Update agent knowledge status

        Args:
            agent_id: Agent UUID
            status: New status (pending, warming, ready, stale)

        Returns:
            True if updated
        """
        query = """
            UPDATE smart_agents.course_agents
            SET
                knowledge_status = %s,
                last_warmed_at = CASE WHEN %s = 'ready' THEN NOW() ELSE last_warmed_at END,
                updated_at = NOW()
            WHERE agent_id = %s
        """
        result = AgentCRUDRepository.execute(query, (status, status, agent_id))
        return result is not None

    @staticmethod
    def increment_stats(
        agent_id: str,
        cache_hit: bool = False,
        tokens_saved: int = 0
    ) -> bool:
        """
        Atomically increment agent statistics

        Args:
            agent_id: Agent UUID
            cache_hit: Whether this was a cache hit
            tokens_saved: Tokens saved (if cache hit)

        Returns:
            True if updated
        """
        query = """
            SELECT increment_agent_stats(%s, %s, %s)
        """
        result = AgentCRUDRepository.execute(query, (agent_id, cache_hit, tokens_saved))
        return result is not None
