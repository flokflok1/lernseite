"""
Math Domain (DDD + Journey-Based Architecture)

Math Toolkit system with DDD layers and journey-based API routes.
ALL data loaded dynamically from database - NO hardcoded values.

Architecture:
- domain/ - Domain entities (9 entities for 9 tables)
- application/ - Business logic services
- infrastructure/ - Database repositories (3 parts due to size)
- journeys/ - Journey-based API routes (admin)

9 Math Tables:
1. math_pattern_categories - Categories (Prozent, Kalkulation, Zins, etc.)
2. math_patterns - Math patterns with formula templates
3. math_formulas - Formula library
4. math_toolkit_sessions - Practice sessions
5. math_calculation_steps - Calculation steps
6. math_calculator_history - Calculator history
7. math_user_progress - User progress with spaced repetition
8. math_pattern_recognition_tasks - Pattern recognition tasks
9. math_scaffolding_hints - Scaffolding hints (Level 1-3)

Usage:
    from src.api.content.math import MathService, admin_math_bp

Exports:
- MathPatternCategory - Domain entity for category
- MathPattern - Domain entity for pattern
- MathFormula - Domain entity for formula
- MathToolkitSession - Domain entity for session
- MathCalculationStep - Domain entity for calculation step
- MathCalculatorHistory - Domain entity for calculator history
- MathUserProgress - Domain entity for user progress
- MathPatternRecognitionTask - Domain entity for recognition task
- MathScaffoldingHint - Domain entity for scaffolding hint
- MathService - Business logic
- MathRepository - Database access (part 1)
- MathRepositoryPart2 - Database access (part 2)
- MathRepositoryPart3 - Database access (part 3)
- admin_math_bp - Admin journey routes
"""

from src.api.content.math.domain.entities.math_pattern_category import MathPatternCategory
from src.api.content.math.domain.entities.math_pattern import MathPattern
from src.api.content.math.domain.entities.math_formula import MathFormula
from src.api.content.math.domain.entities.math_toolkit_session import MathToolkitSession
from src.api.content.math.domain.entities.math_calculation_step import MathCalculationStep
from src.api.content.math.domain.entities.math_calculator_history import MathCalculatorHistory
from src.api.content.math.domain.entities.math_user_progress import MathUserProgress
from src.api.content.math.domain.entities.math_pattern_recognition_task import MathPatternRecognitionTask
from src.api.content.math.domain.entities.math_scaffolding_hint import MathScaffoldingHint
from src.api.content.math.application.services.math_service import MathService
from src.api.content.math.infrastructure.repositories.math_repository import MathRepository
from src.api.content.math.infrastructure.repositories.math_repository_part2 import MathRepositoryPart2
from src.api.content.math.infrastructure.repositories.math_repository_part3 import MathRepositoryPart3
from src.api.content.math.journeys.admin.api.routes.math import admin_math_bp

__all__ = [
    # Domain Entities
    'MathPatternCategory',
    'MathPattern',
    'MathFormula',
    'MathToolkitSession',
    'MathCalculationStep',
    'MathCalculatorHistory',
    'MathUserProgress',
    'MathPatternRecognitionTask',
    'MathScaffoldingHint',

    # Application
    'MathService',

    # Infrastructure
    'MathRepository',
    'MathRepositoryPart2',
    'MathRepositoryPart3',

    # Journeys
    'admin_math_bp',
]
