# Learning Method Repository Package

Modular repository for learning method operations. Originally 1139 LOC, refactored into 4 specialized repositories.

## Quick Start

### Import Specific Repositories
```python
from app.repositories.learning_method import (
    LearningMethodBaseRepository,      # CRUD
    LearningMethodAIRepository,        # AI execution
    LearningMethodFeedbackRepository,  # Feedback
    LearningMethodStatisticsRepository # Statistics
)
```

### Common Operations

**Get all methods:**
```python
methods = LearningMethodBaseRepository.get_all(active_only=True)
```

**Execute AI method:**
```python
result = LearningMethodAIRepository.execute_ai_method(
    user_id="user-123",
    method_id="method-456",
    user_input="Explain this topic",
    language="de"
)
# Returns: {execution_id, output_text, input_tokens, output_tokens, ...}
```

**Create feedback:**
```python
feedback = LearningMethodFeedbackRepository.create_feedback(
    user_id="user-123",
    execution_id="exec-789",
    rating=5,
    is_helpful=True
)
```

**Get token usage:**
```python
stats = LearningMethodStatisticsRepository.get_user_token_usage(
    user_id="user-123",
    period_days=30
)
# Returns: {total_tokens, total_cost_eur, by_method, by_provider, ...}
```

## Module Structure

| Module | LOC | Purpose | Key Classes |
|--------|-----|---------|------------|
| `types.py` | 72 | Type definitions | `AIExecutionResult`, `TokenUsageStats`, etc. |
| `base.py` | 274 | CRUD operations | `LearningMethodBaseRepository` |
| `ai_execution.py` | 539 | AI execution | `LearningMethodAIRepository` |
| `feedback.py` | 182 | Feedback analytics | `LearningMethodFeedbackRepository` |
| `statistics.py` | 296 | Usage reporting | `LearningMethodStatisticsRepository` |

## Repository Methods

### LearningMethodBaseRepository (CRUD)

| Method | Returns | Purpose |
|--------|---------|---------|
| `get_all(active_only, use_cache)` | `List[Dict]` | All methods with optional caching |
| `find_by_id(method_id)` | `Dict \| None` | Get method by UUID |
| `find_by_name(name)` | `Dict \| None` | Get method by title |
| `create(method_data)` | `Dict` | Create new method |
| `update(method_id, data)` | `Dict \| None` | Update method |
| `delete(method_id)` | `bool` | Remove method |
| `activate(method_id)` | `Dict \| None` | Publish method |
| `deactivate(method_id)` | `Dict \| None` | Unpublish method |

### LearningMethodAIRepository (AI Execution)

| Method | Purpose |
|--------|---------|
| `execute_ai_method()` | Full AI execution with token tracking |
| `_build_method_prompt()` | Generate method-specific prompt |
| `log_token_usage()` | Record token consumption for billing |

**Supported Methods (by LM-ID):**
- LM0: Deep Explanation
- LM1: Step-by-Step
- LM12: Math Interactive
- LM13: Flashcards
- LM19: IHK-Style Tasks
- LM22: Exam Quiz

### LearningMethodFeedbackRepository (Feedback)

| Method | Returns |
|--------|---------|
| `create_feedback()` | Feedback record |
| `get_method_feedback()` | List of feedback |
| `get_feedback_stats()` | Aggregated stats (avg rating, etc.) |

### LearningMethodStatisticsRepository (Statistics)

| Method | Returns |
|--------|---------|
| `get_user_token_usage()` | Token consumption by user/method/provider |
| `get_lesson_executions()` | Execution history for lesson |
| `delete_execution()` | Boolean success |
| `get_statistics()` | Overall system statistics |

## Backward Compatibility

Old imports still work:
```python
# Deprecated but still functional
from app.repositories.learning_method_repository import LearningMethodRepository

# All methods available (delegate to sub-repositories)
LearningMethodRepository.find_by_id(method_id)
LearningMethodRepository.execute_ai_method(...)
```

## Architecture

```
BaseRepository (psycopg connection pooling)
         ↓
    4 Specialized Repositories
         ↓
    Bridge Module (backward compat)
```

All repositories use:
- **Direct SQL** with psycopg3 (no ORM)
- **Parameterized queries** (SQL injection prevention)
- **JSONB** for config fields
- **Type hints** on all methods

## Database Tables

- `learning_methods` - Method definitions
- `learning_method_executions` - Execution history with token usage
- `ai_feedback` - User feedback on executions
- `ai_token_usage` - Token tracking for billing

## Error Handling

```python
from app.services.ai_adapter import AIProviderError, AITimeoutError

try:
    result = LearningMethodAIRepository.execute_ai_method(...)
except ValueError as e:
    # Method not found or not active
    print(f"Invalid method: {e}")
except AIProviderError as e:
    # AI provider error
    print(f"AI error: {e}")
except AITimeoutError:
    # Request timeout
    print("AI request timed out")
```

## Performance

- **Caching:** `get_all()` cached (default 3600s)
- **Connection pooling:** All DB operations use pool
- **Pagination:** Large result sets use LIMIT
- **Token tracking:** Asynchronous logging

## Testing

Each module can be tested independently:

```python
# Test CRUD
assert LearningMethodBaseRepository.find_by_id(method_id) is not None

# Test AI execution
result = LearningMethodAIRepository.execute_ai_method(...)
assert result['output_text']
assert result['total_tokens'] > 0

# Test feedback
feedback = LearningMethodFeedbackRepository.create_feedback(...)
assert feedback['rating'] == 5

# Test statistics
stats = LearningMethodStatisticsRepository.get_statistics()
assert stats['total_methods'] > 0
```

## See Also

- `/REFACTORING_SUMMARY.md` - Complete refactoring details
- `backend/app/repositories/base_repository.py` - Base class for connection pooling
- `backend/app/services/ai_adapter.py` - AI provider integration
- `backend/app/services/cache_service.py` - Caching logic
