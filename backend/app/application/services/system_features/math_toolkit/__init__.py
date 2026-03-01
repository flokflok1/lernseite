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

from .solving.parser import ExpressionParser
from .solving.solver import MathSolver
from .solving.patterns import PatternManager
from .tracking.sessions import SessionManager
from .tracking.progress import ProgressTracker
from .tracking.hints import HintProvider
from .tracking.tasks import TaskManager
from .solving.calculator import CalculatorHistory
from .solving.steps import StepRecorder

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
    # - Direct import: from app.application.services.content.lm.math_toolkit import MathToolkitService
    # - Or bridge file: from app.application.services.system_features.math_toolkit.service import MathToolkitService
    # It is not re-exported here to avoid circular import issues
]
