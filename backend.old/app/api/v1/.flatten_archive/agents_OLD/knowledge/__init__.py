"""
LernsystemX Agents Knowledge Package

Knowledge base and feedback management.

Endpoints:
- POST /api/v1/agents/:course_id/feedback - Submit feedback
- POST /api/v1/agents/:course_id/knowledge - Add knowledge entry
- DELETE /api/v1/agents/:course_id/cache - Invalidate cache
- POST /api/v1/agents/:course_id/warm - Warm up cache
"""

from .base import agents_knowledge_bp

__all__ = ['agents_knowledge_bp']
