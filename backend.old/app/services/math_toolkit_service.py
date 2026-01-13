"""
Math Toolkit Service - Bridge Module (DEPRECATED)

NOTICE: This module is deprecated. Use individual modules from the
math_toolkit package instead:

Old:
  from app.services.math_toolkit_service import MathToolkitService
  MathToolkitService.evaluate_expression(expr)

New:
  from app.services.math_toolkit import MathSolver
  MathSolver.evaluate_expression(expr)

This bridge maintains backward compatibility with existing code.
All functionality has been refactored into specialized modules for better
maintainability and adherence to file size limits (max 500 LOC).

Structure:
- parser.py: Expression normalization and validation
- solver.py: Safe mathematical evaluation
- patterns.py: Pattern and formula database access
- sessions.py: Session lifecycle management
- progress.py: User progress and mastery tracking
- hints.py: Scaffolding hints by level
- tasks.py: Pattern recognition exercises
- calculator.py: Calculator history management
- steps.py: Calculation step recording
"""

from typing import Dict, List, Optional, Any

# Import all public interfaces
from app.services.math_toolkit import (
    ExpressionParser,
    MathSolver,
    PatternManager,
    SessionManager,
    ProgressTracker,
    HintProvider,
    TaskManager,
    CalculatorHistory,
    StepRecorder,
)


