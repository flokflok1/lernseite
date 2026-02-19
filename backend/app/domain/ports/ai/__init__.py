"""
AI Domain Ports

Provides abstract interfaces for AI-related domain operations.
"""

from app.domain.ports.ai.ports import (
    AIJobPort,
    PromptTemplatePort,
    LearningMethodCatalogPort,
    LearningMethodGroupPort,
    AIAdapterPort,
    AIJobServicePort
)

__all__ = [
    'AIJobPort',
    'PromptTemplatePort',
    'LearningMethodCatalogPort',
    'LearningMethodGroupPort',
    'AIAdapterPort',
    'AIJobServicePort'
]
