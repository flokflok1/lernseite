# PHASE 3.3: Priority 1 File Conversion Plan

**Status:** STARTING
**Date:** 2026-01-17
**Target:** Convert 13 high-priority API files from hardcoded error messages to ErrorCode enum + i18n mappings
**Total Errors to Convert:** 100+ hardcoded error messages

---

## Overview

Phase 3.3 focuses on converting the highest-priority API files that handle the most critical business logic:
- Course management (CRUD, status changes, archiving)
- Chapter management
- Lesson management
- Exam/Assessment management
- Learning method operations

### Conversion Pattern

**BEFORE:**
```python
if not course:
    return jsonify({'success': False, 'error': 'Course not found'}), 404
```

**AFTER:**
```python
from app.i18n.error_codes import ErrorCode
from app.utils.exceptions import APIException

if not course:
    return error_response(ErrorCode.COURSE_NOT_FOUND, 404)
```

---

## Priority 1 Files (by error count)

### 1. **course_editor/manual_editor/courses.py** ⭐ HIGHEST PRIORITY
**Status:** STARTING
**Error Count:** 55 errors in 372 lines
**Errors to Convert:**
- Line 96: "Invalid parameter" → VALIDATION_INVALID_VALUE
- Line 99: "Failed to list courses" → OPERATION_FAILED
- Line 110: "Course not found" → COURSE_NOT_FOUND
- Line 123: "Failed to get course details" → OPERATION_FAILED
- Line 142: "Failed to create course" → COURSE_CREATE_FAILED
- Line 160: "Validation error" → VALIDATION_ERROR
- Line 178: "Course not found" → COURSE_NOT_FOUND
- Line 187: "Failed to update course" → COURSE_UPDATE_FAILED
- Line 205: "Validation error" → VALIDATION_ERROR
- Line 230: "Forbidden" → AUTH_INSUFFICIENT_PERMISSIONS (with custom message)
- Line 236: "Course not found" → COURSE_NOT_FOUND
- Line 256: "Invalid action" → VALIDATION_INVALID_VALUE
- Line 261: "Failed to change course status" → COURSE_PUBLISH_FAILED
- Line 279: "Validation error" → VALIDATION_ERROR
- Line 282: "Failed to change status" → COURSE_PUBLISH_FAILED
- Line 296: "Course not found" → COURSE_NOT_FOUND
- Line 301: "Failed to archive course" → COURSE_ARCHIVE_FAILED
- Line 316: "Failed to archive course" → COURSE_ARCHIVE_FAILED
- Line 336: "Forbidden" → AUTH_INSUFFICIENT_PERMISSIONS
- Line 343: "Confirmation required" → VALIDATION_REQUIRED_FIELD
- Line 351: "Course not found" → COURSE_NOT_FOUND
- Line 357: "Failed to permanently delete" → OPERATION_FAILED
- Line 372: "Failed to delete" → OPERATION_FAILED

**Impact:** Critical course management operations
**Dependencies:** CourseRepository, AuditService
**Testing:** Need to verify all status transitions work correctly

---

### 2. **course_editor/manual_editor/exams.py**
**Status:** PENDING
**Error Count:** 39 errors in 322 lines
**Key Errors:**
- "Exam not found" → EXAM_NOT_FOUND
- "Failed to create exam" → EXAM_CREATE_FAILED
- "Failed to update exam" → OPERATION_FAILED
- "Failed to delete exam" → OPERATION_FAILED
- "Validation error" → VALIDATION_ERROR
- "Invalid parameter" → VALIDATION_INVALID_VALUE

**Impact:** Exam/assessment creation and management
**Dependencies:** ExamRepository, ValidationError handling
**Testing:** Exam CRUD operations

---

### 3. **course_editor/manual_editor/chapters.py**
**Status:** PENDING
**Error Count:** 27 errors in 204 lines
**Key Errors:**
- "Chapter not found" → CHAPTER_NOT_FOUND
- "Failed to create chapter" → OPERATION_FAILED
- "Failed to update chapter" → OPERATION_FAILED
- "Failed to delete chapter" → OPERATION_FAILED
- "Validation error" → VALIDATION_ERROR
- "Course not found" → COURSE_NOT_FOUND

