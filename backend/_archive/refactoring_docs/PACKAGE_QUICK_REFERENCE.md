# Package Structure Quick Reference

## 🎯 math/ - MathToolkit API

**4 Packages | 9 Files | 644 LOC**

```
/math-toolkit/calculator/*  → calculator/engine.py      (84 LOC)
/math-toolkit/reference/*   → reference/library.py      (134 LOC)
/math-toolkit/sessions/*    → sessions/history.py       (124 LOC)
/math-toolkit/progress/*    → interactive/exercises.py  (213 LOC)
/math-toolkit/hints/*       → interactive/exercises.py
/math-toolkit/tasks/*       → interactive/exercises.py
/math-toolkit/admin/*       → interactive/exercises.py
```

**Blueprint:** `math_toolkit_bp` in `math/__init__.py`

---

## 🌐 i18n/ - Internationalization API

**4 Packages | 12 Files | 1,416 LOC**

```
/i18n/bundle               → public/api.py              (84 LOC)
/i18n/languages            → public/api.py
/i18n/suggestions          → management/suggestions.py  (169 LOC)
/i18n/admin/keys           → management/keys.py         (176 LOC)
/i18n/admin/moderation     → moderation/content.py      (217 LOC)
/i18n/admin/ai/translate   → translation/ai.py          (284 LOC)
/i18n/admin/languages      → translation/languages.py   (348 LOC)
/i18n/admin/export         → translation/languages.py
```

**Blueprints:** 6 blueprints registered in `i18n/__init__.py`

---

## 🎓 learning_methods/ - Learning Methods API

**4 Packages | 11 Files | 1,199 LOC**

```
# Public (No auth)
/learning-methods          → public/catalog.py          (246 LOC)
/learning-methods/:id      → public/catalog.py

# Authenticated
/learning-methods/:id/execute   → execution/runner.py   (339 LOC)
/learning-methods/:id/feedback  → execution/runner.py
/learning-methods/my-usage      → execution/runner.py
/lessons/:id/executions         → execution/validator.py (114 LOC)
/executions/:id                 → execution/validator.py

# Admin
/learning-methods (POST/PUT/DELETE) → admin/management.py (310 LOC)
/learning-methods/stats             → admin/management.py
/learning-methods/:id/activate      → admin/management.py
```

**Blueprints:** 4 blueprints registered in `learning_methods/__init__.py`

---

## 📊 Size Distribution

```
< 100 LOC:  20 files (62.5%)  ← __init__.py, helpers
100-200 LOC: 6 files (18.8%)  ← Small modules
200-300 LOC: 3 files (9.4%)   ← Medium modules  
300-400 LOC: 3 files (9.4%)   ← Large modules
> 400 LOC:   0 files (0%)     ← ✓ NO FILES OVER LIMIT!
```

**Average file size:** 102 LOC  
**Median file size:** 11 LOC (many small __init__.py files)

---

## 🔧 Import Patterns

### Sub-module imports parent helpers:
```python
# learning_methods/public/catalog.py
from .._helpers import (  # Note: .. for parent package
    request,
    jsonify,
    ...
)
```

### Sub-module uses parent blueprint:
```python
# math/calculator/engine.py
from app.api.math import math_toolkit_bp

@math_toolkit_bp.route('/calculator/evaluate', methods=['POST'])
def evaluate_expression():
    ...
```

### Package exports sub-modules:
```python
# learning_methods/__init__.py
from .public import lm_public_bp
from .execution import lm_execution_bp, lm_executions_bp
from .admin import lm_admin_bp

ALL_BLUEPRINTS = [lm_public_bp, lm_execution_bp, ...]
```

---

## ✅ Benefits

1. **Maintainability:** Smaller files easier to understand
2. **Scalability:** Add new features without bloating existing files
3. **Team collaboration:** Less merge conflicts
4. **Code organization:** Clear separation of concerns
5. **Future-proof:** Room to grow without hitting limits

---

**Quick Start:** Navigate to specific package to work on that functionality  
**Documentation:** See AGENT_7_REFACTORING_SUMMARY.md for full details
