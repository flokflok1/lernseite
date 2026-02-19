"""
Port interfaces for base/shared persistence operations.

QueryRunnerPort: raw SQL execution (fetch_one, fetch_all, execute)
UserPort: user persistence operations used by the domain layer
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Tuple


class QueryRunnerPort(ABC):
    """
    Port for raw SQL query execution.

    Used by domain services that need custom queries not covered by
    a dedicated repository (e.g., discovery, analytics, notifications).
    """

    @staticmethod
    @abstractmethod
    def fetch_one(query: str, params: Tuple = ()) -> Optional[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def fetch_all(query: str, params: Tuple = ()) -> List[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def execute(query: str, params: Tuple = ()) -> int: ...


class UserPort(ABC):
    """Port for user persistence operations used by the domain layer."""

    @staticmethod
    @abstractmethod
    def find_by_id(user_id: str) -> Optional[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def execute(query: str, params: Tuple = ()) -> int: ...

    @staticmethod
    @abstractmethod
    def update_bio(user_id: str, bio: str) -> bool: ...

    @staticmethod
    @abstractmethod
    def update_avatar(user_id: str, avatar_url: str) -> bool: ...

    @staticmethod
    @abstractmethod
    def get_portfolio(user_id: str) -> Dict[str, Any]: ...

    @staticmethod
    @abstractmethod
    def get_achievements(user_id: str) -> List[Dict[str, Any]]: ...
