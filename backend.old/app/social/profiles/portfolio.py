"""Learning Portfolio"""

from typing import List, Dict, Any


class PortfolioService:
    """User learning portfolio"""
    
    @staticmethod
    def get_portfolio(user_id: str) -> Dict[str, Any]:
        """Get user's learning portfolio"""
        from app.repositories.base_repository import BaseRepository
        query = """
            SELECT 
                COUNT(DISTINCT e.course_id) as courses_count,
                COUNT(DISTINCT c.certificate_id) as certificates_count
            FROM enrollments e
            LEFT JOIN certificates c ON e.enrollment_id = c.enrollment_id
            WHERE e.user_id = %s
        """
        return BaseRepository.fetch_one(query, (user_id,)) or {}
