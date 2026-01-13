# Courses Domain - DDD Architecture

**Version:** 1.0
**Datum:** 2026-01-08
**Standard:** Domain-Driven Design (DDD) + ISO/IEC 26515

---

## 🏗️ Layered Architecture (Hexagonal)

```
┌────────────────────────────────────────────────────────────┐
│                    API Layer (Routes)                       │
│                  admin/, user/, public/                     │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │   Admin     │  │    User     │  │   Public    │      │
│  │ /courses/   │  │ /courses/   │  │ /courses/   │      │
│  │   crud      │  │ enrollment  │  │  preview    │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│               Application Layer                              │
│          Orchestriert Domain & Infrastructure                │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  Request Validation (Pydantic)                       │ │
│  │  Permission Checks (RBAC)                            │ │
│  │  Audit Logging                                       │ │
│  └──────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   Domain Layer                               │
│        Factory, Services, Entities, Value Objects            │
│              ✨ BUSINESS LOGIC HERE! ✨                     │
│                                                             │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐ │
│  │ CourseFactory  │  │ CourseService  │  │CourseStatus  │ │
│  │ ChapterFactory │  │EnrollmentSvc   │  │Visibility    │ │
│  │ LessonFactory  │  │                │  │Price         │ │
│  └────────────────┘  └────────────────┘  └──────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              Infrastructure Layer                            │
│          Repository, External Services, DB Access            │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │  CourseRepository (Direct SQL via psycopg)          │   │
│  │  ChapterRepository                                  │   │
│  │  LessonRepository                                   │   │
│  │  EnrollmentRepository                               │   │
│  └────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────┘
```

---

## 📦 Package Structure

```
courses/                                    # Bounded Context
│
├── core/                                   # Domain Layer ✨
│   ├── __init__.py                        # Barrel Exports
│   ├── factory.py                         # 412 LOC
│   │   ├── CourseFactory
│   │   │   ├── create_draft()            # Business Rules Applied
│   │   │   ├── create_from_template()
│   │   │   ├── publish()                 # State Transition
│   │   │   ├── unpublish()
│   │   │   └── archive()
│   │   ├── ChapterFactory
│   │   │   └── create()
│   │   └── LessonFactory
│   │       └── create()
│   │
│   ├── services.py                        # 339 LOC
│   │   ├── CourseService
│   │   │   ├── can_user_enroll()         # 6 Business Rules
│   │   │   ├── calculate_progress()
│   │   │   ├── can_issue_certificate()
│   │   │   ├── calculate_course_statistics()
│   │   │   └── validate_course_structure()
│   │   └── EnrollmentService
│   │       ├── create_enrollment_with_payment()
│   │       └── bulk_enroll_users()
│   │
│   └── value_objects.py                   # 246 LOC
│       ├── Enums
│       │   ├── CourseStatus (draft, published, archived)
│       │   ├── Visibility (private, unlisted, public)
│       │   ├── EnrollmentType (open, approval, invite, closed)
│       │   ├── EnrollmentStatus (active, completed, cancelled)
│       │   └── LessonType (text, video, quiz, ai, ...)
│       ├── Dataclasses (Immutable)
│       │   ├── CourseSettings
│       │   ├── Price (amount, currency)
│       │   ├── EnrollmentWindow (start_date, end_date)
│       │   └── ProgressSnapshot
│       └── Type Aliases
│           └── CourseId, ChapterId, LessonId, UserId
│
├── admin/                                  # Admin API Layer
│   ├── __init__.py
│   └── crud.py                            # 473 LOC
│       ├── GET    /api/v1/admin/courses
│       ├── GET    /api/v1/admin/courses/{id}
│       ├── POST   /api/v1/admin/courses         # ✅ Uses Factory
│       ├── PATCH  /api/v1/admin/courses/{id}
│       ├── POST   /api/v1/admin/courses/{id}/status  # ✅ Uses Factory
│       ├── DELETE /api/v1/admin/courses/{id}    # ✅ Uses Factory
│       └── DELETE /api/v1/admin/courses/{id}/permanent
│
├── crud/                                   # User API Layer
│   ├── courses/
│   │   ├── __init__.py
│   │   ├── read.py                        # GET /courses, /courses/{id}
│   │   ├── write.py                       # POST, PATCH, DELETE
│   │   └── stats.py                       # Statistics
│   ├── chapters/
│   │   ├── __init__.py
│   │   ├── direct.py                      # Direct chapter access
│   │   └── nested.py                      # Nested under course
│   └── lessons.py                         # Lesson management
│
├── enrollment.py                           # User Enrollment
│   ├── GET    /courses/{id}/progress
│   ├── POST   /courses/{id}/enroll
│   ├── GET    /courses/my-courses
│   └── GET    /courses/enrolled
│
├── public/ (future)                        # Public API Layer
│   └── preview.py
│       └── GET /courses/{id}/preview
│
└── __init__.py                            # Package Integration
```

