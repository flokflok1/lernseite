"""
Agent Statistics Repository

Database access for agent performance metrics:
- Agent statistics from materialized views
- Query performance tracking
- Cache hit metrics

ISO 9001:2015 compliant - Agent metrics management
"""

from typing import Dict, Any, Optional, List
from app.infrastructure.persistence.repositories.base_repository import BaseRepository


class AgentStatsRepository(BaseRepository):
    """
    Repository for agent statistics and analytics

    Views:
    - v_agent_stats: Aggregated agent performance metrics
    """

    @staticmethod
    def get_agent_stats(agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get agent statistics from view

        Args:
            agent_id: Agent UUID

        Returns:
            Statistics data or None if not found
        """
        query = """
            SELECT *
            FROM v_agent_stats
            WHERE agent_id = %s
        """
        return AgentStatsRepository.fetch_one(query, (agent_id,))

    @staticmethod
    def get_all_agents_stats(
        limit: int = 50,
        offset: int = 0,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all agents with statistics, with optional filtering

        Retrieves agent statistics with pagination. Results ordered by
        total queries in descending order.

        Args:
            limit: Maximum number of results (default 50)
            offset: Pagination offset (default 0)
            status: Optional filter by knowledge_status

        Returns:
            List of agent statistics dictionaries
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
        return AgentStatsRepository.fetch_all(query, tuple(params))
