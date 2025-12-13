"""
LernsystemX Agent Repository

Database access for Smart Agent System:
- Course agents configuration
- Agent statistics and status
- Organization extensions

ISO 9001:2015 compliant - Agent data management
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from app.repositories.base_repository import BaseRepository


class AgentRepository(BaseRepository):
    """
    Repository for Smart Agent System database operations

    Tables:
    - course_agents: Agent configuration per course
    - agent_org_extensions: Organization-specific customizations
    """

    # =========================================================================
    # Course Agents
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
            FROM course_agents
            WHERE course_id = %s
        """
        return AgentRepository.fetch_one(query, (course_id,))

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
            FROM course_agents
            WHERE agent_id = %s
        """
        return AgentRepository.fetch_one(query, (agent_id,))

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
        return AgentRepository.fetch_one(query, (
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
        agent = AgentRepository.get_agent_by_course(course_id)
        if agent:
            return agent
        return AgentRepository.create_agent(course_id, **kwargs)

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
            return AgentRepository.get_agent_by_id(agent_id)

        set_clause = ', '.join([f"{k} = %s" for k in updates.keys()])
        query = f"""
            UPDATE course_agents
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
        return AgentRepository.fetch_one(query, tuple(values))

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
            UPDATE course_agents
            SET
                knowledge_status = %s,
                last_warmed_at = CASE WHEN %s = 'ready' THEN NOW() ELSE last_warmed_at END,
                updated_at = NOW()
            WHERE agent_id = %s
        """
        result = AgentRepository.execute(query, (status, status, agent_id))
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
        result = AgentRepository.execute(query, (agent_id, cache_hit, tokens_saved))
        return result is not None

    # =========================================================================
    # Agent Statistics
    # =========================================================================

    @staticmethod
    def get_agent_stats(agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get agent statistics from view

        Args:
            agent_id: Agent UUID

        Returns:
            Statistics data
        """
        query = """
            SELECT *
            FROM v_agent_stats
            WHERE agent_id = %s
        """
        return AgentRepository.fetch_one(query, (agent_id,))

    @staticmethod
    def get_all_agents_stats(
        limit: int = 50,
        offset: int = 0,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all agents with statistics

        Args:
            limit: Max results
            offset: Pagination offset
            status: Filter by knowledge_status

        Returns:
            List of agent statistics
        """
        where_clause = ""
        params: List[Any] = []

        if status:
            where_clause = "WHERE knowledge_status = %s"
            params.append(status)

        query = f"""
            SELECT *
            FROM v_agent_stats
            {where_clause}
            ORDER BY total_queries DESC
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        return AgentRepository.fetch_all(query, tuple(params))

    # =========================================================================
    # Organization Extensions
    # =========================================================================

    @staticmethod
    def get_org_extension(
        agent_id: str,
        organization_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get organization-specific agent extension

        Args:
            agent_id: Agent UUID
            organization_id: Organization UUID

        Returns:
            Extension data or None
        """
        query = """
            SELECT
                extension_id,
                agent_id,
                organization_id,
                custom_persona,
                custom_language,
                custom_terminology,
                custom_examples,
                additional_context,
                blocked_topics,
                enabled,
                created_at,
                updated_at
            FROM agent_org_extensions
            WHERE agent_id = %s AND organization_id = %s
        """
        return AgentRepository.fetch_one(query, (agent_id, organization_id))

    @staticmethod
    def create_org_extension(
        agent_id: str,
        organization_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create organization-specific agent extension

        Args:
            agent_id: Agent UUID
            organization_id: Organization UUID
            **kwargs: Extension settings

        Returns:
            Created extension data
        """
        import json

        query = """
            INSERT INTO agent_org_extensions (
                agent_id,
                organization_id,
                custom_persona,
                custom_language,
                custom_terminology,
                custom_examples,
                additional_context,
                blocked_topics
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING *
        """
        return AgentRepository.fetch_one(query, (
            agent_id,
            organization_id,
            kwargs.get('custom_persona'),
            kwargs.get('custom_language'),
            json.dumps(kwargs.get('custom_terminology', {})),
            json.dumps(kwargs.get('custom_examples', [])),
            kwargs.get('additional_context'),
            json.dumps(kwargs.get('blocked_topics', []))
        ))

    @staticmethod
    def update_org_extension(
        extension_id: str,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Update organization extension

        Args:
            extension_id: Extension UUID
            **kwargs: Fields to update

        Returns:
            Updated extension data
        """
        import json

        allowed_fields = {
            'custom_persona', 'custom_language', 'custom_terminology',
            'custom_examples', 'additional_context', 'blocked_topics', 'enabled'
        }

        updates = {}
        for k, v in kwargs.items():
            if k not in allowed_fields:
                continue
            if k in ('custom_terminology', 'custom_examples', 'blocked_topics'):
                updates[k] = json.dumps(v) if v else None
            else:
                updates[k] = v

        if not updates:
            return None

        set_clause = ', '.join([f"{k} = %s" for k in updates.keys()])
        query = f"""
            UPDATE agent_org_extensions
            SET {set_clause}, updated_at = NOW()
            WHERE extension_id = %s
            RETURNING *
        """
        values = list(updates.values()) + [extension_id]
        return AgentRepository.fetch_one(query, tuple(values))

    @staticmethod
    def get_effective_agent_config(
        course_id: str,
        organization_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get effective agent configuration, merging base + org extension

        Args:
            course_id: Course UUID
            organization_id: Optional organization UUID

        Returns:
            Merged agent configuration
        """
        agent = AgentRepository.get_or_create_agent(course_id)

        config = {
            'agent_id': agent['agent_id'],
            'course_id': agent['course_id'],
            'name': agent['name'],
            'persona': agent['persona'],
            'language': agent['language'],
            'primary_provider': agent['primary_provider'],
            'primary_model': agent['primary_model'],
            'temperature': float(agent['temperature']) if agent['temperature'] else 0.7,
            'max_tokens': agent['max_tokens'],
            'knowledge_status': agent['knowledge_status'],
            'custom_terminology': {},
            'blocked_topics': []
        }

        # Merge organization extension if available
        if organization_id:
            ext = AgentRepository.get_org_extension(agent['agent_id'], organization_id)
            if ext and ext.get('enabled', True):
                if ext.get('custom_persona'):
                    config['persona'] = ext['custom_persona']
                if ext.get('custom_language'):
                    config['language'] = ext['custom_language']
                if ext.get('custom_terminology'):
                    config['custom_terminology'] = ext['custom_terminology']
                if ext.get('blocked_topics'):
                    config['blocked_topics'] = ext['blocked_topics']
                if ext.get('additional_context'):
                    config['additional_context'] = ext['additional_context']

        return config

    # =========================================================================
    # Warm Jobs
    # =========================================================================

    @staticmethod
    def create_warm_job(
        agent_id: str,
        job_type: str,
        target_tier: Optional[int] = None,
        total_items: int = 0
    ) -> Dict[str, Any]:
        """
        Create a new warm-up job

        Args:
            agent_id: Agent UUID
            job_type: Job type (full_warm, incremental, tier_specific, etc.)
            target_tier: Optional target tier
            total_items: Total items to process

        Returns:
            Created job data
        """
        query = """
            INSERT INTO agent_warm_jobs (
                agent_id,
                job_type,
                target_tier,
                total_items
            ) VALUES (%s, %s, %s, %s)
            RETURNING *
        """
        return AgentRepository.fetch_one(query, (
            agent_id, job_type, target_tier, total_items
        ))

    @staticmethod
    def update_warm_job(
        job_id: str,
        status: str,
        completed_items: int = 0,
        tokens_used: int = 0,
        cost_eur: float = 0,
        items_cached: int = 0,
        errors: Optional[list] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update warm-up job progress

        Args:
            job_id: Job UUID
            status: New status
            completed_items: Items completed
            tokens_used: Tokens consumed
            cost_eur: Cost in EUR
            items_cached: Items cached
            errors: List of errors

        Returns:
            Updated job data
        """
        import json

        query = """
            UPDATE agent_warm_jobs
            SET
                status = %s,
                completed_items = %s,
                progress = CASE WHEN total_items > 0
                    THEN ROUND((%s::decimal / total_items) * 100)
                    ELSE 0 END,
                tokens_used = tokens_used + %s,
                cost_eur = cost_eur + %s,
                items_cached = items_cached + %s,
                errors = COALESCE(%s::jsonb, errors),
                started_at = CASE WHEN status = 'running' AND started_at IS NULL THEN NOW() ELSE started_at END,
                completed_at = CASE WHEN %s IN ('completed', 'failed', 'cancelled') THEN NOW() ELSE completed_at END
            WHERE job_id = %s
            RETURNING *
        """
        return AgentRepository.fetch_one(query, (
            status,
            completed_items,
            completed_items,
            tokens_used,
            cost_eur,
            items_cached,
            json.dumps(errors) if errors else None,
            status,
            job_id
        ))

    @staticmethod
    def get_pending_warm_jobs(agent_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get pending warm-up jobs

        Args:
            agent_id: Optional filter by agent

        Returns:
            List of pending jobs
        """
        if agent_id:
            query = """
                SELECT * FROM agent_warm_jobs
                WHERE agent_id = %s AND status IN ('pending', 'running')
                ORDER BY created_at
            """
            return AgentRepository.fetch_all(query, (agent_id,))
        else:
            query = """
                SELECT * FROM agent_warm_jobs
                WHERE status IN ('pending', 'running')
                ORDER BY created_at
            """
            return AgentRepository.fetch_all(query)
