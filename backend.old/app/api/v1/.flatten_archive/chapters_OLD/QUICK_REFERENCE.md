# Chapter Theory API - Quick Reference

**DDD Structure** | **Updated:** 2026-01-08

---

## Import Cheat Sheet

```python
# Admin operations
from app.api.chapter_theory.admin import (
    chapter_theory_gen_bp,
    generate_theory_content,
    chapter_theory_admin_management_bp,
    chapter_theory_audio_bp,
    generate_theory_audio,
)

# User operations
from app.api.chapter_theory.user import chapter_theory_user_read_bp

# Core logic
from app.api.chapter_theory.core import (
    TheoryFactory,
    get_chapter_theory,
    save_chapter_theory,
)
```

---

## Factory Pattern

```python
# Create theory with validation
theory = TheoryFactory.create_theory(
    chapter_id="uuid",
    style="adhs",
    theory_data={...},
    tokens_used=1234
)

# Create with defaults
theory = TheoryFactory.create_with_defaults(
    chapter_id="uuid",
    style="standard"
)

# Save to database
result = save_chapter_theory(**theory)
```

---

## API Endpoints

| Method | Endpoint | Module | Auth |
|--------|----------|--------|------|
| POST | `/chapters/:id/theory/generate` | admin/generation | ✅ |
| GET | `/chapters/:id/theories` | user/read | ✅ |
| GET | `/chapters/:id/theory` | user/read | ✅ |
| GET | `/chapter-theory/:id` | user/read | ✅ |
| PATCH | `/chapter-theory/:id` | admin/management | ✅ |
| DELETE | `/chapter-theory/:id` | admin/management | ✅ |
| GET | `/chapter-theory/:id/audio` | admin/media | ✅ |

---

## Theory Styles

- `adhs` - ADHS-friendly with whiteboard
- `detailed` - Academic style
- `short` - Compact summary
- `exam_focus` - IHK exam-focused
- `standard` - Balanced (default)

---

## Repository Functions

```python
# Read
theory = get_chapter_theory(chapter_id, style)
theory = get_chapter_theory_by_id(theory_id)
theories = list_chapter_theories(chapter_id)

# Write
result = save_chapter_theory(chapter_id, style, theory_data, ...)
result = update_chapter_theory_title(theory_id, title)

# Delete
deleted = delete_chapter_theory_by_id(theory_id)
deleted = delete_chapter_theory_by_style(chapter_id, style)

# Context
chapter = get_chapter_info(chapter_id)
lessons = get_chapter_lessons(chapter_id)
theory = get_fallback_theory(chapter_id)
```

---

## Structure

```
chapter_theory/
├── admin/      # Admin-only (generation, management, media)
├── user/       # User-facing (read-only)
└── core/       # Domain logic (repository, factory)
```

---

## Example: Generate Theory

```python
# 1. Check if exists
existing = get_chapter_theory(chapter_id, 'adhs')
if existing:
    return existing

# 2. Get context
chapter = get_chapter_info(chapter_id)
lessons = get_chapter_lessons(chapter_id)

# 3. Generate
theory_data, tokens, model = generate_theory_content('adhs', context)

# 4. Generate audio (optional)
audio_result = generate_theory_audio(theory_data, 'nova', chapter_id, user_id)

# 5. Save
save_chapter_theory(
    chapter_id=chapter_id,
    style='adhs',
    theory_data=theory_data,
    audio_url=audio_result['url'],
    tokens_used=tokens
)
```

---

## Testing

```bash
# Test imports
python -c "from app.api.chapter_theory.core import TheoryFactory"

# Test factory
python -c "
from app.api.chapter_theory.core import TheoryFactory
theory = TheoryFactory.create_with_defaults('test-id')
print(theory)
"

# Start backend
python run.py
```

---

**Full Documentation:** See `REFACTORING_SUMMARY.md`
