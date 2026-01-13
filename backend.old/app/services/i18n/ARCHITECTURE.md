# i18n Package Architecture

## Package Overview

```
services/i18n/ (modular i18n service package)
│
├── __init__.py
│   └── Exports: TranslationManager, LanguageManager, KeyManager,
│                 SuggestionManager, AITranslationGenerator, ConfigManager
│
├── bridge.py (I18nService facade - BACKWARD COMPATIBLE)
│   │
│   ├──→ TranslationManager (translations.py)
│   │    └─ get_bundle, get_key_translations, set_translation, invalidate_cache
│   │
│   ├──→ LanguageManager (languages.py)
│   │    └─ get_primary_language, get_languages, get_language_progress
│   │
│   ├──→ KeyManager (keys.py)
│   │    └─ get_namespaces, get_keys, create_key
│   │
│   ├──→ SuggestionManager (suggestions.py)
│   │    └─ submit_suggestion, vote_suggestion, get_suggestions, request_translation
│   │
│   ├──→ AITranslationGenerator (ai_generation.py)
│   │    └─ generate_ai_translation, bulk_generate_translations
│   │
│   └──→ ConfigManager (config.py)
│        └─ get_ai_config, update_ai_config, get_moderation_dashboard
│
└── services/i18n_service.py (minimal bridge re-export)
    └── from app.services.i18n.bridge import I18nService
```

## Module Interaction Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  API Layer (app/api/i18n/*.py)                                   │
│  - public.py, keys.py, suggestions.py, ai_translation.py, etc.   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
          ┌──────────────────────────────┐
          │  I18nService (bridge.py)     │  ← Import point
          │  (30 static methods)         │     from app.services.i18n_service
          └──────────────────────────────┘

     ┌─────────┬──────────┬───────┬──────────┬────────┬────────┐
     │          │          │       │          │        │        │
     ▼          ▼          ▼       ▼          ▼        ▼        ▼
┌─────────┐ ┌────────┐ ┌─────┐ ┌──────────┐ ┌──────┐ ┌──────┐ ┌──────┐
│ Trans   │ │ Lang   │ │ Key │ │ Suggest  │ │ AI   │ │ Config│ │Cache │
│ Manager │ │Manager │ │Mgr  │ │ Manager  │ │ Gen  │ │Manager│ │Svc   │
└─────────┘ └────────┘ └─────┘ └──────────┘ └──────┘ └──────┘ └──────┘
     │          │          │       │          │        │        │
     └─────────┬┴──────────┴───────┴──────────┴────────┴────────┘
               │
               ▼
    ┌──────────────────────┐
    │  Cache Service       │
    │  (Redis)             │
    └──────────────────────┘
               │
               ▼
    ┌──────────────────────┐
    │  Database            │
    │  (PostgreSQL)        │
    │  - i18n_keys         │
    │  - i18n_translations │
    │  - i18n_suggestions  │
    │  - supported_langs   │
    │  - i18n_namespaces   │
    │  - i18n_ai_config    │
    └──────────────────────┘
```

## Data Flow Examples

### 1. Get Translation Bundle

```
API: GET /i18n/bundle/<lang_code>
  │
  ▼
I18nService.get_bundle(language_code)
  │
  ▼
TranslationManager.get_bundle()
  ├─ Check: CacheService.cache_get()
  │   ✓ Found → Return cached bundle
  │   ✗ Not found → Continue
  │
  ├─ Query: SELECT get_i18n_bundle(%s, %s)
  │
  ├─ Cache: CacheService.cache_set() [TTL: 3600s]
  │
  └─ Return: { key: value, ... }
```

### 2. Submit Translation Suggestion

```
API: POST /i18n/suggestions
  │
  ▼
I18nService.submit_suggestion(user_id, language_code, value, ...)
  │
  ▼
SuggestionManager.submit_suggestion()
  ├─ Insert: INTO i18n_suggestions (...)
  │
  ├─ Callback: TranslationManager.invalidate_cache()
  │
  └─ Return: suggestion_id
```

### 3. Generate AI Translation

```
API: POST /i18n/ai-translations
  │
  ▼
I18nService.generate_ai_translation(key_id, target_lang, user_id)
  │
  ├─ Get Primary Language
  │  └─ LanguageManager.get_primary_language()
  │
  ▼
AITranslationGenerator.generate_ai_translation()
  ├─ Query: SELECT key info + source translation
  │
  ├─ Build Prompt: Context-aware (namespace, key_path, description)
  │
  ├─ Call: AIAdapter.generate_content() [Anthropic Claude]
  │
  ├─ Save: TranslationManager.set_translation()
  │
  └─ Return: { success, translation, tokens_used }
