"""
LernsystemX Knowledge Repository Package

Data access layer for Agent Knowledge Base:
- Knowledge entries (Q&A pairs, explanations, examples)
- Query logging and analytics
- Cache entry management and lifecycle
- Learning from interactions

Features:
- Full-text search for similar questions
- Question hash-based deduplication
- Performance metrics and cost tracking
- Multi-tier cache support
- User feedback recording

ISO 9001:2015 compliant - Knowledge data management
ISO 27001:2013 compliant - Secure knowledge storage

This package provides backward-compatible bridge for existing imports:
    from app.repositories.knowledge import KnowledgeRepository
    # Maps to: from app.repositories.knowledge import KnowledgeRepository

Modules:
- crud: Create, read, update knowledge entries
- search: Find and match knowledge entries
- learning: Learn from user interactions
- query_log: Log and analyze queries
- cache: Manage cache entry lifecycle
"""

from app.repositories.knowledge.crud import KnowledgeRepositoryCRUD
from app.repositories.knowledge.search import KnowledgeRepositorySearch
from app.repositories.knowledge.learning import KnowledgeRepositoryLearning
from app.repositories.knowledge.query_log import KnowledgeRepositoryQueryLog
from app.repositories.knowledge.cache import KnowledgeRepositoryCache


class KnowledgeRepository(
    KnowledgeRepositoryCRUD,
    KnowledgeRepositorySearch,
    KnowledgeRepositoryLearning,
    KnowledgeRepositoryQueryLog,
    KnowledgeRepositoryCache
):
    """
    Unified KnowledgeRepository combining all functionality

    This class uses multiple inheritance to aggregate methods from specialized
    module classes. All methods are organized by domain:
    - CRUD: Create, find, update knowledge entries
    - Search: Full-text search and matching
    - Learning: Learn from user interactions
    - QueryLog: Query logging and analytics
    - Cache: Cache entry management

    Example:
        >>> knowledge = KnowledgeRepository.create_knowledge(
        ...     agent_id='agent-123',
        ...     answer_text='The answer is...',
        ...     question_text='What is...?'
        ... )
        >>> best_match = KnowledgeRepository.get_best_match(
        ...     agent_id='agent-123',
        ...     question='What is...?'
        ... )
        >>> KnowledgeRepository.log_query(
        ...     agent_id='agent-123',
        ...     user_id='user-456',
        ...     query_text='What is...?',
        ...     response_source='cache_hit'
        ... )
    """
    pass


__all__ = [
    'KnowledgeRepository',
    'KnowledgeRepositoryCRUD',
    'KnowledgeRepositorySearch',
    'KnowledgeRepositoryLearning',
    'KnowledgeRepositoryQueryLog',
    'KnowledgeRepositoryCache',
]