class MathToolkitService:
    """
    Legacy service class for backward compatibility.

    Routes all calls to appropriate specialized modules.
    DEPRECATED: Use direct imports from math_toolkit package.
    """

    # =========================================================================
    # PATTERN CATEGORIES
    # =========================================================================

    @staticmethod
    def get_categories(active_only: bool = True) -> List[Dict]:
        """Holt alle Muster-Kategorien"""
        return PatternManager.get_categories(active_only)

    @staticmethod
    def get_category_by_code(code: str) -> Optional[Dict]:
        """Holt Kategorie nach Code"""
        return PatternManager.get_category_by_code(code)

    # =========================================================================
    # PATTERNS (Rechenmuster)
    # =========================================================================

    @staticmethod
    def get_patterns(
        category_code: str = None,
        ihk_only: bool = False,
        difficulty: int = None,
        active_only: bool = True
    ) -> List[Dict]:
        """Holt Rechenmuster mit optionalen Filtern"""
        return PatternManager.get_patterns(
            category_code, ihk_only, difficulty, active_only
        )

    @staticmethod
    def get_pattern_by_id(pattern_id: str) -> Optional[Dict]:
        """Holt ein Muster mit allen Details"""
        return PatternManager.get_pattern_by_id(pattern_id)

    @staticmethod
    def get_pattern_by_code(pattern_code: str) -> Optional[Dict]:
        """Holt ein Muster nach Code"""
        return PatternManager.get_pattern_by_code(pattern_code)

    # =========================================================================
    # FORMULAS (Formel-Bibliothek)
    # =========================================================================

    @staticmethod
    def get_formulas(
        category_code: str = None,
        favorites_only: bool = False
    ) -> List[Dict]:
        """Holt Formeln aus der Bibliothek"""
        return PatternManager.get_formulas(category_code, favorites_only)

    @staticmethod
    def increment_formula_usage(formula_id: str) -> bool:
        """Erhöht den Nutzungszähler einer Formel"""
        return PatternManager.increment_formula_usage(formula_id)

    @staticmethod
    def toggle_formula_favorite(formula_id: str) -> Optional[bool]:
        """Toggled Favoriten-Status einer Formel"""
        return PatternManager.toggle_formula_favorite(formula_id)

    # =========================================================================
    # SESSIONS
    # =========================================================================

    @staticmethod
    def start_session(
        user_id: str,
        session_type: str = 'practice',
        pattern_id: str = None,
        scaffolding_level: int = 1,
        course_id: str = None,
        lesson_id: str = None
    ) -> Optional[str]:
        """Startet eine neue Toolkit-Session"""
        return SessionManager.start_session(
            user_id, session_type, pattern_id, scaffolding_level,
            course_id, lesson_id
        )

    @staticmethod
    def end_session(session_id: str) -> bool:
        """Beendet eine Session"""
        return SessionManager.end_session(session_id)

    @staticmethod
    def get_session(session_id: str) -> Optional[Dict]:
        """Holt Session-Details"""
        return SessionManager.get_session(session_id)

    @staticmethod
    def update_session_stats(
        session_id: str,
        tasks_completed: int = None,
        tasks_correct: int = None,
        hints_used: int = None
    ) -> bool:
        """Aktualisiert Session-Statistiken"""
        return SessionManager.update_session_stats(
            session_id, tasks_completed, tasks_correct, hints_used
        )

    # =========================================================================
    # CALCULATION STEPS
    # =========================================================================

    @staticmethod
    def save_calculation_step(
        session_id: str,
        step_number: int,
        input_expression: str,
        input_values: Dict = None,
        result_value: float = None,
        result_display: str = None,
        calculator_keystrokes: List[str] = None,
        is_correct: bool = None,
        expected_value: float = None,
        error_type: str = None,
        hint_shown: str = None
    ) -> Optional[str]:
        """Speichert einen Rechenschritt"""
        return StepRecorder.save_calculation_step(
            session_id, step_number, input_expression, input_values,
            result_value, result_display, calculator_keystrokes,
            is_correct, expected_value, error_type, hint_shown
        )

    @staticmethod
    def get_session_steps(session_id: str) -> List[Dict]:
        """Holt alle Schritte einer Session"""
        return StepRecorder.get_session_steps(session_id)

    # =========================================================================
    # CALCULATOR
    # =========================================================================

    @staticmethod
    def evaluate_expression(expression: str) -> Dict[str, Any]:
        """Wertet einen mathematischen Ausdruck aus"""
        return MathSolver.evaluate_expression(expression)

    @staticmethod
    def save_calculator_entry(
        user_id: str,
        expression: str,
        result: float,
        result_display: str,
        session_id: str = None,
        keystrokes: List[str] = None,
        memory_used: bool = False,
        memory_value: float = None
    ) -> Optional[str]:
        """Speichert Taschenrechner-Eingabe"""
        return CalculatorHistory.save_calculator_entry(
            user_id, expression, result, result_display,
            session_id, keystrokes, memory_used, memory_value
        )

    @staticmethod
    def get_calculator_history(user_id: str, limit: int = 50) -> List[Dict]:
        """Holt Taschenrechner-Verlauf"""
        return CalculatorHistory.get_calculator_history(user_id, limit)

    # =========================================================================
    # USER PROGRESS
    # =========================================================================

    @staticmethod
    def get_user_progress(
        user_id: str,
        pattern_id: str = None
    ) -> List[Dict]:
        """Holt User-Fortschritt (optional gefiltert)"""
        return ProgressTracker.get_user_progress(user_id, pattern_id)

    @staticmethod
    def update_user_progress(
        user_id: str,
        pattern_id: str,
        is_correct: bool,
        update_level: bool = True
    ) -> Dict:
        """Aktualisiert User-Fortschritt nach einer Aufgabe"""
        return ProgressTracker.update_user_progress(
            user_id, pattern_id, is_correct, update_level
        )

    # =========================================================================
    # SCAFFOLDING HINTS
    # =========================================================================

    @staticmethod
    def get_hint(
        pattern_id: str,
        hint_type: str,
        scaffolding_level: int,
        step_number: int = None,
        error_type: str = None
    ) -> Optional[str]:
        """Holt passenden Hint basierend auf Kontext und Level"""
        return HintProvider.get_hint(
            pattern_id, hint_type, scaffolding_level, step_number, error_type
        )

    # =========================================================================
    # PATTERN RECOGNITION TASKS
    # =========================================================================

    @staticmethod
    def get_pattern_tasks(
        pattern_id: str = None,
        task_type: str = None,
        difficulty: int = None,
        limit: int = 10
    ) -> List[Dict]:
        """Holt Muster-Erkennungs-Aufgaben"""
        return TaskManager.get_pattern_tasks(
            pattern_id, task_type, difficulty, limit
        )

    @staticmethod
    def check_pattern_task_answer(task_id: str, user_answer: Any) -> Dict:
        """Prüft Antwort auf eine Muster-Aufgabe"""
        return TaskManager.check_pattern_task_answer(task_id, user_answer)

    # =========================================================================
    # ADMIN: Pattern & Formula Management
    # =========================================================================

    @staticmethod
    def create_pattern(
        pattern_code: str,
        name: str,
        category_code: str,
        formula_template: str,
        variables: List[Dict],
        steps_template: List[Dict],
        **kwargs
    ) -> Optional[str]:
        """Erstellt ein neues Rechenmuster"""
        return PatternManager.create_pattern(
            pattern_code, name, category_code, formula_template,
            variables, steps_template, **kwargs
        )

    @staticmethod
    def create_formula(
        name: str,
        formula_text: str,
        category_code: str = None,
        **kwargs
    ) -> Optional[str]:
        """Erstellt eine neue Formel"""
        return PatternManager.create_formula(
            name, formula_text, category_code, **kwargs
        )
