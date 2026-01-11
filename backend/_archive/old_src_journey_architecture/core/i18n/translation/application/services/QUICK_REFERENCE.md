# i18n Package - Quick Reference Guide

## Files at a Glance

| File | LOC | Purpose | Main Exports |
|------|-----|---------|--------------|
| `__init__.py` | 30 | Package exports | All 6 managers |
| `bridge.py` | 228 | Backward-compatible facade | `I18nService` (30 methods) |
| `translations.py` | 149 | Translation CRUD & cache | `TranslationManager` |
| `languages.py` | 155 | Language metadata & progress | `LanguageManager` |
| `keys.py` | 163 | Keys & namespaces | `KeyManager` |
| `suggestions.py` | 188 | Suggestions & voting | `SuggestionManager` |
| `ai_generation.py` | 204 | AI translation generation | `AITranslationGenerator` |
| `config.py` | 133 | Configuration & moderation | `ConfigManager` |

## Import Patterns

### Backward Compatible (existing code)
```python
from app.services.i18n_service import I18nService

# Use all methods as before
bundle = I18nService.get_bundle('de')
langs = I18nService.get_languages()
```

### Direct Imports (new code preferred)
```python
from app.services.i18n import (
    TranslationManager,
    LanguageManager,
    KeyManager,
    SuggestionManager,
    AITranslationGenerator,
    ConfigManager,
)

# More specific imports
bundle = TranslationManager.get_bundle('de')
langs = LanguageManager.get_languages()
```

## Manager API Summary

### TranslationManager
```python
get_bundle(language_code, namespace=None) → Dict[str, str]
get_key_translations(key_id) → List[Dict]
set_translation(key_id, language_code, value, translator_id=None, is_machine_translated=False) → bool
invalidate_cache(language_code=None) → None
```

### LanguageManager
```python
get_primary_language() → str  # Returns 'de' by default
invalidate_primary_language_cache() → None
get_languages() → List[Dict]  # All languages with stats
get_language_progress(language_code) → Optional[Dict]
```

### KeyManager
```python
get_namespaces() → List[Dict]
get_keys(namespace_id=None, search=None, limit=100, offset=0) → Dict
create_key(namespace_id, key_path, description=None, ...) → Optional[int]
```

### SuggestionManager
```python
submit_suggestion(user_id, language_code, suggested_value, ...) → Optional[str]
vote_suggestion(user_id, suggestion_id, vote_type) → bool
get_suggestions(language_code=None, status='pending', limit=50) → List[Dict]
request_translation(user_id, target_language, scope='full', namespace_id=None) → Optional[Dict]
```

### AITranslationGenerator
```python
generate_ai_translation(key_id, target_language, user_id, ...) → Optional[Dict]
bulk_generate_translations(target_language, namespace_id=None, ...) → Dict
```

### ConfigManager
```python
get_ai_config() → Dict[str, Any]
update_ai_config(config_key, config_value, user_id) → bool
get_moderation_dashboard() → List[Dict]
get_moderation_queue(status=None, language_code=None, limit=50) → List[Dict]
review_queue_item(queue_id, user_id, decision, comment=None) → bool
```

## Common Tasks

### Get Translation Bundle
```python
from app.services.i18n import TranslationManager

bundle = TranslationManager.get_bundle('de')
# Returns: {'common.save': 'Speichern', 'common.cancel': 'Abbrechen', ...}
```

### Update Translation
```python
TranslationManager.set_translation(
    key_id='user_settings_title',
    language_code='en',
    value='User Settings',
    translator_id=current_user.id
)
```

### Get Language Progress
```python
from app.services.i18n import LanguageManager

progress = LanguageManager.get_language_progress('pl')
# Returns: {
#     'progress': {
#         'language_code': 'pl',
#         'total_keys': 150,
#         'translated_keys': 142,
#         'completion_percent': 94.7
#     },
#     'missing_sample': []
# }
```

### Generate AI Translation
```python
from app.services.i18n import AITranslationGenerator

result = AITranslationGenerator.generate_ai_translation(
    key_id=123,
    target_language='fr',
    user_id=current_user.id,
    primary_language='de'
)
# Returns: {
#     'success': True,
#     'translation': 'Paramètres utilisateur',
#     'tokens_used': 250
# }
```

