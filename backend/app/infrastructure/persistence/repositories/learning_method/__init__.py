"""
Learning Method Repository Package

Modular repository for learning method operations, split into:
- base: Core CRUD operations (get_all, find_by_id, create, update, delete)
- ai_execution: AI execution with token tracking (execute_ai_method, log_token_usage)
- ai_execution_part2: AI prompt building (method-specific prompt templates)
- feedback: Feedback collection and analysis (create_feedback, get_feedback_stats)
- statistics: Usage statistics and reporting (get_user_token_usage, get_statistics)
- instances: Learning method instance management (user progress, completions)

For backward compatibility, imports are re-exported at package level.
Original learning_method_repository.py imports still work via bridge module.
"""

from .base import LearningMethodBaseRepository
from .execution.ai_execution import LearningMethodAIRepository
from .execution.ai_execution_part2 import LearningMethodAIPromptsMixin
from .feedback import LearningMethodFeedbackRepository
from .statistics import LearningMethodStatisticsRepository
from .execution.instances import LearningMethodInstanceRepository
from .execution.instances_part2 import LearningMethodInstanceStatisticsRepository
from .execution.progress import LearningMethodProgressRepository
from .config.types import (
    LearningMethodBase,
    AIExecutionResult,
    TokenUsageStats,
    FeedbackStats,
    MethodStatistics
)



class LearningMethodRepository(
    LearningMethodBaseRepository,
    LearningMethodAIRepository,
    LearningMethodFeedbackRepository,
    LearningMethodStatisticsRepository,
    LearningMethodInstanceRepository
):
    """
    Unified LearningMethodRepository combining all functionality
    This class uses multiple inheritance to aggregate methods from specialized modules.
    """
    pass


__all__ = [
    # Repositories
    'LearningMethodBaseRepository',
    'LearningMethodAIRepository',
    'LearningMethodAIPromptsMixin',
    'LearningMethodFeedbackRepository',
    'LearningMethodStatisticsRepository',
    'LearningMethodInstanceRepository',
    'LearningMethodInstanceStatisticsRepository',
    'LearningMethodProgressRepository',
    # Types
    'LearningMethodBase',
    'AIExecutionResult',
    'TokenUsageStats',
    'FeedbackStats',
    'MethodStatistics',
]
