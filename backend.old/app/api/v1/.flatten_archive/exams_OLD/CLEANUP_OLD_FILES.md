# Cleanup Old Files

**Status:** PENDING CLEANUP
**Date:** 2026-01-08

---

## Old Files to Remove

After verifying the new DDD structure works, the following old files should be removed:

### Files to DELETE:

```bash
# Old files (now replaced by DDD structure)
rm -f /home/pascal/Lernsystem/backend/app/api/exams/attempts.py
rm -f /home/pascal/Lernsystem/backend/app/api/exams/context.py
rm -f /home/pascal/Lernsystem/backend/app/api/exams/generation.py
rm -f /home/pascal/Lernsystem/backend/app/api/exams/models.py
rm -f /home/pascal/Lernsystem/backend/app/api/exams/simulations.py
rm -f /home/pascal/Lernsystem/backend/app/api/exams/user_profile.py
```

### New Files (Keep):

```
exams/
├── __init__.py                 # NEW - DDD exports
├── admin/
│   ├── __init__.py            # NEW
│   ├── context.py             # NEW (replaces old context.py)
│   └── generation.py          # NEW (replaces old generation.py)
├── user/
│   ├── __init__.py            # NEW
│   ├── simulations.py         # NEW (replaces old simulations.py)
│   ├── attempts.py            # NEW (replaces old attempts.py)
│   └── user_profile.py        # NEW (replaces old user_profile.py)
└── core/
    ├── __init__.py            # NEW
    ├── value_objects.py       # NEW (domain concepts)
    ├── factory.py             # NEW (DDD factory)
    ├── services.py            # NEW (business logic)
    └── models.py              # NEW (enhanced Pydantic models)
```

---

## Cleanup Commands

**Step 1: Backup old files (optional)**

```bash
cd /home/pascal/Lernsystem/backend/app/api/exams
mkdir -p .backup_old_files
mv attempts.py context.py generation.py models.py simulations.py user_profile.py .backup_old_files/
```

**Step 2: Or delete directly**

```bash
cd /home/pascal/Lernsystem/backend/app/api/exams
rm -f attempts.py context.py generation.py models.py simulations.py user_profile.py
```

---

## Verification Steps

Before cleanup:

1. **Test imports work:**
   ```python
   from app.api.exams.core import ExamFactory, ExamService
   from app.api.exams.admin import exam_context_bp
   from app.api.exams.user import exam_simulations_bp
   ```

2. **Test backend starts:**
   ```bash
   cd /home/pascal/Lernsystem/backend
   python run.py
   ```

3. **Test endpoints work:**
   ```bash
   curl -X GET http://localhost:5000/api/v1/exam-simulations
   ```

After cleanup:

4. **Verify no import errors:**
   ```bash
   python -c "from app.api.exams import *"
   ```

5. **Run tests:**
   ```bash
   pytest backend/tests/test_exams.py -v
   ```

---

## Status: READY FOR CLEANUP

All new files created ✅
All functionality migrated ✅
Backward compatibility maintained ✅
Quality Gates passed ✅

**Safe to proceed with cleanup after verification.**

---

**Note:** Keep `.backup_old_files/` directory for 1 week in case rollback needed.