**Impact:** Course chapter management
**Dependencies:** ChapterRepository, CourseRepository
**Testing:** Chapter CRUD and ordering

---

### 4. **course_editor/manual_editor/lessons.py**
**Status:** PENDING
**Error Count:** ~30 errors
**Key Errors:**
- "Lesson not found" → LESSON_NOT_FOUND
- "Chapter not found" → CHAPTER_NOT_FOUND
- "Failed to create lesson" → OPERATION_FAILED
- "Failed to update lesson" → OPERATION_FAILED
- "Failed to delete lesson" → OPERATION_FAILED
- "Validation error" → VALIDATION_ERROR

**Impact:** Lesson management within chapters
**Dependencies:** LessonRepository, ChapterRepository
**Testing:** Lesson CRUD and reordering

---

### 5. **courses/crud.py**
**Status:** PENDING
**Error Count:** 36 errors in 217 lines
**Key Errors:**
- "Course not found" → COURSE_NOT_FOUND
- "Failed to create course" → COURSE_CREATE_FAILED
- "Failed to update course" → COURSE_UPDATE_FAILED
- "Validation error" → VALIDATION_ERROR
- "Course already exists" → COURSE_CREATE_FAILED
- "Forbidden" → AUTH_INSUFFICIENT_PERMISSIONS

**Impact:** Main course CRUD operations
**Dependencies:** CourseRepository
**Testing:** User-facing course creation/editing

---

### 6. **courses/core.py**
**Status:** PENDING
**Error Count:** 21 errors in 205 lines
**Key Errors:**
- "Course not found" → COURSE_NOT_FOUND
- "Forbidden" → COURSE_ACCESS_DENIED
- "Failed to enroll" → COURSE_CREATE_FAILED
- "Validation error" → VALIDATION_ERROR

**Impact:** Course listing and core operations
**Testing:** Course filtering and permissions

---

### 7. **courses/publishing.py**
**Status:** PENDING
**Error Count:** ~25 errors
**Key Errors:**
- "Course not found" → COURSE_NOT_FOUND
- "Failed to publish" → COURSE_PUBLISH_FAILED
- "Failed to unpublish" → COURSE_PUBLISH_FAILED
- "Validation error" → VALIDATION_ERROR
- "Forbidden" → COURSE_ACCESS_DENIED

**Impact:** Course publication workflow
**Testing:** Publish/unpublish transitions

---

### 8. **courses/enrollment.py**
**Status:** PENDING
**Error Count:** ~20 errors
**Key Errors:**
- "Course not found" → COURSE_NOT_FOUND
- "User not found" → USER_NOT_FOUND
- "Already enrolled" → COURSE_ALREADY_ENROLLED
- "Not enrolled" → COURSE_NOT_ENROLLED
- "Forbidden" → AUTH_INSUFFICIENT_PERMISSIONS

**Impact:** Course enrollment operations
**Testing:** Enrollment/unenrollment flows

---

### 9. **learning_methods/core.py**
**Status:** PENDING
**Error Count:** ~22 errors
**Key Errors:**
- "Learning method not found" → LM_NOT_FOUND
- "Lesson not found" → LESSON_NOT_FOUND
- "Failed to create" → LM_CREATE_FAILED
- "Failed to update" → LM_UPDATE_FAILED
- "Validation error" → VALIDATION_ERROR

**Impact:** Learning method instance operations
**Testing:** Learning method CRUD

---

### 10. **learning_methods/chapters.py**
**Status:** PENDING
**Error Count:** ~18 errors
**Key Errors:**
- "Chapter not found" → CHAPTER_NOT_FOUND
- "Course not found" → COURSE_NOT_FOUND
- "Learning method not found" → LM_NOT_FOUND
- "Validation error" → VALIDATION_ERROR

---

### 11. **learning_methods/explanations.py**
**Status:** PENDING
**Error Count:** ~15 errors
**Key Errors:**
- "Content not found" → LESSON_NOT_FOUND
- "Failed to generate" → AI_GENERATION_FAILED
- "Validation error" → VALIDATION_ERROR

---

### 12. **learning_methods/videos.py**
**Status:** PENDING
**Error Count:** ~12 errors
**Key Errors:**
- "Video not found" → FILE_NOT_FOUND
- "Failed to upload" → FILE_UPLOAD_FAILED
- "Validation error" → VALIDATION_ERROR

