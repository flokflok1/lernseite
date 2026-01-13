"""Reach Metrics (Impressions, Reach)"""

class ReachMetrics:
    """Track content reach"""
    
    @staticmethod
    def get_reach(post_id: str) -> dict:
        """Get reach metrics"""
        return {'impressions': 0, 'reach': 0}
