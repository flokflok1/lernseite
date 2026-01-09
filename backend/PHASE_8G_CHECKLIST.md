# Phase 8g: Backend Testing Checklist

Use this checklist for future backend refactorings to ensure quality.

---

## Pre-Refactoring Checklist

- [ ] Read relevant documentation in `LernsystemX-Doku/`
- [ ] Check `35_Developer-Guide-KI.md` for size limits (max 500 LOC)
- [ ] Identify files >500 lines that need splitting
- [ ] Plan package structure before implementation
- [ ] Ensure no circular import dependencies in design

---

## During Refactoring

### Code Organization
- [ ] Files stay under 500 lines
- [ ] Packages have proper `__init__.py` with `__all__`
- [ ] Docstrings present in all modules
- [ ] Type hints on all functions
- [ ] Imports organized (stdlib → third-party → local)

### Blueprint Pattern
- [ ] `api_v1` imported ONCE in parent `__init__.py`
- [ ] `api_v1` re-exported in parent's `__all__`
- [ ] Submodules import from parent package (NOT from `app.api`)
- [ ] Route decorators use `@api_v1.route(...)`

### Anti-Patterns to Avoid
- [ ] No `from app.api import api_v1` in submodules (use parent package)
- [ ] No empty `__init__.py` files (always define `__all__`)
- [ ] No circular imports (verify with import test)
- [ ] No hardcoded strings (use i18n for user-facing text)

---

## Post-Refactoring Testing

### 1. Python Syntax Check
```bash
cd /home/pascal/Lernsystem/backend
python3 -m py_compile app/api/[package]/*.py
```
- [ ] All files compile without syntax errors

### 2. Import Test
```bash
cd /home/pascal/Lernsystem/backend
source venv/bin/activate
python test_imports_phase8.py
```
- [ ] All packages import successfully
- [ ] No circular import errors

### 3. Flask App Creation
```bash
cd /home/pascal/Lernsystem/backend
source venv/bin/activate
python -c "from app import create_app; app = create_app('development')"
```
- [ ] App creates successfully
- [ ] Expected number of blueprints registered
- [ ] No errors in middleware initialization

### 4. Route Verification
```bash
python -c "from app import create_app; app = create_app('development'); print(len(list(app.url_map.iter_rules())))"
```
- [ ] Expected number of routes registered
- [ ] No duplicate route definitions
- [ ] All endpoints follow naming conventions

---

## Documentation Updates

- [ ] Update `LernsystemX-Doku/05_Technical/05_Backend-Struktur.md`
- [ ] Document new packages/modules in architecture docs
- [ ] Update API documentation if endpoints changed
- [ ] Add migration notes if breaking changes exist

---

## Git Commit

### Before Commit
- [ ] Run all tests above
- [ ] Verify no `.pyc` files in commit
- [ ] Check `git status` for untracked files
- [ ] Review `git diff` for unintended changes

### Commit Message Template
```
<type>(backend): <short description>

<Detailed description of changes>

Changes:
- <Change 1>
- <Change 2>

Testing:
- ✅ Syntax check: X files compiled
- ✅ Import test: All packages OK
- ✅ Flask app: X blueprints, Y routes

Files modified: Z
Files created: W

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`

---

## Quality Gates (G01-G10)

| Gate | Check | Status |
|------|-------|--------|
| G01 | No duplicates (.old, .bak, _v2) | [ ] |
| G02 | LSX-Architektur konsistent | [ ] |
| G04 | Vollständige Dateien (keine Fragmente) | [ ] |
| G05 | Docstrings, Type Hints | [ ] |
| G07 | OWASP-konform, keine Secrets | [ ] |
| G09 | Effiziente Queries, Caching | [ ] |

---

## Common Issues & Fixes

### Issue: Circular Import
**Symptom:** `cannot import name 'X' from partially initialized module`  
**Fix:** Import `api_v1` once in parent `__init__.py`, submodules import from parent  
**Reference:** `PHASE_8G_CIRCULAR_IMPORT_FIX.md`

### Issue: Empty `__init__.py`
**Symptom:** `cannot import name 'X' from 'package'`  
**Fix:** Add proper imports and `__all__` to `__init__.py`  
**Example:** See `app/api/media/__init__.py` (Phase 8g fix)

### Issue: File Too Large
**Symptom:** File >500 lines  
**Fix:** Split into submodules using DDD principles  
**Example:** See Phase 8a-8f refactorings

---

## Test Artifacts

Use these scripts for automated testing:

| Script | Purpose |
|--------|---------|
| `test_imports_phase8.py` | Test all package imports |
| `PHASE_8G_BACKEND_TESTING.md` | Full testing report template |
| `PHASE_8G_CIRCULAR_IMPORT_FIX.md` | Circular import debugging guide |

---

**Created:** 2026-01-08  
**Last Updated:** 2026-01-08  
**Version:** 1.0
