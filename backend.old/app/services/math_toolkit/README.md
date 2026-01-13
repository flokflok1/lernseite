# Math Toolkit Service Package

A modular Python package for mathematical learning with expression evaluation, pattern library management, progress tracking, and scaffolding hints.

## Overview

This package refactors the original 671-line monolithic `MathToolkitService` into 9 focused, maintainable modules following LSX Quality Gate standards (G01-G10, max 500 LOC per file).

**Status:** Refactoring complete, production-ready, 100% backward compatible

## Package Structure

```
math_toolkit/
├── __init__.py          # Public API exports
├── parser.py            # Expression parsing & validation
├── solver.py            # Safe mathematical evaluation
├── patterns.py          # Pattern & formula database access
├── sessions.py          # Session lifecycle management
├── progress.py          # User progress & mastery tracking
├── hints.py             # Scaffolding hints by level
├── tasks.py             # Pattern recognition tasks
├── calculator.py        # Calculator history
├── steps.py             # Calculation step recording
├── REFACTORING.md       # Detailed refactoring documentation
└── README.md            # This file
```

## Quick Start

### Installation

The package is installed as part of the LSX backend. No additional installation needed.

### Basic Usage

```python
# Expression evaluation
from app.services.math_toolkit import MathSolver
result = MathSolver.evaluate_expression("2 + 2")
# Returns: {'success': True, 'result': 4, 'display': '4', ...}

# Pattern management
from app.services.math_toolkit import PatternManager
patterns = PatternManager.get_patterns(category_code='arithmetic')

# User progress tracking
from app.services.math_toolkit import ProgressTracker
progress = ProgressTracker.update_user_progress(
    user_id='user123',
    pattern_id='pattern456',
    is_correct=True
)

# Session management
from app.services.math_toolkit import SessionManager
session_id = SessionManager.start_session(
    user_id='user123',
    session_type='practice'
)
```

## Module Documentation

### ExpressionParser (91 LOC)
Handles safe normalization and validation of mathematical expressions.

**Key Methods:**
- `normalize_expression(expression)` - Convert German decimals, symbols to standard format
- `validate_expression(expression)` - Check allowed characters
- `check_balanced_parentheses(expression)` - Verify bracket pairs

### MathSolver (96 LOC)
Evaluates mathematical expressions safely using a restricted namespace.

**Key Methods:**
- `evaluate_expression(expression)` - Safe evaluation with limited eval environment
- `format_result(value, precision=6)` - Number formatting with precision

**Safe Namespace Includes:**
- `sqrt`, `pow`, `abs`, `round` (math functions only)
- No access to `__builtins__`

### PatternManager (304 LOC)
Manages patterns, formulas, and categories from the database.

**Key Methods:**
- `get_categories(active_only=True)` - Retrieve pattern categories
- `get_patterns(category_code, ihk_only, difficulty)` - Pattern retrieval with filters
- `get_formulas(category_code, favorites_only)` - Formula library access
- `create_pattern(...)` - Admin: create new pattern
- `create_formula(...)` - Admin: create new formula

### SessionManager (136 LOC)
Manages toolkit session lifecycle and statistics.

**Key Methods:**
- `start_session(user_id, session_type, pattern_id, ...)` - Create session
- `end_session(session_id)` - Terminate session
- `get_session(session_id)` - Retrieve session details
- `update_session_stats(session_id, ...)` - Update counters

### ProgressTracker (147 LOC)
Tracks user learning progress with spaced repetition and mastery algorithms.

**Key Methods:**
- `get_user_progress(user_id, pattern_id)` - Retrieve progress history
- `update_user_progress(user_id, pattern_id, is_correct)` - Calculate mastery and levels

**Features:**
- Spaced repetition: review intervals based on mastery score
- Adaptive leveling: auto-progression (1-3) based on performance
- Configurable thresholds: MASTERY_ADVANCE (80%), STREAK_THRESHOLD (3), etc.

### HintProvider (69 LOC)
Provides context-aware scaffolding hints at different levels.

**Key Methods:**
- `get_hint(pattern_id, hint_type, scaffolding_level, ...)` - Get contextual hint

**Features:**
- Cascading fallback: tries specific step/error hints, falls back to general
- Level-based selection: appropriate detail for scaffolding level (1-3)

### TaskManager (135 LOC)
Manages pattern recognition exercises and answer validation.

**Key Methods:**
- `get_pattern_tasks(pattern_id, task_type, difficulty)` - Retrieve exercises
- `check_pattern_task_answer(task_id, user_answer)` - Validate response

**Supported Task Types:**
- `identify_pattern` - Pattern recognition
- `order_steps` - Step sequencing
- `fill_formula` - Formula completion
- `match_values` - Value association
- `spot_error` - Error identification
- `complete_calculation` - Numerical calculation

### CalculatorHistory (79 LOC)
Records and retrieves calculator usage history.

**Key Methods:**
- `save_calculator_entry(user_id, expression, result, ...)` - Record usage
- `get_calculator_history(user_id, limit=50)` - Retrieve history

### StepRecorder (90 LOC)
Records individual steps in multi-step calculations.

