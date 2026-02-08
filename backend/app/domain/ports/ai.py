"""
Port interfaces for AI domain repositories.

These ABCs define the contract that infrastructure implementations must fulfill.
Domain code accesses repos through the registry, never by direct import.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any


class AIJobPort(ABC):
    """Port for AI job persistence."""

    @staticmethod
    @abstractmethod
    def find_by_id(job_id: str) -> Optional[Dict[str, Any]]: ...


class PromptTemplatePort(ABC):
    """Port for prompt template persistence."""

    @staticmethod
    @abstractmethod
    def find_by_code(code: str) -> Optional[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def find_by_category_and_style(
        category: str, style: str
    ) -> Optional[Dict[str, Any]]: ...


class LearningMethodCatalogPort(ABC):
    """Port for learning method catalog persistence."""

    @staticmethod
    @abstractmethod
    def get_by_type(method_type: int) -> Optional[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def get_full_catalog(use_cache: bool = True) -> List[Dict[str, Any]]: ...


class LearningMethodGroupPort(ABC):
    """Port for learning method group persistence."""

    @staticmethod
    @abstractmethod
    def find_by_code(code: str) -> Optional[Dict[str, Any]]: ...
