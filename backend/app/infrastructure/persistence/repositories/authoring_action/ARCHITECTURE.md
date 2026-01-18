# Authoring Action Repository - Architecture Guide

## Overview

The `authoring_action` package provides database access for authoring actions (Quick-Actions) used in the KI-Studio. It replaces hardcoded buttons with flexible, database-driven actions.

## Package Structure

```
repositories/authoring_action/
├── __init__.py              # Main interface (AuthoringActionRepository)
├── crud.py                  # Create, Update, Delete, Duplicate
├── queries.py               # Find & retrieve operations
├── analytics.py             # Usage tracking & statistics
├── reorder.py               # Display order management
└── ARCHITECTURE.md          # This file
```

## Design Pattern: Modular Repository with Unified Interface

### Problem Solved
- Original file: 556 LOC monolithic class
- Issue: Single file exceeds 500 LOC maintainability limit
- Solution: Split into 4 focused modules + 1 unified interface

### Pattern Benefits
1. **Single Responsibility:** Each module has one clear purpose
2. **Maintainability:** Smaller files easier to understand and modify
3. **Testability:** Can test each module independently
4. **Scalability:** Easy to add new modules (e.g., caching, validation)
5. **Backward Compatibility:** Bridge module maintains old import paths

## Module Responsibilities

### `crud.py` - Create, Update, Delete, Duplicate
**Responsibility:** Mutating operations

**When to Use:**
- Creating new actions: `AuthoringActionRepository.create(data)`
- Updating action properties: `AuthoringActionRepository.update(id, updates)`
- Deleting actions: `AuthoringActionRepository.delete(id)`
- Cloning actions: `AuthoringActionRepository.duplicate(id, new_key)`

**Key Features:**
- JSON serialization for JSONB fields
- Whitelist validation for update fields
- System action protection
- Full parameterized SQL

---

### `queries.py` - Find & Retrieve
**Responsibility:** Read-only query operations

**When to Use:**
- Looking up single actions: `find_by_id()`, `find_by_key()`
- Filtering by category: `get_by_category(category)`
- Getting all actions: `get_all_active()`
- Filtering by entity type: `get_by_context_entity(entity)`
- Filtering by learning method: `get_by_lm_type(lm_type)`
- Getting statistics: `get_categories()`

**Key Features:**
- DRY SELECT fields constant
- Consistent ordering
- Role-based filtering
- Always returns active actions (unless explicitly looking by ID)

---

### `analytics.py` - Usage Tracking
**Responsibility:** Usage metrics and statistics

**When to Use:**
- Recording action execution: `log_usage(action_id, user_id, ...)`
- Getting statistics: `get_usage_stats(action_id, days=30)`
- Finding popular actions: `get_popular_actions(limit=10, days=30)`

**Key Features:**
- Time-windowed analytics
- Token and cost tracking
- Response time metrics
- System-wide vs. single-action stats

---

### `reorder.py` - Display Order
**Responsibility:** Bulk reordering operations

**When to Use:**
- Updating action order after drag-and-drop: `reorder(category, updates)`

**Key Features:**
- Category-scoped updates
- Batch operation capability

---

## Usage Examples

### Import Patterns

```python
# ✓ RECOMMENDED (new code)
from app.repositories.authoring_action import AuthoringActionRepository

# ✓ ALSO WORKS (backward compatible)
from app.repositories.authoring_action_repository import AuthoringActionRepository

# ✓ ADVANCED (direct sub-module import)
from app.repositories.authoring_action.queries import AuthoringActionQueries
from app.repositories.authoring_action.crud import AuthoringActionCRUD
```

### Common Operations

