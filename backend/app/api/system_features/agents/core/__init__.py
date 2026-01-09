"""
LernsystemX Agents Core Package

Core agent endpoints for Q&A and configuration.

Endpoints:
- POST /api/v1/agents/:course_id/ask - Ask the agent a question
- GET /api/v1/agents/:course_id/status - Get agent status
- GET /api/v1/agents/:course_id/config - Get agent configuration
- PUT /api/v1/agents/:course_id/config - Update agent configuration
"""

from .engine import agents_core_bp

# Optional: Factory pattern for agent creation (reference implementation)
# from .factory import AgentFactory

__all__ = [
    'agents_core_bp',
    # 'AgentFactory',  # Uncomment when factory is integrated
]
