"""
MathToolkit Service - Dynamisches Mathe-Lern-System

Funktionen:
- Taschenrechner mit Verlauf
- Rechenweg-Builder (Schritt-für-Schritt)
- Muster-Erkennung (Pattern Recognition)
- Tutorial-Modus mit Scaffolding
- Formel-Bibliothek
- User-Fortschritt & Mastery

Alles dynamisch über DB konfigurierbar, nichts hardcoded!
"""

from typing import List, Dict, Optional, Any
from decimal import Decimal, InvalidOperation
import math
import re
import logging
from uuid import UUID

from app.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class MathToolkitService:
    """Service für das Mathe-Toolkit System"""

    # =========================================================================
    # PATTERN CATEGORIES
    # =========================================================================

    @staticmethod
    def get_categories(active_only: bool = True) -> List[Dict]:
        """Holt alle Muster-Kategorien"""
        query = """
            SELECT category_id, category_code, name, description, icon, color, sort_order
            FROM math_pattern_categories
            WHERE ($1 = FALSE OR is_active = TRUE)
            ORDER BY sort_order, name
        """
        return BaseRepository.fetch_all(query, (active_only,)) or []

    @staticmethod
    def get_category_by_code(code: str) -> Optional[Dict]:
        """Holt Kategorie nach Code"""
        query = """
            SELECT category_id, category_code, name, description, icon, color
            FROM math_pattern_categories
            WHERE category_code = %s AND is_active = TRUE
        """
        return BaseRepository.fetch_one(query, (code,))

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
        query = """
            SELECT
                p.pattern_id, p.pattern_code, p.name, p.description,
                p.formula_template, p.formula_latex,
                p.variables, p.steps_template, p.example_values,
                p.difficulty, p.ihk_relevant, p.tags,
                c.category_code, c.name as category_name, c.icon as category_icon
            FROM math_patterns p
            LEFT JOIN math_pattern_categories c ON p.category_id = c.category_id
            WHERE ($1 = FALSE OR p.is_active = TRUE)
              AND ($2::text IS NULL OR c.category_code = $2)
              AND ($3 = FALSE OR p.ihk_relevant = TRUE)
              AND ($4::int IS NULL OR p.difficulty = $4)
            ORDER BY c.sort_order, p.sort_order, p.name
        """
        return BaseRepository.fetch_all(query, (active_only, category_code, ihk_only, difficulty)) or []

    @staticmethod
    def get_pattern_by_id(pattern_id: str) -> Optional[Dict]:
        """Holt ein Muster mit allen Details"""
        query = """
            SELECT
                p.pattern_id, p.pattern_code, p.name, p.description,
                p.formula_template, p.formula_latex,
                p.variables, p.steps_template, p.example_values,
                p.difficulty, p.ihk_relevant, p.tags,
                c.category_code, c.name as category_name, c.icon as category_icon
            FROM math_patterns p
            LEFT JOIN math_pattern_categories c ON p.category_id = c.category_id
            WHERE p.pattern_id = %s
        """
        return BaseRepository.fetch_one(query, (pattern_id,))

    @staticmethod
    def get_pattern_by_code(pattern_code: str) -> Optional[Dict]:
        """Holt ein Muster nach Code"""
        query = """
            SELECT
                p.pattern_id, p.pattern_code, p.name, p.description,
                p.formula_template, p.formula_latex,
                p.variables, p.steps_template, p.example_values,
                p.difficulty, p.ihk_relevant, p.tags,
                c.category_code, c.name as category_name
            FROM math_patterns p
            LEFT JOIN math_pattern_categories c ON p.category_id = c.category_id
            WHERE p.pattern_code = %s AND p.is_active = TRUE
        """
        return BaseRepository.fetch_one(query, (pattern_code,))

    # =========================================================================
    # FORMULAS (Formel-Bibliothek)
    # =========================================================================

    @staticmethod
    def get_formulas(category_code: str = None, favorites_only: bool = False) -> List[Dict]:
        """Holt Formeln aus der Bibliothek"""
        query = """
            SELECT
                f.formula_id, f.name, f.description,
                f.formula_text, f.formula_latex, f.formula_display,
                f.variables, f.example_input, f.example_output,
                f.is_favorite, f.usage_count,
                c.category_code, c.name as category_name, c.icon as category_icon
            FROM math_formulas f
            LEFT JOIN math_pattern_categories c ON f.category_id = c.category_id
            WHERE f.is_active = TRUE
              AND ($1::text IS NULL OR c.category_code = $1)
              AND ($2 = FALSE OR f.is_favorite = TRUE)
            ORDER BY f.is_favorite DESC, f.usage_count DESC, f.name
        """
        return BaseRepository.fetch_all(query, (category_code, favorites_only)) or []

    @staticmethod
    def increment_formula_usage(formula_id: str) -> bool:
        """Erhöht den Nutzungszähler einer Formel"""
        query = """
            UPDATE math_formulas
            SET usage_count = usage_count + 1
            WHERE formula_id = %s
        """
        return BaseRepository.execute(query, (formula_id,))

    @staticmethod
    def toggle_formula_favorite(formula_id: str) -> Optional[bool]:
        """Toggled Favoriten-Status einer Formel"""
        query = """
            UPDATE math_formulas
            SET is_favorite = NOT is_favorite
            WHERE formula_id = %s
            RETURNING is_favorite
        """
        result = BaseRepository.fetch_one(query, (formula_id,))
        return result.get('is_favorite') if result else None

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
        query = """
            INSERT INTO math_toolkit_sessions
                (user_id, session_type, pattern_id, scaffolding_level, course_id, lesson_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING session_id
        """
        result = BaseRepository.fetch_one(query, (
            user_id, session_type, pattern_id, scaffolding_level, course_id, lesson_id
        ))
        return str(result['session_id']) if result else None

    @staticmethod
    def end_session(session_id: str) -> bool:
        """Beendet eine Session"""
        query = """
            UPDATE math_toolkit_sessions
            SET ended_at = NOW()
            WHERE session_id = %s AND ended_at IS NULL
        """
        return BaseRepository.execute(query, (session_id,))

    @staticmethod
    def get_session(session_id: str) -> Optional[Dict]:
        """Holt Session-Details"""
        query = """
            SELECT
                s.session_id, s.user_id, s.session_type,
                s.scaffolding_level, s.started_at, s.ended_at,
                s.tasks_completed, s.tasks_correct, s.hints_used,
                p.pattern_code, p.name as pattern_name
            FROM math_toolkit_sessions s
            LEFT JOIN math_patterns p ON s.pattern_id = p.pattern_id
            WHERE s.session_id = %s
        """
        return BaseRepository.fetch_one(query, (session_id,))

    @staticmethod
    def update_session_stats(
        session_id: str,
        tasks_completed: int = None,
        tasks_correct: int = None,
        hints_used: int = None
    ) -> bool:
        """Aktualisiert Session-Statistiken"""
        updates = []
        params = []

        if tasks_completed is not None:
            updates.append("tasks_completed = %s")
            params.append(tasks_completed)
        if tasks_correct is not None:
            updates.append("tasks_correct = %s")
            params.append(tasks_correct)
        if hints_used is not None:
            updates.append("hints_used = %s")
            params.append(hints_used)

        if not updates:
            return False

        params.append(session_id)
        query = f"""
            UPDATE math_toolkit_sessions
            SET {', '.join(updates)}
            WHERE session_id = %s
        """
        return BaseRepository.execute(query, tuple(params))

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
        query = """
            INSERT INTO math_calculation_steps
                (session_id, step_number, input_expression, input_values,
                 result_value, result_display, calculator_keystrokes,
                 is_correct, expected_value, error_type, hint_shown)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING step_id
        """
        import json
        result = BaseRepository.fetch_one(query, (
            session_id, step_number, input_expression,
            json.dumps(input_values or {}),
            result_value, result_display,
            json.dumps(calculator_keystrokes or []),
            is_correct, expected_value, error_type, hint_shown
        ))
        return str(result['step_id']) if result else None

    @staticmethod
    def get_session_steps(session_id: str) -> List[Dict]:
        """Holt alle Schritte einer Session"""
        query = """
            SELECT
                step_id, step_number, input_expression, input_values,
                result_value, result_display, calculator_keystrokes,
                is_correct, expected_value, error_type, hint_shown,
                created_at
            FROM math_calculation_steps
            WHERE session_id = %s
            ORDER BY step_number
        """
        return BaseRepository.fetch_all(query, (session_id,)) or []

    # =========================================================================
    # CALCULATOR
    # =========================================================================

    @staticmethod
    def evaluate_expression(expression: str) -> Dict[str, Any]:
        """
        Wertet einen mathematischen Ausdruck aus.
        Sicher - keine eval() auf User-Input!
        """
        try:
            # Bereinige Expression
            expr = expression.strip()
            expr = expr.replace(',', '.')  # Deutsche Dezimalzahlen
            expr = expr.replace('×', '*').replace('÷', '/')
            expr = expr.replace('^', '**')

            # Prozent-Berechnung
            expr = re.sub(r'(\d+(?:\.\d+)?)\s*%\s*of\s*(\d+(?:\.\d+)?)',
                          r'(\1/100)*\2', expr, flags=re.IGNORECASE)

            # Nur erlaubte Zeichen
            if not re.match(r'^[\d\s\+\-\*\/\.\(\)\%\^]+$', expr):
                return {'success': False, 'error': 'Ungültige Zeichen im Ausdruck'}

            # Sichere Auswertung
            result = eval(expr, {"__builtins__": {}}, {
                'sqrt': math.sqrt,
                'pow': pow,
                'abs': abs,
                'round': round
            })

            # Formatierung
            if isinstance(result, float):
                # Runde auf 6 Dezimalstellen
                result = round(result, 6)
                # Entferne trailing zeros
                result_display = f"{result:g}"
            else:
                result_display = str(result)

            return {
                'success': True,
                'result': result,
                'display': result_display,
                'expression': expression
            }

        except ZeroDivisionError:
            return {'success': False, 'error': 'Division durch Null'}
        except Exception as e:
            logger.warning(f"Fehler bei Auswertung: {expression} - {e}")
            return {'success': False, 'error': 'Ungültiger Ausdruck'}

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
        query = """
            INSERT INTO math_calculator_history
                (user_id, session_id, expression, result, result_display,
                 keystrokes, memory_used, memory_value)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING history_id
        """
        import json
        result_row = BaseRepository.fetch_one(query, (
            user_id, session_id, expression, result, result_display,
            json.dumps(keystrokes or []), memory_used, memory_value
        ))
        return str(result_row['history_id']) if result_row else None

    @staticmethod
    def get_calculator_history(user_id: str, limit: int = 50) -> List[Dict]:
        """Holt Taschenrechner-Verlauf"""
        query = """
            SELECT history_id, expression, result, result_display, keystrokes,
                   memory_used, memory_value, created_at
            FROM math_calculator_history
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """
        return BaseRepository.fetch_all(query, (user_id, limit)) or []

    # =========================================================================
    # USER PROGRESS
    # =========================================================================

    @staticmethod
    def get_user_progress(user_id: str, pattern_id: str = None) -> List[Dict]:
        """Holt User-Fortschritt (optional gefiltert)"""
        query = """
            SELECT
                up.progress_id, up.current_level, up.total_attempts,
                up.correct_attempts, up.mastery_score,
                up.current_streak, up.best_streak,
                up.last_practiced_at, up.next_review_at,
                p.pattern_code, p.name as pattern_name,
                c.category_code, c.name as category_name
            FROM math_user_progress up
            JOIN math_patterns p ON up.pattern_id = p.pattern_id
            LEFT JOIN math_pattern_categories c ON p.category_id = c.category_id
            WHERE up.user_id = %s
              AND ($2::uuid IS NULL OR up.pattern_id = $2)
            ORDER BY up.mastery_score DESC, up.last_practiced_at DESC
        """
        return BaseRepository.fetch_all(query, (user_id, pattern_id)) or []

    @staticmethod
    def update_user_progress(
        user_id: str,
        pattern_id: str,
        is_correct: bool,
        update_level: bool = True
    ) -> Dict:
        """Aktualisiert User-Fortschritt nach einer Aufgabe"""
        # Hole aktuellen Fortschritt oder erstelle neuen
        query_get = """
            SELECT progress_id, current_level, total_attempts, correct_attempts,
                   mastery_score, current_streak, best_streak
            FROM math_user_progress
            WHERE user_id = %s AND pattern_id = %s
        """
        progress = BaseRepository.fetch_one(query_get, (user_id, pattern_id))

        if not progress:
            # Neu erstellen
            query_insert = """
                INSERT INTO math_user_progress (user_id, pattern_id)
                VALUES (%s, %s)
                RETURNING progress_id, current_level, total_attempts,
                          correct_attempts, mastery_score, current_streak, best_streak
            """
            progress = BaseRepository.fetch_one(query_insert, (user_id, pattern_id))

        # Berechne neue Werte
        total = progress['total_attempts'] + 1
        correct = progress['correct_attempts'] + (1 if is_correct else 0)
        streak = (progress['current_streak'] + 1) if is_correct else 0
        best_streak = max(progress['best_streak'], streak)

        # Mastery berechnen (gewichteter Durchschnitt der letzten Versuche)
        mastery = min(100, (correct / total) * 100) if total > 0 else 0

        # Level-Update (wenn genug Mastery)
        new_level = progress['current_level']
        if update_level:
            if mastery >= 80 and streak >= 3 and new_level < 3:
                new_level = min(3, new_level + 1)
            elif mastery < 40 and new_level > 1:
                new_level = max(1, new_level - 1)

        # Update
        query_update = """
            UPDATE math_user_progress
            SET current_level = %s,
                total_attempts = %s,
                correct_attempts = %s,
                mastery_score = %s,
                current_streak = %s,
                best_streak = %s,
                last_practiced_at = NOW(),
                next_review_at = NOW() + INTERVAL '1 day' * %s
            WHERE user_id = %s AND pattern_id = %s
        """
        # Spaced Repetition: je höher Mastery, desto später Review
        review_days = int(1 + (mastery / 20))
        BaseRepository.execute(query_update, (
            new_level, total, correct, mastery, streak, best_streak,
            review_days, user_id, pattern_id
        ))

        return {
            'current_level': new_level,
            'total_attempts': total,
            'correct_attempts': correct,
            'mastery_score': round(mastery, 1),
            'current_streak': streak,
            'best_streak': best_streak,
            'level_changed': new_level != progress['current_level']
        }

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
        query = """
            SELECT hint_level_1, hint_level_2, hint_level_3
            FROM math_scaffolding_hints
            WHERE pattern_id = %s
              AND hint_type = %s
              AND ($3::int IS NULL OR step_number = $3 OR step_number IS NULL)
              AND ($4::text IS NULL OR error_type = $4 OR error_type IS NULL)
              AND is_active = TRUE
            ORDER BY
                CASE WHEN step_number = $3 THEN 0 ELSE 1 END,
                CASE WHEN error_type = $4 THEN 0 ELSE 1 END
            LIMIT 1
        """
        result = BaseRepository.fetch_one(query, (pattern_id, hint_type, step_number, error_type))

        if not result:
            return None

        # Wähle Hint basierend auf Level
        if scaffolding_level == 1:
            return result['hint_level_1']
        elif scaffolding_level == 2:
            return result['hint_level_2'] or result['hint_level_1']
        else:
            return result['hint_level_3'] or "Versuche es nochmal!"

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
        query = """
            SELECT
                t.task_id, t.task_type, t.task_text, t.task_data,
                t.solution, t.difficulty,
                p.pattern_code, p.name as pattern_name
            FROM math_pattern_recognition_tasks t
            JOIN math_patterns p ON t.pattern_id = p.pattern_id
            WHERE t.is_active = TRUE
              AND ($1::uuid IS NULL OR t.pattern_id = $1)
              AND ($2::text IS NULL OR t.task_type = $2)
              AND ($3::int IS NULL OR t.difficulty = $3)
            ORDER BY RANDOM()
            LIMIT %s
        """
        return BaseRepository.fetch_all(query, (pattern_id, task_type, difficulty, limit)) or []

    @staticmethod
    def check_pattern_task_answer(task_id: str, user_answer: Any) -> Dict:
        """Prüft Antwort auf eine Muster-Aufgabe"""
        query = """
            SELECT task_type, solution
            FROM math_pattern_recognition_tasks
            WHERE task_id = %s
        """
        task = BaseRepository.fetch_one(query, (task_id,))

        if not task:
            return {'success': False, 'error': 'Aufgabe nicht gefunden'}

        solution = task['solution']
        is_correct = False

        # Vergleich je nach Aufgabentyp
        if task['task_type'] == 'identify_pattern':
            is_correct = str(user_answer).lower() == str(solution.get('pattern_code', '')).lower()
        elif task['task_type'] == 'order_steps':
            is_correct = user_answer == solution.get('correct_order', [])
        elif task['task_type'] == 'fill_formula':
            is_correct = str(user_answer).strip() == str(solution.get('answer', '')).strip()
        elif task['task_type'] == 'match_values':
            is_correct = user_answer == solution.get('matches', {})
        elif task['task_type'] == 'spot_error':
            is_correct = user_answer == solution.get('error_position')
        elif task['task_type'] == 'complete_calculation':
            try:
                is_correct = abs(float(user_answer) - float(solution.get('result', 0))) < 0.01
            except (ValueError, TypeError):
                is_correct = False

        return {
            'success': True,
            'is_correct': is_correct,
            'solution': solution if not is_correct else None,
            'feedback': solution.get('feedback', 'Richtig!' if is_correct else 'Leider falsch.')
        }

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
        import json

        # Hole category_id
        cat = MathToolkitService.get_category_by_code(category_code)
        if not cat:
            return None

        query = """
            INSERT INTO math_patterns
                (pattern_code, name, category_id, description,
                 formula_template, formula_latex, variables, steps_template,
                 example_values, difficulty, ihk_relevant, tags)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING pattern_id
        """
        result = BaseRepository.fetch_one(query, (
            pattern_code, name, cat['category_id'],
            kwargs.get('description'),
            formula_template,
            kwargs.get('formula_latex'),
            json.dumps(variables),
            json.dumps(steps_template),
            json.dumps(kwargs.get('example_values', {})),
            kwargs.get('difficulty', 1),
            kwargs.get('ihk_relevant', False),
            json.dumps(kwargs.get('tags', []))
        ))
        return str(result['pattern_id']) if result else None

    @staticmethod
    def create_formula(
        name: str,
        formula_text: str,
        category_code: str = None,
        **kwargs
    ) -> Optional[str]:
        """Erstellt eine neue Formel"""
        import json

        category_id = None
        if category_code:
            cat = MathToolkitService.get_category_by_code(category_code)
            category_id = cat['category_id'] if cat else None

        query = """
            INSERT INTO math_formulas
                (name, formula_text, category_id, description,
                 formula_latex, formula_display, variables,
                 example_input, example_output, tags)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING formula_id
        """
        result = BaseRepository.fetch_one(query, (
            name, formula_text, category_id,
            kwargs.get('description'),
            kwargs.get('formula_latex'),
            kwargs.get('formula_display'),
            json.dumps(kwargs.get('variables', [])),
            json.dumps(kwargs.get('example_input', {})),
            kwargs.get('example_output'),
            json.dumps(kwargs.get('tags', []))
        ))
        return str(result['formula_id']) if result else None
