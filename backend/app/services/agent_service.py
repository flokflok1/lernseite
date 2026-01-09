"""
Agent Service - Bridge Module

DEPRECATED: This module is kept for backwards compatibility.

New code should use:
  from app.services.agent import AgentService

All functionality has been refactored into a modular package:
  - agent.core: Main ask() and status
  - agent.routing: AI provider routing
  - agent.knowledge: Knowledge management
  - agent.prompts: Prompt building
  - agent.media: Audio/TTS responses

This file re-exports the public API from the new package.
"""

# For backwards compatibility, re-export the main class
from app.services.agent import (
    AgentService,
    AgentCore,
    AgentRouter,
    KnowledgeManager,
    PromptBuilder,
    MediaOperations,
    CACHE_TTL_TIER_1,
    CACHE_TTL_TIER_2,
    CACHE_TTL_TIER_3
)

__all__ = [
    'AgentService',
    'AgentCore',
    'AgentRouter',
    'KnowledgeManager',
    'PromptBuilder',
    'MediaOperations',
    'CACHE_TTL_TIER_1',
    'CACHE_TTL_TIER_2',
    'CACHE_TTL_TIER_3'
]