```python
from app.repositories.authoring_action import AuthoringActionRepository

# ========== CRUD ==========

# Create
action = AuthoringActionRepository.create({
    'action_key': 'suggest_title',
    'category': 'course_builder',
    'label': 'Title vorschlagen',
    'description': 'KI schlägt einen Kurstitel vor',
    'prompt_template': 'Suggest a course title...',
    'mode': 'stream',
    'context_entity': 'course',
    'requires_context': {'course_id': 'uuid'},
    'model': 'claude-3-5-sonnet',
    'provider': 'anthropic',
    'output_format': 'text',
    'created_by': user_id
})

# Update
updated = AuthoringActionRepository.update(action['action_id'], {
    'label': 'Improved Label',
    'is_active': True
})

# Delete
deleted = AuthoringActionRepository.delete(action['action_id'])

# Duplicate
copy = AuthoringActionRepository.duplicate(
    action['action_id'],
    new_key='suggest_title_v2',
    created_by=user_id
)

# ========== QUERIES ==========

# Find single action
action = AuthoringActionRepository.find_by_id(action_id)
action = AuthoringActionRepository.find_by_key('suggest_title')

# Get filtered lists
actions = AuthoringActionRepository.get_by_category('course_builder', roles=['admin'])
actions = AuthoringActionRepository.get_all_active(roles=['admin', 'creator'])
actions = AuthoringActionRepository.get_by_context_entity('course')
actions = AuthoringActionRepository.get_by_lm_type(0)  # LM00

# Get statistics
categories = AuthoringActionRepository.get_categories()
# Returns: [
#   {'category': 'course_builder', 'action_count': 5, 'system_count': 2},
#   {'category': 'chat', 'action_count': 8, 'system_count': 1},
#   ...
# ]

# ========== ANALYTICS ==========

# Log usage
AuthoringActionRepository.log_usage(
    action_id=action_id,
    user_id=user_id,
    session_id=session_id,
    context_data={'course_id': course_id},
    was_successful=True,
    was_confirmed=True,
    result_entity_id=created_id,
    tokens_input=150,
    tokens_output=200,
    cost_eur=0.0015,
    response_time_ms=1234
)

# Get statistics
stats = AuthoringActionRepository.get_usage_stats(action_id, days=30)
# Returns: {
#   'total_uses': 42,
#   'successful_uses': 40,
#   'confirmed_uses': 38,
#   'total_tokens': 8500,
#   'total_cost': 0.12,
#   'avg_response_time': 1150
# }

# Get system-wide stats
stats = AuthoringActionRepository.get_usage_stats(days=7)
# Returns: {..., 'actions_used': 12, 'unique_users': 34}

# Get popular actions
popular = AuthoringActionRepository.get_popular_actions(limit=10, days=30)
# Returns: [
#   {
#       'action_id': '...', 'action_key': 'suggest_title',
#       'category': 'course_builder', 'label': 'Title vorschlagen',
#       'icon': 'sparkles', 'usage_count': 42, 'success_count': 40
#   },
#   ...
# ]

# ========== REORDER ==========

# Reorder actions in a category
AuthoringActionRepository.reorder('course_builder', [
    {'action_id': 'uuid1', 'order_index': 0},
    {'action_id': 'uuid2', 'order_index': 1},
    {'action_id': 'uuid3', 'order_index': 2}
])
```

## Database Schema Reference

### Main Table: `learning_methods.authoring_actions`

