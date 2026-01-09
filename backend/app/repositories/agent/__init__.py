"""
Agent Repository Package

Provides database access for Smart Agent System operations:
- Course agent CRUD and configuration
- Agent statistics and performance metrics
- Organization-specific agent extensions
- Knowledge base warming jobs and progress

This package replaces the monolithic agent_repository.py module
while maintaining full backward compatibility through re-exports.

Structure:
- agents.py: Core CRUD operations and agent management
- stats.py: Performance metrics and aggregated statistics
- extensions.py: Organization-specific customizations
- warming.py: Knowledge base warming jobs

ISO 9001:2015 compliant - Agent management system
"""

# Re-export all repositories from submodules for backward compatibility
from app.repositories.agent.agents import AgentCRUDRepository
from app.repositories.agent.stats import AgentStatsRepository
from app.repositories.agent.extensions import AgentExtensionRepository
from app.repositories.agent.warming import AgentWarmingRepository


# Backward-compatible unified interface
class AgentRepository:
    """
    Unified repository interface for agent operations

    Provides backward-compatible access to all agent repository methods
    by delegating to specialized repositories.
    """

    # =========================================================================
    # Course Agents (from AgentCRUDRepository)
    # =========================================================================

    @staticmethod
    def get_agent_by_course(course_id: str):
        """Get agent for a course"""
        return AgentCRUDRepository.get_agent_by_course(course_id)

    @staticmethod
    def get_agent_by_id(agent_id: str):
        """Get agent by ID"""
        return AgentCRUDRepository.get_agent_by_id(agent_id)

    @staticmethod
    def create_agent(course_id: str, **kwargs):
        """Create a new agent for a course"""
        return AgentCRUDRepository.create_agent(course_id, **kwargs)

    @staticmethod
    def get_or_create_agent(course_id: str, **kwargs):
        """Get existing agent or create new one"""
        return AgentCRUDRepository.get_or_create_agent(course_id, **kwargs)

    @staticmethod
    def update_agent(agent_id: str, **kwargs):
        """Update agent settings"""
        return AgentCRUDRepository.update_agent(agent_id, **kwargs)

    @staticmethod
    def update_knowledge_status(agent_id: str, status: str):
        """Update agent knowledge status"""
        return AgentCRUDRepository.update_knowledge_status(agent_id, status)

    @staticmethod
    def increment_stats(agent_id: str, cache_hit: bool = False, tokens_saved: int = 0):
        """Increment agent statistics"""
        return AgentCRUDRepository.increment_stats(agent_id, cache_hit, tokens_saved)

    # =========================================================================
    # Agent Statistics (from AgentStatsRepository)
    # =========================================================================

    @staticmethod
    def get_agent_stats(agent_id: str):
        """Get agent statistics from view"""
        return AgentStatsRepository.get_agent_stats(agent_id)

    @staticmethod
    def get_all_agents_stats(limit: int = 50, offset: int = 0, status=None):
        """Get all agents with statistics"""
        return AgentStatsRepository.get_all_agents_stats(limit, offset, status)

    # =========================================================================
    # Organization Extensions (from AgentExtensionRepository)
    # =========================================================================

    @staticmethod
    def get_org_extension(agent_id: str, organization_id: str):
        """Get organization-specific agent extension"""
        return AgentExtensionRepository.get_org_extension(agent_id, organization_id)

    @staticmethod
    def create_org_extension(agent_id: str, organization_id: str, **kwargs):
        """Create organization-specific agent extension"""
        return AgentExtensionRepository.create_org_extension(agent_id, organization_id, **kwargs)

    @staticmethod
    def update_org_extension(extension_id: str, **kwargs):
        """Update organization extension"""
        return AgentExtensionRepository.update_org_extension(extension_id, **kwargs)

    @staticmethod
    def get_effective_agent_config(course_id: str, organization_id=None):
        """
        Get effective agent configuration (merged base + org extension)

        Note: This method has a different signature than the original.
        The original took course_id and internally loaded the agent.
        The new version in AgentExtensionRepository takes the base_agent dict.

        For backward compatibility, this loads the agent first.
        """
        agent = AgentCRUDRepository.get_or_create_agent(course_id)
        return AgentExtensionRepository.get_effective_agent_config(agent, organization_id)

    # =========================================================================
    # Warming Jobs (from AgentWarmingRepository)
    # =========================================================================

    @staticmethod
    def create_warm_job(agent_id: str, job_type: str, target_tier=None, total_items: int = 0):
        """Create a new warm-up job"""
        return AgentWarmingRepository.create_warm_job(agent_id, job_type, target_tier, total_items)

    @staticmethod
    def update_warm_job(job_id: str, status: str, completed_items: int = 0,
                       tokens_used: int = 0, cost_eur: float = 0,
                       items_cached: int = 0, errors=None):
        """Update warm-up job progress"""
        return AgentWarmingRepository.update_warm_job(
            job_id, status, completed_items, tokens_used, cost_eur, items_cached, errors
        )

    @staticmethod
    def get_pending_warm_jobs(agent_id=None):
        """Get pending warm-up jobs"""
        return AgentWarmingRepository.get_pending_warm_jobs(agent_id)




class AgentRepository(
    AgentCRUDRepository,
    AgentStatsRepository,
    AgentWarmingRepository,
    AgentExtensionRepository
):
    """
    Unified AgentRepository combining all functionality
    This class uses multiple inheritance to aggregate methods from specialized modules.
    """
    pass


__all__ = [
    'AgentRepository',
    'AgentCRUDRepository',
    'AgentStatsRepository',
    'AgentExtensionRepository',
    'AgentWarmingRepository',
]
