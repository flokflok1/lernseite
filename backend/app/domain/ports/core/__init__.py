"""
Core Domain Ports

Provides base abstract interfaces and repository registry.
"""

from app.domain.ports.core.base import (
    QueryRunnerPort,
    UserPort
)
from app.domain.ports.core.registry import _RepositoryRegistry

__all__ = [
    'QueryRunnerPort',
    'UserPort',
    '_RepositoryRegistry'
]