---

### 13. **admin-panel/user_management/users.py** (if applicable)
**Status:** PENDING
**Error Count:** ~10+ errors

---

## Conversion Implementation Strategy

### Step 1: Add Imports
Each file needs:
```python
from app.i18n.error_codes import ErrorCode
from app.utils.exceptions import APIException, error_response
```

### Step 2: Replace Hardcoded Errors
Replace all `jsonify` error responses with `error_response()` helper:

**Pattern 1 - Not Found Errors:**
```python
# BEFORE
if not course:
    return jsonify({'success': False, 'error': 'Course not found'}), 404

# AFTER
if not course:
    return error_response(ErrorCode.COURSE_NOT_FOUND, 404)
```

**Pattern 2 - Validation Errors:**
```python
# BEFORE
except ValidationError as e:
    return jsonify({'success': False, 'error': 'Validation error', 'details': e.errors()}), 400

# AFTER
except ValidationError as e:
    return error_response(ErrorCode.VALIDATION_ERROR, 400, details=e.errors())
```

**Pattern 3 - Operation Failed:**
```python
# BEFORE
if not result:
    return jsonify({'success': False, 'error': 'Failed to create course'}), 500

# AFTER
if not result:
    return error_response(ErrorCode.COURSE_CREATE_FAILED, 500)
```

### Step 3: Update Response Format
Some endpoints use custom messages. After error_response() helper adoption, the format becomes consistent:
```json
{
  "success": false,
  "error": {
    "code": "COURSE_NOT_FOUND",
    "message": "Course not found"
  }
}
```

### Step 4: Testing
After each file conversion:
1. Run `python -m py_compile` on the file
2. Test affected endpoints via cURL or integration tests
3. Verify error code is returned correctly
4. Verify i18n mapping exists for error code

---

## Error Code Mapping Reference

**Generic Errors:**
- VALIDATION_ERROR → 400
- VALIDATION_INVALID_VALUE → 400
- VALIDATION_REQUIRED_FIELD → 400
- OPERATION_FAILED → 500

**Resource Not Found:**
- COURSE_NOT_FOUND → 404
- CHAPTER_NOT_FOUND → 404
- LESSON_NOT_FOUND → 404
- EXAM_NOT_FOUND → 404
- USER_NOT_FOUND → 404
- LM_NOT_FOUND → 404
- FILE_NOT_FOUND → 404

**CRUD Operations:**
- COURSE_CREATE_FAILED → 400/500
- COURSE_UPDATE_FAILED → 400/500
- COURSE_PUBLISH_FAILED → 400/500
- COURSE_ARCHIVE_FAILED → 500
- COURSE_DELETE_FAILED → 500
- LM_CREATE_FAILED → 400/500
- LM_UPDATE_FAILED → 400/500

**Access Control:**
- AUTH_INSUFFICIENT_PERMISSIONS → 403
- COURSE_ACCESS_DENIED → 403
- FORBIDDEN → 403

**Business Logic:**
- COURSE_ALREADY_ENROLLED → 409
- COURSE_NOT_ENROLLED → 400

---

## Progress Tracking

**Completed:** 0/13 files
**In Progress:** 1 file (courses.py)
**Pending:** 12 files

### Conversion Sequence
1. courses/manual_editor/courses.py ← START HERE
2. courses/manual_editor/exams.py
3. courses/manual_editor/chapters.py
4. courses/manual_editor/lessons.py
5. courses/crud.py
6. courses/core.py
7. courses/publishing.py
8. courses/enrollment.py
9. learning_methods/core.py
10. learning_methods/chapters.py
11. learning_methods/explanations.py
12. learning_methods/videos.py
13. admin-panel/users.py (if time permits)

---

## Success Criteria

✅ All 13 Priority 1 files converted
✅ All 100+ error messages replaced with ErrorCode enum
✅ Python syntax validation passes
✅ All i18n keys exist in ERROR_CODE_I18N_MAPPING
✅ Integration tests pass for affected endpoints
✅ No regression in existing functionality

---

**Next Action:** Begin conversion of `courses.py` - replace 55 hardcoded errors with ErrorCode enum values
