"""
Math Toolkit Service Package

Modular system for mathematical learning with:
- Safe expression evaluation
- Pattern library management
- Progress tracking & mastery
- Scaffolding hints
- Session management
- Calculation history

All functionality accessible through MathToolkitService for backward compatibility.
"""

from .parser import ExpressionParser
from .solver import MathSolver
from .patterns import PatternManager
from .sessions import SessionManager
from .progress import ProgressTracker
from .hints import HintProvider
from .tasks import TaskManager
from .calculator import CalculatorHistory
from .steps import StepRecorder

__all__ = [
    'ExpressionParser',
    'MathSolver',
    'PatternManager',
    'SessionManager',
    'ProgressTracker',
    'HintProvider',
    'TaskManager',
    'CalculatorHistory',
    'StepRecorder',
    # NOTE: MathToolkitService is available via:
    # - Direct import: from app.application.services.lm.math_toolkit import MathToolkitService
    # - Or bridge file: from app.application.services.math_toolkit_service import MathToolkitService
    # It is not re-exported here to avoid circular import issues
]