---

## 🔄 Data Flow Examples

### Example 1: Admin Creates Course

```
┌──────────────────────────────────────────────────────────────┐
│ 1. Request                                                    │
│    POST /api/v1/admin/courses                                │
│    { "title": "Python Basics", "category_id": "..." }        │
└─────────────────────┬────────────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────────────┐
│ 2. API Layer (admin/crud.py)                                 │
│    - Pydantic Validation (AdminCourseCreateRequest)          │
│    - Permission Check (require_permission)                   │
└─────────────────────┬────────────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────────────┐
│ 3. Domain Layer (core/factory.py)                            │
│    course = CourseFactory.create_draft(                      │
│        creator_id=user_id,                                   │
│        title="Python Basics",                                │
│        category_id=cat_id                                    │
│    )                                                          │
│    ✅ Business Rules Applied:                                │
│    - status = 'draft'                                        │
│    - visibility = 'private'                                  │
│    - is_published = False                                    │
│    - requires_enrollment = True                              │
└─────────────────────┬────────────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────────────┐
│ 4. Infrastructure Layer (repositories/)                      │
│    CourseRepository.create(course)                           │
│    → SQL INSERT mit psycopg3                                 │
└─────────────────────┬────────────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────────────┐
│ 5. Response                                                   │
│    { "success": true, "course": {...} }                      │
└──────────────────────────────────────────────────────────────┘
```

### Example 2: Admin Publishes Course

```
┌──────────────────────────────────────────────────────────────┐
│ 1. Request                                                    │
│    POST /api/v1/admin/courses/{id}/status                    │
│    { "action": "publish" }                                   │
└─────────────────────┬────────────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────────────┐
│ 2. API Layer (admin/crud.py)                                 │
│    - Load existing course                                    │
│    - Permission Check                                        │
└─────────────────────┬────────────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────────────┐
│ 3. Domain Layer (core/factory.py)                            │
│    published = CourseFactory.publish(course, publisher_id)   │
│    ✅ Business Rules Validated:                              │
│    - Already published? → ValueError                         │
│    - Has ≥1 chapter? → _has_required_content()              │
│    ✅ State Transition:                                      │
│    - is_published = True                                     │
│    - status = 'published'                                    │
│    - visibility = 'public'                                   │
│    - published_at = now()                                    │
│    - published_by = publisher_id                             │
└─────────────────────┬────────────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────────────┐
│ 4. Infrastructure Layer                                      │
│    CourseRepository.update(published)                        │
│    → SQL UPDATE                                              │
└─────────────────────┬────────────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────────────┐
│ 5. Response                                                   │
│    { "success": true, "status": "published" }                │
└──────────────────────────────────────────────────────────────┘
```

### Example 3: User Enrolls in Course

```
┌──────────────────────────────────────────────────────────────┐
│ 1. Request                                                    │
│    POST /api/v1/courses/{id}/enroll                          │
└─────────────────────┬────────────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────────────┐
│ 2. API Layer (enrollment.py)                                 │
│    - Load user and course                                    │
│    - Token Authentication                                    │
└─────────────────────┬────────────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────────────┐
│ 3. Domain Layer (core/services.py)                           │
│    can_enroll, reason = CourseService.can_user_enroll(       │
│        user, course                                          │
│    )                                                          │
│    ✅ Business Rules Checked:                                │
│    1. Course published?                                      │
│    2. Enrollment window active?                              │
│    3. Capacity not exceeded?                                 │
│    4. Not already enrolled?                                  │
│    5. Prerequisites met?                                     │
└─────────────────────┬────────────────────────────────────────┘
                      │
                      ├─ ✅ Allowed
                      │
┌─────────────────────▼────────────────────────────────────────┐
│ 4. Infrastructure Layer                                      │
│    EnrollmentRepository.create(enrollment_data)              │
│    → SQL INSERT                                              │
└─────────────────────┬────────────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────────────┐
│ 5. Response                                                   │
│    { "success": true, "enrollment": {...} }                  │
└──────────────────────────────────────────────────────────────┘
```

