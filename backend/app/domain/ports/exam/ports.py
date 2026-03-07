"""
Port interfaces for exam domain repositories.

These ABCs define the contract that infrastructure implementations must fulfill.
Domain code accesses repos through the registry, never by direct import.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any


class ExamTypeRegistryPort(ABC):
    """Port for exam type registry persistence."""

    @staticmethod
    @abstractmethod
    def find_all() -> List[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def find_by_type(exam_type: str) -> Optional[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def create(data: Dict[str, Any]) -> Optional[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def update(exam_type: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def delete(exam_type: str) -> bool: ...


class TopicTaxonomyPort(ABC):
    """Port for exam topic taxonomy persistence."""

    @staticmethod
    @abstractmethod
    def find_by_exam_type(exam_type: str) -> List[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def find_by_id(topic_id: str) -> Optional[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def find_by_topic_keys(
        exam_type: str, topic_keys: List[str]
    ) -> List[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def create(data: Dict[str, Any]) -> Optional[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def update(
        topic_id: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def delete(topic_id: str) -> bool: ...


class UserExamGoalsPort(ABC):
    """Port for user exam goals persistence."""

    @staticmethod
    @abstractmethod
    def find_by_user(
        user_id: str, status: Optional[str] = None
    ) -> List[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def find_active_exam_types(user_id: str) -> List[str]: ...

    @staticmethod
    @abstractmethod
    def create(
        user_id: str,
        exam_type: str,
        target_date: Optional[str] = None,
        status: str = 'active',
    ) -> Optional[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def update_status(
        goal_id: str, status: str
    ) -> Optional[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def delete(goal_id: str) -> bool: ...