### Submit Translation Suggestion
```python
from app.services.i18n import SuggestionManager

suggestion_id = SuggestionManager.submit_suggestion(
    user_id='user123',
    language_code='en',
    suggested_value='Better wording',
    key_id='some_key',
    reason='More natural English'
)
```

## File Locations

```
backend/
└── app/
    ├── services/
    │   ├── i18n_service.py (bridge re-export, 29 LOC)
    │   └── i18n/ (NEW PACKAGE)
    │       ├── __init__.py
    │       ├── bridge.py
    │       ├── translations.py
    │       ├── languages.py
    │       ├── keys.py
    │       ├── suggestions.py
    │       ├── ai_generation.py
    │       ├── config.py
    │       ├── REFACTORING.md (detailed refactoring doc)
    │       ├── ARCHITECTURE.md (architecture diagrams)
    │       └── QUICK_REFERENCE.md (this file)
    │
    └── api/
        └── i18n/
            ├── public.py
            ├── keys.py
            ├── suggestions.py
            ├── ai_translation.py
            ├── languages.py
            └── moderation.py
```

## Testing

### Run All i18n Tests
```bash
pytest tests/ -k i18n
```

### Test Specific Manager
```bash
pytest tests/test_i18n_translations.py
pytest tests/test_i18n_languages.py
```

### Test Backward Compatibility
```bash
pytest tests/test_i18n_service.py  # Tests bridge.py
```

## Key Differences from Monolith

### Before: Single File
```python
# i18n_service.py (730 LOC)
class I18nService:
    # All 30 methods in one class
```

### After: Modular Package
```python
# bridge.py (228 LOC)
class I18nService:
    # Delegates to 6 managers
    # Methods call: TranslationManager.get_bundle()
    #               LanguageManager.get_languages()
    #               etc.
```

**Benefit:** Can import specific managers for unit testing and code clarity.

## Performance Notes

- **No regression:** Same SQL queries, same database calls
- **Better caching:** Cache invalidation is more granular
- **Lazy loading:** Only needed managers are imported
- **Testability:** Mock individual managers in isolation

## Backward Compatibility Guarantees

✓ All method signatures unchanged
✓ Return types identical
✓ Constants re-exported (BUNDLE_CACHE_TTL)
✓ Error handling consistent
✓ Database queries unchanged
✓ Zero breaking changes

## Migration Timeline

### Phase 1: NOW ✓
- New package deployed
- Existing code continues to work
- New code can use modular imports

### Phase 2: OPTIONAL (1-2 releases)
- Gradually update imports in new code
- Document preferred patterns
- No urgency to migrate

### Phase 3: OPTIONAL (Future)
- Fully migrate if desired
- Remove bridge module
- Delete i18n_service.py

## Documentation

- **REFACTORING.md** - Detailed refactoring summary
- **ARCHITECTURE.md** - Architecture diagrams and design
- **QUICK_REFERENCE.md** - This file (quick lookup)

## Troubleshooting

### Import Issues
```python
# If you get ImportError, check:
✓ Python path includes backend/
✓ app/__init__.py exists
✓ app/services/__init__.py exists
✓ app/services/i18n/__init__.py exists
```

### Method Not Found
```python
# Check you're using correct manager:
TranslationManager.set_translation()  # ✓
LanguageManager.get_languages()       # ✓
KeyManager.get_keys()                 # ✓

# Or use facade:
I18nService.set_translation()  # ✓
```

### Cache Not Invalidating
```python
# Use the correct invalidate method:
TranslationManager.invalidate_cache(language_code)  # ✓

# Or through bridge:
I18nService.invalidate_cache(language_code)  # ✓
```

## Contact & Support

For questions about the i18n package architecture:
1. Review ARCHITECTURE.md for design details
2. Check REFACTORING.md for implementation notes
3. Look at module docstrings for API details
4. Review test files for usage examples

---

**Last Updated:** 2025-01-07
**Package Version:** 1.0 (Stable)
**Status:** Production Ready