| Column | Type | Notes |
|--------|------|-------|
| action_id | UUID | Primary key |
| action_key | VARCHAR | Unique identifier |
| category | VARCHAR | course_builder, chat, chapter, lesson, method, content |
| label | VARCHAR | Human-readable name |
| description | TEXT | Action description |
| icon | VARCHAR | Icon identifier |
| color | VARCHAR | Color code |
| prompt_template | TEXT | KI prompt template |
| mode | VARCHAR | execution mode (stream, complete, etc.) |
| context_entity | VARCHAR | course, chapter, lesson, method |
| requires_context | JSONB | Required context fields |
| variables | JSONB | Template variables |
| action_type | VARCHAR | chat, tool, etc. |
| requires_confirmation | BOOLEAN | Show confirmation dialog |
| confirmation_label | VARCHAR | Confirmation button text |
| model | VARCHAR | KI model name |
| provider | VARCHAR | anthropic, openai, etc. |
| temperature | FLOAT | KI temperature |
| max_tokens | INT | Max tokens to generate |
| output_format | VARCHAR | text, json, markdown |
| output_entity | VARCHAR | Target entity type for output |
| output_schema | JSONB | Schema for output validation |
| lm_types | INT[] | Applicable learning method IDs |
| roles_allowed | TEXT[] | Roles that can use this |
| is_premium | BOOLEAN | Requires premium plan |
| order_index | INT | Display order |
| is_system | BOOLEAN | System action (can't delete) |
| is_active | BOOLEAN | Soft delete flag |
| created_at | TIMESTAMP | Creation timestamp |
| created_by | UUID | Creator user ID |
| updated_at | TIMESTAMP | Last update timestamp |
| updated_by | UUID | Last update user ID |

### Usage Table: `learning_methods.authoring_action_usage`

| Column | Type | Notes |
|--------|------|-------|
| usage_id | UUID | Primary key |
| action_id | UUID | FK to authoring_actions |
| user_id | UUID | Who executed action |
| session_id | UUID | Optional authoring session |
| context_data | JSONB | Context when triggered |
| was_successful | BOOLEAN | Execution success |
| was_confirmed | BOOLEAN | User confirmation |
| result_entity_id | UUID | Created/modified entity |
| tokens_input | INT | Input tokens |
| tokens_output | INT | Output tokens |
| tokens_total | INT | Sum of input + output |
| cost_eur | DECIMAL | Cost in EUR |
| response_time_ms | INT | Generation time |
| created_at | TIMESTAMP | Timestamp |

## Testing

### Unit Test Structure

```python
# tests/test_repositories/test_authoring_action/
├── test_crud.py         # Test AuthoringActionCRUD
├── test_queries.py      # Test AuthoringActionQueries
├── test_analytics.py    # Test AuthoringActionAnalytics
├── test_reorder.py      # Test AuthoringActionReorder
└── test_integration.py  # Test unified interface
```

### Mock Example

```python
from unittest.mock import patch
from app.repositories.authoring_action.queries import AuthoringActionQueries

@patch('app.repositories.authoring_action.queries.fetch_all')
def test_get_by_category(mock_fetch_all):
    mock_fetch_all.return_value = [
        {'action_id': '...', 'label': 'Action 1'},
        {'action_id': '...', 'label': 'Action 2'}
    ]

    actions = AuthoringActionQueries.get_by_category('course_builder')
    assert len(actions) == 2
    assert actions[0]['label'] == 'Action 1'
```

## Performance Considerations

### Query Optimization
- All queries use indexed columns (action_key, action_id)
- No N+1 queries (methods are atomic)
- JOIN in get_popular_actions is optimized with LEFT JOIN

### Scalability
- No in-memory caching (relies on PostgreSQL)
- Batch operations supported (reorder)
- Time-windowed analytics (no full table scans)

### Future Enhancements
- Add query caching layer
- Add batch insert/update operations
- Add full-text search for actions
- Add monitoring/metrics collection

## Related Files

- **API Layer:** `/app/api/admin/ai_authoring/actions.py` (uses this repository)
- **Database:** `migrations/03_AI/061_authoring_actions.sql`
- **Tests:** `tests/test_repositories/test_authoring_action/`
- **Documentation:** `LernsystemX-Doku/04_KI/01_KI-Pipeline.md`

## Error Handling

All methods return:
- Single result: `Optional[Dict[str, Any]]` (None if not found)
- Multiple results: `List[Dict[str, Any]]` (empty list if none found)
- Boolean: `True` on success, `False` on failure
- Stats: `Dict[str, Any]` (empty dict as fallback)

No exceptions are raised - callers should always check return values.

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-07 | Initial refactoring from monolithic 556 LOC file |

---

**Last Updated:** 2026-01-07
**Status:** Production Ready
