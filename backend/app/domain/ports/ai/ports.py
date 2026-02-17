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


class AIAdapterPort(ABC):
    """Port for AI provider communication.

    Domain code uses this interface to send prompts to AI providers
    without depending on specific provider implementations.
    """

    @abstractmethod
    def send_request(
        self,
        prompt: str,
        context: Optional[str] = None,
        language: str = 'de',
        temperature: float = 0.7,
        max_tokens: int = 2000,
        conversation_history: Optional[list] = None
    ) -> Dict[str, Any]: ...


class AIJobServicePort(ABC):
    """Port for AI job lifecycle management.

    Domain code uses this interface to track job progress
    without depending on the application-layer job service.
    """

    @abstractmethod
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]: ...

    @abstractmethod
    def start_processing(self, job_id: str) -> None: ...

    @abstractmethod
    def update_progress(self, job_id: str, progress: int) -> None: ...

    @abstractmethod
    def update_output(self, job_id: str, output_data: Dict[str, Any]) -> None: ...

    @abstractmethod
    def fail_job(self, job_id: str, error_message: str) -> None: ...

    @abstractmethod
    def complete_job(self, job_id: str) -> None: ...