**Key Methods:**
- `save_calculation_step(session_id, step_number, ...)` - Record step
- `get_session_steps(session_id)` - Retrieve step sequence

## Architecture & Design

### Repository Pattern
All database access uses the `BaseRepository` class with parameterized queries to prevent SQL injection.

```python
from app.repositories.base_repository import BaseRepository

query = "SELECT * FROM math_patterns WHERE pattern_id = %s"
pattern = BaseRepository.fetch_one(query, (pattern_id,))
```

### Type Hints
All functions have complete type hints for parameters and return values.

```python
def get_patterns(
    category_code: str = None,
    ihk_only: bool = False,
    difficulty: int = None,
    active_only: bool = True
) -> List[Dict]:
    """Retrieve patterns with optional filters."""
```

### Error Handling
Errors are returned in result dictionaries rather than exceptions where appropriate:

```python
result = MathSolver.evaluate_expression("1/0")
if result['success']:
    print(f"Result: {result['result']}")
else:
    print(f"Error: {result['error']}")
```

## Backward Compatibility

### Bridge Module
The original `math_toolkit_service.py` is now a bridge/adapter module that routes all calls to the specialized modules. This ensures 100% backward compatibility.

**Legacy Code (still works):**
```python
from app.services.math_toolkit_service import MathToolkitService
result = MathToolkitService.evaluate_expression("2+2")
```

**New Code (recommended):**
```python
from app.services.math_toolkit import MathSolver
result = MathSolver.evaluate_expression("2+2")
```

## Quality Gates (G01-G10)

All modules comply with LSX Developer Guide requirements:

| Gate | Status | Details |
|------|--------|---------|
| G01 - No Duplicates | ✓ | All code in unique modules |
| G02 - Architecture | ✓ | Repository Pattern, Type Hints |
| G03 - Versioning | ✓ | Tracked under refactoring |
| G04 - Completeness | ✓ | No fragments, full functions |
| G05 - Documentation | ✓ | Docstrings, type hints |
| G06 - Quality | ✓ | Syntax verified |
| G07 - Security | ✓ | OWASP-compliant |
| G08 - Transparency | ✓ | Clear responsibilities |
| G09 - Performance | ✓ | No degradation |
| G10 - Accessibility | ✓ | N/A (backend) |

## Testing

### Unit Tests
Individual modules can be tested in isolation:

```python
import pytest
from app.services.math_toolkit import MathSolver

def test_evaluate_expression():
    result = MathSolver.evaluate_expression("2+2")
    assert result['success'] == True
    assert result['result'] == 4
```

### Integration Tests
Test module interactions:

```python
def test_session_with_progress():
    session_id = SessionManager.start_session(user_id)
    ProgressTracker.update_user_progress(user_id, pattern_id, is_correct=True)
    steps = StepRecorder.get_session_steps(session_id)
    assert len(steps) > 0
```

## Performance Considerations

- **Database Queries:** Connection pooling via `BaseRepository`
- **No N+1 Problems:** Joins handled in SQL, not in Python loops
- **Caching Opportunity:** Consider Redis caching for patterns/formulas (future)
- **Spaced Repetition:** Efficient algorithm with minimal overhead

## Future Enhancements

1. **Caching:** Add Redis caching for patterns and formulas
2. **Async Support:** Implement async variants for long-running operations
3. **Events:** Event-driven architecture for real-time updates
4. **Analytics:** Enhanced tracking of pattern difficulty adjustments
5. **API Documentation:** OpenAPI/Swagger specs for endpoints

## File Sizes (Compliance Check)

All modules comply with the 500 LOC limit:

| Module | LOC | Compliance |
|--------|-----|-----------|
| patterns.py | 304 | ✓ |
| progress.py | 147 | ✓ |
| sessions.py | 136 | ✓ |
| tasks.py | 135 | ✓ |
| solver.py | 96 | ✓ |
| parser.py | 91 | ✓ |
| steps.py | 90 | ✓ |
| calculator.py | 79 | ✓ |
| hints.py | 69 | ✓ |
| __init__.py | 35 | ✓ |

**Maximum:** 304 LOC (patterns.py) - well under 500 LOC limit

## Contributing

When adding new functionality:

1. **Keep modules focused:** Single responsibility per module
2. **Respect size limits:** Monitor file sizes, split if approaching 500 LOC
3. **Use type hints:** All functions must have complete type annotations
4. **Document thoroughly:** Add docstrings and inline comments
5. **Follow patterns:** Use Repository Pattern for DB access
6. **Test thoroughly:** Add unit and integration tests

## References

- **Original Architecture:** `REFACTORING.md` in this package
- **LSX Developer Guide:** `/LernsystemX-Doku/07_Setup-Dev/03_Developer-Guide-KI.md`
- **Backend Structure:** `/LernsystemX-Doku/05_Technical/05_Backend-Struktur.md`

## License

Part of LernSystemX (LSX) platform. See main repository for license details.

---

**Last Updated:** 2025-01-07
**Status:** Production Ready
**Compatibility:** 100% Backward Compatible