---

## 🎯 DDD Patterns Used

| Pattern | Implementation | Beispiel |
|---------|---------------|----------|
| **Factory** | `CourseFactory.create_draft()` | Komplexe Objekterstellung mit Business Rules |
| **Domain Service** | `CourseService.can_user_enroll()` | Business Logic über mehrere Entities |
| **Value Object** | `Price`, `CourseSettings` | Immutable Domain Concepts |
| **Enum** | `CourseStatus`, `Visibility` | Type-safe Zustandswerte |
| **Repository** | `CourseRepository` (extern) | Datenzugriff gekapselt |
| **Specification** | (future) `PublishableSpecification` | Business Rules testbar machen |

---

## 📋 Business Rules (Domain Layer)

### CourseFactory

| Rule | Validation | Location |
|------|------------|----------|
| Draft courses are private | `visibility = 'private'` | `create_draft()` |
| Enrollment required by default | `requires_enrollment = True` | `create_draft()` |
| Cannot publish without content | `_has_required_content()` | `publish()` |
| Auto-public on publish | `visibility = 'public'` | `publish()` |
| Cannot republish published course | `if is_published: raise ValueError` | `publish()` |

### CourseService

| Rule | Validation | Location |
|------|------------|----------|
| Course must be published | `if not is_published: False` | `can_user_enroll()` |
| Enrollment window active | `start_date <= now <= end_date` | `can_user_enroll()` |
| Not exceeded capacity | `count < max_students` | `can_user_enroll()` |
| Not already enrolled | Check existing enrollment | `can_user_enroll()` |
| Prerequisites met | (future) | `can_user_enroll()` |
| 100% progress for certificate | `progress >= 100` | `can_issue_certificate()` |

---

## 🔒 Immutability & Type Safety

### Value Objects (Immutable)

```python
@dataclass(frozen=True)
class Price:
    amount: float
    currency: str = "EUR"

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Price cannot be negative")

# ✅ Type-safe Creation
price = Price(29.99, "EUR")
print(price)  # 29.99 EUR

# ❌ Cannot Modify (frozen)
price.amount = 39.99  # FrozenInstanceError
```

### Enums (Type-safe)

```python
class CourseStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

# ✅ Type-safe Usage
course['status'] = CourseStatus.DRAFT

# ❌ Invalid Status Prevented at Type Level
course['status'] = "invalid"  # Type Checker Error
```

---

## 🧪 Testing Strategy

### Unit Tests (Domain Layer)

```python
# tests/test_course_factory.py
def test_create_draft_applies_business_rules():
    course = CourseFactory.create_draft(
        creator_id="user123",
        title="Test Course",
        category_id="cat456"
    )
    assert course['status'] == 'draft'
    assert course['visibility'] == 'private'
    assert course['is_published'] is False

def test_publish_validates_content():
    course = CourseFactory.create_draft(...)
    with pytest.raises(ValueError, match="must have at least 1 chapter"):
        CourseFactory.publish(course, "admin123")
```

```python
# tests/test_course_service.py
def test_can_user_enroll_checks_published():
    user = {'user_id': 'user123'}
    course = {'is_published': False}
    can_enroll, reason = CourseService.can_user_enroll(user, course)
    assert can_enroll is False
    assert reason == "Course is not published"
```

### Integration Tests (API Layer)

```python
# tests/test_admin_crud.py
def test_admin_create_course_uses_factory(client, admin_headers):
    response = client.post('/api/v1/admin/courses', json={
        'title': 'Test Course',
        'category_id': 'cat123'
    }, headers=admin_headers)
    assert response.status_code == 201
    data = response.get_json()
    assert data['course']['status'] == 'draft'
    assert data['course']['visibility'] == 'private'
```

---

## 📚 References

- **DDD Book:** Eric Evans - Domain-Driven Design
- **ISO Standard:** ISO/IEC 26515 (User Documentation)
- **Pattern Catalog:** Martin Fowler - Patterns of Enterprise Application Architecture
- **Project Docs:** `LernsystemX-Doku/05_Technical/05_Backend-Struktur.md`

---

**Version:** 1.0
**Datum:** 2026-01-08
**Status:** ✅ PRODUCTION-READY