```

## Module Responsibilities

| Module | Primary Role | Secondary Role | Dependencies |
|--------|-------------|----------------|--------------|
| **bridge.py** | Facade/Adapter | API compatibility | All managers |
| **translations.py** | CRUD, caching | Bundle retrieval | CacheService |
| **languages.py** | Metadata, stats | Primary lang cache | - |
| **keys.py** | Keys, namespaces | Search, pagination | - |
| **suggestions.py** | Voting system | Translation requests | TranslationMgr |
| **ai_generation.py** | AI prompting | Batch processing | AIAdapter, LanguageMgr |
| **config.py** | Configuration | Dashboard, moderation | - |

## Dependency Graph

```
bridge.py
├── translations.py
├── languages.py
├── keys.py
├── suggestions.py
│   └── translations.py (invalidate_cache)
├── ai_generation.py
│   ├── languages.py (get_primary_language)
│   └── translations.py (set_translation)
└── config.py

External Dependencies:
├── app.database.connection (fetch_one, fetch_all, execute_query)
├── app.services.cache_service (CacheService)
├── app.services.ai_adapter (AIAdapter) [ai_generation.py only]
└── Standard library (json, logging, typing)
```

## Testing Strategy

### Unit Tests (by module)

```python
# Test individual managers
pytest tests/i18n/test_translations.py
pytest tests/i18n/test_languages.py
pytest tests/i18n/test_keys.py
pytest tests/i18n/test_suggestions.py
pytest tests/i18n/test_ai_generation.py
pytest tests/i18n/test_config.py

# Test the bridge (backward compatibility)
pytest tests/i18n/test_bridge.py
```

### Integration Tests

```python
# Test complete workflows
pytest tests/i18n/test_integration.py
  - test_translation_workflow()
  - test_ai_generation_workflow()
  - test_suggestion_voting()
```

### Example Test Structure

```python
# tests/i18n/test_translations.py
import pytest
from app.services.i18n import TranslationManager
from unittest.mock import patch, MagicMock

class TestTranslationManager:

    @patch('app.services.cache_service.CacheService.cache_get')
    def test_get_bundle_cached(self, mock_cache):
        """Test bundle retrieval from cache"""
        mock_cache.return_value = {'key': 'value'}

        result = TranslationManager.get_bundle('de')

        assert result == {'key': 'value'}
        mock_cache.assert_called_once()

    @patch('app.services.cache_service.CacheService.cache_get')
    @patch('app.database.connection.fetch_one')
    def test_get_bundle_from_db(self, mock_fetch, mock_cache):
        """Test bundle retrieval from database when not cached"""
        mock_cache.return_value = None  # Not in cache
        mock_fetch.return_value = {'bundle': {'key': 'value'}}

        result = TranslationManager.get_bundle('en')

        assert result == {'key': 'value'}
        mock_fetch.assert_called_once()
```

## Performance Characteristics

| Operation | Complexity | Cache | Notes |
|-----------|-----------|-------|-------|
| get_bundle | O(1) | Redis (1h TTL) | DB function call |
| get_languages | O(n) | Redis (5m TTL) | n = num languages |
| get_keys | O(k log k) | None | k = keys, paginated |
| get_suggestions | O(s) | None | s = suggestions |
| generate_ai_translation | O(1) | None | AI call ~2s |
| bulk_generate | O(n) | None | n keys sequentially |

## Extension Points

Future enhancements without breaking existing API:

```python
# Add ValidationManager for translation validation
from app.services.i18n import ValidationManager

# Add AuditManager for translation history
from app.services.i18n import AuditManager

# Add MetricsManager for completion statistics
from app.services.i18n import MetricsManager

# All would be added to __init__.py and bridge.py
```

## Migration Path

### Stage 1: Current (Backward Compatible)
```python
# Old code still works
from app.services.i18n_service import I18nService
I18nService.get_bundle('de')
```

### Stage 2: Optional (New Code)
```python
# New code can be more specific
from app.services.i18n import TranslationManager
TranslationManager.get_bundle('de')

# Or mixed
from app.services.i18n_service import I18nService
from app.services.i18n import KeyManager
```

### Stage 3: Future (Full Migration)
```python
# All code uses specific managers
from app.services.i18n import (
    TranslationManager,
    LanguageManager,
    KeyManager,
)
```

---

**Documentation Generated:** 2025-01-07
**Architecture Version:** 1.0
**Status:** Final (Production Ready)
