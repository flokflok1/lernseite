"""
Agent Knowledge Warming Jobs Repository

Database access for agent knowledge base warm-up operations:
- Create and manage warm-up jobs
- Track warm-up progress and statistics
- Monitor cost and token usage

ISO 9001:2015 compliant - Agent warming management
"""

import json
from typing import Dict, Any, Optional, List
from app.infrastructure.persistence.repositories.base_repository import BaseRepository


class AgentWarmingRepository(BaseRepository):
    """
    Repository for agent knowledge warming jobs

    Tables:
    - agent_warm_jobs: Warm-up job records and progress
    """

    @staticmethod
    def create_warm_job(
        agent_id: str,
        job_type: str,
        target_tier: Optional[int] = None,
        total_items: int = 0
    ) -> Dict[str, Any]:
        """
        Create a new warm-up job

        Initiates a knowledge base warming job for an agent.
        Various job types support different warming strategies.

        Args:
            agent_id: Agent UUID
            job_type: Job type (full_warm, incremental, tier_specific, etc.)
            target_tier: Optional target tier for tier-specific warming
            total_items: Total items to process in this job

        Returns:
            Created job data with all fields
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
        return AgentWarmingRepository.fetch_one(query, (
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

        Atomically updates job status and accumulates statistics.
        Automatically sets started_at when status becomes 'running'
        and completed_at when job finishes.

        Args:
            job_id: Job UUID
            status: New status (pending, running, completed, failed, cancelled)
            completed_items: Items completed so far
            tokens_used: Tokens consumed in this update
            cost_eur: Cost in EUR for this update
            items_cached: Items added to cache
            errors: List of error messages (if any)

        Returns:
            Updated job data or None if update failed
        """
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
        return AgentWarmingRepository.fetch_one(query, (
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

        Retrieves jobs with pending or running status, optionally
        filtered by agent. Results ordered by creation time.

        Args:
            agent_id: Optional filter by agent UUID

        Returns:
            List of pending/running job records
        """
        if agent_id:
            query = """
                SELECT * FROM agent_warm_jobs
                WHERE agent_id = %s AND status IN ('pending', 'running')
                ORDER BY created_at
            """
            return AgentWarmingRepository.fetch_all(query, (agent_id,))
        else:
            query = """
                SELECT * FROM agent_warm_jobs
                WHERE status IN ('pending', 'running')
                ORDER BY created_at
            """
            return AgentWarmingRepository.fetch_all(query)
