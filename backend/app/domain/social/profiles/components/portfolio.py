"""Learning Portfolio"""

from typing import Dict, Any
from app.domain.ports.core.registry import repos


class PortfolioService:
    """User learning portfolio"""

    @staticmethod
    def get_portfolio(user_id: str) -> Dict[str, Any]:
        """Get user's learning portfolio"""
        return repos.users.get_portfolio(user_id)
